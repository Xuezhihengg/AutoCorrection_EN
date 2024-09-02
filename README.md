# AutoCorrection_EN
基于LLM的高中英语作文自动批改应用
# 项目结构
.  
├── main.py  
├── llm_func.py  
├── ocr_func.py  
├── prompt.py  
├── test_article.py  
├── requirements.txt  
└── test_image  

**main.py** ：demo主文件夹，评分主流程在此执行，先调用OCR服务识别手写作文，再调用LLM进行评分  
**llm_func.py** ：LLM大模型方法，对作文进行评分和解析  
**ocr_func.py** ：调用百度智能云的OCR服务  
**prompt.py** ：对大模型提示词任务的类型封装  
**test_article.py** ：测试文章  
**test_image** ：测试用到的手写作文图片

# 运行

直接运行main.py即可：  
`python main.py`  
注意: 本Demo选用百度千帆LLM大模型：ERNIE-4.0-8K，以及百度智能云的通用文字识别（高精度版）API服务，运行main.py前需要为百度千帆的API Key和Secret Key以及百度智能云应用的API Key和Secret Key设置环境变量  
`touch .env`  
在.env文件内输入：
```
QIANFAN_AK=YOUR_AK
QIANFAN_SK=YOUR_SK

OCR_AK=YOUR_AK
OCR_SK=YOUR_SK
```
