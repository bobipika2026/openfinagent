"""
统一日志系统

提供统一的日志框架，支持：
- 日志分级 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
- 日志持久化 (文件 + 控制台)
- 日志格式化 (时间、模块、级别、消息)
- 日志轮转 (按大小/时间)
- 日志查询和过滤

@module: utils.logger
@author: OpenFinAgent Team
@version: 0.4.0
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import json


class LogFormatter(logging.Formatter):
    """
    自定义日志格式化器
    
    支持彩色输出和详细格式
    """
    
    # ANSI 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m'        # 重置
    }
    
    # 详细格式 (文件用)
    DETAILED_FORMAT = (
        '%(asctime)s | '
        '%(levelname)-8s | '
        '%(name)s | '
        '%(funcName)s:%(lineno)d | '
        '%(message)s'
    )
    
    # 简洁格式 (控制台用)
    SIMPLE_FORMAT = (
        '%(asctime)s | '
        '%(levelname)-8s | '
        '%(message)s'
    )
    
    def __init__(self, colored: bool = False, detailed: bool = False):
        """
        初始化格式化器
        
        Args:
            colored: 是否使用彩色输出
            detailed: 是否使用详细格式
        """
        super().__init__()
        self.colored = colored
        self.detailed = detailed
        
        # 选择格式
        if detailed:
            self._fmt = self.DETAILED_FORMAT
        else:
            self._fmt = self.SIMPLE_FORMAT
        
        # 时间格式
        self.datefmt = '%Y-%m-%d %H:%M:%S'
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录"""
        # 基础格式化
        message = super().format(record)
        
        # 添加颜色
        if self.colored and record.levelname in self.COLORS:
            color = self.COLORS[record.levelname]
            reset = self.COLORS['RESET']
            message = message.replace(
                record.levelname,
                f'{color}{record.levelname}{reset}'
            )
        
        return message


class LoggerConfig:
    """日志配置"""
    
    def __init__(
        self,
        level: str = 'INFO',
        log_dir: str = '~/.openfinagent/logs',
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        console_output: bool = True,
        file_output: bool = True,
        json_output: bool = False
    ):
        """
        初始化日志配置
        
        Args:
            level: 日志级别
            log_dir: 日志文件目录
            max_bytes: 单个日志文件最大大小
            backup_count: 保留的备份文件数量
            console_output: 是否输出到控制台
            file_output: 是否输出到文件
            json_output: 是否输出 JSON 格式日志
        """
        self.level = getattr(logging, level.upper(), logging.INFO)
        self.log_dir = Path(log_dir).expanduser()
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.console_output = console_output
        self.file_output = file_output
        self.json_output = json_output


