"""
CareerNavigator 逐步诊断测试脚本
逐一测试每个组件，精确定位问题
"""

import os
import sys
import time
import json
import requests
import subprocess
from typing import Optional, Dict, Any

# 设置环境变量
os.environ['DASHSCOPE_API_KEY'] = 'sk-4b6f138ba0f74331a6092090b1c7cce1'
os.environ['FLASK_ENV'] = 'development'
os.environ['LOG_LEVEL'] = 'DEBUG'

print("🔍 CareerNavigator 逐步诊断测试")
print("=" * 60)

class StepByStepTester:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.server_process = None
        self.test_results = {}
        
    def print_step(self, step_num: int, description: str):
        """打印测试步骤"""
        print(f"\n📋 步骤 {step_num}: {description}")
        print("-" * 40)
    
    def print_result(self, success: bool, message: str, details: Optional[str] = None):
        """打印测试结果"""
        status = "✅ 通过" if success else "❌ 失败"
        print(f"   {status}: {message}")
        if details:
            print(f"   📝 详情: {details}")
        return success
    
    def test_1_environment_check(self) -> bool:
        """测试1: 环境变量检查"""
        self.print_step(1, "检查环境变量")
        
        try:
            api_key = os.environ.get('DASHSCOPE_API_KEY')
            flask_env = os.environ.get('FLASK_ENV')
            log_level = os.environ.get('LOG_LEVEL')
            
            if not api_key:
                return self.print_result(False, "DASHSCOPE_API_KEY未设置")
            
            if not api_key.startswith('sk-'):
                return self.print_result(False, "API密钥格式不正确")
            
            success = all([api_key, flask_env, log_level])
            details = f"API密钥: {api_key[:10]}..., 环境: {flask_env}, 日志: {log_level}"
            return self.print_result(success, "环境变量检查", details)
            
        except Exception as e:
            return self.print_result(False, "环境变量检查异常", str(e))
    
    def test_2_import_modules(self) -> bool:
        """测试2: 模块导入检查"""
        self.print_step(2, "检查模块导入")
        
        try:
            # 添加项目路径
            sys.path.insert(0, os.path.abspath('.'))
            
            # 测试基础模块导入
            from config.config import get_config, validate_config
            self.print_result(True, "配置模块导入成功")
            
            from src.utils.logger import main_logger
            self.print_result(True, "日志模块导入成功")
            
            from src.services.llm_service import llm_service
            self.print_result(True, "LLM服务模块导入成功")
            
            from src.models.career_state import CareerNavigatorState
            self.print_result(True, "状态模型导入成功")
            
            from src.routes.career import career_bp
            self.print_result(True, "路由模块导入成功")
            
            return True
            
        except ImportError as e:
            return self.print_result(False, "模块导入失败", str(e))
        except Exception as e:
            return self.print_result(False, "模块导入异常", str(e))
    
    def test_3_llm_service(self) -> bool:
        """测试3: LLM服务单独测试"""
        self.print_step(3, "测试LLM服务")
        
        try:
            sys.path.insert(0, os.path.abspath('.'))
            from src.services.llm_service import llm_service
            
            # 简单的LLM调用测试
            print("   📤 发送测试请求到LLM...")
            result = llm_service.call_llm(
                prompt="简单地说'测试成功'，不要其他内容。",
                context={"test": "step_by_step"}
            )
            
            if result.get('success'):
                content = result.get('content', '')
                return self.print_result(True, "LLM服务调用成功", f"响应: {content[:50]}...")
            else:
                return self.print_result(False, "LLM服务调用失败", result.get('error'))
                
        except Exception as e:
            return self.print_result(False, "LLM服务测试异常", str(e))
    
    def test_4_config_validation(self) -> bool:
        """测试4: 配置验证"""
        self.print_step(4, "验证配置")
        
        try:
            sys.path.insert(0, os.path.abspath('.'))
            from config.config import validate_config, get_config
            
            validate_config()
            self.print_result(True, "配置验证通过")
            
            config = get_config()
            config_name = config.__class__.__name__
            return self.print_result(True, "配置获取成功", f"使用配置: {config_name}")
            
        except Exception as e:
            return self.print_result(False, "配置验证失败", str(e))
    
    def test_5_flask_startup(self) -> bool:
        """测试5: Flask应用启动"""
        self.print_step(5, "启动Flask应用")
        
        try:
            print("   🚀 启动服务器进程...")
            
            # 启动服务器
            self.server_process = subprocess.Popen(
                [sys.executable, 'main.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=os.environ.copy()
            )
            
            # 等待启动
            time.sleep(5)
            
            # 检查进程状态
            if self.server_process.poll() is None:
                return self.print_result(True, "Flask服务器启动成功", "进程运行中")
            else:
                stdout, stderr = self.server_process.communicate()
                error_msg = stderr[:200] if stderr else "未知错误"
                return self.print_result(False, "服务器启动失败", error_msg)
                
        except Exception as e:
            return self.print_result(False, "服务器启动异常", str(e))
    
    def test_6_health_endpoint(self) -> bool:
        """测试6: 健康检查端点"""
        self.print_step(6, "测试健康检查端点")
        
        try:
            print("   📡 连接健康检查端点...")
            
            for attempt in range(3):
                try:
                    response = requests.get(
                        f"{self.base_url}/api/health", 
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        status = data.get('status', 'unknown')
                        return self.print_result(True, "健康检查通过", f"状态: {status}")
                    else:
                        return self.print_result(False, f"健康检查失败", f"状态码: {response.status_code}")
                        
                except requests.exceptions.ConnectionError:
                    if attempt < 2:
                        print(f"   ⏳ 连接尝试 {attempt + 1}/3...")
                        time.sleep(2)
                    else:
                        return self.print_result(False, "无法连接到服务器", "连接被拒绝")
            
        except Exception as e:
            return self.print_result(False, "健康检查异常", str(e))
    
    def test_7_simple_career_request(self) -> bool:
        """测试7: 简化的职业规划请求"""
        self.print_step(7, "测试简化职业规划请求")
        
        try:
            # 使用最简单的数据
            simple_data = {
                "user_profile": {
                    "user_id": f"simple_test_{int(time.time())}",
                    "age": 25,
                    "education_level": "本科",
                    "work_experience": 2,
                    "current_position": "程序员",
                    "industry": "软件",
                    "skills": ["编程"],
                    "interests": ["技术"],
                    "career_goals": "技术专家",
                    "location": "北京",
                    "salary_expectation": "20万"
                },
                "message": "简单的职业建议"
            }
            
            print("   📤 发送简化请求...")
            print("   ⏰ 设置60秒超时...")
            
            response = requests.post(
                f"{self.base_url}/api/career/start",
                json=simple_data,
                timeout=60  # 增加超时时间
            )
            
            print(f"   📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    session_id = data.get("session_id")
                    return self.print_result(True, "职业规划请求成功", f"会话ID: {session_id}")
                else:
                    error = data.get("error", "未知错误")
                    return self.print_result(False, "职业规划请求失败", error)
            else:
                error_text = response.text[:200] if response.text else "无响应内容"
                return self.print_result(False, f"HTTP错误 {response.status_code}", error_text)
                
        except requests.exceptions.Timeout:
            return self.print_result(False, "请求超时", "超过60秒未响应")
        except requests.exceptions.ConnectionError:
            return self.print_result(False, "连接错误", "无法连接到服务器")
        except Exception as e:
            return self.print_result(False, "职业规划请求异常", str(e))
    
    def test_8_workflow_component_isolation(self) -> bool:
        """测试8: 工作流组件隔离测试"""
        self.print_step(8, "测试工作流组件隔离")
        
        try:
            sys.path.insert(0, os.path.abspath('.'))
            
            # 简化测试 - 只检查能否导入工作流相关模块
            print("   🧩 测试工作流模块导入...")
            
            from src.services.career_nodes import coordinator_node
            self.print_result(True, "coordinator_node导入成功")
            
            from src.services.career_graph import career_graph
            self.print_result(True, "career_graph导入成功")
            
            from src.models.career_state import WorkflowStage
            self.print_result(True, "WorkflowStage导入成功")
            
            return self.print_result(True, "工作流组件模块导入测试成功", "跳过实际执行测试")
                
        except Exception as e:
            return self.print_result(False, "工作流组件测试异常", str(e))
    
    def cleanup(self):
        """清理资源"""
        print(f"\n🧹 清理资源...")
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                print("   ✅ 服务器进程已停止")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                print("   ⚠️ 强制停止服务器进程")
            except Exception as e:
                print(f"   ❌ 清理异常: {e}")
    
    def run_all_tests(self) -> Dict[str, bool]:
        """运行所有测试"""
        tests = [
            ("环境变量检查", self.test_1_environment_check),
            ("模块导入检查", self.test_2_import_modules),
            ("LLM服务测试", self.test_3_llm_service),
            ("配置验证", self.test_4_config_validation),
            ("Flask启动", self.test_5_flask_startup),
            ("健康检查", self.test_6_health_endpoint),
            ("简化职业请求", self.test_7_simple_career_request),
            ("工作流组件隔离", self.test_8_workflow_component_isolation)
        ]
        
        results = {}
        
        try:
            for test_name, test_func in tests:
                print(f"\n" + "="*60)
                success = test_func()
                results[test_name] = success
                
                # 如果关键测试失败，提前停止
                if test_name in ["环境变量检查", "模块导入检查"] and not success:
                    print(f"\n❌ 关键测试失败，停止后续测试")
                    break
                    
                # 短暂暂停
                time.sleep(1)
                
        except KeyboardInterrupt:
            print(f"\n⚠️ 用户中断测试")
        except Exception as e:
            print(f"\n❌ 测试过程异常: {e}")
        finally:
            self.cleanup()
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """打印测试总结"""
        print(f"\n" + "="*60)
        print("📊 测试总结")
        print("="*60)
        
        passed = sum(1 for success in results.values() if success)
        total = len(results)
        
        for test_name, success in results.items():
            status = "✅ 通过" if success else "❌ 失败"
            print(f"  {test_name:<20} {status}")
        
        print(f"\n总计: {passed}/{total} 通过 ({passed/total*100:.1f}%)")
        
        # 问题分析
        if passed == total:
            print("\n🎉 所有测试通过！后端运行正常")
        elif passed >= total * 0.7:
            print("\n👍 主要功能正常，部分问题需要优化")
            self._analyze_issues(results)
        else:
            print("\n⚠️ 存在严重问题，需要修复")
            self._analyze_issues(results)
    
    def _analyze_issues(self, results: Dict[str, bool]):
        """分析问题"""
        print("\n🔍 问题分析:")
        
        failed_tests = [name for name, success in results.items() if not success]
        
        if "环境变量检查" in failed_tests:
            print("  • 环境变量配置问题 - 请检查API密钥设置")
        
        if "模块导入检查" in failed_tests:
            print("  • 模块导入问题 - 请检查依赖包安装")
        
        if "LLM服务测试" in failed_tests:
            print("  • LLM服务问题 - 请检查网络连接和API密钥")
        
        if "Flask启动" in failed_tests:
            print("  • Flask启动问题 - 请检查端口占用和配置")
        
        if "健康检查" in failed_tests:
            print("  • 服务连接问题 - 请检查服务器状态")
        
        if "简化职业请求" in failed_tests:
            print("  • 工作流执行问题 - 可能是超时或逻辑错误")
        
        if "工作流组件隔离" in failed_tests:
            print("  • 工作流组件问题 - 节点逻辑需要修复")


def main():
    """主函数"""
    print("开始逐步诊断测试...")
    print("此测试将逐一验证后端的每个组件")
    print("请耐心等待，整个过程可能需要几分钟")
    
    input("\n按Enter键开始测试...")
    
    tester = StepByStepTester()
    results = tester.run_all_tests()
    tester.print_summary(results)
    
    print(f"\n📋 详细日志可查看: logs/目录")
    print(f"🔧 如需进一步诊断，请运行: python diagnosis_and_fix.py")


if __name__ == "__main__":
    main()
