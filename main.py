from ocr_func import orc
import llm_func
from test_article import *

LETTER_IMG_PATH = "test_image/letter_1.png"


def main():
    print("-" * 40 + "作文识别中" + "-" * 40)
    letter = orc(LETTER_IMG_PATH)
    print("手写识别成功，作文内容为：")
    print(letter)
    print("-" * 40 + "作文评分解析中" + "-" * 40)
    output = llm_func.handler_letter_correct(letter)
    print(output)
    print("-" * 90)


if __name__ == '__main__':
    # main()
    print(llm_func.handler_single_sentence("I should ask the some people the Chinese cultures's beautiful."))
