# CareerNavigator 状态字段参考手册

## 快速索引

| 字段类别 | 核心字段 | 生成节点 | 使用节点 | 类型 |
|---------|---------|----------|----------|------|
| **基础信息** | session_id | 初始化 | 全部 | str |
| | user_profile | 初始化 | 全部 | UserProfile |
| | current_stage | 初始化 | 全部 | WorkflowStage |
| | messages | 初始化 | 全部 | List[BaseMessage] |
| **规划策略** | planning_strategy | planner | supervisor+ | str |
| | cached_data | coordinator | planner+ | Dict |
| **任务管理** | agent_tasks | supervisor | 并行分析 | List[AgentTask] |
| | agent_outputs | 并行分析 | reporter+ | List[AgentOutput] |
| **分析结果** | self_insight_result | user_profiler | reporter+ | Dict |
| | industry_research_result | industry_researcher | reporter+ | Dict |
| | career_analysis_result | job_analyzer | reporter+ | Dict |
| | integrated_report | reporter | goal_decomposer+ | Dict |
| **用户交互** | user_feedback_history | 用户反馈 | supervisor+ | List[UserFeedback] |
| | current_satisfaction | 用户反馈 | 路由判断 | UserSatisfactionLevel |
| | requires_user_input | reporter,scheduler | 控制逻辑 | bool |
| | pending_questions | reporter,scheduler | 用户界面 | List[str] |
| **目标规划** | career_goals | goal_decomposer | scheduler | List[CareerGoal] |
| | final_plan | scheduler | 最终确认 | Dict |
| **系统控制** | iteration_count | 初始化 | 迭代控制 | int |
| | max_iterations | 初始化 | 迭代控制 | int |
| | system_metrics | 初始化 | 监控 | SystemMetrics |
| | error_log | 错误处理 | 调试 | List[Dict] |

## 详细字段说明

### 1. 基础信息字段

#### 1.1 session_id
```python
类型: str
作用: 唯一标识一个会话
生成: 初始化时UUID生成
示例: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
持久化: 整个会话生命周期
```

#### 1.2 user_profile
```python
类型: UserProfile (TypedDict)
结构: {
    "user_id": str,
    "age": Optional[int],
    "education_level": Optional[str],
    "work_experience": Optional[int],
    "current_position": Optional[str],
    "industry": Optional[str],
    "skills": Optional[List[str]],
    "interests": Optional[List[str]],
    "career_goals": Optional[str],
    "location": Optional[str],
    "salary_expectation": Optional[str],
    "additional_info": Optional[Dict[str, Any]]
}
```

#### 1.3 current_stage
```python
类型: WorkflowStage (Enum)
可选值:
- INITIAL: "initial"
- PLANNING: "planning"
- PARALLEL_ANALYSIS: "parallel_analysis"
- RESULT_INTEGRATION: "result_integration"
- USER_FEEDBACK: "user_feedback"
- GOAL_DECOMPOSITION: "goal_decomposition"
- SCHEDULE_PLANNING: "schedule_planning"
- FINAL_CONFIRMATION: "final_confirmation"
- COMPLETED: "completed"
```

#### 1.4 messages
```python
类型: Sequence[BaseMessage]
作用: 存储对话历史
初始: [HumanMessage(content="用户初始请求")]
更新: 系统响应时可能添加AI消息
```

### 2. 规划策略字段

#### 2.1 planning_strategy
```python
类型: Optional[str]
生成节点: planner_node
典型值: "制定个性化职业分析策略"
作用: 指导后续并行分析的策略方向
```

#### 2.2 cached_data
```python
类型: Optional[Dict[str, Any]]
生成节点: coordinator_node
典型结构: {
    "goal_analysis": {
        "is_goal_clear": bool,
        "clarity_score": int,
        "analysis_details": str
    }
}
```

### 3. 任务管理字段

#### 3.1 agent_tasks
```python
类型: Annotated[List[AgentTask], operator.add]
注解: 支持并发添加
结构: [
    {
        "task_id": str,
        "agent_name": str,  # "user_profiler_node", "industry_researcher_node", "job_analyzer_node"
        "task_type": str,   # "个人分析", "行业研究", "职业分析"
        "priority": int,    # 1-5
        "description": str,
        "input_data": Dict[str, Any],
        "status": AgentStatus,  # IDLE, WORKING, COMPLETED, FAILED, WAITING_FEEDBACK
        "created_at": datetime,
        "started_at": Optional[datetime],
        "completed_at": Optional[datetime],
        "deadline": Optional[datetime],
        "dependencies": Optional[List[str]]
    }
]
```

#### 3.2 agent_outputs
```python
类型: Annotated[List[AgentOutput], operator.add]
注解: 支持并发添加
结构: [
    {
        "agent_name": str,
        "task_id": str,
        "output_type": str,  # "个人画像", "行业报告", "职业建议"
        "content": Dict[str, Any],
        "confidence_score": float,  # 0-1
        "data_sources": List[str],
        "analysis_method": str,
        "timestamp": datetime,
        "quality_metrics": Dict[str, float],
        "recommendations": Optional[List[str]],
        "warnings": Optional[List[str]]
    }
]
```

