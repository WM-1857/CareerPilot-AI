"""
CareerNavigator 开发环境启动脚本
"""

import os
import sys
import subprocess
import time
from pathlib import Path


def setup_environment():
    """设置开发环境"""
    print("🔧 设置开发环境...")
    
    # 设置环境变量
    env_vars = {
        'FLASK_ENV': 'development',
        'LOG_LEVEL': 'DEBUG',
        'DASHSCOPE_API_KEY': 'your_api_key_here',  # 需要用户设置
        'HOST': '0.0.0.0',
        'PORT': '5050'
    }
    
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
            print(f"  ✅ 设置环境变量: {key} = {value}")
    
    # 检查API密钥
    if os.environ.get('DASHSCOPE_API_KEY') == 'your_api_key_here':
        print("  ⚠️ 请设置正确的DASHSCOPE_API_KEY环境变量")
        print("  💡 在命令行运行: set DASHSCOPE_API_KEY=your_actual_key")


def check_dependencies():
    """检查依赖"""
    print("📦 检查依赖...")
    
    required_packages = [
        'flask',
        'flask-cors',
        'requests',
        'langgraph',
        'dashscope'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️ 缺少依赖包: {', '.join(missing_packages)}")
        print("💡 请运行: pip install " + " ".join(missing_packages))
        return False
    
    return True


def create_requirements_txt():
    """创建requirements.txt文件"""
    requirements_content = """# CareerNavigator 后端依赖
flask>=3.0.0
flask-cors>=4.0.0
flask-sqlalchemy>=3.0.0
requests>=2.31.0
langgraph>=0.6.0
dashscope>=1.17.0
python-dotenv>=1.0.0

# 开发依赖
pytest>=7.0.0
pytest-cov>=4.0.0
black>=23.0.0
flake8>=6.0.0
"""
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements_content)
    
    print("✅ 创建了 requirements.txt 文件")


def start_backend():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    
    try:
        # 运行主应用
        subprocess.run([sys.executable, 'main.py'], check=True)
    except KeyboardInterrupt:
        print("\n👋 用户中断，停止服务")
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        return False
    
    return True


def run_tests():
    """运行测试"""
    print("🧪 运行测试...")
    
    # 运行组件测试
    try:
        result = subprocess.run([
            sys.executable, 
            'tests/test_components.py'
        ], capture_output=True, text=True)
        
        print("组件测试结果:")
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
            
    except Exception as e:
        print(f"运行组件测试失败: {e}")
    
    # 运行后端API测试（需要服务运行）
    print("\n💡 要运行API测试，请:")
    print("1. 先启动后端服务: python main.py")
    print("2. 然后在另一个终端运行: python tests/test_backend.py")


def show_menu():
    """显示菜单"""
    print("\n" + "="*50)
    print("🎯 CareerNavigator 开发工具")
    print("="*50)
    print("1. 设置开发环境")
    print("2. 检查依赖")
    print("3. 创建requirements.txt")
    print("4. 启动后端服务")
    print("5. 运行组件测试")
    print("6. 显示项目信息")
    print("0. 退出")
    print("-"*50)


def show_project_info():
    """显示项目信息"""
    print("\n📋 项目信息")
    print("-"*30)
    print("项目名称: CareerNavigator")
    print("版本: 1.0.0")
    print("描述: 基于AI的智能职业规划助手")
    print("\n📁 文件结构:")
    print("├── main.py                 # 主应用入口")
    print("├── config/                 # 配置文件")
    print("├── src/                    # 源代码")
    print("│   ├── models/             # 数据模型")
    print("│   ├── services/           # 业务服务")
    print("│   ├── routes/             # API路由")
    print("│   └── utils/              # 工具模块")
    print("├── tests/                  # 测试文件")
    print("├── logs/                   # 日志文件")
    print("└── frontend/               # 前端文件")
    
    print("\n🔗 API端点:")
    print("- GET  /api/health          # 健康检查")
    print("- POST /api/career/start    # 开始职业规划")
    print("- GET  /api/career/status/  # 获取状态")
    print("- POST /api/career/feedback # 提交反馈")


def main():
    """主函数"""
    while True:
        show_menu()
        choice = input("请选择操作 (0-6): ").strip()
        
        if choice == '0':
            print("👋 再见!")
            break
        elif choice == '1':
            setup_environment()
        elif choice == '2':
            check_dependencies()
        elif choice == '3':
            create_requirements_txt()
        elif choice == '4':
            if check_dependencies():
                start_backend()
        elif choice == '5':
            run_tests()
        elif choice == '6':
            show_project_info()
        else:
            print("❌ 无效选择，请重试")
        
        input("\n按Enter键继续...")


if __name__ == "__main__":
    main()
