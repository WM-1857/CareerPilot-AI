"""
CareerNavigator LangGraph 节点实现
基于阿里云百炼API的原子化节点设计
"""

import uuid
import json
import re
from datetime import datetime
from typing import Dict, Any, List

from src.models.career_state import (
    CareerNavigatorState, AgentTask, AgentOutput, AgentStatus, 
    WorkflowStage, StateUpdater, UserFeedback, UserSatisfactionLevel
)
from src.services.llm_service import llm_service, call_mcp_api


def parse_llm_json_content(content: str) -> Dict[str, Any]:
    """
    智能解析LLM返回的JSON内容，处理多种格式
    
    Args:
        content: LLM返回的原始内容
        
    Returns:
        解析后的字典对象
        
    Raises:
        json.JSONDecodeError: 当所有解析方法都失败时
    """
    if not content or not isinstance(content, str):
        raise json.JSONDecodeError("内容为空或格式错误", content or "", 0)
    
    content = content.strip()
    
    # 方法1: 直接解析JSON
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    
    # 方法2: 提取```json代码块中的内容
    json_block_pattern = r'```json\s*(.*?)\s*```'
    json_match = re.search(json_block_pattern, content, re.DOTALL | re.IGNORECASE)
    if json_match:
        try:
            json_content = json_match.group(1).strip()
            return json.loads(json_content)
        except json.JSONDecodeError:
            pass
    
    # 方法3: 提取任意代码块中的内容（可能是```没有指定语言）
    code_block_pattern = r'```\s*(.*?)\s*```'
    code_match = re.search(code_block_pattern, content, re.DOTALL)
    if code_match:
        try:
            json_content = code_match.group(1).strip()
            return json.loads(json_content)
        except json.JSONDecodeError:
            pass
    
    # 方法4: 提取{}包围的JSON内容
    if '{' in content and '}' in content:
        try:
            # 找到第一个{和最后一个}
            start = content.find('{')
            end = content.rfind('}') + 1
            json_content = content[start:end]
            return json.loads(json_content)
        except json.JSONDecodeError:
            pass
    
    # 方法5: 尝试移除可能的前后缀文本，提取JSON部分
    lines = content.split('\n')
    json_lines = []
    in_json = False
    brace_count = 0
    
    for line in lines:
        stripped_line = line.strip()
        if '{' in stripped_line and not in_json:
            in_json = True
            json_lines.append(line)
            brace_count += stripped_line.count('{') - stripped_line.count('}')
        elif in_json:
            json_lines.append(line)
            brace_count += stripped_line.count('{') - stripped_line.count('}')
            if brace_count == 0:
                break
    
    if json_lines:
        try:
            json_content = '\n'.join(json_lines)
            return json.loads(json_content)
        except json.JSONDecodeError:
            pass
    
    # 方法6: 处理截断的JSON (尝试补齐括号)
    try:
        # 提取最外层的 { } 内容
        start = content.find('{')
        if start != -1:
            json_part = content[start:]
            # 移除末尾的非JSON字符（如 ```）
            json_part = re.sub(r'```.*$', '', json_part, flags=re.DOTALL).strip()
            
            # 修复常见的列表未闭合问题: "key": ["val" \n "next_key": -> "key": ["val"], \n "next_key":
            # 这种错误常出现在LLM输出中，它开启了一个列表但忘记关闭就直接写下一个键值对了
            json_part = re.sub(r'(\[[^\]]*?)\s*\n\s*(\s*\"[\w_]+\"\s*:\s*)', r'\1], \n \2', json_part)
            
            # 修复缺失逗号的问题: "key1": "val1" \n "key2": "val2" -> "key1": "val1", \n "key2": "val2"
            # 匹配模式：一个值后面紧跟换行和下一个键名，但中间没有逗号
            json_part = re.sub(r'(\"(?:[^\"\\]|\\.)*\"\s*:\s*(?:\"(?:[^\"\\]|\\.)*\"|\d+|true|false|null|\[(?:[^\[\]]|\[[^\[\]]*\])*\]|\{(?:[^{}]|\{[^{}]*\})*\}))\s*\n\s*(\"(?:[^\"\\]|\\.)*\"\s*:\s*)', r'\1, \n \2', json_part)

            # 尝试修复被截断的字符串（如果最后一行没有闭合引号）
            # 查找最后一个未闭合的引号
            last_quote = json_part.rfind('"')
            if last_quote != -1:
                # 检查这个引号是否是闭合引号
                # 简单逻辑：如果引号后面紧跟的是 , } ] 或空白，则认为是闭合的
                remaining = json_part[last_quote+1:].strip()
                if remaining and not any(c in remaining for c in [',', '}', ']', ':']):
                    # 可能是截断在字符串中间，尝试补齐引号
                    json_part += '"'
            
            # 统计括号
            open_braces = json_part.count('{')
            close_braces = json_part.count('}')
            open_brackets = json_part.count('[')
            close_brackets = json_part.count(']')
            
            # 补齐缺失的括号
            fixed_json = json_part
            if open_brackets > close_brackets:
                fixed_json += ']' * (open_brackets - close_brackets)
            if open_braces > close_braces:
                fixed_json += '}' * (open_braces - close_braces)
                
            return json.loads(fixed_json)
    except:
        pass
    
    # 如果所有方法都失败，抛出异常
    raise json.JSONDecodeError(f"无法解析JSON内容。原始内容: {content[:200]}...", content, 0)


