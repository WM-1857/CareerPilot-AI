# CareerNavigator API 文档

本文档详细描述了 CareerNavigator 智能职业规划系统的 RESTful API 接口。

## 基础信息

- **基础 URL**: `http://localhost:5050/api/career`
- **API 版本**: v1.0
- **内容类型**: `application/json`
- **字符编码**: UTF-8

## 认证

当前版本不需要认证，但建议在生产环境中实现适当的认证机制。

## 通用响应格式

### 成功响应
```json
{
  "success": true,
  "data": {},
  "message": "操作成功"
}
```

### 错误响应
```json
{
  "success": false,
  "error": "错误描述",
  "code": "ERROR_CODE"
}
```

## API 端点

### 1. 开始职业规划

启动新的职业规划会话。

**端点**: `POST /start`

**请求体**:
```json
{
  "user_profile": {
    "user_id": "string (可选)",
    "age": "integer (可选)",
    "education_level": "string (可选)",
    "work_experience": "integer (可选)",
    "current_position": "string (可选)",
    "industry": "string (可选)",
    "skills": ["string"] (可选),
    "interests": ["string"] (可选),
    "career_goals": "string (可选)",
    "location": "string (可选)",
    "salary_expectation": "string (可选)",
    "additional_info": {} (可选)
  },
  "message": "string (必需)"
}
```

**请求示例**:
```json
{
  "user_profile": {
    "age": 25,
    "education_level": "本科",
    "work_experience": 3,
    "current_position": "软件工程师",
    "industry": "互联网",
    "skills": ["Python", "React", "数据分析"],
    "interests": ["人工智能", "产品设计", "创业"],
    "career_goals": "成为AI产品经理",
    "location": "北京",
    "salary_expectation": "20-30k"
  },
  "message": "我希望从技术转向产品管理方向，请帮我制定详细的职业规划"
}
```

**响应示例**:
```json
{
  "success": true,
  "session_id": "uuid-string",
  "stage_info": {
    "current_stage": "initial",
    "stage_info": {
      "name": "初始化",
      "description": "系统正在初始化，准备开始职业规划分析",
      "next_action": "分析用户需求"
    },
    "iteration_count": 0,
    "max_iterations": 3,
    "requires_user_input": false,
    "pending_questions": []
  },
  "message": "职业规划已开始"
}
```

**状态码**:
- `200`: 成功
- `400`: 请求参数错误
- `500`: 服务器内部错误

---

### 2. 获取规划状态

获取指定会话的当前规划状态和结果。

**端点**: `GET /status/{session_id}`

**路径参数**:
- `session_id`: 会话ID (必需)

**响应示例**:
```json
{
  "session_id": "uuid-string",
  "stage_info": {
    "current_stage": "user_feedback",
    "stage_info": {
      "name": "用户反馈",
      "description": "等待用户对分析报告的反馈",
      "next_action": "收集用户意见"
    },
    "iteration_count": 1,
    "max_iterations": 3,
    "requires_user_input": true,
    "pending_questions": [
      "您对这份综合报告满意吗？请提供您的反馈或修改意见。"
    ]
  },
  "results": {
    "integrated_report": {
      "executive_summary": "基于您的背景分析...",
      "personal_analysis": "您具备强大的技术基础...",
      "industry_opportunities": "AI产品管理领域前景广阔...",
      "career_match": {
        "match_score": 85,
        "match_reasons": [
          "技术背景与AI产品需求高度匹配",
          "学习能力强，适合快速转型"
        ],
        "concerns": [
          "缺乏产品管理经验",
          "需要补充商业思维"
        ]
      },
      "development_plan": {
        "short_term": [
          "学习产品管理基础知识",
          "参与产品相关项目"
        ],
        "medium_term": [
          "获得产品管理认证",
          "积累用户研究经验"
        ],
        "long_term": [
          "成为资深AI产品经理",
          "建立行业影响力"
        ]
      },
      "action_items": [
        "报名产品管理课程",
        "阅读《人人都是产品经理》",
        "寻找产品实习机会"
      ],
      "risk_warnings": [
        "转型期间可能面临收入下降",
        "需要投入大量时间学习"
      ],
      "next_steps": [
        "制定详细学习计划",
        "开始网络建设"
      ]
    }
  }
}
```

**状态码**:
- `200`: 成功
- `404`: 会话不存在
- `500`: 服务器内部错误

---

### 3. 提交用户反馈

提交用户对当前阶段结果的反馈。

**端点**: `POST /feedback/{session_id}`

**路径参数**:
- `session_id`: 会话ID (必需)

**请求体**:
```json
{
  "satisfaction_level": "string (必需)",
  "feedback_text": "string (可选)"
}
```

