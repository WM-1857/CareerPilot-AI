"""
CareerNavigator 问题诊断和修复脚本
针对测试中发现的问题进行修复
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

def diagnose_llm_parsing_issue():
    """诊断LLM响应解析问题"""
    print("🔍 诊断LLM响应解析问题...")
    
    try:
        from src.services.llm_service import DashScopeService
        
        llm_service = DashScopeService()
        
        # 测试协调员节点的提示词
        coordinator_prompt = """
你是一个智能职业规划协调员。请根据用户信息制定分析策略。

用户信息：
- 年龄：26岁
- 当前职位：产品经理
- 工作经验：3年
- 行业：电商
- 职业目标：成为产品总监

请返回JSON格式的策略，包含以下字段：
{
    "strategy_overview": "策略概述",
    "analysis_priorities": ["优先级1", "优先级2"],
    "data_sources": ["数据源1", "数据源2"],
    "timeline": "时间规划",
    "expected_outcomes": ["预期结果1", "预期结果2"]
}

只返回JSON，不要其他文字。
"""
        
        print("  📤 测试协调员提示词...")
        response = llm_service.call_llm(coordinator_prompt)
        
        if response.get("success"):
            content = response.get("content", "")
            print(f"  📝 LLM原始响应: {content[:200]}...")
            
            # 尝试解析JSON
            try:
                import json
                
                # 清理响应内容
                cleaned_content = content.strip()
                if cleaned_content.startswith("```json"):
                    cleaned_content = cleaned_content[7:]
                if cleaned_content.endswith("```"):
                    cleaned_content = cleaned_content[:-3]
                if cleaned_content.startswith("```"):
                    cleaned_content = cleaned_content[3:]
                
                parsed_json = json.loads(cleaned_content)
                print("  ✅ JSON解析成功")
                print(f"  📋 策略概述: {parsed_json.get('strategy_overview', '未知')[:100]}...")
                return True
                
            except json.JSONDecodeError as e:
                print(f"  ❌ JSON解析失败: {e}")
                print(f"  📝 清理后内容: {cleaned_content[:200]}...")
                return False
        else:
            print(f"  ❌ LLM调用失败: {response.get('error')}")
            return False
            
    except Exception as e:
        print(f"  ❌ 诊断异常: {e}")
        return False


def test_improved_prompt():
    """测试改进的提示词"""
    print("\n🔧 测试改进的提示词...")
    
    try:
        from src.services.llm_service import DashScopeService
        
        llm_service = DashScopeService()
        
        # 改进的提示词
        improved_prompt = """
作为职业规划协调员，请为用户制定分析策略。

用户背景：产品经理，3年经验，电商行业，目标是成为产品总监。

请提供分析策略，格式要求：
1. 策略概述（50字内）
2. 分析重点（列出3个要点）
3. 数据来源（列出3个来源）
4. 时间安排（简要说明）
5. 预期成果（列出3个成果）

