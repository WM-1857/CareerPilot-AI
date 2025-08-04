# 测试结果存储目录

此目录用于存储测试套件的执行结果。

## 文件命名规则

测试结果文件按以下格式命名：
```
test_results_YYYYMMDD_HHMMSS.json
```

例如：
- `test_results_20240804_143022.json` - 2024年8月4日 14:30:22 的测试结果

## 结果文件内容

每个结果文件包含：

```json
{
  "overall_success": true,
  "total_modules": 3,
  "passed_modules": 3,
  "failed_modules": 0,
  "overall_duration": 7.35,
  "module_results": [
    {
      "module_id": "environment",
      "module_name": "环境配置测试",
      "success": true,
      "duration": 1.23,
      "return_code": 0,
      "stdout": "...",
      "stderr": "",
      "timestamp": "2024-08-04T14:30:22"
    }
  ],
  "timestamp": "2024-08-04T14:30:29"
}
```

## 结果分析

可以通过以下方式分析测试结果：

1. **查看最新结果**：文件按时间戳排序，最新的在最后
2. **趋势分析**：比较不同时间的测试结果
3. **失败追踪**：查找重复失败的模块
4. **性能监控**：跟踪测试执行时间变化

## 自动清理

建议定期清理旧的测试结果文件，保留最近30天的结果即可。