class LogManager:
    """
    日志管理器
    
    统一管理所有日志记录器
    """
    
    _instance = None
    _loggers: Dict[str, logging.Logger] = {}
    _config: Optional[LoggerConfig] = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self, config: Optional[LoggerConfig] = None) -> None:
        """
        初始化日志系统
        
        Args:
            config: 日志配置
        """
        if config is None:
            config = LoggerConfig()
        
        self._config = config
        
        # 创建日志目录
        if config.file_output:
            config.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置根日志记录器
        self._setup_root_logger()
    
    def _setup_root_logger(self) -> None:
        """配置根日志记录器"""
        root_logger = logging.getLogger()
        root_logger.setLevel(self._config.level)
        
        # 清除现有处理器
        root_logger.handlers.clear()
        
        # 添加控制台处理器
        if self._config.console_output:
            console_handler = self._create_console_handler()
            root_logger.addHandler(console_handler)
        
        # 添加文件处理器
        if self._config.file_output:
            file_handler = self._create_file_handler()
            root_logger.addHandler(file_handler)
            
            # 添加 JSON 文件处理器 (可选)
            if self._config.json_output:
                json_handler = self._create_json_handler()
                root_logger.addHandler(json_handler)
    
    def _create_console_handler(self) -> logging.StreamHandler:
        """创建控制台处理器"""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(self._config.level)
        
        # 使用彩色简洁格式
        formatter = LogFormatter(colored=True, detailed=False)
        handler.setFormatter(formatter)
        
        return handler
    
    def _create_file_handler(self) -> RotatingFileHandler:
        """创建文件处理器"""
        # 按日期生成日志文件名
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = self._config.log_dir / f'openfinagent_{date_str}.log'
        
        # 使用轮转文件处理器
        handler = RotatingFileHandler(
            log_file,
            maxBytes=self._config.max_bytes,
            backupCount=self._config.backup_count,
            encoding='utf-8'
        )
        handler.setLevel(self._config.level)
        
        # 使用详细格式
        formatter = LogFormatter(colored=False, detailed=True)
        handler.setFormatter(formatter)
        
        return handler
    
    def _create_json_handler(self) -> RotatingFileHandler:
        """创建 JSON 格式文件处理器"""
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = self._config.log_dir / f'openfinagent_{date_str}.json'
        
        handler = RotatingFileHandler(
            log_file,
            maxBytes=self._config.max_bytes,
            backupCount=self._config.backup_count,
            encoding='utf-8'
        )
        handler.setLevel(self._config.level)
        
        # JSON 格式化器
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    'timestamp': datetime.now().isoformat(),
                    'level': record.levelname,
                    'logger': record.name,
                    'function': f'{record.funcName}:{record.lineno}',
                    'message': record.getMessage(),
                }
                
                # 添加额外字段
                if hasattr(record, 'extra_data'):
                    log_data['extra'] = record.extra_data
                
                return json.dumps(log_data, ensure_ascii=False)
        
        handler.setFormatter(JSONFormatter())
        return handler
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        获取日志记录器
        
        Args:
            name: 日志记录器名称 (通常是模块名)
        
        Returns:
            日志记录器实例
        """
        if name not in self._loggers:
            logger = logging.getLogger(name)
            self._loggers[name] = logger
        
        return self._loggers[name]
    
    def set_level(self, level: str) -> None:
        """
        设置全局日志级别
        
        Args:
            level: 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        """
        log_level = getattr(logging, level.upper(), logging.INFO)
        
        # 设置根日志记录器级别
        logging.getLogger().setLevel(log_level)
        
        # 设置所有处理器级别
        for handler in logging.getLogger().handlers:
            handler.setLevel(log_level)
    
    def get_log_files(self) -> List[Path]:
        """
        获取所有日志文件
        
        Returns:
            日志文件路径列表
        """
        if not self._config or not self._config.file_output:
            return []
        
        return list(self._config.log_dir.glob('openfinagent_*.log'))
    
    def clear_old_logs(self, keep_days: int = 7) -> int:
        """
        清理旧日志文件
        
        Args:
            keep_days: 保留的天数
        
        Returns:
            删除的文件数量
        """
        if not self._config or not self._config.file_output:
            return 0
        
        cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        deleted_count = 0
        
        for log_file in self.get_log_files():
            # 从文件名提取日期
            try:
                date_str = log_file.stem.split('_')[1]
                file_date = datetime.strptime(date_str, '%Y%m%d').timestamp()
                
                if file_date < cutoff_date:
                    log_file.unlink()
                    deleted_count += 1
            except (IndexError, ValueError):
                # 文件名格式不正确，跳过
                continue
        
        return deleted_count


# 全局日志管理器实例
_log_manager = LogManager()


def init_logger(config: Optional[LoggerConfig] = None) -> None:
    """
    初始化日志系统
    
    Args:
        config: 日志配置
    """
    _log_manager.initialize(config)


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
    
    Returns:
        日志记录器实例
    """
    return _log_manager.get_logger(name)


def set_log_level(level: str) -> None:
    """
    设置全局日志级别
    
    Args:
        level: 日志级别
    """
    _log_manager.set_level(level)


def get_log_files() -> List[Path]:
    """
    获取所有日志文件
    
    Returns:
        日志文件路径列表
    """
    return _log_manager.get_log_files()


def clear_old_logs(keep_days: int = 7) -> int:
    """
    清理旧日志文件
    
    Args:
        keep_days: 保留的天数
    
    Returns:
        删除的文件数量
    """
    return _log_manager.clear_old_logs(keep_days)


# 便捷函数
def log_debug(logger: logging.Logger, message: str, **kwargs) -> None:
    """记录 DEBUG 日志"""
    if kwargs:
        logger.debug(message, extra={'extra_data': kwargs})
    else:
        logger.debug(message)


def log_info(logger: logging.Logger, message: str, **kwargs) -> None:
    """记录 INFO 日志"""
    if kwargs:
        logger.info(message, extra={'extra_data': kwargs})
    else:
        logger.info(message)


def log_warning(logger: logging.Logger, message: str, **kwargs) -> None:
    """记录 WARNING 日志"""
    if kwargs:
        logger.warning(message, extra={'extra_data': kwargs})
    else:
        logger.warning(message)


def log_error(logger: logging.Logger, message: str, **kwargs) -> None:
    """记录 ERROR 日志"""
    if kwargs:
        logger.error(message, extra={'extra_data': kwargs})
    else:
        logger.error(message)


def log_critical(logger: logging.Logger, message: str, **kwargs) -> None:
    """记录 CRITICAL 日志"""
    if kwargs:
        logger.critical(message, extra={'extra_data': kwargs})
    else:
        logger.critical(message)


# 自动初始化 (如果尚未初始化)
if not logging.getLogger().handlers:
    init_logger()