from langchain_core.runnables import RunnableConfig

def coordinator_node(state: CareerNavigatorState, config: RunnableConfig = None) -> Dict[str, Any]:
    """
    协调员节点 (入口点)
    
    职责:
    1. 检查用户的初始请求。
    2. 调用LLM判断用户的职业目标是否已经明确。
    3. 根据判断结果，决定下一个流程节点。
    """
    print("=" * 60)
    print("🚀 正在执行: coordinator_node")
    print("=" * 60)
    
    # 获取流式回调
    stream_callback = None
    if config and "configurable" in config and "stream_callback" in config["configurable"]:
        stream_callback = config["configurable"]["stream_callback"]
        if stream_callback:
            stream_callback(json.dumps({"node": "coordinator", "status": "start"}))

    # 检查用户满意度，如果已经有了满意度反馈，说明是点击了“满意”或“不满意”后重新进入的
    # 优先从 state 直接获取，如果不存在则尝试从 user_feedback_history 获取
    current_satisfaction = state.get("current_satisfaction")
    if current_satisfaction is None and state.get("user_feedback_history"):
        latest_feedback = state["user_feedback_history"][-1]
        # 兼容字典和对象格式
        if isinstance(latest_feedback, dict):
            current_satisfaction = latest_feedback.get("satisfaction_level")
        else:
            current_satisfaction = getattr(latest_feedback, "satisfaction_level", None)
        print(f"ℹ️ 从历史记录中恢复满意度状态: {current_satisfaction}")

    current_stage = state.get("current_stage")
    
    print(f"🔍 Coordinator 检查状态: stage={current_stage}, satisfaction={current_satisfaction}")
    
    # 如果已经有综合报告且处于等待反馈阶段，但没有新的满意度输入，说明可能是重复触发，直接结束
    if current_satisfaction is None and current_stage == WorkflowStage.USER_FEEDBACK and state.get("integrated_report"):
        print("⏸️ 当前处于等待用户反馈阶段，且已有报告，跳过重复执行")
        if stream_callback:
            stream_callback(json.dumps({"node": "coordinator", "content": "正在等待您的反馈..."}))
            stream_callback(json.dumps({"node": "coordinator", "status": "end"}))
        return {"next_node": "end"}
    
    # 如果处于后续阶段，自动跳转
    if current_satisfaction is None:
        if current_stage == WorkflowStage.GOAL_DECOMPOSITION:
            print("⏩ 自动跳转到目标拆解阶段")
            updates = {"next_node": "goal_decomposer"}
            return updates
        elif current_stage == WorkflowStage.SCHEDULE_PLANNING:
            print("⏩ 自动跳转到日程规划阶段")
            updates = {"next_node": "scheduler"}
            return updates
        elif current_stage == WorkflowStage.COMPLETED:
            print("✅ 流程已完成，直接结束")
            updates = {"next_node": "end"}
            return updates

    if current_satisfaction is not None:
        # 处理分析报告阶段的反馈
        if current_stage == WorkflowStage.USER_FEEDBACK:
            if current_satisfaction in [UserSatisfactionLevel.SATISFIED, UserSatisfactionLevel.VERY_SATISFIED]:
                print(f"✅ 检测到用户已满意分析报告({current_satisfaction.value})，直接跳转到目标拆分阶段")
                updates = StateUpdater.update_stage(state, WorkflowStage.GOAL_DECOMPOSITION)
                updates["next_node"] = "goal_decomposer"
                updates["current_satisfaction"] = None
                if stream_callback:
                    stream_callback(json.dumps({"node": "coordinator", "content": "检测到您已确认报告，正在进入目标拆解阶段..."}))
                    stream_callback(json.dumps({"node": "coordinator", "status": "end"}))
                return updates
            elif current_satisfaction in [UserSatisfactionLevel.DISSATISFIED, UserSatisfactionLevel.VERY_DISSATISFIED]:
                print(f"🔄 检测到用户不满意分析报告({current_satisfaction.value})，重新进入策略制定阶段")
                updates = StateUpdater.update_stage(state, WorkflowStage.PLANNING)
                updates["next_node"] = "planner"
                updates["current_satisfaction"] = None
                if stream_callback:
                    stream_callback(json.dumps({"node": "coordinator", "content": "检测到您对报告有修改意见，正在重新为您分析..."}))
                    stream_callback(json.dumps({"node": "coordinator", "status": "end"}))
                return updates
        
        # 处理最终确认阶段的反馈
        elif current_stage == WorkflowStage.FINAL_CONFIRMATION:
            if current_satisfaction in [UserSatisfactionLevel.SATISFIED, UserSatisfactionLevel.VERY_SATISFIED]:
                print(f"✅ 检测到用户已满意最终计划({current_satisfaction.value})，流程结束")
                updates = StateUpdater.update_stage(state, WorkflowStage.COMPLETED)
                updates["next_node"] = "end"
                updates["current_satisfaction"] = None
                if stream_callback:
                    stream_callback(json.dumps({"node": "coordinator", "content": "感谢您的确认，职业规划流程已圆满完成！"}))
                    stream_callback(json.dumps({"node": "coordinator", "status": "end"}))
                return updates
            elif current_satisfaction in [UserSatisfactionLevel.DISSATISFIED, UserSatisfactionLevel.VERY_DISSATISFIED]:
                print(f"🔄 检测到用户不满意最终计划({current_satisfaction.value})，返回目标拆分阶段重新调整")
                updates = StateUpdater.update_stage(state, WorkflowStage.GOAL_DECOMPOSITION)
                updates["next_node"] = "goal_decomposer"
                updates["current_satisfaction"] = None
                if stream_callback:
                    stream_callback(json.dumps({"node": "coordinator", "content": "检测到您对计划有修改意见，正在为您重新调整目标拆解..."}))
                    stream_callback(json.dumps({"node": "coordinator", "status": "end"}))
                return updates

    messages = state.get("messages", [])
    user_request = messages[-1].content if messages else ""
    print(f"📝 用户请求: {user_request}")
    
    # 安全获取用户画像
    user_profile = state.get("user_profile")
    if not user_profile:
        print("⚠️ 警告: 未找到用户画像，使用默认值")
        user_profile = {
            "user_id": "unknown",
            "age": 0,
            "education_level": "未知",
            "work_experience": 0,
            "current_position": "未知",
            "industry": "未知",
            "skills": [],
            "interests": [],
            "career_goals": "未知",
            "location": "未知",
            "salary_expectation": "未知"
        }

    # 调用百炼API分析目标明确度
    llm_response = llm_service.analyze_career_goal_clarity(
        user_request, 
        user_profile,
        stream_callback=lambda x: stream_callback(json.dumps({"node": "coordinator", "content": x})) if stream_callback else None
    )
    
    if stream_callback:
        stream_callback(json.dumps({"node": "coordinator", "status": "end"}))
    
    print(f"🤖 LLM原始响应: {json.dumps(llm_response, ensure_ascii=False, indent=2)}")
    
    if llm_response.get("success"):
        try:
            # 使用智能JSON解析
            analysis = parse_llm_json_content(llm_response["content"])
            is_goal_clear = analysis.get("is_goal_clear", False)
            clarity_score = analysis.get("clarity_score", 0)
            
            print(f"📊 目标明确度分析结果:")
            print(f"   - 目标是否明确: {is_goal_clear}")
            print(f"   - 明确度评分: {clarity_score}")
            print(f"   - 详细分析: {json.dumps(analysis, ensure_ascii=False, indent=2)}")
            
            if is_goal_clear:
                print("✅ 判断：目标明确，直接进入目标拆分。")
                # 更新状态，直接进入目标拆分阶段
                updates = StateUpdater.update_stage(state, WorkflowStage.GOAL_DECOMPOSITION)
                updates["next_node"] = "goal_decomposer"
                updates["cached_data"] = {"goal_analysis": analysis}
                
                print(f"🔄 状态更新: {json.dumps(updates, ensure_ascii=False, indent=2, default=str)}")
                return updates
            else:
                print("🔄 判断：目标不明确，需要进行规划和分析。")
                # 更新状态，进入策略制定阶段
                updates = StateUpdater.update_stage(state, WorkflowStage.PLANNING)
                updates["next_node"] = "planner"
                updates["cached_data"] = {"goal_analysis": analysis}
                
                print(f"🔄 状态更新: {json.dumps(updates, ensure_ascii=False, indent=2, default=str)}")
                return updates
        except json.JSONDecodeError as e:
            print(f"❌ LLM响应解析失败: {str(e)}")
            print(f"📄 原始响应内容: {llm_response['content'][:300]}...")
            print("🔄 默认进入规划阶段")
            updates = StateUpdater.update_stage(state, WorkflowStage.PLANNING)
            updates["next_node"] = "planner"
            
            print(f"🔄 状态更新: {json.dumps(updates, ensure_ascii=False, indent=2, default=str)}")
            return updates
    else:
        print(f"❌ LLM调用失败: {llm_response.get('error')}")
        # 默认进入规划阶段
        updates = StateUpdater.update_stage(state, WorkflowStage.PLANNING)
        updates["next_node"] = "planner"
        
        print(f"🔄 状态更新: {json.dumps(updates, ensure_ascii=False, indent=2, default=str)}")
        return updates


