@echo off
echo CareerNavigator 环境变量设置脚本
echo ================================

echo 请按照以下步骤设置环境变量:
echo.
echo 1. 访问阿里云百炼控制台: https://dashscope.console.aliyun.com/
echo 2. 登录并获取API密钥
echo 3. 将API密钥填入下面的变量中
echo.

REM 检查是否已设置API密钥
if "%DASHSCOPE_API_KEY%"=="" (
    echo 错误: 未设置 DASHSCOPE_API_KEY 环境变量
    echo.
    echo 请设置环境变量的方法:
    echo.
    echo 方法1 - 临时设置 (仅当前会话有效):
    echo   set DASHSCOPE_API_KEY=your_api_key_here
    echo.
    echo 方法2 - 永久设置 (推荐):
    echo   1. 右键"此电脑" -> 属性 -> 高级系统设置
    echo   2. 环境变量 -> 新建系统变量
    echo   3. 变量名: DASHSCOPE_API_KEY
    echo   4. 变量值: your_api_key_here
    echo.
    echo 方法3 - 修改 start_server.bat:
    echo   将第5行的 set DASHSCOPE_API_KEY=Aliyun_API_KEY
    echo   改为 set DASHSCOPE_API_KEY=your_api_key_here
    echo.
    pause
    exit /b 1
) else (
    echo API密钥已设置: %DASHSCOPE_API_KEY%
    echo.
    echo 现在可以运行 start_server.bat 启动服务
    echo.
)

pause 