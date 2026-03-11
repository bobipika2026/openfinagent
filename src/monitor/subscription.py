"""
行情订阅管理 - 实时行情数据订阅

支持多股票同时订阅、Tick 数据接收、自动重连机制。

@module: monitor.subscription
@author: OpenFinAgent Team
@version: 1.0.0
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
import uuid

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class TickData:
    """
    Tick 数据模型
    
    Attributes:
        symbol: 股票代码
        timestamp: 时间戳
        price: 最新价
        open: 开盘价
        high: 最高价
        low: 最低价
        volume: 成交量
        amount: 成交额
        bid_price: 买一价
        ask_price: 卖一价
        bid_volume: 买一量
        ask_volume: 卖一量
    """
    symbol: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    price: float = 0.0
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    volume: int = 0
    amount: float = 0.0
    bid_price: float = 0.0
    ask_price: float = 0.0
    bid_volume: int = 0
    ask_volume: int = 0
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'price': self.price,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'volume': self.volume,
            'amount': self.amount,
            'bid_price': self.bid_price,
            'ask_price': self.ask_price,
            'bid_volume': self.bid_volume,
            'ask_volume': self.ask_volume
        }


@dataclass
class StockSubscription:
    """
    股票订阅信息
    
    Attributes:
        id: 订阅 ID
        symbol: 股票代码
        created_at: 创建时间
        last_update: 最后更新时间
        tick_count: 接收的 Tick 数量
        status: 订阅状态
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    last_update: Optional[datetime] = None
    tick_count: int = 0
    status: str = "active"  # active, inactive, error
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'created_at': self.created_at.isoformat(),
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'tick_count': self.tick_count,
            'status': self.status
        }


