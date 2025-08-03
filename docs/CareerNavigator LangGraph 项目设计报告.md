# CareerNavigator LangGraph 项目设计报告

## 1. 引言

本报告旨在详细阐述基于 LangGraph 框架的 CareerNavigator 职业生涯规划多智能体系统的状态（State）设计和原子化节点（Node）实现。我们将结合用户提供的流程图和详细文档，确保系统能够高效、灵活地处理复杂的职业规划任务，并支持多轮交互和迭代修正。

## 2. 状态（State）设计

LangGraph 的核心在于其状态管理。一个清晰、全面的 `State` 定义是构建健壮工作流的基础。我们采用 `TypedDict` 来定义 `CareerNavigatorState`，确保类型安全和结构清晰。此外，我们还定义了多个辅助 `TypedDict` 和 `Enum`，以更好地组织和管理复杂数据。

### 2.1 核心状态 `CareerNavigatorState`

`CareerNavigatorState` 包含了整个职业规划过程中所有需要共享和更新的信息，包括用户基础信息、任务管理、分析结果、用户交互历史、目标规划、系统控制和性能指标等。

```python
from typing import TypedDict, List, Dict, Optional, Sequence, Literal, Any
from langchain_core.messages import BaseMessage
from datetime import datetime
from enum import Enum


class WorkflowStage(Enum):
    """工作流程阶段枚举"""
    INITIAL = "initial"                    # 初始阶段
    PLANNING = "planning"                  # 策略制定阶段
    PARALLEL_ANALYSIS = "parallel_analysis"  # 并行分析阶段
    RESULT_INTEGRATION = "result_integration"  # 结果整合阶段
    USER_FEEDBACK = "user_feedback"        # 用户反馈阶段
    GOAL_DECOMPOSITION = "goal_decomposition"  # 目标拆分阶段
    SCHEDULE_PLANNING = "schedule_planning"    # 日程规划阶段
    FINAL_CONFIRMATION = "final_confirmation"  # 最终确认阶段
    COMPLETED = "completed"                # 完成阶段


class AgentStatus(Enum):
    """智能体状态枚举"""
    IDLE = "idle"                         # 空闲
    WORKING = "working"                   # 工作中
    COMPLETED = "completed"               # 已完成
    FAILED = "failed"                     # 失败
    WAITING_FEEDBACK = "waiting_feedback"  # 等待反馈


class UserSatisfactionLevel(Enum):
    """用户满意度级别"""
    VERY_SATISFIED = "very_satisfied"     # 非常满意
    SATISFIED = "satisfied"               # 满意
    NEUTRAL = "neutral"                   # 中性
    DISSATISFIED = "dissatisfied"         # 不满意
    VERY_DISSATISFIED = "very_dissatisfied"  # 非常不满意


# 用户基础信息结构
class UserProfile(TypedDict):
    """用户基础信息"""
    user_id: str                          # 用户ID
    age: Optional[int]                    # 年龄
    education_level: Optional[str]        # 学历水平
    work_experience: Optional[int]        # 工作经验年数
    current_position: Optional[str]       # 当前职位
    industry: Optional[str]               # 所在行业
    skills: Optional[List[str]]           # 技能列表
    interests: Optional[List[str]]        # 兴趣爱好
    career_goals: Optional[str]           # 职业目标
    location: Optional[str]               # 所在地区
    salary_expectation: Optional[str]     # 薪资期望
    additional_info: Optional[Dict[str, Any]]  # 其他补充信息


# 任务分发结构
class AgentTask(TypedDict):
    """智能体任务结构"""
    task_id: str                          # 任务ID
    agent_name: str                       # 智能体名称
    task_type: str                        # 任务类型
    priority: int                         # 优先级 (1-5)
    description: str                      # 任务描述
    input_data: Dict[str, Any]           # 输入数据
    deadline: Optional[datetime]          # 截止时间
    dependencies: Optional[List[str]]     # 依赖任务
    status: AgentStatus                   # 任务状态
    created_at: datetime                  # 创建时间
    started_at: Optional[datetime]        # 开始时间
    completed_at: Optional[datetime]      # 完成时间


# 智能体输出结果结构
class AgentOutput(TypedDict):
    """智能体输出结果"""
    agent_name: str                       # 智能体名称
    task_id: str                          # 对应任务ID
    output_type: str                      # 输出类型
    content: Dict[str, Any]              # 输出内容
    confidence_score: float               # 置信度分数 (0-1)
    data_sources: List[str]              # 数据来源
    analysis_method: str                  # 分析方法
    timestamp: datetime                   # 输出时间
    quality_metrics: Dict[str, float]    # 质量指标
    recommendations: Optional[List[str]]  # 建议列表
    warnings: Optional[List[str]]        # 警告信息


# 用户反馈结构
class UserFeedback(TypedDict):
    """用户反馈结构"""
    feedback_id: str                      # 反馈ID
    stage: WorkflowStage                  # 反馈阶段
    satisfaction_level: UserSatisfactionLevel  # 满意度级别
    specific_feedback: Dict[str, str]     # 具体反馈内容
    improvement_requests: List[str]       # 改进要求
    additional_requirements: Optional[List[str]]  # 额外需求
    timestamp: datetime                   # 反馈时间
    feedback_text: Optional[str]          # 文本反馈


# 目标拆分结构
class CareerGoal(TypedDict):
    """职业目标结构"""
    goal_id: str                          # 目标ID
    goal_type: Literal["long_term", "medium_term", "short_term"]  # 目标类型
    title: str                            # 目标标题
    description: str                      # 目标描述
    target_date: datetime                 # 目标日期
    success_criteria: List[str]           # 成功标准
    required_skills: List[str]            # 所需技能
    required_resources: List[str]         # 所需资源
    milestones: List[Dict[str, Any]]     # 里程碑
    dependencies: Optional[List[str]]     # 依赖关系
    priority: int                         # 优先级
    progress: float                       # 进度 (0-1)


# 日程计划结构
class ScheduleItem(TypedDict):
    """日程项目结构"""
    item_id: str                          # 项目ID
    title: str                            # 标题
    description: str                      # 描述
    start_time: datetime                  # 开始时间
    end_time: datetime                    # 结束时间
    item_type: Literal["learning", "practice", "networking", "application"]  # 项目类型
    related_goal_id: str                  # 关联目标ID
    priority: int                         # 优先级
    status: Literal["planned", "in_progress", "completed", "cancelled"]  # 状态
    reminders: List[datetime]             # 提醒时间
    resources: List[str]                  # 相关资源


# 系统性能监控结构
class SystemMetrics(TypedDict):
    """系统性能指标"""
    response_time: float                  # 响应时间(秒)
    mcp_call_success_rate: float         # MCP调用成功率
    agent_success_rate: Dict[str, float] # 各智能体成功率
    user_satisfaction_avg: float         # 用户满意度平均值
    iteration_count: int                  # 当前迭代次数
    max_iterations: int                   # 最大迭代次数
    memory_usage: float                   # 内存使用率
    concurrent_users: int                 # 并发用户数
    error_count: int                      # 错误计数
    last_updated: datetime                # 最后更新时间


# 主要的图状态结构
class CareerNavigatorState(TypedDict):
    """
    CareerNavigator 系统的主要状态结构
    
    这个状态将在整个LangGraph工作流中传递和更新，包含了系统运行的所有关键信息。
    """
    
    # === 基础信息 ===
    session_id: str                       # 会话ID
    user_profile: UserProfile             # 用户基础信息
    current_stage: WorkflowStage          # 当前工作流阶段
    messages: Sequence[BaseMessage]       # 对话历史
    
    # === 任务管理 ===
    planning_strategy: Optional[str]      # 规划策略
    agent_tasks: List[AgentTask]         # 智能体任务列表
    agent_outputs: List[AgentOutput]     # 智能体输出结果
    
    # === 分析结果 ===
    self_insight_result: Optional[Dict[str, Any]]      # 自我洞察结果
    industry_research_result: Optional[Dict[str, Any]] # 行业研究结果
    career_analysis_result: Optional[Dict[str, Any]]   # 职业分析结果
    integrated_report: Optional[Dict[str, Any]]        # 综合分析报告
    
    # === 用户交互 ===
    user_feedback_history: List[UserFeedback]          # 用户反馈历史
    current_satisfaction: Optional[UserSatisfactionLevel]  # 当前满意度
    pending_questions: Optional[List[str]]              # 待回答问题
    
    # === 目标规划 ===
    career_goals: Optional[List[CareerGoal]]           # 职业目标列表
    schedule_items: Optional[List[ScheduleItem]]       # 日程安排项目
    final_plan: Optional[Dict[str, Any]]               # 最终规划方案
    
    # === 系统控制 ===
    iteration_count: int                               # 迭代次数
    max_iterations: int                                # 最大迭代次数
    system_metrics: SystemMetrics                      # 系统性能指标
    error_log: List[Dict[str, Any]]                   # 错误日志
    
    # === 状态标志 ===
    is_analysis_complete: bool                         # 分析是否完成
    is_planning_complete: bool                         # 规划是否完成
    requires_user_input: bool                          # 是否需要用户输入
    can_proceed_to_next_stage: bool                   # 是否可以进入下一阶段
    
    # === 缓存和优化 ===
    cached_data: Optional[Dict[str, Any]]             # 缓存数据
    mcp_call_history: List[Dict[str, Any]]            # MCP调用历史
    performance_logs: List[Dict[str, Any]]            # 性能日志


# 状态更新辅助函数
class StateUpdater:
    """状态更新辅助类"""
    
    @staticmethod
    def update_stage(state: CareerNavigatorState, new_stage: WorkflowStage) -> Dict[str, Any]:
        """更新工作流阶段"""
        return {
            "current_stage": new_stage,
            "system_metrics": {
                **state["system_metrics"],
                "last_updated": datetime.now()
            }
        }
    
    @staticmethod
    def add_agent_task(state: CareerNavigatorState, task: AgentTask) -> Dict[str, Any]:
        """添加智能体任务"""
        updated_tasks = state["agent_tasks"].copy()
        updated_tasks.append(task)
        return {"agent_tasks": updated_tasks}
    
    @staticmethod
    def update_agent_status(state: CareerNavigatorState, task_id: str, 
                          new_status: AgentStatus) -> Dict[str, Any]:
        """更新智能体任务状态"""
        updated_tasks = []
        for task in state["agent_tasks"]:
            if task["task_id"] == task_id:
                task["status"] = new_status
                if new_status == AgentStatus.COMPLETED:
                    task["completed_at"] = datetime.now()
                elif new_status == AgentStatus.WORKING:
                    task["started_at"] = datetime.now()
            updated_tasks.append(task)
        return {"agent_tasks": updated_tasks}
    
    @staticmethod
    def add_agent_output(state: CareerNavigatorState, output: AgentOutput) -> Dict[str, Any]:
        """添加智能体输出结果"""
        updated_outputs = state["agent_outputs"].copy()
        updated_outputs.append(output)
        return {"agent_outputs": updated_outputs}
    
    @staticmethod
    def add_user_feedback(state: CareerNavigatorState, feedback: UserFeedback) -> Dict[str, Any]:
        """添加用户反馈"""
        updated_feedback = state["user_feedback_history"].copy()
        updated_feedback.append(feedback)
        return {
            "user_feedback_history": updated_feedback,
            "current_satisfaction": feedback["satisfaction_level"]
        }
    
    @staticmethod
    def increment_iteration(state: CareerNavigatorState) -> Dict[str, Any]:
        """增加迭代次数"""
        new_count = state["iteration_count"] + 1
        return {
            "iteration_count": new_count,
            "system_metrics": {
                **state["system_metrics"],
                "iteration_count": new_count,
                "last_updated": datetime.now()
            }
        }
    
    @staticmethod
    def check_iteration_limit(state: CareerNavigatorState) -> bool:
        """检查是否达到迭代限制"""
        return state["iteration_count"] >= state["max_iterations"]
    
    @staticmethod
    def set_user_input_required(state: CareerNavigatorState, required: bool, 
                              questions: Optional[List[str]] = None) -> Dict[str, Any]:
        """设置是否需要用户输入"""
        update_dict = {"requires_user_input": required}
        if questions:
            update_dict["pending_questions"] = questions
        return update_dict
    
    @staticmethod
    def log_error(state: CareerNavigatorState, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """记录错误信息"""
        updated_errors = state["error_log"].copy()
        error_entry = {
            **error_info,
            "timestamp": datetime.now(),
            "session_id": state["session_id"]
        }
        updated_errors.append(error_entry)
        
        # 更新系统指标中的错误计数
        updated_metrics = state["system_metrics"].copy()
        updated_metrics["error_count"] += 1
        updated_metrics["last_updated"] = datetime.now()
        
        return {
            "error_log": updated_errors,
            "system_metrics": updated_metrics
        }


# 状态验证器
class StateValidator:
    """状态验证器"""
    
    @staticmethod
    def validate_state_transition(current_stage: WorkflowStage, 
                                 target_stage: WorkflowStage) -> bool:
        """验证状态转换是否合法"""
        valid_transitions = {
            WorkflowStage.INITIAL: [WorkflowStage.PLANNING],
            WorkflowStage.PLANNING: [WorkflowStage.PARALLEL_ANALYSIS],
            WorkflowStage.PARALLEL_ANALYSIS: [WorkflowStage.RESULT_INTEGRATION],
            WorkflowStage.RESULT_INTEGRATION: [WorkflowStage.USER_FEEDBACK],
            WorkflowStage.USER_FEEDBACK: [
                WorkflowStage.GOAL_DECOMPOSITION,  # 满意时
                WorkflowStage.PLANNING              # 不满意时，重新规划
            ],
            WorkflowStage.GOAL_DECOMPOSITION: [WorkflowStage.SCHEDULE_PLANNING],
            WorkflowStage.SCHEDULE_PLANNING: [WorkflowStage.FINAL_CONFIRMATION],
            WorkflowStage.FINAL_CONFIRMATION: [
                WorkflowStage.COMPLETED,            # 满意时
                WorkflowStage.SCHEDULE_PLANNING     # 不满意时，重新规划
            ]
        }
        
        return target_stage in valid_transitions.get(current_stage, [])
    
    @staticmethod
    def validate_required_fields(state: CareerNavigatorState, stage: WorkflowStage) -> List[str]:
        """验证当前阶段所需的必要字段"""
        missing_fields = []
        
        if stage == WorkflowStage.PARALLEL_ANALYSIS:
            if not state.get("planning_strategy"):
                missing_fields.append("planning_strategy")
            if not state.get("agent_tasks"):
                missing_fields.append("agent_tasks")
        
        elif stage == WorkflowStage.RESULT_INTEGRATION:
            required_results = ["self_insight_result", "industry_research_result", "career_analysis_result"]
            for field in required_results:
                if not state.get(field):
                    missing_fields.append(field)
        
        elif stage == WorkflowStage.GOAL_DECOMPOSITION:
            if not state.get("integrated_report"):
                missing_fields.append("integrated_report")
            if state.get("current_satisfaction") not in [UserSatisfactionLevel.SATISFIED, UserSatisfactionLevel.VERY_SATISFIED]:
                missing_fields.append("user_satisfaction")
        
        elif stage == WorkflowStage.SCHEDULE_PLANNING:
            if not state.get("career_goals"):
                missing_fields.append("career_goals")
        
        return missing_fields


# 初始化函数
def create_initial_state(user_profile: UserProfile, session_id: str) -> CareerNavigatorState:
    """创建初始状态"""
    return CareerNavigatorState(
        session_id=session_id,
        user_profile=user_profile,
        current_stage=WorkflowStage.INITIAL,
        messages=[],
        
        planning_strategy=None,
        agent_tasks=[],
        agent_outputs=[],
        
        self_insight_result=None,
        industry_research_result=None,
        career_analysis_result=None,
        integrated_report=None,
        
        user_feedback_history=[],
        current_satisfaction=None,
        pending_questions=None,
        
        career_goals=None,
        schedule_items=None,
        final_plan=None,
        
        iteration_count=0,
        max_iterations=3,  # 默认最大迭代3次
        system_metrics=SystemMetrics(
            response_time=0.0,
            mcp_call_success_rate=1.0,
            agent_success_rate={},
            user_satisfaction_avg=0.0,
            iteration_count=0,
            max_iterations=3,
            memory_usage=0.0,
            concurrent_users=1,
            error_count=0,
            last_updated=datetime.now()
        ),
        error_log=[],
        
        is_analysis_complete=False,
        is_planning_complete=False,
        requires_user_input=False,
        can_proceed_to_next_stage=True,
        
        cached_data=None,
        mcp_call_history=[],
        performance_logs=[]
    )
```

