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
if not os.getenv('DASHSCOPE_API_KEY'):
    os.environ['DASHSCOPE_API_KEY'] = 'sk-temp-for-testing'

try:
    from src.services.career_graph import CareerNavigatorGraph
    from src.models.career_state import (
        CareerNavigatorState, WorkflowStage, UserProfile, UserSatisfactionLevel,
        create_initial_state, StateUpdater, UserFeedback
    )
    from langchain_core.messages import HumanMessage
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
            
            for state_update in self.graph.app.stream(self.current_state):
                print(f"📈 工作流进度: {list(state_update.keys())}")
                
                # 更新当前状态
                node_name = list(state_update.keys())[-1]
                self.current_state = state_update[node_name]
                
                # 检查是否到达需要用户反馈的阶段
                current_stage = self.current_state.get("current_stage")
                
                # 1. 分析报告反馈阶段
                if current_stage == WorkflowStage.USER_FEEDBACK and "integrated_report" in self.current_state:
                    report = self.current_state["integrated_report"]
                    self.display_report(report)
                    
                    # 收集用户反馈
                    satisfaction, feedback_text = self.get_user_feedback()
                    
                    # 更新状态并继续执行
                    self.current_state = self.graph.update_user_feedback(
                        self.current_state, satisfaction, feedback_text
                    )
                    
                    if satisfaction in [UserSatisfactionLevel.SATISFIED, UserSatisfactionLevel.VERY_SATISFIED]:
                        print(f"\n✅ 用户满意，继续进入目标拆分阶段...")
                        # 继续执行工作流
                        continue
                    else:
                        print(f"\n🔄 用户不满意，重新执行分析...")
                        # 重新开始分析流程
                        continue
                
                # 2. 最终规划反馈阶段  
                elif current_stage == WorkflowStage.FINAL_CONFIRMATION and "final_career_plan" in self.current_state:
                    plan = self.current_state["final_career_plan"]
                    self.display_goal_plan(plan)
                    
                    # 收集用户对最终规划的反馈
                    satisfaction, feedback_text = self.get_user_feedback()
                    
                    # 更新状态
                    self.current_state = self.graph.update_user_feedback(
                        self.current_state, satisfaction, feedback_text
                    )
                    
                    if satisfaction in [UserSatisfactionLevel.SATISFIED, UserSatisfactionLevel.VERY_SATISFIED]:
                        print(f"\n🎉 规划完成！用户满意度: {satisfaction.value}")
                        break
                    else:
                        print(f"\n🔄 用户不满意最终规划，重新调整...")
                        continue
                
                # 3. 工作流完成
                elif current_stage == WorkflowStage.COMPLETED:
                    print(f"\n🎉 职业规划完成！")
                    break
            
            # 显示最终结果
            self.display_final_results()
            
        except Exception as e:
            print(f"\n❌ 工作流执行异常: {e}")
            return False
        
        return True
    
    def display_final_results(self):
        """显示最终结果"""
        self.print_separator("🏆 规划完成")
        
        if self.current_state is None:
            print("❌ 当前状态为空，无法显示结果")
            return
        
        session_info = self.graph.get_current_stage_info(self.current_state)
        
        print(f"会话ID: {self.current_state.get('session_id', '未知')}")
        print(f"当前阶段: {session_info['stage_info'].get('name', '未知')}")
        print(f"迭代次数: {session_info['iteration_count']}")
        
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
    
    initial_message = "我想从当前的软件工程师岗位转向AI产品经理，希望得到详细的职业规划建议"
    
    # 创建交互式执行器并运行
    runner = InteractiveWorkflowRunner()
    success = runner.run_interactive_workflow(test_user_profile, initial_message)  # type: ignore
    
    if success:
        print("\n🎉 交互式职业规划完成！")
    else:
        print("\n❌ 交互式职业规划失败")


if __name__ == "__main__":
    main()
