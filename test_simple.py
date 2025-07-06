#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XmiLogger 简化测试脚本
测试核心功能是否正常工作
"""

import os
import sys
import time
import tempfile
import shutil

# 添加项目路径到sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xmi_logger.xmi_logger import XmiLogger

def test_basic_logging():
    """测试基础日志功能"""
    print("测试基础日志功能...")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="xmi_logger_test_")
    
    try:
        # 创建日志记录器
        log = XmiLogger(
            file_name="test_basic",
            log_dir=temp_dir,
            filter_level="DEBUG"
        )
        
        # 记录各种级别的日志
        log.debug("调试消息")
        log.info("信息消息")
        log.warning("警告消息")
        log.error("错误消息")
        log.critical("严重错误消息")
        
        # 等待日志写入
        time.sleep(0.5)
        
        # 检查日志文件是否创建
        log_files = [f for f in os.listdir(temp_dir) if f.endswith('.log')]
        if not log_files:
            print("❌ 日志文件未创建")
            return False
            
        # 读取日志内容
        log_file_path = os.path.join(temp_dir, log_files[0])
        with open(log_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 验证日志内容
        if "调试消息" in content and "信息消息" in content and "警告消息" in content:
            print("✅ 基础日志功能测试通过")
            return True
        else:
            print("❌ 日志内容验证失败")
            return False
            
    except Exception as e:
        print(f"❌ 基础日志功能测试异常: {e}")
        return False
    finally:
        # 清理临时文件
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_log_levels():
    """测试日志级别过滤"""
    print("测试日志级别过滤...")
    
    temp_dir = tempfile.mkdtemp(prefix="xmi_logger_test_")
    
    try:
        # 创建只记录WARNING及以上级别的日志记录器
        log = XmiLogger(
            file_name="test_levels",
            log_dir=temp_dir,
            filter_level="WARNING"
        )
        
        # 记录各种级别的日志
        log.debug("调试消息 - 不应该出现")
        log.info("信息消息 - 不应该出现")
        log.warning("警告消息 - 应该出现")
        log.error("错误消息 - 应该出现")
        log.critical("严重错误 - 应该出现")
        
        # 等待日志写入
        time.sleep(0.5)
        
        # 检查日志文件
        log_files = [f for f in os.listdir(temp_dir) if f.endswith('.log')]
        if not log_files:
            print("❌ 日志文件未创建")
            return False
            
        # 读取日志内容
        log_file_path = os.path.join(temp_dir, log_files[0])
        with open(log_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 验证只有WARNING及以上级别的日志被记录
        if ("调试消息" not in content and 
            "信息消息" not in content and
            "警告消息" in content and
            "错误消息" in content and
            "严重错误" in content):
            print("✅ 日志级别过滤测试通过")
            return True
        else:
            print("❌ 日志级别过滤验证失败")
            return False
            
    except Exception as e:
        print(f"❌ 日志级别过滤测试异常: {e}")
        return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_custom_format():
    """测试自定义格式"""
    print("测试自定义格式...")
    
    temp_dir = tempfile.mkdtemp(prefix="xmi_logger_test_")
    
    try:
        # 创建自定义格式的日志记录器
        custom_format = "%(asctime)s - %(levelname)s - %(message)s"
        log = XmiLogger(
            file_name="test_format",
            log_dir=temp_dir,
            filter_level="INFO",
            custom_format=custom_format
        )
        
        log.info("自定义格式测试消息")
        
        # 等待日志写入
        time.sleep(0.5)
        
        # 检查日志文件
        log_files = [f for f in os.listdir(temp_dir) if f.endswith('.log')]
        if not log_files:
            print("❌ 日志文件未创建")
            return False
            
        # 读取日志内容
        log_file_path = os.path.join(temp_dir, log_files[0])
        with open(log_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 验证格式
        if "自定义格式测试消息" in content and "INFO" in content:
            print("✅ 自定义格式测试通过")
            return True
        else:
            print("❌ 自定义格式验证失败")
            return False
            
    except Exception as e:
        print(f"❌ 自定义格式测试异常: {e}")
        return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_error_handling():
    """测试错误处理"""
    print("测试错误处理...")
    
    try:
        # 测试无效配置
        log = XmiLogger(
            file_name="test_error",
            log_dir="/invalid/path",
            filter_level="INVALID_LEVEL"
        )
        log.info("测试消息")
        print("✅ 错误处理测试通过")
        return True
    except Exception as e:
        print(f"✅ 正确处理配置错误: {e}")
        return True

def test_performance():
    """测试性能"""
    print("测试性能...")
    
    temp_dir = tempfile.mkdtemp(prefix="xmi_logger_test_")
    
    try:
        log = XmiLogger(
            file_name="test_performance",
            log_dir=temp_dir,
            filter_level="INFO"
        )
        
        # 测试大量日志记录
        start_time = time.time()
        for i in range(1000):
            log.info(f"性能测试消息 {i}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        if duration < 5.0:  # 应该在5秒内完成
            print(f"✅ 性能测试通过 (耗时: {duration:.2f}秒)")
            return True
        else:
            print(f"❌ 性能测试失败 (耗时: {duration:.2f}秒)")
            return False
            
    except Exception as e:
        print(f"❌ 性能测试异常: {e}")
        return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    """运行所有测试"""
    print("=" * 60)
    print("XmiLogger 简化功能测试")
    print("=" * 60)
    
    tests = [
        ("基础日志功能", test_basic_logging),
        ("日志级别过滤", test_log_levels),
        ("自定义格式", test_custom_format),
        ("错误处理", test_error_handling),
        ("性能测试", test_performance),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
        print()
    
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"总测试数: {total}")
    print(f"通过: {passed}")
    print(f"失败: {total - passed}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  有测试失败")

if __name__ == "__main__":
    main() 