### 2.2 状态更新辅助类 `StateUpdater`

为了方便和规范地更新 `CareerNavigatorState`，我们设计了一个 `StateUpdater` 辅助类，它提供了一系列静态方法来执行原子化的状态修改操作。这有助于避免直接修改状态字典可能引入的错误，并确保状态更新的逻辑集中管理。

```python
# 状态更新辅助函数
class StateUpdater:
    """状态更新辅助类"""
    
    @staticmethod
    def update_stage(state: CareerNavigatorState, new_stage: WorkflowStage) -> Dict[str, Any]:
        """更新工作流阶段"""
        return {
            "current_stage": new_stage,
            "system_metrics": {
                **state["system_metrics"],
                "last_updated": datetime.now()
            }
        }
    
    @staticmethod
    def add_agent_task(state: CareerNavigatorState, task: AgentTask) -> Dict[str, Any]:
        """添加智能体任务"""
        updated_tasks = state["agent_tasks"].copy()
        updated_tasks.append(task)
        return {"agent_tasks": updated_tasks}
    
    @staticmethod
    def update_agent_status(state: CareerNavigatorState, task_id: str, 
                          new_status: AgentStatus) -> Dict[str, Any]:
        """更新智能体任务状态"""
        updated_tasks = []
        for task in state["agent_tasks"]:
            if task["task_id"] == task_id:
                task["status"] = new_status
                if new_status == AgentStatus.COMPLETED:
                    task["completed_at"] = datetime.now()
                elif new_status == AgentStatus.WORKING:
                    task["started_at"] = datetime.now()
            updated_tasks.append(task)
        return {"agent_tasks": updated_tasks}
    
    @staticmethod
    def add_agent_output(state: CareerNavigatorState, output: AgentOutput) -> Dict[str, Any]:
        """添加智能体输出结果"""
        updated_outputs = state["agent_outputs"].copy()
        updated_outputs.append(output)
        return {"agent_outputs": updated_outputs}
    
    @staticmethod
    def add_user_feedback(state: CareerNavigatorState, feedback: UserFeedback) -> Dict[str, Any]:
        """添加用户反馈"""
        updated_feedback = state["user_feedback_history"].copy()
        updated_feedback.append(feedback)
        return {
            "user_feedback_history": updated_feedback,
            "current_satisfaction": feedback["satisfaction_level"]
        }
    
    @staticmethod
    def increment_iteration(state: CareerNavigatorState) -> Dict[str, Any]:
        """增加迭代次数"""
        new_count = state["iteration_count"] + 1
        return {
            "iteration_count": new_count,
            "system_metrics": {
                **state["system_metrics"],
                "iteration_count": new_count,
                "last_updated": datetime.now()
            }
        }
    
    @staticmethod
    def check_iteration_limit(state: CareerNavigatorState) -> bool:
        """检查是否达到迭代限制"""
        return state["iteration_count"] >= state["max_iterations"]
    
    @staticmethod
    def set_user_input_required(state: CareerNavigatorState, required: bool, 
                              questions: Optional[List[str]] = None) -> Dict[str, Any]:
        """设置是否需要用户输入"""
        update_dict = {"requires_user_input": required}
        if questions:
            update_dict["pending_questions"] = questions
        return update_dict
    
    @staticmethod
    def log_error(state: CareerNavigatorState, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """记录错误信息"""
        updated_errors = state["error_log"].copy()
        error_entry = {
            **error_info,
            "timestamp": datetime.now(),
            "session_id": state["session_id"]
        }
        updated_errors.append(error_entry)
        
        # 更新系统指标中的错误计数
        updated_metrics = state["system_metrics"].copy()
        updated_metrics["error_count"] += 1
        updated_metrics["last_updated"] = datetime.now()
        
        return {
            "error_log": updated_errors,
            "system_metrics": updated_metrics
        }
```

