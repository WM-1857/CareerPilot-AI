# CareerNavigator Windows 测试指南

本文档介绍如何在 Windows 环境下运行 CareerNavigator 的测试套件。

## 测试环境准备

### 前提条件
- Python 3.8+
- 已安装项目依赖 (`pip install -r requirements.txt`)
- 设置有效的 `DASHSCOPE_API_KEY` 环境变量

### 快速测试

使用提供的批处理脚本：
```cmd
run_tests.bat
```

## 测试类型

### 1. 快速测试（推荐新用户）
```cmd
# 运行环境检查和LLM服务测试
python tests/run_tests.py --mode quick
```

包含：
- 环境依赖检查
- LLM 服务连接测试
- 基础功能验证

### 2. 核心测试
```cmd
# 运行核心工作流测试
python tests/run_tests.py --mode core
```

包含：
- 环境检查
- LLM 服务测试
- LangGraph 工作流测试

### 3. 完整测试
```cmd
# 运行所有自动化测试
python tests/run_tests.py --mode full
```

包含：
- 所有核心测试
- 集成测试
- API 端点测试

### 4. 交互式测试
```cmd
# 运行交互式测试（需要用户输入）
python tests/run_tests.py --mode interactive
```

包含：
- 完整工作流体验
- 用户界面测试

## 单独运行测试

### 环境测试
```cmd
# Windows 环境测试
python tests/unit/test_environment_win.py

# 通用环境测试
python tests/unit/test_environment.py
```

### LLM 服务测试
```cmd
# Windows LLM 测试
python tests/unit/test_llm_service_win.py

# 通用 LLM 测试
python tests/unit/test_llm_service.py
```

### LangGraph 工作流测试
```cmd
# Windows LangGraph 测试
python tests/unit/test_langgraph_win.py

# 通用 LangGraph 测试
python tests/unit/test_langgraph.py
```

### 集成测试
```cmd
# 工作流集成测试
python tests/integration/test_workflow.py
```

### 端到端测试
```cmd
# 交互式测试
python tests/e2e/test_interactive.py
```

## 测试结果

测试结果会保存在 `tests/results/` 目录下，文件名格式为：
```
test_results_YYYYMMDD_HHMMSS.json
```

## 常见问题

### 1. API 密钥错误
```
Error: Invalid API key
```
**解决方案**: 检查 `DASHSCOPE_API_KEY` 环境变量是否正确设置

### 2. 网络连接问题
```
Error: Connection timeout
```
**解决方案**: 检查网络连接，确认能访问阿里云百炼服务

### 3. 依赖包缺失
```
ModuleNotFoundError: No module named 'xxx'
```
**解决方案**: 运行 `pip install -r requirements.txt` 重新安装依赖

### 4. 权限问题
```
PermissionError: Access denied
```
**解决方案**: 以管理员身份运行命令提示符

## 测试性能优化

- **快速测试**: 约 2 分钟
- **核心测试**: 约 5 分钟  
- **完整测试**: 约 10 分钟
- **交互测试**: 约 15 分钟

建议开发时使用快速测试，发布前运行完整测试。
