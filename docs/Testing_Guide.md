# CareerNavigator 测试指南

本文档介绍如何对 CareerNavigator 系统进行功能验证和自动化测试。

## 🛠️ 环境准备

在运行测试之前，请确保：
1. 已安装所有依赖: `pip install -r requirements.txt`
2. 已设置环境变量: `set DASHSCOPE_API_KEY=your_api_key`

## 🚀 快速测试

项目根目录下提供了批处理脚本，可以一键运行基础测试：

```cmd
run_tests.bat
```

## 🧪 自动化测试脚本

项目包含多个专门的测试脚本，用于验证不同模块的功能：

### 1. 核心功能测试 (`test_mcp_output.py`)
验证 LangGraph 节点和 LLM 服务的集成情况。
```cmd
python test_mcp_output.py
```

### 2. Tavily 搜索集成测试 (`test_tavily_integration.py`)
验证外部搜索工具的集成（如果配置了相关 API）。
```cmd
python test_tavily_integration.py
```

### 3. 来源验证测试 (`verify_sources.py`)
验证分析报告中的数据来源可靠性。
```cmd
python verify_sources.py
```

## 📊 交互式工作流测试

如果您想在命令行中体验完整的工作流，可以运行：

```cmd
python interactive_workflow.py
```

该脚本将模拟前端交互，允许您输入个人信息并实时查看 LangGraph 节点的执行过程和输出。

## 🔍 常见问题排查

- **API 调用超时**: 请检查网络连接，或尝试增加 `src/services/llm_service.py` 中的超时设置。
- **JSON 解析错误**: 查看 `logs/` 目录下的日志文件，确认 LLM 返回的原始响应内容。
- **OCR 识别失败**: 确保安装了 `paddleocr` 及其相关依赖，且上传的图片格式正确（jpg/png）。
