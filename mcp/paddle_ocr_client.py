#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PaddleOCR MCP 客户端
调用 PaddleOCR MCP 服务提取文档/图片中的文字，并解析为特定格式的关键字段
"""

import os
import sys
import json
import asyncio
from typing import Dict, Any, Optional

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from src.services.llm_service import llm_service
    from src.utils.logger import workflow_logger
except ImportError as e:
    print(f"导入失败: {e}")
    print("请确保已安装 mcp 和 paddleocr-mcp: pip install mcp paddleocr-mcp[local-cpu]")
    sys.exit(1)

class PaddleOCRClient:
    """PaddleOCR MCP 客户端类"""
    
    def __init__(self, pipeline: str = "OCR", ppocr_source: str = "local"):
        """
        初始化客户端
        
        Args:
            pipeline: 产线名称 (OCR, PP-StructureV3, PaddleOCR-VL)
            ppocr_source: 能力来源 (local, aistudio, qianfan, self_hosted)
        """
        self.pipeline = pipeline
        self.ppocr_source = ppocr_source
        # 获取 python 解释器路径，确保在 conda 环境中运行
        self.python_exe = sys.executable
        
    async def extract_text_from_file(self, file_path: str) -> str:
        """
        使用 MCP 服务从图片或 PDF 文件中提取文字
        
        Args:
            file_path: 图片或 PDF 文件路径
            
        Returns:
            提取的原始文本
        """
        # 转换为绝对路径，确保 MCP 服务器能正确找到文件
        abs_file_path = os.path.abspath(file_path)
        if not os.path.exists(abs_file_path):
            raise FileNotFoundError(f"找不到文件: {abs_file_path}")
            
        # 设置 MCP 服务器参数
        env = os.environ.copy()
        env["PADDLEOCR_MCP_PPOCR_SOURCE"] = self.ppocr_source
        env["PADDLEOCR_MCP_PIPELINE"] = self.pipeline
        
        server_params = StdioServerParameters(
            command=self.python_exe,
            args=["-m", "paddleocr_mcp", "--pipeline", self.pipeline, "--ppocr_source", self.ppocr_source],
            env=env
        )
        
        print(f"正在启动 PaddleOCR MCP 服务器 (pipeline={self.pipeline})...")
        
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # 初始化会话
                    await session.initialize()
                    
                    # 获取可用工具列表
                    tools_result = await session.list_tools()
                    tool_names = [t.name for t in tools_result.tools]
                    print(f"可用 MCP 工具: {tool_names}")
                    
                    # 确定要使用的工具名称（优先匹配 OCR 或 ocr）
                    target_tool = "OCR"
                    if "OCR" not in tool_names:
                        if "ocr" in tool_names:
                            target_tool = "ocr"
                        elif tool_names:
                            target_tool = tool_names[0]
                            print(f"⚠️ 未找到 'OCR' 或 'ocr' 工具，尝试使用第一个可用工具: {target_tool}")
                        else:
                            raise RuntimeError("MCP 服务器未提供任何工具")
                    
                    # 获取工具详情以确定参数名称
                    target_tool_obj = next((t for t in tools_result.tools if t.name == target_tool), None)
                    arg_name = "image" # 默认值
                    if target_tool_obj and target_tool_obj.inputSchema:
                        schema = target_tool_obj.inputSchema
                        properties = schema.get("properties", {})
                        # 优先检查 input_data，因为 paddleocr-mcp 0.4.1 使用这个
                        if "input_data" in properties:
                            arg_name = "input_data"
                        elif "image" in properties:
                            arg_name = "image"
                        print(f"工具 '{target_tool}' 使用参数名: {arg_name}")
                    
                    # 调用 OCR 工具
                    print(f"正在对文件进行 OCR 识别: {abs_file_path}")
                    result = await session.call_tool(target_tool, arguments={arg_name: abs_file_path})
                    
                    # 调试：打印原始结果类型
                    print(f"MCP 返回结果类型: {type(result)}")
                    
                    # 处理结果
                    if hasattr(result, 'content') and result.content:
                        text_content = ""
                        for i, item in enumerate(result.content):
                            # print(f"内容项 {i} 类型: {type(item)}")
                            if hasattr(item, 'text'):
                                text_content += item.text + "\n"
                            elif isinstance(item, dict) and 'text' in item:
                                text_content += item['text'] + "\n"
                            else:
                                # 尝试将整个 item 转为字符串，看看里面有什么
                                print(f"内容项 {i} 详情: {str(item)[:200]}")
                        
                        final_text = text_content.strip()
                        print(f"提取到的总文本长度: {len(final_text)}")
                        return final_text
                    else:
                        print(f"⚠️ OCR 识别未返回 content 字段或为空: {result}")
                        return ""
        except Exception as e:
            print(f"❌ 调用 MCP 服务出错: {e}")
            raise

    def parse_to_user_profile(self, ocr_text: str) -> Dict[str, Any]:
        """
        使用 LLM 将 OCR 文本解析为特定格式的用户画像
        
        Args:
            ocr_text: OCR 识别出的原始文本
            
        Returns:
            格式化后的用户画像字典
        """
        if not ocr_text:
            return {}
            
        prompt = f"""
