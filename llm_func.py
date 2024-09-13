import dotenv
from prompt import *
from langchain_community.llms.baidu_qianfan_endpoint import QianfanLLMEndpoint
from langchain_community.chat_models import ChatSparkLLM
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

dotenv.load_dotenv()

model = QianfanLLMEndpoint(
    model="ERNIE-4.0-8K",
    timeout=120
)

# model = ChatSparkLLM(
#     model='Spark 4.0Ultra'
# )

parser = JsonOutputParser()


def handler_letter_correct(essay: str) -> str:
    """
    这个方法处理书信作文批改任务，返回评分、错误分析、亮点分析与写作建议的Json结构化输出
    :param essay: 待批改文章
    :return: Json格式输出 e.g.{"评分":"xx","错误分析":{"拼写错误":"xxxxxxxx","语法错误":"xxxxxxxx","用词不当":"xxxxxxxx"},"亮点分析":{"高级词汇":"xxxxxxxx","亮点表达":"xxxxxxxx"},"写作建议":"xxxxxxxx"}
    """
    prompt = PromptTemplate(
        template=task_letter.prompt(),
        input_variables=task_letter.input_variables(),
        partial_variables={"format_instructions": task_letter.format_instruction()}

    )
    chain = prompt | model | parser
    output = chain.invoke({"essay": essay})

    return output


def handler_single_sentence(sentence: str) -> str:
    """
    这个方法处理单英文句子批改分析任务，返回Json结构化输出
    :param essay: 待分析句子
    :return: Json格式输出 e.g.{"拼写错误":"xxxxxxxx,""语法错误":"xxxxxxxx","用词不当":"xxxxxxxx","高级表达":"xxxxxxxx"}
    """
    prompt = PromptTemplate(
        template=task_single_sentence.prompt(),
        input_variables=task_single_sentence.input_variables(),
        partial_variables={"format_instructions": task_single_sentence.format_instruction()}

    )
    chain = prompt | model
    output = chain.invoke({"sentence": sentence})

    return output


__all__ = ["handler_letter_correct","handler_single_sentence"]
