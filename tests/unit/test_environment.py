#!/usr/bin/env python3
"""
环境和配置测试模块
测试环境变量、依赖包、配置文件等基础设施
"""

import os
import sys
import time
import importlib.util
from typing import Dict, List, Tuple, Any

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class EnvironmentTester:
    """环境测试器"""
    
    def __init__(self):
        self.results = {}
        
    def print_separator(self, title: str):
        """打印分隔符"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print('='*60)
    
    def print_result(self, test_name: str, success: bool, message: str, details: str = ""):
        """打印测试结果"""
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   📝 {details}")
        self.results[test_name] = {"success": success, "message": message, "details": details}
        return success
    
    def test_environment_variables(self) -> bool:
        """测试环境变量"""
        print("\n🔧 测试环境变量...")
        
        required_vars = [
            ("DASHSCOPE_API_KEY", "阿里云百炼API密钥"),
            ("FLASK_ENV", "Flask环境设置"),
            ("LOG_LEVEL", "日志级别")
        ]
        
        all_success = True
        
        for var_name, description in required_vars:
            value = os.getenv(var_name)
            if not value:
                all_success = self.print_result(
                    f"环境变量_{var_name}", 
                    False, 
                    f"未设置{description}",
                    f"请在.env文件中设置 {var_name}"
                ) and all_success
            elif var_name == "DASHSCOPE_API_KEY" and value == "your_actual_dashscope_api_key_here":
                all_success = self.print_result(
                    f"环境变量_{var_name}", 
                    False, 
                    "API密钥为占位符",
                    "请设置真实的API密钥"
                ) and all_success
            else:
                display_value = value[:10] + "..." if len(value) > 10 else value
                all_success = self.print_result(
                    f"环境变量_{var_name}", 
                    True, 
                    f"{description}已设置",
                    f"值: {display_value}"
                ) and all_success
        
        return all_success
    
    def test_dependencies(self) -> bool:
        """测试依赖包"""
        print("\n📦 测试依赖包...")
        
        dependencies = [
            ("flask", "Flask Web框架"),
            ("dashscope", "阿里云百炼SDK"),
            ("langgraph", "LangGraph工作流框架"),
            ("langchain_core", "LangChain核心库"),
            ("requests", "HTTP请求库"),
            ("python-dotenv", "环境变量加载"),
            ("pydantic", "数据验证库")
        ]
        
        all_success = True
        
        for package, description in dependencies:
            try:
                spec = importlib.util.find_spec(package)
                if spec is not None:
                    # 尝试导入以确保包可用
                    module = importlib.import_module(package)
                    version = getattr(module, '__version__', 'unknown')
                    all_success = self.print_result(
                        f"依赖_{package}", 
                        True, 
                        f"{description}可用",
                        f"版本: {version}"
                    ) and all_success
                else:
                    all_success = self.print_result(
                        f"依赖_{package}", 
                        False, 
                        f"{description}未安装",
                        f"请运行: pip install {package}"
                    ) and all_success
            except Exception as e:
                all_success = self.print_result(
                    f"依赖_{package}", 
                    False, 
                    f"{description}导入失败",
                    f"错误: {str(e)}"
                ) and all_success
        
        return all_success
    
    def test_project_structure(self) -> bool:
        """测试项目结构"""
        print("\n📁 测试项目结构...")
        
        required_dirs = [
            ("src", "源代码目录"),
            ("src/models", "数据模型目录"),
            ("src/services", "服务模块目录"),
            ("src/routes", "路由模块目录"),
            ("src/utils", "工具模块目录"),
            ("config", "配置目录"),
            ("docs", "文档目录"),
            ("logs", "日志目录")
        ]
        
        required_files = [
            ("src/models/career_state.py", "职业状态模型"),
            ("src/services/career_graph.py", "职业规划图服务"),
            ("src/services/career_nodes.py", "职业规划节点"),
            ("src/services/llm_service.py", "LLM服务"),
            ("config/config.py", "配置文件"),
            ("main.py", "主启动文件"),
            (".env", "环境变量文件")
        ]
        
        all_success = True
        project_root = os.path.dirname(os.path.dirname(__file__))
        
        # 检查目录
        for dir_path, description in required_dirs:
            full_path = os.path.join(project_root, dir_path)
            if os.path.isdir(full_path):
                all_success = self.print_result(
                    f"目录_{dir_path}", 
                    True, 
                    f"{description}存在",
                    f"路径: {full_path}"
                ) and all_success
            else:
                all_success = self.print_result(
                    f"目录_{dir_path}", 
                    False, 
                    f"{description}不存在",
                    f"路径: {full_path}"
                ) and all_success
        
        # 检查文件
        for file_path, description in required_files:
            full_path = os.path.join(project_root, file_path)
            if os.path.isfile(full_path):
                file_size = os.path.getsize(full_path)
                all_success = self.print_result(
                    f"文件_{file_path}", 
                    True, 
                    f"{description}存在",
                    f"大小: {file_size} bytes"
                ) and all_success
            else:
                all_success = self.print_result(
                    f"文件_{file_path}", 
                    False, 
                    f"{description}不存在",
                    f"路径: {full_path}"
                ) and all_success
        
        return all_success
    
    def test_module_imports(self) -> bool:
        """测试模块导入"""
        print("\n🔍 测试模块导入...")
        
        modules_to_test = [
            ("config.config", "配置模块"),
            ("src.utils.logger", "日志模块"),
            ("src.models.career_state", "状态模型"),
            ("src.services.llm_service", "LLM服务"),
            ("src.services.career_graph", "职业规划图"),
            ("src.services.career_nodes", "职业规划节点"),
        ]
        
        all_success = True
        
        for module_name, description in modules_to_test:
            try:
                module = importlib.import_module(module_name)
                
                # 检查关键类/函数是否存在
                key_items = self._get_expected_items(module_name)
                missing_items = []
                
                for item in key_items:
                    if not hasattr(module, item):
                        missing_items.append(item)
                
                if missing_items:
                    all_success = self.print_result(
                        f"模块_{module_name}", 
                        False, 
                        f"{description}导入成功但缺少关键项",
                        f"缺少: {', '.join(missing_items)}"
                    ) and all_success
                else:
                    all_success = self.print_result(
                        f"模块_{module_name}", 
                        True, 
                        f"{description}导入成功",
                        f"包含所有必要项: {', '.join(key_items)}"
                    ) and all_success
                    
            except ImportError as e:
                all_success = self.print_result(
                    f"模块_{module_name}", 
                    False, 
                    f"{description}导入失败",
                    f"错误: {str(e)}"
                ) and all_success
            except Exception as e:
                all_success = self.print_result(
                    f"模块_{module_name}", 
                    False, 
                    f"{description}导入异常",
                    f"错误: {str(e)}"
                ) and all_success
        
        return all_success
    
    def _get_expected_items(self, module_name: str) -> List[str]:
        """获取模块应包含的关键项"""
        expected_items = {
            "config.config": ["get_config", "validate_config"],
            "src.utils.logger": ["main_logger", "CareerNavigatorLogger"],
            "src.models.career_state": ["CareerNavigatorState", "WorkflowStage", "create_initial_state"],
            "src.services.llm_service": ["llm_service", "call_mcp_api"],
            "src.services.career_graph": ["CareerNavigatorGraph"],
            "src.services.career_nodes": ["coordinator_node", "planner_node", "supervisor_node"]
        }
        return expected_items.get(module_name, [])
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        self.print_separator("CareerNavigator 环境配置测试")
        
        print("🚀 开始环境测试...")
        start_time = time.time()
        
        # 运行各项测试
        env_result = self.test_environment_variables()
        deps_result = self.test_dependencies()
        structure_result = self.test_project_structure()
        imports_result = self.test_module_imports()
        
        # 汇总结果
        end_time = time.time()
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r["success"])
        
        self.print_separator("测试结果汇总")
        print(f"📊 总测试数: {total_tests}")
        print(f"✅ 通过: {passed_tests}")
        print(f"❌ 失败: {total_tests - passed_tests}")
        print(f"⏱️ 耗时: {end_time - start_time:.2f}秒")
        
        overall_success = all([env_result, deps_result, structure_result, imports_result])
        
        if overall_success:
            print("\n🎉 所有环境测试通过！系统准备就绪。")
        else:
            print("\n⚠️ 存在环境问题，请根据上述信息进行修复。")
        
        return {
            "overall_success": overall_success,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "duration": end_time - start_time,
            "details": self.results
        }


def main():
    """主函数"""
    import time
    
    tester = EnvironmentTester()
    results = tester.run_all_tests()
    
    # 返回退出码
    exit_code = 0 if results["overall_success"] else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