### 4. 分析结果字段

#### 4.1 self_insight_result
```python
类型: Optional[Dict[str, Any]]
生成节点: user_profiler_node
典型结构: {
    "strengths": List[str],
    "improvement_areas": List[str],
    "personality_analysis": Dict,
    "skill_assessment": Dict,
    "iteration_info": {
        "iteration_count": int,
        "adjustments_applied": Dict,
        "analysis_timestamp": str
    },
    "recommendations": List[str]
}
```

#### 4.2 industry_research_result
```python
类型: Optional[Dict[str, Any]]
生成节点: industry_researcher_node
典型结构: {
    "industry_trends": List[str],
    "market_analysis": Dict,
    "growth_opportunities": List[str],
    "challenges": List[str],
    "market_data": Dict,  # 来自MCP API
    "iteration_info": {
        "iteration_count": int,
        "adjustments_applied": Dict,
        "research_timestamp": str
    }
}
```

#### 4.3 career_analysis_result
```python
类型: Optional[Dict[str, Any]]
生成节点: job_analyzer_node
典型结构: {
    "career_paths": List[Dict],
    "skill_gaps": List[str],
    "salary_analysis": Dict,
    "job_market_data": Dict,  # 来自MCP API
    "career_progression": Dict,
    "iteration_info": {
        "iteration_count": int,
        "adjustments_applied": Dict,
        "analysis_timestamp": str
    }
}
```

#### 4.4 integrated_report
```python
类型: Optional[Dict[str, Any]]
生成节点: reporter_node
典型结构: {
    "executive_summary": str,
    "career_match": {
        "recommended_career": str,
        "match_score": float,
        "justification": str
    },
    "key_findings": List[str],
    "recommendations": List[str],
    "action_priorities": List[str],
    "iteration_summary": str,  # 仅在迭代时
    "iteration_count": int
}
```

### 5. 用户交互字段

#### 5.1 user_feedback_history
```python
类型: List[UserFeedback]
结构: [
    {
        "feedback_id": str,
        "stage": WorkflowStage,
        "satisfaction_level": UserSatisfactionLevel,
        "specific_feedback": Dict[str, str],
        "improvement_requests": List[str],
        "additional_requirements": Optional[List[str]],
        "timestamp": datetime,
        "feedback_text": Optional[str]
    }
]
累积性: 每次用户反馈都会添加到历史中
```

#### 5.2 current_satisfaction
```python
类型: Optional[UserSatisfactionLevel]
可选值:
- VERY_SATISFIED: "very_satisfied"
- SATISFIED: "satisfied"
- NEUTRAL: "neutral"
- DISSATISFIED: "dissatisfied"
- VERY_DISSATISFIED: "very_dissatisfied"
路由影响: 决定是否继续下一阶段或重新迭代
```

#### 5.3 requires_user_input
```python
类型: bool
设置节点: reporter_node, scheduler_node
作用: 控制工作流是否暂停等待用户输入
相关字段: pending_questions
```

#### 5.4 pending_questions
```python
类型: Optional[List[str]]
典型值: [
    "您对这份综合报告满意吗？请提供您的反馈或修改意见。",
    "这是为您生成的最终行动计划，您是否满意？"
]
```

### 6. 目标规划字段

#### 6.1 career_goals
```python
类型: Optional[List[CareerGoal]]
生成节点: goal_decomposer_node
结构: [
    {
        "goal_id": str,
        "goal_type": "long_term" | "medium_term" | "short_term",
        "title": str,
        "description": str,
        "target_date": datetime,
        "success_criteria": List[str],
        "required_skills": List[str],
        "required_resources": List[str],
        "milestones": List[Dict[str, Any]],
        "dependencies": Optional[List[str]],
        "priority": int,
        "progress": float  # 0-1
    }
]
```

#### 6.2 final_plan
```python
类型: Optional[Dict[str, Any]]
生成节点: scheduler_node
典型结构: {
    "schedule_overview": str,
    "action_items": List[ScheduleItem],
    "timeline": Dict,
    "resources": List[str],
    "milestones": List[Dict],
    "budget_estimation": Optional[Dict],
    "risk_assessment": Optional[List[str]]
}
```

### 7. 系统控制字段

#### 7.1 iteration_count
```python
类型: int
初始值: 0
递增: 每次用户反馈不满意时+1
限制: 受max_iterations控制
作用: 迭代控制和质量递增
```

#### 7.2 max_iterations
```python
类型: int
默认值: 3
作用: 防止无限迭代循环
检查: 在路由判断时检查是否达到限制
```

