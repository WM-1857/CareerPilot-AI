"""
职业规划API路由
提供RESTful API接口供前端调用
"""

import json
from flask import Blueprint, request, jsonify
from datetime import datetime

from src.models.career_state import UserProfile, UserSatisfactionLevel
from src.services.career_graph import career_graph

career_bp = Blueprint('career', __name__)

# 存储会话状态的简单内存存储（生产环境应使用Redis或数据库）
session_store = {}


@career_bp.route('/start', methods=['POST'])
def start_career_planning():
    """
    开始职业规划
    
    请求体:
    {
        "user_profile": {
            "user_id": "string",
            "age": int,
            "education_level": "string",
            "work_experience": int,
            "current_position": "string",
            "industry": "string",
            "skills": ["string"],
            "interests": ["string"],
            "career_goals": "string",
            "location": "string",
            "salary_expectation": "string"
        },
        "message": "string"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "请提供请求数据"}), 400
        
        # 验证必要字段
        if 'user_profile' not in data or 'message' not in data:
            return jsonify({"error": "缺少必要字段: user_profile 和 message"}), 400
        
        user_profile_data = data['user_profile']
        user_message = data['message']
        
        # 创建用户画像
        user_profile = UserProfile(
            user_id=user_profile_data.get('user_id', f"user_{datetime.now().timestamp()}"),
            age=user_profile_data.get('age'),
            education_level=user_profile_data.get('education_level'),
            work_experience=user_profile_data.get('work_experience'),
            current_position=user_profile_data.get('current_position'),
            industry=user_profile_data.get('industry'),
            skills=user_profile_data.get('skills'),
            interests=user_profile_data.get('interests'),
            career_goals=user_profile_data.get('career_goals'),
            location=user_profile_data.get('location'),
            salary_expectation=user_profile_data.get('salary_expectation'),
            additional_info=user_profile_data.get('additional_info')
        )
        
        # 创建会话
        initial_state = career_graph.create_session(user_profile, user_message)
        session_id = initial_state['session_id']
        
        # 存储会话状态
        session_store[session_id] = initial_state
        
        # 运行工作流
        result = career_graph.run_workflow(initial_state)
        
        if result['success']:
            # 更新会话状态
            session_store[session_id] = result['final_state']
            
            # 获取当前阶段信息
            stage_info = career_graph.get_current_stage_info(result['final_state'])
            
            return jsonify({
                "success": True,
                "session_id": session_id,
                "stage_info": stage_info,
                "message": "职业规划已开始"
            })
        else:
            return jsonify({
                "success": False,
                "error": result['error']
            }), 500
            
    except Exception as e:
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500


@career_bp.route('/status/<session_id>', methods=['GET'])
def get_planning_status(session_id):
    """
    获取规划状态
    """
    try:
        if session_id not in session_store:
            return jsonify({"error": "会话不存在"}), 404
        
        state = session_store[session_id]
        stage_info = career_graph.get_current_stage_info(state)
        
        # 构建响应数据
        response_data = {
            "session_id": session_id,
            "stage_info": stage_info,
            "results": {}
        }
        
        # 根据当前阶段添加相应的结果
        current_stage = state['current_stage']
        
        if state.get('integrated_report'):
            response_data['results']['integrated_report'] = state['integrated_report']
        
        if state.get('career_goals'):
            response_data['results']['career_goals'] = state['career_goals']
        
        if state.get('final_plan'):
            response_data['results']['final_plan'] = state['final_plan']
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500


@career_bp.route('/feedback/<session_id>', methods=['POST'])
def submit_feedback(session_id):
    """
    提交用户反馈
    
    请求体:
    {
        "satisfaction_level": "satisfied|dissatisfied|neutral|very_satisfied|very_dissatisfied",
        "feedback_text": "string"
    }
    """
    try:
        if session_id not in session_store:
            return jsonify({"error": "会话不存在"}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "请提供反馈数据"}), 400
        
        satisfaction_level_str = data.get('satisfaction_level', 'neutral')
        feedback_text = data.get('feedback_text', '')
        
        # 转换满意度级别
        satisfaction_mapping = {
            'very_satisfied': UserSatisfactionLevel.VERY_SATISFIED,
            'satisfied': UserSatisfactionLevel.SATISFIED,
            'neutral': UserSatisfactionLevel.NEUTRAL,
            'dissatisfied': UserSatisfactionLevel.DISSATISFIED,
            'very_dissatisfied': UserSatisfactionLevel.VERY_DISSATISFIED
        }
        
        satisfaction_level = satisfaction_mapping.get(
            satisfaction_level_str, 
            UserSatisfactionLevel.NEUTRAL
        )
        
        # 获取当前状态
        current_state = session_store[session_id]
        
        # 更新用户反馈
        updated_state = career_graph.update_user_feedback(
            current_state, 
            satisfaction_level, 
            feedback_text
        )
        
        # 如果用户不满意，继续运行工作流
        if satisfaction_level in [UserSatisfactionLevel.DISSATISFIED, UserSatisfactionLevel.VERY_DISSATISFIED]:
            result = career_graph.run_workflow(updated_state)
            
            if result['success']:
                session_store[session_id] = result['final_state']
                stage_info = career_graph.get_current_stage_info(result['final_state'])
                
                return jsonify({
                    "success": True,
                    "message": "反馈已收到，正在重新分析",
                    "stage_info": stage_info
                })
            else:
                return jsonify({
                    "success": False,
                    "error": result['error']
                }), 500
        else:
            # 用户满意，继续下一阶段
            session_store[session_id] = updated_state
            result = career_graph.run_workflow(updated_state)
            
            if result['success']:
                session_store[session_id] = result['final_state']
                stage_info = career_graph.get_current_stage_info(result['final_state'])
                
                return jsonify({
                    "success": True,
                    "message": "反馈已收到，进入下一阶段",
                    "stage_info": stage_info
                })
            else:
                return jsonify({
                    "success": False,
                    "error": result['error']
                }), 500
        
    except Exception as e:
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500


@career_bp.route('/report/<session_id>', methods=['GET'])
def get_report(session_id):
    """
    获取分析报告
    """
    try:
        if session_id not in session_store:
            return jsonify({"error": "会话不存在"}), 404
        
        state = session_store[session_id]
        
        report_data = {
            "session_id": session_id,
            "user_profile": state['user_profile'],
            "integrated_report": state.get('integrated_report'),
            "career_goals": state.get('career_goals'),
            "final_plan": state.get('final_plan'),
            "analysis_results": {
                "self_insight": state.get('self_insight_result'),
                "industry_research": state.get('industry_research_result'),
                "career_analysis": state.get('career_analysis_result')
            },
            "system_metrics": state['system_metrics'],
            "generated_at": datetime.now().isoformat()
        }
        
        return jsonify(report_data)
        
    except Exception as e:
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500


@career_bp.route('/sessions', methods=['GET'])
def list_sessions():
    """
    列出所有会话（用于调试）
    """
    try:
        sessions = []
        for session_id, state in session_store.items():
            sessions.append({
                "session_id": session_id,
                "user_id": state['user_profile']['user_id'],
                "current_stage": state['current_stage'].value,
                "created_at": state['system_metrics']['last_updated'].isoformat()
            })
        
        return jsonify({
            "sessions": sessions,
            "total": len(sessions)
        })
        
    except Exception as e:
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500


@career_bp.route('/health', methods=['GET'])
def health_check():
    """
    健康检查
    """
    return jsonify({
        "status": "healthy",
        "service": "CareerNavigator API",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(session_store)
    })