**satisfaction_level 可选值**:
- `very_satisfied`: 非常满意
- `satisfied`: 满意
- `neutral`: 中性
- `dissatisfied`: 不满意
- `very_dissatisfied`: 非常不满意

**请求示例**:
```json
{
  "satisfaction_level": "satisfied",
  "feedback_text": "分析很全面，但希望能提供更具体的学习资源推荐"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "反馈已收到，进入下一阶段",
  "stage_info": {
    "current_stage": "goal_decomposition",
    "stage_info": {
      "name": "目标拆分",
      "description": "正在将职业目标拆分为具体的阶段性目标",
      "next_action": "制定目标"
    },
    "iteration_count": 1,
    "max_iterations": 3,
    "requires_user_input": false,
    "pending_questions": []
  }
}
```

**状态码**:
- `200`: 成功
- `400`: 请求参数错误
- `404`: 会话不存在
- `500`: 服务器内部错误

---

### 4. 获取完整报告

获取指定会话的完整分析报告。

**端点**: `GET /report/{session_id}`

**路径参数**:
- `session_id`: 会话ID (必需)

**响应示例**:
```json
{
  "session_id": "uuid-string",
  "user_profile": {
    "user_id": "user_123",
    "age": 25,
    "education_level": "本科",
    "work_experience": 3,
    "current_position": "软件工程师",
    "industry": "互联网",
    "skills": ["Python", "React", "数据分析"],
    "interests": ["人工智能", "产品设计", "创业"],
    "career_goals": "成为AI产品经理",
    "location": "北京",
    "salary_expectation": "20-30k"
  },
  "integrated_report": {
    "executive_summary": "综合分析摘要...",
    "personal_analysis": "个人能力分析...",
    "industry_opportunities": "行业机会分析...",
    "career_match": {
      "match_score": 85,
      "match_reasons": ["..."],
      "concerns": ["..."]
    },
    "development_plan": {
      "short_term": ["..."],
      "medium_term": ["..."],
      "long_term": ["..."]
    },
    "action_items": ["..."],
    "risk_warnings": ["..."],
    "next_steps": ["..."]
  },
  "career_goals": {
    "long_term_goals": [
      {
        "title": "成为资深AI产品经理",
        "description": "在AI领域建立专业声誉...",
        "timeline": "3-5年",
        "success_criteria": [
          "管理年收入超过1000万的AI产品",
          "在行业会议上发表演讲"
        ],
        "required_skills": [
          "深度学习理解",
          "商业战略思维"
        ],
        "milestones": [
          "获得高级产品经理职位",
          "成功推出AI产品"
        ]
      }
    ],
    "medium_term_goals": [
      {
        "title": "获得产品经理职位",
        "description": "成功转型为产品经理...",
        "timeline": "1-3年",
        "success_criteria": [
          "获得产品经理offer",
          "成功管理产品团队"
        ],
        "required_skills": [
          "产品设计",
          "用户研究"
        ],
        "milestones": [
          "完成产品管理培训",
          "获得产品实习经验"
        ]
      }
    ],
    "short_term_goals": [
      {
        "title": "掌握产品管理基础",
        "description": "学习产品管理核心技能...",
        "timeline": "3-12个月",
        "success_criteria": [
          "完成产品管理课程",
          "设计一个完整的产品方案"
        ],
        "required_skills": [
          "需求分析",
          "原型设计"
        ],
        "milestones": [
          "完成在线课程",
          "参与开源项目"
        ]
      }
    ]
  },
  "final_plan": {
    "schedule_overview": "为期12个月的转型计划...",
    "weekly_schedule": [
      {
        "week": 1,
        "focus_area": "产品管理基础学习",
        "tasks": [
          {
            "task": "阅读《人人都是产品经理》",
            "duration": "5小时",
            "priority": "高",
            "resources": ["书籍", "笔记本"]
          }
        ]
      }
    ],
    "monthly_milestones": [
      {
        "month": 1,
        "milestone": "完成产品管理基础学习",
        "deliverables": [
          "产品管理知识框架",
          "学习笔记整理"
        ],
        "success_metrics": [
          "通过在线测试",
          "完成案例分析"
        ]
      }
    ],
    "learning_plan": {
      "courses": [
        "产品经理实战课程",
        "用户体验设计",
        "数据分析与产品决策"
      ],
      "books": [
        "《人人都是产品经理》",
        "《用户体验要素》",
        "《精益创业》"
      ],
      "certifications": [
        "PMP项目管理认证",
        "Google产品管理证书"
      ]
    },
    "networking_plan": [
      "加入产品经理社群",
      "参加行业meetup",
      "寻找产品导师"
    ],
    "progress_tracking": [
      "每周学习进度回顾",
      "月度目标达成评估",
      "季度职业发展检查"
    ]
  },
  "analysis_results": {
    "self_insight": {
      "strengths": ["技术能力强", "学习能力强"],
      "weaknesses": ["产品经验不足", "商业思维待提升"],
      "personality_traits": ["逻辑思维", "创新意识"],
      "skill_assessment": {
        "technical_skills": ["Python", "数据分析"],
        "soft_skills": ["沟通能力", "团队协作"],
        "skill_gaps": ["产品设计", "市场分析"]
      },
      "career_interests": ["AI技术", "产品创新"],
      "development_potential": "具备很强的转型潜力",
      "recommendations": ["加强商业思维训练"]
    },
    "industry_research": {
      "industry_overview": "AI产品管理是新兴高增长领域",
      "current_status": "市场需求旺盛，人才稀缺",
      "future_trends": ["AI技术普及", "产品智能化"],
      "growth_drivers": ["技术进步", "市场需求"],
      "challenges": ["技术复杂性", "人才竞争"],
      "salary_analysis": {
        "entry_level": "15-25k",
        "mid_level": "25-40k",
        "senior_level": "40-80k"
      },
      "job_prospects": "前景广阔，增长迅速",
      "key_companies": ["字节跳动", "阿里巴巴", "腾讯"],
      "recommendations": ["关注AI技术发展趋势"]
    },
    "career_analysis": {
      "job_description": "负责AI产品的规划和管理",
      "key_responsibilities": [
        "产品需求分析",
        "技术方案评估",
        "用户体验设计"
      ],
      "required_skills": {
        "must_have": ["产品思维", "技术理解"],
        "nice_to_have": ["AI知识", "数据分析"]
      },
      "career_path": [
        "产品助理",
        "产品经理",
        "高级产品经理",
        "产品总监"
      ],
      "market_demand": "需求量大，竞争激烈",
      "ai_replacement_risk": {
        "risk_level": "低",
        "risk_factors": ["创意性工作"],
        "mitigation_strategies": ["提升战略思维"]
      },
      "user_match_score": 85,
      "gap_analysis": ["产品经验", "商业思维"],
      "recommendations": ["先从产品助理开始"]
    }
  },
  "system_metrics": {
    "response_time": 2.5,
    "mcp_call_success_rate": 0.95,
    "agent_success_rate": {
      "user_profiler": 1.0,
      "industry_researcher": 0.9,
      "job_analyzer": 0.95
    },
    "user_satisfaction_avg": 4.2,
    "iteration_count": 1,
    "max_iterations": 3,
    "memory_usage": 0.6,
    "concurrent_users": 1,
    "error_count": 0,
    "last_updated": "2024-01-15T10:30:00Z"
  },
  "generated_at": "2024-01-15T10:30:00Z"
}
```