#### 7.3 system_metrics
```python
类型: SystemMetrics
结构: {
    "response_time": float,
    "mcp_call_success_rate": float,
    "agent_success_rate": Dict[str, float],
    "user_satisfaction_avg": float,
    "iteration_count": int,
    "max_iterations": int,
    "memory_usage": float,
    "concurrent_users": int,
    "error_count": int,
    "last_updated": datetime
}
```

#### 7.4 error_log
```python
类型: Annotated[List[Dict[str, Any]], operator.add]
注解: 支持并发添加
结构: [
    {
        "error": str,
        "timestamp": datetime,
        "session_id": str,
        "stage": WorkflowStage,
        "node_name": Optional[str],
        "error_type": Optional[str],
        "stack_trace": Optional[str]
    }
]
```

### 8. 辅助字段

#### 8.1 is_analysis_complete
```python
类型: bool
作用: 标记并行分析是否完成
检查: 所有分析结果字段是否非空
```

#### 8.2 is_planning_complete
```python
类型: bool
作用: 标记规划是否完成
检查: 最终计划是否生成
```

#### 8.3 can_proceed_to_next_stage
```python
类型: bool
作用: 标记是否可以进入下一阶段
检查: 当前阶段必要条件是否满足
```

### 9. 缓存与性能字段

#### 9.1 mcp_call_history
```python
类型: List[Dict[str, Any]]
作用: 记录MCP API调用历史
结构: [
    {
        "api_name": str,
        "request_data": Dict,
        "response_data": Dict,
        "timestamp": datetime,
        "success": bool,
        "response_time": float
    }
]
```

#### 9.2 performance_logs
```python
类型: List[Dict[str, Any]]
作用: 性能监控日志
结构: [
    {
        "node_name": str,
        "execution_time": float,
        "memory_before": float,
        "memory_after": float,
        "timestamp": datetime
    }
]
```

## 字段生命周期管理

### 初始化时创建
- session_id, user_profile, current_stage, messages
- iteration_count=0, max_iterations=3
- 各种空列表和None值

### 执行过程中创建
- planning_strategy (planner)
- agent_tasks (supervisor)
- 分析结果字段 (并行分析)
- integrated_report (reporter)
- career_goals (goal_decomposer)
- final_plan (scheduler)

### 用户交互时更新
- user_feedback_history (累积)
- current_satisfaction (覆盖)
- iteration_count (递增)

### 系统监控字段
- system_metrics (持续更新)
- error_log (累积)
- performance_logs (累积)

## 字段验证规则

### 必要字段检查
```python
def validate_required_fields(state, stage):
    rules = {
        WorkflowStage.PARALLEL_ANALYSIS: ["planning_strategy", "agent_tasks"],
        WorkflowStage.RESULT_INTEGRATION: ["self_insight_result", "industry_research_result", "career_analysis_result"],
        WorkflowStage.GOAL_DECOMPOSITION: ["integrated_report"],
        WorkflowStage.SCHEDULE_PLANNING: ["career_goals"],
        WorkflowStage.FINAL_CONFIRMATION: ["final_plan"]
    }
    
    required = rules.get(stage, [])
    missing = [field for field in required if not state.get(field)]
    return missing
```

### 数据类型检查
```python
def validate_field_types(state):
    type_rules = {
        "session_id": str,
        "iteration_count": int,
        "max_iterations": int,
        "requires_user_input": bool,
        "agent_tasks": list,
        "agent_outputs": list,
        "user_feedback_history": list,
        "error_log": list
    }
    
    errors = []
    for field, expected_type in type_rules.items():
        if field in state and not isinstance(state[field], expected_type):
            errors.append(f"{field}: expected {expected_type}, got {type(state[field])}")
    
    return errors
```

## 常用操作示例

### 添加用户反馈
```python
def add_user_feedback(state, satisfaction, feedback_text):
    feedback = UserFeedback(
        feedback_id=str(uuid.uuid4()),
        stage=state["current_stage"],
        satisfaction_level=satisfaction,
        feedback_text=feedback_text,
        timestamp=datetime.now()
    )
    
    updated_state = state.copy()
    updated_state["user_feedback_history"].append(feedback)
    updated_state["current_satisfaction"] = satisfaction
    updated_state["iteration_count"] += 1
    
    return updated_state
```

### 检查状态完整性
```python
def check_state_integrity(state):
    critical_fields = ["session_id", "user_profile", "current_stage", "messages"]
    missing = [f for f in critical_fields if f not in state]
    
    if missing:
        print(f"⚠️ 缺失关键字段: {missing}")
        return False
    
    return True
```

### 清理历史数据
```python
def cleanup_state(state, max_history=10):
    """清理过长的历史数据"""
    if len(state.get("performance_logs", [])) > max_history:
        state["performance_logs"] = state["performance_logs"][-max_history:]
    
    if len(state.get("mcp_call_history", [])) > max_history:
        state["mcp_call_history"] = state["mcp_call_history"][-max_history:]
    
    return state
```

---

这份参考手册提供了CareerNavigator状态管理的完整技术规范，可作为开发、调试和维护的快速参考工具。
