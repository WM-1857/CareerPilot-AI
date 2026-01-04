# CareerNavigator MCP 服务集成

本文件夹包含了与 Model Context Protocol (MCP) 服务集成的相关代码。

## 主要功能

### PaddleOCR MCP 客户端 (`paddle_ocr_client.py`)

该客户端实现了调用 PaddleOCR MCP 服务器来提取文档或图片中的文字，并利用大语言模型 (LLM) 将提取的原始文本解析为结构化的用户画像数据。

#### 提取的字段包括：
- `user_id`: 用户唯一标识
- `age`: 年龄
- `education_level`: 教育程度
- `work_experience`: 工作年限
- `current_position`: 当前职位
- `industry`: 行业
- `skills`: 技能列表
- `interests`: 兴趣爱好
- `career_goals`: 职业目标
- `location`: 所在地
- `salary_expectation`: 期望薪资

## 安装依赖

```bash
pip install mcp "paddleocr-mcp[local-cpu]" paddleocr>=3.2 paddlepaddle>=3.0.0
```

## 使用方法

你可以直接运行脚本来测试图片识别：

```bash
python mcp_app/paddle_ocr_client.py <图片路径>
```

或者在代码中调用：

```python
from mcp_app.paddle_ocr_client import PaddleOCRClient
import asyncio

async def test():
    client = PaddleOCRClient()
    profile = await client.process_image("path/to/your/resume.jpg")
    print(profile)

if __name__ == "__main__":
    asyncio.run(test())
```

## 参考文档

- [PaddleOCR MCP Server 官方文档](https://www.paddleocr.ai/latest/version3.x/deployment/mcp_server.html)
- [Model Context Protocol 官方网站](https://modelcontextprotocol.io/)
