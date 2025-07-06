#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
测试增强的错误日志功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from xmi_logger import XmiLogger

def test_enhanced_error_logging():
    """测试增强的错误日志功能"""
    
    # 创建日志记录器
    log = XmiLogger(
        "test_enhanced",
        log_dir="test_logs",
        enable_stats=True
    )
    
    # 设置全局异常处理器
    log.setup_exception_handler()
    
    print("=== 测试增强错误日志功能 ===")
    
    @log.log_decorator("测试除零错误", level="ERROR")
    def test_division_error():
        """测试除零错误"""
        return 1 / 0
    
    @log.log_decorator("测试索引错误", level="ERROR")
    def test_index_error():
        """测试索引错误"""
        lst = [1, 2, 3]
        return lst[10]
    
    @log.log_decorator("测试属性错误", level="ERROR")
    def test_attribute_error():
        """测试属性错误"""
        obj = None
        return obj.non_existent_attribute
    
    # 测试带位置信息的日志
    log.log_with_location("INFO", "这是带位置信息的日志")
    log.log_with_location("WARNING", "这是带位置信息的警告")
    
    # 测试各种错误
    try:
        test_division_error()
    except ZeroDivisionError:
        log.exception("捕获到除零错误")
    
    try:
        test_index_error()
    except IndexError:
        log.exception("捕获到索引错误")
    
    try:
        test_attribute_error()
    except AttributeError:
        log.exception("捕获到属性错误")
    
    print("=== 测试完成 ===")
    print("请查看 test_logs 目录中的日志文件来查看详细的错误信息")

if __name__ == "__main__":
    test_enhanced_error_logging() 