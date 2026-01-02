#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph工作流测试模块（Windows兼容版本）
测试工作流节点、状态管理和人机交互
"""

import os
import sys
import json
import time
from typing import Dict, Any, Optional
from unittest.mock import patch

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

try:
    # 临时设置API密钥避免导入错误
    if not os.getenv('SPARK_API_KEY'):
        os.environ['SPARK_API_KEY'] = 'Bearer orFKteCwMFcKbowYftHz:OpmCHRrdIjguGUkfFwUk'
    
    if not os.getenv('DASHSCOPE_API_KEY'):
        os.environ['DASHSCOPE_API_KEY'] = os.environ['SPARK_API_KEY']
    
    from src.services.career_graph import CareerNavigatorGraph
    from src.services.career_nodes import (
        coordinator_node, planner_node, supervisor_node,
        user_profiler_node, industry_researcher_node, job_analyzer_node,
        reporter_node, goal_decomposer_node, scheduler_node
    )
    from src.models.career_state import (
        CareerNavigatorState, WorkflowStage, UserProfile, UserSatisfactionLevel,
        create_initial_state, StateUpdater, UserFeedback
    )
    IMPORT_SUCCESS = True
    MOCK_MODE = os.getenv('SPARK_API_KEY') == 'Bearer orFKteCwMFcKbowYftHz:OpmCHRrdIjguGUkfFwUk'
except ImportError as e:
    IMPORT_SUCCESS = False
    IMPORT_ERROR = str(e)
    MOCK_MODE = False


class LangGraphTester:
    """LangGraph工作流测试器"""
    
    def __init__(self):
        self.project_root = project_root
        self.results = {}
        self.errors = []
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
    
    def print_separator(self, title: str):
        """打印分隔符"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print('='*60)
    
    def print_result(self, test_name: str, success: bool, message: str, details: str = ""):
        """打印测试结果（ASCII兼容）"""
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   Details: {details}")
        self.results[test_name] = {"success": success, "message": message, "details": details}
        return success
    
    def print_status(self, message: str, success: Optional[bool] = None):
        """打印状态信息"""
        if success is True:
            print(f"[PASS] {message}")
        elif success is False:
            print(f"[FAIL] {message}")
        else:
            print(f"[INFO] {message}")
    
    def test_state_creation(self) -> bool:
        """测试状态创建"""
        print("\n[Testing] State Creation...")
        
        if not IMPORT_SUCCESS:
            return self.print_result(
                "状态创建",
                False,
                "无法测试（模块导入失败）",
                IMPORT_ERROR
            )
        
        try:
            # 测试初始状态创建
            session_id = "test_session_001"
            initial_state = create_initial_state(self.test_user_profile, session_id)
            
            # 验证必要字段
            required_fields = [
                "session_id", "user_profile", "current_stage", "messages",
                "iteration_count", "max_iterations", "agent_tasks", "agent_outputs"
            ]
            
            missing_fields = [f for f in required_fields if f not in initial_state]
            
            if not missing_fields:
                return self.print_result(
                    "状态创建",
                    True,
                    "初始状态创建成功",
                    f"包含所有必要字段: {len(required_fields)}个"
                )
            else:
                return self.print_result(
                    "状态创建",
                    False,
                    "初始状态字段不完整",
                    f"缺少字段: {missing_fields}"
                )
                
        except Exception as e:
            return self.print_result(
                "状态创建",
                False,
                "状态创建异常",
                f"异常: {str(e)}"
            )
    
    def test_coordinator_node(self) -> bool:
        """测试协调员节点"""
        print("\n[Testing] Coordinator Node...")
        
        if not IMPORT_SUCCESS:
            return self.print_result(
                "协调员节点",
                False,
                "无法测试（模块导入失败）",
                IMPORT_ERROR
            )
        
        try:
            # 创建测试状态
            initial_state = create_initial_state(self.test_user_profile, "test_session")
            
            # 创建正确的消息格式
            from langchain_core.messages import HumanMessage
            initial_state["messages"] = [HumanMessage(content="我想转向AI产品经理")]
            
            # 模拟LLM响应
            with patch('src.services.llm_service.llm_service.analyze_career_goal_clarity') as mock_llm:
                mock_llm.return_value = {
                    "success": True,
                    "content": json.dumps({
                        "is_goal_clear": False,
                        "clarity_score": 45,
                        "analysis_details": "目标需要进一步明确"
                    })
                }
                
                result = coordinator_node(initial_state)
                
                if result and "next_node" in result:
                    return self.print_result(
                        "协调员节点",
                        True,
                        "协调员节点执行成功",
                        f"路由到: {result['next_node']}"
                    )
                else:
                    return self.print_result(
                        "协调员节点",
                        False,
                        "协调员节点输出格式错误",
                        f"结果: {result}"
                    )
                    
        except Exception as e:
            return self.print_result(
                "协调员节点",
                False,
                "协调员节点执行异常",
                f"异常: {str(e)}"
            )
    
    def test_planner_node(self) -> bool:
        """测试计划员节点"""
        print("\n[Testing] Planner Node...")
        
        if not IMPORT_SUCCESS:
            return self.print_result(
                "计划员节点",
                False,
                "无法测试（模块导入失败）",
                IMPORT_ERROR
            )
        
        try:
            # 创建测试状态
            test_state = create_initial_state(self.test_user_profile, "test_session")
            test_state["current_stage"] = WorkflowStage.PLANNING
            
            # 模拟LLM响应
            with patch('src.services.llm_service.llm_service.create_analysis_strategy') as mock_llm:
                mock_llm.return_value = {
                    "success": True,
                    "content": json.dumps({
                        "strategy_overview": "制定个性化职业分析策略"
                    })
                }
                
                result = planner_node(test_state)
                
                if result and "planning_strategy" in result:
                    return self.print_result(
                        "计划员节点",
                        True,
                        "计划员节点执行成功",
                        f"策略: {result['planning_strategy'][:50]}..."
                    )
                else:
                    return self.print_result(
                        "计划员节点",
                        False,
                        "计划员节点输出格式错误",
                        f"结果: {result}"
                    )
                    
        except Exception as e:
            return self.print_result(
                "计划员节点",
                False,
                "计划员节点执行异常",
                f"异常: {str(e)}"
            )
    
    def test_supervisor_node(self) -> bool:
        """测试管理员节点"""
        print("\n[Testing] Supervisor Node...")
        
        if not IMPORT_SUCCESS:
            return self.print_result(
                "管理员节点",
                False,
                "无法测试（模块导入失败）",
                IMPORT_ERROR
            )
        
        try:
            # 创建测试状态
            test_state = create_initial_state(self.test_user_profile, "test_session")
            test_state["planning_strategy"] = "制定个性化职业分析策略"
            test_state["current_stage"] = WorkflowStage.PLANNING
            
            result = supervisor_node(test_state)
            
            if result and "agent_tasks" in result:
                tasks = result["agent_tasks"]
                if len(tasks) == 3:  # 应该创建3个任务
                    agent_names = [task["agent_name"] for task in tasks]
                    expected_agents = ["user_profiler_node", "industry_researcher_node", "job_analyzer_node"]
                    
                    if all(agent in agent_names for agent in expected_agents):
                        return self.print_result(
                            "管理员节点",
                            True,
                            "管理员节点执行成功",
                            f"创建了{len(tasks)}个任务: {agent_names}"
                        )
                    else:
                        return self.print_result(
                            "管理员节点",
                            False,
                            "管理员节点任务配置错误",
                            f"任务代理: {agent_names}, 期望: {expected_agents}"
                        )
                else:
                    return self.print_result(
                        "管理员节点",
                        False,
                        "管理员节点任务数量错误",
                        f"创建了{len(tasks)}个任务，期望3个"
                    )
            else:
                return self.print_result(
                    "管理员节点",
                    False,
                    "管理员节点输出格式错误",
                    f"结果: {result}"
                )
                
        except Exception as e:
            return self.print_result(
                "管理员节点",
                False,
                "管理员节点执行异常",
                f"异常: {str(e)}"
            )
    
    def test_parallel_analysis_nodes(self) -> bool:
        """测试并行分析节点"""
        print("\n[Testing] Parallel Analysis Nodes...")
        
        if not IMPORT_SUCCESS:
            return self.print_result(
                "并行分析节点",
                False,
                "无法测试（模块导入失败）",
                IMPORT_ERROR
            )
        
        # 创建基础测试状态和任务
        test_state = create_initial_state(self.test_user_profile, "test_session")
        test_state["current_stage"] = WorkflowStage.PARALLEL_ANALYSIS
        
        # 添加测试任务
        test_task_base = {
            "task_id": "test_task",
            "priority": 1,
            "description": "测试任务",
            "input_data": {
                "user_profile": self.test_user_profile,
                "feedback_adjustments": {},
                "iteration_count": 0
            },
            "status": "idle",
            "created_at": time.time()
        }
        
        nodes_to_test = [
            {
                "name": "用户画像节点",
                "node_func": user_profiler_node,
                "agent_name": "user_profiler_node",
                "expected_result_key": "self_insight_result"
            },
            {
                "name": "行业研究节点", 
                "node_func": industry_researcher_node,
                "agent_name": "industry_researcher_node",
                "expected_result_key": "industry_research_result"
            },
            {
                "name": "职业分析节点",
                "node_func": job_analyzer_node,
                "agent_name": "job_analyzer_node", 
                "expected_result_key": "career_analysis_result"
            }
        ]
        
        all_success = True
        
        for node_info in nodes_to_test:
            try:
                # 准备特定节点的状态
                node_state = test_state.copy()
                task = test_task_base.copy()
                task["agent_name"] = node_info["agent_name"]
                task["task_id"] = f"test_{node_info['agent_name']}"
                node_state["agent_tasks"] = [task]
                
                # 模拟LLM响应
                with patch('src.services.llm_service.llm_service') as mock_llm_service:
                    # 配置模拟响应
                    mock_response = {
                        "success": True,
                        "content": json.dumps({
                            "analysis_result": "模拟分析结果",
                            "recommendations": ["建议1", "建议2"],
                            "confidence_score": 0.8
                        })
                    }
                    
                    # 为不同节点设置不同的模拟方法
                    if "user_profiler" in node_info["agent_name"]:
                        mock_llm_service.analyze_user_profile.return_value = mock_response
                    elif "industry_researcher" in node_info["agent_name"]:
                        mock_llm_service.research_industry_trends.return_value = mock_response
                    elif "job_analyzer" in node_info["agent_name"]:
                        mock_llm_service.analyze_career_opportunities.return_value = mock_response
                    
                    # 执行节点
                    result = node_info["node_func"](node_state)
                    
                    if result and node_info["expected_result_key"] in result:
                        all_success = self.print_result(
                            node_info["name"],
                            True,
                            f"{node_info['name']}执行成功",
                            f"生成了{node_info['expected_result_key']}"
                        ) and all_success
                    else:
                        all_success = self.print_result(
                            node_info["name"],
                            False,
                            f"{node_info['name']}输出格式错误",
                            f"结果: {list(result.keys()) if result else 'None'}"
                        ) and all_success
                        
            except Exception as e:
                all_success = self.print_result(
                    node_info["name"],
                    False,
                    f"{node_info['name']}执行异常",
                    f"异常: {str(e)}"
                ) and all_success
        
        return all_success
    
    def test_state_updater(self) -> bool:
        """测试状态更新器"""
        print("\n[Testing] State Updater...")
        
        if not IMPORT_SUCCESS:
            return self.print_result(
                "状态更新器",
                False,
                "无法测试（模块导入失败）",
                IMPORT_ERROR
            )
        
        try:
            # 创建测试状态
            test_state = create_initial_state(self.test_user_profile, "test_session")
            
            # 测试阶段更新
            stage_update = StateUpdater.update_stage(test_state, WorkflowStage.PLANNING)
            if stage_update.get("current_stage") == WorkflowStage.PLANNING:
                stage_success = True
            else:
                stage_success = False
            
            # 测试迭代计数
            iteration_update = StateUpdater.increment_iteration(test_state)
            if iteration_update.get("iteration_count") == 1:
                iteration_success = True
            else:
                iteration_success = False
            
            # 测试用户反馈添加
            mock_feedback = {
                "feedback_id": "test_feedback",
                "stage": WorkflowStage.USER_FEEDBACK,
                "satisfaction_level": UserSatisfactionLevel.SATISFIED,
                "feedback_text": "测试反馈",
                "timestamp": time.time()
            }
            
            feedback_update = StateUpdater.add_user_feedback(test_state, mock_feedback)
            if (feedback_update.get("user_feedback_history") and 
                len(feedback_update["user_feedback_history"]) > 0):
                feedback_success = True
            else:
                feedback_success = False
            
            overall_success = all([stage_success, iteration_success, feedback_success])
            
            return self.print_result(
                "状态更新器",
                overall_success,
                "状态更新器测试完成",
                f"阶段更新: {stage_success}, 迭代计数: {iteration_success}, 反馈添加: {feedback_success}"
            )
            
        except Exception as e:
            return self.print_result(
                "状态更新器",
                False,
                "状态更新器测试异常",
                f"异常: {str(e)}"
            )
    
    def test_graph_compilation(self) -> bool:
        """测试图编译"""
        print("\n[Testing] Graph Compilation...")
        
        if not IMPORT_SUCCESS:
            return self.print_result(
                "图编译",
                False,
                "无法测试（模块导入失败）",
                IMPORT_ERROR
            )
        
        try:
            # 初始化图
            graph = CareerNavigatorGraph()
            
            # 检查图是否正确编译
            if graph.app is not None:
                return self.print_result(
                    "图编译",
                    True,
                    "LangGraph编译成功",
                    "工作流应用已就绪"
                )
            else:
                return self.print_result(
                    "图编译",
                    False,
                    "LangGraph编译失败",
                    "工作流应用为None"
                )
                
        except Exception as e:
            return self.print_result(
                "图编译",
                False,
                "图编译测试异常",
                f"异常: {str(e)}"
            )
    
    def test_session_creation(self) -> bool:
        """测试会话创建"""
        print("\n[Testing] Session Creation...")
        
        if not IMPORT_SUCCESS:
            return self.print_result(
                "会话创建",
                False,
                "无法测试（模块导入失败）",
                IMPORT_ERROR
            )
        
        try:
            graph = CareerNavigatorGraph()
            user_message = "我想从软件工程师转向AI产品经理"
            session_state = graph.create_session(self.test_user_profile, user_message)
            
            # 验证会话状态
            if (session_state.get("session_id") and 
                session_state.get("user_profile") and
                session_state.get("messages")):
                return self.print_result(
                    "会话创建",
                    True,
                    "会话创建成功",
                    f"会话ID: {session_state['session_id'][:8]}..."
                )
            else:
                return self.print_result(
                    "会话创建",
                    False,
                    "会话状态不完整",
                    f"状态字段: {list(session_state.keys())}"
                )
                
        except Exception as e:
            return self.print_result(
                "会话创建",
                False,
                "会话创建异常",
                f"异常: {str(e)}"
            )
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有LangGraph测试"""
        self.print_separator("CareerNavigator LangGraph工作流测试")
        
        print("Testing LangGraph Workflow...")
        start_time = time.time()
        
        # 运行各项测试
        tests = [
            ("状态创建", self.test_state_creation),
            ("协调员节点", self.test_coordinator_node),
            ("计划员节点", self.test_planner_node),
            ("管理员节点", self.test_supervisor_node),
            ("并行分析节点", self.test_parallel_analysis_nodes),
            ("状态更新器", self.test_state_updater),
            ("图编译", self.test_graph_compilation),
            ("会话创建", self.test_session_creation)
        ]
        
        results = {}
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"\nExecuting test: {test_name}")
            try:
                result = test_func()
                results[test_name] = result
                if result:
                    passed_tests += 1
            except Exception as e:
                print(f"Test {test_name} exception: {str(e)}")
                results[test_name] = False
                self.errors.append(f"Test {test_name} exception: {str(e)}")
        
        end_time = time.time()
        
        # 汇总结果
        self.print_separator("测试结果汇总")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Duration: {end_time - start_time:.2f}s")
        
        overall_success = passed_tests == total_tests
        
        if overall_success:
            print("\nAll LangGraph tests passed! Workflow is ready.")
        else:
            print("\nSome LangGraph tests failed. Please check the issues above.")
            if self.errors:
                print("\nDetailed errors:")
                for error in self.errors:
                    print(f"  - {error}")
        
        return {
            'success': overall_success,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'duration': end_time - start_time,
            'results': results,
            'errors': self.errors
        }


def main():
    """主函数"""
    tester = LangGraphTester()
    results = tester.run_all_tests()
    
    # 返回适当的退出码
    exit_code = 0 if results['success'] else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
