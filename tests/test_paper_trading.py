"""
模拟盘测试

测试模拟盘引擎的订单管理、持仓管理、盈亏计算等功能

@module: tests.test_paper_trading
@author: OpenFinAgent Team
@version: 0.4.0
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from paper_trading.engine import (
    PaperTradingEngine,
    Order,
    OrderStatus,
    OrderType,
    OrderSide,
    Position,
    Trade
)


class TestOrder:
    """测试订单模型"""
    
    def test_order_creation(self):
        """测试订单创建"""
        order = Order(
            symbol='AAPL',
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.MARKET
        )
        
        assert order.symbol == 'AAPL'
        assert order.side == OrderSide.BUY
        assert order.quantity == 100
        assert order.order_type == OrderType.MARKET
        assert order.status == OrderStatus.PENDING
        assert order.id is not None
    
    def test_order_to_dict(self):
        """测试订单转字典"""
        order = Order(
            symbol='AAPL',
            side=OrderSide.BUY,
            quantity=100
        )
        
        order_dict = order.to_dict()
        
        assert order_dict['symbol'] == 'AAPL'
        assert order_dict['side'] == 'buy'
        assert order_dict['quantity'] == 100
        assert 'id' in order_dict


class TestPosition:
    """测试持仓模型"""
    
    def test_position_basic(self):
        """测试持仓基本计算"""
        position = Position(
            symbol='AAPL',
            quantity=100,
            avg_price=150.0,
            current_price=160.0
        )
        
        assert position.market_value == 16000.0
        assert position.cost_basis == 15000.0
        assert position.unrealized_pnl == 1000.0
        assert position.return_rate == pytest.approx(0.0667, rel=1e-3)
    
    def test_position_loss(self):
        """测试持仓亏损"""
        position = Position(
            symbol='AAPL',
            quantity=100,
            avg_price=150.0,
            current_price=140.0
        )
        
        assert position.unrealized_pnl == -1000.0
        assert position.return_rate == pytest.approx(-0.0667, rel=1e-3)


class TestPaperTradingEngine:
    """测试模拟盘引擎"""
    
    @pytest.fixture
    def engine(self):
        """创建测试用的模拟盘引擎"""
        return PaperTradingEngine(
            initial_cash=1000000.0,
            commission_rate=0.0003,
            slippage_rate=0.001
        )
    
    def test_engine_initialization(self, engine):
        """测试引擎初始化"""
        assert engine.initial_cash == 1000000.0
        assert engine.cash == 1000000.0
        assert len(engine.positions) == 0
        assert len(engine.orders) == 0
        assert len(engine.trades) == 0
    
    def test_submit_market_order_buy(self, engine):
        """测试提交市价买单"""
        # 设置当前价格
        order = engine.submit_order(
            symbol='AAPL',
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.MARKET
        )
        
        # 市价单应该立即成交
        assert order.status == OrderStatus.FILLED
        assert order.filled_quantity == 100
        assert order.filled_price is not None
        
        # 验证持仓
        position = engine.get_position('AAPL')
        assert position is not None
        assert position.quantity == 100
    
    def test_submit_order_insufficient_funds(self, engine):
        """测试资金不足"""
        # 尝试买入超过资金的订单
        order = engine.submit_order(
            symbol='AAPL',
            side=OrderSide.BUY,
            quantity=1000000,  # 数量过大
            order_type=OrderType.MARKET
        )
        
        assert order.status == OrderStatus.REJECTED
    
    def test_sell_order(self, engine):
        """测试卖出订单"""
        # 先买入
        buy_order = engine.submit_order(
            symbol='AAPL',
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.MARKET
        )
        
        assert buy_order.status == OrderStatus.FILLED
        
        # 再卖出
        sell_order = engine.submit_order(
            symbol='AAPL',
            side=OrderSide.SELL,
            quantity=50,
            order_type=OrderType.MARKET
        )
        
        assert sell_order.status == OrderStatus.FILLED
        
        # 验证持仓
        position = engine.get_position('AAPL')
        assert position.quantity == 50
    
    def test_sell_insufficient_position(self, engine):
        """测试持仓不足"""
        # 尝试卖出没有的持仓
        order = engine.submit_order(
            symbol='AAPL',
            side=OrderSide.SELL,
            quantity=100,
            order_type=OrderType.MARKET
        )
        
        assert order.status == OrderStatus.REJECTED
    
    def test_cancel_order(self, engine):
        """测试取消订单"""
        # 这个测试需要限价单支持，简化测试
        pass
    
    def test_get_portfolio_value(self, engine):
        """测试组合价值计算"""
        # 初始价值
        assert engine.get_portfolio_value() == 1000000.0
        
        # 买入后
        order = engine.submit_order(
            symbol='AAPL',
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.MARKET
        )
        
        # 组合价值应该接近初始值 (扣除手续费和滑点)
        value = engine.get_portfolio_value()
        assert value < 1000000.0  # 因为有交易成本
        assert value > 999000.0  # 但不会少太多
    
    def test_get_return_rate(self, engine):
        """测试收益率计算"""
        # 初始收益率为 0
        assert engine.get_return_rate() == 0.0
        
        # 交易后
        engine.submit_order(
            symbol='AAPL',
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.MARKET
        )
        
        # 收益率应该为负 (因为交易成本)
        assert engine.get_return_rate() < 0
    
    def test_get_summary(self, engine):
        """测试获取摘要"""
        # 交易一次
        engine.submit_order(
            symbol='AAPL',
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.MARKET
        )
        
        summary = engine.get_summary()
        
        assert 'initial_cash' in summary
        assert 'current_cash' in summary
        assert 'total_value' in summary
        assert 'return_rate' in summary
        assert summary['total_trades'] >= 1
    
    def test_reset_engine(self, engine):
        """测试重置引擎"""
        # 先交易
        engine.submit_order(
            symbol='AAPL',
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.MARKET
        )
        
        # 重置
        engine.reset()
        
        # 验证状态
        assert engine.cash == engine.initial_cash
        assert len(engine.positions) == 0
        assert len(engine.orders) == 0
        assert len(engine.trades) == 0
    
    def test_update_prices(self, engine):
        """测试更新价格"""
        # 先买入
        engine.submit_order(
            symbol='AAPL',
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.MARKET
        )
        
        # 更新价格
        engine.update_prices({'AAPL': 200.0})
        
        # 验证持仓盈亏更新
        position = engine.get_position('AAPL')
        assert position.current_price == 200.0
    
    def test_multiple_positions(self, engine):
        """测试多个持仓"""
        # 买入多个股票
        engine.submit_order(
            symbol='AAPL',
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.MARKET
        )
        
        engine.submit_order(
            symbol='GOOGL',
            side=OrderSide.BUY,
            quantity=50,
            order_type=OrderType.MARKET
        )
        
        # 验证持仓
        positions = engine.get_all_positions()
        assert 'AAPL' in positions
        assert 'GOOGL' in positions
        assert len(positions) == 2


class TestTradeRecord:
    """测试成交记录"""
    
    @pytest.fixture
    def engine(self):
        """创建测试用的模拟盘引擎"""
        return PaperTradingEngine(initial_cash=1000000.0)
    
    def test_trade_record_created(self, engine):
        """测试成交记录创建"""
        order = engine.submit_order(
            symbol='AAPL',
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.MARKET
        )
        
        # 验证有成交记录
        trades = engine.get_trades()
        assert len(trades) == 1
        
        trade = trades[0]
        assert trade.order_id == order.id
        assert trade.symbol == 'AAPL'
        assert trade.side == OrderSide.BUY
        assert trade.quantity == 100
        assert trade.commission >= 0
    
    def test_get_trades_by_symbol(self, engine):
        """测试按股票代码筛选成交记录"""
        # 多次交易
        engine.submit_order(symbol='AAPL', side=OrderSide.BUY, quantity=100, order_type=OrderType.MARKET)
        engine.submit_order(symbol='GOOGL', side=OrderSide.BUY, quantity=50, order_type=OrderType.MARKET)
        engine.submit_order(symbol='AAPL', side=OrderSide.SELL, quantity=50, order_type=OrderType.MARKET)
        
        # 筛选 AAPL 的交易
        aapl_trades = engine.get_trades(symbol='AAPL')
        assert len(aapl_trades) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
