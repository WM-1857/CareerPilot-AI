"""
CareerNavigator LangGraph State 设计
基于用户提供的设计文档和流程图，设计完整的状态管理结构
"""

from typing import TypedDict, List, Dict, Optional, Sequence, Literal, Any, Annotated
from langchain_core.messages import BaseMessage
from datetime import datetime
from enum import Enum
import operator


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
    agent_tasks: Annotated[List[AgentTask], operator.add]         # 智能体任务列表（支持并发添加）
    agent_outputs: Annotated[List[AgentOutput], operator.add]     # 智能体输出结果（支持并发添加）
    
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
    error_log: Annotated[List[Dict[str, Any]], operator.add]     # 错误日志（支持并发添加）
    
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
        # 检查并初始化用户反馈历史
        feedback_history = state.get("user_feedback_history", [])
        if isinstance(feedback_history, list):
            updated_feedback = feedback_history.copy()
        else:
            updated_feedback = []
        
        updated_feedback.append(feedback)
        return {
            "user_feedback_history": updated_feedback,
            "current_satisfaction": feedback["satisfaction_level"]
        }
    
    @staticmethod
    def increment_iteration(state: CareerNavigatorState) -> Dict[str, Any]:
        """增加迭代次数"""
        current_count = state.get("iteration_count", 0)
        new_count = current_count + 1
        return {
            "iteration_count": new_count,
            "system_metrics": {
                **state.get("system_metrics", {}),
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

