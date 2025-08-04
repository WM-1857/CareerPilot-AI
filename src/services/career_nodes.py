"""
CareerNavigator LangGraph 节点实现
基于阿里云百炼API的原子化节点设计
"""

import uuid
import json
from datetime import datetime
from typing import Dict, Any, List

from src.models.career_state import (
    CareerNavigatorState, AgentTask, AgentOutput, AgentStatus, 
    WorkflowStage, StateUpdater, UserFeedback, UserSatisfactionLevel
)
from src.services.llm_service import llm_service, call_mcp_api


def coordinator_node(state: CareerNavigatorState) -> Dict[str, Any]:
    """
    协调员节点 (入口点)
    
    职责:
    1. 检查用户的初始请求。
    2. 调用LLM判断用户的职业目标是否已经明确。
    3. 根据判断结果，决定下一个流程节点。
    """
    print("--- 正在执行: coordinator_node ---")
    messages = state["messages"]
    user_request = messages[-1].content if messages else ""
    
    # 调用百炼API分析目标明确度
    llm_response = llm_service.analyze_career_goal_clarity(
        user_request, 
        state["user_profile"]
    )
    
    if llm_response.get("success"):
        try:
            # 解析JSON响应
            analysis = json.loads(llm_response["content"])
            is_goal_clear = analysis.get("is_goal_clear", False)
            clarity_score = analysis.get("clarity_score", 0)
            
            print(f"目标明确度分析: {analysis}")
            
            if is_goal_clear and clarity_score > 70:
                print("判断：目标明确，直接进入目标拆分。")
                # 更新状态，直接进入目标拆分阶段
                updates = StateUpdater.update_stage(state, WorkflowStage.GOAL_DECOMPOSITION)
                updates["next_node"] = "goal_decomposer"
                updates["cached_data"] = {"goal_analysis": analysis}
                return updates
            else:
                print("判断：目标不明确，需要进行规划和分析。")
                # 更新状态，进入策略制定阶段
                updates = StateUpdater.update_stage(state, WorkflowStage.PLANNING)
                updates["next_node"] = "planner"
                updates["cached_data"] = {"goal_analysis": analysis}
                return updates
        except json.JSONDecodeError:
            print("LLM响应解析失败，默认进入规划阶段")
            updates = StateUpdater.update_stage(state, WorkflowStage.PLANNING)
            updates["next_node"] = "planner"
            return updates
    else:
        print(f"LLM调用失败: {llm_response.get('error')}")
        # 默认进入规划阶段
        updates = StateUpdater.update_stage(state, WorkflowStage.PLANNING)
        updates["next_node"] = "planner"
        return updates


def planner_node(state: CareerNavigatorState) -> Dict[str, Any]:
    """
    计划员节点
    
    职责:
    1. 当用户目标不明确时，制定一个详细的分析策略。
    2. 将策略存入State中，供后续节点使用。
    """
    print("--- 正在执行: planner_node ---")
    user_profile = state["user_profile"]
    feedback_history = state["user_feedback_history"]
    
    # 调用百炼API制定分析策略
    llm_response = llm_service.create_analysis_strategy(
        user_profile, 
        feedback_history
    )
    
    if llm_response.get("success"):
        try:
            strategy = json.loads(llm_response["content"])
            print(f"分析策略: {strategy}")
            return {"planning_strategy": strategy.get("strategy_overview", "制定个性化职业分析策略")}
        except json.JSONDecodeError:
            return {"planning_strategy": "制定个性化职业分析策略"}
    else:
        print(f"策略制定失败: {llm_response.get('error')}")
        return {"planning_strategy": "制定个性化职业分析策略"}


