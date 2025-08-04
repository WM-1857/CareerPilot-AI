"""
CareerNavigator LangGraph 工作流构建
基于状态和节点定义构建完整的职业规划工作流
"""

import uuid
import json
from datetime import datetime
from typing import Dict, Any, List

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

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
        self.app = self.workflow.compile()
    
    def _add_edges(self):
        """添加工作流边"""
        # 协调员的条件路由
        self.workflow.add_conditional_edges(
            "coordinator",
            self._route_coordinator,
            {
                "planner": "planner",
                "goal_decomposer": "goal_decomposer"
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
        
        # 汇报员的条件路由 (用户对分析报告的满意度)
        self.workflow.add_conditional_edges(
            "reporter",
            self._route_user_satisfaction_analysis,
            {
                "satisfied": "goal_decomposer",
                "not_satisfied": "supervisor"  # 不满意则返回supervisor重新执行并行分析
            }
        )
        
        # 目标拆分 -> 日程计划
        self.workflow.add_edge("goal_decomposer", "scheduler")
        
        # 日程计划的条件路由 (用户对最终计划的满意度)
        self.workflow.add_conditional_edges(
            "scheduler",
            self._route_user_satisfaction_planning,
            {
                "satisfied": END,  # 满意则结束
                "not_satisfied": "scheduler"  # 不满意则返回日程计划员重新调整
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
        if current_satisfaction in [UserSatisfactionLevel.SATISFIED, UserSatisfactionLevel.VERY_SATISFIED]:
            return "satisfied"
        else:
            # 增加迭代次数
            return "not_satisfied"
    
    def _route_user_satisfaction_planning(self, state: CareerNavigatorState) -> str:
        """用户对规划计划满意度判断后的路由逻辑"""
        # 检查迭代次数限制
        if StateUpdater.check_iteration_limit(state):
            print("达到最大迭代次数，强制完成规划。")
            return "satisfied"  # 强制完成

        # 检查用户满意度
        current_satisfaction = state.get("current_satisfaction")
        if current_satisfaction in [UserSatisfactionLevel.SATISFIED, UserSatisfactionLevel.VERY_SATISFIED]:
            return "satisfied"
        else:
            return "not_satisfied"
    
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
    
    def run_workflow(self, initial_state: CareerNavigatorState) -> Dict[str, Any]:
        """
        运行工作流
        
        Args:
            initial_state: 初始状态
            
        Returns:
            工作流执行结果
        """
        try:
            # 运行工作流
            final_state = None
            for state_update in self.app.stream(initial_state):
                print(f"工作流状态更新: {list(state_update.keys())}")
                final_state = state_update
            
            # 提取最终状态
            if final_state:
                # 获取最后一个节点的状态
                last_node = list(final_state.keys())[-1]
                return {
                    "success": True,
                    "final_state": final_state[last_node],
                    "session_id": final_state[last_node]["session_id"]
                }
            else:
                return {
                    "success": False,
                    "error": "工作流执行失败，未获得最终状态"
                }
                
        except Exception as e:
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
        updated_state.update(StateUpdater.increment_iteration(state))
        
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

