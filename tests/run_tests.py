#!/usr/bin/env python3
"""
CareerNavigator 测试套件管理器
统一管理和执行所有测试模块
"""

import os
import sys
import time
import subprocess
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))


class TestSuiteManager:
    """测试套件管理器"""
    
    def __init__(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.test_dir)
        self.results = {}
        
        # 定义测试模块
        self.test_modules = {
            "environment": {
                "path": "tests/unit/test_environment.py",
                "name": "环境配置测试",
                "description": "测试环境变量、依赖包、项目结构",
                "category": "基础",
                "required": True
            },
            "llm_service": {
                "path": "tests/unit/test_llm_service.py", 
                "name": "LLM服务测试",
                "description": "测试阿里云百炼API连接和响应",
                "category": "服务",
                "required": True
            },
            "langgraph": {
                "path": "tests/unit/test_langgraph.py",
                "name": "LangGraph工作流测试", 
                "description": "测试工作流节点和状态管理",
                "category": "核心",
                "required": True
            },
            "integration": {
                "path": "tests/integration/test_workflow.py",
                "name": "集成测试",
                "description": "测试端到端工作流集成",
                "category": "集成",
                "required": False
            },
            "interactive": {
                "path": "tests/e2e/test_interactive.py",
                "name": "交互式端到端测试",
                "description": "测试完整用户交互流程",
                "category": "端到端",
                "required": False
            }
        }
        
        # 测试套件定义
        self.test_suites = {
            "quick": {
                "name": "快速测试",
                "description": "运行基础环境和服务测试",
                "modules": ["environment", "llm_service"]
            },
            "core": {
                "name": "核心测试", 
                "description": "运行所有单元测试",
                "modules": ["environment", "llm_service", "langgraph"]
            },
            "full": {
                "name": "完整测试",
                "description": "运行所有测试包括集成测试", 
                "modules": ["environment", "llm_service", "langgraph", "integration"]
            },
            "all": {
                "name": "全部测试",
                "description": "运行所有测试包括交互式测试",
                "modules": ["environment", "llm_service", "langgraph", "integration", "interactive"]
            }
        }
    
    def print_separator(self, title: str):
        """打印分隔符"""
        print(f"\n{'='*80}")
        print(f"  {title}")
        print('='*80)
    
    def print_banner(self):
        """打印测试横幅"""
        print("🤖 CareerNavigator 测试套件管理器")
        print("=" * 80)
        print("统一管理和执行所有测试模块")
        print("确保系统各个组件正常工作")
        print("=" * 80)
    
    def show_available_options(self):
        """显示可用的测试选项"""
        print("\n📋 可用测试套件:")
        for suite_id, suite_info in self.test_suites.items():
            modules_str = ", ".join(suite_info["modules"])
            print(f"  {suite_id}: {suite_info['name']}")
            print(f"      {suite_info['description']}")
            print(f"      包含模块: {modules_str}")
            print()
        
        print("📦 可用测试模块:")
        for module_id, module_info in self.test_modules.items():
            required_str = "必需" if module_info["required"] else "可选"
            print(f"  {module_id}: {module_info['name']} ({module_info['category']}, {required_str})")
            print(f"      {module_info['description']}")
            print()
    
    def select_tests(self) -> List[str]:
        """选择要运行的测试"""
        self.show_available_options()
        
        print("🎯 选择测试模式:")
        print("1. 输入套件名称 (quick/core/full/all)")
        print("2. 输入模块名称 (environment/llm_service/langgraph/integration/interactive)")
        print("3. 输入多个模块名称，用逗号分隔")
        print("4. 输入 'custom' 进行自定义选择")
        
        while True:
            try:
                selection = input("\n请输入选择: ").strip().lower()
                
                if selection in self.test_suites:
                    modules = self.test_suites[selection]["modules"]
                    print(f"✅ 选择了套件 '{selection}': {self.test_suites[selection]['name']}")
                    print(f"包含模块: {', '.join(modules)}")
                    return modules
                
                elif selection in self.test_modules:
                    print(f"✅ 选择了模块 '{selection}': {self.test_modules[selection]['name']}")
                    return [selection]
                
                elif ',' in selection:
                    modules = [m.strip() for m in selection.split(',') if m.strip()]
                    invalid_modules = [m for m in modules if m not in self.test_modules]
                    
                    if invalid_modules:
                        print(f"❌ 无效模块: {invalid_modules}")
                        continue
                    
                    print(f"✅ 选择了多个模块: {', '.join(modules)}")
                    return modules
                
                elif selection == 'custom':
                    return self._custom_selection()
                
                else:
                    print("❌ 无效选择，请重新输入")
                    
            except KeyboardInterrupt:
                print("\n👋 测试被用户中断")
                sys.exit(0)
    
    def _custom_selection(self) -> List[str]:
        """自定义选择测试模块"""
        print("\n🎛️ 自定义测试选择:")
        selected_modules = []
        
        for module_id, module_info in self.test_modules.items():
            required_str = " (必需)" if module_info["required"] else ""
            default = "Y" if module_info["required"] else "n"
            
            prompt = f"运行 {module_info['name']}{required_str}? (Y/n): "
            
            while True:
                try:
                    choice = input(prompt).strip().lower()
                    if choice == '' or choice in ['y', 'yes']:
                        selected_modules.append(module_id)
                        print(f"  ✅ 已选择: {module_info['name']}")
                        break
                    elif choice in ['n', 'no']:
                        if module_info["required"]:
                            print(f"  ⚠️ {module_info['name']} 是必需的，已自动选择")
                            selected_modules.append(module_id)
                        else:
                            print(f"  ⏭️ 跳过: {module_info['name']}")
                        break
                    else:
                        print("  ❌ 请输入 y/yes 或 n/no")
                except KeyboardInterrupt:
                    print("\n👋 自定义选择被中断")
                    sys.exit(0)
        
        return selected_modules
    
    def run_test_module(self, module_id: str) -> Dict[str, Any]:
        """运行单个测试模块"""
        module_info = self.test_modules[module_id]
        test_path = os.path.join(self.project_root, module_info["path"])
        
        print(f"\n🧪 运行测试: {module_info['name']}")
        print(f"📁 路径: {module_info['path']}")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            # 运行测试模块
            result = subprocess.run(
                [sys.executable, test_path],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # 解析结果
            success = result.returncode == 0
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            
            # 显示输出
            if stdout:
                print(stdout)
            if stderr and not success:
                print(f"\n❌ 错误输出:\n{stderr}")
            
            test_result = {
                "module_id": module_id,
                "module_name": module_info["name"],
                "success": success,
                "duration": duration,
                "return_code": result.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "timestamp": datetime.now().isoformat()
            }
            
            if success:
                print(f"\n✅ {module_info['name']} 测试通过 ({duration:.2f}秒)")
            else:
                print(f"\n❌ {module_info['name']} 测试失败 ({duration:.2f}秒)")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"\n⏰ {module_info['name']} 测试超时 ({duration:.2f}秒)")
            
            return {
                "module_id": module_id,
                "module_name": module_info["name"],
                "success": False,
                "duration": duration,
                "return_code": -1,
                "stdout": "",
                "stderr": "测试超时",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"\n💥 {module_info['name']} 测试异常: {str(e)}")
            
            return {
                "module_id": module_id,
                "module_name": module_info["name"],
                "success": False,
                "duration": duration,
                "return_code": -2,
                "stdout": "",
                "stderr": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_tests(self, modules: List[str]) -> Dict[str, Any]:
        """运行选定的测试模块"""
        self.print_separator(f"执行测试 - 共{len(modules)}个模块")
        
        overall_start_time = time.time()
        module_results = []
        
        for i, module_id in enumerate(modules, 1):
            print(f"\n🔄 进度: {i}/{len(modules)}")
            result = self.run_test_module(module_id)
            module_results.append(result)
            self.results[module_id] = result
        
        overall_end_time = time.time()
        overall_duration = overall_end_time - overall_start_time
        
        # 汇总结果
        passed_tests = sum(1 for r in module_results if r["success"])
        failed_tests = len(module_results) - passed_tests
        
        overall_success = failed_tests == 0
        
        summary = {
            "overall_success": overall_success,
            "total_modules": len(modules),
            "passed_modules": passed_tests,
            "failed_modules": failed_tests,
            "overall_duration": overall_duration,
            "module_results": module_results,
            "timestamp": datetime.now().isoformat()
        }
        
        return summary
    
    def display_summary(self, summary: Dict[str, Any]):
        """显示测试汇总"""
        self.print_separator("测试结果汇总")
        
        print(f"📊 总体结果: {'✅ 全部通过' if summary['overall_success'] else '❌ 有失败'}")
        print(f"📈 模块统计: {summary['passed_modules']}/{summary['total_modules']} 通过")
        print(f"⏱️ 总用时: {summary['overall_duration']:.2f}秒")
        print(f"📅 测试时间: {summary['timestamp']}")
        
        print(f"\n📋 详细结果:")
        for result in summary["module_results"]:
            status = "✅" if result["success"] else "❌"
            duration = result["duration"]
            print(f"  {status} {result['module_name']} ({duration:.2f}秒)")
            if not result["success"] and result["stderr"]:
                print(f"     💬 错误: {result['stderr'][:100]}...")
        
        if summary["failed_modules"] > 0:
            print(f"\n⚠️ 有 {summary['failed_modules']} 个模块测试失败")
            print("建议:")
            print("1. 检查失败模块的详细错误信息")
            print("2. 确认环境配置和依赖是否正确")
            print("3. 逐个运行失败的测试模块进行调试")
        else:
            print(f"\n🎉 恭喜！所有测试模块都已通过")
            print("系统已准备就绪，可以正常使用")
    
    def save_results(self, summary: Dict[str, Any]):
        """保存测试结果"""
        results_dir = os.path.join(self.project_root, "tests", "results")
        os.makedirs(results_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(results_dir, f"test_results_{timestamp}.json")
        
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 测试结果已保存: {results_file}")
            
        except Exception as e:
            print(f"\n⚠️ 保存测试结果失败: {e}")
    
    def run(self):
        """运行测试套件管理器"""
        self.print_banner()
        
        try:
            # 选择测试
            selected_modules = self.select_tests()
            
            if not selected_modules:
                print("⚠️ 未选择任何测试模块")
                return
            
            # 确认运行
            modules_str = ", ".join([self.test_modules[m]["name"] for m in selected_modules])
            print(f"\n📋 即将运行测试:")
            print(f"   {modules_str}")
            
            confirm = input("\n继续执行？(Y/n): ").strip().lower()
            if confirm not in ['', 'y', 'yes']:
                print("👋 测试已取消")
                return
            
            # 运行测试
            summary = self.run_tests(selected_modules)
            
            # 显示结果
            self.display_summary(summary)
            
            # 保存结果
            self.save_results(summary)
            
            # 返回退出码
            exit_code = 0 if summary["overall_success"] else 1
            sys.exit(exit_code)
            
        except KeyboardInterrupt:
            print("\n\n👋 测试被用户中断")
            sys.exit(1)
        except Exception as e:
            print(f"\n💥 测试管理器异常: {e}")
            sys.exit(1)


def main():
    """主函数"""
    manager = TestSuiteManager()
    manager.run()


if __name__ == "__main__":
    main()
