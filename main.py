import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, g
from flask_cors import CORS
from datetime import datetime
import time

# 导入配置和日志
from config.config import get_config, validate_config
from src.routes.career import career_bp
from src.utils.logger import main_logger, api_logger, log_api_request, log_api_response
from interactive_workflow import InteractiveWorkflowRunner

# 验证配置
try:
    validate_config()
    main_logger.info("✅ 配置验证通过")
except ValueError as e:
    main_logger.error(f"❌ 配置验证失败: {str(e)}")
    # 在开发环境继续运行，生产环境退出
    if os.environ.get('FLASK_ENV') == 'production':
        sys.exit(1)

# 获取配置
config = get_config()
main_logger.info(f"📋 使用配置: {config.__class__.__name__}")

# 创建Flask应用
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'frontend'))
app.config.from_object(config)

main_logger.info(f"🚀 CareerNavigator后端启动中...")
main_logger.info(f"📊 调试模式: {app.config['DEBUG']}")
main_logger.info(f"📝 日志级别: {app.config['LOG_LEVEL']}")
main_logger.info(f"📁 静态文件夹: {app.static_folder}")

# 启用CORS支持
CORS(app, origins=app.config['CORS_ORIGINS'])
main_logger.info(f"🌐 CORS配置: {app.config['CORS_ORIGINS']}")

# 请求前后的日志记录
@app.before_request
def before_request():
    """请求前的处理"""
    g.start_time = time.time()
    
    # 记录API请求（排除静态文件）
    if not request.path.startswith('/static'):
        log_api_request(request.method, request.path, request.get_json(silent=True))

@app.after_request
def after_request(response):
    """请求后的处理"""
    # 计算请求时间
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        response.headers['X-Response-Time'] = f"{duration:.3f}s"
        
        # 记录API响应（排除静态文件）
        if not request.path.startswith('/static'):
            try:
                response_data = response.get_json() if response.is_json else None
            except:
                response_data = None
            
            log_api_response(request.path, response.status_code, {
                "response_time": f"{duration:.3f}s",
                "content_length": response.content_length
            })
    
    return response

# 注册蓝图
app.register_blueprint(career_bp, url_prefix='/api/career')
main_logger.info("📚 API蓝图注册完成")

main_logger.info("� 无数据库模式，跳过数据库初始化")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """静态文件服务"""
    static_folder_path = app.static_folder
    main_logger.debug(f"📂 请求路径: '{path}', 静态文件夹: {static_folder_path}")
    
    if static_folder_path is None:
        main_logger.warning("📁 静态文件夹未配置")
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        main_logger.debug(f"📄 提供静态文件: {path}")
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        main_logger.debug(f"📄 检查index.html路径: {index_path}")
        if os.path.exists(index_path):
            main_logger.debug("📄 提供index.html")
            return send_from_directory(static_folder_path, 'index.html')
        else:
            main_logger.warning(f"📄 文件未找到: {path}, index.html路径: {index_path}")
            return "index.html not found", 404


@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    main_logger.warning(f"❌ 404错误: {request.path}")
    return {"error": "资源未找到", "path": request.path}, 404


@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    main_logger.error(f"❌ 500错误: {str(error)}", exc_info=True)
    return {"error": "服务器内部错误", "message": str(error)}, 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """系统健康检查"""
    health_data = {
        "status": "healthy",
        "service": "CareerNavigator Backend",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "healthy",
            "memory_storage": "healthy"
        },
        "environment": os.environ.get('FLASK_ENV', 'development')
    }
    
    main_logger.info("💓 健康检查完成", health_data)
    return health_data


if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5050))
    debug = app.config['DEBUG']
    
    main_logger.info(f"🌟 CareerNavigator后端启动完成")
    main_logger.info(f"🔗 服务地址: http://{host}:{port}")
    main_logger.info(f"🔧 调试模式: {'开启' if debug else '关闭'}")
    
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        main_logger.info("👋 用户中断，服务器关闭")
    except Exception as e:
        main_logger.error(f"❌ 服务器启动失败: {str(e)}", exc_info=True)
