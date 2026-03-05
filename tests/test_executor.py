"""
Executor 模块单元测试
测试覆盖率目标：90%+
"""

import pytest
from tradeflow.executor import Executor


class TestExecutorInit:
    """Executor 初始化测试"""

    def test_default_init(self):
        """测试默认初始化"""
        executor = Executor()
        assert executor.broker == "paper"
        assert executor.positions == {}

    def test_init_with_broker(self):
        """测试指定经纪商"""
        executor = Executor(broker="binance")
        assert executor.broker == "binance"
        assert executor.positions == {}

    def test_init_creates_instance(self):
        """测试创建实例"""
        executor = Executor()
        assert isinstance(executor, Executor)


class TestExecutorConnect:
    """连接经纪商测试"""

    def test_connect_basic(self, mock_executor):
        """测试基础连接"""
        result = mock_executor.connect()
        assert result is mock_executor  # 支持链式调用

    def test_connect_with_api_key(self, mock_executor):
        """测试带 API 密钥连接"""
        result = mock_executor.connect(api_key="test_key_123")
        assert result is mock_executor

    def test_connect_chainable(self, mock_executor):
        """测试链式调用"""
        result = mock_executor.connect()
        assert result is mock_executor


class TestExecutorBuy:
    """买入订单测试"""

    def test_buy_basic(self, mock_executor):
        """测试基础买入"""
        result = mock_executor.buy("600519.SH", 100)
        assert result is mock_executor  # 支持链式调用

    def test_buy_with_price(self, mock_executor):
        """测试限价买入"""
        result = mock_executor.buy("600519.SH", 100, price=150.0)
        assert result is mock_executor

    def test_buy_market_order(self, mock_executor):
        """测试市价买入"""
        result = mock_executor.buy("600519.SH", 100)
        assert result is mock_executor

    def test_buy_different_quantities(self, mock_executor):
        """测试不同数量买入"""
        quantities = [1, 10, 100, 1000]
        for qty in quantities:
            result = mock_executor.buy("600519.SH", qty)
            assert result is mock_executor
    
    def test_submit_order_returns_dict(self, mock_executor):
        """测试 submit_order 返回订单字典"""
        result = mock_executor.submit_order("BUY", "600519.SH", 100)
        assert isinstance(result, dict)
        assert "order_id" in result


class TestExecutorSell:
    """卖出订单测试"""

    def test_sell_basic(self, mock_executor):
        """测试基础卖出"""
        result = mock_executor.sell("600519.SH", 100)
        assert result is mock_executor  # 支持链式调用

    def test_sell_with_price(self, mock_executor):
        """测试限价卖出"""
        result = mock_executor.sell("600519.SH", 100, price=200.0)
        assert result is mock_executor

    def test_sell_market_order(self, mock_executor):
        """测试市价卖出"""
        result = mock_executor.sell("600519.SH", 100)
        assert result is mock_executor

    def test_sell_different_quantities(self, mock_executor):
        """测试不同数量卖出"""
        quantities = [1, 10, 100, 1000]
        for qty in quantities:
            result = mock_executor.sell("600519.SH", qty)
            assert result is mock_executor


class TestExecutorGetPositions:
    """获取持仓测试"""

    def test_get_positions_empty(self, mock_executor):
        """测试空持仓"""
        positions = mock_executor.get_positions()
        assert positions == {}
        assert isinstance(positions, dict)

    def test_get_positions_after_trades(self, mock_executor):
        """测试交易后持仓"""
        mock_executor.buy("600519.SH", 100)
        mock_executor.sell("600519.SH", 50)
        positions = mock_executor.get_positions()
        assert isinstance(positions, dict)


class TestExecutorWorkflow:
    """Executor 工作流测试"""

    def test_full_trading_workflow(self):
        """测试完整交易工作流"""
        executor = Executor(broker="paper")
        executor.connect()
        executor.buy("600519.SH", 100)
        executor.sell("600519.SH", 50)
        positions = executor.get_positions()
        
        assert isinstance(positions, dict)

    def test_chained_workflow(self):
        """测试链式工作流"""
        executor = Executor()
        executor.connect().buy("600519.SH", 100).sell("600519.SH", 50)
        positions = executor.get_positions()
        assert isinstance(positions, dict)
    
    def test_workflow_with_submit_order(self):
        """测试使用 submit_order 的工作流"""
        executor = Executor()
        executor.connect()
        buy_result = executor.submit_order("BUY", "600519.SH", 100)
        sell_result = executor.submit_order("SELL", "600519.SH", 50)
        
        assert isinstance(buy_result, dict)
        assert isinstance(sell_result, dict)


class TestExecutorEdgeCases:
    """边界情况测试"""

    def test_buy_zero_quantity(self, mock_executor):
        """测试买入 0 股"""
        result = mock_executor.buy("600519.SH", 0)
        assert result is mock_executor  # 支持链式调用

    def test_sell_zero_quantity(self, mock_executor):
        """测试卖出 0 股"""
        result = mock_executor.sell("600519.SH", 0)
        assert result is mock_executor  # 支持链式调用

    def test_multiple_brokers(self):
        """测试多个经纪商"""
        brokers = ["paper", "binance", "huobi", "ibkr"]
        for broker in brokers:
            executor = Executor(broker=broker)
            assert executor.broker == broker