def planner_node(state: CareerNavigatorState, config: RunnableConfig = None) -> Dict[str, Any]:
    """
    计划员节点
    
    职责:
    1. 当用户目标不明确时，制定一个详细的分析策略。
    2. 将策略存入State中，供后续节点使用。
    """
    print("=" * 60)
    print("📋 正在执行: planner_node")
    print("=" * 60)
    
    # 获取流式回调
    stream_callback = None
    if config and "configurable" in config and "stream_callback" in config["configurable"]:
        stream_callback = config["configurable"]["stream_callback"]
        if stream_callback:
            stream_callback(json.dumps({"node": "planner", "status": "start"}))

    user_profile = state["user_profile"]
    feedback_history = state["user_feedback_history"]
    
    print(f"👤 用户画像: {json.dumps(dict(user_profile), ensure_ascii=False, indent=2)}")
    print(f"💬 反馈历史: {len(feedback_history)} 条记录")
    
    # 调用百炼API制定分析策略
    llm_response = llm_service.create_analysis_strategy(
        user_profile, 
        feedback_history,
        stream_callback=lambda x: stream_callback(json.dumps({"node": "planner", "content": x})) if stream_callback else None
    )
    
    if stream_callback:
        stream_callback(json.dumps({"node": "planner", "status": "end"}))
    
    print(f"🤖 LLM原始响应: {json.dumps(llm_response, ensure_ascii=False, indent=2)}")
    
    # 准备更新，同时清除满意度状态，以便下次反馈循环
    updates = {"current_satisfaction": None}
    
    if llm_response.get("success"):
        try:
            # 使用智能JSON解析
            strategy = parse_llm_json_content(llm_response["content"])
            print(f"📊 分析策略结果: {json.dumps(strategy, ensure_ascii=False, indent=2)}")
            
            updates["planning_strategy"] = strategy.get("strategy_overview", "制定个性化职业分析策略")
            print(f"🔄 状态更新: {json.dumps(updates, ensure_ascii=False, indent=2)}")
            return updates
        except json.JSONDecodeError as e:
            print(f"❌ 策略解析失败: {str(e)}")
            print(f"📄 原始响应内容: {llm_response['content'][:300]}...")
            print("🔄 使用默认策略")
            updates["planning_strategy"] = "制定个性化职业分析策略"
            print(f"🔄 状态更新: {json.dumps(updates, ensure_ascii=False, indent=2)}")
            return updates
    else:
        print(f"❌ 策略制定失败: {llm_response.get('error')}")
        updates["planning_strategy"] = "制定个性化职业分析策略"
        print(f"🔄 状态更新: {json.dumps(updates, ensure_ascii=False, indent=2)}")
        return updates


