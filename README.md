# CareerNavigator - 智能职业规划助手

## 🎯 项目简介

CareerNavigator 是一个基于AI的智能职业规划助手，帮助用户制定个性化的职业发展计划。

## 🏗️ 技术架构

- **后端**: Flask + LangGraph + 阿里云百炼API
- **前端**: React + Tailwind CSS
- **存储**: 内存存储（简化版本，无数据库）

## 📁 项目结构

```
CareerNavigator/
├── main.py                     # 主应用入口
├── dev_tools.py               # 开发工具脚本
├── config/                    # 配置文件
│   └── config.py
├── src/                       # 后端源代码
│   ├── models/               # 数据模型
│   │   └── career_state.py   # 状态管理
│   ├── services/             # 业务服务
│   │   ├── llm_service.py    # LLM服务
│   │   ├── career_nodes.py   # 工作流节点
│   │   └── career_graph.py   # 工作流图
│   ├── routes/               # API路由
│   │   └── career.py         # 职业规划API
│   └── utils/                # 工具模块
│       └── logger.py         # 日志工具
├── tests/                    # 测试文件
│   ├── test_backend.py       # 后端API测试
│   └── test_components.py    # 组件单元测试
├── frontend/                 # 前端文件
│   ├── src/
│   │   ├── App.jsx          # 主应用
│   │   └── components/      # React组件
│   └── index.html
├── logs/                     # 日志目录
└── docs/                     # 文档目录
```

## 🚀 快速开始

### 1. 环境准备

确保你有以下环境：
- Python 3.8+
- Git（可选，用于获取项目）

### 2. 安装依赖

```cmd
pip install -r requirements.txt
```

### 3. 设置API密钥

编辑 `start_server.bat` 文件，将 `your_api_key_here` 替换为您的阿里云百炼API密钥：
```bat
set DASHSCOPE_API_KEY=your_actual_api_key_here
```

### 4. 启动服务

```cmd
start_server.bat
```

### 5. 访问应用

打开浏览器访问：http://localhost:5050

## 🧪 运行测试

```cmd
run_tests.bat
```

## 📚 文档

详细文档请查看 `docs/` 目录：
- [快速开始指南](docs/CareerNavigator%20快速开始指南.md)
- [API 文档](docs/CareerNavigator%20API%20文档.md)  
- [部署指南](docs/CareerNavigator%20部署指南.md)
- [完整文档索引](docs/README.md)

## 🔧 开发工具

项目提供了便捷的开发工具脚本：

### Windows 批处理脚本
- `start_server.bat` - 启动开发服务器
- `run_tests.bat` - 运行测试套件

### Python 开发工具
```cmd
python dev_tools.py
```
提供交互式菜单，包括：
- 启动开发服务器
- 运行测试
- 检查依赖
- 生成API文档

服务将在 http://localhost:5050 启动

## 🧪 测试

### 组件测试
```bash
python tests/test_components.py
```

### API测试
```bash
# 先启动后端服务
python main.py

## � 相关链接

- [阿里云百炼控制台](https://dashscope.console.aliyun.com/)
- [LangGraph 文档](https://python.langchain.com/docs/langgraph)
- [Flask 文档](https://flask.palletsprojects.com/)
- [React 文档](https://react.dev/)

## � 许可证

本项目采用 MIT 许可证。详情请查看 LICENSE 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进项目。

---

💡 **快速开始提示**: 如果您是首次使用，请直接运行 `start_server.bat` 并访问 http://localhost:5050
1. 检查日志文件
2. 运行健康检查 `GET /api/health`
3. 运行测试脚本验证功能

## 📄 许可证

MIT License

---

💡 **提示**: 使用 `python dev_tools.py` 获取更多开发工具和帮助！
