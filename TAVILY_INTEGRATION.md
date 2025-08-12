# Tavily搜索工具集成说明

## 概述

本项目已成功集成Tavily搜索工具，用于获取最新的行业和职位信息，替代了原来的模拟数据。

## 集成内容

### 1. 配置文件
- `searchsrc/config.py`: Tavily API配置
- `decorators.py`: 日志装饰器

### 2. 主要功能

#### A. 用户画像分析 (`user_profile_analysis`)
```python
# 搜索用户画像相关的职业测评信息
search_query = f"职业测评 个人能力分析 {current_position}"
```

**功能**：
- 分析用户的核心优势
- 识别需要改进的方面
- 评估性格特质
- 分析技术技能和软技能
- 识别技能缺口

#### B. 行业数据 (`industry_data`)
```python
# 搜索行业趋势和薪资数据
search_query = f"{target_industry} 行业趋势 薪资水平 2024"
```

**功能**：
- 获取行业发展趋势
- 分析薪资水平
- 识别重点企业
- 评估就业前景

#### C. 职位市场 (`job_market`)
```python
# 搜索职位市场信息
search_query = f"{target_career} 职位要求 薪资 招聘 2024"
```

**功能**：
- 获取职位要求
- 分析薪资范围
- 评估市场需求
- 识别技能要求

### 3. 数据提取函数

项目包含多个数据提取函数：

- `extract_strengths_from_search()`: 提取优势
- `extract_weaknesses_from_search()`: 提取劣势
- `extract_personality_from_search()`: 提取性格特质
- `extract_technical_skills()`: 提取技术技能
- `extract_soft_skills()`: 提取软技能
- `extract_skill_gaps()`: 提取技能缺口
- `extract_industry_trends()`: 提取行业趋势
- `extract_salary_ranges()`: 提取薪资范围
- `extract_job_market_data()`: 提取职位市场数据

## 使用方法

### 1. 环境变量设置

在启动脚本中设置API密钥：

```batch
set DASHSCOPE_API_KEY=your_dashscope_api_key
set TAVILY_API_KEY=your_tavily_api_key
```

### 2. 在代码中使用

```python
from src.services.llm_service import call_mcp_api

# 调用用户画像分析
result = call_mcp_api("user_profile_analysis", {
    "user_profile": user_profile
})

# 调用行业数据
result = call_mcp_api("industry_data", {
    "target_industry": "AI行业"
})

# 调用职位市场
result = call_mcp_api("job_market", {
    "target_career": "产品经理"
})
```

### 3. 测试集成

运行测试脚本：

```bash
python test_tavily_integration.py
```

## 返回数据格式

### 用户画像分析
```json
{
    "profile": {
        "strengths": ["沟通能力强", "学习能力强", "团队协作"],
        "weaknesses": ["编程经验不足", "行业经验有限"],
        "personality_traits": ["外向", "创新", "责任心强"],
        "skill_assessment": {
            "technical_skills": ["Python基础", "数据分析"],
            "soft_skills": ["项目管理", "演讲能力"],
            "skill_gaps": ["机器学习", "产品设计"]
        }
    },
    "data_sources": ["https://example.com/source1", "https://example.com/source2"]
}
```

### 行业数据
```json
{
    "trends": [
        {"name": "人工智能", "growth": 0.25, "outlook": "非常积极"},
        {"name": "数据科学", "growth": 0.20, "outlook": "积极"}
    ],
    "salary_ranges": {
        "AI产品经理": {"entry": "15-25k", "mid": "25-40k", "senior": "40-80k"}
    },
    "data_sources": ["https://example.com/industry1", "https://example.com/industry2"]
}
```

### 职位市场
```json
{
    "jobs": [
        {
            "title": "AI产品经理",
            "salary": "25-40k",
            "demand": "高",
            "requirements": ["产品思维", "技术理解", "数据分析"]
        }
    ],
    "data_sources": ["https://example.com/job1", "https://example.com/job2"]
}
```

## 错误处理

系统包含完整的错误处理机制：

1. **API调用失败**: 记录错误日志并返回错误信息
2. **数据解析失败**: 提供默认数据作为备选
3. **网络异常**: 捕获异常并提供友好的错误信息

## 日志记录

使用 `decorators.py` 中的日志装饰器记录：

- API调用参数
- 返回结果
- 错误信息
- 性能指标

## 优势

1. **实时数据**: 获取最新的行业和职位信息
2. **多源数据**: 从多个网站获取数据
3. **结构化输出**: 提供结构化的分析结果
4. **错误恢复**: 完善的错误处理机制
5. **日志追踪**: 完整的操作日志记录

## 注意事项

1. **API限制**: 注意Tavily API的调用限制
2. **数据质量**: 搜索结果的质量取决于搜索查询的准确性
3. **网络依赖**: 需要稳定的网络连接
4. **成本控制**: 监控API调用成本

## 未来改进

1. **智能搜索**: 优化搜索查询策略
2. **数据缓存**: 实现数据缓存机制
3. **NLP增强**: 使用更复杂的NLP技术提取信息
4. **多语言支持**: 支持多语言搜索
5. **数据验证**: 增加数据质量验证机制 