**状态码**:
- `200`: 成功
- `404`: 会话不存在
- `500`: 服务器内部错误

---

### 5. 列出所有会话

获取所有活跃会话的列表（主要用于调试）。

**端点**: `GET /sessions`

**响应示例**:
```json
{
  "sessions": [
    {
      "session_id": "uuid-1",
      "user_id": "user_123",
      "current_stage": "completed",
      "created_at": "2024-01-15T09:00:00Z"
    },
    {
      "session_id": "uuid-2",
      "user_id": "user_456",
      "current_stage": "user_feedback",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 2
}
```

**状态码**:
- `200`: 成功
- `500`: 服务器内部错误

---

### 6. 健康检查

检查 API 服务的健康状态。

**端点**: `GET /health`

**响应示例**:
```json
{
  "status": "healthy",
  "service": "CareerNavigator API",
  "timestamp": "2024-01-15T10:30:00Z",
  "active_sessions": 5
}
```

**状态码**:
- `200`: 服务正常
- `503`: 服务不可用

## 数据模型

### UserProfile 用户画像
```json
{
  "user_id": "string",
  "age": "integer",
  "education_level": "string",
  "work_experience": "integer",
  "current_position": "string",
  "industry": "string",
  "skills": ["string"],
  "interests": ["string"],
  "career_goals": "string",
  "location": "string",
  "salary_expectation": "string",
  "additional_info": {}
}
```

### StageInfo 阶段信息
```json
{
  "current_stage": "string",
  "stage_info": {
    "name": "string",
    "description": "string",
    "next_action": "string"
  },
  "iteration_count": "integer",
  "max_iterations": "integer",
  "requires_user_input": "boolean",
  "pending_questions": ["string"]
}
```

### CareerGoal 职业目标
```json
{
  "title": "string",
  "description": "string",
  "timeline": "string",
  "success_criteria": ["string"],
  "required_skills": ["string"],
  "milestones": ["string"]
}
```

