"""
模拟盘引擎

提供模拟交易功能，使用实时数据但不实际下单

@module: paper_trading.engine
@author: OpenFinAgent Team
@version: 0.4.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid
import logging

import pandas as pd

logger = logging.getLogger(__name__)


class OrderStatus(Enum):
    """订单状态"""
    PENDING = "pending"  # 待成交
    FILLED = "filled"  # 已成交
    PARTIALLY_FILLED = "partially_filled"  # 部分成交
    CANCELLED = "cancelled"  # 已取消
    REJECTED = "rejected"  # 已拒绝


class OrderType(Enum):
    """订单类型"""
    MARKET = "market"  # 市价单
    LIMIT = "limit"  # 限价单
    STOP = "stop"  # 止损单
    STOP_LIMIT = "stop_limit"  # 止损限价单


class OrderSide(Enum):
    """订单方向"""
    BUY = "buy"  # 买入
    SELL = "sell"  # 卖出


@dataclass
class Order:
    """
    订单数据模型
    
    Attributes:
        id: 订单 ID
        symbol: 股票代码
        side: 买卖方向
        quantity: 数量
        price: 价格 (限价单)
        order_type: 订单类型
        status: 订单状态
        filled_price: 成交均价
        filled_quantity: 成交数量
        created_at: 创建时间
        filled_at: 成交时间
        cancelled_at: 取消时间
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = ""
    side: OrderSide = OrderSide.BUY
    quantity: float = 0
    price: Optional[float] = None
    order_type: OrderType = OrderType.MARKET
    status: OrderStatus = OrderStatus.PENDING
    filled_price: Optional[float] = None
    filled_quantity: float = 0
    created_at: datetime = field(default_factory=datetime.now)
    filled_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side.value,
            'quantity': self.quantity,
            'price': self.price,
            'order_type': self.order_type.value,
            'status': self.status.value,
            'filled_price': self.filled_price,
            'filled_quantity': self.filled_quantity,
            'created_at': self.created_at.isoformat(),
            'filled_at': self.filled_at.isoformat() if self.filled_at else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None
        }


@dataclass
class Position:
    """
    持仓数据模型
    
    Attributes:
        symbol: 股票代码
        quantity: 持仓数量
        avg_price: 平均成本价
        current_price: 当前价格
        unrealized_pnl: 浮动盈亏
        realized_pnl: 已实现盈亏
    """
    symbol: str = ""
    quantity: float = 0
    avg_price: float = 0
    current_price: float = 0
    unrealized_pnl: float = 0
    realized_pnl: float = 0
    
    @property
    def market_value(self) -> float:
        """市值"""
        return self.quantity * self.current_price
    
    @property
    def cost_basis(self) -> float:
        """成本"""
        return self.quantity * self.avg_price
    
    @property
    def return_rate(self) -> float:
        """收益率"""
        if self.cost_basis == 0:
            return 0
        return (self.market_value - self.cost_basis) / self.cost_basis
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'symbol': self.symbol,
            'quantity': self.quantity,
            'avg_price': self.avg_price,
            'current_price': self.current_price,
            'market_value': self.market_value,
            'cost_basis': self.cost_basis,
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl,
            'return_rate': self.return_rate
        }