def supervisor_node(state: CareerNavigatorState, config: RunnableConfig = None) -> Dict[str, Any]:
    """
    管理员节点
    
    职责:
    1. 根据 `planning_strategy` 创建并分发并行的分析任务。
    2. 为每个任务创建一个 AgentTask 对象，并添加到 State 中。
    3. 在迭代时，考虑用户反馈来调整分析策略。
    """
    print("=" * 60)
    print("👨‍💼 正在执行: supervisor_node")
    print("=" * 60)
    
    # 获取流式回调
    stream_callback = None
    if config and "configurable" in config and "stream_callback" in config["configurable"]:
        stream_callback = config["configurable"]["stream_callback"]
        if stream_callback:
            stream_callback(json.dumps({"node": "supervisor", "status": "start"}))
            stream_callback(json.dumps({"node": "supervisor", "content": "正在根据策略分配分析任务..."}))

    plan = state.get("planning_strategy", "制定个性化职业分析策略")
    print(f"📋 当前策略: {plan}")
    
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
    
    print(f"🎯 分析调整: {json.dumps(analysis_adjustments, ensure_ascii=False, indent=2)}")
    
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
    
    print(f"📋 创建了 {len(tasks)} 个并行任务:")
    for i, task in enumerate(tasks, 1):
        print(f"   {i}. {task['agent_name']} - {task['task_type']}")
        print(f"      描述: {task['description']}")
        print(f"      输入数据: {json.dumps(task['input_data'], ensure_ascii=False, indent=6, default=str)}")
    
    # 更新状态，进入并行分析阶段
    updated_state = StateUpdater.update_stage(state, WorkflowStage.PARALLEL_ANALYSIS)
    updated_state["agent_tasks"] = tasks
    
    # 在 supervisor_node 结束前发送结束状态
    if stream_callback:
        stream_callback(json.dumps({"node": "supervisor", "status": "end"}))
    
    print(f"🔄 状态更新: {json.dumps(updated_state, ensure_ascii=False, indent=2, default=str)}")
    return updated_state


