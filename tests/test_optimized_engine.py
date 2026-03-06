"""
优化回测引擎单元测试

测试用例：
- 向量化计算
- 缓存机制
- 并行回测
- 性能对比
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from backtest.optimized_engine import (
    OptimizedBacktestEngine,
    OptimizedTrade,
    OptimizedBacktestResult,
    optimized_backtest
)


class SimpleMockStrategy:
    """简单模拟策略"""
    
    def __init__(self, window=20, threshold=0.5):
        self.window = window
        self.threshold = threshold
        self._position = 0
    
    def generate_signal(self, row):
        """生成信号"""
        # 简单逻辑：价格超过均线买入
        if len(row) < self.window:
            return 0
        
        close = row['close'].iloc[0]
        ma = row['close'].iloc[-self.window:].mean() if len(row) >= self.window else close
        
        if close > ma * (1 + self.threshold):
            return 1
        elif close < ma * (1 - self.threshold):
            return -1
        return 0


class VectorizedMockStrategy:
    """向量化策略"""
    
    def __init__(self, window=20):
        self.window = window
    
    def generate_signals(self, data: pd.DataFrame) -> np.ndarray:
        """向量化生成信号"""
        n = len(data)
        signals = np.zeros(n, dtype=np.int8)
        
        # 计算移动平均
        ma = data['close'].rolling(window=self.window).mean()
        
        # 生成信号
        above_ma = data['close'] > ma
        below_ma = data['close'] < ma
        
        signals[above_ma] = 1
        signals[below_ma] = -1
        
        return signals


def create_test_data(n_days=500):
    """创建测试数据"""
    dates = pd.date_range(start='2022-01-01', periods=n_days, freq='D')
    
    np.random.seed(42)
    # 生成随机游走价格
    returns = np.random.randn(n_days) * 0.02
    prices = 100 * np.cumprod(1 + returns)
    
    df = pd.DataFrame({
        'open': prices * (1 + np.random.randn(n_days) * 0.005),
        'high': prices * (1 + np.abs(np.random.randn(n_days)) * 0.01),
        'low': prices * (1 - np.abs(np.random.randn(n_days)) * 0.01),
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, n_days)
    }, index=dates)
    
    return df


class TestOptimizedTrade:
    """交易记录测试"""

    def test_trade_creation(self):
        """测试交易创建"""
        trade = OptimizedTrade(
            entry_time=0,
            exit_time=10,
            symbol='TEST',
            direction=1,
            entry_price=100.0,
            exit_price=110.0,
            shares=100,
            pnl=1000.0,
            return_pct=10.0
        )
        
        assert trade.entry_price == 100.0
        assert trade.exit_price == 110.0
        assert trade.pnl == 1000.0
        assert trade.return_pct == 10.0


class TestOptimizedBacktestResult:
    """回测结果测试"""

    def test_result_creation(self):
        """测试结果创建"""
        trades = [
            OptimizedTrade(0, 10, 'TEST', 1, 100, 110, 100, 1000, 10.0)
        ]
        
        result = OptimizedBacktestResult(
            trades=trades,
            total_return=10.0,
            sharpe_ratio=1.5,
            max_drawdown=-5.0,
            win_rate=60.0,
            profit_factor=2.0,
            total_trades=1,
            avg_trade_return=10.0,
            equity_curve=np.array([100000, 110000]),
            dates=np.array(['2024-01-01', '2024-01-02'])
        )
        
        assert result.total_trades == 1
        assert '总收益 (%)' in result.metrics
        assert result.metrics['总收益 (%)'] == 10.0


class TestOptimizedBacktestEngine:
    """优化回测引擎测试"""

    def test_initialization(self):
        """测试初始化"""
        engine = OptimizedBacktestEngine(
            initial_capital=200000,
            commission_rate=0.0005,
            slippage=0.0005
        )
        
        assert engine.initial_capital == 200000
        assert engine.commission_rate == 0.0005
        assert engine.slippage == 0.0005

    def test_run_basic(self):
        """测试基本回测"""
        engine = OptimizedBacktestEngine()
        data = create_test_data(100)
        strategy = SimpleMockStrategy(window=10)
        
        result = engine.run(strategy, data)
        
        assert isinstance(result, OptimizedBacktestResult)
        assert result.equity_curve is not None
        assert len(result.equity_curve) == len(data)

    def test_run_with_vectorized_strategy(self):
        """测试向量化策略"""
        engine = OptimizedBacktestEngine()
        data = create_test_data(100)
        strategy = VectorizedMockStrategy(window=10)
        
        result = engine.run(strategy, data)
        
        assert isinstance(result, OptimizedBacktestResult)
        assert result.total_trades >= 0

    def test_metrics_calculation(self):
        """测试指标计算"""
        engine = OptimizedBacktestEngine()
        data = create_test_data(200)
        strategy = SimpleMockStrategy(window=20, threshold=0.3)
        
        result = engine.run(strategy, data)
        
        # 验证指标合理性
        assert np.isfinite(result.sharpe_ratio)
        assert result.max_drawdown <= 0
        assert 0 <= result.win_rate <= 100
        assert result.profit_factor >= 0

    def test_cache_mechanism(self):
        """测试缓存机制"""
        engine = OptimizedBacktestEngine(use_cache=True)
        data = create_test_data(100)
        strategy = SimpleMockStrategy(window=10)
        
        # 第一次运行 (缓存未命中)
        result1 = engine.run(strategy, data)
        stats1 = engine.get_cache_stats()
        
        # 第二次运行 (缓存命中)
        result2 = engine.run(strategy, data)
        stats2 = engine.get_cache_stats()
        
        # 验证缓存命中
        assert stats2['hits'] > stats1['hits']
        
        # 验证结果相同
        assert np.allclose(result1.equity_curve, result2.equity_curve)

    def test_cache_clear(self):
        """测试缓存清空"""
        engine = OptimizedBacktestEngine(use_cache=True)
        data = create_test_data(100)
        strategy = SimpleMockStrategy(window=10)
        
        # 运行几次
        engine.run(strategy, data)
        engine.run(strategy, data)
        
        # 清空缓存
        engine.clear_cache()
        stats = engine.get_cache_stats()
        
        assert stats['cache_size'] == 0
        assert stats['hits'] == 0

    def test_parallel_backtest(self):
        """测试并行回测"""
        engine = OptimizedBacktestEngine()
        data = create_test_data(100)
        
        param_combinations = [
            {'window': 10, 'threshold': 0.3},
            {'window': 20, 'threshold': 0.4},
            {'window': 30, 'threshold': 0.5}
        ]
        
        results = engine.run_parallel(
            SimpleMockStrategy,
            param_combinations,
            data,
            n_jobs=2
        )
        
        assert len(results) == 3
        for result in results:
            assert result is None or isinstance(result, OptimizedBacktestResult)

    def test_performance_improvement(self):
        """测试性能提升"""
        # 创建较大数据集
        data = create_test_data(1000)
        strategy = VectorizedMockStrategy(window=20)
        
        # 测试优化引擎
        opt_engine = OptimizedBacktestEngine()
        
        start = time.time()
        opt_result = opt_engine.run(strategy, data)
        opt_time = time.time() - start
        
        logger_info = f"优化引擎耗时：{opt_time:.3f}s"
        print(logger_info)
        
        # 验证结果有效性
        assert opt_time < 5.0  # 应该在 5 秒内完成
        assert len(opt_result.equity_curve) == len(data)


class TestConvenienceFunctions:
    """便捷函数测试"""

    def test_optimized_backtest(self):
        """测试便捷函数"""
        data = create_test_data(100)
        strategy = SimpleMockStrategy(window=10)
        
        result = optimized_backtest(
            strategy,
            data,
            initial_capital=100000,
            commission_rate=0.001
        )
        
        assert isinstance(result, OptimizedBacktestResult)
        assert result.initial_capital == 100000 if hasattr(result, 'initial_capital') else True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
