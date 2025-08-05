# CareerNavigator - 智能职业规划助手

基于 LangGraph 和阿里云百炼 API 的智能职业规划系统，为用户提供个性化的职业发展建议和行动计划。

## 项目概述

CareerNavigator 是一个完整的全栈应用，采用现代化的技术栈构建：

- **后端**: Flask + LangGraph + 阿里云百炼 API
- **前端**: React + Tailwind CSS + shadcn/ui
- **架构**: 基于状态机的智能工作流

## 核心功能

### 🎯 智能分析
- 个人能力画像分析
- 行业趋势研究
- 职业机会评估
- 综合匹配度评估

### 📋 目标规划
- 长期、中期、短期目标拆分
- SMART 原则目标制定
- 个性化发展路径

### 📅 行动计划
- 详细的时间安排
- 学习发展建议
- 人脉建设指导
- 进度跟踪方法

### 🔄 迭代优化
- 用户反馈收集
- 智能调整建议
- 多轮优化机制

## 技术架构

### 后端架构
```
Flask Application
├── LangGraph 工作流引擎
├── 阿里云百炼 API 集成
├── 状态管理系统
└── RESTful API 接口
```

### 前端架构
```
React Application
├── 用户信息表单
├── 进度展示组件
├── 结果展示组件
└── 反馈交互组件
```

### 工作流设计
```
协调员 → 计划员 → 管理员 → [并行分析] → 汇报员 → 目标拆分 → 日程规划
```

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 20+
- pnpm
- 阿里云百炼 API 密钥

### 安装步骤（Windows环境）

1. **克隆项目**
```cmd
git clone <repository-url>
cd CareerNavigator
```

2. **环境设置**
```cmd
# 安装Python依赖
pip install -r requirements.txt
```

3. **前端设置**
```cmd
cd frontend
npm install
```

4. **环境配置**
```cmd
# 设置阿里云百炼 API 密钥
set DASHSCOPE_API_KEY=your_api_key_here
```

### 本地运行

1. **启动后端服务（推荐使用批处理脚本）**
```cmd
start_server.bat
```

或手动启动：
```cmd
set DASHSCOPE_API_KEY=your_api_key_here
python main.py
```

2. **访问应用**
- 前端: http://localhost:5050 (静态文件服务)
- 后端 API: http://localhost:5050/api
- 健康检查: http://localhost:5050/api/health

## API 文档

### 开始职业规划
```http
POST /api/career/start
Content-Type: application/json

{
  "user_profile": {
    "user_id": "string",
    "age": 25,
    "education_level": "本科",
    "work_experience": 3,
    "current_position": "软件工程师",
    "industry": "互联网",
    "skills": ["Python", "React"],
    "interests": ["AI", "产品设计"],
    "career_goals": "成为AI产品经理",
    "location": "北京",
    "salary_expectation": "20-30k"
  },
  "message": "我希望从技术转向产品管理方向"
}
```

### 获取规划状态
```http
GET /api/career/status/{session_id}
```

### 提交用户反馈
```http
POST /api/career/feedback/{session_id}
Content-Type: application/json

{
  "satisfaction_level": "satisfied|dissatisfied|neutral",
  "feedback_text": "具体反馈内容"
}
```

### 获取完整报告
```http
GET /api/career/report/{session_id}
```

## 部署指南

### 本地测试部署

1. **构建前端**
```bash
cd career_navigator_frontend
pnpm run build
```

2. **复制前端文件到后端**
```bash
cp -r dist/* ../career_navigator_backend/src/static/
```

3. **启动完整应用**
```bash
cd ../career_navigator_backend
source venv/bin/activate
python src/main.py
```

### 生产环境部署

详细的生产环境部署指南请参考 [DEPLOYMENT.md](./DEPLOYMENT.md)

## 项目结构

```
career_navigator_project/
├── career_navigator_backend/          # Flask 后端
│   ├── src/
│   │   ├── models/                   # 数据模型
│   │   │   ├── career_state.py       # 状态定义
│   │   │   └── user.py              # 用户模型
│   │   ├── services/                 # 业务服务
│   │   │   ├── llm_service.py        # 百炼API服务
│   │   │   ├── career_nodes.py       # LangGraph节点
│   │   │   └── career_graph.py       # 工作流定义
│   │   ├── routes/                   # API路由
│   │   │   ├── career.py            # 职业规划API
│   │   │   └── user.py              # 用户API
│   │   ├── static/                   # 静态文件
│   │   └── main.py                   # 应用入口
│   ├── venv/                        # Python虚拟环境
│   └── requirements.txt             # Python依赖
├── career_navigator_frontend/        # React 前端
│   ├── src/
│   │   ├── components/              # React组件
│   │   │   ├── UserProfileForm.jsx   # 用户表单
│   │   │   ├── PlanningProgress.jsx  # 进度展示
│   │   │   └── ResultDisplay.jsx     # 结果展示
│   │   ├── App.jsx                  # 主应用
│   │   └── main.jsx                 # 入口文件
│   ├── public/                      # 公共资源
│   └── package.json                 # 前端依赖
├── README.md                        # 项目说明
└── DEPLOYMENT.md                    # 部署文档
```

## 开发指南

### 添加新的分析节点

1. 在 `career_nodes.py` 中定义新节点函数
2. 在 `career_graph.py` 中注册节点
3. 更新状态定义和路由逻辑

### 扩展前端组件

1. 在 `src/components/` 中创建新组件
2. 使用 shadcn/ui 组件库保持一致性
3. 更新主应用的状态管理

### 集成新的 LLM 服务

1. 在 `llm_service.py` 中添加新的服务类
2. 实现统一的接口规范
3. 更新节点中的调用逻辑

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交变更
4. 发起 Pull Request

## 许可证

MIT License

## 联系方式

- 项目维护者: Manus AI
- 技术支持: [技术文档](./docs/)
- 问题反馈: [Issues](./issues/)

---

**让 AI 为您的职业发展保驾护航！**

