import os
import sys
from openai import OpenAI
import openai

# 强制设置标准输出编码为 UTF-8，解决 Windows 控制台乱码问题
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

client = OpenAI(
    # 1、http协议的APIpassword； 2、ws协议的apikey和apisecret 按照ak:sk格式拼接；
    api_key="FVuyeuSYMCNQbhrSXpDU:YHvavxbeDTRXxLtizTMR", 
    base_url="https://spark-api-open.xf-yun.com/v1",
)

stream_res = True
# stream_res = False


stream = client.chat.completions.create(
    messages=[
          {
            "role": "user",
            "content": "你好，介绍一下智能交互设计专业"
        },

    ],

    model="lite",
    stream=stream_res,
    user="123456",

)
full_response = ""

if not stream_res:
    print(stream.to_json())
else:
    for chunk in stream:
        if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content is not None:
            reasoning_content = chunk.choices[0].delta.reasoning_content
            print(reasoning_content, end="", flush=True)  # 实时打印思考模型输出的思考过程每个片段
        
        if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            print(content, end="", flush=True)  # 实时打印每个片段
            full_response += content
    
    print("\n\n ------完整响应：", full_response)   
