"""
双均线 + 成交量策略

结合双均线交叉和成交量确认的复合策略。

策略逻辑：
- 短均线上穿长均线 (金叉) + 成交量放大 → 买入信号
- 短均线下穿长均线 (死叉) + 成交量放大 → 卖出信号
- 成交量确认：当前成交量 > N 日均量 * 倍数

@module: strategy.dual_ma_volume_strategy
@author: OpenFinAgent Team
@version: 1.0.0
"""

from typing import Dict, Optional
import pandas as pd
import numpy as np
import logging

from .base import BaseStrategy
from .indicators import calculate_sma, detect_crossover

logger = logging.getLogger(__name__)


class DualMAVolumeStrategy(BaseStrategy):
    """
    双均线 + 成交量确认策略

    在传统双均线策略基础上增加成交量确认，提高信号可靠性。

    Attributes:
        short_window: 短期均线周期
        long_window: 长期均线周期
        volume_window: 成交量均线周期
        volume_multiplier: 成交量确认倍数
        require_volume_confirm: 是否要求成交量确认
    """

    def __init__(
        self,
        short_window: int = 5,
        long_window: int = 20,
        volume_window: int = 20,
        volume_multiplier: float = 1.5,
        require_volume_confirm: bool = True,
        **kwargs
    ):
        """
        初始化双均线 + 成交量策略

        Args:
            short_window: 短期均线周期 (默认 5)
            long_window: 长期均线周期 (默认 20)
            volume_window: 成交量均线周期 (默认 20)
            volume_multiplier: 成交量确认倍数 (默认 1.5 倍)
            require_volume_confirm: 是否要求成交量确认 (默认 True)
            **kwargs: 传递给基类的参数
        """
        if 'name' not in kwargs:
            kwargs['name'] = f'DualMA_Vol_{short_window}_{long_window}'
        super().__init__(**kwargs)

        # 参数验证
        if short_window >= long_window:
            raise ValueError(f"短周期 ({short_window}) 必须小于长周期 ({long_window})")
        if short_window <= 0 or long_window <= 0:
            raise ValueError("均线周期必须大于 0")
        if volume_window <= 0:
            raise ValueError(f"成交量周期必须大于 0，当前值：{volume_window}")
        if volume_multiplier <= 0:
            raise ValueError(f"成交量倍数必须大于 0，当前值：{volume_multiplier}")

        self.short_window = short_window
        self.long_window = long_window
        self.volume_window = volume_window
        self.volume_multiplier = volume_multiplier
        self.require_volume_confirm = require_volume_confirm

        # 状态变量
        self.short_ma: Optional[pd.Series] = None
        self.long_ma: Optional[pd.Series] = None
        self.volume_ma: Optional[pd.Series] = None
        self.signals: Optional[pd.Series] = None

        logger.info(
            f"双均线 + 成交量策略初始化：short={short_window}, long={long_window}, "
            f"vol_window={volume_window}, vol_mult={volume_multiplier}"
        )

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成双均线 + 成交量交易信号

        Args:
            data: 市场数据 DataFrame，必须包含 'close' 和 'volume' 列

        Returns:
            信号 Series (1=买入，-1=卖出，0=持有)
        """
        if 'close' not in data.columns:
            raise ValueError("数据必须包含 'close' 列")
        if 'volume' not in data.columns:
            raise ValueError("数据必须包含 'volume' 列")

        # 计算均线
        self.short_ma = calculate_sma(data['close'], self.short_window)
        self.long_ma = calculate_sma(data['close'], self.long_window)
        self.volume_ma = calculate_sma(data['volume'], self.volume_window)

        # 检测均线交叉
        golden_cross = detect_crossover(
            self.short_ma,
            self.long_ma,
            direction='cross_above'
        )
        death_cross = detect_crossover(
            self.short_ma,
            self.long_ma,
            direction='cross_below'
        )

        # 成交量确认
        volume_confirm = data['volume'] > (self.volume_ma * self.volume_multiplier)

        # 生成基础信号
        self.signals = pd.Series(0, index=data.index)

        if self.require_volume_confirm:
            # 需要成交量确认
            self.signals[golden_cross & volume_confirm] = 1
            self.signals[death_cross & volume_confirm] = -1
        else:
            # 不需要成交量确认
            self.signals[golden_cross] = 1
            self.signals[death_cross] = -1

        logger.debug(
            f"双均线 + 成交量信号生成完成：买入={self.signals.sum()}, "
            f"卖出={(-self.signals).sum()}"
        )
        return self.signals

    def on_bar(self, data: pd.DataFrame, index: int) -> Optional[Dict]:
        """
        每根 K 线回调 - 执行交易逻辑

        Args:
            data: 市场数据 DataFrame
            index: 当前 K 线索引

        Returns:
            交易指令字典或 None
        """
        # 需要足够的数据计算指标
        min_index = max(self.long_window, self.volume_window)
        if index < min_index:
            return None

        # 确保指标已计算
        if self.short_ma is None:
            self.generate_signals(data)

        current_price = data['close'].iloc[index]
        current_volume = data['volume'].iloc[index]
        timestamp = data.index[index]

        # 当前指标值
        short_ma = self.short_ma.iloc[index]
        long_ma = self.long_ma.iloc[index]
        volume_ma = self.volume_ma.iloc[index]

        # 前一根 K 线的值
        prev_short_ma = self.short_ma.iloc[index - 1]
        prev_long_ma = self.long_ma.iloc[index - 1]

        # 检测交叉
        golden_cross = (prev_short_ma < prev_long_ma) and (short_ma > long_ma)
        death_cross = (prev_short_ma > prev_long_ma) and (short_ma < long_ma)

        # 成交量确认
        volume_ratio = current_volume / volume_ma if volume_ma > 0 else 0
        volume_confirm = volume_ratio >= self.volume_multiplier

        # 交易逻辑
        signal = 0
        reason = ''

        if golden_cross:
            if not self.require_volume_confirm or volume_confirm:
                signal = 1
                reason = 'GoldenCross_VolConfirm' if volume_confirm else 'GoldenCross'
                logger.debug(
                    f"金叉信号：短 MA={short_ma:.2f} > 长 MA={long_ma:.2f}, "
                    f"成交量比={volume_ratio:.2f}"
                )

        elif death_cross:
            if not self.require_volume_confirm or volume_confirm:
                signal = -1
                reason = 'DeathCross_VolConfirm' if volume_confirm else 'DeathCross'
                logger.debug(
                    f"死叉信号：短 MA={short_ma:.2f} < 长 MA={long_ma:.2f}, "
                    f"成交量比={volume_ratio:.2f}"
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
                    'short_ma': short_ma,
                    'long_ma': long_ma,
                    'volume': current_volume,
                    'volume_ma': volume_ma,
                    'volume_ratio': volume_ratio,
                    'reason': reason
                }

        return None

    def reset(self):
        """重置策略状态"""
        super().reset()
        self.short_ma = None
        self.long_ma = None
        self.volume_ma = None
        self.signals = None
        logger.debug("双均线 + 成交量策略状态已重置")

    def get_strategy_info(self) -> Dict:
        """
        获取策略信息

        Returns:
            策略参数字典
        """
        return {
            'strategy_type': 'DualMA_Volume',
            'short_window': self.short_window,
            'long_window': self.long_window,
            'volume_window': self.volume_window,
            'volume_multiplier': self.volume_multiplier,
            'require_volume_confirm': self.require_volume_confirm,
            'current_short_ma': float(self.short_ma.iloc[-1]) if self.short_ma is not None else None,
            'current_long_ma': float(self.long_ma.iloc[-1]) if self.long_ma is not None else None,
            'current_volume_ma': float(self.volume_ma.iloc[-1]) if self.volume_ma is not None else None
        }
