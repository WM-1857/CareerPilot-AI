"""
用户数据模型
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    name = db.Column(db.String(100), nullable=True)
    
    # 基础信息
    age = db.Column(db.Integer, nullable=True)
    education_level = db.Column(db.String(50), nullable=True)
    work_experience = db.Column(db.Integer, nullable=True)
    current_position = db.Column(db.String(100), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    salary_expectation = db.Column(db.String(50), nullable=True)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email': self.email,
            'name': self.name,
            'age': self.age,
            'education_level': self.education_level,
            'work_experience': self.work_experience,
            'current_position': self.current_position,
            'industry': self.industry,
            'location': self.location,
            'salary_expectation': self.salary_expectation,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CareerSession(db.Model):
    """职业规划会话模型"""
    __tablename__ = 'career_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.String(100), nullable=False)
    
    # 会话状态
    current_stage = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, completed, failed
    
    # 会话数据
    user_profile = db.Column(db.Text, nullable=True)  # JSON格式
    session_data = db.Column(db.Text, nullable=True)  # JSON格式
    results = db.Column(db.Text, nullable=True)  # JSON格式
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'current_stage': self.current_stage,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