# --- 并行分析节点 ---
def user_profiler_node(state: CareerNavigatorState, config: RunnableConfig = None) -> Dict[str, Any]:
    """用户建模节点 (并行)"""
    print("=" * 60)
    print("👤 正在执行: user_profiler_node")
    print("=" * 60)
    
    # 获取流式回调
    stream_callback = None
    if config and "configurable" in config and "stream_callback" in config["configurable"]:
        stream_callback = config["configurable"]["stream_callback"]
        if stream_callback:
            stream_callback(json.dumps({"node": "user_profiler", "status": "start"}))

    task = next((t for t in state["agent_tasks"] if t["agent_name"] == "user_profiler_node"), None)
    
    if not task:
        print("❌ 未找到用户画像分析任务")
        if stream_callback:
            stream_callback(json.dumps({"node": "user_profiler", "status": "end"}))
        return StateUpdater.log_error(state, {"error": "未找到用户画像分析任务"})
    
    print(f"📋 任务信息: {task['task_type']} - {task['description']}")
    
    # 获取分析调整和迭代信息
    input_data = task["input_data"]
    feedback_adjustments = input_data.get("feedback_adjustments", {})
    iteration_count = input_data.get("iteration_count", 0)
    
    print(f"🔄 迭代次数: {iteration_count}")
    print(f"🎯 反馈调整: {json.dumps(feedback_adjustments, ensure_ascii=False, indent=2)}")
    
    # 构建分析请求，包含反馈调整
    analysis_request = {
        "user_profile": dict(input_data.get("user_profile", {})),
        "feedback_adjustments": feedback_adjustments,
        "focus_areas": feedback_adjustments.get("focus_areas", []),
        "is_iteration": iteration_count > 0,
        "improvement_notes": "结合用户反馈重新分析用户能力和优势"
    }
    
    print(f"📤 分析请求: {json.dumps(analysis_request, ensure_ascii=False, indent=2, default=str)}")
    
    # 调用百炼API进行用户画像分析
    llm_response = llm_service.analyze_user_profile(
        analysis_request["user_profile"],
        feedback_adjustments=analysis_request["feedback_adjustments"],
        stream_callback=lambda x: stream_callback(json.dumps({"node": "user_profiler", "content": x})) if stream_callback else None
    )
    
    if stream_callback:
        stream_callback(json.dumps({"node": "user_profiler", "status": "end"}))
    
    print(f"🤖 LLM原始响应: {json.dumps(llm_response, ensure_ascii=False, indent=2)}")
    
    if llm_response.get("success"):
        try:
            # 使用智能JSON解析
            result = parse_llm_json_content(llm_response["content"])
            print(f"📊 用户画像分析结果 (迭代{iteration_count}): {json.dumps(result, ensure_ascii=False, indent=2)}")
        except json.JSONDecodeError as e:
            result = {"error": f"响应解析失败: {str(e)}", "raw_response": llm_response["content"][:500]}
            print(f"❌ 响应解析失败: {result}")
    else:
        result = {"error": llm_response.get("error", "分析失败")}
        print(f"❌ 分析失败: {result}")
    
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
    
    updates = {
        "self_insight_result": result, 
        "agent_outputs": [output]  # 返回单个输出，由Annotated自动合并
    }
    
    print(f"🔄 状态更新: {json.dumps(updates, ensure_ascii=False, indent=2, default=str)}")
    return updates


def industry_researcher_node(state: CareerNavigatorState, config: RunnableConfig = None) -> Dict[str, Any]:
    """行业研究节点 (并行)"""
    print("=" * 60)
    print("🏢 正在执行: industry_researcher_node")
    print("=" * 60)
    
    # 获取流式回调
    stream_callback = None
    if config and "configurable" in config and "stream_callback" in config["configurable"]:
        stream_callback = config["configurable"]["stream_callback"]
        if stream_callback:
            stream_callback(json.dumps({"node": "industry_researcher", "status": "start"}))

    task = next((t for t in state["agent_tasks"] if t["agent_name"] == "industry_researcher_node"), None)
    
    if not task:
        print("❌ 未找到行业研究任务")
        if stream_callback:
            stream_callback(json.dumps({"node": "industry_researcher", "status": "end"}))
        return StateUpdater.log_error(state, {"error": "未找到行业研究任务"})
    
    print(f"📋 任务信息: {task['task_type']} - {task['description']}")
    
    target_industry = task["input_data"].get("target_industry", "科技行业")
    feedback_adjustments = task["input_data"].get("feedback_adjustments", {})
    iteration_count = task["input_data"].get("iteration_count", 0)
    
    print(f"🏢 目标行业: {target_industry}")
    print(f"🔄 迭代次数: {iteration_count}")
    print(f"🎯 反馈调整: {json.dumps(feedback_adjustments, ensure_ascii=False, indent=2)}")
    
    # 构建研究请求，包含反馈调整
    research_request = {
        "target_industry": target_industry,
        "focus_areas": feedback_adjustments.get("focus_areas", []),
        "is_iteration": iteration_count > 0,
        "special_focus": "结合用户反馈，重点关注AI和大模型相关的行业机会" if "AI" in str(feedback_adjustments) else ""
    }
    
    print(f"📤 研究请求: {json.dumps(research_request, ensure_ascii=False, indent=2)}")
    
    # 调用百炼API进行行业研究
    llm_response = llm_service.research_industry_trends(
        target_industry,
        stream_callback=lambda x: stream_callback(json.dumps({"node": "industry_researcher", "content": x})) if stream_callback else None
    )
    
    if stream_callback:
        stream_callback(json.dumps({"node": "industry_researcher", "status": "end"}))
    
    print(f"🤖 LLM原始响应: {json.dumps(llm_response, ensure_ascii=False, indent=2)}")
    
    if llm_response.get("success"):
        try:
            # 使用智能JSON解析
            result = parse_llm_json_content(llm_response["content"])
            print(f"📊 行业研究结果 (迭代{iteration_count}): {json.dumps(result, ensure_ascii=False, indent=2)}")
        except json.JSONDecodeError as e:
            result = {"error": f"响应解析失败: {str(e)}", "raw_response": llm_response["content"][:500]}
            print(f"❌ 响应解析失败: {result}")
    else:
        result = {"error": llm_response.get("error", "研究失败")}
        print(f"❌ 研究失败: {result}")
    
    # 补充模拟的市场数据
    mcp_data = call_mcp_api("industry_data", task["input_data"])
    # print(f"🔗 MCP industry_data 结果: {json.dumps(mcp_data, ensure_ascii=False, indent=2)}")
    #就业市场爬取结果
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
    
    updates = {
        "industry_research_result": result, 
        "agent_outputs": [output]  # 返回单个输出，由Annotated自动合并
    }
    
    print(f"🔄 状态更新: {json.dumps(updates, ensure_ascii=False, indent=2, default=str)}")
    return updates


