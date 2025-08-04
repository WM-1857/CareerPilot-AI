#!/usr/bin/env python3
"""
端到端人机交互测试
测试完整的用户交互流程和实际的人机对话
"""

import os
import sys
import json
import time
from typing import Dict, Any, Optional

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 加载环境变量
def load_env():
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

try:
    from src.services.career_graph import CareerNavigatorGraph
    from src.models.career_state import (
        CareerNavigatorState, WorkflowStage, UserProfile, UserSatisfactionLevel,
        create_initial_state
    )
    from src.utils.logger import main_logger
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请先运行环境测试确保所有依赖正常")
    sys.exit(1)


class E2EInteractiveTester:
    """端到端交互测试器"""
    
    def __init__(self):
        self.results = {}
        self.graph = CareerNavigatorGraph()
        self.current_state = None
        self.session_id = None
        
        # 测试配置
        self.test_modes = {
            "auto": "自动测试模式（预设响应）",
            "interactive": "交互测试模式（真实用户输入）",
            "mixed": "混合模式（部分自动，部分交互）"
        }
        
        # 预设的自动响应
        self.auto_responses = {
            "dissatisfied_feedback": "我希望重点关注大模型和多智能体方向的AI产品经理岗位，现在的分析太泛泛",
            "satisfied_feedback": "这个分析很好，我很满意",
            "plan_feedback": "计划很详细，我同意这个安排"
        }
        
        self.test_user_profile = {
            "user_id": "e2e_test_user",
            "age": 28,
            "education_level": "本科",
            "work_experience": 3,
            "current_position": "软件工程师",
            "industry": "互联网",
            "skills": ["Python", "JavaScript", "React", "机器学习"],
            "interests": ["人工智能", "产品管理", "创业"],
            "career_goals": "希望转向AI产品经理方向发展",
            "location": "北京",
            "salary_expectation": "30-50万",
            "additional_info": {
                "work_values": ["创新", "挑战", "成长"],
                "personality_traits": ["逻辑思维强", "沟通能力好", "学习能力强"],
                "work_preference": "大厂或有潜力的AI创业公司",
                "constraints": ["不能出差太频繁"]
            }
        }
    
    def print_separator(self, title: str):
        """打印分隔符"""
        print(f"\n{'='*80}")
        print(f"  {title}")
        print('='*80)
    
    def print_result(self, test_name: str, success: bool, message: str, details: str = ""):
        """打印测试结果"""
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   📝 {details}")
        self.results[test_name] = {"success": success, "message": message, "details": details}
        return success
    
    def select_test_mode(self) -> str:
        """选择测试模式"""
        print("\n🎛️ 请选择测试模式:")
        for key, desc in self.test_modes.items():
            print(f"  {key}: {desc}")
        
        while True:
            try:
                mode = input("\n请输入测试模式 (auto/interactive/mixed): ").strip().lower()
                if mode in self.test_modes:
                    print(f"✅ 选择了 {mode} 模式: {self.test_modes[mode]}")
                    return mode
                else:
                    print("❌ 无效选择，请输入 auto、interactive 或 mixed")
            except KeyboardInterrupt:
                print("\n👋 测试被用户中断")
                sys.exit(0)
    
    def print_stage_info(self, state: CareerNavigatorState):
        """打印当前阶段信息"""
        try:
            stage_info = self.graph.get_current_stage_info(state)
            
            print(f"\n📍 当前阶段: {stage_info['stage_info'].get('name', '未知')}")
            print(f"📝 阶段描述: {stage_info['stage_info'].get('description', '无描述')}")
            print(f"🔄 迭代次数: {stage_info['iteration_count']}/{stage_info['max_iterations']}")
            
            if stage_info['requires_user_input']:
                print("⏳ 需要用户输入")
                questions = stage_info.get('pending_questions', [])
                if questions:
                    print("❓ 待回答问题:")
                    for i, question in enumerate(questions, 1):
                        print(f"   {i}. {question}")
        except Exception as e:
            print(f"⚠️ 无法获取阶段信息: {e}")
            current_stage = state.get("current_stage", "未知")
            print(f"📍 当前阶段: {current_stage}")
    
    def display_current_results(self, state: CareerNavigatorState):
        """显示当前阶段的结果"""
        current_stage = state.get("current_stage")
        
        if current_stage == WorkflowStage.USER_FEEDBACK:
            # 显示综合报告
            report = state.get("integrated_report")
            if report:
                print("\n📊 综合分析报告:")
                print("-" * 60)
                
                if "executive_summary" in report:
                    print(f"📋 执行摘要: {report['executive_summary']}")
                
                if "career_match" in report:
                    career_match = report["career_match"]
                    print(f"🎯 推荐职业: {career_match.get('recommended_career', 'N/A')}")
                    print(f"📈 匹配度: {career_match.get('match_score', 'N/A')}")
                
                if "key_findings" in report:
                    findings = report["key_findings"]
                    if isinstance(findings, list):
                        print("🔍 关键发现:")
                        for finding in findings:
                            print(f"   • {finding}")
                
                if "recommendations" in report:
                    recommendations = report["recommendations"]
                    if isinstance(recommendations, list):
                        print("💡 建议:")
                        for rec in recommendations:
                            print(f"   • {rec}")
                            
                # 显示迭代信息
                iteration_count = state.get("iteration_count", 0)
                if iteration_count > 0:
                    print(f"\n🔄 这是第 {iteration_count + 1} 次分析结果")
                    feedback_history = state.get("user_feedback_history", [])
                    if feedback_history:
                        latest_feedback = feedback_history[-1]
                        print(f"💬 基于您的反馈: {latest_feedback.get('feedback_text', '')}")
                        
        elif current_stage == WorkflowStage.FINAL_CONFIRMATION:
            # 显示最终计划
            final_plan = state.get("final_plan")
            career_goals = state.get("career_goals")
            
            print("\n🎯 最终职业规划:")
            print("-" * 60)
            
            if career_goals:
                if isinstance(career_goals, dict):
                    if "short_term_goals" in career_goals:
                        print("📅 短期目标 (3-6个月):")
                        goals = career_goals["short_term_goals"]
                        if isinstance(goals, list):
                            for goal in goals:
                                print(f"   • {goal}")
                    
                    if "medium_term_goals" in career_goals:
                        print("📆 中期目标 (6个月-2年):")
                        goals = career_goals["medium_term_goals"]
                        if isinstance(goals, list):
                            for goal in goals:
                                print(f"   • {goal}")
                    
                    if "long_term_goals" in career_goals:
                        print("📊 长期目标 (2-5年):")
                        goals = career_goals["long_term_goals"]
                        if isinstance(goals, list):
                            for goal in goals:
                                print(f"   • {goal}")
            
            if final_plan:
                if "schedule_overview" in final_plan:
                    print(f"\n⏰ 总体时间规划: {final_plan['schedule_overview']}")
                
                if "milestones" in final_plan:
                    milestones = final_plan["milestones"]
                    if isinstance(milestones, list):
                        print("🎖️ 重要里程碑:")
                        for milestone in milestones:
                            print(f"   • {milestone}")
    
    def wait_for_user_feedback(self, state: CareerNavigatorState, mode: str) -> CareerNavigatorState:
        """等待并处理用户反馈"""
        self.print_separator("等待用户反馈")
        
        # 显示当前阶段的报告或结果
        self.display_current_results(state)
        
        iteration_count = state.get("iteration_count", 0)
        current_stage = state.get("current_stage")
        
        # 根据模式和情况选择反馈方式
        if mode == "auto":
            # 自动模式：使用预设响应
            if current_stage == WorkflowStage.USER_FEEDBACK:
                if iteration_count == 0:
                    # 第一次给不满意反馈，触发迭代
                    feedback_text = self.auto_responses["dissatisfied_feedback"]
                    satisfaction_level = UserSatisfactionLevel.DISSATISFIED
                    print(f"\n🤖 自动反馈（不满意）: {feedback_text}")
                else:
                    # 第二次给满意反馈，继续流程
                    feedback_text = self.auto_responses["satisfied_feedback"]
                    satisfaction_level = UserSatisfactionLevel.SATISFIED
                    print(f"\n🤖 自动反馈（满意）: {feedback_text}")
            elif current_stage == WorkflowStage.FINAL_CONFIRMATION:
                feedback_text = self.auto_responses["plan_feedback"]
                satisfaction_level = UserSatisfactionLevel.SATISFIED
                print(f"\n🤖 自动反馈（计划确认）: {feedback_text}")
            else:
                feedback_text = "自动测试反馈"
                satisfaction_level = UserSatisfactionLevel.SATISFIED
                
        elif mode == "mixed":
            # 混合模式：第一次自动，后续交互
            if iteration_count == 0 and current_stage == WorkflowStage.USER_FEEDBACK:
                feedback_text = self.auto_responses["dissatisfied_feedback"]
                satisfaction_level = UserSatisfactionLevel.DISSATISFIED
                print(f"\n🤖 自动反馈（触发迭代）: {feedback_text}")
            else:
                # 交互式反馈
                satisfaction_level, feedback_text = self._get_interactive_feedback()
                
        else:  # interactive
            # 完全交互模式
            satisfaction_level, feedback_text = self._get_interactive_feedback()
        
        # 更新状态
        updated_state = self.graph.update_user_feedback(
            state, satisfaction_level, feedback_text
        )
        
        print(f"\n✅ 已记录反馈: {satisfaction_level.value}")
        if feedback_text:
            print(f"💬 反馈内容: {feedback_text}")
        
        return updated_state
    
    def _get_interactive_feedback(self):
        """获取交互式用户反馈"""
        print("\n🔄 请对当前结果进行评估:")
        print("1. 很满意 (very_satisfied)")
        print("2. 满意 (satisfied)")  
        print("3. 中性 (neutral)")
        print("4. 不满意 (dissatisfied)")
        print("5. 很不满意 (very_dissatisfied)")
        print("6. 直接输入详细反馈")
        
        while True:
            try:
                user_input = input("\n请选择满意度级别 (1-5) 或输入详细反馈: ").strip()
                
                if user_input in ["1", "2", "3", "4", "5"]:
                    satisfaction_mapping = {
                        "1": UserSatisfactionLevel.VERY_SATISFIED,
                        "2": UserSatisfactionLevel.SATISFIED,
                        "3": UserSatisfactionLevel.NEUTRAL,
                        "4": UserSatisfactionLevel.DISSATISFIED,
                        "5": UserSatisfactionLevel.VERY_DISSATISFIED
                    }
                    satisfaction_level = satisfaction_mapping[user_input]
                    
                    # 获取详细反馈
                    feedback_text = input("请提供具体的反馈意见 (可选): ").strip()
                    
                    return satisfaction_level, feedback_text
                    
                elif len(user_input) > 10:  # 详细反馈
                    # 根据反馈内容自动判断满意度
                    positive_keywords = ["好", "满意", "不错", "优秀", "赞", "棒", "perfect", "good", "great"]
                    negative_keywords = ["不好", "不满意", "差", "糟糕", "问题", "错误", "bad", "poor", "terrible"]
                    
                    feedback_lower = user_input.lower()
                    if any(keyword in feedback_lower for keyword in positive_keywords):
                        satisfaction_level = UserSatisfactionLevel.SATISFIED
                    elif any(keyword in feedback_lower for keyword in negative_keywords):
                        satisfaction_level = UserSatisfactionLevel.DISSATISFIED
                    else:
                        satisfaction_level = UserSatisfactionLevel.NEUTRAL
                    
                    return satisfaction_level, user_input
                    
                else:
                    print("❌ 输入无效，请选择 1-5 或输入详细反馈 (至少10个字符)")
                    
            except KeyboardInterrupt:
                print("\n\n👋 用户中断测试")
                return UserSatisfactionLevel.NEUTRAL, "用户中断"
            except Exception as e:
                print(f"❌ 输入处理错误: {e}")
    
    def run_workflow_step(self, state: CareerNavigatorState, mode: str) -> Optional[CareerNavigatorState]:
        """运行工作流的一个步骤"""
        try:
            print(f"\n🚀 运行工作流步骤...")
            
            # 运行工作流
            result = None
            step_count = 0
            
            if self.graph.app:
                for state_update in self.graph.app.stream(state):
                    step_count += 1
                    print(f"📝 步骤 {step_count}: {list(state_update.keys())}")
                    
                    # 获取最新状态
                    last_node = list(state_update.keys())[-1]
                    current_state = state_update[last_node]
                    
                    # 显示阶段信息
                    self.print_stage_info(current_state)
                    
                    # 检查是否需要用户输入
                    if current_state.get("requires_user_input"):
                        print("\n⏸️ 工作流暂停，等待用户反馈...")
                        
                        # 等待用户反馈
                        updated_state = self.wait_for_user_feedback(current_state, mode)
                        
                        # 确保状态的完整性
                        critical_fields = ["messages", "session_id", "user_profile", "current_stage", 
                                         "iteration_count", "max_iterations", "agent_tasks", "agent_outputs",
                                         "user_feedback_history", "system_metrics", "error_log"]
                        
                        for field in critical_fields:
                            if field not in updated_state and field in current_state:
                                updated_state[field] = current_state[field]
                        
                        # 确保基本默认值
                        if "messages" not in updated_state:
                            updated_state["messages"] = []
                        if "agent_tasks" not in updated_state:
                            updated_state["agent_tasks"] = []
                        if "agent_outputs" not in updated_state:
                            updated_state["agent_outputs"] = []
                        if "error_log" not in updated_state:
                            updated_state["error_log"] = []
                        
                        return updated_state
                    
                    result = current_state
            else:
                print("❌ 工作流应用未初始化")
                return None
            
            return result
            
        except Exception as e:
            print(f"❌ 工作流执行错误: {e}")
            main_logger.error(f"工作流执行错误: {e}", exc_info=True)
            return None
    
    def test_complete_e2e_workflow(self, mode: str) -> bool:
        """测试完整的端到端工作流"""
        print(f"\n🎯 测试完整端到端工作流 ({mode}模式)...")
        
        try:
            # 1. 创建测试用户档案
            print("\n1️⃣ 创建测试用户档案...")
            print(f"✅ 用户档案: {self.test_user_profile['career_goals']}")
            
            # 2. 创建初始会话
            print("\n2️⃣ 创建会话状态...")
            user_message = "我想从软件工程师转向AI产品经理，需要制定一个详细的职业发展规划"
            initial_state = self.graph.create_session(self.test_user_profile, user_message)
            self.session_id = initial_state["session_id"]
            print(f"✅ 会话创建完成: {self.session_id}")
            
            # 3. 运行工作流
            print(f"\n3️⃣ 开始运行LangGraph工作流 ({mode}模式)...")
            current_state = initial_state
            max_cycles = 20  # 防止无限循环
            cycle_count = 0
            feedback_count = 0
            
            while cycle_count < max_cycles:
                cycle_count += 1
                print(f"\n🔄 执行周期 {cycle_count}")
                
                # 运行一个工作流步骤
                result_state = self.run_workflow_step(current_state, mode)
                
                if result_state is None:
                    print("❌ 工作流执行失败")
                    break
                
                current_state = result_state
                
                # 如果处理了用户反馈，计数
                if current_state.get("user_feedback_history"):
                    new_feedback_count = len(current_state["user_feedback_history"])
                    if new_feedback_count > feedback_count:
                        feedback_count = new_feedback_count
                        print(f"💬 已处理 {feedback_count} 次用户反馈")
                
                # 检查是否完成
                current_stage = current_state.get("current_stage")
                if current_stage in [WorkflowStage.COMPLETED, WorkflowStage.FINAL_CONFIRMATION]:
                    print(f"🎉 工作流到达终点: {current_stage}")
                    break
                
                # 如果没有需要用户输入且没有继续执行，可能已结束
                if not current_state.get("requires_user_input"):
                    print("ℹ️ 工作流自然结束（无需更多用户输入）")
                    break
            
            # 4. 验证最终结果
            final_stage = current_state.get("current_stage")
            iteration_count = current_state.get("iteration_count", 0)
            
            # 检查关键结果是否生成
            has_analysis_results = all([
                current_state.get("self_insight_result"),
                current_state.get("industry_research_result"),
                current_state.get("career_analysis_result"),
                current_state.get("integrated_report")
            ])
            
            has_planning_results = current_state.get("career_goals") or current_state.get("final_plan")
            
            # 评估测试成功性
            success_criteria = [
                cycle_count < max_cycles,  # 未超时
                feedback_count > 0,  # 至少有一次反馈
                has_analysis_results,  # 有分析结果
                final_stage in [WorkflowStage.FINAL_CONFIRMATION, WorkflowStage.SCHEDULE_PLANNING, WorkflowStage.COMPLETED]  # 到达合理的最终阶段
            ]
            
            success = all(success_criteria)
            
            return self.print_result(
                f"完整E2E工作流_{mode}",
                success,
                f"E2E测试{'成功' if success else '失败'}",
                f"周期: {cycle_count}, 反馈: {feedback_count}, 迭代: {iteration_count}, 最终阶段: {final_stage}"
            )
            
        except Exception as e:
            return self.print_result(
                f"完整E2E工作流_{mode}",
                False,
                "E2E测试异常",
                f"异常: {str(e)}"
            )
    
    def display_final_results(self, final_state: CareerNavigatorState):
        """显示最终测试结果"""
        self.print_separator("最终结果展示")
        
        print(f"🏁 最终阶段: {final_state.get('current_stage', 'unknown')}")
        print(f"🔄 总迭代次数: {final_state.get('iteration_count', 0)}")
        print(f"🆔 会话ID: {final_state.get('session_id', 'unknown')}")
        
        # 显示关键结果
        results_summary = []
        if final_state.get("integrated_report"):
            results_summary.append("📊 综合分析报告")
            
        if final_state.get("career_goals"):
            results_summary.append("🎯 职业目标拆分")
            
        if final_state.get("final_plan"):
            results_summary.append("📅 详细行动计划")
        
        if results_summary:
            print(f"\n✅ 生成的结果:")
            for result in results_summary:
                print(f"   {result}")
        
        # 显示用户反馈历史
        feedback_history = final_state.get("user_feedback_history", [])
        if feedback_history:
            print(f"\n💬 用户反馈历史 ({len(feedback_history)} 次):")
            for i, feedback in enumerate(feedback_history, 1):
                satisfaction = feedback.get('satisfaction_level', 'unknown')
                feedback_text = feedback.get('feedback_text', 'N/A')
                print(f"   {i}. {satisfaction}: {feedback_text[:50]}{'...' if len(feedback_text) > 50 else ''}")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有E2E测试"""
        self.print_separator("CareerNavigator 端到端测试")
        
        # 选择测试模式
        mode = self.select_test_mode()
        
        print(f"🚀 开始端到端测试 ({mode}模式)...")
        start_time = time.time()
        
        # 运行E2E测试
        e2e_result = self.test_complete_e2e_workflow(mode)
        
        # 汇总结果
        end_time = time.time()
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r["success"])
        
        self.print_separator("测试结果汇总")
        print(f"📊 总测试数: {total_tests}")
        print(f"✅ 通过: {passed_tests}")
        print(f"❌ 失败: {total_tests - passed_tests}")
        print(f"⏱️ 耗时: {end_time - start_time:.2f}秒")
        print(f"🎛️ 测试模式: {self.test_modes[mode]}")
        
        if e2e_result:
            print("\n🎉 端到端测试通过！系统可以正常服务用户。")
        else:
            print("\n⚠️ 端到端测试失败，请检查完整工作流程。")
        
        return {
            "overall_success": e2e_result,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "duration": end_time - start_time,
            "mode": mode,
            "details": self.results
        }


def main():
    """主函数"""
    print("🤖 CareerNavigator 端到端人机交互测试")
    print("=" * 80)
    print("这个测试将运行完整的工作流程，包括真实的LLM调用和用户交互")
    print("请确保:")
    print("1. 已设置正确的API密钥")
    print("2. 网络连接正常")
    print("3. 有足够时间完成交互测试")
    
    confirm = input("\n是否继续？(y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("👋 测试已取消")
        return
    
    tester = E2EInteractiveTester()
    results = tester.run_all_tests()
    
    print("\n" + "="*80)
    print("端到端测试完成！")
    
    # 返回退出码
    exit_code = 0 if results["overall_success"] else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
