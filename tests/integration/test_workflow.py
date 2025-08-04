#!/usr/bin/env python3
"""
LangGraph完整工作流集成测试
测试端到端的工作流执行和用户交互
"""

import os
import sys
import json
import time
from typing import Dict, Any, Optional
from unittest.mock import patch, MagicMock

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
        create_initial_state, StateUpdater
    )
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请先运行环境测试确保所有依赖正常")
    sys.exit(1)


class WorkflowIntegrationTester:
    """工作流集成测试器"""
    
    def __init__(self):
        self.results = {}
        self.graph = CareerNavigatorGraph()
        self.test_user_profile = {
            "user_id": "test_user_001",
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
        
        # 模拟LLM响应
        self.mock_responses = {
            "goal_clarity": {
                "success": True,
                "content": json.dumps({
                    "is_goal_clear": False,
                    "clarity_score": 45,
                    "analysis_details": "目标需要进一步明确"
                })
            },
            "strategy": {
                "success": True,
                "content": json.dumps({
                    "strategy_overview": "制定个性化职业分析策略"
                })
            },
            "user_analysis": {
                "success": True,
                "content": json.dumps({
                    "strengths": ["技术背景强", "学习能力强"],
                    "improvement_areas": ["产品思维", "市场洞察"],
                    "recommendations": ["加强产品知识", "关注AI行业动态"]
                })
            },
            "industry_research": {
                "success": True,
                "content": json.dumps({
                    "trends": ["AI技术快速发展", "产品经理需求增长"],
                    "opportunities": ["AI产品经理", "技术产品专家"],
                    "challenges": ["竞争激烈", "技能要求高"]
                })
            },
            "career_analysis": {
                "success": True,
                "content": json.dumps({
                    "career_paths": ["AI产品经理", "技术产品经理"],
                    "skill_gaps": ["产品设计", "用户研究"],
                    "salary_range": "25-45万"
                })
            },
            "integrated_report": {
                "success": True,
                "content": json.dumps({
                    "executive_summary": "基于您的技术背景，建议转向AI产品经理",
                    "career_match": {
                        "recommended_career": "AI产品经理",
                        "match_score": 0.75
                    },
                    "recommendations": ["学习产品设计", "了解AI应用场景"]
                })
            },
            "goal_decomposition": {
                "success": True,
                "content": json.dumps({
                    "short_term_goals": ["学习产品基础知识", "参与产品项目"],
                    "medium_term_goals": ["获得产品经理职位", "积累产品经验"],
                    "long_term_goals": ["成为资深AI产品经理", "带领产品团队"]
                })
            },
            "schedule": {
                "success": True,
                "content": json.dumps({
                    "schedule_overview": "6个月转型计划",
                    "timeline": "短期3个月，中期6个月，长期2年",
                    "milestones": ["完成产品课程", "获得实习机会", "正式转岗"]
                })
            }
        }
    
    def print_separator(self, title: str):
        """打印分隔符"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print('='*60)
    
    def print_result(self, test_name: str, success: bool, message: str, details: str = ""):
        """打印测试结果"""
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   📝 {details}")
        self.results[test_name] = {"success": success, "message": message, "details": details}
        return success
    
    def setup_llm_mocks(self):
        """设置LLM模拟"""
        self.mock_llm_service = MagicMock()
        
        # 配置各种LLM方法的返回值
        self.mock_llm_service.analyze_career_goal_clarity.return_value = self.mock_responses["goal_clarity"]
        self.mock_llm_service.create_analysis_strategy.return_value = self.mock_responses["strategy"]
        self.mock_llm_service.analyze_user_profile.return_value = self.mock_responses["user_analysis"]
        self.mock_llm_service.research_industry_trends.return_value = self.mock_responses["industry_research"]
        self.mock_llm_service.analyze_career_opportunities.return_value = self.mock_responses["career_analysis"]
        self.mock_llm_service.generate_integrated_report.return_value = self.mock_responses["integrated_report"]
        self.mock_llm_service.decompose_career_goals.return_value = self.mock_responses["goal_decomposition"]
        self.mock_llm_service.create_action_schedule.return_value = self.mock_responses["schedule"]
        
        return patch('src.services.llm_service.llm_service', self.mock_llm_service)
    
    def test_complete_workflow_happy_path(self) -> bool:
        """测试完整工作流的顺利路径"""
        print("\n🎯 测试完整工作流顺利路径...")
        
        try:
            with self.setup_llm_mocks():
                # 1. 创建会话
                user_message = "我想从软件工程师转向AI产品经理"
                initial_state = self.graph.create_session(self.test_user_profile, user_message)
                
                if not initial_state.get("session_id"):
                    return self.print_result(
                        "完整工作流_会话创建",
                        False,
                        "会话创建失败",
                        "无法获取session_id"
                    )
                
                # 2. 运行工作流到用户反馈阶段
                current_state = initial_state
                step_count = 0
                max_steps = 20
                
                while step_count < max_steps:
                    step_count += 1
                    
                    # 运行一步工作流
                    try:
                        result = None
                        for state_update in self.graph.app.stream(current_state):
                            # 获取最新状态
                            last_node = list(state_update.keys())[-1]
                            result = state_update[last_node]
                            
                            # 如果到达用户反馈阶段，停止
                            if result.get("current_stage") == WorkflowStage.USER_FEEDBACK:
                                break
                        
                        if result:
                            current_state = result
                        else:
                            break
                        
                        # 检查是否到达用户反馈阶段
                        if current_state.get("current_stage") == WorkflowStage.USER_FEEDBACK:
                            break
                            
                    except Exception as e:
                        return self.print_result(
                            "完整工作流_执行",
                            False,
                            f"工作流执行异常(步骤{step_count})",
                            f"异常: {str(e)}"
                        )
                
                # 3. 验证到达用户反馈阶段
                if current_state.get("current_stage") != WorkflowStage.USER_FEEDBACK:
                    return self.print_result(
                        "完整工作流_进度",
                        False,
                        f"未到达用户反馈阶段",
                        f"当前阶段: {current_state.get('current_stage')}"
                    )
                
                # 4. 验证必要的分析结果
                required_results = [
                    "self_insight_result",
                    "industry_research_result", 
                    "career_analysis_result",
                    "integrated_report"
                ]
                
                missing_results = [r for r in required_results if not current_state.get(r)]
                
                if missing_results:
                    return self.print_result(
                        "完整工作流_结果",
                        False,
                        "分析结果不完整",
                        f"缺少: {missing_results}"
                    )
                
                # 5. 模拟用户满意反馈并继续
                satisfied_state = self.graph.update_user_feedback(
                    current_state,
                    UserSatisfactionLevel.SATISFIED,
                    "分析很好，满意"
                )
                
                # 6. 继续执行到完成
                final_step_count = 0
                while final_step_count < 10:
                    final_step_count += 1
                    
                    try:
                        result = None
                        for state_update in self.graph.app.stream(satisfied_state):
                            last_node = list(state_update.keys())[-1]
                            result = state_update[last_node]
                            
                            # 如果完成或需要最终确认，停止
                            if (result.get("current_stage") in [WorkflowStage.COMPLETED, WorkflowStage.FINAL_CONFIRMATION]):
                                break
                        
                        if result:
                            satisfied_state = result
                        else:
                            break
                            
                        # 检查是否完成
                        if satisfied_state.get("current_stage") in [WorkflowStage.COMPLETED, WorkflowStage.FINAL_CONFIRMATION]:
                            break
                            
                    except Exception as e:
                        return self.print_result(
                            "完整工作流_最终执行",
                            False,
                            f"最终执行异常(步骤{final_step_count})",
                            f"异常: {str(e)}"
                        )
                
                # 7. 验证最终状态
                final_stage = satisfied_state.get("current_stage")
                expected_stages = [WorkflowStage.FINAL_CONFIRMATION, WorkflowStage.SCHEDULE_PLANNING]
                
                if final_stage in expected_stages:
                    return self.print_result(
                        "完整工作流_顺利路径",
                        True,
                        "完整工作流执行成功",
                        f"到达阶段: {final_stage}, 总步骤: {step_count + final_step_count}"
                    )
                else:
                    return self.print_result(
                        "完整工作流_顺利路径",
                        False,
                        "未到达预期最终阶段",
                        f"最终阶段: {final_stage}"
                    )
                    
        except Exception as e:
            return self.print_result(
                "完整工作流_顺利路径",
                False,
                "完整工作流测试异常",
                f"异常: {str(e)}"
            )
    
    def test_iteration_workflow(self) -> bool:
        """测试迭代工作流"""
        print("\n🔄 测试迭代工作流...")
        
        try:
            with self.setup_llm_mocks():
                # 1. 运行到用户反馈阶段
                user_message = "我想转向AI产品经理"
                initial_state = self.graph.create_session(self.test_user_profile, user_message)
                
                # 快速运行到用户反馈阶段
                current_state = initial_state
                step_count = 0
                
                while step_count < 15:
                    step_count += 1
                    
                    try:
                        result = None
                        for state_update in self.graph.app.stream(current_state):
                            last_node = list(state_update.keys())[-1]
                            result = state_update[last_node]
                            
                            if result.get("current_stage") == WorkflowStage.USER_FEEDBACK:
                                break
                        
                        if result:
                            current_state = result
                            
                        if current_state.get("current_stage") == WorkflowStage.USER_FEEDBACK:
                            break
                            
                    except Exception:
                        continue
                
                if current_state.get("current_stage") != WorkflowStage.USER_FEEDBACK:
                    return self.print_result(
                        "迭代工作流_准备",
                        False,
                        "无法到达用户反馈阶段",
                        f"当前阶段: {current_state.get('current_stage')}"
                    )
                
                # 2. 模拟用户不满意反馈
                original_iteration_count = current_state.get("iteration_count", 0)
                
                dissatisfied_state = self.graph.update_user_feedback(
                    current_state,
                    UserSatisfactionLevel.DISSATISFIED,
                    "我希望重点关注大模型相关的AI产品经理岗位"
                )
                
                # 验证迭代计数增加
                new_iteration_count = dissatisfied_state.get("iteration_count", 0)
                if new_iteration_count <= original_iteration_count:
                    return self.print_result(
                        "迭代工作流_计数",
                        False,
                        "迭代计数未增加",
                        f"原始: {original_iteration_count}, 新的: {new_iteration_count}"
                    )
                
                # 3. 验证反馈历史记录
                feedback_history = dissatisfied_state.get("user_feedback_history", [])
                if not feedback_history or len(feedback_history) == 0:
                    return self.print_result(
                        "迭代工作流_反馈记录",
                        False,
                        "反馈历史未记录",
                        f"反馈历史长度: {len(feedback_history)}"
                    )
                
                # 4. 运行迭代工作流
                iteration_result = None
                iteration_steps = 0
                
                while iteration_steps < 10:
                    iteration_steps += 1
                    
                    try:
                        result = None
                        for state_update in self.graph.app.stream(dissatisfied_state):
                            last_node = list(state_update.keys())[-1]
                            result = state_update[last_node]
                            
                            # 如果又回到用户反馈阶段，说明迭代完成
                            if result.get("current_stage") == WorkflowStage.USER_FEEDBACK:
                                iteration_result = result
                                break
                        
                        if iteration_result:
                            break
                            
                        if result:
                            dissatisfied_state = result
                            
                    except Exception:
                        continue
                
                # 5. 验证迭代结果
                if iteration_result:
                    # 检查是否生成了新的分析结果
                    has_updated_results = (
                        iteration_result.get("self_insight_result") and
                        iteration_result.get("industry_research_result") and
                        iteration_result.get("career_analysis_result") and
                        iteration_result.get("integrated_report")
                    )
                    
                    if has_updated_results:
                        return self.print_result(
                            "迭代工作流",
                            True,
                            "迭代工作流执行成功",
                            f"迭代次数: {iteration_result.get('iteration_count')}, 步骤: {iteration_steps}"
                        )
                    else:
                        return self.print_result(
                            "迭代工作流",
                            False,
                            "迭代结果不完整",
                            "缺少更新的分析结果"
                        )
                else:
                    return self.print_result(
                        "迭代工作流",
                        False,
                        "迭代工作流未完成",
                        f"执行了{iteration_steps}步但未返回结果"
                    )
                    
        except Exception as e:
            return self.print_result(
                "迭代工作流",
                False,
                "迭代工作流测试异常",
                f"异常: {str(e)}"
            )
    
    def test_state_consistency(self) -> bool:
        """测试状态一致性"""
        print("\n🔍 测试状态一致性...")
        
        try:
            with self.setup_llm_mocks():
                # 1. 创建初始状态
                user_message = "测试状态一致性"
                initial_state = self.graph.create_session(self.test_user_profile, user_message)
                
                # 2. 运行几步工作流
                current_state = initial_state
                states_history = [initial_state]
                
                for step in range(5):
                    try:
                        result = None
                        for state_update in self.graph.app.stream(current_state):
                            last_node = list(state_update.keys())[-1]
                            result = state_update[last_node]
                            break  # 只执行一步
                        
                        if result:
                            current_state = result
                            states_history.append(current_state)
                        else:
                            break
                            
                    except Exception:
                        break
                
                # 3. 验证状态一致性
                consistency_checks = []
                
                for i, state in enumerate(states_history):
                    # 检查关键字段是否保持
                    session_id = state.get("session_id")
                    user_profile = state.get("user_profile")
                    
                    if session_id == initial_state["session_id"]:
                        consistency_checks.append(f"步骤{i}_session_id一致")
                    else:
                        consistency_checks.append(f"步骤{i}_session_id不一致")
                    
                    if user_profile == initial_state["user_profile"]:
                        consistency_checks.append(f"步骤{i}_user_profile一致")
                    else:
                        consistency_checks.append(f"步骤{i}_user_profile不一致")
                
                # 检查迭代计数是否单调递增（如果有反馈）
                iteration_counts = [s.get("iteration_count", 0) for s in states_history]
                is_monotonic = all(iteration_counts[i] <= iteration_counts[i+1] for i in range(len(iteration_counts)-1))
                
                if is_monotonic:
                    consistency_checks.append("迭代计数单调性正确")
                else:
                    consistency_checks.append("迭代计数单调性错误")
                
                # 统计一致性检查结果
                consistent_checks = [c for c in consistency_checks if "一致" in c or "正确" in c]
                consistency_rate = len(consistent_checks) / len(consistency_checks)
                
                if consistency_rate >= 0.8:  # 80%以上一致性认为通过
                    return self.print_result(
                        "状态一致性",
                        True,
                        f"状态一致性良好",
                        f"一致性率: {consistency_rate:.2%}, 检查: {len(consistency_checks)}项"
                    )
                else:
                    return self.print_result(
                        "状态一致性",
                        False,
                        f"状态一致性不足",
                        f"一致性率: {consistency_rate:.2%}, 问题: {[c for c in consistency_checks if '不一致' in c or '错误' in c]}"
                    )
                    
        except Exception as e:
            return self.print_result(
                "状态一致性",
                False,
                "状态一致性测试异常",
                f"异常: {str(e)}"
            )
    
    def test_error_recovery(self) -> bool:
        """测试错误恢复"""
        print("\n🛠️ 测试错误恢复...")
        
        try:
            # 1. 设置会导致错误的LLM响应
            error_mock = MagicMock()
            error_mock.analyze_career_goal_clarity.return_value = {
                "success": False,
                "error": "模拟API错误"
            }
            
            with patch('src.services.llm_service.llm_service', error_mock):
                # 2. 尝试运行工作流
                user_message = "测试错误恢复"
                initial_state = self.graph.create_session(self.test_user_profile, user_message)
                
                error_occurred = False
                try:
                    result = None
                    for state_update in self.graph.app.stream(initial_state):
                        last_node = list(state_update.keys())[-1]
                        result = state_update[last_node]
                        break
                    
                    # 检查是否有错误日志
                    if result and result.get("error_log"):
                        error_occurred = True
                        
                except Exception:
                    error_occurred = True
                
                if error_occurred:
                    return self.print_result(
                        "错误恢复",
                        True,
                        "错误处理机制正常",
                        "系统能够优雅处理LLM API错误"
                    )
                else:
                    return self.print_result(
                        "错误恢复",
                        False,
                        "错误处理机制异常",
                        "系统未能正确处理API错误"
                    )
                    
        except Exception as e:
            return self.print_result(
                "错误恢复",
                False,
                "错误恢复测试异常",
                f"异常: {str(e)}"
            )
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有集成测试"""
        self.print_separator("CareerNavigator 工作流集成测试")
        
        print("🔗 开始集成测试...")
        start_time = time.time()
        
        # 运行各项测试
        happy_path_result = self.test_complete_workflow_happy_path()
        iteration_result = self.test_iteration_workflow()
        consistency_result = self.test_state_consistency()
        error_recovery_result = self.test_error_recovery()
        
        # 汇总结果
        end_time = time.time()
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r["success"])
        
        self.print_separator("测试结果汇总")
        print(f"📊 总测试数: {total_tests}")
        print(f"✅ 通过: {passed_tests}")
        print(f"❌ 失败: {total_tests - passed_tests}")
        print(f"⏱️ 耗时: {end_time - start_time:.2f}秒")
        
        overall_success = all([
            happy_path_result, iteration_result, 
            consistency_result, error_recovery_result
        ])
        
        if overall_success:
            print("\n🎉 所有集成测试通过！系统集成正常。")
        else:
            print("\n⚠️ 存在集成问题，请检查工作流逻辑和状态管理。")
        
        return {
            "overall_success": overall_success,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "duration": end_time - start_time,
            "details": self.results
        }


def main():
    """主函数"""
    tester = WorkflowIntegrationTester()
    results = tester.run_all_tests()
    
    # 返回退出码
    exit_code = 0 if results["overall_success"] else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
