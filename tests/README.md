# CareerNavigator 测试套件使用指南

## 概述

CareerNavigator 测试套件是一个模块化、分层次的测试框架，用于确保系统各个组件的正常工作。测试套件包含从环境配置到端到端用户交互的完整测试覆盖。

## 测试架构

### 测试分层结构

```
tests/
├── unit/                    # 单元测试
│   ├── test_environment_win.py     # 环境配置测试 (Windows兼容版)
│   ├── test_llm_service_win.py     # LLM服务测试 (Windows兼容版)
│   └── test_langgraph_win.py       # LangGraph工作流测试 (Windows兼容版)
├── integration/             # 集成测试
│   └── test_workflow.py        # 端到端工作流集成测试
├── e2e/                     # 端到端测试
│   └── test_interactive.py     # 交互式用户测试
├── results/                 # 测试结果存储
└── run_tests.py            # 测试套件管理器
```

> **📝 注意**: Windows兼容版本（`*_win.py`）解决了控制台编码和模块导入问题，提供更好的Windows环境支持。推荐在Windows系统上使用这些版本。

### 测试模块说明

#### 1. 环境配置测试 (`test_environment_win.py`)
- **目的**: 验证系统运行环境
- **测试内容**:
  - 环境变量配置 (API密钥等)
  - Python依赖包安装
  - 项目文件结构完整性
  - 配置文件有效性

#### 2. LLM服务测试 (`test_llm_service_win.py`)
- **目的**: 验证大语言模型服务连接
- **测试内容**:
  - 阿里云百炼API连接
  - API密钥有效性
  - 服务响应质量
  - 错误处理机制

#### 3. LangGraph工作流测试 (`test_langgraph_win.py`)
- **目的**: 验证工作流节点和状态管理
- **测试内容**:
  - 工作流图构建
  - 各节点功能验证
  - 状态转换机制
  - 条件路由逻辑

#### 4. 集成测试 (`test_workflow.py`)
- **目的**: 验证完整工作流集成
- **测试内容**:
  - 端到端工作流执行
  - 多节点协调工作
  - 状态一致性
  - 错误恢复机制

#### 5. 交互式端到端测试 (`test_interactive.py`)
- **目的**: 验证用户交互体验
- **测试内容**:
  - 用户输入处理
  - 交互式对话流程
  - 结果展示质量
  - 用户体验完整性

## 使用方法

### 1. 快速开始

#### 运行测试套件管理器
```bash
cd h:\projects\coach
python tests\run_tests.py
```

#### 选择预定义测试套件
测试管理器提供4个预定义套件：

1. **quick** - 快速测试
   - 包含: 环境配置 + LLM服务测试
   - 用时: ~2分钟
   - 适用: 快速验证基础功能

2. **core** - 核心测试  
   - 包含: 环境配置 + LLM服务 + LangGraph工作流测试
   - 用时: ~5分钟
   - 适用: 验证核心功能

3. **full** - 完整测试
   - 包含: 所有单元测试 + 集成测试
   - 用时: ~10分钟
   - 适用: 全面功能验证

4. **all** - 全部测试
   - 包含: 所有测试包括交互式测试
   - 用时: ~15分钟
   - 适用: 完整系统验证

### 2. 单独运行测试模块

#### 环境配置测试
```bash
python tests\unit\test_environment_win.py
```

#### LLM服务测试
```bash
python tests\unit\test_llm_service_win.py
```

#### LangGraph工作流测试
```bash
python tests\unit\test_langgraph_win.py
```

#### 集成测试
```bash
python tests\integration\test_workflow.py
```

#### 交互式测试
```bash
python tests\e2e\test_interactive.py
```

### 3. 自定义测试组合

在测试管理器中选择 `custom` 可以自定义测试组合:

```
请输入选择: custom

自定义测试选择:
运行 环境配置测试 (必需)? (Y/n): Y
运行 LLM服务测试 (必需)? (Y/n): Y  
运行 LangGraph工作流测试 (必需)? (Y/n): Y
运行 集成测试? (Y/n): n
运行 交互式端到端测试? (Y/n): Y
```

## 测试结果解读

### 成功示例
```
✅ 环境配置测试 (1.23秒)
✅ LLM服务测试 (2.45秒)
✅ LangGraph工作流测试 (3.67秒)

📊 总体结果: ✅ 全部通过
📈 模块统计: 3/3 通过
⏱️ 总用时: 7.35秒
🎉 恭喜！所有测试模块都已通过
```