def job_analyzer_node(state: CareerNavigatorState, config: RunnableConfig = None) -> Dict[str, Any]:
    """职业分析节点 (并行)"""
    print("=" * 60)
    print("💼 正在执行: job_analyzer_node")
    print("=" * 60)
    
    # 获取流式回调
    stream_callback = None
    if config and "configurable" in config and "stream_callback" in config["configurable"]:
        stream_callback = config["configurable"]["stream_callback"]
        if stream_callback:
            stream_callback(json.dumps({"node": "job_analyzer", "status": "start"}))

    task = next((t for t in state["agent_tasks"] if t["agent_name"] == "job_analyzer_node"), None)
    
    if not task:
        print("❌ 未找到职业分析任务")
        if stream_callback:
            stream_callback(json.dumps({"node": "job_analyzer", "status": "end"}))
        return StateUpdater.log_error(state, {"error": "未找到职业分析任务"})
    
    print(f"📋 任务信息: {task['task_type']} - {task['description']}")
    
    target_career = task["input_data"].get("target_career", "产品经理")
    user_profile = state["user_profile"]
    feedback_adjustments = task["input_data"].get("feedback_adjustments", {})
    iteration_count = task["input_data"].get("iteration_count", 0)
    
    print(f"💼 目标职业: {target_career}")
    print(f"🔄 迭代次数: {iteration_count}")
    print(f"🎯 反馈调整: {json.dumps(feedback_adjustments, ensure_ascii=False, indent=2)}")
    
    # 构建分析请求，将UserProfile转换为dict
    analysis_request = {
        "target_career": target_career,
        "user_profile": dict(user_profile),  # 转换为普通字典
        "focus_areas": feedback_adjustments.get("focus_areas", []),
        "is_iteration": iteration_count > 0,
        "special_considerations": "结合用户反馈，重点分析AI产品经理相关的技能和路径" if "AI" in str(feedback_adjustments) else ""
    }
    
    print(f"📤 分析请求: {json.dumps(analysis_request, ensure_ascii=False, indent=2, default=str)}")
    
    # 调用百炼API进行职业分析
    llm_response = llm_service.analyze_career_opportunities(
        target_career, 
        dict(user_profile),
        stream_callback=lambda x: stream_callback(json.dumps({"node": "job_analyzer", "content": x})) if stream_callback else None
    )
    
    if stream_callback:
        stream_callback(json.dumps({"node": "job_analyzer", "status": "end"}))
    
    print(f"🤖 LLM原始响应: {json.dumps(llm_response, ensure_ascii=False, indent=2)}")
    
    if llm_response.get("success"):
        try:
            # 使用智能JSON解析
            result = parse_llm_json_content(llm_response["content"])
            print(f"📊 职业分析结果 (迭代{iteration_count}): {json.dumps(result, ensure_ascii=False, indent=2)}")
        except json.JSONDecodeError as e:
            result = {"error": f"响应解析失败: {str(e)}", "raw_response": llm_response["content"][:500]}
            print(f"❌ 响应解析失败: {result}")
    else:
        result = {"error": llm_response.get("error", "分析失败")}
        print(f"❌ 分析失败: {result}")
    
    # 补充模拟的职位市场数据
    mcp_data = call_mcp_api("job_market", task["input_data"])
    #print(f"🔗 MCP job_market 结果: {json.dumps(mcp_data, ensure_ascii=False, indent=2)}")
    #职业市场爬取结果
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
    
    updates = {
        "career_analysis_result": result, 
        "agent_outputs": [output]  # 返回单个输出，由Annotated自动合并
    }
    
    print(f"🔄 状态更新: {json.dumps(updates, ensure_ascii=False, indent=2, default=str)}")
    return updates


