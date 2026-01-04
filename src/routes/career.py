"""
职业规划API路由
提供RESTful API接口供前端调用
"""

import json
import queue
import threading
import os
import uuid
import asyncio
from flask import Blueprint, request, jsonify, Response, stream_with_context
from datetime import datetime

from src.models.career_state import UserProfile, UserSatisfactionLevel
from src.services.career_graph import career_graph
from mcp_app.paddle_ocr_client import PaddleOCRClient

career_bp = Blueprint('career', __name__)

# 存储会话状态的简单内存存储（生产环境应使用Redis或数据库）
session_store = {}


@career_bp.route('/stream', methods=['GET'])
def stream_career_planning():
    """
    流式获取职业规划进度
    使用 SSE (Server-Sent Events)
    """
    session_id = request.args.get('session_id')
    if not session_id or session_id not in session_store:
        return jsonify({"error": "无效的会话ID"}), 400

    initial_state = session_store[session_id]
    
    def generate():
        q = queue.Queue()
        
        def callback(data):
            q.put(data)
            
        def run_graph():
            try:
                result = career_graph.run_workflow(initial_state, stream_callback=callback)
                if result['success']:
                    session_store[session_id] = result['final_state']
                    # 发送完成信号
                    q.put(json.dumps({"status": "completed", "session_id": session_id}))
                else:
                    q.put(json.dumps({"status": "error", "message": result.get('error', '未知错误')}))
            except Exception as e:
                q.put(json.dumps({"status": "error", "message": str(e)}))
            finally:
                q.put(None) # 结束信号

        # 在后台线程运行工作流
        thread = threading.Thread(target=run_graph)
        thread.start()

        while True:
            data = q.get()
            if data is None:
                break
            yield f"data: {data}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')


@career_bp.route('/upload-resume', methods=['POST'])
def upload_resume():
    """
    上传简历图片并使用 OCR 提取信息
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "没有文件上传"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "未选择文件"}), 400
        
        if file:
            # 确保上传目录存在
            # 路径相对于项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            upload_dir = os.path.join(project_root, 'uploads')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
                
            # 生成唯一文件名
            ext = os.path.splitext(file.filename)[1]
            filename = f"{uuid.uuid4()}{ext}"
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            print(f"文件已保存至: {file_path}")
            
            try:
                # 调用 OCR 客户端
                print("正在初始化 PaddleOCRClient...")
                client = PaddleOCRClient()
                
                # 运行异步任务处理简历
                print("正在启动异步任务处理简历...")
                try:
                    # 尝试获取当前事件循环
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    # 如果没有当前循环，创建一个新的
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                result = loop.run_until_complete(client.process_file(file_path))
                print(f"简历解析完成，结果长度: {len(str(result))}")
                
                # 删除临时文件
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
                if not result:
                    return jsonify({"error": "未能从简历中提取有效信息，请确保图片清晰"}), 422
                    
                return jsonify(result)
            except Exception as e:
                # 发生错误也尝试删除临时文件
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass
                print(f"OCR 处理过程中发生错误: {str(e)}")
                import traceback
                traceback.print_exc()
                return jsonify({"error": f"解析失败: {str(e)}"}), 500
    except Exception as e:
        print(f"上传简历接口发生未捕获错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"服务器内部错误: {str(e)}"}), 500


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
        
        # 立即返回，不在这里运行工作流
        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "会话已创建，准备开始规划"
        })
            
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
        
        if state.get('final_career_plan'):
            response_data['results']['final_career_plan'] = state['final_career_plan']
        elif state.get('final_plan'):
            response_data['results']['final_career_plan'] = state['final_plan']
        
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
        
        # 清除需要用户输入的标志
        from src.models.career_state import StateUpdater
        updated_state.update(StateUpdater.set_user_input_required(updated_state, False))
        
        # 存储更新后的状态
        session_store[session_id] = updated_state
        
        # 立即返回，让前端通过 /stream 接口触发后续流程
        return jsonify({
            "success": True,
            "message": "反馈已收到，正在处理",
            "session_id": session_id
        })
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500


@career_bp.route('/report/<session_id>', methods=['GET'])
def get_full_report(session_id):
    """
    获取完整报告
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
    列出所有会话 (用于调试)
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

