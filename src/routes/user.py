"""
用户管理API路由
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import json

from ..models.user import db, User, CareerSession
from ..utils.logger import api_logger, log_api_request, log_api_response

user_bp = Blueprint('user', __name__)


@user_bp.route('/users', methods=['POST'])
def create_user():
    """创建新用户"""
    log_api_request('POST', '/users', request.get_json())
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "请提供用户数据"}), 400
        
        # 检查用户是否已存在
        existing_user = User.query.filter_by(user_id=data.get('user_id')).first()
        if existing_user:
            response_data = {"message": "用户已存在", "user": existing_user.to_dict()}
            log_api_response('/users', 200, response_data)
            return jsonify(response_data)
        
        # 创建新用户
        user = User(
            user_id=data.get('user_id'),
            email=data.get('email'),
            name=data.get('name'),
            age=data.get('age'),
            education_level=data.get('education_level'),
            work_experience=data.get('work_experience'),
            current_position=data.get('current_position'),
            industry=data.get('industry'),
            location=data.get('location'),
            salary_expectation=data.get('salary_expectation')
        )
        
        db.session.add(user)
        db.session.commit()
        
        response_data = {"message": "用户创建成功", "user": user.to_dict()}
        log_api_response('/users', 201, response_data)
        return jsonify(response_data), 201
        
    except Exception as e:
        api_logger.error("创建用户失败", {"error": str(e)}, exc_info=True)
        log_api_response('/users', 500, {"error": str(e)})
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500


@user_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """获取用户信息"""
    log_api_request('GET', f'/users/{user_id}')
    
    try:
        user = User.query.filter_by(user_id=user_id).first()
        
        if not user:
            response_data = {"error": "用户不存在"}
            log_api_response(f'/users/{user_id}', 404, response_data)
            return jsonify(response_data), 404
        
        response_data = {"user": user.to_dict()}
        log_api_response(f'/users/{user_id}', 200, response_data)
        return jsonify(response_data)
        
    except Exception as e:
        api_logger.error("获取用户失败", {"user_id": user_id, "error": str(e)}, exc_info=True)
        log_api_response(f'/users/{user_id}', 500, {"error": str(e)})
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500


@user_bp.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """更新用户信息"""
    log_api_request('PUT', f'/users/{user_id}', request.get_json())
    
    try:
        data = request.get_json()
        user = User.query.filter_by(user_id=user_id).first()
        
        if not user:
            response_data = {"error": "用户不存在"}
            log_api_response(f'/users/{user_id}', 404, response_data)
            return jsonify(response_data), 404
        
        # 更新用户信息
        for field in ['email', 'name', 'age', 'education_level', 'work_experience', 
                     'current_position', 'industry', 'location', 'salary_expectation']:
            if field in data:
                setattr(user, field, data[field])
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        response_data = {"message": "用户信息更新成功", "user": user.to_dict()}
        log_api_response(f'/users/{user_id}', 200, response_data)
        return jsonify(response_data)
        
    except Exception as e:
        api_logger.error("更新用户失败", {"user_id": user_id, "error": str(e)}, exc_info=True)
        log_api_response(f'/users/{user_id}', 500, {"error": str(e)})
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500


@user_bp.route('/users/<user_id>/sessions', methods=['GET'])
def get_user_sessions(user_id):
    """获取用户的职业规划会话列表"""
    log_api_request('GET', f'/users/{user_id}/sessions')
    
    try:
        sessions = CareerSession.query.filter_by(user_id=user_id).order_by(
            CareerSession.created_at.desc()).all()
        
        sessions_data = [session.to_dict() for session in sessions]
        
        response_data = {
            "sessions": sessions_data,
            "total": len(sessions_data)
        }
        log_api_response(f'/users/{user_id}/sessions', 200, response_data)
        return jsonify(response_data)
        
    except Exception as e:
        api_logger.error("获取用户会话失败", {"user_id": user_id, "error": str(e)}, exc_info=True)
        log_api_response(f'/users/{user_id}/sessions', 500, {"error": str(e)})
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500


@user_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "service": "User API",
        "timestamp": datetime.now().isoformat()
    })
