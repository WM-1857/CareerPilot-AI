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
- Node.js 16+ (如果需要前端开发)

### 2. 安装依赖

```bash
# 安装Python依赖
pip install flask flask-cors requests langgraph dashscope

# 或使用开发工具脚本
python dev_tools.py
```

### 3. 配置环境变量

```bash
# Windows
set DASHSCOPE_API_KEY=your_actual_api_key
set FLASK_ENV=development
set LOG_LEVEL=DEBUG

# Linux/Mac
export DASHSCOPE_API_KEY=your_actual_api_key
export FLASK_ENV=development
export LOG_LEVEL=DEBUG
```

### 4. 启动服务

```bash
# 使用开发工具（推荐）
python dev_tools.py

# 或直接启动
python main.py
```

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

# 然后在另一个终端运行
python tests/test_backend.py
```

## 📋 API文档

### 健康检查
```
GET /api/health
```

### 开始职业规划
```
POST /api/career/start
Content-Type: application/json

{
  "user_profile": {
    "user_id": "string",
    "age": 25,
    "education_level": "本科",
    "work_experience": 2,
    "current_position": "软件工程师",
    "industry": "互联网",
    "skills": ["Python", "JavaScript"],
    "interests": ["技术管理"],
    "career_goals": "成为技术leader",
    "location": "北京",
    "salary_expectation": "20-30万"
  },
  "message": "我想制定一个3年的职业发展计划"
}
```

### 获取规划状态
```
GET /api/career/status/{session_id}
```

### 提交用户反馈
```
POST /api/career/feedback/{session_id}
Content-Type: application/json

{
  "satisfaction_level": "satisfied",
  "feedback_text": "分析结果很好，请继续"
}
```

## 🔧 开发指南

### 添加新功能

1. **添加新的API端点**: 在 `src/routes/career.py` 中添加
2. **添加新的工作流节点**: 在 `src/services/career_nodes.py` 中添加
3. **修改状态结构**: 在 `src/models/career_state.py` 中修改
4. **添加日志**: 使用 `src/utils/logger.py` 中的日志工具

### 调试技巧

1. **查看实时日志**: 日志会输出到控制台和 `logs/` 目录
2. **设置调试级别**: `set LOG_LEVEL=DEBUG`
3. **使用开发工具**: `python dev_tools.py`

## 📝 注意事项

1. **API密钥**: 需要设置有效的阿里云百炼API密钥
2. **内存存储**: 当前版本使用内存存储，重启服务会丢失会话数据
3. **并发限制**: 建议同时处理的会话数不超过100个

## 🔗 相关文档

- [部署指南](docs/CareerNavigator%20部署指南.md)
- [API文档](docs/CareerNavigator%20API%20文档.md)
- [项目设计报告](docs/CareerNavigator%20LangGraph%20项目设计报告.md)

## 📞 支持

如果遇到问题，请：
1. 检查日志文件
2. 运行健康检查 `GET /api/health`
3. 运行测试脚本验证功能

## 📄 许可证

MIT License

---

💡 **提示**: 使用 `python dev_tools.py` 获取更多开发工具和帮助！
