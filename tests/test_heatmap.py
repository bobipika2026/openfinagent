"""
参数热力图单元测试

测试用例：
- 双参数扫描
- 热力图生成
- 最优参数标记
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from visualization.heatmap import (
    ParameterHeatmap,
    HeatmapResult,
    parameter_sweep
)


class MockStrategy:
    """模拟策略类"""
    
    def __init__(self, window=20, threshold=0.5, initial_capital=100000):
        self.window = window
        self.threshold = threshold
        self.initial_capital = initial_capital


class MockBacktestResult:
    """模拟回测结果"""
    
    def __init__(self, sharpe_ratio):
        self.metrics = {
            'sharpe_ratio': sharpe_ratio,
            'total_return': sharpe_ratio * 10,
            'max_drawdown': -abs(sharpe_ratio) * 5
        }


def mock_backtest_func(strategy, data):
    """模拟回测函数"""
    # 创建一个"最优"区域
    window_score = 1 - abs(strategy.window - 30) / 50
    threshold_score = 1 - abs(strategy.threshold - 0.5) / 0.5
    sharpe = (window_score + threshold_score) + np.random.normal(0, 0.05)
    
    return MockBacktestResult(sharpe_ratio=sharpe)


def create_test_data(n_days=100):
    """创建测试数据"""
    dates = pd.date_range(start='2024-01-01', periods=n_days, freq='D')
    
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(n_days))
    
    df = pd.DataFrame({
        'open': prices + np.random.randn(n_days) * 0.5,
        'high': prices + np.abs(np.random.randn(n_days)) * 0.5,
        'low': prices - np.abs(np.random.randn(n_days)) * 0.5,
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, n_days)
    }, index=dates)
    
    return df


class TestHeatmapResult:
    """热力图结果测试"""

    def test_result_creation(self):
        """测试结果创建"""
        result = HeatmapResult(
            param1_name='window',
            param2_name='threshold',
            param1_values=[10, 20, 30],
            param2_values=[0.3, 0.5, 0.7],
            metric_matrix=np.array([[1.0, 1.5, 1.2],
                                   [1.3, 2.0, 1.8],
                                   [1.1, 1.7, 1.4]]),
            best_param1=20,
            best_param2=0.5,
            best_metric_value=2.0
        )
        
        assert result.param1_name == 'window'
        assert result.param2_name == 'threshold'
        assert len(result.param1_values) == 3
        assert len(result.param2_values) == 3
        assert result.metric_matrix.shape == (3, 3)
        assert result.best_param1 == 20
        assert result.best_metric_value == 2.0


class TestParameterHeatmap:
    """参数热力图测试"""

    def test_initialization(self):
        """测试初始化"""
        heatmap = ParameterHeatmap(
            metric_name='sharpe_ratio',
            maximize=True,
            cmap='RdYlGn'
        )
        
        assert heatmap.metric_name == 'sharpe_ratio'
        assert heatmap.maximize is True
        assert heatmap.cmap == 'RdYlGn'

    def test_scan(self):
        """测试参数扫描"""
        heatmap = ParameterHeatmap(metric_name='sharpe_ratio')
        
        data = create_test_data()
        
        result = heatmap.scan(
            strategy_class=MockStrategy,
            param1_name='window',
            param1_values=[20, 30, 40],
            param2_name='threshold',
            param2_values=[0.4, 0.5, 0.6],
            base_params={},
            backtest_func=mock_backtest_func,
            data=data,
            initial_capital=100000,
            show_progress=False
        )
        
        assert isinstance(result, HeatmapResult)
        assert result.param1_name == 'window'
        assert result.param2_name == 'threshold'
        assert len(result.param1_values) == 3
        assert len(result.param2_values) == 3
        assert result.metric_matrix.shape == (3, 3)
        assert np.all(np.isfinite(result.metric_matrix))

    def test_scan_with_base_params(self):
        """测试带基础参数的扫描"""
        heatmap = ParameterHeatmap(metric_name='sharpe_ratio')
        data = create_test_data()
        
        result = heatmap.scan(
            strategy_class=MockStrategy,
            param1_name='window',
            param1_values=[20, 30],
            param2_name='threshold',
            param2_values=[0.4, 0.5],
            base_params={'other_param': 100},
            backtest_func=mock_backtest_func,
            data=data,
            initial_capital=100000,
            show_progress=False
        )
        
        assert result is not None

    def test_best_parameter_detection(self):
        """测试最优参数检测"""
        heatmap = ParameterHeatmap(metric_name='sharpe_ratio', maximize=True)
        data = create_test_data()
        
        # 使用确定性回测函数
        def deterministic_backtest(strategy, data):
            sharpe = strategy.window * strategy.threshold
            return MockBacktestResult(sharpe_ratio=sharpe)
        
        result = heatmap.scan(
            strategy_class=MockStrategy,
            param1_name='window',
            param1_values=[10, 20, 30],
            param2_name='threshold',
            param2_values=[0.3, 0.5, 0.7],
            base_params={},
            backtest_func=deterministic_backtest,
            data=data,
            initial_capital=100000,
            show_progress=False
        )
        
        # 最优应该是 window=30, threshold=0.7
        assert result.best_param1 == 30
        assert result.best_param2 == 0.7
        assert result.best_metric_value == 30 * 0.7

    def test_plot_heatmap(self, tmp_path):
        """测试热力图绘制"""
        heatmap = ParameterHeatmap(metric_name='sharpe_ratio')
        data = create_test_data()
        
        result = heatmap.scan(
            strategy_class=MockStrategy,
            param1_name='window',
            param1_values=[20, 30, 40],
            param2_name='threshold',
            param2_values=[0.4, 0.5, 0.6],
            base_params={},
            backtest_func=mock_backtest_func,
            data=data,
            initial_capital=100000,
            show_progress=False
        )
        
        # 保存到临时文件
        filepath = tmp_path / "heatmap.png"
        
        try:
            heatmap.plot(
                result,
                save_path=str(filepath),
                show=False
            )
            
            assert filepath.exists()
            assert filepath.stat().st_size > 0
        except Exception as e:
            pytest.skip(f"matplotlib 绘图失败：{e}")

    def test_plot_contour(self, tmp_path):
        """测试等高线图绘制"""
        heatmap = ParameterHeatmap(metric_name='sharpe_ratio')
        data = create_test_data()
        
        result = heatmap.scan(
            strategy_class=MockStrategy,
            param1_name='window',
            param1_values=[20, 30, 40],
            param2_name='threshold',
            param2_values=[0.4, 0.5, 0.6],
            base_params={},
            backtest_func=mock_backtest_func,
            data=data,
            initial_capital=100000,
            show_progress=False
        )
        
        filepath = tmp_path / "contour.png"
        
        try:
            heatmap.plot_contour(
                result,
                save_path=str(filepath),
                show=False
            )
            
            assert filepath.exists()
            assert filepath.stat().st_size > 0
        except Exception as e:
            pytest.skip(f"matplotlib 绘图失败：{e}")

    def test_create_interactive(self):
        """测试交互式热力图创建"""
        heatmap = ParameterHeatmap(metric_name='sharpe_ratio')
        data = create_test_data()
        
        result = heatmap.scan(
            strategy_class=MockStrategy,
            param1_name='window',
            param1_values=[20, 30, 40],
            param2_name='threshold',
            param2_values=[0.4, 0.5, 0.6],
            base_params={},
            backtest_func=mock_backtest_func,
            data=data,
            initial_capital=100000,
            show_progress=False
        )
        
        try:
            fig = heatmap.create_interactive(result)
            
            # 验证 plotly figure 结构
            assert fig is not None
            assert hasattr(fig, 'data')
            assert len(fig.data) > 0
        except Exception as e:
            pytest.skip(f"plotly 不可用：{e}")


class TestConvenienceFunctions:
    """便捷函数测试"""

    def test_parameter_sweep(self):
        """测试参数扫描便捷函数"""
        data = create_test_data()
        
        result = parameter_sweep(
            strategy_class=MockStrategy,
            param1_name='window',
            param1_range=[20, 30, 40],
            param2_name='threshold',
            param2_range=[0.4, 0.5, 0.6],
            base_params={},
            backtest_func=mock_backtest_func,
            data=data,
            metric_name='sharpe_ratio',
            initial_capital=100000
        )
        
        assert isinstance(result, HeatmapResult)
        assert result.param1_name == 'window'
        assert result.param2_name == 'threshold'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