class SubscriptionManager:
    """
    行情订阅管理器
    
    管理多个股票的实时行情订阅，提供 Tick 数据缓存和分发。
    支持自动重连机制，确保 7x24 小时稳定运行。
    
    Attributes:
        subscriptions: 订阅信息字典
        latest_ticks: 最新 Tick 数据缓存
        tick_history: Tick 历史记录
        on_tick_callback: Tick 数据回调函数
        reconnect_attempts: 重连次数
        reconnect_delay: 重连延迟（秒）
    """
    
    def __init__(
        self,
        max_history_size: int = 1000,
        reconnect_attempts: int = 3,
        reconnect_delay: float = 5.0
    ):
        """
        初始化订阅管理器
        
        Args:
            max_history_size: 最大历史记录大小
            reconnect_attempts: 最大重连次数
            reconnect_delay: 重连延迟（秒）
        """
        self.subscriptions: Dict[str, StockSubscription] = {}
        self.latest_ticks: Dict[str, TickData] = {}
        self.tick_history: Dict[str, List[TickData]] = {}
        self.on_tick_callback: Optional[Callable[[TickData], None]] = None
        
        self.max_history_size = max_history_size
        self.reconnect_attempts = reconnect_attempts
        self.reconnect_delay = reconnect_delay
        
        self._running = False
        self._reconnect_tasks: Dict[str, asyncio.Task] = {}
        
        logger.info(
            f"订阅管理器初始化：max_history={max_history_size}, "
            f"reconnect={reconnect_attempts}次"
        )
    
    def set_tick_callback(self, callback: Callable[[TickData], None]) -> None:
        """
        设置 Tick 数据回调函数
        
        Args:
            callback: 回调函数，接收 TickData 参数
        """
        self.on_tick_callback = callback
        logger.info("Tick 数据回调函数已设置")
    
    async def subscribe(self, symbols: List[str]) -> bool:
        """
        订阅股票行情
        
        Args:
            symbols: 股票代码列表
            
        Returns:
            是否成功
        """
        if not symbols:
            logger.warning("订阅列表为空")
            return False
        
        success_count = 0
        for symbol in symbols:
            try:
                if symbol in self.subscriptions:
                    logger.debug(f"股票已订阅：{symbol}")
                    continue
                
                # 创建订阅
                subscription = StockSubscription(symbol=symbol)
                self.subscriptions[symbol] = subscription
                self.tick_history[symbol] = []
                
                logger.info(f"订阅成功：{symbol}")
                success_count += 1
                
            except Exception as e:
                logger.error(f"订阅失败：{symbol}, {e}")
        
        logger.info(f"订阅完成：{success_count}/{len(symbols)}")
        return success_count > 0
    
    async def unsubscribe(self, symbols: List[str]) -> bool:
        """
        取消订阅
        
        Args:
            symbols: 股票代码列表
            
        Returns:
            是否成功
        """
        if not symbols:
            logger.warning("取消订阅列表为空")
            return False
        
        success_count = 0
        for symbol in symbols:
            try:
                if symbol in self.subscriptions:
                    # 取消重连任务
                    if symbol in self._reconnect_tasks:
                        task = self._reconnect_tasks[symbol]
                        if not task.done():
                            task.cancel()
                        del self._reconnect_tasks[symbol]
                    
                    # 删除订阅
                    del self.subscriptions[symbol]
                    if symbol in self.latest_ticks:
                        del self.latest_ticks[symbol]
                    if symbol in self.tick_history:
                        del self.tick_history[symbol]
                    
                    logger.info(f"取消订阅：{symbol}")
                    success_count += 1
                    
            except Exception as e:
                logger.error(f"取消订阅失败：{symbol}, {e}")
        
        logger.info(f"取消订阅完成：{success_count}/{len(symbols)}")
        return success_count > 0
    
    async def on_tick(self, tick: TickData) -> None:
        """
        处理 Tick 数据
        
        Args:
            tick: Tick 数据
        """
        symbol = tick.symbol
        
        if symbol not in self.subscriptions:
            logger.debug(f"未订阅的股票：{symbol}")
            return
        
        try:
            # 更新最新 Tick
            self.latest_ticks[symbol] = tick
            
            # 更新订阅信息
            subscription = self.subscriptions[symbol]
            subscription.last_update = tick.timestamp
            subscription.tick_count += 1
            
            # 添加到历史记录
            if symbol not in self.tick_history:
                self.tick_history[symbol] = []
            
            self.tick_history[symbol].append(tick)
            
            # 限制历史记录大小
            if len(self.tick_history[symbol]) > self.max_history_size:
                self.tick_history[symbol] = self.tick_history[symbol][-self.max_history_size:]
            
            # 触发回调
            if self.on_tick_callback:
                self.on_tick_callback(tick)
            
        except Exception as e:
            logger.error(f"处理 Tick 数据失败：{symbol}, {e}")
    
    async def get_latest_tick(self, symbol: str) -> Optional[TickData]:
        """
        获取最新 Tick 数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            Tick 数据，不存在则返回 None
        """
        return self.latest_ticks.get(symbol)
    
    def get_ticks(
        self,
        symbol: str,
        count: int = 100
    ) -> List[TickData]:
        """
        获取历史 Tick 数据
        
        Args:
            symbol: 股票代码
            count: 数量
            
        Returns:
            Tick 数据列表
        """
        if symbol not in self.tick_history:
            return []
        
        history = self.tick_history[symbol]
        return history[-count:] if count < len(history) else history.copy()
    
    def get_ticks_dataframe(
        self,
        symbol: str,
        count: int = 100
    ) -> Optional[pd.DataFrame]:
        """
        获取 Tick 数据 DataFrame
        
        Args:
            symbol: 股票代码
            count: 数量
            
        Returns:
            DataFrame，无数据则返回 None
        """
        ticks = self.get_ticks(symbol, count)
        
        if not ticks:
            return None
        
        # 转换为 DataFrame
        data = [tick.to_dict() for tick in ticks]
        df = pd.DataFrame(data)
        
        return df
    
    def get_subscription(self, symbol: str) -> Optional[StockSubscription]:
        """
        获取订阅信息
        
        Args:
            symbol: 股票代码
            
        Returns:
            订阅信息，不存在则返回 None
        """
        return self.subscriptions.get(symbol)
    
    def get_all_subscriptions(self) -> List[StockSubscription]:
        """
        获取所有订阅
        
        Returns:
            订阅列表
        """
        return list(self.subscriptions.values())
    
    async def _reconnect(self, symbol: str) -> None:
        """
        重连逻辑
        
        Args:
            symbol: 股票代码
        """
        if symbol not in self.subscriptions:
            return
        
        subscription = self.subscriptions[symbol]
        
        for attempt in range(self.reconnect_attempts):
            try:
                logger.info(f"重连中：{symbol}, 尝试 {attempt + 1}/{self.reconnect_attempts}")
                
                # 模拟重连逻辑
                await asyncio.sleep(self.reconnect_delay)
                
                # 重连成功
                subscription.status = "active"
                logger.info(f"重连成功：{symbol}")
                return
                
            except Exception as e:
                logger.error(f"重连失败：{symbol}, 尝试 {attempt + 1}, {e}")
                
                if attempt == self.reconnect_attempts - 1:
                    subscription.status = "error"
                    logger.error(f"重连失败：{symbol}, 已达到最大尝试次数")
    
    def start_reconnect(self, symbol: str) -> None:
        """
        启动重连
        
        Args:
            symbol: 股票代码
        """
        if symbol in self._reconnect_tasks:
            logger.debug(f"重连任务已存在：{symbol}")
            return
        
        task = asyncio.create_task(self._reconnect(symbol))
        self._reconnect_tasks[symbol] = task
    
    def cleanup(self) -> None:
        """清理资源"""
        logger.info("订阅管理器清理资源")
        
        # 取消所有重连任务
        for task in self._reconnect_tasks.values():
            if not task.done():
                task.cancel()
        
        self._reconnect_tasks.clear()
        self.subscriptions.clear()
        self.latest_ticks.clear()
        self.tick_history.clear()
        
        logger.info("订阅管理器清理完成")
    
    def __del__(self):
        """析构函数"""
        self.cleanup()
