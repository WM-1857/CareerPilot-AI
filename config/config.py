"""
配置管理
"""

import os
from typing import Optional


class BaseConfig:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # LLM配置
    SPARK_API_KEY = os.environ.get('SPARK_API_KEY') or "Bearer orFKteCwMFcKbowYftHz:OpmCHRrdIjguGUkfFwUk"
    SPARK_API_URL = os.environ.get('SPARK_API_URL') or "https://spark-api-open.xf-yun.com/v1/chat/completions"
    
    # 兼容旧配置名
    DASHSCOPE_API_KEY = SPARK_API_KEY
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_DIR = os.environ.get('LOG_DIR', 'logs')
    
    # CORS配置
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # 会话配置
    SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', '3600'))  # 1小时
    MAX_CONCURRENT_SESSIONS = int(os.environ.get('MAX_CONCURRENT_SESSIONS', '100'))


class DevelopmentConfig(BaseConfig):
    """开发环境配置"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'
    
    # 开发环境CORS
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:5173']


class TestingConfig(BaseConfig):
    """测试环境配置"""
    DEBUG = False
    TESTING = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(BaseConfig):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'WARNING'
    
    # 安全配置
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 更严格的CORS配置
    CORS_ORIGINS = BaseConfig.CORS_ORIGINS if BaseConfig.CORS_ORIGINS != ['*'] else []


# 配置映射
config_mapping = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: Optional[str] = None) -> BaseConfig:
    """获取配置类"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config_mapping.get(config_name, DevelopmentConfig)


# 验证必需的环境变量
def validate_config():
    """验证配置是否完整"""
    required_vars = ['SPARK_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"缺少必需的环境变量: {', '.join(missing_vars)}")
    
    return True
