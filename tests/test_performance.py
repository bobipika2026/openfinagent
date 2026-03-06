#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试 - 测试系统性能和扩展性

包含：
- 回测引擎性能测试
- 批量回测性能测试
- 策略优化性能测试
- 内存使用测试
"""

import sys
import pytest
import pandas as pd
import numpy as np
import time
from datetime import datetime

sys.path.insert(0, '../src')

from openfinagent.strategy import (
    MACrossStrategy,
    RSIStrategy,
    MACDStrategy,
    BollingerStrategy
)
from openfinagent.backtest import (
    BacktestEngine,
    BatchBacktester,
    BatchBacktestConfig
)
from openfinagent.optimization.optimizer import (
    StrategyOptimizer,
    ParameterRange
)
from openfinagent.data.sources import MockDataSource


def generate_large_dataset(n_days=2000, n_stocks=50, seed=42):
    """生成大规模测试数据集"""
    np.random.seed(seed)
    
    dates = pd.date_range(start='2020-01-01', periods=n_days, freq='B')
    data_dict = {}
    
    for i in range(n_stocks):
        returns = np.random.normal(0.0005, 0.02, n_days)
        prices = 100.0 * np.cumprod(1 + returns)
        
        df = pd.DataFrame(index=dates)
        df['close'] = prices
        df['open'] = prices * (1 + np.random.uniform(-0.01, 0.01, n_days))
        df['high'] = df[['open', 'close']].max(axis=1) * (1 + np.random.uniform(0, 0.02, n_days))
        df['low'] = df[['open', 'close']].min(axis=1) * (1 - np.random.uniform(0, 0.02, n_days))
        df['volume'] = np.random.randint(1000000, 10000000, n_days)
        
        data_dict[f'STOCK{i:03d}'] = df
    
    return data_dict


class TestBacktestPerformance:
    """回测引擎性能测试"""

    def test_backtest_speed_single_strategy(self):
        """测试单策略回测速度"""
        data = generate_large_dataset(n_days=1000, n_stocks=1)[0]
        strategy = MACrossStrategy(short_window=5, long_window=20)
        engine = BacktestEngine()
        
        start_time = time.time()
        results = engine.run(strategy, data, show_progress=False)
        elapsed = time.time() - start_time
        
        # 验证性能：1000 天数据应在 1 秒内完成
        assert elapsed < 1.0, f"回测耗时过长：{elapsed:.2f}秒"
        
        # 验证结果正确性
        assert results is not None
        assert len(results.equity_curve) == len(data)
        
        print(f"\n单策略回测性能：{len(data)}天数据，耗时{elapsed:.3f}秒")

    def test_backtest_speed_multiple_strategies(self):
        """测试多策略回测速度"""
        data = generate_large_dataset(n_days=500, n_stocks=1)[0]
        
        strategies = [
            MACrossStrategy(short_window=5, long_window=20),
            RSIStrategy(rsi_period=14),
            MACDStrategy(fast_period=12, slow_period=26),
            BollingerStrategy(window=20)
        ]
        
        engine = BacktestEngine()
        
        start_time = time.time()
        
        for strategy in strategies:
            results = engine.run(strategy, data, show_progress=False)
            assert results is not None
        
        elapsed = time.time() - start_time
        
        # 验证性能：4 个策略应在 2 秒内完成
        assert elapsed < 2.0, f"多策略回测耗时过长：{elapsed:.2f}秒"
        
        print(f"\n多策略回测性能：4 个策略，{len(data)}天数据，耗时{elapsed:.3f}秒")


class TestBatchBacktestPerformance:
    """批量回测性能测试"""

    def test_batch_backtest_parallel(self):
        """测试并行批量回测性能"""
        symbols = [f'STOCK{i:03d}' for i in range(20)]
        
        config = BatchBacktestConfig(
            symbols=symbols,
            strategy_class=MACrossStrategy,
            strategy_params={'short_window': 5, 'long_window': 20},
            initial_capital=100000,
            start_date='2020-01-01',
            end_date='2023-12-31',
            data_source='mock',
            n_jobs=4,
            show_progress=False
        )
        
        batch_backtester = BatchBacktester(config)
        
        start_time = time.time()
        results = batch_backtester.run()
        elapsed = time.time() - start_time
        
        # 验证性能：20 只股票应在 10 秒内完成
        assert elapsed < 10.0, f"批量回测耗时过长：{elapsed:.2f}秒"
        
        # 验证结果
        successful = [r for r in results if r.success]
        assert len(successful) > 0
        
        print(f"\n并行批量回测性能：{len(symbols)}只股票，耗时{elapsed:.3f}秒")

    def test_batch_backtest_serial_vs_parallel(self):
        """测试串行 vs 并行性能对比"""
        symbols = [f'STOCK{i:03d}' for i in range(10)]
        
        # 串行
        config_serial = BatchBacktestConfig(
            symbols=symbols,
            strategy_class=RSIStrategy,
            strategy_params={'rsi_period': 14},
            initial_capital=100000,
            start_date='2020-01-01',
            end_date='2023-12-31',
            data_source='mock',
            n_jobs=1,
            show_progress=False
        )
        
        batch_serial = BatchBacktester(config_serial)
        start_time = time.time()
        batch_serial.run()
        time_serial = time.time() - start_time
        
        # 并行
        config_parallel = BatchBacktestConfig(
            symbols=symbols,
            strategy_class=RSIStrategy,
            strategy_params={'rsi_period': 14},
            initial_capital=100000,
            start_date='2020-01-01',
            end_date='2023-12-31',
            data_source='mock',
            n_jobs=4,
            show_progress=False
        )
        
        batch_parallel = BatchBacktester(config_parallel)
        start_time = time.time()
        batch_parallel.run()
        time_parallel = time.time() - start_time
        
        # 验证并行加速
        speedup = time_serial / time_parallel if time_parallel > 0 else float('inf')
        print(f"\n串行 vs 并行性能对比:")
        print(f"  串行：{time_serial:.3f}秒")
        print(f"  并行：{time_parallel:.3f}秒")
        print(f"  加速比：{speedup:.2f}x")


class TestOptimizerPerformance:
    """优化器性能测试"""

    def test_grid_search_performance(self):
        """测试网格搜索性能"""
        data = generate_large_dataset(n_days=500, n_stocks=1)[0]
        
        def backtest_func(strategy, data):
            engine = BacktestEngine()
            return engine.run(strategy, data, show_progress=False)
        
        optimizer = StrategyOptimizer(n_jobs=1)
        
        # 中等规模参数空间
        param_ranges = [
            ParameterRange(name='short_window', values=list(range(5, 21, 2))),  # 8 个值
            ParameterRange(name='long_window', values=list(range(20, 61, 5)))  # 9 个值
        ]
        
        total_combos = len(param_ranges[0].values) * len(param_ranges[1].values)
        
        start_time = time.time()
        results = optimizer.grid_search(
            strategy_class=MACrossStrategy,
            parameter_ranges=param_ranges,
            backtest_func=backtest_func,
            data=data,
            initial_capital=100000,
            show_progress=False
        )
        elapsed = time.time() - start_time
        
        # 验证结果
        assert len(results) == total_combos
        
        print(f"\n网格搜索性能：{total_combos}个参数组合，耗时{elapsed:.3f}秒")
        print(f"  平均每组合：{elapsed/total_combos*1000:.2f}毫秒")

    def test_large_parameter_space(self):
        """测试大参数空间优化"""
        data = generate_large_dataset(n_days=300, n_stocks=1)[0]
        
        def backtest_func(strategy, data):
            engine = BacktestEngine()
            return engine.run(strategy, data, show_progress=False)
        
        optimizer = StrategyOptimizer(n_jobs=4)
        
        # 大参数空间
        param_ranges = [
            ParameterRange(name='rsi_period', values=list(range(10, 30, 2))),  # 10 个值
            ParameterRange(name='oversold_threshold', values=[20, 25, 30, 35]),  # 4 个值
            ParameterRange(name='overbought_threshold', values=[65, 70, 75, 80])  # 4 个值
        ]
        
        total_combos = 10 * 4 * 4
        
        start_time = time.time()
        results = optimizer.grid_search(
            strategy_class=RSIStrategy,
            parameter_ranges=param_ranges,
            backtest_func=backtest_func,
            data=data,
            initial_capital=100000,
            show_progress=False
        )
        elapsed = time.time() - start_time
        
        print(f"\n大参数空间优化性能：")
        print(f"  参数组合数：{total_combos}")
        print(f"  总耗时：{elapsed:.3f}秒")
        print(f"  平均每组合：{elapsed/total_combos*1000:.2f}毫秒")


class TestMemoryUsage:
    """内存使用测试"""

    def test_memory_efficiency(self):
        """测试内存效率"""
        import tracemalloc
        
        # 开始内存跟踪
        tracemalloc.start()
        
        # 执行回测
        data = generate_large_dataset(n_days=1000, n_stocks=1)[0]
        strategy = MACrossStrategy()
        engine = BacktestEngine()
        results = engine.run(strategy, data, show_progress=False)
        
        # 获取内存使用
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # 验证内存使用 (峰值应小于 100MB)
        peak_mb = peak / 1024 / 1024
        print(f"\n内存使用测试:")
        print(f"  当前：{current / 1024 / 1024:.2f} MB")
        print(f"  峰值：{peak_mb:.2f} MB")
        
        assert peak_mb < 100, f"内存使用过高：{peak_mb:.2f}MB"

    def test_batch_backtest_memory(self):
        """测试批量回测内存使用"""
        import tracemalloc
        
        tracemalloc.start()
        
        symbols = [f'STOCK{i:03d}' for i in range(10)]
        
        config = BatchBacktestConfig(
            symbols=symbols,
            strategy_class=MACrossStrategy,
            strategy_params={'short_window': 5, 'long_window': 20},
            initial_capital=100000,
            start_date='2020-01-01',
            end_date='2023-12-31',
            data_source='mock',
            n_jobs=4,
            show_progress=False
        )
        
        batch_backtester = BatchBacktester(config)
        results = batch_backtester.run()
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        peak_mb = peak / 1024 / 1024
        print(f"\n批量回测内存使用:")
        print(f"  峰值：{peak_mb:.2f} MB")
        
        # 批量回测内存使用应小于 200MB
        assert peak_mb < 200, f"批量回测内存使用过高：{peak_mb:.2f}MB"


class TestScalability:
    """扩展性测试"""

    def test_data_size_scalability(self):
        """测试数据规模扩展性"""
        data_sizes = [200, 500, 1000, 2000]
        times = []
        
        strategy = MACrossStrategy()
        engine = BacktestEngine()
        
        for n_days in data_sizes:
            data = generate_large_dataset(n_days=n_days, n_stocks=1)[0]
            
            start_time = time.time()
            results = engine.run(strategy, data, show_progress=False)
            elapsed = time.time() - start_time
            times.append(elapsed)
            
            print(f"  数据规模：{n_days}天，耗时：{elapsed:.3f}秒")
        
        # 验证线性扩展 (时间增长应接近线性)
        # 2000 天的时间不应超过 200 天的 15 倍
        assert times[-1] / times[0] < 15, "性能随数据规模增长过快"

    def test_strategy_count_scalability(self):
        """测试策略数量扩展性"""
        strategy_counts = [1, 2, 4, 8]
        times = []
        
        data = generate_large_dataset(n_days=500, n_stocks=1)[0]
        engine = BacktestEngine()
        
        for count in strategy_counts:
            strategies = []
            for i in range(count):
                if i % 4 == 0:
                    strategies.append(MACrossStrategy(short_window=5+i, long_window=20+i))
                elif i % 4 == 1:
                    strategies.append(RSIStrategy(rsi_period=14+i))
                elif i % 4 == 2:
                    strategies.append(MACDStrategy(fast_period=12, slow_period=26+i))
                else:
                    strategies.append(BollingerStrategy(window=20+i))
            
            start_time = time.time()
            for strategy in strategies:
                results = engine.run(strategy, data, show_progress=False)
            elapsed = time.time() - start_time
            times.append(elapsed)
            
            print(f"  策略数量：{count}，耗时：{elapsed:.3f}秒")
        
        # 验证线性扩展
        assert times[-1] / times[0] < 10, "性能随策略数量增长过快"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short', '-s'])