@dataclass
class Trade:
    """
    成交记录
    
    Attributes:
        id: 成交 ID
        order_id: 关联订单 ID
        symbol: 股票代码
        side: 买卖方向
        price: 成交价格
        quantity: 成交数量
        commission: 手续费
        timestamp: 成交时间
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str = ""
    symbol: str = ""
    side: OrderSide = OrderSide.BUY
    price: float = 0
    quantity: float = 0
    commission: float = 0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'symbol': self.symbol,
            'side': self.side.value,
            'price': self.price,
            'quantity': self.quantity,
            'commission': self.commission,
            'timestamp': self.timestamp.isoformat()
        }


class PaperTradingEngine:
    """
    模拟盘引擎
    
    提供模拟交易功能，包括：
    - 订单管理
    - 持仓管理
    - 资金管理
    - 盈亏计算
    - 交易记录
    
    Attributes:
        initial_cash: 初始资金
        cash: 当前现金
        commission_rate: 手续费率
        slippage_rate: 滑点率
        positions: 持仓字典
        orders: 订单列表
        trades: 成交记录列表
    """
    
    def __init__(
        self,
        initial_cash: float = 1000000.0,
        commission_rate: float = 0.0003,
        slippage_rate: float = 0.001,
        data_feed: Optional[Any] = None
    ):
        """
        初始化模拟盘引擎
        
        Args:
            initial_cash: 初始资金 (默认 100 万)
            commission_rate: 手续费率 (默认万分之三)
            slippage_rate: 滑点率 (默认 0.1%)
            data_feed: 数据源 (用于获取实时价格)
        """
        if initial_cash <= 0:
            raise ValueError("初始资金必须大于 0")
        if not 0 <= commission_rate <= 1:
            raise ValueError("手续费率必须在 0-1 之间")
        if not 0 <= slippage_rate <= 1:
            raise ValueError("滑点率必须在 0-1 之间")
        
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        self.data_feed = data_feed
        
        # 持仓管理
        self.positions: Dict[str, Position] = {}
        
        # 订单管理
        self.orders: List[Order] = []
        self.pending_orders: List[Order] = []
        
        # 成交记录
        self.trades: List[Trade] = []
        
        # 状态
        self.running = False
        self.paused = False
        
        # 回调函数
        self.on_order_callback: Optional[Callable] = None
        self.on_trade_callback: Optional[Callable] = None
        
        logger.info(
            f"模拟盘引擎初始化完成，初始资金：{initial_cash:,.2f}, "
            f"手续费率：{commission_rate:.4f}, 滑点率：{slippage_rate:.4f}"
        )
    
    def submit_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        order_type: OrderType = OrderType.MARKET,
        price: Optional[float] = None
    ) -> Order:
        """
        提交订单
        
        Args:
            symbol: 股票代码
            side: 买卖方向
            quantity: 数量
            order_type: 订单类型
            price: 价格 (限价单需要)
        
        Returns:
            订单对象
        
        Raises:
            ValueError: 当参数不合法或资金/持仓不足时
        """
        # 参数验证
        if quantity <= 0:
            raise ValueError("数量必须大于 0")
        
        if order_type == OrderType.LIMIT and price is None:
            raise ValueError("限价单必须指定价格")
        
        # 创建订单
        order = Order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            price=price
        )
        
        # 预检查
        if not self._validate_order(order):
            order.status = OrderStatus.REJECTED
            self.orders.append(order)
            logger.warning(f"订单被拒绝：{order.symbol} {order.side.value} {order.quantity}")
            return order
        
        # 添加订单
        self.orders.append(order)
        
        if order.order_type == OrderType.MARKET:
            # 市价单立即执行
            self._execute_order(order)
        else:
            # 限价单加入待成交队列
            self.pending_orders.append(order)
            logger.info(f"订单已提交：{order.id}, {order.symbol} {order.side.value} {order.quantity} @ {order.price}")
        
        # 回调
        if self.on_order_callback:
            self.on_order_callback(order)
        
        return order
    
    def cancel_order(self, order_id: str) -> bool:
        """
        取消订单
        
        Args:
            order_id: 订单 ID
        
        Returns:
            是否取消成功
        """
        # 查找订单
        order = self._get_order(order_id)
        
        if not order:
            logger.warning(f"订单不存在：{order_id}")
            return False
        
        if order.status not in [OrderStatus.PENDING]:
            logger.warning(f"订单不能取消：{order_id}, 状态={order.status.value}")
            return False
        
        # 取消订单
        order.status = OrderStatus.CANCELLED
        order.cancelled_at = datetime.now()
        
        # 从待成交队列移除
        if order in self.pending_orders:
            self.pending_orders.remove(order)
        
        logger.info(f"订单已取消：{order_id}")
        
        return True
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """
        获取持仓
        
        Args:
            symbol: 股票代码
        
        Returns:
            持仓对象或 None
        """
        return self.positions.get(symbol)
    
    def get_all_positions(self) -> Dict[str, Position]:
        """
        获取所有持仓
        
        Returns:
            持仓字典
        """
        return self.positions
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """
        获取订单
        
        Args:
            order_id: 订单 ID
        
        Returns:
            订单对象或 None
        """
        return self._get_order(order_id)
    
    def get_orders(self, symbol: Optional[str] = None, status: Optional[OrderStatus] = None) -> List[Order]:
        """
        获取订单列表
        
        Args:
            symbol: 股票代码 (可选)
            status: 订单状态 (可选)
        
        Returns:
            订单列表
        """
        orders = self.orders
        
        if symbol:
            orders = [o for o in orders if o.symbol == symbol]
        
        if status:
            orders = [o for o in orders if o.status == status]
        
        return orders
    
    def get_trades(self, symbol: Optional[str] = None) -> List[Trade]:
        """
        获取成交记录
        
        Args:
            symbol: 股票代码 (可选)
        
        Returns:
            成交记录列表
        """
        trades = self.trades
        
        if symbol:
            trades = [t for t in trades if t.symbol == symbol]
        
        return trades
    
    def get_portfolio_value(self) -> float:
        """
        获取组合总价值
        
        Returns:
            组合总价值 (现金 + 持仓市值)
        """
        position_value = sum(pos.market_value for pos in self.positions.values())
        return self.cash + position_value
    
    def get_return_rate(self) -> float:
        """
        获取收益率
        
        Returns:
            收益率
        """
        current_value = self.get_portfolio_value()
        return (current_value - self.initial_cash) / self.initial_cash
    
    def update_prices(self, prices: Dict[str, float]) -> None:
        """
        更新价格 (用于计算持仓盈亏)
        
        Args:
            prices: 价格字典 {symbol: price}
        """
        for symbol, price in prices.items():
            if symbol in self.positions:
                position = self.positions[symbol]
                position.current_price = price
                position.unrealized_pnl = (price - position.avg_price) * position.quantity
        
        # 检查限价单是否可以成交
        self._check_pending_orders(prices)
    
    def start(self) -> None:
        """启动模拟盘"""
        self.running = True
        self.paused = False
        logger.info("模拟盘已启动")
    
    def pause(self) -> None:
        """暂停模拟盘"""
        self.paused = True
        logger.info("模拟盘已暂停")
    
    def resume(self) -> None:
        """恢复模拟盘"""
        self.paused = False
        logger.info("模拟盘已恢复")
    
    def stop(self) -> None:
        """停止模拟盘"""
        self.running = False
        self.paused = False
        logger.info("模拟盘已停止")
    
    def reset(self) -> None:
        """重置模拟盘到初始状态"""
        self.cash = self.initial_cash
        self.positions.clear()
        self.orders.clear()
        self.pending_orders.clear()
        self.trades.clear()
        self.running = False
        self.paused = False
        
        logger.info("模拟盘已重置")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        获取模拟盘摘要
        
        Returns:
            摘要字典
        """
        total_value = self.get_portfolio_value()
        return_rate = self.get_return_rate()
        
        total_unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
        total_realized_pnl = sum(pos.realized_pnl for pos in self.positions.values())
        
        return {
            'initial_cash': self.initial_cash,
            'current_cash': self.cash,
            'total_value': total_value,
            'return_rate': return_rate,
            'return_rate_pct': f"{return_rate * 100:.2f}%",
            'position_count': len(self.positions),
            'total_unrealized_pnl': total_unrealized_pnl,
            'total_realized_pnl': total_realized_pnl,
            'total_trades': len(self.trades),
            'total_orders': len(self.orders),
            'pending_orders': len(self.pending_orders)
        }
    
    def _validate_order(self, order: Order) -> bool:
        """
        验证订单
        
        Args:
            order: 订单对象
        
        Returns:
            是否有效
        """
        # 检查资金是否充足 (买入)
        if order.side == OrderSide.BUY:
            estimated_cost = self._estimate_cost(order)
            
            if estimated_cost > self.cash:
                logger.warning(f"资金不足：需要 {estimated_cost:,.2f}, 可用 {self.cash:,.2f}")
                return False
        
        # 检查持仓是否充足 (卖出)
        elif order.side == OrderSide.SELL:
            position = self.positions.get(order.symbol)
            
            if not position or position.quantity < order.quantity:
                available = position.quantity if position else 0
                logger.warning(f"持仓不足：需要 {order.quantity}, 可用 {available}")
                return False
        
        return True
    
    def _estimate_cost(self, order: Order) -> float:
        """
        估算订单成本
        
        Args:
            order: 订单对象
        
        Returns:
            估算成本
        """
        # 获取当前价格
        price = order.price or self._get_current_price(order.symbol)
        
        if price is None:
            return float('inf')
        
        # 计算总成本 (含手续费和滑点)
        base_cost = price * order.quantity
        slippage = base_cost * self.slippage_rate
        commission = base_cost * self.commission_rate
        
        return base_cost + slippage + commission
    
    def _get_current_price(self, symbol: str) -> Optional[float]:
        """
        获取当前价格
        
        Args:
            symbol: 股票代码
        
        Returns:
            当前价格或 None
        """
        # 从持仓获取
        if symbol in self.positions:
            return self.positions[symbol].current_price
        
        # 从数据源获取
        if self.data_feed and hasattr(self.data_feed, 'get_realtime'):
            try:
                data = self.data_feed.get_realtime(symbol)
                return data.get('price')
            except Exception:
                pass
        
        return None
    
    def _execute_order(self, order: Order) -> None:
        """
        执行订单
        
        Args:
            order: 订单对象
        """
        # 获取当前价格
        current_price = self._get_current_price(order.symbol)
        
        if current_price is None:
            logger.error(f"无法获取价格：{order.symbol}")
            order.status = OrderStatus.REJECTED
            return
        
        # 应用滑点
        if order.side == OrderSide.BUY:
            fill_price = current_price * (1 + self.slippage_rate)
        else:
            fill_price = current_price * (1 - self.slippage_rate)
        
        # 限价单检查
        if order.order_type == OrderType.LIMIT:
            if order.side == OrderSide.BUY and fill_price > order.price:
                logger.info(f"限价单未成交：买入价 {fill_price:.2f} > 限价 {order.price:.2f}")
                return
            elif order.side == OrderSide.SELL and fill_price < order.price:
                logger.info(f"限价单未成交：卖出价 {fill_price:.2f} < 限价 {order.price:.2f}")
                return
        
        # 计算手续费
        commission = fill_price * order.quantity * self.commission_rate
        
        # 执行交易
        if order.side == OrderSide.BUY:
            total_cost = fill_price * order.quantity + commission
            
            if total_cost > self.cash:
                logger.warning(f"资金不足，订单部分成交或拒绝")
                order.status = OrderStatus.REJECTED
                return
            
            # 更新资金
            self.cash -= total_cost
            
            # 更新持仓
            if order.symbol not in self.positions:
                self.positions[order.symbol] = Position(symbol=order.symbol)
            
            position = self.positions[order.symbol]
            
            # 计算新的平均成本
            old_cost = position.avg_price * position.quantity
            new_cost = fill_price * order.quantity
            total_quantity = position.quantity + order.quantity
            
            position.quantity = total_quantity
            position.avg_price = (old_cost + new_cost) / total_quantity if total_quantity > 0 else 0
            position.current_price = fill_price
            
        else:  # SELL
            position = self.positions.get(order.symbol)
            
            if not position:
                order.status = OrderStatus.REJECTED
                return
            
            # 计算已实现盈亏
            realized_pnl = (fill_price - position.avg_price) * order.quantity
            position.realized_pnl += realized_pnl
            
            # 更新持仓
            position.quantity -= order.quantity
            
            # 更新资金
            revenue = fill_price * order.quantity - commission
            self.cash += revenue
            
            # 如果持仓为 0，移除
            if position.quantity <= 0:
                del self.positions[order.symbol]
        
        # 更新订单状态
        order.status = OrderStatus.FILLED
        order.filled_price = fill_price
        order.filled_quantity = order.quantity
        order.filled_at = datetime.now()
        
        # 创建成交记录
        trade = Trade(
            order_id=order.id,
            symbol=order.symbol,
            side=order.side,
            price=fill_price,
            quantity=order.quantity,
            commission=commission
        )
        
        self.trades.append(trade)
        
        logger.info(
            f"订单成交：{order.id}, {order.symbol} {order.side.value} "
            f"{order.quantity} @ {fill_price:.2f}, 手续费：{commission:.2f}"
        )
        
        # 回调
        if self.on_trade_callback:
            self.on_trade_callback(trade)
    
    def _check_pending_orders(self, prices: Dict[str, float]) -> None:
        """
        检查待成交订单
        
        Args:
            prices: 价格字典
        """
        orders_to_remove = []
        
        for order in self.pending_orders:
            if order.symbol not in prices:
                continue
            
            current_price = prices[order.symbol]
            
            # 检查是否可以成交
            should_fill = False
            
            if order.order_type == OrderType.LIMIT:
                if order.side == OrderSide.BUY and current_price <= order.price:
                    should_fill = True
                elif order.side == OrderSide.SELL and current_price >= order.price:
                    should_fill = True
            
            if should_fill:
                # 执行订单
                order.price = current_price  # 更新为市场价
                self._execute_order(order)
                orders_to_remove.append(order)
        
        # 移除已成交的订单
        for order in orders_to_remove:
            if order in self.pending_orders:
                self.pending_orders.remove(order)
    
    def _get_order(self, order_id: str) -> Optional[Order]:
        """根据 ID 获取订单"""
        for order in self.orders:
            if order.id == order_id:
                return order
        return None
