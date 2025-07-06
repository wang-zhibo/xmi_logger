#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
XmiLogger 高级功能演示
展示新增的批量处理、自适应级别、日志分析等功能
"""

import sys
import os
import time
import asyncio
import json
import threading
from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from xmi_logger import XmiLogger

def demo_batch_logging():
    """演示批量日志记录功能"""
    print("=== 批量日志记录演示 ===")
    
    log = XmiLogger(
        "batch_demo",
        log_dir="test_logs",
        enable_stats=True,
        cache_size=256
    )
    
    # 准备批量日志数据
    batch_logs = [
        {'level': 'INFO', 'message': '批量日志消息 1', 'tag': 'BATCH'},
        {'level': 'WARNING', 'message': '批量警告消息 1', 'category': 'SYSTEM'},
        {'level': 'ERROR', 'message': '批量错误消息 1'},
        {'level': 'INFO', 'message': '批量日志消息 2', 'tag': 'BATCH'},
        {'level': 'DEBUG', 'message': '批量调试消息 1', 'category': 'DEBUG'},
    ]
    
    # 同步批量记录
    start_time = time.perf_counter()
    log.batch_log(batch_logs)
    sync_duration = time.perf_counter() - start_time
    
    print(f"同步批量记录耗时: {sync_duration:.4f} 秒")
    
    # 异步批量记录
    start_time = time.perf_counter()
    asyncio.run(log.async_batch_log(batch_logs))
    async_duration = time.perf_counter() - start_time
    
    print(f"异步批量记录耗时: {async_duration:.4f} 秒")
    
    return sync_duration, async_duration

def demo_context_logging():
    """演示上下文日志记录功能"""
    print("\n=== 上下文日志记录演示 ===")
    
    log = XmiLogger(
        "context_demo",
        log_dir="test_logs",
        enable_stats=True
    )
    
    # 带上下文的日志记录
    context = {
        'user_id': 12345,
        'session_id': 'sess_abc123',
        'request_id': 'req_xyz789',
        'ip': '192.168.1.100'
    }
    
    log.log_with_context("INFO", "用户登录", context)
    log.log_with_context("WARNING", "用户权限不足", context)
    log.log_with_context("ERROR", "数据库连接失败", context)
    
    # 带计时信息的日志记录
    timing_data = {
        'db_query': 0.125,
        'api_call': 0.342,
        'total': 0.467
    }
    
    log.log_with_timing("INFO", "API请求完成", timing_data)
    
    print("上下文日志记录完成")

def demo_adaptive_level():
    """演示自适应日志级别功能"""
    print("\n=== 自适应日志级别演示 ===")
    
    log = XmiLogger(
        "adaptive_demo",
        log_dir="test_logs",
        enable_stats=True,
        adaptive_level=True,
        performance_mode=True
    )
    
    # 模拟高错误率场景
    print("模拟高错误率场景...")
    for i in range(50):
        try:
            if i % 10 == 0:
                raise ValueError(f"模拟错误 {i}")
            log.info(f"正常日志消息 {i}")
        except ValueError:
            log.error(f"捕获到错误 {i}")
    
    # 检查自适应调整
    log.set_adaptive_level(error_rate_threshold=0.1)
    print(f"当前日志级别: {log.filter_level}")
    
    # 启用性能模式
    log.enable_performance_mode()
    print(f"性能模式下的日志级别: {log.filter_level}")
    
    # 禁用性能模式
    log.disable_performance_mode()
    print(f"恢复后的日志级别: {log.filter_level}")

def demo_log_management():
    """演示日志管理功能"""
    print("\n=== 日志管理功能演示 ===")
    
    log = XmiLogger(
        "management_demo",
        log_dir="test_logs",
        enable_stats=True
    )
    
    # 记录一些测试日志
    for i in range(100):
        log.info(f"管理测试日志 {i}")
        if i % 20 == 0:
            log.error(f"管理测试错误 {i}")
    
    # 压缩日志
    print("压缩日志文件...")
    log.compress_logs(days_old=0)  # 立即压缩
    
    # 归档日志
    print("归档日志文件...")
    log.archive_logs()
    
    # 清理旧日志
    print("清理旧日志文件...")
    log.cleanup_old_logs(max_days=1)  # 清理1天前的日志
    
    print("日志管理功能演示完成")

def demo_log_analysis():
    """演示日志分析功能"""
    print("\n=== 日志分析功能演示 ===")
    
    log = XmiLogger(
        "analysis_demo",
        log_dir="test_logs",
        enable_stats=True
    )
    
    # 记录一些测试日志用于分析
    for i in range(200):
        log.info(f"分析测试日志 {i}")
        if i % 10 == 0:
            log.warning(f"分析测试警告 {i}")
        if i % 20 == 0:
            log.error(f"分析测试错误 {i}")
    
    # 分析日志
    print("分析最近24小时的日志...")
    analysis = log.analyze_logs(hours=24)
    
    print(f"分析结果:")
    print(f"  总日志数: {analysis['total_logs']}")
    print(f"  错误数: {analysis['error_count']}")
    print(f"  警告数: {analysis['warning_count']}")
    print(f"  错误率: {analysis['error_rate']:.2%}")
    
    # 生成报告
    report = log.generate_log_report(hours=24)
    print("\n日志报告:")
    print(report)
    
    # 导出日志到JSON
    print("导出日志到JSON...")
    log.export_logs_to_json("test_logs/exported_logs.json", hours=24)
    
    print("日志分析功能演示完成")

def demo_performance_monitoring():
    """演示性能监控功能"""
    print("\n=== 性能监控功能演示 ===")
    
    log = XmiLogger(
        "performance_demo",
        log_dir="test_logs",
        enable_stats=True,
        cache_size=512
    )
    
    # 记录大量日志
    print("记录大量日志以测试性能...")
    for i in range(1000):
        log.info(f"性能测试日志 {i}")
        if i % 100 == 0:
            log.warning(f"性能测试警告 {i}")
        if i % 200 == 0:
            log.error(f"性能测试错误 {i}")
    
    # 获取性能统计
    perf_stats = log.get_performance_stats()
    print("\n性能统计:")
    print(json.dumps(perf_stats, indent=2, ensure_ascii=False))
    
    # 测试缓存清理
    print("\n清理缓存...")
    log.clear_caches()
    
    # 再次获取性能统计
    perf_stats_after = log.get_performance_stats()
    print("清理后的性能统计:")
    print(json.dumps(perf_stats_after, indent=2, ensure_ascii=False))

def demo_concurrent_logging():
    """演示并发日志记录"""
    print("\n=== 并发日志记录演示 ===")
    
    log = XmiLogger(
        "concurrent_demo",
        log_dir="test_logs",
        enable_stats=True,
        cache_size=1024
    )
    
    def worker(worker_id):
        """工作线程函数"""
        for i in range(50):
            log.info(f"工作线程 {worker_id} - 消息 {i}")
            log.debug(f"工作线程 {worker_id} - 调试 {i}")
            if i % 10 == 0:
                log.warning(f"工作线程 {worker_id} - 警告 {i}")
            time.sleep(0.001)  # 模拟工作负载
    
    # 使用线程池测试并发
    start_time = time.perf_counter()
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(worker, i) for i in range(20)]
        for future in futures:
            future.result()
    
    duration = time.perf_counter() - start_time
    
    print(f"20个线程并发记录 2000 条日志耗时: {duration:.4f} 秒")
    print(f"平均每条日志耗时: {duration/2000*1000:.2f} 毫秒")
    
    return duration

async def demo_async_features():
    """演示异步功能"""
    print("\n=== 异步功能演示 ===")
    
    log = XmiLogger(
        "async_demo",
        log_dir="test_logs",
        enable_stats=True
    )
    
    @log.log_decorator("异步测试", level="INFO")
    async def async_worker(worker_id):
        """异步工作函数"""
        await asyncio.sleep(0.01)  # 模拟异步操作
        for i in range(10):
            log.info(f"异步工作线程 {worker_id} - 消息 {i}")
        return f"工作线程 {worker_id} 完成"
    
    start_time = time.perf_counter()
    
    # 创建多个异步任务
    tasks = [async_worker(i) for i in range(50)]
    results = await asyncio.gather(*tasks)
    
    duration = time.perf_counter() - start_time
    
    print(f"50个异步任务记录日志耗时: {duration:.4f} 秒")
    print(f"平均每个任务耗时: {duration/50*1000:.2f} 毫秒")
    
    return duration

def main():
    """主演示函数"""
    print("开始 XmiLogger 高级功能演示")
    print("=" * 60)
    
    results = {}
    
    # 运行各种功能演示
    results['batch'] = demo_batch_logging()
    demo_context_logging()
    demo_adaptive_level()
    demo_log_management()
    demo_log_analysis()
    demo_performance_monitoring()
    results['concurrent'] = demo_concurrent_logging()
    results['async'] = asyncio.run(demo_async_features())
    
    # 输出演示总结
    print("\n" + "=" * 60)
    print("高级功能演示总结:")
    print("=" * 60)
    
    print(f"批量日志记录:")
    print(f"  同步: {results['batch'][0]:.4f} 秒")
    print(f"  异步: {results['batch'][1]:.4f} 秒")
    print(f"并发日志记录: {results['concurrent']:.4f} 秒")
    print(f"异步日志记录: {results['async']:.4f} 秒")
    
    print("\n新增功能特性:")
    print("✅ 批量日志处理 - 提高大量日志记录性能")
    print("✅ 上下文日志 - 自动添加相关上下文信息")
    print("✅ 自适应级别 - 根据系统状态自动调整日志级别")
    print("✅ 日志管理 - 压缩、归档、清理功能")
    print("✅ 日志分析 - 智能分析日志内容和趋势")
    print("✅ 性能监控 - 实时监控缓存和性能指标")
    print("✅ 并发优化 - 支持高并发日志记录")
    print("✅ 异步支持 - 完整的异步日志处理")

if __name__ == "__main__":
    main() 