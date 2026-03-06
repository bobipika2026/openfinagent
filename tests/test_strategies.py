#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略模块测试 - 测试所有策略实现

包含：
- 策略基类测试
- 各策略实现测试
- 指标计算测试
"""

import sys
import pytest
import pandas as pd
import numpy as np
from datetime import datetime

# 添加 src 到路径
sys.path.insert(0, '../src')

from tradeflow.strategy import (
    BaseStrategy,
    MACrossStrategy,
    MomentumStrategy,
    RSIStrategy,
    MACDStrategy,
    BollingerStrategy,
    DualMAVolumeStrategy,
    StrategyBuilder,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands
)
from tradeflow.backtest import BacktestEngine, BacktestResults


def generate_test_data(n_days=200, initial_price=100.0, seed=42):
    """生成测试数据"""
    np.random.seed(seed)
    dates = pd.date_range(start='2023-01-01', periods=n_days, freq='B')
    
    # 生成价格序列
    returns = np.random.normal(0.0005, 0.02, n_days)
    prices = initial_price * np.cumprod(1 + returns)
    
    df = pd.DataFrame(index=dates)
    df['close'] = prices
    df['open'] = prices * (1 + np.random.uniform(-0.01, 0.01, n_days))
    df['high'] = df[['open', 'close']].max(axis=1) * (1 + np.random.uniform(0, 0.02, n_days))
    df['low'] = df[['open', 'close']].min(axis=1) * (1 - np.random.uniform(0, 0.02, n_days))
    df['volume'] = np.random.randint(1000000, 10000000, n_days)
    
    return df


class TestIndicators:
    """技术指标测试"""

    def test_rsi_calculation(self):
        """测试 RSI 计算"""
        prices = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109] * 10)
        rsi = calculate_rsi(prices, period=14)
        
        assert len(rsi) == len(prices)
        assert rsi.notna().sum() > 0
        assert (rsi >= 0).all() and (rsi <= 100).all()

    def test_macd_calculation(self):
        """测试 MACD 计算"""
        prices = pd.Series(np.random.randn(100).cumsum() + 100)
        macd_line, signal_line, histogram = calculate_macd(prices)
        
        assert len(macd_line) == len(prices)
        assert len(signal_line) == len(prices)
        assert len(histogram) == len(prices)
        assert np.allclose(macd_line - signal_line, histogram)

    def test_bollinger_bands_calculation(self):
        """测试布林带计算"""
        prices = pd.Series(np.random.randn(100).cumsum() + 100)
        upper, middle, lower = calculate_bollinger_bands(prices, window=20, num_std=2)
        
        assert len(upper) == len(prices)
        assert len(middle) == len(prices)
        assert len(lower) == len(prices)
        assert (upper >= middle).all()
        assert (middle >= lower).all()


class TestRSIStrategy:
    """RSI 策略测试"""

    def test_rsi_strategy_init(self):
        """测试 RSI 策略初始化"""
        strategy = RSIStrategy(
            rsi_period=14,
            oversold_threshold=30,
            overbought_threshold=70
        )
        
        assert strategy.rsi_period == 14
        assert strategy.oversold_threshold == 30
        assert strategy.overbought_threshold == 70

    def test_rsi_strategy_signals(self):
        """测试 RSI 策略信号生成"""
        strategy = RSIStrategy(rsi_period=14)
        data = generate_test_data(200)
        
        signals = strategy.generate_signals(data)
        
        assert len(signals) == len(data)
        assert set(signals.unique()).issubset({-1, 0, 1})

    def test_rsi_strategy_backtest(self):
        """测试 RSI 策略回测"""
        strategy = RSIStrategy(initial_capital=100000)
        data = generate_test_data(200)
        
        engine = BacktestEngine()
        results = engine.run(strategy, data, show_progress=False)
        
        assert isinstance(results, BacktestResults)
        assert '总收益 (%)' in results.metrics

    def test_rsi_invalid_params(self):
        """测试 RSI 策略无效参数"""
        with pytest.raises(ValueError):
            RSIStrategy(rsi_period=0)
        
        with pytest.raises(ValueError):
            RSIStrategy(oversold_threshold=80, overbought_threshold=70)


class TestMACDStrategy:
    """MACD 策略测试"""

    def test_macd_strategy_init(self):
        """测试 MACD 策略初始化"""
        strategy = MACDStrategy(
            fast_period=12,
            slow_period=26,
            signal_period=9
        )
        
        assert strategy.fast_period == 12
        assert strategy.slow_period == 26
        assert strategy.signal_period == 9

    def test_macd_strategy_signals(self):
        """测试 MACD 策略信号生成"""
        strategy = MACDStrategy()
        data = generate_test_data(200)
        
        signals = strategy.generate_signals(data)
        
        assert len(signals) == len(data)
        assert set(signals.unique()).issubset({-1, 0, 1})

    def test_macd_strategy_backtest(self):
        """测试 MACD 策略回测"""
        strategy = MACDStrategy(initial_capital=100000)
        data = generate_test_data(200)
        
        engine = BacktestEngine()
        results = engine.run(strategy, data, show_progress=False)
        
        assert isinstance(results, BacktestResults)

    def test_macd_invalid_params(self):
        """测试 MACD 策略无效参数"""
        with pytest.raises(ValueError):
            MACDStrategy(fast_period=30, slow_period=20)


class TestBollingerStrategy:
    """布林带策略测试"""

    def test_bollinger_strategy_init(self):
        """测试布林带策略初始化"""
        strategy = BollingerStrategy(
            window=20,
            num_std=2.0,
            mode='mean_reversion'
        )
        
        assert strategy.window == 20
        assert strategy.num_std == 2.0
        assert strategy.mode == 'mean_reversion'

    def test_bollinger_strategy_mean_reversion(self):
        """测试均值回归模式"""
        strategy = BollingerStrategy(mode='mean_reversion')
        data = generate_test_data(200)
        
        signals = strategy.generate_signals(data)
        assert len(signals) == len(data)

    def test_bollinger_strategy_trend_breakout(self):
        """测试趋势突破模式"""
        strategy = BollingerStrategy(mode='trend_breakout')
        data = generate_test_data(200)
        
        signals = strategy.generate_signals(data)
        assert len(signals) == len(data)

    def test_bollinger_invalid_params(self):
        """测试布林带策略无效参数"""
        with pytest.raises(ValueError):
            BollingerStrategy(window=0)
        
        with pytest.raises(ValueError):
            BollingerStrategy(num_std=-1)
        
        with pytest.raises(ValueError):
            BollingerStrategy(mode='invalid')


class TestDualMAVolumeStrategy:
    """双均线 + 成交量策略测试"""

    def test_dual_ma_volume_init(self):
        """测试双均线 + 成交量策略初始化"""
        strategy = DualMAVolumeStrategy(
            short_window=5,
            long_window=20,
            volume_window=20,
            volume_multiplier=1.5
        )
        
        assert strategy.short_window == 5
        assert strategy.long_window == 20
        assert strategy.volume_multiplier == 1.5

    def test_dual_ma_volume_signals(self):
        """测试双均线 + 成交量策略信号"""
        strategy = DualMAVolumeStrategy()
        data = generate_test_data(200)
        
        signals = strategy.generate_signals(data)
        
        assert len(signals) == len(data)

    def test_dual_ma_volume_backtest(self):
        """测试双均线 + 成交量策略回测"""
        strategy = DualMAVolumeStrategy(initial_capital=100000)
        data = generate_test_data(200)
        
        engine = BacktestEngine()
        results = engine.run(strategy, data, show_progress=False)
        
        assert isinstance(results, BacktestResults)

    def test_dual_ma_volume_invalid_params(self):
        """测试双均线 + 成交量策略无效参数"""
        with pytest.raises(ValueError):
            DualMAVolumeStrategy(short_window=30, long_window=20)


class TestStrategyBuilder:
    """策略构建器测试"""

    def test_create_rsi_strategy(self):
        """测试创建 RSI 策略"""
        strategy = StrategyBuilder.create(
            'rsi',
            rsi_period=14,
            oversold_threshold=30,
            overbought_threshold=70
        )
        
        assert isinstance(strategy, RSIStrategy)
        assert strategy.rsi_period == 14

    def test_create_macd_strategy(self):
        """测试创建 MACD 策略"""
        strategy = StrategyBuilder.create(
            'macd',
            fast_period=12,
            slow_period=26
        )
        
        assert isinstance(strategy, MACDStrategy)

    def test_create_bollinger_strategy(self):
        """测试创建布林带策略"""
        strategy = StrategyBuilder.create(
            'bollinger',
            window=20,
            mode='mean_reversion'
        )
        
        assert isinstance(strategy, BollingerStrategy)

    def test_create_dual_ma_volume_strategy(self):
        """测试创建双均线 + 成交量策略"""
        strategy = StrategyBuilder.create(
            'dual_ma_volume',
            short_window=5,
            long_window=20
        )
        
        assert isinstance(strategy, DualMAVolumeStrategy)

    def test_list_all_strategies(self):
        """测试列出所有策略"""
        strategies = StrategyBuilder.list_strategies()
        
        assert 'ma_cross' in strategies
        assert 'momentum' in strategies
        assert 'rsi' in strategies
        assert 'macd' in strategies
        assert 'bollinger' in strategies
        assert 'dual_ma_volume' in strategies


class TestAllStrategiesComparison:
    """所有策略对比测试"""

    def test_all_strategies_backtest(self):
        """测试所有策略回测对比"""
        data = generate_test_data(200)
        
        strategies = [
            MACrossStrategy(short_window=5, long_window=20, name='MA_Cross'),
            MomentumStrategy(lookback_period=20, threshold=0.05, name='Momentum'),
            RSIStrategy(rsi_period=14, name='RSI'),
            MACDStrategy(fast_period=12, slow_period=26, name='MACD'),
            BollingerStrategy(window=20, name='Bollinger'),
            DualMAVolumeStrategy(short_window=5, long_window=20, name='DualMA_Vol')
        ]
        
        engine = BacktestEngine()
        results = {}
        
        for strategy in strategies:
            result = engine.run(strategy, data, show_progress=False)
            results[strategy.name] = result
        
        # 验证所有策略都成功回测
        assert len(results) == 6
        
        # 验证所有结果都有指标
        for name, result in results.items():
            assert '总收益 (%)' in result.metrics, f"{name} 缺少总收益指标"
            assert '夏普比率' in result.metrics, f"{name} 缺少夏普比率指标"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
