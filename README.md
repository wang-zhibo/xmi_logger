# XmiLogger

基于 Loguru 的增强日志记录器，支持多语言、异步操作和高级统计功能。

## 特性

- 🚀 高性能：使用 LRU 缓存和异步处理
- 🌐 多语言支持：支持中文和英文日志输出
- 📊 高级统计：支持日志分类统计和趋势分析
- 🔄 异步支持：支持异步函数日志记录
- 📝 自定义格式：支持自定义日志格式
- 🔒 安全性：内置错误处理和配置验证
- 📦 日志轮转：支持按大小和时间轮转
- 🌍 远程日志：支持异步远程日志收集

## 安装

```bash
pip install xmi-logger
```

## 快速开始

### 基本使用

```python
from xmi_logger import XmiLogger

# 创建日志记录器实例
logger = XmiLogger(
    file_name="app",
    log_dir="logs",
    language="zh"  # 使用中文输出
)

# 记录不同级别的日志
logger.info("这是一条信息日志")
logger.warning("这是一条警告日志")
logger.error("这是一条错误日志")
```

### 异步函数支持

```python
import asyncio

@logger.log_decorator()
async def async_function():
    await asyncio.sleep(1)
    return "异步操作完成"

# 使用异步函数
async def main():
    result = await async_function()
    logger.info(f"异步函数结果: {result}")

asyncio.run(main())
```

### 远程日志收集

```python
logger = XmiLogger(
    file_name="app",
    remote_log_url="https://your-log-server.com/logs",
    max_workers=3
)
```

### 日志统计功能

```python
# 启用统计功能
logger = XmiLogger(
    file_name="app",
    enable_stats=True
)

# 获取统计信息
stats = logger.get_stats()
print(logger.get_stats_summary())

# 获取错误趋势
error_trend = logger.get_error_trend()

# 获取分类分布
category_dist = logger.get_category_distribution()
```

## 高级配置

### 完整配置示例

```python
logger = XmiLogger(
    file_name="app",                    # 日志文件名
    log_dir="logs",                     # 日志目录
    max_size=14,                        # 单个日志文件最大大小（MB）
    retention="7 days",                 # 日志保留时间
    remote_log_url=None,                # 远程日志服务器URL
    max_workers=3,                      # 远程日志发送线程数
    work_type=False,                    # 工作模式（False为测试环境）
    language="zh",                      # 日志语言（zh/en）
    rotation_time="1 day",              # 日志轮转时间
    custom_format=None,                 # 自定义日志格式
    filter_level="DEBUG",               # 日志过滤级别
    compression="zip",                  # 日志压缩格式
    enable_stats=False,                 # 是否启用统计
    categories=None,                    # 日志分类列表
    cache_size=128                      # 缓存大小
)
```

### 自定义日志格式

```python
custom_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "ReqID:{extra[request_id]} | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

logger = XmiLogger(
    file_name="app",
    custom_format=custom_format
)
```

## 主要功能

### 1. 日志记录
- 支持所有标准日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- 支持自定义日志级别
- 支持带标签和分类的日志记录

### 2. 日志管理
- 自动日志轮转
- 日志压缩
- 日志保留策略
- 多文件输出（按级别分文件）

### 3. 统计功能
- 日志总数统计
- 错误率统计
- 按类别统计
- 按时间统计
- 错误趋势分析

### 4. 远程日志
- 异步远程日志发送
- 自动重试机制
- 线程池管理
- 错误处理

### 5. 装饰器支持
- 函数执行时间记录
- 异常捕获和记录
- 支持同步和异步函数

## 错误处理

```python
try:
    logger = XmiLogger("app", log_dir="/path/to/logs")
except RuntimeError as e:
    print(f"日志配置失败: {e}")
```

## 注意事项

1. 确保日志目录具有写入权限
2. 远程日志URL必须是有效的HTTP(S)地址
3. 建议在生产环境中启用统计功能
4. 异步操作时注意正确处理异常

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

