#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境和配置测试模块（Windows兼容版本）
测试环境变量、依赖包、配置文件等基础设施
"""

import os
import sys
import time
import importlib.util
from typing import Dict, List, Tuple, Any, Optional

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


class EnvironmentTester:
    """环境测试器"""
    
    def __init__(self):
        self.project_root = project_root
        self.results = {}
        self.errors = []
    
    def print_status(self, message: str, success: Optional[bool] = None):
        """打印状态信息"""
        if success is True:
            print(f"[PASS] {message}")
        elif success is False:
            print(f"[FAIL] {message}")
        else:
            print(f"[INFO] {message}")
    
    def test_environment_variables(self) -> bool:
        """测试环境变量配置"""
        print("\n检查环境变量...")
        
        # 检查必需的环境变量
        required_vars = [
            'SPARK_API_KEY',
        ]
        
        optional_vars = [
            'PYTHONPATH',
            'PATH'
        ]
        
        all_good = True
        
        for var in required_vars:
            value = os.getenv(var)
            if value:
                self.print_status(f"环境变量 {var}: 已配置", True)
            else:
                self.print_status(f"环境变量 {var}: 未配置", False)
                self.errors.append(f"缺少必需的环境变量: {var}")
                all_good = False
        
        for var in optional_vars:
            value = os.getenv(var)
            if value:
                self.print_status(f"环境变量 {var}: 已配置", True)
            else:
                self.print_status(f"环境变量 {var}: 未配置（可选）", None)
        
        return all_good
    
    def test_python_dependencies(self) -> bool:
        """测试Python依赖包"""
        print("\n检查Python依赖包...")
        
        required_packages = [
            'requests',
            'python-dotenv',
            'langgraph',
            'langchain',
            'langchain_core'
        ]
        
        optional_packages = [
            'fastapi',
            'uvicorn',
            'pydantic'
        ]
        
        all_good = True
        
        for package in required_packages:
            try:
                __import__(package)
                self.print_status(f"依赖包 {package}: 已安装", True)
            except ImportError:
                self.print_status(f"依赖包 {package}: 未安装", False)
                self.errors.append(f"缺少必需的依赖包: {package}")
                all_good = False
        
        for package in optional_packages:
            try:
                __import__(package)
                self.print_status(f"依赖包 {package}: 已安装", True)
            except ImportError:
                self.print_status(f"依赖包 {package}: 未安装（可选）", None)
        
        return all_good
    
    def test_project_structure(self) -> bool:
        """测试项目文件结构"""
        print("\n检查项目结构...")
        
        required_files = [
            'main.py',
            'config/config.py',
            'src/services/llm_service.py',
            'src/services/career_graph.py',
            'src/services/career_nodes.py'
        ]
        
        required_dirs = [
            'src',
            'src/services',
            'src/models',
            'src/routes',
            'config',
            'logs'
        ]
        
        all_good = True
        
        # 检查目录
        for dir_path in required_dirs:
            full_path = os.path.join(self.project_root, dir_path)
            if os.path.isdir(full_path):
                self.print_status(f"目录 {dir_path}: 存在", True)
            else:
                self.print_status(f"目录 {dir_path}: 不存在", False)
                self.errors.append(f"缺少必需的目录: {dir_path}")
                all_good = False
        
        # 检查文件
        for file_path in required_files:
            full_path = os.path.join(self.project_root, file_path)
            if os.path.isfile(full_path):
                self.print_status(f"文件 {file_path}: 存在", True)
            else:
                self.print_status(f"文件 {file_path}: 不存在", False)
                self.errors.append(f"缺少必需的文件: {file_path}")
                all_good = False
        
        return all_good
    
    def test_config_files(self) -> bool:
        """测试配置文件"""
        print("\n检查配置文件...")
        
        config_files = [
            'config/config.py',
            '.env'
        ]
        
        all_good = True
        
        for config_file in config_files:
            full_path = os.path.join(self.project_root, config_file)
            if os.path.isfile(full_path):
                self.print_status(f"配置文件 {config_file}: 存在", True)
                
                # 尝试读取配置文件
                try:
                    if config_file.endswith('.py'):
                        spec = importlib.util.spec_from_file_location("config", full_path)
                        config_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(config_module)
                        self.print_status(f"配置文件 {config_file}: 语法正确", True)
                    elif config_file.endswith('.env'):
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if 'SPARK_API_KEY' in content:
                                self.print_status(f"配置文件 {config_file}: 包含API密钥", True)
                            else:
                                self.print_status(f"配置文件 {config_file}: 未包含API密钥", False)
                                all_good = False
                except Exception as e:
                    self.print_status(f"配置文件 {config_file}: 读取失败 - {str(e)}", False)
                    self.errors.append(f"配置文件 {config_file} 读取失败: {str(e)}")
                    all_good = False
            else:
                if config_file == '.env':
                    self.print_status(f"配置文件 {config_file}: 不存在（建议创建）", None)
                else:
                    self.print_status(f"配置文件 {config_file}: 不存在", False)
                    self.errors.append(f"缺少配置文件: {config_file}")
                    all_good = False
        
        return all_good
    
    def test_write_permissions(self) -> bool:
        """测试写入权限"""
        print("\n检查写入权限...")
        
        test_dirs = [
            'logs',
            'tests/results'
        ]
        
        all_good = True
        
        for test_dir in test_dirs:
            full_path = os.path.join(self.project_root, test_dir)
            try:
                # 确保目录存在
                os.makedirs(full_path, exist_ok=True)
                
                # 测试写入权限
                test_file = os.path.join(full_path, 'test_write.tmp')
                with open(test_file, 'w') as f:
                    f.write('test')
                
                # 清理测试文件
                os.remove(test_file)
                
                self.print_status(f"目录 {test_dir}: 写入权限正常", True)
                
            except Exception as e:
                self.print_status(f"目录 {test_dir}: 写入权限异常 - {str(e)}", False)
                self.errors.append(f"目录 {test_dir} 写入权限异常: {str(e)}")
                all_good = False
        
        return all_good
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有环境测试"""
        print("开始环境测试...")
        print("=" * 60)
        
        start_time = time.time()
        
        # 运行各项测试
        tests = [
            ("环境变量", self.test_environment_variables),
            ("Python依赖", self.test_python_dependencies),
            ("项目结构", self.test_project_structure),
            ("配置文件", self.test_config_files),
            ("写入权限", self.test_write_permissions)
        ]
        
        results = {}
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n执行测试: {test_name}")
            try:
                result = test_func()
                results[test_name] = result
                if result:
                    passed_tests += 1
            except Exception as e:
                print(f"测试 {test_name} 异常: {str(e)}")
                results[test_name] = False
                self.errors.append(f"测试 {test_name} 异常: {str(e)}")
        
        end_time = time.time()
        
        # 汇总结果
        print("\n" + "=" * 60)
        print("环境测试汇总")
        print("=" * 60)
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {total_tests - passed_tests}")
        print(f"耗时: {end_time - start_time:.2f}秒")
        
        overall_success = passed_tests == total_tests
        
        if overall_success:
            print("\n环境测试全部通过，系统已准备就绪！")
        else:
            print("\n存在环境问题，请根据上述信息进行修复。")
            if self.errors:
                print("\n详细错误信息:")
                for error in self.errors:
                    print(f"  - {error}")
        
        return {
            'success': overall_success,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'duration': end_time - start_time,
            'results': results,
            'errors': self.errors
        }


def main():
    """主函数"""
    tester = EnvironmentTester()
    results = tester.run_all_tests()
    
    # 返回适当的退出码
    exit_code = 0 if results['success'] else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
