"""
Strategy 模块单元测试
测试覆盖率目标：90%+
"""

import pytest
from tradeflow.strategy import Strategy


class TestStrategyInit:
    """Strategy 初始化测试"""

    def test_default_init(self):
        """测试默认初始化"""
        strategy = Strategy()
        assert strategy.name == "Unnamed Strategy"
        assert strategy.conditions == []
        assert strategy.actions == []

    def test_init_with_name(self):
        """测试带名称初始化"""
        strategy = Strategy(name="测试策略")
        assert strategy.name == "测试策略"
        assert strategy.conditions == []
        assert strategy.actions == []


class TestStrategyFromNaturalLanguage:
    """自然语言策略创建测试"""

    def test_from_natural_language_basic(self):
        """测试基础自然语言策略创建"""
        description = "当 5 日均线上穿 20 日均线时买入"
        strategy = Strategy.from_natural_language(description)
        assert strategy.name == description
        assert isinstance(strategy, Strategy)

    def test_from_natural_language_complex(self):
        """测试复杂自然语言策略创建"""
        description = "当 MACD 金叉且成交量放大时买入，死叉时卖出"
        strategy = Strategy.from_natural_language(description)
        assert strategy.name == description
        assert isinstance(strategy, Strategy)

    def test_from_natural_language_returns_instance(self):
        """测试返回正确的实例类型"""
        strategy = Strategy.from_natural_language("测试策略")
        assert isinstance(strategy, Strategy)


class TestStrategyAddCondition:
    """添加交易条件测试"""

    def test_add_single_condition(self, mock_strategy):
        """测试添加单个条件"""
        strategy = mock_strategy
        result = strategy.add_condition("MA5 > MA20")
        assert len(strategy.conditions) == 1
        assert strategy.conditions[0] == "MA5 > MA20"
        assert result is strategy  # 支持链式调用

    def test_add_multiple_conditions(self, mock_strategy):
        """测试添加多个条件"""
        strategy = mock_strategy
        strategy.add_condition("MA5 > MA20")
        strategy.add_condition("Volume > MA(Volume, 5)")
        assert len(strategy.conditions) == 2

    def test_add_condition_chainable(self, mock_strategy):
        """测试链式调用"""
        strategy = mock_strategy
        result = strategy.add_condition("COND1").add_condition("COND2")
        assert len(strategy.conditions) == 2
        assert result is strategy


class TestStrategyAddAction:
    """添加交易动作测试"""

    def test_add_single_action(self, mock_strategy):
        """测试添加单个动作"""
        strategy = mock_strategy
        result = strategy.add_action("BUY")
        assert len(strategy.actions) == 1
        assert strategy.actions[0] == "BUY"
        assert result is strategy

    def test_add_multiple_actions(self, mock_strategy):
        """测试添加多个动作"""
        strategy = mock_strategy
        strategy.add_action("BUY")
        strategy.add_action("SELL")
        strategy.add_action("HOLD")
        assert len(strategy.actions) == 3

    def test_add_action_chainable(self, mock_strategy):
        """测试链式调用"""
        strategy = mock_strategy
        result = strategy.add_action("BUY").add_action("SELL")
        assert len(strategy.actions) == 2
        assert result is strategy


class TestStrategyBacktest:
    """策略回测测试"""

    def test_backtest_basic(self, mock_strategy):
        """测试基础回测"""
        result = mock_strategy.backtest("2023-01-01", "2024-01-01")
        assert isinstance(result, dict)
        assert "total_return" in result
        assert "sharpe_ratio" in result
        assert "max_drawdown" in result
        assert "win_rate" in result

    def test_backtest_date_range(self, mock_strategy):
        """测试回测日期范围"""
        result = mock_strategy.backtest("2023-06-01", "2023-12-31")
        assert isinstance(result, dict)

    def test_backtest_returns_metrics(self, mock_strategy):
        """测试回测返回指标"""
        result = mock_strategy.backtest("2023-01-01", "2024-01-01")
        assert all(key in result for key in [
            "total_return",
            "sharpe_ratio",
            "max_drawdown",
            "win_rate"
        ])


class TestStrategyExecute:
    """策略执行测试"""

    def test_execute_basic(self, mock_strategy):
        """测试基础执行"""
        result = mock_strategy.execute()
        assert result is True

    def test_execute_with_conditions(self, mock_strategy):
        """测试带条件的执行"""
        mock_strategy.add_condition("MA5 > MA20")
        mock_strategy.add_action("BUY")
        result = mock_strategy.execute()
        assert result is True


class TestStrategyIntegration:
    """Strategy 集成测试"""

    def test_full_workflow(self):
        """测试完整工作流"""
        strategy = Strategy.from_natural_language("均线交叉策略")
        strategy.add_condition("MA5 > MA20")
        strategy.add_action("BUY")
        result = strategy.backtest("2023-01-01", "2024-01-01")
        assert isinstance(result, dict)
        execute_result = strategy.execute()
        assert execute_result is True

    def test_strategy_with_multiple_conditions_and_actions(self):
        """测试多条件多动作策略"""
        strategy = Strategy(name="复杂策略")
        strategy.add_condition("MA5 > MA20")
        strategy.add_condition("MACD > 0")
        strategy.add_action("BUY")
        strategy.add_action("HOLD")
        assert len(strategy.conditions) == 2
        assert len(strategy.actions) == 2