### 2.3 状态验证器 `StateValidator`

为了确保工作流的健壮性和正确性，我们引入了 `StateValidator`。它提供了方法来验证状态转换的合法性以及在特定阶段所需字段的完整性，这有助于在流程中提前发现潜在问题。

```python
# 状态验证器
class StateValidator:
    """状态验证器"""
    
    @staticmethod
    def validate_state_transition(current_stage: WorkflowStage, 
                                 target_stage: WorkflowStage) -> bool:
        """验证状态转换是否合法"""
        valid_transitions = {
            WorkflowStage.INITIAL: [WorkflowStage.PLANNING],
            WorkflowStage.PLANNING: [WorkflowStage.PARALLEL_ANALYSIS],
            WorkflowStage.PARALLEL_ANALYSIS: [WorkflowStage.RESULT_INTEGRATION],
            WorkflowStage.RESULT_INTEGRATION: [WorkflowStage.USER_FEEDBACK],
            WorkflowStage.USER_FEEDBACK: [
                WorkflowStage.GOAL_DECOMPOSITION,  # 满意时
                WorkflowStage.PLANNING              # 不满意时，重新规划
            ],
            WorkflowStage.GOAL_DECOMPOSITION: [WorkflowStage.SCHEDULE_PLANNING],
            WorkflowStage.SCHEDULE_PLANNING: [WorkflowStage.FINAL_CONFIRMATION],
            WorkflowStage.FINAL_CONFIRMATION: [
                WorkflowStage.COMPLETED,            # 满意时
                WorkflowStage.SCHEDULE_PLANNING     # 不满意时，重新规划
            ]
        }
        
        return target_stage in valid_transitions.get(current_stage, [])
    
    @staticmethod
    def validate_required_fields(state: CareerNavigatorState, stage: WorkflowStage) -> List[str]:
        """验证当前阶段所需的必要字段"""
        missing_fields = []
        
        if stage == WorkflowStage.PARALLEL_ANALYSIS:
            if not state.get("planning_strategy"):
                missing_fields.append("planning_strategy")
            if not state.get("agent_tasks"):
                missing_fields.append("agent_tasks")
        
        elif stage == WorkflowStage.RESULT_INTEGRATION:
            required_results = ["self_insight_result", "industry_research_result", "career_analysis_result"]
            for field in required_results:
                if not state.get(field):
                    missing_fields.append(field)
        
        elif stage == WorkflowStage.GOAL_DECOMPOSITION:
            if not state.get("integrated_report"):
                missing_fields.append("integrated_report")
            if state.get("current_satisfaction") not in [UserSatisfactionLevel.SATISFIED, UserSatisfactionLevel.VERY_SATISFIED]:
                missing_fields.append("user_satisfaction")
        
        elif stage == WorkflowStage.SCHEDULE_PLANNING:
            if not state.get("career_goals"):
                missing_fields.append("career_goals")
        
        return missing_fields
```

