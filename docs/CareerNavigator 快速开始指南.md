# CareerNavigator 快速开始指南

本指南将帮助您在 Windows 环境下快速启动 CareerNavigator 智能职业规划系统。

## 🚀 一键启动

### 前提条件

确保您的 Windows 系统已安装：
- Python 3.8+
- Git

### 快速部署

1. **克隆项目**
```cmd
git clone <repository-url>
cd CareerNavigator
```

2. **安装依赖**
```cmd
pip install -r requirements.txt
```

3. **设置环境变量（方式一：使用批处理脚本）**
```cmd
start_server.bat
```

**或者手动设置（方式二）**
```cmd
set DASHSCOPE_API_KEY=your_api_key_here
python main.py
```

4. **访问应用**
打开浏览器访问: http://localhost:5050

## 🎯 快速体验

### 1. 填写用户信息
- 年龄: 25
- 学历: 本科
- 工作经验: 3年
- 当前职位: 软件工程师
- 所在行业: 互联网
- 技能标签: Python, React, 数据分析
- 兴趣爱好: 人工智能, 产品设计
- 职业目标: 成为AI产品经理
- 所在地区: 北京
- 薪资期望: 20-30k

### 2. 输入需求
在"您的具体需求"框中输入：
```
我希望从技术转向产品管理方向，请帮我制定详细的职业规划和转型路径。
```

### 3. 开始分析
点击"开始职业规划分析"按钮，系统将：
- 分析您的个人能力画像
- 研究目标行业趋势
- 评估职业匹配度
- 制定发展计划

### 4. 查看结果
系统会生成包含以下内容的报告：
- 执行摘要
- 个人能力分析
- 行业机会分析
- 职业匹配度评估
- 发展建议和行动计划

### 5. 提供反馈
根据分析结果提供反馈：
- 满意：继续下一步目标拆分
- 需要调整：系统会重新分析

## 📋 API 快速测试

### 使用 PowerShell 测试

```powershell
# 1. 开始职业规划
$headers = @{
    "Content-Type" = "application/json"
}

$body = @{
    user_profile = @{
        age = 25
        education_level = "本科"
        work_experience = 3
        current_position = "软件工程师"
        industry = "互联网"
        skills = @("Python", "React")
        interests = @("AI", "产品设计")
        career_goals = "成为AI产品经理"
        location = "北京"
        salary_expectation = "20-30k"
    }
    message = "我希望从技术转向产品管理方向"
} | ConvertTo-Json -Depth 3

Invoke-RestMethod -Uri "http://localhost:5050/api/career/start" -Method POST -Headers $headers -Body $body
```

### 使用 curl 测试 (需要先安装 curl)

```cmd
curl -X POST http://localhost:5050/api/career/start ^
  -H "Content-Type: application/json" ^
  -d "{\"user_profile\":{\"age\":25,\"education_level\":\"本科\",\"work_experience\":3,\"current_position\":\"软件工程师\",\"industry\":\"互联网\",\"skills\":[\"Python\",\"React\"],\"interests\":[\"AI\",\"产品设计\"],\"career_goals\":\"成为AI产品经理\",\"location\":\"北京\",\"salary_expectation\":\"20-30k\"},\"message\":\"我希望从技术转向产品管理方向\"}"
```
  }'

# 2. 获取状态 (替换 SESSION_ID)
curl http://localhost:5050/api/career/status/SESSION_ID

# 3. 健康检查
curl http://localhost:5050/api/career/health
```

### 使用 Python 测试

```python
import requests
import json

# 开始职业规划
response = requests.post('http://localhost:5050/api/career/start', json={
    'user_profile': {
        'age': 25,
        'education_level': '本科',
        'work_experience': 3,
        'current_position': '软件工程师',
        'industry': '互联网',
        'skills': ['Python', 'React'],
        'career_goals': '成为AI产品经理'
    },
    'message': '我想转型做产品经理'
})

result = response.json()
print(json.dumps(result, indent=2, ensure_ascii=False))
```

## 🔧 常见问题

### Q: API 密钥在哪里获取？
A: 访问 [阿里云百炼控制台](https://dashscope.console.aliyun.com/) 注册并获取 API 密钥。

### Q: 应用启动失败怎么办？
A: 检查以下几点：
1. Python 版本是否为 3.11+
2. 是否正确设置了 DASHSCOPE_API_KEY
3. 是否在虚拟环境中安装了依赖

### Q: 前端页面无法访问？
A: 确保：
1. 后端服务正在运行
2. 前端文件已正确复制到 `src/static/` 目录
3. 访问 http://localhost:5050 而不是前端开发服务器地址

### Q: 分析结果不准确？
A: 这可能是因为：
1. 使用了测试 API 密钥
2. 输入信息不够详细
3. 需要提供更具体的职业目标

## 📚 更多资源

- [完整部署指南](./DEPLOYMENT.md)
- [API 文档](./API_DOCUMENTATION.md)
- [项目说明](./README.md)

## 🆘 获取帮助

如果遇到问题：
1. 查看控制台错误信息
2. 检查日志文件
3. 参考故障排除文档
4. 联系技术支持

---

**祝您使用愉快！让 AI 为您的职业发展保驾护航！** 🚀

