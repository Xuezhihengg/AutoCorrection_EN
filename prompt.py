from typing import List


class BaseTask:
    def __init__(self, prompt: str, input_variables: List[str], format_instruction: str) -> None:
        self.__prompt: str = prompt
        self.__format_instruction: str = format_instruction
        self.__input_variables: List[str] = input_variables

    def prompt(self) -> str:
        return self.__prompt

    def format_instruction(self) -> str:
        return self.__format_instruction

    def input_variables(self) -> List[str]:
        return self.__input_variables


task_letter = BaseTask(
    prompt="""
你是一名高中英语老师，现有一篇英语书信作文需要你批改，你需要对这篇作文评分(满分为15分)并找出文章中所有的拼写错误，用词不当以及语法错误；同时找出文章中的高级词汇，亮点表达；最后，你还需要为该同学提出写作进步的建议。
为了定位，请将文章中的所有错误的开始下标与结束下标返回；对于错误分析，请详细分析语法知识点并给出一定的正例与反例；对于亮点分析，请详细给出亮点的优秀之处。
作文：{essay}
输出格式：{format_instructions}""",
    input_variables=["essay"],
    format_instruction="""
输出格式为如下json格式：
{"评分":"xx","错误分析":{"拼写错误":"xxxxxxxx","语法错误":"xxxxxxxx","用词不当":"xxxxxxxx"},"亮点分析":{"高级词汇":"xxxxxxxx","亮点表达":"xxxxxxxx"},"写作建议":"xxxxxxxx"}"""
)

task_single_sentence = BaseTask(
    prompt="""
    你是一名高中英语老师,现在你需要对一段英文句子进行如下分析：
    1、拼写错误（并给出正确的拼写）
    2、语法错误（需要详细分析语法知识点并给出一定的正例与反例）
    3、用词不当（需要给出不合适的理由并给出修改建议）
    4、高级表达（如高级的单词、词组或句型，并分析该表达的高级之处）
    句子：{sentence}
    输出格式：{format_instructions}""",
    input_variables=["sentence"],
    format_instruction="""
    按自然语言输出。    
    """
)