你是一位专业的职业规划专家。请从以下 OCR 识别出的简历文本中提取关键信息，用于后续的职业生涯规划分析。
请以 JSON 格式返回提取的数据。

提取规则：
1. 如果某个字段在文本中未直接提及，请根据简历内容（如毕业时间、工作经历）进行合理推断。
2. 如果确实无法推断，请留空（字符串型留空 ""，列表型留空 []，数值型留空 0）。
3. age（年龄）：如果简历中没有直接写年龄，请根据最早的本科学位毕业时间推断（假设本科毕业时为 22 岁）。
4. work_experience（工作年限）：请计算从第一份正式工作至今的总年限（整数）。如果是学生或应届生，请填 0。
5. current_position（当前职位）：提取最近一份工作的职位名称。如果是学生，请填 "学生"。
6. industry（行业）：根据工作经历推断所属的主要行业。

需要提取的关键字段：
- user_id: 用户ID（固定设为 "interactive_user_001"）
- age: 年龄（整数）
- education_level: 最高教育程度（如：本科、硕士、博士等）
- work_experience: 工作年限（整数）
- current_position: 当前职位
- industry: 行业
- skills: 技能列表（列表，包含专业技能、工具、语言等）
- interests: 兴趣爱好（列表）
- career_goals: 职业目标（从简历的自我评价或求职意向中提取）
- location: 所在地（城市）
- salary_expectation: 期望薪资（如果简历中没有，请根据行业水平和职位进行合理推断，如 "20k-30k"）

OCR 文本内容：
---
{ocr_text}
---

请仅返回纯 JSON 格式的数据，不要包含任何 Markdown 代码块标签或解释性文字。
"""
        
        print("正在调用 LLM 解析 OCR 文本...")
        response = llm_service.call_llm(prompt)
        
        try:
            content = response.get("content", "{}")
            # 记录 LLM 返回的原始内容长度
            print(f"LLM 响应长度: {len(content)}")
            
            # 清理可能的 markdown 标记
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                # 寻找第一个和最后一个花括号
                start = content.find("{")
                end = content.rfind("}")
                if start != -1 and end != -1:
                    content = content[start:end+1]
                else:
                    content = content.split("```")[1].split("```")[0].strip()
            
            # 再次尝试寻找花括号，以防 LLM 返回了额外的解释文字
            if not content.startswith("{"):
                start = content.find("{")
                end = content.rfind("}")
                if start != -1 and end != -1:
                    content = content[start:end+1]
                
            profile_data = json.loads(content)
            return profile_data
        except Exception as e:
            print(f"❌ 解析 LLM 响应失败: {e}, 原始响应: {response.get('content')}")
            return {}

    async def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        一键处理文件：OCR 识别 + LLM 解析
        """
        ocr_text = await self.extract_text_from_file(file_path)
        if not ocr_text:
            print("⚠️ OCR 识别结果为空，请检查图片是否清晰或路径是否正确")
            return {}
        
        # 打印 OCR 提取的原始文本以便调试
        print(f"--- OCR 提取文本预览 (前500字) ---\n{ocr_text[:500]}...\n---")
        
        return self.parse_to_user_profile(ocr_text)

async def main():
    """测试函数"""
    if len(sys.argv) < 2:
        print("用法: python paddle_ocr_client.py <文件路径>")
        return
        
    file_path = sys.argv[1]
    client = PaddleOCRClient()
    
    try:
        result = await client.process_file(file_path)
        print("\n" + "="*50)
        print("🚀 提取的用户画像数据:")
        print("="*50)
        print(json.dumps(result, indent=4, ensure_ascii=False))
        print("="*50)
    except Exception as e:
        print(f"❌ 处理失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())