### 2.4 初始状态创建函数

`create_initial_state` 函数用于在工作流开始时初始化 `CareerNavigatorState`，设置所有字段的默认值，并为后续流程做好准备。

```python
# 初始化函数
def create_initial_state(user_profile: UserProfile, session_id: str) -> CareerNavigatorState:
    """创建初始状态"""
    return CareerNavigatorState(
        session_id=session_id,
        user_profile=user_profile,
        current_stage=WorkflowStage.INITIAL,
        messages=[],
        
        planning_strategy=None,
        agent_tasks=[],
        agent_outputs=[],
        
        self_insight_result=None,
        industry_research_result=None,
        career_analysis_result=None,
        integrated_report=None,
        
        user_feedback_history=[],
        current_satisfaction=None,
        pending_questions=None,
        
        career_goals=None,
        schedule_items=None,
        final_plan=None,
        
        iteration_count=0,
        max_iterations=3,  # 默认最大迭代3次
        system_metrics=SystemMetrics(
            response_time=0.0,
            mcp_call_success_rate=1.0,
            agent_success_rate={},
            user_satisfaction_avg=0.0,
            iteration_count=0,
            max_iterations=3,
            memory_usage=0.0,
            concurrent_users=1,
            error_count=0,
            last_updated=datetime.now()
        ),
        error_log=[],
        
        is_analysis_complete=False,
        is_planning_complete=False,
        requires_user_input=False,
        can_proceed_to_next_stage=True,
        
        cached_data=None,
        mcp_call_history=[],
        performance_logs=[]
    )
```

