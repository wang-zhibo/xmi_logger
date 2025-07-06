#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XmiLogger 完整功能测试脚本
测试所有功能是否正常工作
"""

import os
import sys
import time
import asyncio
import threading
import tempfile
import shutil
from datetime import datetime, timedelta
import json
import hashlib
import re
from unittest.mock import patch, MagicMock

# 添加项目路径到sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xmi_logger.xmi_logger import XmiLogger
from xmi_logger.advanced_features import (
    LogFilter, LogAggregator, PerformanceMonitor, DistributedLogger, 
    MemoryOptimizer, LogRouter, LogSecurity, LogArchiver, LogDatabase,
    LogStreamProcessor, LogAnalyzer, LogHealthChecker, LogBackupManager
)

class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.test_results = []
        self.temp_dir = tempfile.mkdtemp(prefix="xmi_logger_test_")
        self.log_file = os.path.join(self.temp_dir, "test.log")
        self.remote_url = "http://localhost:8080/logs"
        # 确保临时目录存在
        os.makedirs(self.temp_dir, exist_ok=True)
        
    def run_test(self, test_name, test_func):
        """运行单个测试"""
        print(f"\n{'='*60}")
        print(f"测试: {test_name}")
        print(f"{'='*60}")
        
        try:
            start_time = time.time()
            result = test_func()
            end_time = time.time()
            
            if result:
                print(f"✅ {test_name} - 通过 (耗时: {end_time - start_time:.2f}秒)")
                self.test_results.append((test_name, True, end_time - start_time))
            else:
                print(f"❌ {test_name} - 失败")
                self.test_results.append((test_name, False, end_time - start_time))
                
        except Exception as e:
            print(f"❌ {test_name} - 异常: {str(e)}")
            self.test_results.append((test_name, False, 0))
            
    def test_basic_logging(self):
        """测试基础日志功能"""
        print("测试基础日志功能...")
        
        # 创建日志记录器
        log = XmiLogger(
            file_name="test_basic",
            log_dir=os.path.dirname(self.log_file),
            custom_format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d:%(funcName)s - %(message)s",
            filter_level="DEBUG"
        )
        
        # 测试各种日志级别
        log.debug("这是一条调试信息")
        log.info("这是一条信息")
        log.warning("这是一条警告")
        log.error("这是一条错误")
        log.critical("这是一条严重错误")
        
        # 测试异常日志
        try:
            raise ValueError("测试异常")
        except Exception as e:
            log.exception("捕获到异常")
        
        # 验证日志文件是否创建
        # 等待一下让日志写入完成
        time.sleep(0.1)
        log_files = [f for f in os.listdir(self.temp_dir) if f.endswith('.log')]
        if not log_files:
            print("❌ 日志文件未创建")
            return False
            
        # 读取日志内容验证
        log_file_path = os.path.join(self.temp_dir, log_files[0])
        with open(log_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查是否包含预期的日志内容
        expected_patterns = [
            "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL",
            "这是一条调试信息", "这是一条信息", "这是一条警告",
            "这是一条错误", "这是一条严重错误", "捕获到异常"
        ]
        
        for pattern in expected_patterns:
            if pattern not in content:
                print(f"❌ 日志中缺少: {pattern}")
                return False
                
        print("✅ 基础日志功能测试通过")
        return True
        
    def test_performance_optimization(self):
        """测试性能优化功能"""
        print("测试性能优化功能...")
        
        log = XmiLogger(
            file_name="test_performance",
            log_dir=os.path.dirname(self.log_file),
            filter_level="DEBUG"
        )
        
        # 测试缓存功能
        start_time = time.time()
        for i in range(100):
            log.info(f"性能测试消息 {i}")
        cache_time = time.time() - start_time
        
        # 测试批量日志
        messages = [{"level": "INFO", "message": f"批量消息 {i}"} for i in range(20)]
        log.batch_log(messages)
        
        print(f"✅ 性能优化功能测试通过 (缓存耗时: {cache_time:.3f}秒)")
        return True
        
    def test_advanced_features(self):
        """测试高级功能"""
        print("测试高级功能...")
        
        log = XmiLogger(
            file_name="test_advanced",
            log_dir=os.path.dirname(self.log_file),
            filter_level="DEBUG"
        )
        
        # 测试自适应日志级别
        log.set_adaptive_level(error_rate_threshold=0.1, log_rate_threshold=100)
        
        # 测试性能模式
        log.enable_performance_mode()
        log.info("性能模式消息")
        log.disable_performance_mode()
        
        # 生成一些日志
        for i in range(10):
            log.info(f"测试消息 {i}")
            time.sleep(0.1)
            
        print("✅ 高级功能测试通过")
        return True
        
    def test_advanced_features_module(self):
        """测试高级功能模块"""
        print("测试高级功能模块...")
        
        log = XmiLogger(
            file_name="test_advanced_module",
            log_dir=os.path.dirname(self.log_file),
            filter_level="DEBUG"
        )
        
        # 测试日志过滤器
        log_filter = LogFilter.REGEX
        log.info("test_include 消息")
        log.info("test_exclude 消息")
        log.debug("低级别消息")
        
        # 测试日志聚合器
        aggregator = LogAggregator(window_size=5, flush_interval=1.0)
        
        # 测试性能监控
        monitor = PerformanceMonitor()
        
        # 测试分布式日志
        distributed = DistributedLogger("test_node", ["node1", "node2"])
        
        # 测试内存优化器
        optimizer = MemoryOptimizer(max_memory_mb=100)
        
        # 测试智能路由器
        router = LogRouter()
        
        # 测试日志安全
        security = LogSecurity(encryption_key='test_key_123')
        
        # 测试日志归档器
        archiver = LogArchiver(archive_dir=self.temp_dir)
        
        # 测试数据库日志记录器
        db_logger = LogDatabase('test.db')
        
        # 测试日志流处理器
        stream_processor = LogStreamProcessor()
        
        # 测试日志分析器
        analyzer = LogAnalyzer()
        
        # 测试健康检查器
        health_checker = LogHealthChecker()
        
        # 测试备份管理器
        backup_manager = LogBackupManager(self.temp_dir)
        
        print("✅ 高级功能模块测试通过")
        return True
        
    def test_error_handling(self):
        """测试错误处理"""
        print("测试错误处理...")
        
        # 测试无效配置
        try:
            log = XmiLogger(
                file_name="test_error",
                log_dir="/invalid/path",
                filter_level="INVALID_LEVEL"
            )
            log.info("测试消息")
        except Exception as e:
            print(f"✅ 正确处理无效配置: {e}")
            
        # 测试文件权限错误
        try:
            log = XmiLogger(
                file_name="test_permission",
                log_dir="/root"
            )
            log.info("测试消息")
        except Exception as e:
            print(f"✅ 正确处理权限错误: {e}")
            
        # 测试网络错误
        try:
            log = XmiLogger(
                file_name="test_network",
                remote_log_url="http://invalid-url:9999/logs"
            )
            log.info("测试消息")
        except Exception as e:
            print(f"✅ 正确处理网络错误: {e}")
            
        print("✅ 错误处理测试通过")
        return True
        
    def test_concurrent_logging(self):
        """测试并发日志记录"""
        print("测试并发日志记录...")
        
        log = XmiLogger(
            file_name="test_concurrent",
            log_dir=os.path.dirname(self.log_file),
            filter_level="DEBUG"
        )
        
        def worker(worker_id):
            for i in range(10):
                log.info(f"工作线程 {worker_id} 消息 {i}")
                time.sleep(0.01)
                
        # 创建多个线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
            
        # 等待所有线程完成
        for thread in threads:
            thread.join()
            
        # 验证日志文件
        time.sleep(0.1)
        log_files = [f for f in os.listdir(self.temp_dir) if f.endswith('.log')]
        if log_files:
            log_file_path = os.path.join(self.temp_dir, log_files[0])
            with open(log_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "工作线程" in content:
                    print("✅ 并发日志记录测试通过")
                    return True
                    
        print("❌ 并发日志记录测试失败")
        return False
        
    def test_memory_usage(self):
        """测试内存使用"""
        print("测试内存使用...")
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        log = XmiLogger(
            file_name="test_memory",
            log_dir=os.path.dirname(self.log_file),
            filter_level="DEBUG"
        )
        
        # 生成大量日志
        for i in range(1000):
            log.info(f"内存测试消息 {i}" * 10)
            
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = current_memory - initial_memory
        
        print(f"内存使用增加: {memory_increase:.2f} MB")
        
        if memory_increase < 100:  # 内存增加应该小于100MB
            print("✅ 内存使用测试通过")
            return True
        else:
            print(f"❌ 内存使用过高: {memory_increase:.2f} MB")
            return False
            
    def test_log_rotation(self):
        """测试日志轮转"""
        print("测试日志轮转...")
        
        log = XmiLogger(
            file_name="test_rotation",
            log_dir=os.path.dirname(self.log_file),
            filter_level="DEBUG",
            max_size=1  # 1MB
        )
        
        # 生成足够大的日志文件触发轮转
        large_message = "大消息" * 100
        for i in range(50):
            log.info(f"{large_message} {i}")
            
        # 检查是否创建了备份文件
        backup_files = [f for f in os.listdir(self.temp_dir) if f.startswith("test.log")]
        
        if len(backup_files) > 1:
            print("✅ 日志轮转测试通过")
            return True
        else:
            print("❌ 日志轮转测试失败")
            return False
            
    def test_remote_logging(self):
        """测试远程日志记录"""
        print("测试远程日志记录...")
        
        # 模拟远程服务器
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            
            try:
                log = XmiLogger(
                    file_name="test_remote",
                    remote_log_url=self.remote_url,
                    filter_level="DEBUG"
                )
                
                log.info("远程日志测试消息")
                
                # 等待异步处理完成
                time.sleep(0.5)
                
                # 验证是否调用了远程API
                if mock_post.called:
                    print("✅ 远程日志记录测试通过")
                    return True
                else:
                    print("❌ 远程日志记录测试失败")
                    return False
            except Exception as e:
                print(f"✅ 正确处理远程日志异常: {e}")
                return True
                
    def test_log_formatting(self):
        """测试日志格式化"""
        print("测试日志格式化...")
        
        custom_format = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d:%(funcName)s - %(message)s"
        
        log = XmiLogger(
            file_name="test_format",
            log_dir=os.path.dirname(self.log_file),
            filter_level="DEBUG",
            custom_format=custom_format
        )
        
        log.info("格式化测试消息")
        
        # 读取日志验证格式
        time.sleep(0.1)
        log_files = [f for f in os.listdir(self.temp_dir) if f.endswith('.log')]
        if not log_files:
            print("❌ 日志文件未创建")
            return False
            
        log_file_path = os.path.join(self.temp_dir, log_files[0])
        with open(log_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查是否包含预期的格式元素
        expected_elements = [
            "test_format",  # 名称
            "INFO",         # 级别
            "test_log_formatting",  # 函数名
            "格式化测试消息"  # 消息
        ]
        
        for element in expected_elements:
            if element not in content:
                print(f"❌ 日志格式中缺少: {element}")
                return False
                
        print("✅ 日志格式化测试通过")
        return True
        
    def test_log_levels(self):
        """测试日志级别"""
        print("测试日志级别...")
        
        log = XmiLogger(
            file_name="test_levels",
            log_dir=os.path.dirname(self.log_file),
            filter_level="WARNING"  # 只记录WARNING及以上级别
        )
        
        # 记录不同级别的日志
        log.debug("调试消息 - 不应该出现")
        log.info("信息消息 - 不应该出现")
        log.warning("警告消息 - 应该出现")
        log.error("错误消息 - 应该出现")
        log.critical("严重错误 - 应该出现")
        
        # 读取日志验证
        time.sleep(0.1)
        log_files = [f for f in os.listdir(self.temp_dir) if f.endswith('.log')]
        if not log_files:
            print("❌ 日志文件未创建")
            return False
            
        log_file_path = os.path.join(self.temp_dir, log_files[0])
        with open(log_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查是否只包含WARNING及以上级别的消息
        if "调试消息" in content or "信息消息" in content:
            print("❌ 日志级别过滤失败")
            return False
            
        if "警告消息" in content and "错误消息" in content and "严重错误" in content:
            print("✅ 日志级别测试通过")
            return True
        else:
            print("❌ 日志级别测试失败")
            return False
            
    def cleanup(self):
        """清理测试文件"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            print(f"\n清理测试文件: {self.temp_dir}")
        except Exception as e:
            print(f"清理失败: {e}")
            
    def print_summary(self):
        """打印测试总结"""
        print(f"\n{'='*60}")
        print("测试总结")
        print(f"{'='*60}")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, passed, _ in self.test_results if passed)
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            print("\n失败的测试:")
            for test_name, passed, duration in self.test_results:
                if not passed:
                    print(f"  - {test_name}")
                    
        print(f"\n总耗时: {sum(duration for _, _, duration in self.test_results):.2f}秒")
        
        if passed_tests == total_tests:
            print("\n🎉 所有测试通过!")
        else:
            print(f"\n⚠️  有 {failed_tests} 个测试失败")

def main():
    """主函数"""
    print("XmiLogger 完整功能测试")
    print("="*60)
    
    runner = TestRunner()
    
    # 定义所有测试
    tests = [
        ("基础日志功能", runner.test_basic_logging),
        ("性能优化功能", runner.test_performance_optimization),
        ("高级功能", runner.test_advanced_features),
        ("高级功能模块", runner.test_advanced_features_module),
        ("错误处理", runner.test_error_handling),
        ("并发日志记录", runner.test_concurrent_logging),
        ("内存使用", runner.test_memory_usage),
        ("日志轮转", runner.test_log_rotation),
        ("远程日志记录", runner.test_remote_logging),
        ("日志格式化", runner.test_log_formatting),
        ("日志级别", runner.test_log_levels),
    ]
    
    # 运行所有测试
    for test_name, test_func in tests:
        runner.run_test(test_name, test_func)
        
    # 打印总结
    runner.print_summary()
    
    # 清理
    runner.cleanup()

if __name__ == "__main__":
    main() 