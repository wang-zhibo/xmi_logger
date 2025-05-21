#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Author: zhibo.wang
# E-mail: gm.zhibo.wang@gmail.com
# Date  : 2025-01-03
# Desc  : Enhanced Logger with Loguru (with async support) + Language Option

import os
import sys
import inspect
import requests
import asyncio
import aiohttp

from typing import Optional, Dict, Any, Union, List, Tuple

from functools import wraps, lru_cache
from time import perf_counter
from contextvars import ContextVar
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from datetime import datetime, timedelta
import threading

from loguru import logger


class XmiLogger:
    """
    基于 Loguru 的增强日志记录器，具有以下功能：
    - 自定义日志格式
    - 日志轮转和保留策略
    - 上下文信息管理（如 request_id）
    - 远程日志收集（使用线程池防止阻塞）
    - 装饰器用于记录函数调用和执行时间，支持同步/异步函数
    - 自定义日志级别（避免与 Loguru 预定义的冲突）
    - 统一异常处理

    新增：
    - 可指定语言（中文/英文），默认中文
    - 支持按时间轮转日志
    - 支持自定义日志格式
    - 支持日志级别过滤
    - 支持自定义压缩格式
    - 支持自定义文件命名模式
    """

    # 在 _LANG_MAP 中添加新的语言项
    _LANG_MAP = {
        'zh': {
            'LOG_STATS': "日志统计: 总计 {total} 条, 错误 {error} 条, 警告 {warning} 条, 信息 {info} 条",
            'LOG_TAGGED': "[{tag}] {message}",
            'LOG_CATEGORY': "分类: {category} - {message}",
            'UNHANDLED_EXCEPTION': "未处理的异常",
            'FAILED_REMOTE': "远程日志发送失败: {error}",
            'START_FUNCTION_CALL': "开始函数调用",
            'END_FUNCTION_CALL': "结束函数调用",
            'START_ASYNC_FUNCTION_CALL': "开始异步函数调用",
            'END_ASYNC_FUNCTION_CALL': "结束异步函数调用",
            'CALLING_FUNCTION': "调用函数: {func}，参数: {args}，关键字参数: {kwargs}",
            'CALLING_ASYNC_FUNCTION': "调用异步函数: {func}，参数: {args}，关键字参数: {kwargs}",
            'FUNCTION_RETURNED': "函数 {func} 返回结果: {result}，耗时: {duration}秒",
            'ASYNC_FUNCTION_RETURNED': "异步函数 {func} 返回结果: {result}，耗时: {duration}秒",
        },
        'en': {
            'LOG_STATS': "Log statistics: Total {total}, Errors {error}, Warnings {warning}, Info {info}",
            'LOG_TAGGED': "[{tag}] {message}",
            'LOG_CATEGORY': "Category: {category} - {message}",
            'UNHANDLED_EXCEPTION': "Unhandled exception",
            'FAILED_REMOTE': "Remote logging failed: {error}",
            'START_FUNCTION_CALL': "Starting function call",
            'END_FUNCTION_CALL': "Ending function call",
            'START_ASYNC_FUNCTION_CALL': "Starting async function call",
            'END_ASYNC_FUNCTION_CALL': "Ending async function call",
            'CALLING_FUNCTION': "Calling function: {func}, args: {args}, kwargs: {kwargs}",
            'CALLING_ASYNC_FUNCTION': "Calling async function: {func}, args: {args}, kwargs: {kwargs}",
            'FUNCTION_RETURNED': "Function {func} returned: {result}, duration: {duration}s",
            'ASYNC_FUNCTION_RETURNED': "Async function {func} returned: {result}, duration: {duration}s",
        }
    }

    # 添加类级别的缓存
    _format_cache: Dict[str, str] = {}
    _message_cache: Dict[str, str] = {}

    def __init__(
        self,
        file_name: str,
        log_dir: str = 'logs',
        max_size: int = 14,        # 单位：MB
        retention: str = '7 days',
        remote_log_url: Optional[str] = None,
        max_workers: int = 3,
        work_type: bool = False,
        language: str = 'zh',      # 语言选项，默认为中文
        rotation_time: Optional[str] = None,  # 新增：按时间轮转，如 "1 day", "1 week"
        custom_format: Optional[str] = None,  # 新增：自定义日志格式
        filter_level: str = "DEBUG",  # 新增：日志过滤级别
        compression: str = "zip",   # 新增：压缩格式，支持 zip, gz, tar
        enable_stats: bool = False,  # 新增：是否启用日志统计
        categories: Optional[list] = None,  # 新增：日志分类列表
        cache_size: int = 128,  # 新增：缓存大小配置
    ) -> None:
        """
        初始化日志记录器。

        Args:
            file_name (str): 日志文件名称（主日志文件前缀）。
            log_dir (str): 日志文件目录。
            max_size (int): 日志文件大小（MB）超过时进行轮转。
            retention (str): 日志保留策略。
            remote_log_url (str, optional): 远程日志收集的URL。如果提供，将启用远程日志收集。
            max_workers (int): 线程池的最大工作线程数。
            work_type (bool): False 测试环境
            language (str): 'zh' 或 'en'，表示日志输出语言，默认为中文。
        """
        self.file_name = file_name
        self.log_dir = log_dir
        self.max_size = max_size
        self.retention = retention
        self.remote_log_url = remote_log_url
        
        # 保存新增的参数为实例属性
        self.rotation_time = rotation_time
        self.custom_format = custom_format
        self.filter_level = filter_level
        self.compression = compression
        self.enable_stats = enable_stats
        self.categories = categories or []
        self._cache_size = cache_size
        self._async_queue = asyncio.Queue() if remote_log_url else None
        self._remote_task = None
        if self._async_queue:
            self._start_remote_worker()

        # 语言选项
        self.language = language if language in ('zh', 'en') else 'zh'

        # 定义上下文变量，用于存储 request_id
        self.request_id_var = ContextVar("request_id", default="no-request-id")

        # 使用 patch 确保每条日志记录都包含 'request_id'
        self.logger = logger.patch(
            lambda record: record["extra"].update(
                request_id=self.request_id_var.get() or "no-request-id"
            )
        )
        if work_type:
            self.enqueue = False
            self.diagnose = False
            self.backtrace = False
        else:
            self.enqueue = True
            self.diagnose = True
            self.backtrace = True

        # 用于远程日志发送的线程池
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

        # 初始化 Logger 配置
        self.configure_logger()

        self._stats_lock = threading.Lock()
        self._stats = {
            'total': 0,
            'error': 0,
            'warning': 0,
            'info': 0,
            'debug': 0,
            'by_category': defaultdict(int),
            'by_hour': defaultdict(int),
            'errors': [],
            'last_error_time': None,
            'error_rate': 0.0
        }
        self._stats_start_time = datetime.now()

    def _msg(self, key: str, **kwargs) -> str:
        """消息格式化处理"""
        try:
            # 获取消息模板
            text = self._LANG_MAP.get(self.language, {}).get(key, key)
            
            # 将所有参数转换为字符串
            str_kwargs = {}
            for k, v in kwargs.items():
                try:
                    if isinstance(v, (list, tuple)):
                        str_kwargs[k] = [str(item) for item in v]
                    elif isinstance(v, dict):
                        str_kwargs[k] = {str(kk): str(vv) for kk, vv in v.items()}
                    else:
                        str_kwargs[k] = str(v)
                except Exception:
                    str_kwargs[k] = f"<{type(v).__name__}>"
            
            # 格式化消息
            return text.format(**str_kwargs)
            
        except KeyError as e:
            return f"{text} (格式化错误: 缺少参数 {e})"
        except Exception as e:
            return f"{text} (格式化错误: {str(e)})"

    def configure_logger(self) -> None:
        """配置日志记录器，添加错误处理和安全性检查"""
        try:
            # 移除所有现有的处理器
            self.logger.remove()
            
            # 验证配置参数
            self._validate_config()
            
            # 确保日志目录存在且可写
            self._ensure_log_directory()
            
            # 配置日志格式
            log_format = self._get_log_format()
            
            # 添加控制台处理器
            self._add_console_handler(log_format)
            
            # 添加文件处理器
            self._add_file_handlers(log_format)
            
            # 配置远程日志（如果启用）
            if self.remote_log_url:
                self._configure_remote_logging()
            
            # 设置异常处理器
            self.setup_exception_handler()
            
        except Exception as e:
            # 如果配置失败，使用基本配置
            self._fallback_configuration()
            raise RuntimeError(f"日志配置失败: {str(e)}")
    
    def _validate_config(self) -> None:
        """验证配置参数"""
        if not isinstance(self.max_size, int) or self.max_size <= 0:
            raise ValueError("max_size 必须是正整数")
        
        if not isinstance(self.retention, str):
            raise ValueError("retention 必须是字符串")
        
        if self.remote_log_url and not self.remote_log_url.startswith(('http://', 'https://')):
            raise ValueError("remote_log_url 必须是有效的 HTTP(S) URL")
        
        if self.language not in ('zh', 'en'):
            raise ValueError("language 必须是 'zh' 或 'en'")
        
        if self.compression not in ('zip', 'gz', 'tar'):
            raise ValueError("compression 必须是 'zip', 'gz' 或 'tar'")
    
    def _ensure_log_directory(self) -> None:
        """确保日志目录存在且可写"""
        try:
            os.makedirs(self.log_dir, exist_ok=True)
            # 测试目录是否可写
            test_file = os.path.join(self.log_dir, '.write_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except (OSError, IOError) as e:
            raise RuntimeError(f"无法创建或写入日志目录: {str(e)}")
    
    def _get_log_format(self) -> str:
        """获取日志格式"""
        if self.custom_format:
            return self.custom_format
        
        return (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "ReqID:{extra[request_id]} | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )
    
    def _add_console_handler(self, log_format: str) -> None:
        """添加控制台处理器"""
        self.logger.add(
            sys.stdout,
            format=log_format,
            level=self.filter_level,
            enqueue=self.enqueue,
            diagnose=self.diagnose,
            backtrace=self.backtrace,
        )
    
    def _add_file_handlers(self, log_format: str) -> None:
        """添加文件处理器"""
        # 主日志文件
        self.logger.add(
            os.path.join(self.log_dir, f"{self.file_name}.log"),
            format=log_format,
            level=self.filter_level,
            rotation=self.rotation_time or f"{self.max_size} MB",
            retention=self.retention,
            compression=self.compression,
            encoding='utf-8',
            enqueue=self.enqueue,
            diagnose=self.diagnose,
            backtrace=self.backtrace,
        )
        
        # 错误日志文件
        self.logger.add(
            self._get_level_log_path("error"),
            format=log_format,
            level="ERROR",
            rotation=f"{self.max_size} MB",
            retention=self.retention,
            compression=self.compression,
            encoding='utf-8',
            enqueue=self.enqueue,
            diagnose=self.diagnose,
            backtrace=self.backtrace,
        )
    
    def _fallback_configuration(self) -> None:
        """配置失败时的后备方案"""
        self.logger.remove()
        self.logger.add(
            sys.stderr,
            format="<red>{time:YYYY-MM-DD HH:mm:ss}</red> | <level>{level: <8}</level> | <level>{message}</level>",
            level="ERROR"
        )

    def _configure_remote_logging(self):
        """
        配置远程日志收集。
        """
        # 当远程日志收集启用时，只发送 ERROR 及以上级别的日志
        self.logger.add(
            self.remote_sink,
            level="ERROR",
            enqueue=self.enqueue,
        )

    def log_with_tag(self, level: str, message: str, tag: str):
        """
        使用标签记录日志消息。
        
        Args:
            level: 日志级别 (info, debug, warning, error, critical)
            message: 日志消息
            tag: 标签名称
        """
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        tagged_message = self._msg('LOG_TAGGED', tag=tag, message=message)
        log_method(tagged_message)
    
    def log_with_category(self, level: str, message: str, category: str):
        """
        使用分类记录日志消息。
        
        Args:
            level: 日志级别 (info, debug, warning, error, critical)
            message: 日志消息
            category: 分类名称
        """
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        categorized_message = self._msg('LOG_CATEGORY', category=category, message=message)
        log_method(categorized_message)
    
    def setup_exception_handler(self):
        """
        设置统一的异常处理函数，将未处理的异常记录到日志。
        """
        def exception_handler(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                # 允许程序被 Ctrl+C 中断
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            try:
                # 安全地格式化异常信息
                error_msg = self._msg('UNHANDLED_EXCEPTION') if 'UNHANDLED_EXCEPTION' in self._LANG_MAP[self.language] else "未处理的异常"
                
                # 安全地格式化异常值
                exc_value_str = str(exc_value) if exc_value is not None else "None"
                
                # 组合错误消息
                full_error_msg = f"{error_msg}: {exc_type.__name__}: {exc_value_str}"
                
                # 记录错误
                self.logger.opt(exception=True).error(full_error_msg)
            except Exception as e:
                # 如果格式化失败，使用最基本的错误记录
                self.logger.opt(exception=True).error(f"未处理的异常: {exc_type.__name__}")

        sys.excepthook = exception_handler

    def _get_level_log_path(self, level_name):
        """
        获取不同级别日志文件的路径。
        """
        return os.path.join(self.log_dir, f"{self.file_name}_{level_name}.log")

    def get_log_path(self, message):
        """
        如果需要将所有日志按照级别分文件时，可使用此方法。
        """
        log_level = message.record["level"].name.lower()
        log_file = f"{log_level}.log"
        return os.path.join(self.log_dir, log_file)

    def _start_remote_worker(self):
        """启动异步远程日志工作器"""
        async def remote_worker():
            while True:
                try:
                    message = await self._async_queue.get()
                    await self._send_to_remote_async(message)
                    self._async_queue.task_done()
                except Exception as e:
                    self.logger.error(f"远程日志工作器错误: {e}")
                await asyncio.sleep(0.1)
        
        self._remote_task = asyncio.create_task(remote_worker())
    
    async def _send_to_remote_async(self, message: Any) -> None:
        """异步发送日志到远程服务器"""
        log_entry = message.record
        payload = {
            "time": log_entry["time"].strftime("%Y-%m-%d %H:%M:%S"),
            "level": log_entry["level"].name,
            "message": log_entry["message"],
            "file": os.path.basename(log_entry["file"].path) if log_entry["file"] else "",
            "line": log_entry["line"],
            "function": log_entry["function"],
            "request_id": log_entry["extra"].get("request_id", "no-request-id")
        }
        
        async with aiohttp.ClientSession() as session:
            for attempt in range(3):
                try:
                    async with session.post(
                        self.remote_log_url,
                        json=payload,
                        timeout=5
                    ) as response:
                        response.raise_for_status()
                        return
                except Exception as e:
                    if attempt == 2:
                        self.logger.warning(
                            self._msg('FAILED_REMOTE', error=f"最终尝试失败: {e}")
                        )
                    await asyncio.sleep(1 * (attempt + 1))
    
    def remote_sink(self, message):
        """优化的远程日志处理器"""
        if self._async_queue:
            asyncio.create_task(self._async_queue.put(message))
        else:
            self._executor.submit(self._send_to_remote, message)

    def _send_to_remote(self, message) -> None:
        """Send log message to remote server with retry logic.
        
        Args:
            message: Log message to send
            
        Returns:
            None
        """
        """
        线程池中实际执行的远程日志发送逻辑。
        """
        log_entry = message.record
        payload = {
            "time": log_entry["time"].strftime("%Y-%m-%d %H:%M:%S"),
            "level": log_entry["level"].name,
            "message": log_entry["message"],
            "file": os.path.basename(log_entry["file"].path) if log_entry["file"] else "",
            "line": log_entry["line"],
            "function": log_entry["function"],
            "request_id": log_entry["extra"].get("request_id", "no-request-id")
        }
        headers = {"Content-Type": "application/json"}

        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.remote_log_url,
                    headers=headers,
                    json=payload,
                    timeout=5
                )
                response.raise_for_status()
                return
            except requests.RequestException as e:
                if attempt == max_retries - 1:  # Last attempt
                    self.logger.warning(
                        self._msg('FAILED_REMOTE', error=f"Final attempt failed: {e}")
                    )
                else:
                    time.sleep(retry_delay * (attempt + 1))

    def add_custom_level(self, level_name, no, color, icon):
        """
        增加自定义日志级别。

        Args:
            level_name (str): 日志级别名称。
            no (int): 日志级别编号。
            color (str): 日志级别颜色。
            icon (str): 日志级别图标。
        """
        try:
            self.logger.level(level_name, no=no, color=color, icon=icon)
            self.logger.debug(f"Custom log level '{level_name}' added.")
        except TypeError:
            # 如果日志级别已存在，记录调试信息
            self.logger.debug(f"Log level '{level_name}' already exists, skipping.")

    def __getattr__(self, level: str):
        """
        使 MyLogger 支持直接调用 Loguru 的日志级别方法。

        Args:
            level (str): 日志级别方法名称。
        """
        return getattr(self.logger, level)

    def log_decorator(self, msg: Optional[str] = None, level: str = "ERROR", trace: bool = True):
        """
        增强版日志装饰器，支持自定义日志级别和跟踪配置

        Args:
            msg (str): 支持多语言的异常提示信息key（使用_LANG_MAP中的键）
            level (str): 记录异常的日志级别（默认ERROR）
            trace (bool): 是否记录完整堆栈跟踪（默认True）
        """
        def decorator(func):
            _msg_key = msg or 'UNHANDLED_EXCEPTION'
            log_level = level.upper()

            if inspect.iscoroutinefunction(func):
                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    self._log_start(func.__name__, args, kwargs, is_async=True)
                    start_time = perf_counter()
                    try:
                        result = await func(*args, **kwargs)
                        duration = perf_counter() - start_time
                        self._log_end(func.__name__, result, duration, is_async=True)
                        return result
                    except Exception as e:
                        self._log_exception(func.__name__, e, _msg_key, log_level, trace, is_async=True)
                        if trace:
                            raise
                        return None
                return async_wrapper
            else:
                @wraps(func)
                def sync_wrapper(*args, **kwargs):
                    self._log_start(func.__name__, args, kwargs, is_async=False)
                    start_time = perf_counter()
                    try:
                        result = func(*args, **kwargs)
                        duration = perf_counter() - start_time
                        self._log_end(func.__name__, result, duration, is_async=False)
                        return result
                    except Exception as e:
                        self._log_exception(func.__name__, e, _msg_key, log_level, trace, is_async=False)
                        if trace:
                            raise
                        return None
                return sync_wrapper
        return decorator

    def _log_exception(self, func_name: str, error: Exception, msg_key: str,
                     level: str, trace: bool, is_async: bool):
        """统一的异常记录处理"""
        try:
            log_method = getattr(self.logger, level.lower(), self.logger.error)
            
            # 安全地获取消息
            error_msg = self._msg(msg_key) if msg_key in self._LANG_MAP[self.language] else f"发生异常: {msg_key}"
            
            # 安全地格式化错误信息
            error_type = type(error).__name__
            error_value = str(error) if error is not None else "None"
            
            # 组合错误消息
            full_error_msg = f"{error_msg} [{error_type}]: {error_value}"

            if trace:
                # 记录错误消息
                log_method(full_error_msg)
                # 单独记录异常堆栈
                self.logger.opt(exception=True).error("异常堆栈:")
            else:
                log_method(full_error_msg)

            # 记录函数调用结束
            end_msg = self._msg('END_ASYNC_FUNCTION_CALL' if is_async else 'END_FUNCTION_CALL')
            self.logger.info(end_msg)
            
        except Exception as e:
            # 如果格式化失败，使用最基本的错误记录
            self.logger.error(f"记录异常时发生错误: {str(e)}")
            if trace:
                self.logger.opt(exception=True).error("原始异常堆栈:")

    def _log_start(self, func_name, args, kwargs, is_async=False):
        """
        记录函数调用开始的公共逻辑。
        """
        def format_arg(arg):
            try:
                return str(arg)
            except Exception:
                return f"<{type(arg).__name__}>"

        # 安全地格式化参数
        args_str = [format_arg(arg) for arg in args]
        kwargs_str = {k: format_arg(v) for k, v in kwargs.items()}
        
        if is_async:
            self.logger.info(self._msg('START_ASYNC_FUNCTION_CALL'))
            self.logger.info(
                self._msg('CALLING_ASYNC_FUNCTION', 
                         func=func_name, 
                         args=args_str, 
                         kwargs=kwargs_str)
            )
        else:
            self.logger.info(self._msg('START_FUNCTION_CALL'))
            self.logger.info(
                self._msg('CALLING_FUNCTION', 
                         func=func_name, 
                         args=args_str, 
                         kwargs=kwargs_str)
            )

    def _log_end(self, func_name, result, duration, is_async=False):
        """
        记录函数调用结束的公共逻辑。
        """
        def format_result(res):
            try:
                return str(res)
            except Exception:
                return f"<{type(res).__name__}>"

        # 安全地格式化结果和持续时间
        result_str = format_result(result)
        duration_str = f"{duration:.6f}"  # 格式化持续时间为6位小数
        
        if is_async:
            self.logger.info(
                self._msg('ASYNC_FUNCTION_RETURNED', 
                         func=func_name, 
                         result=result_str, 
                         duration=duration_str)
            )
            self.logger.info(self._msg('END_ASYNC_FUNCTION_CALL'))
        else:
            self.logger.info(
                self._msg('FUNCTION_RETURNED', 
                         func=func_name, 
                         result=result_str, 
                         duration=duration_str)
            )
            self.logger.info(self._msg('END_FUNCTION_CALL'))
            
    def _update_stats(self, level: str, category: Optional[str] = None) -> None:
        """更新日志统计信息"""
        if not self.enable_stats:
            return
            
        with self._stats_lock:
            self._stats['total'] += 1
            self._stats[level.lower()] += 1
            
            if category:
                self._stats['by_category'][category] += 1
            
            current_hour = datetime.now().strftime('%Y-%m-%d %H:00')
            self._stats['by_hour'][current_hour] += 1
            
            if level.upper() == 'ERROR':
                self._stats['errors'].append({
                    'time': datetime.now(),
                    'message': f"Error occurred at {current_hour}"
                })
                self._stats['last_error_time'] = datetime.now()
                
                # 计算错误率
                total_time = (datetime.now() - self._stats_start_time).total_seconds()
                if total_time > 0:
                    self._stats['error_rate'] = self._stats['error'] / total_time
    
    def get_stats(self) -> Dict[str, Any]:
        """获取详细的日志统计信息"""
        with self._stats_lock:
            stats = {
                'total': self._stats['total'],
                'error': self._stats['error'],
                'warning': self._stats['warning'],
                'info': self._stats['info'],
                'debug': self._stats['debug'],
                'duration': str(datetime.now() - self._stats_start_time),
                'by_category': dict(self._stats['by_category']),
                'by_hour': dict(self._stats['by_hour']),
                'error_rate': float(self._stats['error_rate']),
                'time_since_last_error': str(datetime.now() - self._stats['last_error_time']) if self._stats['last_error_time'] else None
            }
            
            # 计算每小时的平均日志数
            if stats['by_hour']:
                stats['avg_logs_per_hour'] = sum(stats['by_hour'].values()) / len(stats['by_hour'])
            
            # 获取最近的错误
            if self._stats['errors']:
                stats['recent_errors'] = [
                    {
                        'time': str(error['time']),
                        'message': str(error['message'])
                    }
                    for error in self._stats['errors'][-10:]
                ]
            
            return stats
    
    def get_stats_summary(self) -> str:
        """获取统计信息的摘要"""
        stats = self.get_stats()
        return self._msg('LOG_STATS',
            total=stats['total'],
            error=stats['error'],
            warning=stats['warning'],
            info=stats['info']
        )
    
    def get_error_trend(self) -> List[Tuple[str, int]]:
        """获取错误趋势数据"""
        with self._stats_lock:
            return sorted(
                [(hour, count) for hour, count in self._stats['by_hour'].items()],
                key=lambda x: x[0]
            )
    
    def get_category_distribution(self) -> Dict[str, int]:
        """获取日志分类分布"""
        with self._stats_lock:
            return dict(self._stats['by_category'])
    
    def reset_stats(self) -> None:
        """重置统计信息"""
        with self._stats_lock:
            self._stats = {
                'total': 0,
                'error': 0,
                'warning': 0,
                'info': 0,
                'debug': 0,
                'by_category': defaultdict(int),
                'by_hour': defaultdict(int),
                'errors': [],
                'last_error_time': None,
                'error_rate': 0.0
            }
            self._stats_start_time = datetime.now()



"""
# ==========================
# 以下为使用示例
# ==========================
if __name__ == '__main__':
    import time
    import json
    import asyncio
    import random

    # 自定义日志格式
    custom_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "ReqID:{extra[request_id]} | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<magenta>{process}</magenta> - "
        "<level>{message}</level>"
    )

    # 初始化日志记录器，使用新功能
    log = XmiLogger(
        "test_log",
        rotation_time="1 day",           # 每天轮转
        custom_format=custom_format,     # 自定义格式
        filter_level="DEBUG",            # 日志级别
        compression="zip",               # 压缩格式
        enable_stats=True,               # 启用统计
        categories=["api", "db", "ui"]   # 日志分类
    )

    # 添加自定义日志级别
    log.add_custom_level("IMPORTANT", no=25, color="<yellow>", icon="⚠️")

    @log.log_decorator("除零错误", level="ERROR")
    def test_zero_division_error(a, b):
        return a / b

    @log.log_decorator("JSON解析错误", level="WARNING")
    def test_error():
        json.loads("invalid_json")

    @log.log_decorator("耗时操作", level="INFO", trace=False)
    def compute_something_sync():
        time.sleep(1)
        return "同步计算完成"

    @log.log_decorator("异步耗时操作")
    async def compute_something_async():
        await asyncio.sleep(1)
        return "异步计算完成"

    @log.log_decorator("生成随机数", level="INFO", trace=False)
    def generate_random_number(min_val=1, max_val=100):
        return random.randint(min_val, max_val)

    # 设置请求ID
    token = log.request_id_var.set("🦉")

    try:
        # 基本日志测试
        xxx = "X"
        log.info(f'这是一条信息日志{xxx}')
        log.debug(f'这是一条调试日志{xxx}')
        log.warning(f'这是一条警告日志{xxx}')
        log.error(f'这是一条错误日志{xxx}')
        log.critical(f'这是一条严重错误日志{xxx}')
        
        # 使用自定义日志级别
        log.log("IMPORTANT", "这是一条重要日志消息")
        
        # 使用标签功能
        log.log_with_tag("INFO", "这是带标签的日志", "FEATURE")
        log.log_with_tag("WARNING", "这是带标签的警告", "DEPRECATED")
        
        # 使用分类功能
        log.log_with_category("INFO", "数据库连接成功", "db")
        log.log_with_category("ERROR", "API请求失败", "api")
        log.log_with_category("DEBUG", "UI组件渲染", "ui")

        # 测试异常处理
        try:
            result = test_zero_division_error(1, 0)
        except ZeroDivisionError:
            log.exception("捕获到除零错误")

        try:
            result = test_error()
        except json.JSONDecodeError:
            log.exception("捕获到JSON解析错误")

        # 测试同步函数
        result = compute_something_sync()
        log.info('同步计算结果: {}'.format(result))
        
        # 测试随机数生成
        for _ in range(3):
            num = generate_random_number(1, 1000)
            log.info('生成的随机数: {}'.format(num))

        # 测试异步函数
        async def main():
            # 单个异步任务
            result = await compute_something_async()
            log.info('异步计算结果: {}'.format(result))
            
            # 多个并发异步任务
            tasks = [compute_something_async() for _ in range(3)]
            results = await asyncio.gather(*tasks)
            log.info('多任务异步结果: {}'.format(results))

        asyncio.run(main())
        
        # 输出日志统计
        print("\n日志统计信息:")
        print(json.dumps(log.get_stats(), indent=2, ensure_ascii=False))

    finally:
        # 重置请求ID
        log.request_id_var.reset(token)
        log.info("测试完成")

"""

