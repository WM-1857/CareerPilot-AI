#!/usr/bin/env python3
"""
LLM服务测试模块
测试阿里云百炼API连接、响应质量和错误处理
"""

import os
import sys
import json
import time
from typing import Dict, List, Any, Optional

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
    from src.services.llm_service import llm_service, call_mcp_api
    from src.models.career_state import UserProfile
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请先运行环境测试确保所有依赖正常")
    sys.exit(1)


class LLMServiceTester:
    """LLM服务测试器"""
    
    def __init__(self):
        self.results = {}
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
        """打印测试结果"""
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   📝 {details}")
        self.results[test_name] = {"success": success, "message": message, "details": details}
        return success
    
    def test_api_connection(self) -> bool:
        """测试API连接"""
        print("\n🔌 测试API连接...")
        
        try:
            # 简单的API连接测试
            test_request = "Hello, this is a connection test."
            
            response = llm_service.analyze_career_goal_clarity(test_request, self.test_user_profile)
            
            if response and response.get("success"):
                return self.print_result(
                    "API连接",
                    True,
                    "API连接正常",
                    f"响应时间: {response.get('response_time', 'unknown')}秒"
                )
            else:
                error_msg = response.get("error", "未知错误") if response else "无响应"
                return self.print_result(
                    "API连接",
                    False,
                    "API连接失败",
                    f"错误: {error_msg}"
                )
                
        except Exception as e:
            return self.print_result(
                "API连接",
                False,
                "API连接异常",
                f"异常: {str(e)}"
            )
    
    def test_career_goal_analysis(self) -> bool:
        """测试职业目标分析"""
        print("\n🎯 测试职业目标分析...")
        
        test_cases = [
            {
                "name": "明确目标",
                "request": "我想成为一名AI产品经理，专注于大模型产品设计和用户体验优化",
                "expected_clarity": True
            },
            {
                "name": "模糊目标", 
                "request": "我想换个工作，找个更好的发展机会",
                "expected_clarity": False
            },
            {
                "name": "技术转型",
                "request": "我是软件工程师，想转向产品管理方向",
                "expected_clarity": False
            }
        ]
        
        all_success = True
        
        for case in test_cases:
            try:
                response = llm_service.analyze_career_goal_clarity(
                    case["request"], 
                    self.test_user_profile
                )
                
                if response and response.get("success"):
                    # 尝试解析JSON响应
                    try:
                        content = json.loads(response["content"])
                        is_clear = content.get("is_goal_clear", False)
                        clarity_score = content.get("clarity_score", 0)
                        
                        # 验证响应格式
                        if "is_goal_clear" in content and "clarity_score" in content:
                            all_success = self.print_result(
                                f"目标分析_{case['name']}",
                                True,
                                f"分析成功 - 明确度: {is_clear}, 分数: {clarity_score}",
                                f"请求: {case['request'][:50]}..."
                            ) and all_success
                        else:
                            all_success = self.print_result(
                                f"目标分析_{case['name']}",
                                False,
                                "响应格式不正确",
                                f"缺少必要字段: {list(content.keys())}"
                            ) and all_success
                            
                    except json.JSONDecodeError:
                        all_success = self.print_result(
                            f"目标分析_{case['name']}",
                            False,
                            "响应JSON解析失败",
                            f"原始响应: {response['content'][:100]}..."
                        ) and all_success
                else:
                    error_msg = response.get("error", "未知错误") if response else "无响应"
                    all_success = self.print_result(
                        f"目标分析_{case['name']}",
                        False,
                        "分析失败",
                        f"错误: {error_msg}"
                    ) and all_success
                    
            except Exception as e:
                all_success = self.print_result(
                    f"目标分析_{case['name']}",
                    False,
                    "分析异常",
                    f"异常: {str(e)}"
                ) and all_success
        
        return all_success
    
    def test_analysis_strategy_creation(self) -> bool:
        """测试分析策略制定"""
        print("\n📋 测试分析策略制定...")
        
        try:
            feedback_history = []  # 空反馈历史
            
            response = llm_service.create_analysis_strategy(
                self.test_user_profile,
                feedback_history
            )
            
            if response and response.get("success"):
                try:
                    content = json.loads(response["content"])
                    
                    if "strategy_overview" in content:
                        return self.print_result(
                            "策略制定",
                            True,
                            "策略制定成功",
                            f"策略概述: {content['strategy_overview'][:100]}..."
                        )
                    else:
                        return self.print_result(
                            "策略制定",
                            False,
                            "策略格式不正确",
                            f"响应字段: {list(content.keys())}"
                        )
                        
                except json.JSONDecodeError:
                    return self.print_result(
                        "策略制定",
                        False,
                        "策略JSON解析失败",
                        f"原始响应: {response['content'][:100]}..."
                    )
            else:
                error_msg = response.get("error", "未知错误") if response else "无响应"
                return self.print_result(
                    "策略制定",
                    False,
                    "策略制定失败",
                    f"错误: {error_msg}"
                )
                
        except Exception as e:
            return self.print_result(
                "策略制定",
                False,
                "策略制定异常",
                f"异常: {str(e)}"
            )
    
    def test_user_profile_analysis(self) -> bool:
        """测试用户画像分析"""
        print("\n👤 测试用户画像分析...")
        
        try:
            analysis_request = {
                "user_profile": self.test_user_profile,
                "focus_areas": ["技术背景", "转型意愿"],
                "is_iteration": False
            }
            
            response = llm_service.analyze_user_profile(analysis_request)
            
            if response and response.get("success"):
                try:
                    content = json.loads(response["content"])
                    
                    # 检查关键字段
                    expected_fields = ["strengths", "improvement_areas", "recommendations"]
                    missing_fields = [f for f in expected_fields if f not in content]
                    
                    if not missing_fields:
                        return self.print_result(
                            "用户画像分析",
                            True,
                            "用户画像分析成功",
                            f"包含字段: {list(content.keys())}"
                        )
                    else:
                        return self.print_result(
                            "用户画像分析",
                            False,
                            "用户画像字段不完整",
                            f"缺少字段: {missing_fields}"
                        )
                        
                except json.JSONDecodeError:
                    return self.print_result(
                        "用户画像分析",
                        False,
                        "用户画像JSON解析失败",
                        f"原始响应: {response['content'][:100]}..."
                    )
            else:
                error_msg = response.get("error", "未知错误") if response else "无响应"
                return self.print_result(
                    "用户画像分析",
                    False,
                    "用户画像分析失败",
                    f"错误: {error_msg}"
                )
                
        except Exception as e:
            return self.print_result(
                "用户画像分析",
                False,
                "用户画像分析异常",
                f"异常: {str(e)}"
            )
    
    def test_mcp_api_simulation(self) -> bool:
        """测试MCP API模拟"""
        print("\n🔗 测试MCP API模拟...")
        
        test_cases = [
            {
                "name": "行业数据",
                "api_name": "industry_data",
                "input_data": {"target_industry": "互联网"}
            },
            {
                "name": "职位市场",
                "api_name": "job_market", 
                "input_data": {"target_career": "产品经理"}
            }
        ]
        
        all_success = True
        
        for case in test_cases:
            try:
                response = call_mcp_api(case["api_name"], case["input_data"])
                
                if response and isinstance(response, dict):
                    all_success = self.print_result(
                        f"MCP_{case['name']}",
                        True,
                        f"MCP {case['name']}模拟成功",
                        f"响应字段: {list(response.keys())}"
                    ) and all_success
                else:
                    all_success = self.print_result(
                        f"MCP_{case['name']}",
                        False,
                        f"MCP {case['name']}响应格式错误",
                        f"响应类型: {type(response)}"
                    ) and all_success
                    
            except Exception as e:
                all_success = self.print_result(
                    f"MCP_{case['name']}",
                    False,
                    f"MCP {case['name']}调用异常",
                    f"异常: {str(e)}"
                ) and all_success
        
        return all_success
    
    def test_error_handling(self) -> bool:
        """测试错误处理"""
        print("\n⚠️ 测试错误处理...")
        
        try:
            # 测试无效输入
            invalid_profile = {"invalid": "data"}
            
            response = llm_service.analyze_career_goal_clarity("test", invalid_profile)
            
            # 错误处理应该返回失败但不抛出异常
            if response and "error" in response and not response.get("success"):
                return self.print_result(
                    "错误处理",
                    True,
                    "错误处理正常",
                    f"错误信息: {response['error']}"
                )
            else:
                return self.print_result(
                    "错误处理",
                    False,
                    "错误处理异常",
                    f"应该返回错误但得到: {response}"
                )
                
        except Exception as e:
            # 如果抛出异常，说明错误处理不够健壮
            return self.print_result(
                "错误处理",
                False,
                "错误处理不健壮",
                f"抛出异常: {str(e)}"
            )
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有LLM测试"""
        self.print_separator("CareerNavigator LLM服务测试")
        
        print("🤖 开始LLM服务测试...")
        start_time = time.time()
        
        # 运行各项测试
        connection_result = self.test_api_connection()
        goal_analysis_result = self.test_career_goal_analysis()
        strategy_result = self.test_analysis_strategy_creation()
        profile_result = self.test_user_profile_analysis()
        mcp_result = self.test_mcp_api_simulation()
        error_result = self.test_error_handling()
        
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
            connection_result, goal_analysis_result, strategy_result,
            profile_result, mcp_result, error_result
        ])
        
        if overall_success:
            print("\n🎉 所有LLM测试通过！服务运行正常。")
        else:
            print("\n⚠️ 存在LLM服务问题，请检查API配置和网络连接。")
        
        return {
            "overall_success": overall_success,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "duration": end_time - start_time,
            "details": self.results
        }


def main():
    """主函数"""
    tester = LLMServiceTester()
    results = tester.run_all_tests()
    
    # 返回退出码
    exit_code = 0 if results["overall_success"] else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
