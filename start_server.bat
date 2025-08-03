@echo off
echo CareerNavigator 服务启动脚本
echo ============================

REM 设置环境变量
set DASHSCOPE_API_KEY=sk-4b6f138ba0f74331a6092090b1c7cce1
set FLASK_ENV=development
set LOG_LEVEL=INFO

echo 环境变量设置完成:
echo DASHSCOPE_API_KEY: %DASHSCOPE_API_KEY%
echo FLASK_ENV: %FLASK_ENV%
echo LOG_LEVEL: %LOG_LEVEL%
echo.

echo 启动CareerNavigator后端服务...
echo 服务地址: http://localhost:5050
echo 健康检查: http://localhost:5050/api/health
echo.
echo 按 Ctrl+C 停止服务
echo ============================

python main.py
