"""
监控中心核心类 - 7x24 小时行情监控

提供监控任务管理、行情订阅协调、信号分发功能。

@module: monitor.center
@author: OpenFinAgent Team
@version: 1.0.0
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid

import pandas as pd

try:
    from ..strategy.base import BaseStrategy
except ImportError:
    from strategy.base import BaseStrategy

from .signal_detector import SignalDetector, Signal, SignalType
from .subscription import SubscriptionManager, StockSubscription

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """监控任务状态"""
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class MonitoringTask:
    """
    监控任务数据模型
    
    Attributes:
        id: 任务 ID
        strategy_ids: 策略 ID 列表
        stock_pool_id: 股票池 ID
        status: 任务状态
        created_at: 创建时间
        updated_at: 更新时间
        symbols: 当前监控的股票列表
        signals: 检测到的信号列表
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    strategy_ids: List[str] = field(default_factory=list)
    stock_pool_id: str = ""
    status: TaskStatus = TaskStatus.STOPPED
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    symbols: List[str] = field(default_factory=list)
    signals: List[Signal] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'strategy_ids': self.strategy_ids,
            'stock_pool_id': self.stock_pool_id,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'symbols': self.symbols,
            'signals_count': len(self.signals)
        }


class MonitorCenter:
    """
    监控中心核心类
    
    负责管理多个监控任务，协调行情订阅和信号检测。
    支持 7x24 小时不间断监控，自动重连机制。
    
    Attributes:
        tasks: 监控任务字典
        strategies: 策略实例字典
        subscription_manager: 行情订阅管理器
        signal_detector: 信号检测器
        on_signal_callback: 信号回调函数
    """
    
    def __init__(self):
        """初始化监控中心"""
        self.tasks: Dict[str, MonitoringTask] = {}
        self.strategies: Dict[str, BaseStrategy] = {}
        self.subscription_manager = SubscriptionManager()
        self.signal_detector = SignalDetector()
        self.on_signal_callback: Optional[Callable[[Signal], None]] = None
        self._running = False
        self._monitor_tasks: List[asyncio.Task] = []
        
        logger.info("监控中心初始化完成")
    
    def register_strategy(self, strategy_id: str, strategy: BaseStrategy) -> None:
        """
        注册策略实例
        
        Args:
            strategy_id: 策略 ID
            strategy: 策略实例
            
        Raises:
            ValueError: 当策略 ID 已存在时
        """
        if strategy_id in self.strategies:
            logger.warning(f"策略 ID 已存在：{strategy_id}, 将覆盖")
        
        self.strategies[strategy_id] = strategy
        logger.info(f"策略注册成功：{strategy_id}")
    
    def set_signal_callback(self, callback: Callable[[Signal], None]) -> None:
        """
        设置信号回调函数
        
        Args:
            callback: 信号回调函数，接收 Signal 参数
        """
        self.on_signal_callback = callback
        logger.info("信号回调函数已设置")
    
    async def start_monitoring(
        self,
        strategy_ids: List[str],
        stock_pool_id: str,
        symbols: Optional[List[str]] = None
    ) -> str:
        """
        启动监控任务
        
        Args:
            strategy_ids: 策略 ID 列表
            stock_pool_id: 股票池 ID
            symbols: 股票列表，如果为 None 则从股票池加载
            
        Returns:
            任务 ID
            
        Raises:
            ValueError: 当策略 ID 不存在或参数无效时
        """
        # 验证策略
        for strategy_id in strategy_ids:
            if strategy_id not in self.strategies:
                raise ValueError(f"策略不存在：{strategy_id}")
        
        # 创建监控任务
        task_id = str(uuid.uuid4())
        task = MonitoringTask(
            id=task_id,
            strategy_ids=strategy_ids,
            stock_pool_id=stock_pool_id,
            status=TaskStatus.RUNNING,
            symbols=symbols or []
        )
        
        self.tasks[task_id] = task
        logger.info(f"监控任务启动：{task_id}, 策略：{strategy_ids}, 股票池：{stock_pool_id}")
        
        # 订阅行情
        if symbols:
            await self.subscription_manager.subscribe(symbols)
        
        # 启动监控循环
        monitor_task = asyncio.create_task(self._monitor_loop(task))
        self._monitor_tasks.append(monitor_task)
        
        return task_id
    
    async def stop_monitoring(self, task_id: str) -> bool:
        """
        停止监控任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            是否成功停止
        """
        if task_id not in self.tasks:
            logger.warning(f"任务不存在：{task_id}")
            return False
        
        task = self.tasks[task_id]
        task.status = TaskStatus.STOPPED
        task.updated_at = datetime.now()
        
        # 取消订阅
        await self.subscription_manager.unsubscribe(task.symbols)
        
        logger.info(f"监控任务停止：{task_id}")
        return True
    
    def pause_monitoring(self, task_id: str) -> bool:
        """
        暂停监控任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            是否成功暂停
        """
        if task_id not in self.tasks:
            logger.warning(f"任务不存在：{task_id}")
            return False
        
        task = self.tasks[task_id]
        task.status = TaskStatus.PAUSED
        task.updated_at = datetime.now()
        
        logger.info(f"监控任务暂停：{task_id}")
        return True
    
    def resume_monitoring(self, task_id: str) -> bool:
        """
        恢复监控任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            是否成功恢复
        """
        if task_id not in self.tasks:
            logger.warning(f"任务不存在：{task_id}")
            return False
        
        task = self.tasks[task_id]
        task.status = TaskStatus.RUNNING
        task.updated_at = datetime.now()
        
        logger.info(f"监控任务恢复：{task_id}")
        return True
    
    def get_monitoring_tasks(self) -> List[MonitoringTask]:
        """
        获取所有监控任务
        
        Returns:
            监控任务列表
        """
        return list(self.tasks.values())
    
    def get_task(self, task_id: str) -> Optional[MonitoringTask]:
        """
        获取指定任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            监控任务，不存在则返回 None
        """
        return self.tasks.get(task_id)
    
    async def _monitor_loop(self, task: MonitoringTask) -> None:
        """
        监控循环 - 核心监控逻辑
        
        Args:
            task: 监控任务
        """
        logger.info(f"监控循环启动：{task.id}")
        
        while task.status == TaskStatus.RUNNING:
            try:
                # 获取最新行情数据
                for symbol in task.symbols:
                    data = await self._fetch_market_data(symbol)
                    
                    if data is not None and not data.empty:
                        # 对每个策略检测信号
                        for strategy_id in task.strategy_ids:
                            strategy = self.strategies[strategy_id]
                            signal = self.signal_detector.check_signal(
                                strategy=strategy,
                                symbol=symbol,
                                data=data
                            )
                            
                            if signal:
                                task.signals.append(signal)
                                logger.info(
                                    f"信号检测：{signal.symbol}, "
                                    f"类型：{signal.signal_type.value}, "
                                    f"策略：{strategy_id}"
                                )
                                
                                # 触发回调
                                if self.on_signal_callback:
                                    self.on_signal_callback(signal)
                
                # 等待下一个周期
                await asyncio.sleep(1)  # 1 秒检查一次
                
            except asyncio.CancelledError:
                logger.info(f"监控循环取消：{task.id}")
                break
            except Exception as e:
                logger.error(f"监控循环错误：{task.id}, {e}", exc_info=True)
                task.status = TaskStatus.ERROR
                task.updated_at = datetime.now()
                break
        
        logger.info(f"监控循环结束：{task.id}")
    
    async def _fetch_market_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        获取市场数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            市场数据 DataFrame
        """
        try:
            # 从订阅管理器获取最新 Tick 数据
            tick_data = await self.subscription_manager.get_latest_tick(symbol)
            
            if tick_data:
                # 转换为 DataFrame 格式
                df = pd.DataFrame([tick_data])
                return df
            
            return None
            
        except Exception as e:
            logger.error(f"获取市场数据失败：{symbol}, {e}")
            return None
    
    def cleanup(self) -> None:
        """清理资源"""
        logger.info("监控中心清理资源")
        
        # 取消所有监控任务
        for monitor_task in self._monitor_tasks:
            if not monitor_task.done():
                monitor_task.cancel()
        
        self._running = False
        logger.info("监控中心清理完成")
    
    def __del__(self):
        """析构函数"""
        self.cleanup()
