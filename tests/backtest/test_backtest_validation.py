"""
策略回测验证测试
验证不同策略的回测表现
"""

import pytest
from tradeflow import Strategy, Analyzer


@pytest.mark.backtest
class TestBacktestValidation:
    """回测验证测试"""

    def test_moving_average_crossover_backtest(self):
        """测试均线交叉策略回测"""
        strategy = Strategy.from_natural_language("均线交叉策略：5 日线上穿 20 日线买入")
        strategy.add_condition("MA5 > MA20")
        strategy.add_action("BUY")
        
        result = strategy.backtest("2023-01-01", "2024-01-01")
        
        assert isinstance(result, dict)
        assert "total_return" in result
        assert "sharpe_ratio" in result
        assert "max_drawdown" in result
        assert "win_rate" in result

    def test_macd_strategy_backtest(self):
        """测试 MACD 策略回测"""
        strategy = Strategy.from_natural_language("MACD 金叉策略")
        strategy.add_condition("MACD > Signal")
        strategy.add_action("BUY")
        
        result = strategy.backtest("2023-01-01", "2024-01-01")
        
        assert isinstance(result, dict)
        assert all(key in result for key in [
            "total_return", "sharpe_ratio", "max_drawdown", "win_rate"
        ])

    def test_rsi_strategy_backtest(self):
        """测试 RSI 策略回测"""
        strategy = Strategy.from_natural_language("RSI 超卖策略")
        strategy.add_condition("RSI < 30")
        strategy.add_action("BUY")
        
        result = strategy.backtest("2023-01-01", "2024-01-01")
        
        assert isinstance(result, dict)

    def test_multi_condition_strategy_backtest(self):
        """测试多条件策略回测"""
        strategy = Strategy.from_natural_language("多因子策略")
        strategy.add_condition("MA5 > MA20")
        strategy.add_condition("MACD > 0")
        strategy.add_condition("Volume > MA(Volume, 5)")
        strategy.add_action("BUY")
        
        result = strategy.backtest("2023-01-01", "2024-01-01")
        
        assert isinstance(result, dict)


@pytest.mark.backtest
class TestBacktestPerformance:
    """回测性能测试"""

    def test_backtest_date_range_performance(self):
        """测试不同日期范围的回测性能"""
        strategy = Strategy(name="性能测试策略")
        strategy.add_action("BUY")
        
        date_ranges = [
            ("2023-01-01", "2023-03-31"),  # 季度
            ("2023-01-01", "2023-06-30"),  # 半年
            ("2023-01-01", "2023-12-31"),  # 全年
        ]
        
        for start, end in date_ranges:
            result = strategy.backtest(start, end)
            assert isinstance(result, dict)

    def test_backtest_multiple_symbols(self):
        """测试多标的回测"""
        symbols = ["600519.SH", "000001.SZ", "300750.SZ"]
        
        for symbol in symbols:
            strategy = Strategy(name=f"{symbol} 策略")
            strategy.add_action("BUY")
            result = strategy.backtest("2023-01-01", "2024-01-01")
            assert isinstance(result, dict)


@pytest.mark.backtest
class TestBacktestMetrics:
    """回测指标验证测试"""

    def test_backtest_returns_metrics(self):
        """测试回测返回完整指标"""
        strategy = Strategy(name="指标测试策略")
        strategy.add_action("BUY")
        
        result = strategy.backtest("2023-01-01", "2024-01-01")
        
        required_metrics = [
            "total_return",
            "sharpe_ratio",
            "max_drawdown",
            "win_rate"
        ]
        
        for metric in required_metrics:
            assert metric in result, f"缺少指标：{metric}"
            assert isinstance(result[metric], (int, float))

    def test_backtest_metric_ranges(self):
        """测试回测指标合理范围"""
        strategy = Strategy(name="范围测试策略")
        strategy.add_action("BUY")
        
        result = strategy.backtest("2023-01-01", "2024-01-01")
        
        # 验证指标在合理范围内
        assert -1.0 <= result["total_return"] <= 10.0  # 回报率 -100% 到 1000%
        assert -5.0 <= result["sharpe_ratio"] <= 10.0  # 夏普比率合理范围
        assert -1.0 <= result["max_drawdown"] <= 0.0  # 最大回撤 0% 到 -100%
        assert 0.0 <= result["win_rate"] <= 1.0  # 胜率 0% 到 100%


@pytest.mark.backtest
class TestBacktestEdgeCases:
    """回测边界情况测试"""

    def test_backtest_short_period(self):
        """测试短期回测"""
        strategy = Strategy(name="短期策略")
        strategy.add_action("BUY")
        
        result = strategy.backtest("2023-06-01", "2023-06-30")
        assert isinstance(result, dict)

    def test_backtest_single_strategy(self):
        """测试单一策略回测"""
        strategy = Strategy(name="单一策略")
        strategy.add_condition("MA5 > MA20")
        strategy.add_action("BUY")
        
        result = strategy.backtest("2023-01-01", "2024-01-01")
        assert isinstance(result, dict)

    def test_backtest_with_no_conditions(self):
        """测试无条件策略回测"""
        strategy = Strategy(name="无条件策略")
        strategy.add_action("BUY")
        
        result = strategy.backtest("2023-01-01", "2024-01-01")
        assert isinstance(result, dict)


@pytest.mark.backtest
class TestBacktestComparison:
    """回测对比测试"""

    def test_multiple_strategies_comparison(self):
        """测试多策略对比"""
        strategies = {
            "均线交叉": Strategy.from_natural_language("均线交叉策略"),
            "MACD 金叉": Strategy.from_natural_language("MACD 金叉策略"),
            "RSI 超卖": Strategy.from_natural_language("RSI 超卖策略")
        }
        
        results = {}
        for name, strategy in strategies.items():
            strategy.add_action("BUY")
            results[name] = strategy.backtest("2023-01-01", "2024-01-01")
        
        # 验证所有策略都返回了结果
        assert len(results) == len(strategies)
        for name, result in results.items():
            assert isinstance(result, dict)
            assert "total_return" in result

    def test_backtest_consistency(self):
        """测试回测一致性"""
        strategy = Strategy(name="一致性测试策略")
        strategy.add_action("BUY")
        
        # 多次回测同一策略
        result1 = strategy.backtest("2023-01-01", "2024-01-01")
        result2 = strategy.backtest("2023-01-01", "2024-01-01")
        
        # 验证结果结构一致
        assert result1.keys() == result2.keys()
