"""
测试Tavily搜索工具集成
"""

import sys
import os

# 设置环境变量
os.environ["DASHSCOPE_API_KEY"] = "sk-1234567890abcdef"  # 使用测试用的API key

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.llm_service import call_mcp_api

def test_tavily_integration():
    """测试Tavily搜索工具集成"""
    print("=== 测试Tavily搜索工具集成 ===")
    
    # 测试1: 用户画像分析
    print("\n1. 测试用户画像分析...")
    user_profile = {
        "current_position": "Java开发工程师",
        "skills": ["Java", "Spring", "MySQL"],
        "career_goals": "转行做产品经理"
    }
    
    result1 = call_mcp_api("user_profile_analysis", {
        "user_profile": user_profile
    })
    print(f"用户画像分析结果: {result1}")
    
    # 测试2: 行业数据
    print("\n2. 测试行业数据...")
    result2 = call_mcp_api("industry_data", {
        "target_industry": "AI行业"
    })
    print(f"行业数据结果: {result2}")
    
    # 测试3: 职位市场
    print("\n3. 测试职位市场...")
    result3 = call_mcp_api("job_market", {
        "target_career": "产品经理"
    })
    print(f"职位市场结果: {result3}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_tavily_integration() 