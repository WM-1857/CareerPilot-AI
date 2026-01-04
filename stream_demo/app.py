import os
import sys
import json
from flask import Flask, render_template, request, Response, stream_with_context
from openai import OpenAI

# 强制设置标准输出编码为 UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)

client = OpenAI(
    api_key="FVuyeuSYMCNQbhrSXpDU:YHvavxbeDTRXxLtizTMR", 
    base_url="https://spark-api-open.xf-yun.com/v1",
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    def generate():
        try:
            stream = client.chat.completions.create(
                messages=[{"role": "user", "content": user_message}],
                model="lite",
                stream=True,
                user="123456",
            )
            
            for chunk in stream:
                content = ""
                # 处理思考过程
                if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                    content = chunk.choices[0].delta.reasoning_content
                # 处理正式内容
                elif hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                
                if content:
                    # SSE 格式: data: <content>\n\n
                    yield f"data: {json.dumps({'content': content})}\n\n"
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
