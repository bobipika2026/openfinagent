"""
策略基类 - 所有策略的父类

@module: strategy.base
@author: OpenFinAgent Team
@version: 2.0.0
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
import numpy as np
import logging

# 配置日志
logger = logging.getLogger(__name__)


class BaseStrategy(ABC):
    """策略基类 - 定义所有策略必须实现的接口"""

    def __init__(
        self,
        name: str = "Unnamed Strategy",
        initial_capital: float = 100000.0,
        commission_rate: float = 0.0003,
        slippage: float = 0.001
    ):
        """
        初始化策略

        Args:
            name: 策略名称
            initial_capital: 初始资金 (默认 10 万)
            commission_rate: 手续费率 (默认万分之三)
            slippage: 滑点 (默认 0.1%)

        Raises:
            ValueError: 当初始资金或费率参数不合法时
        """
        if initial_capital <= 0:
            raise ValueError(f"初始资金必须大于 0，当前值：{initial_capital}")
        if not 0 <= commission_rate <= 1:
            raise ValueError(f"手续费率必须在 0-1 之间，当前值：{commission_rate}")
        if not 0 <= slippage <= 1:
            raise ValueError(f"滑点必须在 0-1 之间，当前值：{slippage}")

        self.name = name
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage = slippage

        # 状态变量
        self.positions: Dict[str, Any] = {}  # 持仓
        self.cash: float = initial_capital  # 现金
        self.trades: List[Dict[str, Any]] = []  # 交易记录

        logger.info(f"策略初始化：{name}, 初始资金：{initial_capital:,.2f}")

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成交易信号

        Args:
            data: 市场数据 DataFrame，必须包含 'close' 列

        Returns:
            信号 Series (1=买入，-1=卖出，0=持有)

        Raises:
            ValueError: 当数据格式不合法时
        """
        pass

    @abstractmethod
    def on_bar(self, data: pd.DataFrame, index: int) -> Optional[Dict[str, Any]]:
        """
        每根 K 线回调 - 策略核心逻辑

        Args:
            data: 市场数据 DataFrame
            index: 当前 K 线索引

        Returns:
            交易指令字典，包含 action/price/shares/timestamp，无信号时返回 None
        """
        pass

    def calculate_position_size(self, price: float, signal: int) -> int:
        """
        计算仓位大小

        Args:
            price: 当前价格
            signal: 交易信号 (1=买入，-1=卖出)

        Returns:
            交易数量 (A 股 100 股一手)

        Raises:
            ValueError: 当价格不合法时
        """
        if signal == 0:
            return 0

        if price <= 0:
            logger.warning(f"无效价格：{price}")
            return 0

        # 默认使用 10% 资金
        position_value = self.cash * 0.1
        shares = int(position_value / price / 100) * 100  # A 股 100 股一手

        if shares < 100:
            logger.debug(f"计算仓位不足 1 手：{shares} 股")
            return 0

        return shares

    def execute_trade(
        self,
        price: float,
        shares: int,
        signal: int,
        timestamp: pd.Timestamp
    ) -> bool:
        """
        执行交易

        Args:
            price: 成交价格
            shares: 交易数量
            signal: 买卖方向 (1=买入，-1=卖出)
            timestamp: 时间戳

        Returns:
            是否执行成功
        """
        if shares <= 0:
            logger.debug(f"无效交易数量：{shares}")
            return False

        if price <= 0:
            logger.warning(f"无效成交价格：{price}")
            return False

        try:
            if signal == 1:  # 买入
                cost = price * shares
                if cost <= self.cash:
                    self.cash -= cost
                    self.positions['shares'] = self.positions.get('shares', 0) + shares
                    self.trades.append({
                        'timestamp': timestamp,
                        'type': 'buy',
                        'price': price,
                        'shares': shares,
                        'cost': cost
                    })
                    logger.info(f"买入执行：{shares}股 @ {price:.2f}, 成本：{cost:,.2f}")
                    return True
                else:
                    logger.warning(f"资金不足：需要{cost:,.2f}, 可用{self.cash:,.2f}")
                    return False

            elif signal == -1:  # 卖出
                current_shares = self.positions.get('shares', 0)
                if current_shares >= shares:
                    revenue = price * shares
                    self.cash += revenue
                    self.positions['shares'] = current_shares - shares
                    self.trades.append({
                        'timestamp': timestamp,
                        'type': 'sell',
                        'price': price,
                        'shares': shares,
                        'revenue': revenue
                    })
                    logger.info(f"卖出执行：{shares}股 @ {price:.2f}, 收入：{revenue:,.2f}")
                    return True
                else:
                    logger.warning(f"持仓不足：需要{shares}股，可用{current_shares}股")
                    return False
            else:
                logger.warning(f"无效交易信号：{signal}")
                return False

        except Exception as e:
            logger.error(f"交易执行失败：{e}", exc_info=True)
            return False

    def get_portfolio_value(self, current_price: float) -> float:
        """
        计算组合总价值

        Args:
            current_price: 当前市场价格

        Returns:
            组合总价值 (现金 + 持仓市值)
        """
        if current_price <= 0:
            logger.warning(f"无效价格用于组合估值：{current_price}")
            return self.cash

        shares = self.positions.get('shares', 0)
        portfolio_value = self.cash + shares * current_price
        return portfolio_value

    def get_position_info(self) -> Dict[str, Any]:
        """
        获取持仓信息

        Returns:
            持仓信息字典
        """
        return {
            'shares': self.positions.get('shares', 0),
            'cash': self.cash,
            'total_value': self.get_portfolio_value(0),  # 仅现金
            'trade_count': len(self.trades)
        }

    def reset(self) -> None:
        """重置策略状态到初始值"""
        old_cash = self.cash
        old_trades = len(self.trades)

        self.positions = {}
        self.cash = self.initial_capital
        self.trades = []

        logger.info(f"策略重置：现金从{old_cash:,.2f}恢复到{self.initial_capital:,.2f}, 清除{old_trades}笔交易")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', capital={self.initial_capital:,.2f})"
