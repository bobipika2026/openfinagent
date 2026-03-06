#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试 - 测试完整回测流程

包含：
- 完整回测流程测试
- 批量回测测试
- 策略优化器测试
- 风险控制集成测试
"""

import sys
import pytest
import pandas as pd
import numpy as np
from datetime import datetime

sys.path.insert(0, '../src')

from openfinagent.strategy import (
    MACrossStrategy,
    RSIStrategy,
    MACDStrategy,
    StrategyBuilder
)
from openfinagent.backtest import (
    BacktestEngine,
    BacktestResults,
    BatchBacktester,
    BatchBacktestConfig,
    MultiStrategyBacktester
)
from openfinagent.risk.control import RiskController, RiskLimits
from openfinagent.optimization.optimizer import (
    StrategyOptimizer,
    ParameterRange
)
from openfinagent.data.sources import MockDataSource


def generate_test_data(n_days=300, seed=42):
    """生成测试数据"""
    np.random.seed(seed)
    dates = pd.date_range(start='2023-01-01', periods=n_days, freq='B')
    
    returns = np.random.normal(0.0005, 0.02, n_days)
    prices = 100.0 * np.cumprod(1 + returns)
    
    df = pd.DataFrame(index=dates)
    df['close'] = prices
    df['open'] = prices * (1 + np.random.uniform(-0.01, 0.01, n_days))
    df['high'] = df[['open', 'close']].max(axis=1) * (1 + np.random.uniform(0, 0.02, n_days))
    df['low'] = df[['open', 'close']].min(axis=1) * (1 - np.random.uniform(0, 0.02, n_days))
    df['volume'] = np.random.randint(1000000, 10000000, n_days)
    
    return df


class TestCompleteBacktestFlow:
    """完整回测流程测试"""

    def test_complete_backtest_flow(self):
        """测试完整回测流程"""
        # 1. 准备数据
        data = generate_test_data(300)
        
        # 2. 创建策略
        strategy = StrategyBuilder.from_natural_language("""
        当 5 日均线上穿 20 日均线时买入
        当 5 日均线下穿 20 日均线时卖出
        初始资金 10 万元
        """)
        
        # 3. 创建回测引擎
        engine = BacktestEngine(commission_rate=0.0003, slippage=0.001)
        
        # 4. 运行回测
        results = engine.run(
            strategy,
            data,
            start_date='2023-02-01',
            end_date='2023-12-31',
            show_progress=False
        )
        
        # 5. 验证结果
        assert isinstance(results, BacktestResults)
        assert len(results.equity_curve) > 0
        assert '总收益 (%)' in results.metrics
        assert '夏普比率' in results.metrics
        assert '最大回撤 (%)' in results.metrics

    def test_multi_strategy_comparison(self):
        """测试多策略对比"""
        data = generate_test_data(300)
        
        strategies = [
            MACrossStrategy(short_window=5, long_window=20, name='快策略'),
            MACrossStrategy(short_window=10, long_window=30, name='慢策略'),
            RSIStrategy(rsi_period=14, name='RSI 策略')
        ]
        
        backtester = MultiStrategyBacktester(initial_capital=100000)
        results = backtester.run(strategies, data)
        
        # 验证所有策略都有结果
        assert len(results) == 3
        
        # 获取对比结果
        comparison = backtester.compare()
        assert len(comparison) == 3
        assert 'strategy' in comparison.columns


class TestBatchBacktest:
    """批量回测测试"""

    def test_batch_backtest_single_strategy(self):
        """测试单策略批量回测"""
        # 使用模拟数据源
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META']
        
        config = BatchBacktestConfig(
            symbols=symbols,
            strategy_class=MACrossStrategy,
            strategy_params={'short_window': 5, 'long_window': 20},
            initial_capital=100000,
            start_date='2023-01-01',
            end_date='2023-06-30',
            data_source='mock',
            n_jobs=2,
            show_progress=False
        )
        
        batch_backtester = BatchBacktester(config)
        results = batch_backtester.run()
        
        # 验证结果
        assert len(results) == 5
        
        successful = [r for r in results if r.success]
        assert len(successful) > 0
        
        # 验证汇总
        summary = batch_backtester.get_summary()
        assert summary is not None
        assert len(summary) == len(successful)

    def test_batch_backtest_with_custom_data_loader(self):
        """测试自定义数据加载器的批量回测"""
        def mock_loader(symbol, start_date, end_date):
            source = MockDataSource(initial_price=np.random.uniform(50, 200))
            return source.get_data(symbol, start_date, end_date)
        
        config = BatchBacktestConfig(
            symbols=['STOCK1', 'STOCK2', 'STOCK3'],
            strategy_class=RSIStrategy,
            strategy_params={'rsi_period': 14},
            initial_capital=50000,
            start_date='2023-01-01',
            end_date='2023-03-31',
            n_jobs=1
        )
        
        batch_backtester = BatchBacktester(config)
        results = batch_backtester.run(load_data_func=mock_loader)
        
        assert len(results) == 3


class TestStrategyOptimizer:
    """策略优化器测试"""

    def test_grid_search_optimization(self):
        """测试网格搜索优化"""
        data = generate_test_data(300)
        
        def backtest_func(strategy, data):
            engine = BacktestEngine()
            return engine.run(strategy, data, show_progress=False)
        
        optimizer = StrategyOptimizer(
            optimization_metric='sharpe_ratio',
            maximize=True,
            n_jobs=1
        )
        
        # 定义参数范围
        param_ranges = [
            ParameterRange(name='short_window', values=[5, 10, 15]),
            ParameterRange(name='long_window', values=[20, 30, 40])
        ]
        
        # 执行优化
        results = optimizer.grid_search(
            strategy_class=MACrossStrategy,
            parameter_ranges=param_ranges,
            backtest_func=backtest_func,
            data=data,
            initial_capital=100000,
            show_progress=False
        )
        
        # 验证结果
        assert len(results) > 0
        assert optimizer.best_result is not None
        
        # 验证最优参数
        best_params = optimizer.get_best_params()
        assert 'short_window' in best_params
        assert 'long_window' in best_params

    def test_sensitivity_analysis(self):
        """测试参数敏感性分析"""
        data = generate_test_data(300)
        
        def backtest_func(strategy, data):
            engine = BacktestEngine()
            return engine.run(strategy, data, show_progress=False)
        
        optimizer = StrategyOptimizer()
        
        base_params = {'short_window': 5, 'long_window': 20}
        param_range = ParameterRange(name='short_window', values=[3, 5, 7, 10, 15, 20])
        
        sensitivity_df = optimizer.sensitivity_analysis(
            strategy_class=MACrossStrategy,
            base_params=base_params,
            parameter_to_vary='short_window',
            parameter_range=param_range,
            backtest_func=backtest_func,
            data=data,
            initial_capital=100000
        )
        
        # 验证结果
        assert len(sensitivity_df) > 0
        assert 'short_window' in sensitivity_df.columns
        assert 'sharpe_ratio' in sensitivity_df.columns

    def test_overfitting_detection(self):
        """测试过拟合检测"""
        data = generate_test_data(300)
        
        def backtest_func(strategy, data):
            engine = BacktestEngine()
            return engine.run(strategy, data, show_progress=False)
        
        optimizer = StrategyOptimizer(n_jobs=1)
        
        # 使用大量参数组合
        param_ranges = [
            ParameterRange(name='short_window', values=list(range(3, 21, 2))),
            ParameterRange(name='long_window', values=list(range(20, 61, 5)))
        ]
        
        optimizer.grid_search(
            strategy_class=MACrossStrategy,
            parameter_ranges=param_ranges,
            backtest_func=backtest_func,
            data=data,
            initial_capital=100000,
            show_progress=False
        )
        
        # 检测过拟合
        overfitting_metrics = optimizer.detect_overfitting()
        
        assert 'reliable' in overfitting_metrics
        assert 'overfitting_score' in overfitting_metrics


class TestRiskControlIntegration:
    """风险控制集成测试"""

    def test_risk_controller_integration(self):
        """测试风险控制器集成"""
        data = generate_test_data(300)
        
        # 创建带风险控制的策略
        strategy = MACrossStrategy(initial_capital=100000)
        
        # 创建风险控制器
        limits = RiskLimits(
            max_position_ratio=0.3,
            stop_loss_pct=0.08,
            take_profit_pct=0.20,
            max_drawdown_pct=0.15
        )
        risk_controller = RiskController(limits)
        
        # 运行回测
        engine = BacktestEngine()
        results = engine.run(strategy, data, show_progress=False)
        
        # 验证风险控制指标
        risk_metrics = risk_controller.get_risk_metrics(results.final_capital)
        
        assert 'peak_equity' in risk_metrics
        assert 'current_drawdown' in risk_metrics
        assert 'daily_trades' in risk_metrics

    def test_stop_loss_take_profit_trigger(self):
        """测试止损止盈触发"""
        risk_controller = RiskController()
        
        # 记录买入
        risk_controller.record_trade('buy', price=100.0, shares=1000, symbol='TEST')
        
        # 测试止损触发 (价格下跌 10%)
        action = risk_controller.check_stop_loss_take_profit(
            current_price=90.0,
            symbol='TEST'
        )
        assert action == 'stop_loss'
        
        # 重置
        risk_controller.reset(100000)
        risk_controller.record_trade('buy', price=100.0, shares=1000, symbol='TEST')
        
        # 测试止盈触发 (价格上涨 25%)
        action = risk_controller.check_stop_loss_take_profit(
            current_price=125.0,
            symbol='TEST'
        )
        assert action == 'take_profit'

    def test_position_size_adjustment(self):
        """测试仓位调整"""
        risk_controller = RiskController()
        
        # 当前权益 10 万
        current_equity = 100000
        
        # 提议买入 5 万元仓位 (超过 30% 限制)
        proposed_shares = 500
        price = 100.0
        
        adjusted = risk_controller.adjust_position_size(
            proposed_shares=proposed_shares,
            price=price,
            current_equity=current_equity,
            current_positions={'shares': 0}
        )
        
        # 应该被限制在 30% 以内
        assert adjusted <= 300  # 30% * 100000 / 100


class TestEndToEnd:
    """端到端测试"""

    def test_full_workflow(self):
        """测试完整工作流程"""
        # 1. 加载数据
        data = generate_test_data(500)
        
        # 2. 策略优化
        def backtest_func(strategy, data):
            engine = BacktestEngine()
            return engine.run(strategy, data, show_progress=False)
        
        optimizer = StrategyOptimizer(optimization_metric='总收益 (%)', n_jobs=1)
        
        param_ranges = [
            ParameterRange(name='rsi_period', values=[10, 14, 18]),
            ParameterRange(name='oversold_threshold', values=[25, 30]),
            ParameterRange(name='overbought_threshold', values=[70, 75])
        ]
        
        optimization_results = optimizer.grid_search(
            strategy_class=RSIStrategy,
            parameter_ranges=param_ranges,
            backtest_func=backtest_func,
            data=data,
            initial_capital=100000,
            show_progress=False
        )
        
        # 3. 使用最优参数创建策略
        best_params = optimizer.get_best_params()
        strategy = RSIStrategy(**best_params, initial_capital=100000)
        
        # 4. 运行回测
        engine = BacktestEngine()
        results = engine.run(strategy, data, show_progress=False)
        
        # 5. 验证结果
        assert results.final_capital > 0
        assert len(results.trades) > 0
        
        # 6. 导出结果
        results.show()
        
        # 7. 批量回测多只股票
        symbols = ['STOCK1', 'STOCK2', 'STOCK3']
        
        batch_config = BatchBacktestConfig(
            symbols=symbols,
            strategy_class=RSIStrategy,
            strategy_params=best_params,
            initial_capital=100000,
            start_date='2023-01-01',
            end_date='2023-12-31',
            data_source='mock',
            n_jobs=2
        )
        
        batch_backtester = BatchBacktester(batch_config)
        batch_results = batch_backtester.run()
        
        # 验证批量回测结果
        assert len(batch_results) == 3
        assert batch_backtester.get_summary() is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