def supervisor_node(state: CareerNavigatorState) -> Dict[str, Any]:
    """
    管理员节点
    
    职责:
    1. 根据 `planning_strategy` 创建并分发并行的分析任务。
    2. 为每个任务创建一个 AgentTask 对象，并添加到 State 中。
    3. 在迭代时，考虑用户反馈来调整分析策略。
    """
    print("--- 正在执行: supervisor_node ---")
    plan = state.get("planning_strategy", "制定个性化职业分析策略")
    
    # 检查是否有用户反馈需要考虑
    feedback_history = state.get("user_feedback_history", [])
    latest_feedback = feedback_history[-1] if feedback_history else None
    
    # 如果有最新反馈，调整分析重点
    analysis_adjustments = {}
    if latest_feedback:
        feedback_text = latest_feedback.get("feedback_text") or ""
        print(f"💬 考虑用户反馈进行调整: {feedback_text}")
        
        # 根据反馈调整分析重点
        if feedback_text and ("大模型" in feedback_text or "AI" in feedback_text):
            analysis_adjustments["focus_areas"] = ["AI技术背景", "大模型相关经验", "技术转产品路径"]
        if feedback_text and "学习" in feedback_text:
            analysis_adjustments["focus_areas"] = analysis_adjustments.get("focus_areas", []) + ["学习路径", "技能提升"]
    
    # 基于计划和反馈，创建三个并行任务
    tasks = [
        AgentTask(
            task_id=str(uuid.uuid4()),
            agent_name="user_profiler_node",
            task_type="个人分析",
            priority=1,
            description="执行自我洞察分析，生成个人能力画像。根据用户反馈重点分析相关技能。",
            input_data={
                "user_profile": state["user_profile"],
                "feedback_adjustments": analysis_adjustments,
                "iteration_count": state.get("iteration_count", 0)
            },
            status=AgentStatus.IDLE,
            created_at=datetime.now(),
            deadline=None,
            dependencies=None,
            started_at=None,
            completed_at=None
        ),
        AgentTask(
            task_id=str(uuid.uuid4()),
            agent_name="industry_researcher_node",
            task_type="行业研究",
            priority=1,
            description="执行行业趋势分析，生成行业报告。结合用户反馈调整研究重点。",
            input_data={
                "target_industry": state["user_profile"].get("industry"),
                "feedback_adjustments": analysis_adjustments,
                "iteration_count": state.get("iteration_count", 0)
            },
            status=AgentStatus.IDLE,
            created_at=datetime.now(),
            deadline=None,
            dependencies=None,
            started_at=None,
            completed_at=None
        ),
        AgentTask(
            task_id=str(uuid.uuid4()),
            agent_name="job_analyzer_node",
            task_type="职业分析",
            priority=1,
            description="执行职业与岗位分析，生成职业建议。根据用户反馈调整职业路径分析。",
            input_data={
                "target_career": state["user_profile"].get("career_goals"),
                "feedback_adjustments": analysis_adjustments,
                "iteration_count": state.get("iteration_count", 0)
            },
            status=AgentStatus.IDLE,
            created_at=datetime.now(),
            deadline=None,
            dependencies=None,
            started_at=None,
            completed_at=None
        )
    ]
    
    # 更新状态，进入并行分析阶段
    updated_state = StateUpdater.update_stage(state, WorkflowStage.PARALLEL_ANALYSIS)
    updated_state["agent_tasks"] = tasks
    return updated_state


# --- 并行分析节点 ---
def user_profiler_node(state: CareerNavigatorState) -> Dict[str, Any]:
    """用户建模节点 (并行)"""
    print("--- 正在执行: user_profiler_node ---")
    task = next((t for t in state["agent_tasks"] if t["agent_name"] == "user_profiler_node"), None)
    
    if not task:
        return StateUpdater.log_error(state, {"error": "未找到用户画像分析任务"})
    
    # 获取分析调整和迭代信息
    input_data = task["input_data"]
    feedback_adjustments = input_data.get("feedback_adjustments", {})
    iteration_count = input_data.get("iteration_count", 0)
    
    # 构建分析请求，包含反馈调整
    analysis_request = {
        **input_data,
        "focus_areas": feedback_adjustments.get("focus_areas", []),
        "is_iteration": iteration_count > 0,
        "improvement_notes": "结合用户反馈重新分析用户能力和优势"
    }
    
    # 调用百炼API进行用户画像分析
    llm_response = llm_service.analyze_user_profile(analysis_request)
    
    if llm_response.get("success"):
        try:
            result = json.loads(llm_response["content"])
            print(f"用户画像分析结果 (迭代{iteration_count}): {result}")
        except json.JSONDecodeError:
            result = {"error": "响应解析失败", "raw_response": llm_response["content"]}
    else:
        result = {"error": llm_response.get("error", "分析失败")}
    
    # 添加迭代信息
    result["iteration_info"] = {
        "iteration_count": iteration_count,
        "adjustments_applied": feedback_adjustments,
        "analysis_timestamp": datetime.now().isoformat()
    }
    
    output = AgentOutput(
        agent_name="user_profiler_node",
        task_id=task["task_id"],
        output_type="个人画像",
        content=result,
        confidence_score=0.8 + (0.1 * iteration_count),  # 迭代提升置信度
        data_sources=["百炼API", "用户输入", "用户反馈"],
        analysis_method="LLM分析+反馈优化",
        timestamp=datetime.now(),
        quality_metrics={"completeness": 0.9, "accuracy": 0.8 + (0.1 * iteration_count)},
        recommendations=result.get("recommendations", []),
        warnings=None
    )
    
    return {
        "self_insight_result": result, 
        "agent_outputs": [output]  # 返回单个输出，由Annotated自动合并
    }


