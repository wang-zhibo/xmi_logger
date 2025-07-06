#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
XmiLogger 高级功能演示脚本 v2.0
展示智能日志过滤、聚合、监控、分布式支持等高级功能
"""

import gc
import os
import hashlib
import datetime
import asyncio
import time
import json
import threading
import random
from concurrent.futures import ThreadPoolExecutor
from xmi_logger import XmiLogger
from xmi_logger.advanced_features import *

def demo_advanced_features():
    """演示高级功能"""
    print("🚀 XmiLogger 高级功能演示 v2.0")
    print("=" * 60)
    
    # 创建支持高级功能的日志记录器
    log = XmiLogger(
        "advanced_demo",
        log_dir="test_logs",
        enable_stats=True
    )
    
    # 初始化高级功能组件
    log.aggregator = LogAggregator(window_size=50, flush_interval=3.0)
    log.monitor = PerformanceMonitor()
    log.distributed_logger = DistributedLogger("node-001")
    log.security = LogSecurity()
    log.database = LogDatabase("test_logs/logs.db")
    log.stream_processor = LogStreamProcessor()
    log.analyzer = LogAnalyzer()
    log.health_checker = LogHealthChecker()
    log.backup_manager = LogBackupManager("test_logs/backups")
    log.memory_optimizer = MemoryOptimizer(max_memory_mb=256)
    log.router = LogRouter()
    log.archiver = LogArchiver("test_logs/archives")
    
    # 设置智能路由
    def error_handler(log_entry):
        print(f"🚨 错误日志路由: {log_entry['message']}")
        # 可以发送到错误监控系统
    
    def security_handler(log_entry):
        print(f"🔒 安全日志路由: {log_entry['message']}")
        # 可以发送到安全监控系统
    
    log.router.add_route(lambda entry: entry.get('level') == 'ERROR', error_handler)
    log.router.add_route(lambda entry: 'password' in entry.get('message', '').lower(), security_handler)
    
    # 添加流处理器
    def add_timestamp_processor(log_entry):
        log_entry['processed_timestamp'] = time.time()
        return log_entry
    
    def add_checksum_processor(log_entry):
        message = log_entry.get('message', '')
        log_entry['checksum'] = hashlib.md5(message.encode()).hexdigest()[:8]
        return log_entry
    
    log.stream_processor.add_processor(add_timestamp_processor)
    log.stream_processor.add_processor(add_checksum_processor)
    
    print("\n=== 1. 智能日志分析演示 ===")
    test_messages = [
        "用户登录成功",
        "数据库连接失败: Connection refused",
        "API请求超时: HTTP 504",
        "密码验证失败: Invalid credentials",
        "内存使用率过高: 95%",
        "SQL注入攻击检测: SELECT * FROM users",
        "文件上传成功",
        "认证失败: Unauthorized access"
    ]
    
    for message in test_messages:
        analysis = log.analyzer.analyze_log({'message': message, 'level': 'INFO'})
        print(f"消息: {message}")
        print(f"  严重程度: {analysis['severity']}")
        print(f"  类别: {analysis['categories']}")
        print(f"  建议: {analysis['suggestions']}")
        print()
    
    print("\n=== 2. 分布式日志演示 ===")
    for i in range(5):
        log_id = log.distributed_logger.get_log_id()
        log.info(f"分布式日志消息 {i+1} (ID: {log_id})")
    
    print("\n=== 3. 安全日志演示 ===")
    sensitive_messages = [
        "用户密码: 123456",
        "API密钥: sk-1234567890abcdef",
        "访问令牌: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        "数据库密码: mysecretpassword",
        "普通日志消息"
    ]
    
    for message in sensitive_messages:
        sanitized = log.security.sanitize_message(message)
        print(f"原始: {message}")
        print(f"清理后: {sanitized}")
        print()
    
    print("\n=== 4. 性能监控演示 ===")
    # 模拟大量日志记录
    def worker(worker_id):
        for i in range(100):
            start_time = time.perf_counter()
            log.info(f"工作线程 {worker_id} - 消息 {i}")
            processing_time = (time.perf_counter() - start_time) * 1000
            log.monitor.record_log("INFO", processing_time)
            time.sleep(0.001)
    
    # 使用线程池测试并发
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(worker, i) for i in range(5)]
        for future in futures:
            future.result()
    
    # 获取性能指标
    metrics = log.monitor.get_metrics()
    print("性能指标:")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    
    print("\n=== 5. 日志聚合演示 ===")
    # 记录重复日志
    for i in range(20):
        log.aggregator.add_log({
            'level': 'INFO',
            'message': '重复的日志消息',
            'timestamp': time.time()
        })
    
    # 等待聚合处理
    time.sleep(4)
    
    print("\n=== 6. 流处理演示 ===")
    # 处理一些日志
    test_logs = [
        {'level': 'INFO', 'message': '测试消息1'},
        {'level': 'ERROR', 'message': '测试错误1'},
        {'level': 'WARNING', 'message': '测试警告1'}
    ]
    
    for log_entry in test_logs:
        log.stream_processor.process_log(log_entry)
    
    # 获取处理后的日志
    time.sleep(1)
    processed_logs = []
    while True:
        processed_log = log.stream_processor.get_processed_log()
        if processed_log is None:
            break
        processed_logs.append(processed_log)
    
    print("处理后的日志:")
    for log_entry in processed_logs:
        print(f"  {log_entry}")
    
    print("\n=== 7. 数据库支持演示 ===")
    # 插入一些测试日志
    test_db_logs = [
        {
            'timestamp': datetime.datetime.now().isoformat(),
            'level': 'INFO',
            'message': '数据库测试消息1',
            'file': 'test.py',
            'line': 100,
            'function': 'test_function',
            'process_id': os.getpid(),
            'thread_id': threading.get_ident(),
            'extra_data': {'user_id': 123, 'session_id': 'abc123'}
        },
        {
            'timestamp': datetime.datetime.now().isoformat(),
            'level': 'ERROR',
            'message': '数据库测试错误1',
            'file': 'test.py',
            'line': 200,
            'function': 'error_function',
            'process_id': os.getpid(),
            'thread_id': threading.get_ident(),
            'extra_data': {'error_code': 500, 'request_id': 'req123'}
        }
    ]
    
    for log_entry in test_db_logs:
        log.database.insert_log(log_entry)
    
    # 查询日志
    logs = log.database.query_logs({'level': 'ERROR'}, limit=10)
    print(f"查询到 {len(logs)} 条错误日志")
    
    print("\n=== 8. 健康检查演示 ===")
    health_status = log.health_checker.check_health("test_logs")
    print("系统健康状态:")
    print(json.dumps(health_status, indent=2, ensure_ascii=False))
    
    print("\n=== 9. 备份管理演示 ===")
    # 创建备份
    backup_path = log.backup_manager.create_backup("test_logs", "demo_backup")
    print(f"创建备份: {backup_path}")
    
    # 列出备份
    backups = log.backup_manager.list_backups()
    print(f"备份列表: {len(backups)} 个备份")
    for backup in backups[:3]:  # 只显示前3个
        print(f"  {backup['name']} - {backup['size_mb']:.2f}MB - {backup['created']}")
    
    print("\n=== 10. 内存优化演示 ===")
    # 模拟内存使用
    large_data = []
    for i in range(10000):
        large_data.append(f"测试数据 {i}" * 100)
    
    print(f"创建了 {len(large_data)} 个大数据对象")
    
    # 触发内存优化
    if log.memory_optimizer.check_memory():
        print("检测到内存使用过高，触发优化...")
        log.memory_optimizer.optimize_memory()
    
    # 清理数据
    del large_data
    gc.collect()
    
    print("\n=== 11. 日志归档演示 ===")
    # 创建一些测试日志文件
    test_log_content = "这是测试日志内容\n" * 1000
    for i in range(3):
        with open(f"test_logs/test_log_{i}.log", 'w') as f:
            f.write(test_log_content)
    
    # 归档日志
    archived_files = log.archiver.archive_logs("test_logs", days_old=0)
    print(f"归档了 {len(archived_files)} 个日志文件")
    
    print("\n=== 12. 智能路由演示 ===")
    # 测试不同类型的日志路由
    test_routes = [
        {'level': 'INFO', 'message': '普通信息日志'},
        {'level': 'ERROR', 'message': '这是一个错误'},
        {'level': 'INFO', 'message': '用户密码: secret123'},
        {'level': 'WARNING', 'message': '性能警告'},
        {'level': 'ERROR', 'message': '另一个错误消息'}
    ]
    
    for log_entry in test_routes:
        print(f"路由日志: {log_entry['level']} - {log_entry['message']}")
        log.router.route_log(log_entry)
    
    print("\n=== 演示完成 ===")
    
    # 清理资源
    log.cleanup()
    if hasattr(log, 'aggregator'):
        log.aggregator.stop()
    
    print("✅ 所有高级功能演示完成！")

def demo_advanced_usage():
    """演示高级用法"""
    print("\n🔧 高级用法示例")
    print("=" * 40)
    
    # 创建支持所有高级功能的日志记录器
    log = XmiLogger(
        "production_app",
        log_dir="production_logs",
        enable_stats=True
    )
    
    # 初始化组件
    log.aggregator = LogAggregator(window_size=100, flush_interval=5.0)
    log.monitor = PerformanceMonitor()
    log.distributed_logger = DistributedLogger("prod-node-001")
    log.security = LogSecurity()
    log.database = LogDatabase("production_logs/logs.db")
    log.stream_processor = LogStreamProcessor()
    log.analyzer = LogAnalyzer()
    log.health_checker = LogHealthChecker()
    log.backup_manager = LogBackupManager("production_logs/backups")
    log.memory_optimizer = MemoryOptimizer(max_memory_mb=1024)
    log.router = LogRouter()
    log.archiver = LogArchiver("production_logs/archives")
    
    # 设置生产环境路由
    def critical_error_handler(log_entry):
        # 发送到告警系统
        print(f"🚨 严重错误告警: {log_entry['message']}")
    
    def security_alert_handler(log_entry):
        # 发送到安全监控
        print(f"🔒 安全告警: {log_entry['message']}")
    
    def performance_alert_handler(log_entry):
        # 发送到性能监控
        print(f"⚡ 性能告警: {log_entry['message']}")
    
    log.router.add_route(lambda entry: entry.get('level') == 'CRITICAL', critical_error_handler)
    log.router.add_route(lambda entry: 'security' in entry.get('message', '').lower(), security_alert_handler)
    log.router.add_route(lambda entry: 'performance' in entry.get('message', '').lower(), performance_alert_handler)
    
    # 添加自定义流处理器
    def add_correlation_id(log_entry):
        if 'correlation_id' not in log_entry:
            log_entry['correlation_id'] = str(uuid.uuid4())[:8]
        return log_entry
    
    def add_service_name(log_entry):
        log_entry['service_name'] = 'production_app'
        return log_entry
    
    log.stream_processor.add_processor(add_correlation_id)
    log.stream_processor.add_processor(add_service_name)
    
    # 模拟生产环境日志
    print("模拟生产环境日志记录...")
    
    # 正常业务日志
    for i in range(10):
        log.info(f"用户 {i+1} 登录成功")
        log.info(f"处理订单 {i+1}")
        log.debug(f"数据库查询执行: SELECT * FROM orders WHERE id = {i+1}")
    
    # 错误日志
    try:
        raise ValueError("模拟的业务错误")
    except Exception as e:
        log.error(f"业务处理失败: {e}")
    
    # 安全相关日志
    log.warning("检测到可疑登录尝试: IP 192.168.1.100")
    log.error("安全: 用户密码验证失败次数过多")
    
    # 性能相关日志
    log.warning("性能: API响应时间超过阈值 (2.5s)")
    log.info("性能: 数据库连接池使用率 85%")
    
    # 获取系统状态
    print("\n📊 系统状态报告:")
    metrics = log.monitor.get_metrics()
    print(f"  总日志数: {metrics.get('log_count', 0)}")
    print(f"  错误数: {metrics.get('error_count', 0)}")
    print(f"  平均处理时间: {metrics.get('avg_processing_time', 0):.2f}ms")
    print(f"  内存使用: {metrics.get('memory_usage', 0):.2f}MB")
    print(f"  CPU使用率: {metrics.get('cpu_usage', 0):.2f}%")
    print(f"  吞吐量: {metrics.get('throughput', 0):.2f} 日志/秒")
    
    # 健康检查
    health = log.health_checker.check_health("production_logs")
    print(f"\n🏥 系统健康状态: {health['status']}")
    if health.get('warnings'):
        print("  警告:")
        for warning in health['warnings']:
            print(f"    - {warning}")
    
    # 创建备份
    backup_path = log.backup_manager.create_backup("production_logs", "daily_backup")
    print(f"\n💾 创建备份: {backup_path}")
    
    print("\n✅ 高级用法演示完成！")

if __name__ == "__main__":
    try:
        demo_advanced_features()
        demo_advanced_usage()
        
        print("\n🎉 所有演示完成！")
        print("\n📋 新增高级功能总结:")
        print("✅ 智能日志分析 - 自动识别错误、警告、安全事件")
        print("✅ 分布式日志支持 - 唯一日志ID和节点标识")
        print("✅ 日志安全功能 - 敏感信息清理和加密")
        print("✅ 性能监控 - 实时监控系统资源使用")
        print("✅ 日志聚合 - 自动聚合重复日志")
        print("✅ 流处理 - 可扩展的日志处理管道")
        print("✅ 数据库支持 - 结构化日志存储和查询")
        print("✅ 健康检查 - 系统状态监控")
        print("✅ 备份管理 - 自动备份和恢复")
        print("✅ 内存优化 - 智能垃圾回收")
        print("✅ 智能路由 - 基于条件的日志分发")
        print("✅ 日志归档 - 自动压缩和归档")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc() 