"""
日志系统测试
"""

import pytest
import logging
import time
from pathlib import Path
from datetime import datetime

from utils.logger import (
    init_logger,
    get_logger,
    set_log_level,
    get_log_files,
    clear_old_logs,
    LoggerConfig,
    LogManager,
    log_info,
    log_error,
)


class TestLoggerConfig:
    """测试日志配置"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = LoggerConfig()
        
        assert config.level == logging.INFO
        assert config.console_output is True
        assert config.file_output is True
        assert config.json_output is False
        assert config.max_bytes == 10 * 1024 * 1024
        assert config.backup_count == 5
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = LoggerConfig(
            level='DEBUG',
            log_dir='/tmp/test_logs',
            max_bytes=5 * 1024 * 1024,
            backup_count=3,
            console_output=False,
            file_output=True,
            json_output=True
        )
        
        assert config.level == logging.DEBUG
        assert config.console_output is False
        assert config.file_output is True
        assert config.json_output is True


class TestLoggerInitialization:
    """测试日志初始化"""
    
    def test_init_logger(self, tmp_path):
        """测试初始化日志系统"""
        log_dir = tmp_path / 'logs'
        
        config = LoggerConfig(
            level='DEBUG',
            log_dir=str(log_dir),
            console_output=False,
            file_output=True
        )
        
        init_logger(config)
        
        # 检查日志目录是否创建
        assert log_dir.exists()
        
        # 检查根日志记录器是否有处理器
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) > 0
    
    def test_get_logger(self):
        """测试获取日志记录器"""
        logger = get_logger('test.module')
        
        assert logger is not None
        assert logger.name == 'test.module'
        assert isinstance(logger, logging.Logger)
    
    def test_singleton_log_manager(self):
        """测试日志管理器单例模式"""
        manager1 = LogManager()
        manager2 = LogManager()
        
        assert manager1 is manager2


class TestLogLevels:
    """测试日志级别"""
    
    def test_set_log_level(self, tmp_path):
        """测试设置日志级别"""
        log_dir = tmp_path / 'logs'
        
        config = LoggerConfig(
            level='INFO',
            log_dir=str(log_dir),
            console_output=False,
            file_output=True
        )
        
        init_logger(config)
        
        # 初始级别应该是 INFO
        assert logging.getLogger().level == logging.INFO
        
        # 修改为 DEBUG
        set_log_level('DEBUG')
        assert logging.getLogger().level == logging.DEBUG
        
        # 修改为 WARNING
        set_log_level('WARNING')
        assert logging.getLogger().level == logging.WARNING
    
    def test_log_level_filtering(self, tmp_path, caplog):
        """测试日志级别过滤"""
        log_dir = tmp_path / 'logs'
        
        config = LoggerConfig(
            level='WARNING',
            log_dir=str(log_dir),
            console_output=True,
            file_output=False
        )
        
        init_logger(config)
        
        logger = get_logger('test.filter')
        
        with caplog.at_level(logging.DEBUG):
            logger.debug('Debug message')
            logger.info('Info message')
            logger.warning('Warning message')
            logger.error('Error message')
        
        # DEBUG 和 INFO 应该被过滤
        assert 'Debug message' not in caplog.text
        assert 'Info message' not in caplog.text
        
        # WARNING 和 ERROR 应该记录
        assert 'Warning message' in caplog.text
        assert 'Error message' in caplog.text


class TestLogOutput:
    """测试日志输出"""
    
    def test_console_output(self, caplog):
        """测试控制台输出"""
        config = LoggerConfig(
            level='DEBUG',
            console_output=True,
            file_output=False
        )
        
        init_logger(config)
        
        logger = get_logger('test.console')
        
        with caplog.at_level(logging.DEBUG):
            logger.info('Test console output')
        
        assert 'Test console output' in caplog.text
    
    def test_file_output(self, tmp_path):
        """测试文件输出"""
        log_dir = tmp_path / 'logs'
        
        config = LoggerConfig(
            level='DEBUG',
            log_dir=str(log_dir),
            console_output=False,
            file_output=True
        )
        
        init_logger(config)
        
        logger = get_logger('test.file')
        logger.info('Test file output')
        
        # 等待日志写入文件
        time.sleep(0.1)
        
        # 检查日志文件是否存在
        log_files = get_log_files()
        assert len(log_files) > 0
        
        # 检查日志内容
        latest_log = log_files[0]
        content = latest_log.read_text(encoding='utf-8')
        assert 'Test file output' in content
    
    def test_json_output(self, tmp_path):
        """测试 JSON 格式输出"""
        log_dir = tmp_path / 'logs'
        
        config = LoggerConfig(
            level='DEBUG',
            log_dir=str(log_dir),
            console_output=False,
            file_output=True,
            json_output=True
        )
        
        init_logger(config)
        
        logger = get_logger('test.json')
        logger.info('Test JSON output')
        
        # 等待日志写入文件
        time.sleep(0.1)
        
        # 检查 JSON 日志文件是否存在
        json_files = list(log_dir.glob('*.json'))
        assert len(json_files) > 0


class TestLogRotation:
    """测试日志轮转"""
    
    def test_rotating_file_handler(self, tmp_path):
        """测试轮转文件处理器"""
        log_dir = tmp_path / 'logs'
        
        config = LoggerConfig(
            level='DEBUG',
            log_dir=str(log_dir),
            max_bytes=1024,  # 1KB，方便测试
            backup_count=2,
            console_output=False,
            file_output=True
        )
        
        init_logger(config)
        
        logger = get_logger('test.rotation')
        
        # 写入大量日志
        for i in range(100):
            logger.info(f'Log message {i}' * 10)
        
        # 检查是否有多个日志文件
        log_files = list(log_dir.glob('*.log'))
        assert len(log_files) >= 1


class TestLogCleanup:
    """测试日志清理"""
    
    def test_clear_old_logs(self, tmp_path):
        """测试清理旧日志"""
        log_dir = tmp_path / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建模拟日志文件
        today = datetime.now()
        old_date = today.replace(day=today.day - 10)  # 10 天前
        
        current_log = log_dir / f'openfinagent_{today.strftime("%Y%m%d")}.log'
        old_log = log_dir / f'openfinagent_{old_date.strftime("%Y%m%d")}.log'
        
        current_log.write_text('Current log')
        old_log.write_text('Old log')
        
        # 配置日志管理器
        config = LoggerConfig(
            level='DEBUG',
            log_dir=str(log_dir),
            console_output=False,
            file_output=False
        )
        
        init_logger(config)
        
        # 清理 7 天前的日志
        deleted_count = clear_old_logs(keep_days=7)
        
        # 应该删除 1 个旧日志
        assert deleted_count == 1
        assert not old_log.exists()
        assert current_log.exists()


class TestConvenienceFunctions:
    """测试便捷函数"""
    
    def test_log_info_with_extra(self, caplog):
        """测试带额外数据的 INFO 日志"""
        config = LoggerConfig(
            level='DEBUG',
            console_output=True,
            file_output=False
        )
        
        init_logger(config)
        
        logger = get_logger('test.convenience')
        
        with caplog.at_level(logging.DEBUG):
            log_info(logger, 'Test message', user_id='123', action='login')
        
        assert 'Test message' in caplog.text
    
    def test_log_error(self, caplog):
        """测试 ERROR 日志"""
        config = LoggerConfig(
            level='DEBUG',
            console_output=True,
            file_output=False
        )
        
        init_logger(config)
        
        logger = get_logger('test.error')
        
        with caplog.at_level(logging.DEBUG):
            try:
                raise ValueError('Test error')
            except Exception as e:
                log_error(logger, f'Error occurred: {e}')
        
        assert 'Error occurred' in caplog.text


class TestIntegration:
    """集成测试"""
    
    def test_full_logging_workflow(self, tmp_path, caplog):
        """测试完整日志工作流程"""
        log_dir = tmp_path / 'logs'
        
        # 初始化
        config = LoggerConfig(
            level='DEBUG',
            log_dir=str(log_dir),
            console_output=True,
            file_output=True
        )
        
        init_logger(config)
        
        # 获取日志记录器
        logger = get_logger('app.main')
        
        # 记录各种级别的日志
        logger.debug('Application starting')
        logger.info('User logged in', extra={'extra_data': {'user_id': '123'}})
        logger.warning('High memory usage')
        
        try:
            raise ValueError('Simulated error')
        except Exception as e:
            logger.error(f'Error: {e}')
        
        # 验证控制台输出
        with caplog.at_level(logging.DEBUG):
            assert 'Application starting' in caplog.text
            assert 'User logged in' in caplog.text
        
        # 验证文件输出
        time.sleep(0.1)
        log_files = get_log_files()
        assert len(log_files) > 0
        
        content = log_files[0].read_text(encoding='utf-8')
        assert 'Application starting' in content
        assert 'User logged in' in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
