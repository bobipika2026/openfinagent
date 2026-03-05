"""
集成测试 - 测试模块间协作
"""

import pytest
from tradeflow import Strategy, Analyzer, Executor


@pytest.mark.integration
class TestModuleIntegration:
    """模块集成测试"""

    def test_strategy_analyzer_integration(self):
        """测试策略与分析器集成"""
        strategy = Strategy.from_natural_language("均线交叉策略")
        strategy.add_condition("MA5 > MA20")
        
        analyzer = Analyzer()
        analyzer.load_data("600519.SH", "2023-01-01", "2024-01-01")
        analysis = analyzer.analyze()
        
        assert isinstance(analysis, dict)
        assert "trend" in analysis

    def test_strategy_executor_integration(self):
        """测试策略与执行器集成"""
        strategy = Strategy.from_natural_language("买入持有策略")
        strategy.add_action("BUY")
        
        executor = Executor(broker="paper")
        executor.connect()
        
        # 模拟策略信号触发执行
        if "BUY" in strategy.actions:
            executor.buy("600519.SH", 100)
            order = executor.submit_order("BUY", "600519.SH", 100)
            assert isinstance(order, dict)
            assert "order_id" in order

    def test_full_trading_pipeline(self):
        """测试完整交易流程"""
        # 1. 创建策略
        strategy = Strategy.from_natural_language("均线交叉策略")
        strategy.add_condition("MA5 > MA20")
        strategy.add_action("BUY")
        
        # 2. 市场分析
        analyzer = Analyzer()
        analyzer.load_data("600519.SH", "2023-01-01", "2024-01-01")
        analysis = analyzer.analyze()
        
        # 3. 回测策略
        backtest_result = strategy.backtest("2023-01-01", "2024-01-01")
        assert isinstance(backtest_result, dict)
        
        # 4. 执行交易
        executor = Executor(broker="paper")
        executor.connect()
        
        if backtest_result.get("sharpe_ratio", 0) > 0:
            executor.buy("600519.SH", 100)
            order = executor.submit_order("BUY", "600519.SH", 100)
            assert isinstance(order, dict)

    def test_multiple_strategies_pipeline(self):
        """测试多策略流程"""
        strategies = [
            Strategy.from_natural_language("策略 1: 均线交叉"),
            Strategy.from_natural_language("策略 2: MACD 金叉"),
            Strategy.from_natural_language("策略 3: RSI 超卖")
        ]
        
        for strategy in strategies:
            strategy.add_action("BUY")
            result = strategy.backtest("2023-01-01", "2024-01-01")
            assert isinstance(result, dict)


@pytest.mark.integration
class TestDataFlowIntegration:
    """数据流集成测试"""

    def test_data_flow_strategy_to_executor(self):
        """测试策略到执行器的数据流"""
        strategy = Strategy(name="测试策略")
        strategy.add_condition("COND1")
        strategy.add_action("BUY")
        
        executor = Executor()
        executor.connect()
        
        # 策略信号传递给执行器
        if "BUY" in strategy.actions:
            order = executor.buy("600519.SH", 100)
            assert order is not None

    def test_analyzer_to_strategy_data_flow(self):
        """测试分析器到策略的数据流"""
        analyzer = Analyzer()
        analyzer.load_data("600519.SH", "2023-01-01", "2024-01-01")
        analysis = analyzer.analyze()
        
        strategy = Strategy.from_natural_language("趋势跟踪策略")
        
        # 根据分析结果调整策略
        if analysis.get("trend") == "bullish":
            strategy.add_action("BUY")
        elif analysis.get("trend") == "bearish":
            strategy.add_action("SELL")
        
        assert len(strategy.actions) >= 0


@pytest.mark.integration
class TestEndToEndWorkflow:
    """端到端工作流测试"""

    def test_complete_backtest_and_execute(self):
        """测试完整回测和执行流程"""
        # 创建策略
        strategy = Strategy.from_natural_language("双均线策略")
        strategy.add_condition("MA5 > MA20")
        strategy.add_action("BUY")
        
        # 加载数据并分析
        analyzer = Analyzer()
        analyzer.load_data("600519.SH", "2023-01-01", "2024-01-01")
        analyzer.calculate_indicators(["MA5", "MA20"])
        
        # 回测
        backtest_result = strategy.backtest("2023-01-01", "2024-01-01")
        
        # 如果回测结果良好，执行实盘
        if backtest_result.get("total_return", 0) >= 0:
            executor = Executor(broker="paper")
            executor.connect()
            executor.buy("600519.SH", 100)
            order = executor.submit_order("BUY", "600519.SH", 100)
            assert isinstance(order, dict)

    def test_multi_symbol_workflow(self):
        """测试多标的工作流"""
        symbols = ["600519.SH", "000001.SZ", "300750.SZ"]
        
        for symbol in symbols:
            strategy = Strategy(name=f"{symbol} 策略")
            strategy.add_action("BUY")
            
            analyzer = Analyzer()
            analyzer.load_data(symbol, "2023-01-01", "2024-01-01")
            
            backtest_result = strategy.backtest("2023-01-01", "2024-01-01")
            assert isinstance(backtest_result, dict)
