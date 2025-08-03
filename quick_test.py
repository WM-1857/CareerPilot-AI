"""
CareerNavigator 快速验证脚本
验证基本功能是否正常工作
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        # 测试配置模块
        from config.config import get_config, validate_config
        print("  ✅ 配置模块导入成功")
        
        # 测试日志模块
        from src.utils.logger import main_logger, CareerNavigatorLogger
        print("  ✅ 日志模块导入成功")
        
        # 测试状态模块
        from src.models.career_state import WorkflowStage, UserProfile, create_initial_state
        print("  ✅ 状态模块导入成功")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ 导入失败: {e}")
        return False


def test_config():
    """测试配置功能"""
    print("\n⚙️ 测试配置功能...")
    
    try:
        from config.config import get_config
        
        # 测试开发环境配置
        dev_config = get_config('development')
        assert dev_config.DEBUG == True
        print("  ✅ 开发环境配置正确")
        
        # 测试生产环境配置
        prod_config = get_config('production')
        assert prod_config.DEBUG == False
        print("  ✅ 生产环境配置正确")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 配置测试失败: {e}")
        return False


def test_logger():
    """测试日志功能"""
    print("\n📝 测试日志功能...")
    
    try:
        from src.utils.logger import CareerNavigatorLogger, DebugTracker
        
        # 创建日志器
        logger = CareerNavigatorLogger("Test")
        logger.info("测试日志消息")
        print("  ✅ 日志器创建成功")
        
        # 创建调试追踪器
        debug_tracker = DebugTracker(logger)
        debug_tracker.start_session("test_session", {"user_id": "test"})
        print("  ✅ 调试追踪器工作正常")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 日志测试失败: {e}")
        return False


def test_state_management():
    """测试状态管理"""
    print("\n📊 测试状态管理...")
    
    try:
        from src.models.career_state import UserProfile, create_initial_state, WorkflowStage
        
        # 创建用户档案
        user_profile = UserProfile(
            user_id="test_user",
            age=25,
            education_level="本科",
            work_experience=2,
            current_position="软件工程师",
            industry="互联网",
            skills=["Python"],
            interests=["技术管理"],
            career_goals="成为技术leader",
            location="北京",
            salary_expectation="20-30万",
            additional_info={}
        )
        print("  ✅ 用户档案创建成功")
        
        # 创建初始状态
        initial_state = create_initial_state(user_profile, "test_session")
        assert initial_state["current_stage"] == WorkflowStage.INITIAL
        assert initial_state["user_profile"] == user_profile
        print("  ✅ 初始状态创建成功")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 状态管理测试失败: {e}")
        return False


def test_flask_app():
    """测试Flask应用创建"""
    print("\n🌐 测试Flask应用...")
    
    try:
        # 设置测试环境变量
        os.environ['FLASK_ENV'] = 'testing'
        os.environ['DASHSCOPE_API_KEY'] = 'test_key'
        
        from flask import Flask
        from config.config import get_config
        
        # 创建测试应用
        app = Flask(__name__)
        config = get_config('testing')
        app.config.from_object(config)
        
        assert app.config['TESTING'] == True
        print("  ✅ Flask应用创建成功")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Flask应用测试失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 CareerNavigator 快速验证")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_config,
        test_logger,
        test_state_management,
        test_flask_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} 异常: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 验证结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有基本功能验证通过!")
        print("💡 可以尝试启动服务: python main.py")
    else:
        print("⚠️ 部分功能存在问题，请检查错误信息")
        
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
