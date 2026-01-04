# CareerNavigator API 参考手册

本文档详细介绍了 CareerNavigator 后端提供的 RESTful API 接口。

## 基础信息

- **基础 URL**: `http://localhost:5050/api/career`
- **内容类型**: `application/json`

## 接口列表

### 1. 健康检查
检查服务运行状态。

- **URL**: `/health`
- **方法**: `GET`
- **响应**:
  ```json
  {
    "status": "healthy",
    "service": "CareerNavigator API",
    "timestamp": "2026-01-04T...",
    "active_sessions": 0
  }
  ```

### 2. 开始职业规划
初始化一个新的规划会话。

- **URL**: `/start`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "user_profile": {
      "user_id": "string (可选)",
      "age": 25,
      "education_level": "本科",
      "work_experience": 3,
      "current_position": "软件工程师",
      "industry": "互联网",
      "skills": ["Python", "React"],
      "interests": ["AI"],
      "career_goals": "成为AI架构师",
      "location": "北京",
      "salary_expectation": "30k"
    },
    "message": "请帮我规划职业路径"
  }
  ```
- **响应**:
  ```json
  {
    "success": true,
    "session_id": "uuid-string",
    "message": "会话已创建，准备开始规划"
  }
  ```

### 3. 流式进度获取 (SSE)
实时获取工作流的执行进度和结果。

- **URL**: `/stream?session_id=<session_id>`
- **方法**: `GET`
- **说明**: 使用 Server-Sent Events (SSE) 协议。

### 4. 提交用户反馈
在人工干预节点提交反馈。

- **URL**: `/feedback/<session_id>`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "satisfaction_level": "satisfied|dissatisfied|neutral|very_satisfied|very_dissatisfied",
    "feedback_text": "我觉得分析得很准，请继续"
  }
  ```

### 5. 获取当前状态
获取会话的当前阶段和已生成的结果。

- **URL**: `/status/<session_id>`
- **方法**: `GET`
- **响应示例**:
  ```json
  {
    "session_id": "uuid-string",
    "stage_info": {
      "current_stage": "user_feedback",
      "requires_user_input": true,
      "pending_questions": ["您对目前的薪资满意吗？"],
      "iteration_count": 1,
      "max_iterations": 3
    },
    "results": {
      "integrated_report": { ... }
    }
  }
  ```

### 6. 获取完整报告
获取会话的所有分析和规划结果。

- **URL**: `/report/<session_id>`
- **方法**: `GET`

### 7. 上传简历 (OCR)
上传简历图片并提取信息。

- **URL**: `/upload-resume`
- **方法**: `POST`
- **请求**: `multipart/form-data` 包含 `file` 字段。
- **响应**: 提取出的用户信息 JSON。

### 8. 列出所有会话 (调试用)
- **URL**: `/sessions`
- **方法**: `GET`
