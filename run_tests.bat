@echo off
chcp 65001 >nul
:: CareerNavigator Test Quick Start Script
:: Provides simple test execution entry

echo.
echo ========================================
echo   CareerNavigator Quick Test Launcher
echo ========================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found, please ensure Python is installed and added to PATH
    pause
    exit /b 1
)

:: Set project root directory (current directory where the .bat file is located)
cd /d "%~dp0"

echo CareerNavigator Test Suite
echo.
echo Select test mode:
echo.
echo 1. Quick Test (Environment+LLM Service, ~2 minutes)
echo 2. Core Test (Environment+LLM+Workflow, ~5 minutes)  
echo 3. Full Test (Include Integration Tests, ~10 minutes)
echo 4. All Tests (Include Interactive Tests, ~15 minutes)
echo 5. Custom Test (Interactive Selection)
echo 6. Test Manager (Full Features)
echo.

set /p choice="Please select (1-6): "

if "%choice%"=="1" (
    echo.
    echo Starting Quick Test...
    python tests\run_tests.py quick
) else if "%choice%"=="2" (
    echo.
    echo Starting Core Test...
    python tests\run_tests.py core
) else if "%choice%"=="3" (
    echo.
    echo Starting Full Test...
    python tests\run_tests.py full
) else if "%choice%"=="4" (
    echo.
    echo Starting All Tests...
    python tests\run_tests.py all
) else if "%choice%"=="5" (
    echo.
    echo Starting Custom Test...
    python tests\run_tests.py custom
) else if "%choice%"=="6" (
    echo.
    echo Starting Test Manager...
    python tests\run_tests.py
) else (
    echo.
    echo Invalid selection, starting default test manager...
    python tests\run_tests.py
)

echo.
echo Test completed, press any key to exit...
pause >nul
