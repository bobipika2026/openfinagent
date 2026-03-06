"""
MACD 策略 - 移动平均收敛发散策略

基于 MACD 指标的金叉死叉信号进行交易。

策略逻辑：
- MACD 线上穿 Signal 线 (金叉) → 买入信号
- MACD 线下穿 Signal 线 (死叉) → 卖出信号
- 可结合 Histogram 确认信号强度

@module: strategy.macd_strategy
@author: TradeFlow AI Team
@version: 1.0.0
"""

from typing import Dict, Optional, Tuple
import pandas as pd
import numpy as np
import logging

from .base import BaseStrategy
from .indicators import calculate_macd

logger = logging.getLogger(__name__)


class MACDStrategy(BaseStrategy):
    """
    MACD 金叉死叉策略

    使用 MACD 指标的交叉信号进行趋势跟踪交易。

    Attributes:
        fast_period: 快线 EMA 周期
        slow_period: 慢线 EMA 周期
        signal_period: 信号线 EMA 周期
        use_histogram: 是否使用 Histogram 确认信号
        histogram_threshold: Histogram 确认阈值
    """

    def __init__(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        use_histogram: bool = True,
        histogram_threshold: float = 0.0,
        **kwargs
    ):
        """
        初始化 MACD 策略

        Args:
            fast_period: 快线周期 (默认 12)
            slow_period: 慢线周期 (默认 26)
            signal_period: 信号线周期 (默认 9)
            use_histogram: 是否使用 Histogram 确认 (默认 True)
            histogram_threshold: Histogram 确认阈值 (默认 0)
            **kwargs: 传递给基类的参数
        """
        if 'name' not in kwargs:
            kwargs['name'] = f'MACD_{fast_period}_{slow_period}_{signal_period}'
        super().__init__(**kwargs)

        # 参数验证
        if fast_period >= slow_period:
            raise ValueError(f"快线周期 ({fast_period}) 必须小于慢线周期 ({slow_period})")
        if fast_period <= 0 or slow_period <= 0 or signal_period <= 0:
            raise ValueError("所有周期参数必须大于 0")

        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.use_histogram = use_histogram
        self.histogram_threshold = histogram_threshold

        # 状态变量
        self.macd_line: Optional[pd.Series] = None
        self.signal_line: Optional[pd.Series] = None
        self.histogram: Optional[pd.Series] = None

        logger.info(
            f"MACD 策略初始化：fast={fast_period}, slow={slow_period}, "
            f"signal={signal_period}, histogram={use_histogram}"
        )

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成 MACD 交易信号

        Args:
            data: 市场数据 DataFrame，必须包含 'close' 列

        Returns:
            信号 Series (1=买入，-1=卖出，0=持有)
        """
        if 'close' not in data.columns:
            raise ValueError("数据必须包含 'close' 列")

        # 计算 MACD
        self.macd_line, self.signal_line, self.histogram = calculate_macd(
            data['close'],
            self.fast_period,
            self.slow_period,
            self.signal_period
        )

        # 生成基础信号
        signals = pd.Series(0, index=data.index)

        # 检测金叉 (MACD 线上穿 Signal 线)
        golden_cross = (
            (self.macd_line.shift(1) < self.signal_line.shift(1)) &
            (self.macd_line > self.signal_line)
        )
        signals[golden_cross] = 1

        # 检测死叉 (MACD 线下穿 Signal 线)
        death_cross = (
            (self.macd_line.shift(1) > self.signal_line.shift(1)) &
            (self.macd_line < self.signal_line)
        )
        signals[death_cross] = -1

        # 使用 Histogram 确认信号 (可选)
        if self.use_histogram and self.histogram_threshold > 0:
            # 买入时要求 Histogram > 阈值
            buy_confirm = self.histogram > self.histogram_threshold
            signals[(signals == 1) & ~buy_confirm] = 0

            # 卖出时要求 Histogram < -阈值
            sell_confirm = self.histogram < -self.histogram_threshold
            signals[(signals == -1) & ~sell_confirm] = 0

        logger.debug(
            f"MACD 信号生成完成：金叉={signals.sum()}, "
            f"死叉={(-signals).sum()}"
        )
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
        # 需要足够的数据计算 MACD
        min_index = max(self.fast_period, self.slow_period, self.signal_period)
        if index < min_index:
            return None

        # 确保 MACD 已计算
        if self.macd_line is None:
            self.generate_signals(data)

        current_price = data['close'].iloc[index]
        timestamp = data.index[index]

        # 当前 MACD 值
        current_macd = self.macd_line.iloc[index]
        current_signal = self.signal_line.iloc[index]
        current_hist = self.histogram.iloc[index] if self.histogram is not None else 0

        # 前一根 K 线的 MACD 值
        prev_macd = self.macd_line.iloc[index - 1]
        prev_signal = self.signal_line.iloc[index - 1]

        # 检测交叉
        golden_cross = (prev_macd < prev_signal) and (current_macd > current_signal)
        death_cross = (prev_macd > prev_signal) and (current_macd < current_signal)

        # Histogram 确认
        hist_confirm_buy = not self.use_histogram or (current_hist > self.histogram_threshold)
        hist_confirm_sell = not self.use_histogram or (current_hist < -self.histogram_threshold)

        # 交易逻辑
        signal = 0
        reason = ''

        if golden_cross and hist_confirm_buy:
            signal = 1
            reason = 'MACD_golden_cross'
            logger.debug(
                f"金叉信号：MACD={current_macd:.4f}, Signal={current_signal:.4f}, "
                f"Hist={current_hist:.4f}"
            )

        elif death_cross and hist_confirm_sell:
            signal = -1
            reason = 'MACD_death_cross'
            logger.debug(
                f"死叉信号：MACD={current_macd:.4f}, Signal={current_signal:.4f}, "
                f"Hist={current_hist:.4f}"
            )

        # 执行交易
        if signal != 0:
            shares = self.calculate_position_size(current_price, signal)
            if shares > 0:
                return {
                    'action': 'buy' if signal > 0 else 'sell',
                    'price': current_price,
                    'shares': shares,
                    'timestamp': timestamp,
                    'macd': current_macd,
                    'signal': current_signal,
                    'histogram': current_hist,
                    'reason': reason
                }

        return None

    def reset(self):
        """重置策略状态"""
        super().reset()
        self.macd_line = None
        self.signal_line = None
        self.histogram = None
        logger.debug("MACD 策略状态已重置")

    def get_strategy_info(self) -> Dict:
        """
        获取策略信息

        Returns:
            策略参数字典
        """
        return {
            'strategy_type': 'MACD',
            'fast_period': self.fast_period,
            'slow_period': self.slow_period,
            'signal_period': self.signal_period,
            'use_histogram': self.use_histogram,
            'histogram_threshold': self.histogram_threshold,
            'current_macd': float(self.macd_line.iloc[-1]) if self.macd_line is not None else None,
            'current_signal': float(self.signal_line.iloc[-1]) if self.signal_line is not None else None,
            'current_histogram': float(self.histogram.iloc[-1]) if self.histogram is not None else None
        }