### 失败示例
```
✅ 环境配置测试 (1.23秒)
❌ LLM服务测试 (0.89秒)
⏭️ LangGraph工作流测试 (跳过)

📊 总体结果: ❌ 有失败
📈 模块统计: 1/2 通过
⏱️ 总用时: 2.12秒

❌ LLM服务测试 (0.89秒)
   💬 错误: API密钥无效或服务不可用
```

### 结果文件

测试结果会自动保存到 `tests/results/` 目录：
```
tests/results/test_results_20240804_143022.json
```

结果文件包含：
- 测试汇总信息
- 每个模块的详细结果
- 执行时间和时间戳
- 错误详情和调试信息

## 故障排除

### 常见问题及解决方案

#### 1. 环境配置测试失败
**症状**: 
```
❌ 环境变量检查失败: 未找到 DASHSCOPE_API_KEY
```

**解决方案**:
1. 检查 `.env` 文件是否存在
2. 确认环境变量名称正确
3. 验证API密钥有效性

#### 2. LLM服务测试失败
**症状**:
```
❌ LLM服务连接失败: HTTP 403 Forbidden
```

**解决方案**:
1. 验证阿里云百炼API密钥
2. 检查账户余额和配额
3. 确认网络连接正常

#### 3. LangGraph工作流测试失败
**症状**:
```
❌ 工作流节点构建失败: Missing required dependency
```

**解决方案**:
1. 检查 LangGraph 相关依赖
2. 验证工作流定义文件
3. 确认节点配置正确

#### 4. 集成测试超时
**症状**:
```
⏰ 集成测试 测试超时 (300.00秒)
```

**解决方案**:
1. 检查网络连接稳定性
2. 验证API服务响应速度
3. 考虑增加超时设置

### 调试模式

每个测试模块都支持详细输出模式，可以通过修改测试文件中的 `verbose` 参数启用：

```python
# 在测试文件中设置
verbose = True  # 启用详细输出
```

### 日志文件

测试过程中的详细日志会记录到 `logs/` 目录，可以查看具体的错误信息：
- `logs/test_YYYYMMDD.log` - 测试执行日志
- `logs/api_YYYYMMDD.log` - API调用日志
- `logs/llm_YYYYMMDD.log` - LLM服务日志

## 开发指南

### 添加新测试模块

1. **创建测试文件**
   ```python
   # tests/unit/test_new_feature.py
   
   class NewFeatureTester:
       def __init__(self):
           self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
       
       def run_tests(self):
           # 实现测试逻辑
           pass
   
   if __name__ == "__main__":
       tester = NewFeatureTester()
       tester.run_tests()
   ```

2. **注册到测试管理器**
   ```python
   # 在 run_tests.py 的 test_modules 中添加
   "new_feature": {
       "path": "tests/unit/test_new_feature.py",
       "name": "新功能测试",
       "description": "测试新添加的功能",
       "category": "单元",
       "required": False
   }
   ```

### 测试模块规范

1. **输出格式**: 使用表情符号和结构化输出
2. **错误处理**: 提供清晰的错误信息和建议
3. **Mock支持**: 支持模拟模式用于CI/CD
4. **结果验证**: 提供详细的结果验证逻辑

### 持续集成

测试套件设计支持CI/CD流水线：

```yaml
# .github/workflows/test.yml 示例
- name: Run Quick Tests
  run: python tests/run_tests.py quick

- name: Run Core Tests  
  run: python tests/run_tests.py core
```

## 最佳实践

### 1. 测试频率建议
- **开发阶段**: 运行 `quick` 测试
- **功能完成**: 运行 `core` 测试
- **版本发布**: 运行 `full` 测试
- **生产部署**: 运行 `all` 测试

### 2. 性能优化
- 使用Mock模式减少外部依赖
- 并行运行独立测试模块
- 缓存测试结果避免重复执行

### 3. 结果分析
- 关注失败模块的依赖关系
- 分析性能趋势和瓶颈
- 建立测试结果历史追踪

## 总结

CareerNavigator 测试套件提供了完整的测试覆盖，从基础环境配置到复杂的用户交互流程。通过模块化设计和统一管理，确保系统的可靠性和稳定性。

定期运行测试套件可以：
- 早期发现系统问题
- 验证功能正确性  
- 确保部署质量
- 提升用户体验

建议在开发和部署过程中充分利用测试套件，确保 CareerNavigator 系统的高质量交付。