# --- 结果汇总与规划节点 ---
def reporter_node(state: CareerNavigatorState, config: RunnableConfig = None) -> Dict[str, Any]:
    """
    汇报员节点
    
    职责:
    1. 收集所有并行分析节点的结果。
    2. 调用LLM将结果整合成一份结构化的综合报告。
    3. 更新状态，准备进入用户反馈阶段。
    4. 在迭代时，显示改进信息。
    """
    print("=" * 60)
    print("📊 正在执行: reporter_node")
    print("=" * 60)
    
    # 获取流式回调
    stream_callback = None
    if config and "configurable" in config and "stream_callback" in config["configurable"]:
        stream_callback = config["configurable"]["stream_callback"]
        if stream_callback:
            stream_callback(json.dumps({"node": "reporter", "status": "start"}))
            stream_callback(json.dumps({"node": "reporter", "content": "正在汇总分析结果并生成综合报告..."}))

    # 检查所有分析是否已完成
    required_results = ["self_insight_result", "industry_research_result", "career_analysis_result"]
    if not all(state.get(key) for key in required_results):
        print("❌ 部分分析结果缺失，无法生成报告")
        return StateUpdater.log_error(state, {"error": "部分分析结果缺失，无法生成报告。"})

    analysis_results = {
        "profile_analysis": state["self_insight_result"],
        "industry_research": state["industry_research_result"],
        "career_analysis": state["career_analysis_result"]
    }
    
    print(f"📋 收集到的分析结果:")
    for key, value in analysis_results.items():
        print(f"   - {key}: {type(value).__name__}")
        if isinstance(value, dict) and "error" not in value:
            print(f"     摘要: {json.dumps(value, ensure_ascii=False)[:200]}...")
    
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
    
    print(f"📤 综合报告请求: {json.dumps(analysis_results, ensure_ascii=False, indent=2, default=str)}")
    
    # 调用百炼API生成综合报告 (Reporter节点不需要流式输出)
    llm_response = llm_service.generate_integrated_report(
        analysis_results
    )
    
    print(f"🤖 LLM原始响应: {json.dumps(llm_response, ensure_ascii=False, indent=2)}")
    
    if llm_response.get("success"):
        try:
            # 使用智能JSON解析
            report = parse_llm_json_content(llm_response["content"])
            if iteration_count > 0:
                report["iteration_summary"] = f"这是基于您反馈的第{iteration_count}次优化报告"
            print(f"📊 综合报告生成成功 (迭代{iteration_count}): {json.dumps(report, ensure_ascii=False, indent=2)}")
        except json.JSONDecodeError as e:
            report = {
                "executive_summary": "综合分析报告",
                "error": f"报告解析失败: {str(e)}",
                "raw_response": llm_response["content"][:500],
                "iteration_count": iteration_count
            }
            print(f"❌ 报告解析失败: {report}")
    else:
        report = {
            "executive_summary": "综合分析报告",
            "error": llm_response.get("error", "报告生成失败"),
            "iteration_count": iteration_count
        }
        print(f"❌ 报告生成失败: {report}")
    
    # 检查是否达到最大迭代次数
    iteration_count = state.get("iteration_count", 0)
    max_iterations = state.get("max_iterations", 2)
    
    if iteration_count >= max_iterations:
        print(f"⚠️ 已达到最大迭代次数({max_iterations})，跳过用户反馈，直接进入目标拆分阶段")
        # 直接进入目标拆分阶段，跳过用户反馈
        updated_state = StateUpdater.update_stage(state, WorkflowStage.GOAL_DECOMPOSITION)
        updated_state["integrated_report"] = report
        updated_state["skip_feedback_reason"] = "达到最大迭代次数"
        
        if stream_callback:
            stream_callback(json.dumps({"node": "reporter", "status": "end"}))
            
        print(f"🔄 状态更新: {json.dumps(updated_state, ensure_ascii=False, indent=2, default=str)}")
        return updated_state
    else:
        print(f"📝 迭代次数({iteration_count}/{max_iterations})，进入用户反馈阶段")
        # 更新状态，进入用户反馈阶段
        updated_state = StateUpdater.update_stage(state, WorkflowStage.USER_FEEDBACK)
        updated_state["integrated_report"] = report
        # 设置需要用户输入标志，并提出问题
        feedback_question = f"这是第{iteration_count + 1}次分析报告，您对这份综合报告满意吗？请提供您的反馈或修改意见。" if iteration_count > 0 else "您对这份综合报告满意吗？请提供您的反馈或修改意见。"
        updated_state.update(StateUpdater.set_user_input_required(
            state, True, [feedback_question]
        ))
        
        if stream_callback:
            stream_callback(json.dumps({"node": "reporter", "status": "end"}))
            
        print(f"🔄 状态更新: {json.dumps(updated_state, ensure_ascii=False, indent=2, default=str)}")
        return updated_state


