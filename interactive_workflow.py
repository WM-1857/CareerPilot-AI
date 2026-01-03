#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CareerNavigator 交互式工作流执行脚本
支持用户反馈收集和满意度评分
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 加载环境变量
def load_env():
    env_file = os.path.join(project_root, '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

# 设置临时API密钥（如果未配置）
if not os.getenv('SPARK_API_KEY'):
    print("⚠️  警告：未设置SPARK_API_KEY环境变量")
    print("   请在.env文件中设置正确的讯飞星火API密钥")
    print("   格式示例：SPARK_API_KEY=Bearer orFKteCwMFcKbowYftHz:OpmCHRrdIjguGUkfFwUk")
    # 这里仍然设置一个无效密钥用于演示，但会提供明确的错误信息
    os.environ['SPARK_API_KEY'] = 'Bearer sk-demo-invalid-key-for-testing'
    os.environ['DASHSCOPE_API_KEY'] = os.environ['SPARK_API_KEY']

try:
    from src.services.career_graph import CareerNavigatorGraph
    from src.services.career_nodes import goal_decomposer_node, scheduler_node
    from src.models.career_state import (
        CareerNavigatorState, WorkflowStage, UserProfile, UserSatisfactionLevel,
        create_initial_state, StateUpdater, UserFeedback
    )
    from langchain_core.messages import HumanMessage
    from langchain_core.runnables import RunnableConfig
    from src.utils.logger import workflow_logger
    IMPORT_SUCCESS = True
except ImportError as e:
    IMPORT_SUCCESS = False
    print(f"导入失败: {e}")
    sys.exit(1)


class InteractiveWorkflowRunner:
    """交互式工作流执行器"""
    
    def __init__(self):
        self.graph = CareerNavigatorGraph()
        self.current_state = None
        
    def print_separator(self, title: str, char: str = "=", length: int = 60):
        """打印分隔符"""
        print(f"\n{char * length}")
        print(f"  {title}")
        print(char * length)
    
    def display_report(self, report: Dict[str, Any]) -> None:
        """显示分析报告"""
        self.print_separator("📊 职业规划分析报告", "=", 80)
        
        # 显示执行摘要
        if "executive_summary" in report:
            print(f"\n【执行摘要】")
            print(f"{report['executive_summary']}")
        
        # 显示详细分析结果
        if "detailed_analysis" in report:
            analysis = report["detailed_analysis"]
            
            # 个人画像分析
            if "profile_insights" in analysis:
                print(f"\n【个人画像分析】")
                profile = analysis["profile_insights"]
                if "strengths" in profile:
                    print(f"✓ 优势: {', '.join(profile['strengths'])}")
                if "weaknesses" in profile:
                    print(f"⚠ 待改进: {', '.join(profile['weaknesses'])}")
                if "recommendations" in profile:
                    print(f"💡 建议: {', '.join(profile['recommendations'])}")
            
            # 行业分析
            if "industry_insights" in analysis:
                print(f"\n【行业分析】")
                industry = analysis["industry_insights"]
                if "trends" in industry:
                    print(f"📈 趋势: {', '.join(industry['trends'])}")
                if "opportunities" in industry:
                    print(f"🎯 机会: {', '.join(industry['opportunities'])}")
                if "challenges" in industry:
                    print(f"⚡ 挑战: {', '.join(industry['challenges'])}")
            
            # 职业分析
            if "career_insights" in analysis:
                print(f"\n【职业分析】")
                career = analysis["career_insights"]
                if "suitable_roles" in career:
                    print(f"🎯 适合职位: {', '.join(career['suitable_roles'])}")
                if "skill_gaps" in career:
                    print(f"📚 技能缺口: {', '.join(career['skill_gaps'])}")
                if "development_path" in career:
                    print(f"🛤 发展路径: {', '.join(career['development_path'])}")
        
        # 显示迭代信息（如果有）
        if "iteration_summary" in report:
            print(f"\n【迭代信息】")
            print(f"{report['iteration_summary']}")
        
        print("\n" + "=" * 80)
    
    def get_user_feedback(self) -> tuple[UserSatisfactionLevel, str]:
        """收集用户反馈"""
        self.print_separator("📝 用户反馈收集")
        
        print("\n请对上述分析报告进行评价:")
        print("1 - 非常不满意")
        print("2 - 不满意") 
        print("3 - 一般")
        print("4 - 满意")
        print("5 - 非常满意")
        
        # 获取满意度评分
        while True:
            try:
                score_input = input("\n请输入满意度评分 (1-5): ").strip()
                score = int(score_input)
                if 1 <= score <= 5:
                    break
                else:
                    print("请输入1-5之间的数字")
            except ValueError:
                print("请输入有效的数字")
        
        # 映射满意度级别
        satisfaction_mapping = {
            1: UserSatisfactionLevel.VERY_DISSATISFIED,
            2: UserSatisfactionLevel.DISSATISFIED,
            3: UserSatisfactionLevel.NEUTRAL,
            4: UserSatisfactionLevel.SATISFIED,
            5: UserSatisfactionLevel.VERY_SATISFIED
        }
        
        satisfaction_level = satisfaction_mapping[score]
        
        # 获取文字反馈
        print("\n请输入您的具体意见和建议 (可选，直接回车跳过):")
        feedback_text = input("反馈内容: ").strip()
        
        return satisfaction_level, feedback_text
    
    def display_goal_plan(self, plan: Dict[str, Any]) -> None:
        """显示目标规划"""
        self.print_separator("🎯 职业目标规划", "=", 80)
        
        if "goals" in plan:
            print("\n【目标拆分】")
            for i, goal in enumerate(plan["goals"], 1):
                print(f"{i}. {goal}")
        
        if "timeline" in plan:
            print(f"\n【时间规划】")
            timeline = plan["timeline"]
            for period, tasks in timeline.items():
                print(f"📅 {period}: {', '.join(tasks) if isinstance(tasks, list) else tasks}")
        
        if "action_steps" in plan:
            print(f"\n【行动步骤】")
            for i, step in enumerate(plan["action_steps"], 1):
                print(f"  {i}. {step}")
        
        print("\n" + "=" * 80)
    
    def run_interactive_workflow(self, user_profile: UserProfile, initial_message: str):
        """运行交互式工作流"""
        self.print_separator("🚀 CareerNavigator 交互式职业规划")
        
        print(f"用户: {user_profile['current_position']} -> {user_profile['career_goals']}")
        print(f"初始需求: {initial_message}")
        
        # 创建初始状态
        self.current_state = self.graph.create_session(user_profile, initial_message)
        
        try:
            # 执行工作流直到需要用户反馈
            print("\n🔄 开始执行职业规划分析...")
            
            if self.graph.app is None:
                print("❌ 工作流应用未正确初始化")
                return False
            
            workflow_completed = False
            safety_counter = 0  # 安全计数器，防止无限循环
            max_safety_iterations = 2  # 最大安全迭代次数
            
            # 执行工作流直到完成或需要用户交互
            while not workflow_completed and safety_counter < max_safety_iterations:
                safety_counter += 1
                print(f"\n🔄 工作流执行轮次: {safety_counter}")
                
                config = RunnableConfig(recursion_limit=10)  # 增加递归限制，匹配工作流复杂度
                
                # 获取工作流当前状态快照
                current_snapshot = self.current_state.copy()
                
                try:
                    for state_update in self.graph.app.stream(self.current_state, config=config):
                        print(f"📈 工作流进度: {list(state_update.keys())}")
                        
                        # 更新当前状态 - 正确合并状态而不是替换
                        node_name = list(state_update.keys())[-1]
                        node_update = state_update[node_name]
                        
                        # 合并状态而不是替换
                        if isinstance(node_update, dict):
                            self.current_state.update(node_update)
                        else:
                            self.current_state = node_update
                        
                        # 检查当前阶段
                        current_stage = self.current_state.get("current_stage")
                        
                        # 1. 分析报告反馈阶段
                        if current_stage == WorkflowStage.USER_FEEDBACK and "integrated_report" in self.current_state:
                            report = self.current_state["integrated_report"]
                            if report:  # 确保报告存在
                                self.display_report(report)
                            
                            # 收集用户反馈
                            satisfaction, feedback_text = self.get_user_feedback()
                            
                            # 更新状态
                            self.current_state = self.graph.update_user_feedback(
                                self.current_state, satisfaction, feedback_text
                            )
                            
                            # 设置满意度到状态中供路由使用
                            self.current_state["current_satisfaction"] = satisfaction
                            
                            # 清除用户输入需求标志，让工作流知道可以继续
                            self.current_state["requires_user_input"] = False
                            self.current_state["pending_questions"] = []
                            
                            if satisfaction in [UserSatisfactionLevel.SATISFIED, UserSatisfactionLevel.VERY_SATISFIED]:
                                print(f"\n✅ 用户满意，继续进入目标拆分阶段...")
                                # 直接调用目标拆分节点执行，跳过重新循环
                                try:
                                    print("🎯 开始执行目标拆分...")
                                    goal_result = goal_decomposer_node(self.current_state)
                                    if isinstance(goal_result, dict):
                                        # 将结果字典的键值对合并到当前状态
                                        for key, value in goal_result.items():
                                            if key in self.current_state or hasattr(self.current_state, key):
                                                self.current_state[key] = value  # type: ignore
                                    
                                    print("📅 开始执行日程规划...")
                                    schedule_result = scheduler_node(self.current_state)
                                    if isinstance(schedule_result, dict):
                                        # 将结果字典的键值对合并到当前状态
                                        for key, value in schedule_result.items():
                                            if key in self.current_state or hasattr(self.current_state, key):
                                                self.current_state[key] = value  # type: ignore
                                    
                                    # 显示最终计划并直接完成工作流
                                    if "final_career_plan" in self.current_state:
                                        self.display_goal_plan(self.current_state["final_career_plan"])
                                        print(f"\n🎉 职业规划完成！用户满意度: {satisfaction.value}")
                                        self.current_state["current_stage"] = WorkflowStage.COMPLETED
                                        workflow_completed = True
                                        break
                                        
                                except Exception as e:
                                    print(f"❌ 执行目标拆分和规划出错: {e}")
                                    break
                            else:
                                print(f"\n🔄 用户不满意，将重新执行分析...")
                                # 不满意用户跳出当前流处理，重新启动工作流
                                break
                        
                        # 1.5. 检查是否进入了目标拆分阶段（可能是因为目标明确直接跳过分析，或达到最大迭代次数）
                        elif current_stage == WorkflowStage.GOAL_DECOMPOSITION:
                            skip_reason = self.current_state.get("skip_feedback_reason")
                            if skip_reason:
                                print(f"\n⚠️ 跳过用户反馈阶段：{skip_reason}")
                            else:
                                print(f"\n✅ 目标已明确，直接进入目标拆分阶段")
                            
                            print("📊 显示分析报告...")
                            
                            # 显示报告（如果有）
                            if "integrated_report" in self.current_state:
                                report = self.current_state["integrated_report"]
                                if report:
                                    self.display_report(report)
                            else:
                                print("ℹ️ 由于直接进入目标拆分，跳过了详细的行业和职业分析报告。")
                            
                            print("🎯 正在生成最终职业规划...")
                            
                            # 手动执行后续节点以确保完成
                            try:
                                print("🎯 开始执行目标拆分...")
                                goal_result = goal_decomposer_node(self.current_state)
                                if isinstance(goal_result, dict):
                                    for key, value in goal_result.items():
                                        if key in self.current_state or hasattr(self.current_state, key):
                                            self.current_state[key] = value  # type: ignore
                                
                                print("📅 开始执行日程规划...")
                                schedule_result = scheduler_node(self.current_state)
                                if isinstance(schedule_result, dict):
                                    for key, value in schedule_result.items():
                                        if key in self.current_state or hasattr(self.current_state, key):
                                            self.current_state[key] = value  # type: ignore
                                
                                # 显示最终计划并直接完成工作流
                                if "final_career_plan" in self.current_state:
                                    self.display_goal_plan(self.current_state["final_career_plan"])
                                    if skip_reason:
                                        print(f"\n🎉 职业规划完成！(由于达到最大迭代次数跳过反馈)")
                                    else:
                                        print(f"\n🎉 职业规划完成！(目标明确，直接生成规划)")
                                    self.current_state["current_stage"] = WorkflowStage.COMPLETED
                                    workflow_completed = True
                                    break
                                    
                            except Exception as e:
                                print(f"❌ 执行目标拆分和规划出错: {e}")
                                break
                        
                        # 2. 工作流完成
                        elif current_stage == WorkflowStage.COMPLETED:
                            print(f"\n🎉 职业规划完成！")
                            workflow_completed = True
                            break
                    
                    # 如果正常完成了一轮流处理，检查是否真的完成了
                    if workflow_completed:
                        break
                    
                    # 如果没有触发任何用户交互，可能是工作流正常结束了
                    final_stage = self.current_state.get("current_stage")
                    if final_stage == WorkflowStage.COMPLETED:
                        print(f"\n🎉 职业规划自然完成！")
                        workflow_completed = True
                        break
                
                except Exception as e:
                    print(f"❌ 工作流执行出错: {e}")
                    # 可以选择重试或退出
                    break
                if workflow_completed:
                    break
            
            # 检查是否因为安全计数器达到限制而结束
            if safety_counter >= max_safety_iterations:
                print(f"\n⚠️ 达到最大安全迭代次数（{max_safety_iterations}），强制结束工作流")
                print("🔄 这可能表示工作流存在无限循环问题")
            
            # 显示最终结果
            self.display_final_results()
            
        except Exception as e:
            print(f"\n❌ 工作流执行异常: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True
    
    def display_final_results(self):
        """显示最终结果"""
        self.print_separator("🏆 规划完成")
        
        if self.current_state is None:
            print("❌ 当前状态为空，无法显示结果")
            return
        
        try:
            session_info = self.graph.get_current_stage_info(self.current_state)
            print(f"会话ID: {self.current_state.get('session_id', '未知')}")
            print(f"当前阶段: {session_info.get('stage_info', {}).get('name', '未知')}")
            
            # 安全获取迭代次数
            iteration_count = session_info.get('iteration_count', 0)
            if iteration_count is None:
                iteration_count = self.current_state.get('system_metrics', {}).get('iteration_count', 0)
            print(f"迭代次数: {iteration_count}")
            
        except Exception as e:
            print(f"⚠️ 获取会话信息失败: {e}")
            print(f"会话ID: {self.current_state.get('session_id', '未知')}")
        
        if self.current_state and "final_career_plan" in self.current_state:
            print(f"\n✅ 最终职业规划已生成")
        
        if self.current_state and "integrated_report" in self.current_state:
            print(f"✅ 综合分析报告已生成")
        
        feedback_count = len(self.current_state.get("user_feedback_history", []))
        if feedback_count > 0:
            print(f"✅ 收集了 {feedback_count} 次用户反馈")


def main():
    """主函数"""
    if not IMPORT_SUCCESS:
        print("❌ 模块导入失败，请检查环境配置")
        return
    
    # 测试用户资料
    test_user_profile = {
        "user_id": "interactive_user_001",
        "age": 28,
        "education_level": "本科",
        "work_experience": 3,
        "current_position": "软件工程师",
        "industry": "互联网",
        "skills": ["Python", "JavaScript", "React"],
        "interests": ["人工智能", "产品管理"],
        "career_goals": "希望转向AI产品经理方向发展",
        "location": "北京",
        "salary_expectation": "30-50万"
    }
    
    # initial_message = "我想从当前的软件工程师岗位转向AI产品经理，希望得到详细的职业规划建议"
    initial_message = "我是智能交互设计专业的大三本科生，应该从事什么岗位，帮我进行职业规划"
    
    # 创建交互式执行器并运行
    runner = InteractiveWorkflowRunner()
    success = runner.run_interactive_workflow(test_user_profile, initial_message)  # type: ignore
    
    if success:
        print("\n🎉 交互式职业规划完成！")
    else:
        print("\n❌ 交互式职业规划失败") 


if __name__ == "__main__":
    main()
