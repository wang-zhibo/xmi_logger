#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
XmiLogger 性能测试脚本
测试优化后的性能改进
"""

import sys
import os
import time
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from xmi_logger import XmiLogger

def test_basic_logging_performance():
    """测试基本日志记录性能"""
    print("=== 测试基本日志记录性能 ===")
    
    log = XmiLogger(
        "performance_test",
        log_dir="test_logs",
        enable_stats=True,
        cache_size=256
    )
    
    # 测试基本日志记录
    start_time = time.perf_counter()
    
    for i in range(1000):
        log.info(f"测试日志消息 {i}")
        log.debug(f"调试信息 {i}")
        log.warning(f"警告信息 {i}")
        if i % 100 == 0:
            log.error(f"错误信息 {i}")
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    print(f"记录 4000 条日志耗时: {duration:.4f} 秒")
    print(f"平均每条日志耗时: {duration/4000*1000:.2f} 毫秒")
    
    return duration

def test_cached_logging_performance():
    """测试缓存日志记录性能"""
    print("\n=== 测试缓存日志记录性能 ===")
    
    log = XmiLogger(
        "cached_test",
        log_dir="test_logs",
        enable_stats=True,
        cache_size=256
    )
    
    # 测试重复消息的缓存效果
    start_time = time.perf_counter()
    
    for i in range(1000):
        log.log_with_location("INFO", "重复的日志消息")
        log.log_with_location("WARNING", "重复的警告消息")
        if i % 100 == 0:
            log.log_with_location("ERROR", "重复的错误消息")
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    print(f"记录 3000 条缓存日志耗时: {duration:.4f} 秒")
    print(f"平均每条日志耗时: {duration/3000*1000:.2f} 毫秒")
    
    # 显示性能统计
    perf_stats = log.get_performance_stats()
    print(f"缓存统计: {json.dumps(perf_stats, indent=2, ensure_ascii=False)}")
    
    return duration

def test_concurrent_logging():
    """测试并发日志记录性能"""
    print("\n=== 测试并发日志记录性能 ===")
    
    log = XmiLogger(
        "concurrent_test",
        log_dir="test_logs",
        enable_stats=True,
        cache_size=512
    )
    
    def worker(worker_id):
        """工作线程函数"""
        for i in range(100):
            log.info(f"工作线程 {worker_id} - 消息 {i}")
            log.debug(f"工作线程 {worker_id} - 调试 {i}")
            if i % 20 == 0:
                log.warning(f"工作线程 {worker_id} - 警告 {i}")
    
    # 使用线程池测试并发
    start_time = time.perf_counter()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker, i) for i in range(10)]
        for future in futures:
            future.result()
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    print(f"10个线程并发记录 3000 条日志耗时: {duration:.4f} 秒")
    print(f"平均每条日志耗时: {duration/3000*1000:.2f} 毫秒")
    
    return duration

def test_error_logging_performance():
    """测试错误日志记录性能"""
    print("\n=== 测试错误日志记录性能 ===")
    
    log = XmiLogger(
        "error_test",
        log_dir="test_logs",
        enable_stats=True,
        cache_size=256
    )
    
    @log.log_decorator("测试错误", level="ERROR")
    def test_error_function():
        """测试错误函数"""
        raise ValueError("测试错误")
    
    start_time = time.perf_counter()
    
    for i in range(100):
        try:
            test_error_function()
        except ValueError:
            log.exception(f"捕获到错误 {i}")
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    print(f"记录 100 条错误日志耗时: {duration:.4f} 秒")
    print(f"平均每条错误日志耗时: {duration/100*1000:.2f} 毫秒")
    
    return duration

async def test_async_logging_performance():
    """测试异步日志记录性能"""
    print("\n=== 测试异步日志记录性能 ===")
    
    log = XmiLogger(
        "async_test",
        log_dir="test_logs",
        enable_stats=True,
        cache_size=256
    )
    
    @log.log_decorator("异步测试", level="INFO")
    async def async_worker(worker_id):
        """异步工作函数"""
        await asyncio.sleep(0.001)  # 模拟异步操作
        for i in range(10):
            log.info(f"异步工作线程 {worker_id} - 消息 {i}")
        return f"工作线程 {worker_id} 完成"
    
    start_time = time.perf_counter()
    
    # 创建多个异步任务
    tasks = [async_worker(i) for i in range(20)]
    results = await asyncio.gather(*tasks)
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    print(f"20个异步任务记录日志耗时: {duration:.4f} 秒")
    print(f"平均每个任务耗时: {duration/20*1000:.2f} 毫秒")
    
    return duration

def test_stats_performance():
    """测试统计功能性能"""
    print("\n=== 测试统计功能性能 ===")
    
    log = XmiLogger(
        "stats_test",
        log_dir="test_logs",
        enable_stats=True,
        cache_size=256
    )
    
    # 记录一些日志
    for i in range(500):
        log.info(f"统计测试日志 {i}")
        if i % 50 == 0:
            log.error(f"统计测试错误 {i}")
    
    # 测试统计获取性能
    start_time = time.perf_counter()
    
    for i in range(100):
        stats = log.get_stats()
        summary = log.get_stats_summary()
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    print(f"获取 200 次统计信息耗时: {duration:.4f} 秒")
    print(f"平均每次统计获取耗时: {duration/200*1000:.2f} 毫秒")
    
    # 显示统计信息
    print(f"统计摘要: {log.get_stats_summary()}")
    
    return duration

def main():
    """主测试函数"""
    print("开始 XmiLogger 性能测试")
    print("=" * 50)
    
    results = {}
    
    # 运行各种性能测试
    results['basic'] = test_basic_logging_performance()
    results['cached'] = test_cached_logging_performance()
    results['concurrent'] = test_concurrent_logging()
    results['error'] = test_error_logging_performance()
    results['async'] = asyncio.run(test_async_logging_performance())
    results['stats'] = test_stats_performance()
    
    # 输出性能总结
    print("\n" + "=" * 50)
    print("性能测试总结:")
    print("=" * 50)
    
    total_time = sum(results.values())
    print(f"总测试时间: {total_time:.4f} 秒")
    
    for test_name, duration in results.items():
        print(f"{test_name:12}: {duration:.4f} 秒")
    
    print("\n性能优化建议:")
    print("1. 使用缓存功能减少重复计算")
    print("2. 合理设置缓存大小避免内存泄漏")
    print("3. 在高并发场景下使用异步日志")
    print("4. 定期清理缓存释放内存")
    print("5. 监控性能统计信息优化配置")

if __name__ == "__main__":
    main() 