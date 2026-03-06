#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略模块测试
"""

import sys
import pytest
sys.path.insert(0, '../src')

import pandas as pd
import numpy as np
from datetime import datetime

from tradeflow.strategy import StrategyBuilder, BaseStrategy
from tradeflow.backtest import BacktestEngine, BacktestResults
from tradeflow.nlp import StrategyParser


def generate_test_data(n_days=100, initial_price=100.0):
    """生成测试数据"""
    dates = pd.date_range(start='2023-01-01', periods=n_days, freq='B')
    np.random.seed(42)
    returns = np.random.normal(0.0005, 0.02, n_days)
    prices = initial_price * np.cumprod(1 + returns)

    df = pd.DataFrame(index=dates)
    df['close'] = prices
    df['open'] = prices * (1 + np.random.uniform(-0.01, 0.01, n_days))
    df['high'] = df[['open', 'close']].max(axis=1) * (1 + np.random.uniform(0, 0.02, n_days))
    df['low'] = df[['open', 'close']].min(axis=1) * (1 - np.random.uniform(0, 0.02, n_days))
    df['volume'] = np.random.randint(1000000, 10000000, n_days)

    return df


class TestStrategyBuilder:
    """策略构建器测试"""

    def test_create_ma_cross_strategy(self):
        """测试创建均线策略"""
        strategy = StrategyBuilder.create(
            'ma_cross',
            short_window=5,
            long_window=20,
            initial_capital=100000
        )
        assert strategy.short_window == 5
        assert strategy.long_window == 20
        assert strategy.initial_capital == 100000

    def test_create_momentum_strategy(self):
        """测试创建动量策略"""
        strategy = StrategyBuilder.create(
            'momentum',
            lookback_period=20,
            threshold=0.05,
            initial_capital=50000
        )
        assert strategy.lookback_period == 20
        assert strategy.threshold == 0.05

    def test_from_natural_language_ma(self):
        """测试自然语言创建均线策略"""
        strategy = StrategyBuilder.from_natural_language("""
        当 5 日均线上穿 20 日均线时买入
        当 5 日均线下穿 20 日均线时卖出
        初始资金 10 万元
        """)
        assert strategy.short_window == 5
        assert strategy.long_window == 20
        assert strategy.initial_capital == 100000

    def test_from_natural_language_momentum(self):
        """测试自然语言创建动量策略"""
        strategy = StrategyBuilder.from_natural_language("""
        动量策略
        看 20 天收益率
        超过 5% 买入
        初始资金 50 万元
        """)
        assert strategy.lookback_period == 20
        assert strategy.threshold == 0.05

    def test_list_strategies(self):
        """测试列出策略"""
        strategies = StrategyBuilder.list_strategies()
        assert 'ma_cross' in strategies
        assert 'momentum' in strategies


class TestBacktestEngine:
    """回测引擎测试"""

    def test_run_backtest(self):
        """测试运行回测"""
        strategy = StrategyBuilder.create('ma_cross', short_window=5, long_window=20)
        data = generate_test_data(100)

        engine = BacktestEngine()
        results = engine.run(strategy, data, show_progress=False)

        assert isinstance(results, BacktestResults)
        assert results.initial_capital == 100000
        assert len(results.equity_curve) == 100
        assert '总收益 (%)' in results.metrics

    def test_run_with_dates(self):
        """测试带日期范围的回测"""
        strategy = StrategyBuilder.create('ma_cross')
        data = generate_test_data(200)

        engine = BacktestEngine()
        results = engine.run(
            strategy, data,
            start_date='2023-03-01',
            end_date='2023-06-30',
            show_progress=False
        )

        assert len(results.equity_curve) > 0

    def test_multi_strategy(self):
        """测试多策略回测"""
        strategies = [
            StrategyBuilder.create('ma_cross', short_window=5, long_window=20, name='策略 1'),
            StrategyBuilder.create('ma_cross', short_window=10, long_window=30, name='策略 2'),
        ]
        data = generate_test_data(100)

        engine = BacktestEngine()
        results = engine.run_multi(strategies, data)

        assert len(results) == 2
        assert '策略 1' in results
        assert '策略 2' in results


class TestStrategyParser:
    """策略解析器测试"""

    def test_parse_ma_cross(self):
        """测试均线策略解析"""
        parser = StrategyParser()
        result = parser.parse("""
        当 5 日均线上穿 20 日均线时买入
        当 5 日均线下穿 20 日均线时卖出
        """)

        assert result['strategy_type'] == 'ma_cross'
        assert result['params']['short_window'] == 5
        assert result['params']['long_window'] == 20

    def test_parse_capital(self):
        """测试资金解析"""
        parser = StrategyParser()
        result = parser.parse("初始资金 10 万元")

        assert result['initial_capital'] == 100000

    def test_parse_momentum(self):
        """测试动量策略解析"""
        parser = StrategyParser()
        result = parser.parse("""
        动量策略
        看 20 天
        超过 5%
        """)

        assert result['strategy_type'] == 'momentum'
        assert result['params']['lookback_period'] == 20
        assert result['params']['threshold'] == 0.05

    def test_validate(self):
        """测试验证功能"""
        parser = StrategyParser()
        result = parser.validate("当 5 日均线上穿 20 日均线时买入")

        assert 'parsed' in result
        assert result['parsed']['params']['short_window'] == 5


class TestBaseStrategy:
    """策略基类测试"""

    def test_position_sizing(self):
        """测试仓位计算"""
        strategy = StrategyBuilder.create('ma_cross', initial_capital=100000)

        shares = strategy.calculate_position_size(100.0, 1)
        assert shares > 0
        assert shares % 100 == 0  # A 股 100 股一手

    def test_portfolio_value(self):
        """测试组合价值计算"""
        strategy = StrategyBuilder.create('ma_cross', initial_capital=100000)
        strategy.positions['shares'] = 1000

        value = strategy.get_portfolio_value(150.0)
        assert value == strategy.cash + 1000 * 150.0

    def test_reset(self):
        """测试重置功能"""
        strategy = StrategyBuilder.create('ma_cross', initial_capital=100000)
        strategy.positions['shares'] = 1000
        strategy.cash = 50000

        strategy.reset()
        assert strategy.cash == 100000
        assert strategy.positions == {}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
