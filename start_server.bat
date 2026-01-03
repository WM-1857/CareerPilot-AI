@echo off
echo CareerNavigator 服务启动脚本
echo ============================

REM 设置环境变量
set SPARK_API_KEY=Bearer ELKhwlIPLFySfaiUiJbZ:xRwkBIzxmTJrrephseJo
set SPARK_API_URL=https://spark-api-open.xf-yun.com/v1/chat/completions
set DASHSCOPE_API_KEY=%SPARK_API_KEY%
set TAVILY_API_KEY=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
set FLASK_ENV=development
set LOG_LEVEL=DEBUG

echo 环境变量设置完成:
echo SPARK_API_KEY: %SPARK_API_KEY%
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