## 错误代码

| 错误代码 | HTTP状态码 | 描述 |
|----------|------------|------|
| `INVALID_REQUEST` | 400 | 请求参数无效 |
| `SESSION_NOT_FOUND` | 404 | 会话不存在 |
| `API_KEY_INVALID` | 401 | API密钥无效 |
| `RATE_LIMIT_EXCEEDED` | 429 | 请求频率超限 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |
| `SERVICE_UNAVAILABLE` | 503 | 服务不可用 |

## 使用示例

### JavaScript/Node.js
```javascript
const API_BASE = 'http://localhost:5050/api/career';

// 开始职业规划
async function startCareerPlanning(userProfile, message) {
  const response = await fetch(`${API_BASE}/start`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_profile: userProfile,
      message: message
    })
  });
  
  return await response.json();
}

// 获取状态
async function getStatus(sessionId) {
  const response = await fetch(`${API_BASE}/status/${sessionId}`);
  return await response.json();
}

// 提交反馈
async function submitFeedback(sessionId, satisfaction, feedback) {
  const response = await fetch(`${API_BASE}/feedback/${sessionId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      satisfaction_level: satisfaction,
      feedback_text: feedback
    })
  });
  
  return await response.json();
}
```

### Python
```python
import requests

API_BASE = 'http://localhost:5050/api/career'

def start_career_planning(user_profile, message):
    """开始职业规划"""
    response = requests.post(f'{API_BASE}/start', json={
        'user_profile': user_profile,
        'message': message
    })
    return response.json()

def get_status(session_id):
    """获取状态"""
    response = requests.get(f'{API_BASE}/status/{session_id}')
    return response.json()

def submit_feedback(session_id, satisfaction, feedback):
    """提交反馈"""
    response = requests.post(f'{API_BASE}/feedback/{session_id}', json={
        'satisfaction_level': satisfaction,
        'feedback_text': feedback
    })
    return response.json()

# 使用示例
user_profile = {
    'age': 25,
    'education_level': '本科',
    'work_experience': 3,
    'current_position': '软件工程师',
    'industry': '互联网',
    'skills': ['Python', 'React'],
    'career_goals': '成为AI产品经理'
}

result = start_career_planning(user_profile, '我想转型做产品经理')
session_id = result['session_id']

# 轮询状态
import time
while True:
    status = get_status(session_id)
    if status['stage_info']['requires_user_input']:
        # 提交反馈
        submit_feedback(session_id, 'satisfied', '很好的分析')
        break
    time.sleep(5)
```

### cURL
```bash
# 开始职业规划
curl -X POST http://localhost:5050/api/career/start \
  -H "Content-Type: application/json" \
  -d '{
    "user_profile": {
      "age": 25,
      "education_level": "本科",
      "current_position": "软件工程师",
      "career_goals": "成为AI产品经理"
    },
    "message": "我想转型做产品经理"
  }'

# 获取状态
curl http://localhost:5050/api/career/status/your-session-id

# 提交反馈
curl -X POST http://localhost:5050/api/career/feedback/your-session-id \
  -H "Content-Type: application/json" \
  -d '{
    "satisfaction_level": "satisfied",
    "feedback_text": "分析很详细，谢谢"
  }'
```

## 最佳实践

### 1. 错误处理
```javascript
async function apiCall(url, options) {
  try {
    const response = await fetch(url, options);
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || '请求失败');
    }
    
    return data;
  } catch (error) {
    console.error('API调用失败:', error);
    throw error;
  }
}
```

### 2. 状态轮询
```javascript
async function pollStatus(sessionId, callback) {
  const poll = async () => {
    try {
      const status = await getStatus(sessionId);
      callback(status);
      
      if (status.stage_info.current_stage !== 'completed') {
        setTimeout(poll, 5050); // 5秒后再次轮询
      }
    } catch (error) {
      console.error('轮询失败:', error);
      setTimeout(poll, 10000); // 错误时延长轮询间隔
    }
  };
  
  poll();
}
```

### 3. 请求重试
```javascript
async function retryRequest(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
}
```

## 版本历史

- **v1.0** (2024-01-15): 初始版本，包含基础职业规划功能
- **v1.1** (计划中): 添加用户认证和会话持久化
- **v1.2** (计划中): 支持多语言和国际化

## 支持与反馈

如果您在使用 API 时遇到问题或有改进建议，请通过以下方式联系我们：

- 技术文档: [文档链接]
- 问题反馈: [Issues链接]
- 邮件支持: support@careernavigator.com

---

**注意**: 本 API 目前处于开发阶段，接口可能会有变动。建议在生产环境使用前进行充分测试。

