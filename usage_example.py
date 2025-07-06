#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XmiLogger 使用示例
展示基本的日志记录功能
"""

import os
import sys
import time

# 添加项目路径到sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xmi_logger.xmi_logger import XmiLogger

def basic_usage_example():
    """基础使用示例"""
    print("=" * 50)
    print("XmiLogger 基础使用示例")
    print("=" * 50)
    
    # 创建日志记录器
    log = XmiLogger(
        file_name="example",
        log_dir="./logs",
        filter_level="DEBUG"
    )
    
    # 记录不同级别的日志
    log.debug("这是一条调试信息")
    log.info("这是一条普通信息")
    log.warning("这是一条警告信息")
    log.error("这是一条错误信息")
    log.critical("这是一条严重错误信息")
    
    print("✅ 基础日志记录完成")
    print("日志文件位置: ./logs/")

def performance_example():
    """性能示例"""
    print("\n" + "=" * 50)
    print("性能测试示例")
    print("=" * 50)
    
    log = XmiLogger(
        file_name="performance",
        log_dir="./logs",
        filter_level="INFO"
    )
    
    # 测试大量日志记录
    start_time = time.time()
    for i in range(100):
        log.info(f"性能测试消息 {i}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"✅ 100条日志记录完成，耗时: {duration:.3f}秒")
    print(f"平均每条日志: {duration/100*1000:.2f}毫秒")

def error_handling_example():
    """错误处理示例"""
    print("\n" + "=" * 50)
    print("错误处理示例")
    print("=" * 50)
    
    log = XmiLogger(
        file_name="error_example",
        log_dir="./logs",
        filter_level="DEBUG"
    )
    
    try:
        # 模拟一个错误
        result = 10 / 0
    except Exception as e:
        log.error(f"发生错误: {e}")
        log.debug("错误详情", exc_info=True)
    
    print("✅ 错误处理示例完成")

def custom_format_example():
    """自定义格式示例"""
    print("\n" + "=" * 50)
    print("自定义格式示例")
    print("=" * 50)
    
    # 使用自定义格式
    custom_format = "%(asctime)s - %(levelname)s - %(message)s"
    log = XmiLogger(
        file_name="custom_format",
        log_dir="./logs",
        filter_level="INFO",
        custom_format=custom_format
    )
    
    log.info("使用自定义格式的日志消息")
    log.warning("警告消息")
    log.error("错误消息")
    
    print("✅ 自定义格式示例完成")

def main():
    """运行所有示例"""
    print("开始运行 XmiLogger 使用示例...")
    
    # 确保日志目录存在
    os.makedirs("./logs", exist_ok=True)
    
    # 运行各种示例
    basic_usage_example()
    performance_example()
    error_handling_example()
    custom_format_example()
    
    print("\n" + "=" * 50)
    print("所有示例运行完成！")
    print("=" * 50)
    print("请查看 ./logs/ 目录下的日志文件")
    print("日志文件包括:")
    print("- example.log - 基础使用示例")
    print("- performance.log - 性能测试示例")
    print("- error_example.log - 错误处理示例")
    print("- custom_format.log - 自定义格式示例")

if __name__ == "__main__":
    main() 