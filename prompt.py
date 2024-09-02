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
作文：{essay}
输出格式：{format_instructions}""",
    input_variables=["essay"],
    format_instruction="""
输出格式为如下json格式：
{"评分":"xx","错误分析":{"拼写错误":"xxxxxxxx","语法错误":"xxxxxxxx","用词不当":"xxxxxxxx"},"亮点分析":{"高级词汇":"xxxxxxxx","亮点表达":"xxxxxxxx"},"写作建议":"xxxxxxxx"}
示例如下
{'评分': '7', '错误分析': {'拼写错误': ['ealy(应为early)', 'apriceat(应为appreciate)', 'quikly(应为quickly)', 'zhunbe(应为prepare)', 'gong(应为fun或work，取决于作者想表达的确切意思，但“gong”在英语中没有意义)', 'rangxi(应为grateful，假设作者想表达“感激”的意思)'], '语法错误': ["Your grandfather's orchard are where(应为Your grandfather's orchard is where 或 Your grandfather's orchards are where，取决于orchard是单数还是复数)", 'I can going to help them(应为I can go to help them 或者 I am going to help them)', 'I very happy can help you(应为I am very happy to help you)', 'I need you can tell me(语法结构混乱，应为I need you to tell me)', 'I am buy cat for they orchard(应为I am buying a cat for their orchard，注意主谓一致和冠词使用)', 'and when I need to help you(应改为and tell me when I need to help you，使得句子更加清晰)', "I don't hope going late(应为I don't want to be late 或 I hope I won't be late)", "and I'm very happy help to you(应为and I'm very happy to help you)"], '用词不当': ['If you could apriceat it tell me job(表达不清，可以改为If you could appreciate it, please tell me the details of the job)']}, '亮点分析': {'高级词汇': [], '亮点表达': []}, '写作建议': '除了纠正上述的拼写、语法和用词错误，建议多阅读和掌握基础的英语语法规则，尤其是主谓一致、时态和语态的正确使用。同时，积累更多的英语词汇，并尝试使用更丰富的表达方式。在写作时，可以先写出中文草稿，再逐句翻译成英文，注意保持句子的通顺和语法的正确。最后，务必仔细检查作文，避免拼写和语法错误。'}"""
)
