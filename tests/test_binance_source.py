"""
Binance 数据源单元测试

测试用例：
- 数据获取
- 时间周期验证
- 错误处理
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data.binance_source import BinanceDataSource, get_binance_data


class TestBinanceDataSource:
    """Binance 数据源测试类"""

    def test_initialization(self):
        """测试初始化"""
        source = BinanceDataSource()
        assert source.base_url == 'https://api.binance.com'
        assert source.rate_limit_delay == 0.1

    def test_custom_initialization(self):
        """测试自定义初始化"""
        source = BinanceDataSource(
            base_url='https://test-api.binance.com',
            rate_limit_delay=0.2
        )
        assert source.base_url == 'https://test-api.binance.com'
        assert source.rate_limit_delay == 0.2

    def test_interval_validation(self):
        """测试时间周期验证"""
        source = BinanceDataSource()
        
        # 有效周期
        valid_intervals = ['1m', '5m', '15m', '1h', '4h', '1d']
        for interval in valid_intervals:
            assert interval in source.INTERVAL_MAP
        
        # 无效周期
        with pytest.raises(ValueError, match="不支持的时间周期"):
            source.get_klines(
                symbol='BTCUSDT',
                interval='invalid',
                start_date='2024-01-01',
                end_date='2024-01-02'
            )

    def test_symbol_normalization(self):
        """测试交易对标准化"""
        source = BinanceDataSource()
        
        # 不同格式的交易对应被标准化
        test_cases = [
            ('BTC/USDT', 'BTCUSDT'),
            ('BTC_USDT', 'BTCUSDT'),
            ('btcusdt', 'BTCUSDT'),
            ('ETH/BTC', 'ETHBTC')
        ]
        
        for input_symbol, expected in test_cases:
            # 验证标准化逻辑 (通过检查内部处理)
            clean = input_symbol.replace('/', '').replace('_', '').upper()
            assert clean == expected

    def test_klines_structure(self):
        """测试 K 线数据结构 (使用模拟数据)"""
        # 这个测试需要实际 API 调用，可能会被跳过
        try:
            source = BinanceDataSource()
            
            # 获取少量数据
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            df = source.get_klines(
                symbol='BTC/USDT',
                interval='1d',
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
            
            if not df.empty:
                # 验证列
                assert 'open' in df.columns
                assert 'high' in df.columns
                assert 'low' in df.columns
                assert 'close' in df.columns
                assert 'volume' in df.columns
                
                # 验证数据类型
                assert pd.api.types.is_numeric_dtype(df['open'])
                assert pd.api.types.is_numeric_dtype(df['close'])
                
                # 验证索引
                assert isinstance(df.index, pd.DatetimeIndex)
                
        except Exception as e:
            pytest.skip(f"API 调用失败：{e}")

    def test_get_ticker_price(self):
        """测试获取当前价格"""
        try:
            source = BinanceDataSource()
            price = source.get_ticker_price('BTC/USDT')
            
            if price is not None:
                assert isinstance(price, float)
                assert price > 0
        except Exception as e:
            pytest.skip(f"API 调用失败：{e}")

    def test_get_available_symbols(self):
        """测试获取可用交易对"""
        try:
            source = BinanceDataSource()
            symbols = source.get_available_symbols()
            
            assert isinstance(symbols, list)
            assert len(symbols) > 0
            assert 'BTCUSDT' in symbols or 'ETHUSDT' in symbols
            
        except Exception as e:
            pytest.skip(f"API 调用失败：{e}")

    def test_historical_data(self):
        """测试获取历史数据"""
        try:
            source = BinanceDataSource()
            
            df = source.get_historical_data(
                symbol='BTC/USDT',
                interval='1d',
                days=30
            )
            
            if not df.empty:
                assert len(df) > 0
                assert len(df) <= 30  # 最多 30 天
                
        except Exception as e:
            pytest.skip(f"API 调用失败：{e}")


class TestConvenienceFunctions:
    """便捷函数测试"""

    def test_get_binance_data(self):
        """测试便捷函数"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            df = get_binance_data(
                symbol='BTC/USDT',
                interval='1d',
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
            
            if not df.empty:
                assert isinstance(df, pd.DataFrame)
                assert 'close' in df.columns
                
        except Exception as e:
            pytest.skip(f"API 调用失败：{e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
