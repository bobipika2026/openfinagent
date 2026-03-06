"""
布林带策略 - Bollinger Bands 策略

基于布林带的价格突破和均值回归信号进行交易。

策略逻辑：
- 价格跌破下轨 → 超卖 → 买入信号 (均值回归)
- 价格突破上轨 → 超买 → 卖出信号 (均值回归)
- 价格从中轨下方突破中轨 → 买入信号 (趋势突破)
- 价格从中轨上方跌破中轨 → 卖出信号 (趋势突破)

@module: strategy.bollinger_strategy
@author: OpenFinAgent Team
@version: 1.0.0
"""

from typing import Dict, Optional
import pandas as pd
import numpy as np
import logging

from .base import BaseStrategy
from .indicators import calculate_bollinger_bands

logger = logging.getLogger(__name__)


class BollingerStrategy(BaseStrategy):
    """
    布林带策略

    支持两种交易模式：
    1. 均值回归模式：价格突破上下轨时反向交易
    2. 趋势突破模式：价格突破中轨时顺势交易

    Attributes:
        window: 布林带计算周期
        num_std: 标准差倍数
        mode: 交易模式 ('mean_reversion' 或 'trend_breakout')
        use_middle_band: 是否使用中轨确认信号
    """

    def __init__(
        self,
        window: int = 20,
        num_std: float = 2.0,
        mode: str = 'mean_reversion',
        use_middle_band: bool = True,
        **kwargs
    ):
        """
        初始化布林带策略

        Args:
            window: 计算周期 (默认 20)
            num_std: 标准差倍数 (默认 2)
            mode: 交易模式
                   - 'mean_reversion': 均值回归 (突破上下轨反向交易)
                   - 'trend_breakout': 趋势突破 (突破中轨顺势交易)
            use_middle_band: 是否使用中轨确认 (默认 True)
            **kwargs: 传递给基类的参数
        """
        if 'name' not in kwargs:
            kwargs['name'] = f'Bollinger_{window}_{num_std}_{mode}'
        super().__init__(**kwargs)

        # 参数验证
        if window <= 1:
            raise ValueError(f"窗口必须大于 1，当前值：{window}")
        if num_std <= 0:
            raise ValueError(f"标准差倍数必须大于 0，当前值：{num_std}")
        if mode not in ['mean_reversion', 'trend_breakout']:
            raise ValueError(f"无效的交易模式：{mode}")

        self.window = window
        self.num_std = num_std
        self.mode = mode
        self.use_middle_band = use_middle_band

        # 状态变量
        self.upper_band: Optional[pd.Series] = None
        self.middle_band: Optional[pd.Series] = None
        self.lower_band: Optional[pd.Series] = None
        self.bandwidth: Optional[pd.Series] = None  # 带宽指标

        logger.info(
            f"布林带策略初始化：window={window}, num_std={num_std}, "
            f"mode={mode}, use_middle={use_middle_band}"
        )

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成布林带交易信号

        Args:
            data: 市场数据 DataFrame，必须包含 'close' 列

        Returns:
            信号 Series (1=买入，-1=卖出，0=持有)
        """
        if 'close' not in data.columns:
            raise ValueError("数据必须包含 'close' 列")

        # 计算布林带
        self.upper_band, self.middle_band, self.lower_band = calculate_bollinger_bands(
            data['close'],
            self.window,
            self.num_std
        )

        # 计算带宽 (上轨 - 下轨) / 中轨
        self.bandwidth = (self.upper_band - self.lower_band) / self.middle_band

        # 生成信号
        signals = pd.Series(0, index=data.index)
        close = data['close']

        if self.mode == 'mean_reversion':
            # 均值回归模式
            # 价格跌破下轨 → 买入
            signals[close < self.lower_band] = 1
            # 价格突破上轨 → 卖出
            signals[close > self.upper_band] = -1

        else:  # trend_breakout
            # 趋势突破模式
            # 价格从下向上突破中轨 → 买入
            if self.use_middle_band:
                breakout_up = (
                    (close.shift(1) < self.middle_band.shift(1)) &
                    (close > self.middle_band)
                )
                signals[breakout_up] = 1

                # 价格从上向下跌破中轨 → 卖出
                breakout_down = (
                    (close.shift(1) > self.middle_band.shift(1)) &
                    (close < self.middle_band)
                )
                signals[breakout_down] = -1

        logger.debug(
            f"布林带信号生成完成：模式={self.mode}, "
            f"买入信号={signals.sum()}, 卖出信号={(-signals).sum()}"
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
        if index < self.window:
            # 数据不足，等待布林带计算完成
            return None

        # 确保布林带已计算
        if self.middle_band is None:
            self.generate_signals(data)

        current_price = data['close'].iloc[index]
        timestamp = data.index[index]

        # 当前布林带值
        upper = self.upper_band.iloc[index]
        middle = self.middle_band.iloc[index]
        lower = self.lower_band.iloc[index]
        bandwidth = self.bandwidth.iloc[index] if self.bandwidth is not None else 0

        # 前一根 K 线的值
        prev_price = data['close'].iloc[index - 1]
        prev_middle = self.middle_band.iloc[index - 1]

        # 交易逻辑
        signal = 0
        reason = ''

        if self.mode == 'mean_reversion':
            # 均值回归模式
            if current_price < lower:
                signal = 1
                reason = 'BB_oversold'
                logger.debug(
                    f"超卖信号：价格={current_price:.2f} < 下轨={lower:.2f}"
                )
            elif current_price > upper:
                signal = -1
                reason = 'BB_overbought'
                logger.debug(
                    f"超买信号：价格={current_price:.2f} > 上轨={upper:.2f}"
                )

        else:  # trend_breakout
            # 趋势突破模式
            if self.use_middle_band:
                # 向上突破中轨
                if prev_price < prev_middle and current_price > middle:
                    signal = 1
                    reason = 'BB_breakout_up'
                    logger.debug(
                        f"向上突破：价格={current_price:.2f} > 中轨={middle:.2f}"
                    )
                # 向下跌破中轨
                elif prev_price > prev_middle and current_price < middle:
                    signal = -1
                    reason = 'BB_breakout_down'
                    logger.debug(
                        f"向下跌破：价格={current_price:.2f} < 中轨={middle:.2f}"
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
                    'upper_band': upper,
                    'middle_band': middle,
                    'lower_band': lower,
                    'bandwidth': bandwidth,
                    'reason': reason
                }

        return None

    def reset(self):
        """重置策略状态"""
        super().reset()
        self.upper_band = None
        self.middle_band = None
        self.lower_band = None
        self.bandwidth = None
        logger.debug("布林带策略状态已重置")

    def get_strategy_info(self) -> Dict:
        """
        获取策略信息

        Returns:
            策略参数字典
        """
        return {
            'strategy_type': 'Bollinger',
            'window': self.window,
            'num_std': self.num_std,
            'mode': self.mode,
            'use_middle_band': self.use_middle_band,
            'current_upper': float(self.upper_band.iloc[-1]) if self.upper_band is not None else None,
            'current_middle': float(self.middle_band.iloc[-1]) if self.middle_band is not None else None,
            'current_lower': float(self.lower_band.iloc[-1]) if self.lower_band is not None else None,
            'current_bandwidth': float(self.bandwidth.iloc[-1]) if self.bandwidth is not None else None
        }