## 3. 原子化节点（Node）设计

每个节点在 LangGraph 中都是一个独立的 Python 函数，它接收当前的 `CareerNavigatorState` 作为输入，执行特定的业务逻辑，并返回一个字典来更新状态。这种原子化设计使得每个节点职责单一，易于测试、维护和复用。

为了模拟实际的 LLM 和 MCP (Manus Content Platform) API 调用，我们提供了 `call_llm` 和 `call_mcp_api` 辅助函数。在实际部署时，这些函数将被替换为真实的 API 调用。

```python
import uuid
from datetime import datetime
from typing import Dict, Any, List

# 为了可运行，这里会重新定义依赖的类型
from .career_navigator_state_design import CareerNavigatorState, AgentTask, AgentOutput, AgentStatus, WorkflowStage, StateUpdater, UserFeedback, UserSatisfactionLevel

# === 模拟的工具或LLM调用 ===

def call_llm(prompt: str, context: Dict) -> Dict:
    """模拟调用大语言模型"""
    print(f"--- LLM 调用 ---")
    print(f"Prompt: {prompt[:100]}...")
    # 在真实场景中，这里会是实际的LLM API调用
    # 这里我们返回一个模拟的响应
    if "判断目标是否明确" in prompt:
        return {"is_goal_clear": False, "reason": "用户没有提供明确的职业方向。"}
    if "制定搜索策略" in prompt:
        return {"plan": "1. 分析用户简历. 2. 研究目标行业. 3. 分析相关职位."}
    if "汇总报告" in prompt:
        return {"report": {"title": "综合职业分析报告", "summary": "..."}}
    return {"response": "模拟LLM响应"}

def call_mcp_api(api_name: str, params: Dict) -> Dict:
    """模拟调用MCP（Manus Content Platform）API"""
    print(f"--- MCP API 调用 ---")
    print(f"API: {api_name}, Params: {params}")
    # 模拟返回数据
    if api_name == "user_profile_analysis":
        return {"profile": {"strengths": ["沟通能力"], "weaknesses": ["编程经验"]}}
    if api_name == "industry_data":
        return {"trends": [{"name": "AI", "growth": 0.2}]}
    if api_name == "job_market":
        return {"jobs": [{"title": "AI产品经理", "salary": "30k"}]}
    return {"data": "模拟API数据"}


# === 节点定义 ===

def coordinator_node(state: CareerNavigatorState) -> Dict[str, Any]:
    """
    协调员节点 (入口点)
    
    职责:
    1. 检查用户的初始请求。
    2. 调用LLM判断用户的职业目标是否已经明确。
    3. 根据判断结果，决定下一个流程节点。
    """
    print("--- 正在执行: coordinator_node ---")
    messages = state["messages"]
    user_request = messages[-1].content if messages else ""
    
    prompt = f"根据用户请求 \'{user_request}\'，判断其职业目标是否明确。"
    llm_response = call_llm(prompt, {"user_profile": state["user_profile"]})
    
    if llm_response.get("is_goal_clear"):
        print("判断：目标明确，直接进入目标拆分。")
        # 更新状态，直接进入目标拆分阶段
        updated_state = StateUpdater.update_stage(state, WorkflowStage.GOAL_DECOMPOSITION)
        updated_state["next_node"] = "goal_decomposer"
        return updated_state
    else:
        print("判断：目标不明确，需要进行规划和分析。")
        # 更新状态，进入策略制定阶段
        updated_state = StateUpdater.update_stage(state, WorkflowStage.PLANNING)
        updated_state["next_node"] = "planner"
        return updated_state

def planner_node(state: CareerNavigatorState) -> Dict[str, Any]:
    """
    计划员节点
    
    职责:
    1. 当用户目标不明确时，制定一个详细的分析策略。
    2. 将策略存入State中，供后续节点使用。
    """
    print("--- 正在执行: planner_node ---")
    user_profile = state["user_profile"]
    feedback_history = state["user_feedback_history"]
    
    prompt = f"为用户 {user_profile["user_id"]} 制定一个职业分析搜索策略。"
    if feedback_history:
        prompt += f" 请特别注意用户最近的反馈: {feedback_history[-1]["feedback_text"]}"
        
    llm_response = call_llm(prompt, {"user_profile": user_profile})
    plan = llm_response.get("plan", "未能生成计划。")
    
    return {"planning_strategy": plan}


def supervisor_node(state: CareerNavigatorState) -> Dict[str, Any]:
    """
    管理员节点
    
    职责:
    1. 根据 `planning_strategy` 创建并分发并行的分析任务。
    2. 为每个任务创建一个 AgentTask 对象，并添加到 State 中。
    """
    print("--- 正在执行: supervisor_node ---")
    plan = state["planning_strategy"]
    
    # 基于计划，创建三个并行任务
    tasks = [
        AgentTask(
            task_id=str(uuid.uuid4()),
            agent_name="user_profiler_node",
            task_type="个人分析",
            priority=1,
            description="执行自我洞察分析，生成个人能力画像。",
            input_data={"user_profile": state["user_profile"]},
            status=AgentStatus.IDLE,
            created_at=datetime.now()
        ),
        AgentTask(
            task_id=str(uuid.uuid4()),
            agent_name="industry_researcher_node",
            task_type="行业研究",
            priority=1,
            description="执行行业趋势分析，生成行业报告。",
            input_data={"target_industry": state["user_profile"].get("industry")},
            status=AgentStatus.IDLE,
            created_at=datetime.now()
        ),
        AgentTask(
            task_id=str(uuid.uuid4()),
            agent_name="job_analyzer_node",
            task_type="职业分析",
            priority=1,
            description="执行职业与岗位分析，生成职业建议。",
            input_data={"target_career": state["user_profile"].get("career_goals")},
            status=AgentStatus.IDLE,
            created_at=datetime.now()
        )
    ]
    
    # 更新状态，进入并行分析阶段
    updated_state = StateUpdater.update_stage(state, WorkflowStage.PARALLEL_ANALYSIS)
    updated_state["agent_tasks"] = tasks
    return updated_state


# --- 并行分析节点 ---
def user_profiler_node(state: CareerNavigatorState) -> Dict[str, Any]:
    """用户建模节点 (并行)"""
    print("--- 正在执行: user_profiler_node ---")
    task = next(t for t in state["agent_tasks"] if t["agent_name"] == "user_profiler_node")
    
    # 模拟调用API进行分析
    result = call_mcp_api("user_profile_analysis", task["input_data"])
    
    output = AgentOutput(
        agent_name="user_profiler_node",
        task_id=task["task_id"],
        output_type="个人画像",
        content=result,
        timestamp=datetime.now()
    )
    return {"self_insight_result": result, "agent_outputs": state["agent_outputs"] + [output]}

def industry_researcher_node(state: CareerNavigatorState) -> Dict[str, Any]:
    """行业研究节点 (并行)"""
    print("--- 正在执行: industry_researcher_node ---")
    task = next(t for t in state["agent_tasks"] if t["agent_name"] == "industry_researcher_node")
    result = call_mcp_api("industry_data", task["input_data"])
    output = AgentOutput(
        agent_name="industry_researcher_node",
        task_id=task["task_id"],
        output_type="行业报告",
        content=result,
        timestamp=datetime.now()
    )
    return {"industry_research_result": result, "agent_outputs": state["agent_outputs"] + [output]}

def job_analyzer_node(state: CareerNavigatorState) -> Dict[str, Any]:
    """职业分析节点 (并行)"""
    print("--- 正在执行: job_analyzer_node ---")
    task = next(t for t in state["agent_tasks"] if t["agent_name"] == "job_analyzer_node")
    result = call_mcp_api("job_market", task["input_data"])
    output = AgentOutput(
        agent_name="job_analyzer_node",
        task_id=task["task_id"],
        output_type="职业建议",
        content=result,
        timestamp=datetime.now()
    )
    return {"career_analysis_result": result, "agent_outputs": state["agent_outputs"] + [output]}


# --- 结果汇总与规划节点 ---
def reporter_node(state: CareerNavigatorState) -> Dict[str, Any]:
    """
    汇报员节点
    
    职责:
    1. 收集所有并行分析节点的结果。
    2. 调用LLM将结果整合成一份结构化的综合报告。
    3. 更新状态，准备进入用户反馈阶段。
    """
    print("--- 正在执行: reporter_node ---")
    
    # 检查所有分析是否已完成
    required_results = ["self_insight_result", "industry_research_result", "career_analysis_result"]
    if not all(state.get(key) for key in required_results):
        return StateUpdater.log_error(state, {"error": "部分分析结果缺失，无法生成报告。"})

    context = {
        "profile": state["self_insight_result"],
        "industry": state["industry_research_result"],
        "jobs": state["career_analysis_result"]
    }
    
    prompt = "请根据以下个人画像、行业研究和职业分析，为用户生成一份综合职业规划报告。"
    report = call_llm(prompt, context)
    
    # 更新状态，进入用户反馈阶段
    updated_state = StateUpdater.update_stage(state, WorkflowStage.USER_FEEDBACK)
    updated_state["integrated_report"] = report
    # 设置需要用户输入标志，并提出问题
    updated_state.update(StateUpdater.set_user_input_required(
        state, True, ["您对这份综合报告满意吗？请提供您的反馈或修改意见。"]
    ))
    return updated_state

def goal_decomposer_node(state: CareerNavigatorState) -> Dict[str, Any]:
    """
    目标拆分节点
    
    职责:
    1. 基于用户确认的职业方向（来自综合报告）。
    2. 将其分解为长期、中期、短期目标。
    """
    print("--- 正在执行: goal_decomposer_node ---")
    # ... 实现目标拆分逻辑 ...
    decomposed_goals = {"long_term": "...", "medium_term": "...", "short_term": "..."}
    
    # 更新状态，进入日程规划阶段
    updated_state = StateUpdater.update_stage(state, WorkflowStage.SCHEDULE_PLANNING)
    updated_state["career_goals"] = decomposed_goals
    return updated_state

def scheduler_node(state: CareerNavigatorState) -> Dict[str, Any]:
    """
    日程计划节点
    
    职责:
    1. 将拆分后的目标整合成可执行的、带时间线的具体任务。
    2. 生成最终的计划，并准备进行最终确认。
    """
    print("--- 正在执行: scheduler_node ---")
    # ... 实现日程计划逻辑 ...
    final_schedule = [{"task": "学习Python", "deadline": "2025-09-01"}]
    
    # 更新状态，进入最终确认阶段
    updated_state = StateUpdater.update_stage(state, WorkflowStage.FINAL_CONFIRMATION)
    updated_state["final_plan"] = final_schedule
    # 再次请求用户输入
    updated_state.update(StateUpdater.set_user_input_required(
        state, True, ["这是为您生成的最终行动计划，您是否满意？"]
    ))
    return updated_state
```

