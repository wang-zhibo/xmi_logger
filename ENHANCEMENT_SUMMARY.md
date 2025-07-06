# XmiLogger 增强错误日志功能总结

## 优化概述

本次优化主要针对日志系统在显示错误信息时无法具体显示哪一行有问题的问题，通过增强错误信息显示功能，让开发者能够快速定位问题所在。

## 主要优化内容

### 1. 增强日志格式

**优化前：**
```
2025-01-03 10:30:15 | ERROR | ReqID:REQ-123 | app:function:line | 发生异常: 除零错误
```

**优化后：**
```
2025-01-03 10:30:15.123 | ERROR | ReqID:REQ-123 | app.py:25:divide_numbers | 12345 | 除零错误 [ZeroDivisionError]: division by zero | 位置: app.py:25:divide_numbers | 代码: return a / b
```

### 2. 新增功能

#### 2.1 详细错误位置信息
- 显示错误发生的具体文件名、行号和函数名
- 显示错误发生时的代码行内容
- 显示调用链信息（最后3层调用）

#### 2.2 新增方法
- `get_current_location()`: 获取当前调用位置信息
- `log_with_location()`: 记录带位置信息的日志

#### 2.3 增强异常处理
- 优化 `_log_exception()` 方法，提供更详细的错误信息
- 优化全局异常处理器，显示完整的错误上下文

### 3. 代码修改详情

#### 3.1 日志格式优化 (`xmi_logger.py`)
```python
# 修改前
"<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "

# 修改后  
"<cyan>{file}</cyan>:<cyan>{line}</cyan>:<cyan>{function}</cyan> | "
"<magenta>{process}</magenta> | "
```

#### 3.2 异常处理增强
```python
def _log_exception(self, func_name: str, error: Exception, msg_key: str,
                 level: str, trace: bool, is_async: bool):
    """统一的异常记录处理，增强错误信息显示"""
    # 获取调用栈信息
    import traceback
    tb = traceback.extract_tb(error.__traceback__)
    
    # 获取错误发生的具体位置
    if tb:
        last_frame = tb[-1]
        error_location = f"{last_frame.filename}:{last_frame.lineno}:{last_frame.name}"
        line_content = last_frame.line.strip() if last_frame.line else "未知代码行"
    
    # 组合详细的错误消息
    full_error_msg = (
        f"{error_msg} [{error_type}]: {error_value} | "
        f"位置: {error_location} | "
        f"代码: {line_content}"
    )
    
    # 记录调用链信息
    if len(tb) > 1:
        call_chain = []
        for frame in tb[-3:]:  # 只显示最后3层调用
            call_chain.append(f"{frame.filename}:{frame.lineno}:{frame.name}")
        self.logger.error(f"调用链: {' -> '.join(call_chain)}")
```

#### 3.3 新增位置信息方法
```python
def get_current_location(self) -> str:
    """获取当前调用位置信息"""
    import inspect
    frame = inspect.currentframe()
    try:
        stack = inspect.stack()
        if len(stack) > 1:
            caller = stack[1]
            filename = caller.filename
            lineno = caller.lineno
            function = caller.function
            return f"{filename}:{lineno}:{function}"
        else:
            return "未知位置"
    finally:
        del frame

def log_with_location(self, level: str, message: str, include_location: bool = True):
    """带位置信息的日志记录"""
    if include_location:
        location = self.get_current_location()
        full_message = f"[{location}] {message}"
    else:
        full_message = message
    
    log_method = getattr(self.logger, level.lower(), self.logger.info)
    log_method(full_message)
```

### 4. 使用示例

#### 4.1 基本错误日志
```python
@log.log_decorator("除零错误", level="ERROR")
def divide_numbers(a, b):
    return a / b

try:
    result = divide_numbers(1, 0)
except ZeroDivisionError:
    log.exception("捕获到除零错误")
```

#### 4.2 带位置信息的日志
```python
log.log_with_location("INFO", "这是带位置信息的日志")
# 输出: [app.py:30:main] 这是带位置信息的日志
```

#### 4.3 全局异常处理
```python
log.setup_exception_handler()
# 未捕获的异常会自动记录详细的位置信息
```

### 5. 新增示例文件

- `example/enhanced_error_demo.py`: 完整的增强错误日志演示
- `test_enhanced_logging.py`: 简单的测试脚本

### 6. 文档更新

- 更新了 `README.md`，添加了增强错误信息功能的说明
- 添加了使用示例和输出格式说明

## 优化效果

### 优化前的问题
1. 错误日志只显示基本的错误信息
2. 无法快速定位错误发生的具体位置
3. 缺乏调用链信息，难以追踪错误来源
4. 错误信息不够详细，调试困难

### 优化后的改进
1. **精确定位**: 显示错误发生的具体文件、行号和函数名
2. **代码上下文**: 显示错误发生时的实际代码行
3. **调用链追踪**: 显示最后3层调用链，便于追踪错误来源
4. **增强格式**: 日志格式更加详细，包含进程ID和时间戳
5. **灵活使用**: 提供多种方式记录带位置信息的日志

## 测试建议

1. 运行 `test_enhanced_logging.py` 查看基本功能
2. 运行 `example/enhanced_error_demo.py` 查看完整演示
3. 查看生成的日志文件，验证错误信息的详细程度
4. 测试不同类型的错误，验证位置信息的准确性

## 兼容性

- 所有现有功能保持不变
- 新增功能为可选功能，不影响现有代码
- 向后兼容，现有代码无需修改即可使用

## 总结

通过这次优化，XmiLogger 现在能够提供更加详细和有用的错误信息，大大提高了调试效率。开发者现在可以：

1. 快速定位错误发生的具体位置
2. 了解错误发生时的代码上下文
3. 追踪错误的调用链
4. 获得更丰富的错误信息用于问题诊断

这些改进使得 XmiLogger 成为一个更加强大和实用的日志工具。 