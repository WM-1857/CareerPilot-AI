#!/usr/bin/env python3
"""
测试MCP API输出功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.services.llm_service import call_mcp_api

def test_mcp_api_output():
    """测试MCP API的输出功能"""
    print("🧪 开始测试MCP API输出功能")
    print("=" * 60)
    
    # 测试行业数据API
    print("\n1. 测试行业数据API")
    print("-" * 40)
    industry_result = call_mcp_api("industry_data", {
        "target_industry": "科技行业"
    })
    print(f"✅ 行业数据API调用完成")
    
    # 测试职位市场API
    print("\n2. 测试职位市场API")
    print("-" * 40)
    job_result = call_mcp_api("job_market", {
        "target_career": "产品经理"
    })
    print(f"✅ 职位市场API调用完成")
    
    # 测试用户画像API
    print("\n3. 测试用户画像API")
    print("-" * 40)
    profile_result = call_mcp_api("user_profile_analysis", {
        "user_profile": {
            "current_position": "软件工程师"
        }
    })
    print(f"✅ 用户画像API调用完成")
    
    print("\n" + "=" * 60)
    print("🎉 所有MCP API测试完成！")

if __name__ == "__main__":
    test_mcp_api_output() 