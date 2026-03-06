"""
RSI 策略 - 相对强弱指数策略

基于 RSI 指标的超买超卖信号进行交易。

策略逻辑：
- RSI < 30 (超卖) → 买入信号
- RSI > 70 (超买) → 卖出信号
- 可配置阈值和持仓周期

@module: strategy.rsi_strategy
@author: OpenFinAgent Team
@version: 1.0.0
"""

from typing import Dict, Optional
import pandas as pd
import numpy as np
import logging

from .base import BaseStrategy
from .indicators import calculate_rsi

logger = logging.getLogger(__name__)


class RSIStrategy(BaseStrategy):
    """
    RSI 超买超卖策略

    使用 RSI 指标判断市场超买超卖状态，进行逆向交易。

    Attributes:
        rsi_period: RSI 计算周期
        oversold_threshold: 超卖阈值 (买入触发点)
        overbought_threshold: 超买阈值 (卖出触发点)
        hold_period: 最小持仓周期 (避免频繁交易)
    """

    def __init__(
        self,
        rsi_period: int = 14,
        oversold_threshold: float = 30.0,
        overbought_threshold: float = 70.0,
        hold_period: int = 3,
        **kwargs
    ):
        """
        初始化 RSI 策略

        Args:
            rsi_period: RSI 计算周期 (默认 14)
            oversold_threshold: 超卖阈值 (默认 30)
            overbought_threshold: 超买阈值 (默认 70)
            hold_period: 最小持仓周期 (默认 3 天，避免频繁交易)
            **kwargs: 传递给基类的参数 (name, initial_capital 等)
        """
        if 'name' not in kwargs:
            kwargs['name'] = f'RSI_{rsi_period}_{oversold_threshold}_{overbought_threshold}'
        super().__init__(**kwargs)

        # 参数验证
        if rsi_period <= 1:
            raise ValueError(f"RSI 周期必须大于 1，当前值：{rsi_period}")
        if not 0 <= oversold_threshold < overbought_threshold <= 100:
            raise ValueError(
                f"阈值不合法：超卖={oversold_threshold}, 超买={overbought_threshold}"
            )
        if hold_period < 0:
            raise ValueError(f"持仓周期必须非负，当前值：{hold_period}")

        self.rsi_period = rsi_period
        self.oversold_threshold = oversold_threshold
        self.overbought_threshold = overbought_threshold
        self.hold_period = hold_period

        # 状态变量
        self.rsi_values: Optional[pd.Series] = None
        self.days_in_position = 0
        self.last_trade_type: Optional[str] = None

        logger.info(
            f"RSI 策略初始化：周期={rsi_period}, "
            f"超卖={oversold_threshold}, 超买={overbought_threshold}, "
            f"最小持仓={hold_period}天"
        )

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成 RSI 交易信号

        Args:
            data: 市场数据 DataFrame，必须包含 'close' 列

        Returns:
            信号 Series (1=买入，-1=卖出，0=持有)
        """
        if 'close' not in data.columns:
            raise ValueError("数据必须包含 'close' 列")

        # 计算 RSI
        rsi = calculate_rsi(data['close'], self.rsi_period)
        self.rsi_values = rsi

        # 生成信号
        signals = pd.Series(0, index=data.index)

        # 超卖 → 买入
        signals[rsi < self.oversold_threshold] = 1

        # 超买 → 卖出
        signals[rsi > self.overbought_threshold] = -1

        logger.debug(f"RSI 信号生成完成：买入信号={signals.sum()}, 卖出信号={(-signals).sum()}")
        return signals

    def on_bar(self, data: pd.DataFrame, index: int) -> Optional[Dict]:
        """
        每根 K 线回调 - 执行交易逻辑

        Args:
            data: 市场数据 DataFrame
            index: 当前 K 线索引

        Returns:
            交易指令字典或 None
        """
        if index < self.rsi_period:
            # 数据不足，等待 RSI 计算完成
            return None

        # 确保 RSI 已计算
        if self.rsi_values is None:
            self.rsi_values = self.generate_signals(data)

        current_rsi = self.rsi_values.iloc[index]
        current_price = data['close'].iloc[index]
        timestamp = data.index[index]

        # 检查持仓状态
        current_shares = self.positions.get('shares', 0)
        in_position = current_shares > 0

        # 更新持仓天数
        if in_position:
            self.days_in_position += 1
        else:
            self.days_in_position = 0

        # 交易逻辑
        signal = 0

        # 买入条件：RSI 超卖 + 当前无持仓 + 满足最小持仓间隔
        if (current_rsi < self.oversold_threshold and
            not in_position and
            (self.last_trade_type != 'sell' or self.days_in_position >= self.hold_period)):
            signal = 1
            logger.debug(f"买入信号：RSI={current_rsi:.2f} < {self.oversold_threshold}")

        # 卖出条件：RSI 超买 + 当前有持仓
        elif (current_rsi > self.overbought_threshold and in_position):
            signal = -1
            logger.debug(f"卖出信号：RSI={current_rsi:.2f} > {self.overbought_threshold}")

        # 执行交易
        if signal != 0:
            shares = self.calculate_position_size(current_price, signal)
            if shares > 0:
                return {
                    'action': 'buy' if signal > 0 else 'sell',
                    'price': current_price,
                    'shares': shares,
                    'timestamp': timestamp,
                    'rsi': current_rsi,
                    'reason': 'RSI_oversold' if signal > 0 else 'RSI_overbought'
                }

        return None

    def reset(self):
        """重置策略状态"""
        super().reset()
        self.rsi_values = None
        self.days_in_position = 0
        self.last_trade_type = None
        logger.debug("RSI 策略状态已重置")

    def get_strategy_info(self) -> Dict:
        """
        获取策略信息

        Returns:
            策略参数字典
        """
        return {
            'strategy_type': 'RSI',
            'rsi_period': self.rsi_period,
            'oversold_threshold': self.oversold_threshold,
            'overbought_threshold': self.overbought_threshold,
            'hold_period': self.hold_period,
            'current_rsi': self.rsi_values.iloc[-1] if self.rsi_values is not None else None
        }
