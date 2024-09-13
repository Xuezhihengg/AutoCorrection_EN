import json
import os

import dotenv
import base64
import urllib
import requests

dotenv.load_dotenv()
OCR_AK = os.getenv("OCR_AK")
OCR_SK = os.getenv("OCR_SK")


def orc(img_path: str) -> str:
    """
    调用百度智能云OCR服务，解析上传图片中的手写作文
    :param img_path:图片路径
    :return:识别出的完整作文
    """
    url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token=" + get_access_token()

    payload = "image=" + get_file_content_as_base64(img_path, True)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    result = build_essay(json.loads(response.text))

    return result


def get_file_content_as_base64(path, urlencoded=False):
    """
    获取文件base64编码
    :param path: 文件路径
    :param urlencoded: 是否对结果进行urlencoded
    :return: base64编码信息
    """
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf8")
        if urlencoded:
            content = urllib.parse.quote_plus(content)
    return content


def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": OCR_AK, "client_secret": OCR_SK}
    return str(requests.post(url, params=params).json().get("access_token"))


def build_essay(res) -> str:
    """
    将ocr返回的
    :param res:ocr()方法的返回值
    :return:拼接好的完整作文
    """
    if isinstance(res.get('words_result'), list):
        words_list = [item['words'] for item in res['words_result'] if isinstance(item, dict) and 'words' in item]
        full_essay = " ".join(words_list)
        full_essay = full_essay.replace(" .", ".").replace(" ,", ",")
        return full_essay
    else:
        raise ValueError("Invalid data format: 'words_result' should be a list.")


if __name__ == '__main__':
    print(orc("test_image/letter_2.png"))
