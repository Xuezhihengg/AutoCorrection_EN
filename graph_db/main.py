import dotenv
import db
from typing import List, TypedDict, Optional
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_community.llms import QianfanLLMEndpoint
from langchain_core.prompts import PromptTemplate
from langchain_core.globals import set_debug
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser

# set_debug(True)

dotenv.load_dotenv()

model = QianfanLLMEndpoint(
    model="ERNIE-4.0-8K",
)


class AnalysisStateItem(TypedDict):
    """AnalysisStateItem是AnalysisState列表的元素，是包含“analysis”键和“concept”键的字典"""
    analysis: str
    concepts: List[str]
    isRule: Optional[bool]


class AnalysisState(BaseModel):
    """AnalysisState是一个List，其元素为AnalysisStateItem，即一个包含“analysis”键和“concept”键的TypedDict"""
    answer: List[AnalysisStateItem] = Field(
        "AnalysisState是一个List，其元素为AnalysisStateItem，即一个包含“analysis”键和“concept”键的字典")


class SingleSentenceInput(TypedDict):
    sentence: str


def determine_top_gc(state: SingleSentenceInput) -> AnalysisState:
    """
    分析输入英文句子的语法错误，并找出与之相关的语法概念，这些语法概念只能在知识图的顶级语法概念中选择
    :param state: 输入的英文句子
    :return: 一个AnalysisState对象，AnalysisState是一个List，其元素为AnalysisStateItem，即一个包含“analysis”键和“concept”键的字典
    """
    top_gc_nodes = db.get_top_gc()

    # Prompt
    prompt_template = """
    你是一名分类者，用户将传入一段英文句子（message）与若干英语语法概念（nodes），请你判断这段英文句子中的语法错误属于nodes中的哪个或哪些语法概念（输入到AnalysisStateItem中“concept”键的值），
    并对该语法错误做简要解析（输入到AnalysisStateItem中“analysis”键的值）。
    注意：
    1、AnalysisState列表中的每一项仅对应一个语法错误，不可对应多项语法错误
    2、AnalysisStateItem中“concepts”键的值只能为nodes中的一个（即len(AnalysisStateItem["concept"])=1），且为最相关的一个
    3、AnalysisStateItem中“analysis”只与“concepts”键对应的语法概念相关，与其他语法概念无关，且解析要简短准确
    输出格式要求{format_instructions}
    用户输入：英文句子：{message} \n 英语语法概念：{nodes}
    """

    parser = PydanticOutputParser(pydantic_object=AnalysisState)

    prompt = PromptTemplate.from_template(
        template=prompt_template,
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    chain = prompt | model | parser

    output = chain.invoke({"message": state["sentence"], "nodes": top_gc_nodes})

    print("-" * 50 + "determine_top_gc" + "-" * 50)
    print(output)

    return output


def get_neighbours(state: AnalysisState) -> AnalysisState:
    """
    获取所有AnalysisState中顶层概念节点的相邻节点，并替换原来的concept
    :param state: 一个AnalysisState对象，AnalysisState是一个List，其元素为AnalysisStateItem，即一个包含“analysis”键和“concept”键的字典
    :return: 顶层概念替换为相邻节点后的AnalysisState对象
    """
    state = state.answer
    for item in state:
        if item["isRule"]:
            continue
        concepts = item["concepts"]
        # assert len(concepts) == 1, "get_neighbours处理前的所有item的concepts中应只有一个语法概念"

        is_Rule = db.get_labels(concepts[0]) == "Rule"
        if not is_Rule:
            item["concepts"] = db.get_neighbours(item["concepts"][0])

    print("-" * 50 + "get_neighbours" + "-" * 50)
    print(state)
    return AnalysisState(answer=state)


def determine_most_relevant(state: AnalysisState) -> AnalysisState:
    """
    使用LLM判断若干语法概念中，与输入语法解析最相关的概念
    :param state: 一个AnalysisState对象，来自get_neighbours将但语法概念拓展后
    :return: 最相关分析后的AnalysisState对象
    """
    state = state.answer

    prompt_template = """
    用户输入一句语法解析（analysis），并输入一个包含若干语法概念的列表（concepts），请你判断这句语法解析与concepts中哪个语法概念最相关，并输出该语法概念
    输出格式要求{format_instructions}
    用户输入：语法解析：{analysis} \n 语法概念：{concepts}
    """

    class MostRelevantConcept(BaseModel):
        """与输入语法分析最相关的语法概念"""
        concept: str = Field("与输入语法分析最相关的语法概念")

    parser = PydanticOutputParser(pydantic_object=MostRelevantConcept)

    prompt = PromptTemplate(
        template=prompt_template,
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | model | parser

    for i, item in enumerate(state):
        if item["isRule"]:
            continue

        output = chain.invoke({"analysis": item["analysis"], "concepts": item["concepts"]})
        state[i]["concepts"] = [output.concept]

    return AnalysisState(answer=state)


def judge_is_Rule(state: AnalysisState) -> [AnalysisState, bool]:
    """
    判断AnalysisState中所有item的语法概念是否为Rule类型，若是，则更新其“isRule”字段
    :param state: 最相关分析后的AnalysisState对象
    :return: 更新isRule字段后的AnalysisState对象，以及判断是否全部均已为Rule类型的bool量
    """
    state = state.answer
    count = 0
    all_are_Rule = False
    for i, item in enumerate(state):
        concept = item["concepts"][0]
        is_Rule = db.get_labels(concept)[0] == "Rule"
        if is_Rule:
            state[i]["isRule"] = True
            count += 1

    print("-" * 50 + "judge_is_Rule" + "-" * 50)
    print(state)

    if count == len(state):
        all_are_Rule = True

    return AnalysisState(answer=state), all_are_Rule


class DetailState(BaseModel):
    """DetailState包含列表，每个元素都是一个字符串，其内容为对原有解析内容拓展后的细节解析"""
    answer: List[str] = Field(description="解析内容拓展后的细节解析组成的字符串数组")


def extend_detail(state: AnalysisState) -> DetailState:
    """
    将Rule节点搜寻结束的AnalysisState对象进行解析细节丰富
    :param state: Rule节点搜寻结束的AnalysisState对象
    :return: 解析细节丰富后的AnalysisState对象
    """
    state = state.answer
    prompt_template = """
    用户输入用户输入一句语法解析（analysis），并输入与该语法解析相关的语法概念的详细信息（detail，为一个包含“description”键和“examples”键的字典），你需要结合analysis和detail，对原有的analysis进行扩写和丰富，充分利用其中的examples
    用户输入: 语法解析:{analysis} \n 详细信息:{detail}    
    """

    parser = StrOutputParser()

    prompt = PromptTemplate(
        template=prompt_template,
    )

    chain = prompt | model | parser

    outputs = ["" for _ in range(len(state))]
    for i, item in enumerate(state):
        analysis = item["analysis"]
        concept = item["concepts"][0]
        detail = db.get_detail(concept)

        outputs[i] = chain.invoke({"analysis": analysis, "detail": detail})

    print("-" * 50 + "extend_detail" + "-" * 50)
    print(outputs)

    return DetailState(answer=outputs)


def main():
    raw_analysis = determine_top_gc({"sentence": "I should ask the some people the Chinese cultures's beautiful."})
    all_are_Rule = False
    while not all_are_Rule:
        extend_gc = get_neighbours(raw_analysis)
        after_analysis = determine_most_relevant(extend_gc)
        raw_analysis, all_are_Rule = judge_is_Rule(after_analysis)

    extend_detail(raw_analysis)


if __name__ == "__main__":
    main()
