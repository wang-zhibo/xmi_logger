#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
增强错误日志演示
演示优化后的日志系统如何显示详细的错误位置信息
"""

from xmi_logger import XmiLogger
import time
import json
import asyncio
import random

def main():
    # 自定义日志格式，包含更多调试信息
    custom_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "ReqID:{extra[request_id]} | "
        "<cyan>{file}</cyan>:<cyan>{line}</cyan>:<cyan>{function}</cyan> | "
        "<magenta>{process}</magenta> | "
        "<level>{message}</level>"
    )

    # 初始化日志记录器
    log = XmiLogger(
        "enhanced_error_demo",
        rotation_time="1 day",
        custom_format=custom_format,
        filter_level="DEBUG",
        compression="zip",
        enable_stats=True,
        categories=["api", "db", "ui", "error"]
    )

    # 设置全局异常处理器
    log.setup_exception_handler()

    # 添加自定义日志级别
    log.add_custom_level("CRITICAL_ERROR", no=35, color="<red><bold>", icon="💥")

    @log.log_decorator("除零错误", level="ERROR")
    def test_zero_division_error(a, b):
        """测试除零错误"""
        return a / b

    @log.log_decorator("JSON解析错误", level="WARNING")
    def test_json_error():
        """测试JSON解析错误"""
        return json.loads("invalid_json")

    @log.log_decorator("索引错误", level="ERROR")
    def test_index_error():
        """测试索引错误"""
        lst = [1, 2, 3]
        return lst[10]

    @log.log_decorator("属性错误", level="ERROR")
    def test_attribute_error():
        """测试属性错误"""
        obj = None
        return obj.non_existent_attribute

    @log.log_decorator("类型错误", level="ERROR")
    def test_type_error():
        """测试类型错误"""
        return "string" + 123

    @log.log_decorator("异步错误", level="ERROR")
    async def test_async_error():
        """测试异步函数中的错误"""
        await asyncio.sleep(0.1)
        raise ValueError("异步函数中的错误")

    def test_nested_error():
        """测试嵌套函数中的错误"""
        def inner_function():
            def deepest_function():
                # 这里会引发错误
                return 1 / 0
            return deepest_function()
        return inner_function()

    @log.log_decorator("嵌套错误", level="ERROR")
    def test_nested_error_wrapper():
        """包装嵌套错误测试"""
        return test_nested_error()

    # 设置请求ID
    token = log.request_id_var.set("REQ-ENHANCED-001")

    try:
        log.info("开始增强错误日志演示")
        
        # 测试基本日志功能
        log.info('这是一条信息日志')
        log.debug('这是一条调试日志')
        log.warning('这是一条警告日志')
        log.error('这是一条错误日志')
        log.critical('这是一条严重错误日志')
        
        # 使用带位置信息的日志
        log.log_with_location("INFO", "这是带位置信息的日志")
        log.log_with_location("WARNING", "这是带位置信息的警告")
        
        # 使用自定义日志级别
        log.log("CRITICAL_ERROR", "这是一条严重错误日志")
        
        # 使用标签功能
        log.log_with_tag("INFO", "这是带标签的日志", "FEATURE")
        log.log_with_tag("WARNING", "这是带标签的警告", "DEPRECATED")
        
        # 使用分类功能
        log.log_with_category("INFO", "数据库连接成功", "db")
        log.log_with_category("ERROR", "API请求失败", "api")
        log.log_with_category("DEBUG", "UI组件渲染", "ui")

        print("\n=== 开始错误测试 ===")
        
        # 测试各种类型的错误
        try:
            result = test_zero_division_error(1, 0)
        except ZeroDivisionError:
            log.exception("捕获到除零错误")

        try:
            result = test_json_error()
        except json.JSONDecodeError:
            log.exception("捕获到JSON解析错误")

        try:
            result = test_index_error()
        except IndexError:
            log.exception("捕获到索引错误")

        try:
            result = test_attribute_error()
        except AttributeError:
            log.exception("捕获到属性错误")

        try:
            result = test_type_error()
        except TypeError:
            log.exception("捕获到类型错误")

        try:
            result = test_nested_error_wrapper()
        except ZeroDivisionError:
            log.exception("捕获到嵌套函数错误")

        # 测试异步错误
        async def test_async_errors():
            try:
                await test_async_error()
            except ValueError:
                log.exception("捕获到异步函数错误")

        asyncio.run(test_async_errors())

        # 测试未捕获的异常（会被全局异常处理器捕获）
        print("\n=== 测试未捕获的异常 ===")
        def trigger_unhandled_exception():
            # 这个异常不会被try-catch捕获
            raise RuntimeError("这是一个未捕获的异常")
        
        # 注释掉下面这行来测试全局异常处理器
        # trigger_unhandled_exception()

        print("\n=== 错误测试完成 ===")
        
        # 输出日志统计
        print("\n日志统计信息:")
        print(json.dumps(log.get_stats(), indent=2, ensure_ascii=False))

    finally:
        # 重置请求ID
        log.request_id_var.reset(token)
        log.info("增强错误日志演示完成")

if __name__ == '__main__':
    main() 