def goal_decomposer_node(state: CareerNavigatorState, config: RunnableConfig = None) -> Dict[str, Any]:
    """
    目标拆分节点
    
    职责:
    1. 基于用户确认的职业方向（来自综合报告）。
    2. 将其分解为长期、中期、短期目标。
    """
    print("=" * 60)
    print("🎯 正在执行: goal_decomposer_node")
    print("=" * 60)
    
    # 获取流式回调
    stream_callback = None
    if config and "configurable" in config and "stream_callback" in config["configurable"]:
        stream_callback = config["configurable"]["stream_callback"]
        if stream_callback:
            stream_callback(json.dumps({"node": "goal_decomposer", "status": "start"}))
            stream_callback(json.dumps({"node": "goal_decomposer", "content": "正在将职业目标拆解为阶段性计划..."}))

    # 获取职业方向
    integrated_report = state.get("integrated_report") or {}
    career_match = integrated_report.get("career_match") or {}
    career_direction = career_match.get("recommended_career", "")
    
    if not career_direction:
        # 从用户画像中获取职业目标
        user_profile = state.get("user_profile") or {}
        career_direction = user_profile.get("career_goals", "职业发展")
    
    user_profile = state.get("user_profile") or {}
    
    print(f"🎯 目标职业方向: {career_direction}")
    print(f"👤 用户画像: {json.dumps(dict(user_profile), ensure_ascii=False, indent=2)}")
    
    # 调用百炼API进行目标拆分
    llm_response = llm_service.decompose_career_goals(
        career_direction, 
        user_profile,
        stream_callback=lambda x: stream_callback(json.dumps({"node": "goal_decomposer", "content": x})) if stream_callback else None
    )
    
    if stream_callback:
        stream_callback(json.dumps({"node": "goal_decomposer", "status": "end"}))
    
    print(f"🤖 LLM原始响应: {json.dumps(llm_response, ensure_ascii=False, indent=2)}")
    
    # 准备更新，同时清除满意度状态，以便下次反馈循环
    updated_state = {"current_satisfaction": None}
    
    if llm_response.get("success"):
        try:
            # 使用智能JSON解析
            decomposed_goals = parse_llm_json_content(llm_response["content"])
            print(f"📊 目标拆分完成: {json.dumps(decomposed_goals, ensure_ascii=False, indent=2)}")
            print(f"   - 短期目标: {len(decomposed_goals.get('short_term_goals', []))} 个")
            print(f"   - 中期目标: {len(decomposed_goals.get('medium_term_goals', []))} 个")
            print(f"   - 长期目标: {len(decomposed_goals.get('long_term_goals', []))} 个")
        except json.JSONDecodeError as e:
            decomposed_goals = {
                "error": f"目标拆分解析失败: {str(e)}",
                "raw_response": llm_response["content"][:500]
            }
            print(f"❌ 目标拆分解析失败: {decomposed_goals}")
    else:
        decomposed_goals = {
            "error": llm_response.get("error", "目标拆分失败")
        }
        print(f"❌ 目标拆分失败: {decomposed_goals}")
    
    # 更新状态，进入日程规划阶段
    updated_state.update(StateUpdater.update_stage(state, WorkflowStage.SCHEDULE_PLANNING))
    updated_state["career_goals"] = decomposed_goals
    
    print(f"🔄 状态更新: {json.dumps(updated_state, ensure_ascii=False, indent=2, default=str)}")
    return updated_state


def scheduler_node(state: CareerNavigatorState, config: RunnableConfig = None) -> Dict[str, Any]:
    """
    日程计划节点
    
    职责:
    1. 将拆分后的目标整合成可执行的、带时间线的具体任务。
    2. 生成最终的计划，并准备进行最终确认。
    """
    print("=" * 60)
    print("📅 正在执行: scheduler_node")
    print("=" * 60)
    
    # 获取流式回调
    stream_callback = None
    if config and "configurable" in config and "stream_callback" in config["configurable"]:
        stream_callback = config["configurable"]["stream_callback"]
        if stream_callback:
            stream_callback(json.dumps({"node": "scheduler", "status": "start"}))
            stream_callback(json.dumps({"node": "scheduler", "content": "正在为您制定详细的行动日程表..."}))

    career_goals = state.get("career_goals") or {}
    user_profile = state.get("user_profile") or {}
    
    print(f"🎯 职业目标: {json.dumps(career_goals, ensure_ascii=False, indent=2)}")
    print(f"👤 用户画像: {json.dumps(dict(user_profile), ensure_ascii=False, indent=2)}")
    
    # 构建用户约束条件
    user_constraints = {
        "work_experience": user_profile.get("work_experience", 0),
        "current_position": user_profile.get("current_position", ""),
        "location": user_profile.get("location", ""),
        "available_time": "业余时间",  # 可以从用户输入中获取
        "budget": "中等"  # 可以从用户输入中获取
    }
    
    print(f"⚙️ 用户约束条件: {json.dumps(user_constraints, ensure_ascii=False, indent=2)}")
    
    # 调用百炼API制定行动计划
    llm_response = llm_service.create_action_schedule(
        [career_goals] if career_goals else [], 
        user_constraints,
        stream_callback=lambda x: stream_callback(json.dumps({"node": "scheduler", "content": x})) if stream_callback else None
    )
    
    if stream_callback:
        stream_callback(json.dumps({"node": "scheduler", "status": "end"}))
    
    print(f"🤖 LLM原始响应: {json.dumps(llm_response, ensure_ascii=False, indent=2)}")
    
    if llm_response.get("success"):
        try:
            # 使用智能JSON解析
            final_schedule = parse_llm_json_content(llm_response["content"])
            print(f"📊 行动计划制定完成: {json.dumps(final_schedule, ensure_ascii=False, indent=2)}")
            print(f"   - 计划概述: {final_schedule.get('schedule_overview', '计划已生成')}")
        except json.JSONDecodeError as e:
            final_schedule = {
                "error": f"计划解析失败: {str(e)}",
                "raw_response": llm_response["content"][:500]
            }
            print(f"❌ 计划解析失败: {final_schedule}")
    else:
        final_schedule = {
            "error": llm_response.get("error", "计划制定失败")
        }
        print(f"❌ 计划制定失败: {final_schedule}")
    
    # 更新状态，进入最终确认阶段
    updated_state = StateUpdater.update_stage(state, WorkflowStage.FINAL_CONFIRMATION)
    updated_state["final_career_plan"] = final_schedule  # 使用与interactive_workflow.py一致的键名
    # 再次请求用户输入
    updated_state.update(StateUpdater.set_user_input_required(
        state, True, ["这是为您生成的最终行动计划，您是否满意？"]
    ))
    
    print(f"🔄 状态更新: {json.dumps(updated_state, ensure_ascii=False, indent=2, default=str)}")
    return updated_state

