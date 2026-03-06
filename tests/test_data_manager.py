"""
数据源管理器测试

测试多数据源管理、降级、缓存等功能

@module: tests.test_data_manager
@author: OpenFinAgent Team
@version: 0.4.0
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data.manager import DataManager, DataQualityReport
from data.sources import MockDataSource


class TestDataManager:
    """测试数据源管理器"""
    
    @pytest.fixture
    def manager(self):
        """创建测试用的数据源管理器"""
        config = {
            'primary': 'mock',
            'fallback_order': ['mock'],
            'enable_cache': True,
            'cache_ttl': 3600
        }
        return DataManager(config)
    
    def test_manager_initialization(self, manager):
        """测试管理器初始化"""
        assert manager.primary == 'mock'
        assert 'mock' in manager.feeds
        assert manager.enable_cache is True
    
    def test_get_data_from_mock(self, manager):
        """测试从 Mock 数据源获取数据"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        data = manager.get_data(
            symbol='TEST',
            start_date=start_date,
            end_date=end_date
        )
        
        assert not data.empty
        assert len(data) > 0
        assert all(col in data.columns for col in ['open', 'high', 'low', 'close', 'volume'])
    
    def test_cache_functionality(self, manager):
        """测试缓存功能"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # 第一次获取
        data1 = manager.get_data(
            symbol='TEST',
            start_date=start_date,
            end_date=end_date,
            use_cache=True
        )
        
        # 第二次获取 (应该使用缓存)
        data2 = manager.get_data(
            symbol='TEST',
            start_date=start_date,
            end_date=end_date,
            use_cache=True
        )
        
        # 验证数据相同
        assert data1.equals(data2)
    
    def test_clear_cache(self, manager):
        """测试清空缓存"""
        manager.clear_cache()
        assert len(manager._cache) == 0
    
    def test_get_available_sources(self, manager):
        """测试获取可用数据源列表"""
        sources = manager.get_available_sources()
        
        assert 'mock' in sources
    
    def test_get_realtime(self, manager):
        """测试获取实时行情"""
        realtime = manager.get_realtime('TEST')
        
        # Mock 数据源可能不支持实时行情
        # 这个测试主要验证不会抛出异常
        assert isinstance(realtime, dict)
    
    def test_check_quality(self, manager):
        """测试检查数据质量"""
        reports = manager.check_quality('TEST')
        
        assert len(reports) > 0
        
        # 验证报告格式
        for report in reports:
            assert isinstance(report, DataQualityReport)
            assert report.symbol == 'TEST'
            assert report.source in manager.feeds
    
    def test_get_best_source(self, manager):
        """测试获取最佳数据源"""
        best_source = manager.get_best_source('TEST')
        
        # Mock 数据源应该是最佳的 (因为其他数据源可能未配置)
        assert best_source in manager.get_available_sources()
    
    def test_source_fallback(self):
        """测试数据源降级"""
        # 配置多个数据源，但只有 mock 可用
        config = {
            'primary': 'tushare',  # 未配置 API key
            'fallback_order': ['tushare', 'mock'],
            'enable_cache': False
        }
        
        manager = DataManager(config)
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # 应该自动降级到 mock
        data = manager.get_data(
            symbol='TEST',
            start_date=start_date,
            end_date=end_date
        )
        
        assert not data.empty


class TestDataQualityReport:
    """测试数据质量报告"""
    
    def test_report_creation(self):
        """测试报告创建"""
        report = DataQualityReport(
            symbol='AAPL',
            source='yfinance',
            quality='good',
            missing_rate=0.05
        )
        
        assert report.symbol == 'AAPL'
        assert report.source == 'yfinance'
        assert report.quality == 'good'
        assert report.missing_rate == 0.05
    
    def test_report_to_dict(self):
        """测试报告转字典"""
        report = DataQualityReport(
            symbol='AAPL',
            source='yfinance',
            quality='good'
        )
        
        report_dict = report.to_dict()
        
        assert report_dict['symbol'] == 'AAPL'
        assert report_dict['source'] == 'yfinance'
        assert report_dict['quality'] == 'good'


class TestIntegration:
    """集成测试"""
    
    def test_full_data_workflow(self):
        """测试完整的数据工作流"""
        # 创建管理器
        config = {
            'primary': 'mock',
            'fallback_order': ['mock'],
            'enable_cache': True
        }
        
        manager = DataManager(config)
        
        # 获取数据
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        data = manager.get_data('TEST', start_date, end_date)
        
        # 验证数据
        assert not data.empty
        assert len(data) > 0
        
        # 检查质量
        reports = manager.check_quality('TEST')
        
        # 获取实时行情
        realtime = manager.get_realtime('TEST')
        
        # 获取最佳数据源
        best = manager.get_best_source('TEST')
        
        assert best == 'mock'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
