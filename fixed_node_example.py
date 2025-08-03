
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