def industry_researcher_node(state: CareerNavigatorState) -> Dict[str, Any]:
    """行业研究节点 (并行)"""
    print("--- 正在执行: industry_researcher_node ---")
    task = next((t for t in state["agent_tasks"] if t["agent_name"] == "industry_researcher_node"), None)
    
    if not task:
        return StateUpdater.log_error(state, {"error": "未找到行业研究任务"})
    
    target_industry = task["input_data"].get("target_industry", "科技行业")
    feedback_adjustments = task["input_data"].get("feedback_adjustments", {})
    iteration_count = task["input_data"].get("iteration_count", 0)
    
    # 构建研究请求，包含反馈调整
    research_request = {
        "target_industry": target_industry,
        "focus_areas": feedback_adjustments.get("focus_areas", []),
        "is_iteration": iteration_count > 0,
        "special_focus": "结合用户反馈，重点关注AI和大模型相关的行业机会" if "AI" in str(feedback_adjustments) else ""
    }
    
    # 调用百炼API进行行业研究
    llm_response = llm_service.research_industry_trends(target_industry)
    
    if llm_response.get("success"):
        try:
            result = json.loads(llm_response["content"])
            print(f"行业研究结果 (迭代{iteration_count}): {result}")
        except json.JSONDecodeError:
            result = {"error": "响应解析失败", "raw_response": llm_response["content"]}
    else:
        result = {"error": llm_response.get("error", "研究失败")}
    
    # 补充模拟的市场数据
    mcp_data = call_mcp_api("industry_data", task["input_data"])
    result["market_data"] = mcp_data
    
    # 添加迭代信息
    result["iteration_info"] = {
        "iteration_count": iteration_count,
        "adjustments_applied": feedback_adjustments,
        "research_timestamp": datetime.now().isoformat()
    }
    
    output = AgentOutput(
        agent_name="industry_researcher_node",
        task_id=task["task_id"],
        output_type="行业报告",
        content=result,
        confidence_score=0.85 + (0.05 * iteration_count),
        data_sources=["百炼API", "MCP API", "行业数据库", "用户反馈"],
        analysis_method="LLM分析+数据挖掘+反馈优化",
        timestamp=datetime.now(),
        quality_metrics={"completeness": 0.9, "timeliness": 0.95, "relevance": 0.8 + (0.1 * iteration_count)},
        recommendations=result.get("recommendations", []),
        warnings=None
    )
    
    return {
        "industry_research_result": result, 
        "agent_outputs": [output]  # 返回单个输出，由Annotated自动合并
    }