## 4. LangGraph 工作流集成

在 LangGraph 中，我们将使用 `StateGraph` 来构建整个工作流。以下是构建图的基本步骤和关键部分：

1.  **定义图的状态**: 使用 `CareerNavigatorState` 作为图的状态。
2.  **添加节点**: 将上述原子化节点函数添加到图中。
3.  **定义入口点**: 设置工作流的起始节点。
4.  **添加边**: 定义节点之间的流转关系，包括常规边和条件边。
5.  **编译图**: 将定义好的图编译成可执行的 LangGraph 应用。

### 4.1 构建图的骨架

```python
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

# 导入之前定义的 State 和 Nodes
# from .career_navigator_state_design import CareerNavigatorState, WorkflowStage, UserProfile, StateUpdater, UserSatisfactionLevel
# from .career_navigator_nodes import (
#     coordinator_node, planner_node, supervisor_node, 
#     user_profiler_node, industry_researcher_node, job_analyzer_node, 
#     reporter_node, goal_decomposer_node, scheduler_node
# )

# 为了可运行，这里会重新定义依赖的类型
from career_navigator_state_design import CareerNavigatorState, WorkflowStage, UserProfile, StateUpdater, UserSatisfactionLevel, create_initial_state
from career_navigator_nodes import (
    coordinator_node, planner_node, supervisor_node, 
    user_profiler_node, industry_researcher_node, job_analyzer_node, 
    reporter_node, goal_decomposer_node, scheduler_node
)


# 定义条件边函数
def route_coordinator(state: CareerNavigatorState) -> str:
    """协调员节点后的路由逻辑"""
    # coordinator_node 会在 state 中设置 'next_node'
    return state.get("next_node", "planner") # 默认路由到 planner

def route_user_satisfaction_analysis(state: CareerNavigatorState) -> str:
    """用户对分析报告满意度判断后的路由逻辑"""
    # 这里需要一个机制来获取用户的实际反馈，并更新 state.current_satisfaction
    # 假设用户反馈已经通过外部机制更新到 state.current_satisfaction
    
    # 检查迭代次数限制
    if StateUpdater.check_iteration_limit(state):
        print("达到最大迭代次数，强制进入目标拆分阶段。")
        return "satisfied" # 强制进入下一阶段

    if state.get("current_satisfaction") in [UserSatisfactionLevel.SATISFIED, UserSatisfactionLevel.VERY_SATISFIED]:
        return "satisfied"
    else:
        # 增加迭代次数
        state.update(StateUpdater.increment_iteration(state))
        return "not_satisfied"

def route_user_satisfaction_planning(state: CareerNavigatorState) -> str:
    """用户对规划计划满意度判断后的路由逻辑"""
    # 假设用户反馈已经通过外部机制更新到 state.current_satisfaction
    
    # 检查迭代次数限制
    if StateUpdater.check_iteration_limit(state):
        print("达到最大迭代次数，强制完成规划。")
        return "satisfied" # 强制完成

    if state.get("current_satisfaction") in [UserSatisfactionLevel.SATISFIED, UserSatisfactionLevel.VERY_SATISFIED]:
        return "satisfied"
    else:
        # 增加迭代次数
        state.update(StateUpdater.increment_iteration(state))
        return "not_satisfied"


# 构建图
workflow = StateGraph(CareerNavigatorState)

# 添加节点
workflow.add_node("coordinator", coordinator_node)
workflow.add_node("planner", planner_node)
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("user_profiler", user_profiler_node)
workflow.add_node("industry_researcher", industry_researcher_node)
workflow.add_node("job_analyzer", job_analyzer_node)
workflow.add_node("reporter", reporter_node)
workflow.add_node("goal_decomposer", goal_decomposer_node)
workflow.add_node("scheduler", scheduler_node)

# 设置入口点
workflow.set_entry_point("coordinator")

# 添加边
# 协调员的条件路由
workflow.add_conditional_edges(
    "coordinator",
    route_coordinator,
    {
        "planner": "planner",
        "goal_decomposer": "goal_decomposer"
    }
)

# 计划员 -> 管理员
workflow.add_edge("planner", "supervisor")

# 管理员 -> 并行分析节点 (LangGraph 会自动处理并行执行，当所有并行节点完成后，流转到下一个节点)
# 这里需要特别注意 LangGraph 的并行执行机制，通常是定义一个 Join 节点来汇聚并行结果
# 但对于 StateGraph，如果多个节点可以更新相同的状态，它们会并行执行，并在所有并行路径完成后，
# 自动将状态合并，然后流转到下一个节点。这里我们假设 supervisor 负责分发任务，
# 并且这些任务的执行结果会更新到 State 中，然后 reporter 节点会等待这些结果。
# 因此，从 supervisor 到 reporter 之间，实际上是 user_profiler, industry_researcher, job_analyzer 的并行执行
# 并在它们都完成后，才会触发 reporter_node。
# 在 LangGraph 中，可以通过 add_edge 来连接并行执行的节点到一个汇聚节点。
# 假设并行执行的节点是 'user_profiler', 'industry_researcher', 'job_analyzer'
# 它们都将结果写入 State，然后 'reporter' 节点读取这些结果。
# 我们可以将 supervisor 连接到这些并行节点，然后这些并行节点再连接到 reporter。
# 但更常见的做法是，supervisor 节点只是触发并行任务，然后 LangGraph 自动等待所有任务完成。
# 考虑到流程图，我们直接从 supervisor 引导到并行节点，然后并行节点汇聚到 reporter。

# 从 supervisor 到并行分析节点
workflow.add_edge("supervisor", "user_profiler")
workflow.add_edge("supervisor", "industry_researcher")
workflow.add_edge("supervisor", "job_analyzer")

# 并行分析节点汇聚到汇报员
# LangGraph 默认行为是，如果一个节点有多个入边，它会等待所有入边都触发后才执行。
# 因此，我们让所有并行节点都指向 reporter 即可。
workflow.add_edge("user_profiler", "reporter")
workflow.add_edge("industry_researcher", "reporter")
workflow.add_edge("job_analyzer", "reporter")

# 汇报员的条件路由 (用户对分析报告的满意度)
workflow.add_conditional_edges(
    "reporter",
    route_user_satisfaction_analysis,
    {
        "satisfied": "goal_decomposer",
        "not_satisfied": "planner" # 不满意则返回计划员重新规划
    }
)

# 目标拆分 -> 日程计划
workflow.add_edge("goal_decomposer", "scheduler")

# 日程计划的条件路由 (用户对最终计划的满意度)
workflow.add_conditional_edges(
    "scheduler",
    route_user_satisfaction_planning,
    {
        "satisfied": END, # 满意则结束
        "not_satisfied": "scheduler" # 不满意则返回日程计划员重新调整
    }
)

# 编译图
app = workflow.compile()

# === 示例运行 ===
if __name__ == "__main__":
    # 模拟用户初始信息
    initial_user_profile = UserProfile(
        user_id="user123",
        age=25,
        education_level="本科",
        work_experience=3,
        current_position="软件工程师",
        industry="IT",
        skills=["Python", "Java", "数据分析"],
        interests=["人工智能", "机器学习"],
        career_goals="成为AI产品经理",
        location="北京",
        salary_expectation="20k-30k"
    )
    
    # 创建初始状态
    initial_state = create_initial_state(initial_user_profile, "session_abc")
    initial_state["messages"] = [HumanMessage(content="我想规划我的职业生涯，目前是软件工程师，对AI产品经理感兴趣。")]
    
    print("\n--- 第一次运行 (目标不明确) ---")
    # 模拟用户不满意分析报告，进行迭代
    for s in app.stream(initial_state):
        print(s)
        # 模拟用户反馈
        if "reporter" in s:
            # 模拟用户不满意
            s["reporter"]["current_satisfaction"] = UserSatisfactionLevel.DISSATISFIED
            s["reporter"]["user_feedback_history"].append(UserFeedback(
                feedback_id=str(uuid.uuid4()),
                stage=WorkflowStage.USER_FEEDBACK,
                satisfaction_level=UserSatisfactionLevel.DISSATISFIED,
                specific_feedback={"reason": "报告不够详细"},
                improvement_requests=["增加行业案例"],
                timestamp=datetime.now(),
                feedback_text="报告不够详细，希望能增加更多行业案例。"
            ))
            print("\n--- 模拟用户反馈：不满意分析报告 ---")
        elif "scheduler" in s:
            # 模拟用户满意最终计划
            s["scheduler"]["current_satisfaction"] = UserSatisfactionLevel.SATISFIED
            print("\n--- 模拟用户反馈：满意最终计划 ---")

    print("\n--- 第二次运行 (目标明确) ---")
    # 模拟用户初始目标明确
    initial_state_clear_goal = create_initial_state(initial_user_profile, "session_def")
    initial_state_clear_goal["messages"] = [HumanMessage(content="我希望成为一名AI产品经理，请帮我制定详细的职业规划。")]
    
    for s in app.stream(initial_state_clear_goal):
        print(s)
        if "scheduler" in s:
            # 模拟用户满意最终计划
            s["scheduler"]["current_satisfaction"] = UserSatisfactionLevel.SATISFIED
            print("\n--- 模拟用户反馈：满意最终计划 ---")

```

## 5. 总结

本报告详细阐述了 CareerNavigator 项目的 LangGraph 状态设计和原子化节点实现。通过定义清晰的 `CareerNavigatorState` 和一系列职责单一的节点函数，我们构建了一个模块化、可扩展的职业规划系统。条件边和状态更新辅助类的引入，进一步增强了系统的灵活性和健壮性，使其能够有效处理复杂的业务逻辑和用户交互。

未来的工作将包括实现每个节点中的具体业务逻辑（如调用真实的 LLM 和 MCP API），以及构建用户交互界面来获取用户反馈并更新状态。