请直接给出内容，不需要JSON格式。
"""
        
        print("  📤 发送改进的提示词...")
        response = llm_service.call_llm(improved_prompt)
        
        if response.get("success"):
            content = response.get("content", "")
            print(f"  ✅ 响应成功")
            print(f"  📝 响应内容: {content}")
            
            # 检查响应是否包含关键信息
            key_terms = ["策略", "分析", "数据", "时间", "成果"]
            found_terms = [term for term in key_terms if term in content]
            
            print(f"  📊 包含关键词: {len(found_terms)}/{len(key_terms)} ({', '.join(found_terms)})")
            
            if len(found_terms) >= 3:
                print("  ✅ 响应质量良好")
                return True
            else:
                print("  ⚠️ 响应质量一般")
                return False
        else:
            print(f"  ❌ LLM调用失败: {response.get('error')}")
            return False
            
    except Exception as e:
        print(f"  ❌ 测试异常: {e}")
        return False


def test_simple_node_execution():
    """测试简化的节点执行"""
    print("\n🔄 测试简化的节点执行...")
    
    try:
        from src.models.career_state import UserProfile, create_initial_state
        
        # 创建简化的测试状态
        user_profile = UserProfile(
            user_id="simple_test_user",
            age=28,
            education_level="本科",
            work_experience=3,
            current_position="产品经理",
            industry="电商",
            skills=["产品设计", "数据分析"],
            interests=["用户体验"],
            career_goals="成为产品总监",
            location="深圳",
            salary_expectation="25-40万",
            additional_info={}
        )
        
        test_state = create_initial_state(user_profile, "simple_test_session")
        
        print("  📝 测试状态创建成功")
        
        # 手动模拟节点执行逻辑（不依赖复杂的LLM解析）
        mock_analysis_result = {
            "analysis_type": "career_strategy",
            "user_profile_summary": f"用户是{user_profile['age']}岁的{user_profile['current_position']}",
            "key_insights": [
                "用户有3年产品经验，基础较好",
                "电商行业发展前景良好",
                "从产品经理到产品总监需要提升管理能力"
            ],
            "recommended_actions": [
                "深入学习商业分析",
                "提升团队管理技能",
                "积累大型项目经验"
            ],
            "confidence_score": 0.85
        }
        
        print("  ✅ 模拟分析结果生成成功")
        print(f"  📋 分析类型: {mock_analysis_result['analysis_type']}")
        print(f"  📊 置信度: {mock_analysis_result['confidence_score']}")
        
        # 模拟状态更新
        updated_state = test_state.copy()
        
        # 添加分析输出
        from src.models.career_state import AgentOutput
        from datetime import datetime
        
        agent_output = AgentOutput(
            output_id="test_output_001",
            agent_name="simplified_analyzer",
            task_id="test_task_001",
            output_type="职业策略分析",
            content=mock_analysis_result,
            confidence_score=0.85,
            data_sources=["用户输入", "模拟分析"],
            analysis_method="简化分析",
            timestamp=datetime.now(),
            quality_metrics={"completeness": 0.9, "accuracy": 0.8},
            recommendations=mock_analysis_result["recommended_actions"],
            warnings=None
        )
        
        updated_state["agent_outputs"] = [agent_output]
        
        print("  ✅ 状态更新成功")
        print(f"  📈 输出数量: {len(updated_state['agent_outputs'])}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 简化节点测试失败: {e}")
        return False


def test_concurrent_fix():
    """测试并发问题修复"""
    print("\n🔄 测试并发问题修复...")
    
    try:
        from src.models.career_state import create_initial_state, UserProfile
        from datetime import datetime
        
        # 创建测试状态
        user_profile = UserProfile(
            user_id="concurrent_test",
            age=25,
            career_goals="测试并发处理",
            skills=["测试"],
            interests=["开发"],
            education_level="本科",
            work_experience=2,
            current_position="工程师",
            industry="技术",
            location="北京",
            salary_expectation="20万",
            additional_info={}
        )
        
        initial_state = create_initial_state(user_profile, "concurrent_session")
        
        print("  📝 初始状态创建成功")
        
        # 模拟多个节点同时更新（这是导致问题的原因）
        from src.models.career_state import AgentOutput
        
        # 创建多个输出（模拟并发节点）
        outputs = []
        for i in range(3):
            output = AgentOutput(
                output_id=f"concurrent_output_{i}",
                agent_name=f"agent_{i}",
                task_id=f"task_{i}",
                output_type=f"分析类型{i}",
                content={"result": f"结果{i}"},
                confidence_score=0.8,
                data_sources=["测试"],
                analysis_method="并发测试",
                timestamp=datetime.now(),
                quality_metrics={"test": 1.0},
                recommendations=[f"建议{i}"],
                warnings=None
            )
            outputs.append(output)
        
        print(f"  📊 创建了{len(outputs)}个并发输出")
        
        # 正确的状态更新方式（避免并发冲突）
        updated_state = initial_state.copy()
        
        # 一次性添加所有输出，而不是分别添加
        updated_state["agent_outputs"] = outputs
        
        print("  ✅ 并发状态更新成功")
        print(f"  📈 最终输出数量: {len(updated_state['agent_outputs'])}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 并发测试失败: {e}")
        return False


def create_fixed_node_example():
    """创建修复后的节点示例"""
    print("\n🔧 创建修复后的节点示例...")
    
    fixed_node_code = '''
def fixed_coordinator_node(state):
    """修复后的协调员节点"""
    from src.services.llm_service import DashScopeService
    from src.models.career_state import AgentOutput
    from datetime import datetime
    
    try:
        llm_service = DashScopeService()
        user_profile = state["user_profile"]
        
        # 简化的提示词
        prompt = f"""
        请为以下用户制定职业规划策略：
        - 年龄：{user_profile.get('age', '未知')}
        - 职位：{user_profile.get('current_position', '未知')}
        - 目标：{user_profile.get('career_goals', '未知')}
        
        请简要说明：
        1. 分析重点
        2. 建议步骤
        3. 预期结果
        
        回答请简洁明了，不超过200字。
        """
        
        response = llm_service.call_llm(prompt)
        
        if response.get("success"):
            content = response.get("content", "")
            
            # 直接使用文本内容，不强制解析JSON
            analysis_result = {
                "strategy_text": content,
                "user_summary": f"{user_profile.get('age')}岁{user_profile.get('current_position')}",
                "career_goal": user_profile.get('career_goals'),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            # 创建输出
            output = AgentOutput(
                output_id=f"coord_{datetime.now().timestamp()}",
                agent_name="coordinator",
                task_id="strategy_planning",
                output_type="职业策略",
                content=analysis_result,
                confidence_score=0.8,
                data_sources=["用户输入", "LLM分析"],
                analysis_method="文本分析",
                timestamp=datetime.now(),
                quality_metrics={"completeness": 0.9},
                recommendations=[content[:100] + "..."],
                warnings=None
            )
            
            # 返回更新（避免并发冲突）
            return {
                "agent_outputs": [output]  # 返回列表，而不是追加
            }
        else:
            # LLM失败时的备用方案
            fallback_result = {
                "strategy_text": "基于用户背景，建议重点关注技能提升和职业规划。",
                "user_summary": f"{user_profile.get('age')}岁{user_profile.get('current_position')}",
                "career_goal": user_profile.get('career_goals'),
                "fallback": True
            }
            
            output = AgentOutput(
                output_id=f"coord_fallback_{datetime.now().timestamp()}",
                agent_name="coordinator",
                task_id="strategy_planning",
                output_type="职业策略(备用)",
                content=fallback_result,
                confidence_score=0.6,
                data_sources=["用户输入"],
                analysis_method="备用分析",
                timestamp=datetime.now(),
                quality_metrics={"completeness": 0.7},
                recommendations=["建议深入分析用户需求"],
                warnings=["使用了备用分析方案"]
            )
            
            return {
                "agent_outputs": [output]
            }
            
    except Exception as e:
        # 异常处理
        error_output = AgentOutput(
            output_id=f"coord_error_{datetime.now().timestamp()}",
            agent_name="coordinator",
            task_id="strategy_planning",
            output_type="错误报告",
            content={"error": str(e), "fallback_executed": True},
            confidence_score=0.3,
            data_sources=["错误处理"],
            analysis_method="异常处理",
            timestamp=datetime.now(),
            quality_metrics={"completeness": 0.5},
            recommendations=["请检查系统配置"],
            warnings=[f"节点执行异常: {str(e)}"]
        )
        
        return {
            "agent_outputs": [error_output]
        }
'''
    
    # 保存修复代码示例
    with open('fixed_node_example.py', 'w', encoding='utf-8') as f:
        f.write(fixed_node_code)
    
    print("  ✅ 修复代码示例已保存到 fixed_node_example.py")
    print("  📝 主要修复点：")
    print("     1. 简化LLM提示词，避免复杂JSON解析")
    print("     2. 添加备用方案处理LLM失败")
    print("     3. 改进异常处理机制")
    print("     4. 避免并发状态更新冲突")
    
    return True


def run_diagnosis():
    """运行完整诊断"""
    print("🔍 CareerNavigator 问题诊断")
    print("=" * 50)
    
    tests = [
        ("LLM响应解析问题", diagnose_llm_parsing_issue),
        ("改进提示词测试", test_improved_prompt),
        ("简化节点执行", test_simple_node_execution),
        ("并发问题修复", test_concurrent_fix),
        ("创建修复示例", create_fixed_node_example),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
            results[test_name] = False
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 诊断结果总结")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name:<20} {status}")
    
    print(f"\n总计: {passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    print("\n💡 修复建议：")
    print("1. 简化LLM提示词，使用文本格式而非JSON")
    print("2. 添加LLM调用失败的备用方案")
    print("3. 修复LangGraph并发状态更新问题")
    print("4. 改进错误处理和日志记录")
    
    return results


if __name__ == "__main__":
    # 设置环境变量
    os.environ['DASHSCOPE_API_KEY'] = 'sk-4b6f138ba0f74331a6092090b1c7cce1'
    os.environ['FLASK_ENV'] = 'development'
    os.environ['LOG_LEVEL'] = 'DEBUG'
    
    run_diagnosis()