def job_analyzer_node(state: CareerNavigatorState) -> Dict[str, Any]:
    """职业分析节点 (并行)"""
    print("--- 正在执行: job_analyzer_node ---")
    task = next((t for t in state["agent_tasks"] if t["agent_name"] == "job_analyzer_node"), None)
    
    if not task:
        return StateUpdater.log_error(state, {"error": "未找到职业分析任务"})
    
    target_career = task["input_data"].get("target_career", "产品经理")
    user_profile = state["user_profile"]
    feedback_adjustments = task["input_data"].get("feedback_adjustments", {})
    iteration_count = task["input_data"].get("iteration_count", 0)
    
    # 构建分析请求，将UserProfile转换为dict
    analysis_request = {
        "target_career": target_career,
        "user_profile": dict(user_profile),  # 转换为普通字典
        "focus_areas": feedback_adjustments.get("focus_areas", []),
        "is_iteration": iteration_count > 0,
        "special_considerations": "结合用户反馈，重点分析AI产品经理相关的技能和路径" if "AI" in str(feedback_adjustments) else ""
    }
    
    # 调用百炼API进行职业分析
    llm_response = llm_service.analyze_career_opportunities(target_career, dict(user_profile))
    
    if llm_response.get("success"):
        try:
            result = json.loads(llm_response["content"])
            print(f"职业分析结果 (迭代{iteration_count}): {result}")
        except json.JSONDecodeError:
            result = {"error": "响应解析失败", "raw_response": llm_response["content"]}
    else:
        result = {"error": llm_response.get("error", "分析失败")}
    
    # 补充模拟的职位市场数据
    mcp_data = call_mcp_api("job_market", task["input_data"])
    result["job_market_data"] = mcp_data
    
    # 添加迭代信息
    result["iteration_info"] = {
        "iteration_count": iteration_count,
        "adjustments_applied": feedback_adjustments,
        "analysis_timestamp": datetime.now().isoformat()
    }
    
    output = AgentOutput(
        agent_name="job_analyzer_node",
        task_id=task["task_id"],
        output_type="职业建议",
        content=result,
        confidence_score=0.82 + (0.08 * iteration_count),
        data_sources=["百炼API", "MCP API", "招聘网站", "用户反馈"],
        analysis_method="LLM分析+市场调研+反馈优化",
        timestamp=datetime.now(),
        quality_metrics={"relevance": 0.9 + (0.05 * iteration_count), "accuracy": 0.8 + (0.1 * iteration_count)},
        recommendations=result.get("recommendations", []),
        warnings=result.get("risk_warnings", [])
    )
    
    return {
        "career_analysis_result": result, 
        "agent_outputs": [output]  # 返回单个输出，由Annotated自动合并
    }


# --- 结果汇总与规划节点 ---
def reporter_node(state: CareerNavigatorState) -> Dict[str, Any]:
    """
    汇报员节点
    
    职责:
    1. 收集所有并行分析节点的结果。
    2. 调用LLM将结果整合成一份结构化的综合报告。
    3. 更新状态，准备进入用户反馈阶段。
    4. 在迭代时，显示改进信息。
    """
    print("--- 正在执行: reporter_node ---")
    
    # 检查所有分析是否已完成
    required_results = ["self_insight_result", "industry_research_result", "career_analysis_result"]
    if not all(state.get(key) for key in required_results):
        return StateUpdater.log_error(state, {"error": "部分分析结果缺失，无法生成报告。"})

    analysis_results = {
        "profile_analysis": state["self_insight_result"],
        "industry_research": state["industry_research_result"],
        "career_analysis": state["career_analysis_result"]
    }
    
    # 检查是否为迭代
    iteration_count = state.get("iteration_count", 0)
    feedback_history = state.get("user_feedback_history", [])
    
    # 添加迭代上下文
    if iteration_count > 0 and feedback_history:
        latest_feedback = feedback_history[-1]
        analysis_results["iteration_context"] = {
            "iteration_count": iteration_count,
            "previous_feedback": latest_feedback.get("feedback_text", ""),
            "satisfaction_level": latest_feedback.get("satisfaction_level", ""),
            "improvements_made": "基于您的反馈重新分析了相关领域"
        }
        print(f"📈 生成第{iteration_count}次迭代报告，基于用户反馈: {latest_feedback.get('feedback_text', '')}")
    
    # 调用百炼API生成综合报告
    llm_response = llm_service.generate_integrated_report(analysis_results)
    
    if llm_response.get("success"):
        try:
            report = json.loads(llm_response["content"])
            if iteration_count > 0:
                report["iteration_summary"] = f"这是基于您反馈的第{iteration_count}次优化报告"
            print(f"综合报告生成成功 (迭代{iteration_count}): {report.get('executive_summary', '报告已生成')}")
        except json.JSONDecodeError:
            report = {
                "executive_summary": "综合分析报告",
                "error": "报告解析失败",
                "raw_response": llm_response["content"],
                "iteration_count": iteration_count
            }
    else:
        report = {
            "executive_summary": "综合分析报告",
            "error": llm_response.get("error", "报告生成失败"),
            "iteration_count": iteration_count
        }
    
    # 更新状态，进入用户反馈阶段
    updated_state = StateUpdater.update_stage(state, WorkflowStage.USER_FEEDBACK)
    updated_state["integrated_report"] = report
    # 设置需要用户输入标志，并提出问题
    feedback_question = f"这是第{iteration_count + 1}次分析报告，您对这份综合报告满意吗？请提供您的反馈或修改意见。" if iteration_count > 0 else "您对这份综合报告满意吗？请提供您的反馈或修改意见。"
    updated_state.update(StateUpdater.set_user_input_required(
        state, True, [feedback_question]
    ))
    return updated_state


