"""
CareerNavigator LangGraph 工作流构建
基于状态和节点定义构建完整的职业规划工作流
"""

import uuid
import json
from datetime import datetime
from typing import Dict, Any, List

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from src.models.career_state import (
    CareerNavigatorState, WorkflowStage, UserProfile, StateUpdater, 
    UserSatisfactionLevel, create_initial_state
)
from src.services.career_nodes import (
    coordinator_node, planner_node, supervisor_node, 
    user_profiler_node, industry_researcher_node, job_analyzer_node, 
    reporter_node, goal_decomposer_node, scheduler_node
)


class CareerNavigatorGraph:
    """职业规划LangGraph工作流类"""
    
    def __init__(self):
        """初始化工作流"""
        self.workflow = None
        self.app = None
        self._build_graph()
    
    def _build_graph(self):
        """构建LangGraph工作流"""
        # 创建状态图
        self.workflow = StateGraph(CareerNavigatorState)
        
        # 添加节点
        self.workflow.add_node("coordinator", coordinator_node)
        self.workflow.add_node("planner", planner_node)
        self.workflow.add_node("supervisor", supervisor_node)
        self.workflow.add_node("user_profiler", user_profiler_node)
        self.workflow.add_node("industry_researcher", industry_researcher_node)
        self.workflow.add_node("job_analyzer", job_analyzer_node)
        self.workflow.add_node("reporter", reporter_node)
        self.workflow.add_node("goal_decomposer", goal_decomposer_node)
        self.workflow.add_node("scheduler", scheduler_node)
        
        # 设置入口点
        self.workflow.set_entry_point("coordinator")
        
        # 添加边
        self._add_edges()
        
        # 编译图
        self.memory = MemorySaver()
        # 使用 interrupt_after 实现人工干预 (Human-in-the-loop)
        # 在 reporter 节点（生成分析报告）和 scheduler 节点（生成最终计划）后暂停
        self.app = self.workflow.compile(
            checkpointer=self.memory,
            interrupt_after=["reporter", "scheduler"]
        )
        
        # 设置默认配置
        self.default_config = {
            "recursion_limit": 50,  # 增加递归限制到50
            "thread_id": "career_planning_thread"
        }
    
    def _add_edges(self):
        """添加工作流边"""
        # 协调员的条件路由
        self.workflow.add_conditional_edges(
            "coordinator",
            self._route_coordinator,
            {
                "planner": "planner",
                "goal_decomposer": "goal_decomposer",
                "scheduler": "scheduler",
                "end": END
            }
        )
        
        # 计划员 -> 管理员
        self.workflow.add_edge("planner", "supervisor")
        
        # 管理员 -> 并行分析节点
        self.workflow.add_edge("supervisor", "user_profiler")
        self.workflow.add_edge("supervisor", "industry_researcher")
        self.workflow.add_edge("supervisor", "job_analyzer")
        
        # 并行分析节点汇聚到汇报员
        self.workflow.add_edge("user_profiler", "reporter")
        self.workflow.add_edge("industry_researcher", "reporter")
        self.workflow.add_edge("job_analyzer", "reporter")
        
        # 汇报员的条件路由 (检查迭代次数和用户满意度)
        self.workflow.add_conditional_edges(
            "reporter",
            self._route_user_satisfaction_analysis,
            {
                "satisfied": "goal_decomposer",  # 用户满意，进入目标拆分
                "not_satisfied": "planner",  # 用户不满意，重新规划策略
            }
        )
        
        # 目标拆分 -> 日程计划
        self.workflow.add_edge("goal_decomposer", "scheduler")
        
        # 日程计划后的条件路由 (最终确认)
        self.workflow.add_conditional_edges(
            "scheduler",
            self._route_user_satisfaction_planning,
            {
                "satisfied": END,
                "not_satisfied": "goal_decomposer"
            }
        )
    
    def _route_coordinator(self, state: CareerNavigatorState) -> str:
        """协调员节点后的路由逻辑"""
        # coordinator_node 会在 state 中设置 'next_node'
        return state.get("next_node", "planner")  # 默认路由到 planner
    
    def _route_user_satisfaction_analysis(self, state: CareerNavigatorState) -> str:
        """用户对分析报告满意度判断后的路由逻辑"""
        # 检查迭代次数限制
        if StateUpdater.check_iteration_limit(state):
            print("达到最大迭代次数，强制进入目标拆分阶段。")
            return "satisfied"  # 强制进入下一阶段

        # 检查用户满意度
        current_satisfaction = state.get("current_satisfaction")
        
        # 评分1-3：不满意，需要迭代优化（但要检查迭代次数限制）
        if current_satisfaction in [UserSatisfactionLevel.VERY_DISSATISFIED, 
                                  UserSatisfactionLevel.DISSATISFIED, 
                                  UserSatisfactionLevel.NEUTRAL]:
            iteration_count = state.get("iteration_count", 0)
            max_iterations = state.get("max_iterations", 3)
            
            if iteration_count < max_iterations:
                print(f"用户满意度较低({current_satisfaction.value})，进行第{iteration_count + 1}次迭代优化")
                return "not_satisfied"  # 触发重新分析
            else:
                print(f"已达到最大迭代次数({max_iterations})，强制进入目标拆分阶段")
                return "satisfied"
        
        # 评分4-5：满意，直接进入目标拆分阶段
        elif current_satisfaction in [UserSatisfactionLevel.SATISFIED, UserSatisfactionLevel.VERY_SATISFIED]:
            print(f"用户满意({current_satisfaction.value})，进入目标拆分阶段")
            return "satisfied"
        else:
            # 如果满意度未设置（可能是因为 interrupt_after 刚恢复），默认进入下一阶段或保持现状
            # 在 HITL 模式下，恢复时 current_satisfaction 应该已经被 update_state 设置了
            print("满意度未设置，默认进入目标拆分阶段")
            return "satisfied"
        
    def _route_user_satisfaction_planning(self, state: CareerNavigatorState) -> str:
        """用户对规划计划满意度判断后的路由逻辑"""
        # 检查迭代次数限制
        if StateUpdater.check_iteration_limit(state):
            print("达到最大迭代次数，强制完成规划。")
            return "satisfied"  # 强制完成

        # 检查用户满意度
        current_satisfaction = state.get("current_satisfaction")
        
        # 评分1-3：不满意，需要重新规划（但要检查迭代次数限制）
        if current_satisfaction in [UserSatisfactionLevel.VERY_DISSATISFIED, 
                                  UserSatisfactionLevel.DISSATISFIED, 
                                  UserSatisfactionLevel.NEUTRAL]:
            iteration_count = state.get("iteration_count", 0)
            max_iterations = state.get("max_iterations", 3)
            
            if iteration_count < max_iterations:
                print(f"用户对规划满意度较低({current_satisfaction.value})，重新进行目标拆分")
                return "not_satisfied"  # 重新规划
            else:
                print(f"已达到最大迭代次数({max_iterations})，强制完成规划")
                return "satisfied"
        
        # 评分4-5：满意，完成规划
        elif current_satisfaction in [UserSatisfactionLevel.SATISFIED, UserSatisfactionLevel.VERY_SATISFIED]:
            print(f"用户对规划满意({current_satisfaction.value})，完成规划")
            return "satisfied"
        else:
            print("满意度未设置，默认完成规划")
            return "satisfied"
    def create_session(self, user_profile: UserProfile, user_message: str) -> CareerNavigatorState:
        """
        创建新的会话状态
        
        Args:
            user_profile: 用户基础信息
            user_message: 用户初始消息
            
        Returns:
            初始化的状态
        """
        session_id = str(uuid.uuid4())
        initial_state = create_initial_state(user_profile, session_id)
        initial_state["messages"] = [HumanMessage(content=user_message)]
        return initial_state
    
    def run_workflow(self, initial_state: Dict[str, Any], stream_callback=None) -> Dict[str, Any]:
        """
        运行工作流
        
        Args:
            initial_state: 初始状态或更新的状态字典
            stream_callback: 流式回调函数
            
        Returns:
            工作流执行结果
        """
        try:
            # 获取 session_id 作为 thread_id
            session_id = initial_state.get("session_id")
            if not session_id:
                return {"success": False, "error": "缺少 session_id"}

            # 配置运行参数
            config = RunnableConfig(
                recursion_limit=50,
                configurable={
                    "stream_callback": stream_callback,
                    "thread_id": session_id
                }
            )
            
            # 检查当前图的状态，判断是新开始还是恢复执行
            snapshot = self.app.get_state(config)
            
            if snapshot.next:
                # 如果有 next 节点，说明工作流处于暂停状态（interrupt）
                print(f"⏭️ 恢复工作流执行，当前暂停在: {snapshot.next}")
                # 如果 initial_state 包含更新（如用户反馈），则更新状态
                # 注意：我们只更新非元数据字段
                update_data = {k: v for k, v in initial_state.items() if k not in ["session_id"]}
                if update_data:
                    print(f"📝 更新工作流状态: {list(update_data.keys())}")
                    self.app.update_state(config, update_data)
                
                # 恢复执行时，输入应为 None
                workflow_input = None
            else:
                # 如果没有 next 节点，说明是新开始或已结束
                print("🚀 开始新的工作流执行")
                workflow_input = initial_state
            
            # 使用 stream 模式运行
            # 注意：在 stream 模式下，如果遇到 interrupt，循环会正常结束
            for state_update in self.app.stream(workflow_input, config=config):
                print(f"工作流状态更新: {list(state_update.keys())}")
            
            # 无论是否中断，都从 checkpointer 获取完整的最新状态
            new_snapshot = self.app.get_state(config)
            final_state = new_snapshot.values

            # 检查是否成功执行并获得了状态
            if final_state:
                print(f"✅ 工作流执行结束/暂停，当前阶段: {final_state.get('current_stage')}")
                return {
                    "success": True,
                    "final_state": final_state,
                    "session_id": session_id,
                    "is_interrupted": bool(new_snapshot.next)
                }
            else:
                return {
                    "success": False,
                    "error": "工作流执行失败，未获得最终状态"
                }
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"工作流执行异常: {str(e)}"
            }
    
    def update_user_feedback(self, state: CareerNavigatorState, 
                           satisfaction_level: UserSatisfactionLevel,
                           feedback_text: str = "") -> CareerNavigatorState:
        """
        更新用户反馈
        
        Args:
            state: 当前状态
            satisfaction_level: 满意度级别
            feedback_text: 反馈文本
            
        Returns:
            更新后的状态
        """
        from src.models.career_state import UserFeedback
        
        feedback = UserFeedback(
            feedback_id=str(uuid.uuid4()),
            stage=state["current_stage"],
            satisfaction_level=satisfaction_level,
            specific_feedback={"general": feedback_text},
            improvement_requests=[],
            additional_requirements=None,
            timestamp=datetime.now(),
            feedback_text=feedback_text
        )
        
        # 更新状态
        updated_state = state.copy()
        updated_state.update(StateUpdater.add_user_feedback(state, feedback))
        
        # 设置当前满意度，供工作流路由使用
        updated_state["current_satisfaction"] = satisfaction_level
        
        # 只有在用户不满意时才增加迭代计数器
        if satisfaction_level in [UserSatisfactionLevel.VERY_DISSATISFIED, 
                                UserSatisfactionLevel.DISSATISFIED, 
                                UserSatisfactionLevel.NEUTRAL]:
            iteration_updates = StateUpdater.increment_iteration(state)
            for key, value in iteration_updates.items():
                updated_state[key] = value
        
        return updated_state
    
    def get_current_stage_info(self, state: CareerNavigatorState) -> Dict[str, Any]:
        """
        获取当前阶段信息
        
        Args:
            state: 当前状态
            
        Returns:
            阶段信息
        """
        current_stage = state["current_stage"]
        
        stage_info = {
            WorkflowStage.INITIAL: {
                "name": "初始化",
                "description": "系统正在初始化，准备开始职业规划分析",
                "next_action": "分析用户需求"
            },
            WorkflowStage.PLANNING: {
                "name": "策略制定",
                "description": "正在制定个性化的职业分析策略",
                "next_action": "开始并行分析"
            },
            WorkflowStage.PARALLEL_ANALYSIS: {
                "name": "并行分析",
                "description": "正在进行个人画像、行业研究和职业分析",
                "next_action": "等待分析完成"
            },
            WorkflowStage.RESULT_INTEGRATION: {
                "name": "结果整合",
                "description": "正在整合分析结果，生成综合报告",
                "next_action": "生成报告"
            },
            WorkflowStage.USER_FEEDBACK: {
                "name": "用户反馈",
                "description": "等待用户对分析报告的反馈",
                "next_action": "收集用户意见"
            },
            WorkflowStage.GOAL_DECOMPOSITION: {
                "name": "目标拆分",
                "description": "正在将职业目标拆分为具体的阶段性目标",
                "next_action": "制定目标"
            },
            WorkflowStage.SCHEDULE_PLANNING: {
                "name": "日程规划",
                "description": "正在制定详细的行动计划和时间安排",
                "next_action": "生成计划"
            },
            WorkflowStage.FINAL_CONFIRMATION: {
                "name": "最终确认",
                "description": "等待用户对最终计划的确认",
                "next_action": "确认计划"
            },
            WorkflowStage.COMPLETED: {
                "name": "完成",
                "description": "职业规划已完成",
                "next_action": "开始执行"
            }
        }
        
        return {
            "current_stage": current_stage.value,
            "stage_info": stage_info.get(current_stage, {}),
            "iteration_count": state["iteration_count"],
            "max_iterations": state["max_iterations"],
            "requires_user_input": state["requires_user_input"],
            "pending_questions": state.get("pending_questions", [])
        }


# 创建全局工作流实例
career_graph = CareerNavigatorGraph()

