
import sys
import os
import json
sys.path.insert(0, os.path.dirname(__file__))

from src.services.llm_service import call_mcp_api

def verify_sources():
    print("Verifying data_sources in call_mcp_api output...")
    
    # Test industry_data
    result = call_mcp_api("industry_data", {"target_industry": "AI"})
    if "data_sources" in result:
        print(f"✅ industry_data returned data_sources: {len(result['data_sources'])} sources found.")
        print(f"Sample sources: {result['data_sources'][:2]}")
    else:
        print("❌ industry_data did NOT return data_sources.")
        print(f"Keys: {result.keys()}")

if __name__ == "__main__":
    verify_sources()