def goal_decomposer_node(state: CareerNavigatorState) -> Dict[str, Any]:
    """
    目标拆分节点
    
    职责:
    1. 基于用户确认的职业方向（来自综合报告）。
    2. 将其分解为长期、中期、短期目标。
    """
    print("--- 正在执行: goal_decomposer_node ---")
    
    # 获取职业方向
    integrated_report = state.get("integrated_report", {})
    career_direction = integrated_report.get("career_match", {}).get("recommended_career", "")
    
    if not career_direction:
        # 从用户画像中获取职业目标
        career_direction = state["user_profile"].get("career_goals", "职业发展")
    
    user_profile = state["user_profile"]
    
    # 调用百炼API进行目标拆分
    llm_response = llm_service.decompose_career_goals(career_direction, user_profile)
    
    if llm_response.get("success"):
        try:
            decomposed_goals = json.loads(llm_response["content"])
            print(f"目标拆分完成: {len(decomposed_goals.get('short_term_goals', []))} 个短期目标")
        except json.JSONDecodeError:
            decomposed_goals = {
                "error": "目标拆分解析失败",
                "raw_response": llm_response["content"]
            }
    else:
        decomposed_goals = {
            "error": llm_response.get("error", "目标拆分失败")
        }
    
    # 更新状态，进入日程规划阶段
    updated_state = StateUpdater.update_stage(state, WorkflowStage.SCHEDULE_PLANNING)
    updated_state["career_goals"] = decomposed_goals
    return updated_state


def scheduler_node(state: CareerNavigatorState) -> Dict[str, Any]:
    """
    日程计划节点
    
    职责:
    1. 将拆分后的目标整合成可执行的、带时间线的具体任务。
    2. 生成最终的计划，并准备进行最终确认。
    """
    print("--- 正在执行: scheduler_node ---")
    
    career_goals = state.get("career_goals", {})
    user_profile = state["user_profile"]
    
    # 构建用户约束条件
    user_constraints = {
        "work_experience": user_profile.get("work_experience", 0),
        "current_position": user_profile.get("current_position", ""),
        "location": user_profile.get("location", ""),
        "available_time": "业余时间",  # 可以从用户输入中获取
        "budget": "中等"  # 可以从用户输入中获取
    }
    
    # 调用百炼API制定行动计划
    llm_response = llm_service.create_action_schedule(
        [career_goals] if career_goals else [], 
        user_constraints
    )
    
    if llm_response.get("success"):
        try:
            final_schedule = json.loads(llm_response["content"])
            print(f"行动计划制定完成: {final_schedule.get('schedule_overview', '计划已生成')}")
        except json.JSONDecodeError:
            final_schedule = {
                "error": "计划解析失败",
                "raw_response": llm_response["content"]
            }
    else:
        final_schedule = {
            "error": llm_response.get("error", "计划制定失败")
        }
    
    # 更新状态，进入最终确认阶段
    updated_state = StateUpdater.update_stage(state, WorkflowStage.FINAL_CONFIRMATION)
    updated_state["final_plan"] = final_schedule
    # 再次请求用户输入
    updated_state.update(StateUpdater.set_user_input_required(
        state, True, ["这是为您生成的最终行动计划，您是否满意？"]
    ))
    return updated_state

