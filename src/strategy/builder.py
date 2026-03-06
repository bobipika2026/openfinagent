"""
策略构建器 - 从自然语言生成策略

支持策略类型：
- ma_cross: 均线交叉策略
- momentum: 动量策略
- rsi: RSI 超买超卖策略
- macd: MACD 金叉死叉策略
- bollinger: 布林带策略
- dual_ma_volume: 双均线 + 成交量策略
"""

from typing import Dict, List, Optional, Callable, Type
import pandas as pd
import numpy as np
import logging

from .base import BaseStrategy
from .rsi_strategy import RSIStrategy
from .macd_strategy import MACDStrategy
from .bollinger_strategy import BollingerStrategy
from .dual_ma_volume_strategy import DualMAVolumeStrategy
from ..nlp.parser import StrategyParser

logger = logging.getLogger(__name__)


class MACrossStrategy(BaseStrategy):
    """均线交叉策略"""

    def __init__(self, short_window: int = 5, long_window: int = 20, **kwargs):
        """
        初始化均线交叉策略

        Args:
            short_window: 短期均线周期
            long_window: 长期均线周期
            **kwargs: 传递给基类的参数
        """
        name = kwargs.get('name', f'MA_Cross_{short_window}_{long_window}')
        super().__init__(name=name, **kwargs)
        self.short_window = short_window
        self.long_window = long_window
        self.signals = None

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成均线交叉信号"""
        if 'close' not in data.columns:
            raise ValueError("数据必须包含 'close' 列")

        short_ma = data['close'].rolling(window=self.short_window).mean()
        long_ma = data['close'].rolling(window=self.long_window).mean()

        signals = pd.Series(0, index=data.index)
        signals[short_ma > long_ma] = 1
        signals[short_ma < long_ma] = -1

        # 检测交叉点
        signal_diff = signals.diff()
        buy_signals = (signal_diff == 2).astype(int)
        sell_signals = (signal_diff == -2).astype(int)

        return buy_signals - sell_signals

    def on_bar(self, data: pd.DataFrame, index: int) -> Optional[Dict]:
        if self.signals is None:
            self.signals = self.generate_signals(data)

        if index < self.long_window:
            return None

        signal = self.signals.iloc[index]
        if signal != 0:
            price = data['close'].iloc[index]
            shares = self.calculate_position_size(price, signal)
            if shares > 0:
                return {
                    'action': 'buy' if signal > 0 else 'sell',
                    'price': price,
                    'shares': shares,
                    'timestamp': data.index[index]
                }
        return None


class MomentumStrategy(BaseStrategy):
    """动量策略"""

    def __init__(self, lookback_period: int = 20, threshold: float = 0.05, **kwargs):
        """
        初始化动量策略

        Args:
            lookback_period: 回看周期
            threshold: 收益率阈值
            **kwargs: 传递给基类的参数
        """
        name = kwargs.get('name', f'Momentum_{lookback_period}_{threshold*100:.0f}%')
        super().__init__(name=name, **kwargs)
        self.lookback_period = lookback_period
        self.threshold = threshold

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        if 'close' not in data.columns:
            raise ValueError("数据必须包含 'close' 列")

        returns = data['close'].pct_change(periods=self.lookback_period)
        signals = pd.Series(0, index=data.index)
        signals[returns > self.threshold] = 1
        signals[returns < -self.threshold] = -1
        return signals.diff().fillna(0)

    def on_bar(self, data: pd.DataFrame, index: int) -> Optional[Dict]:
        if index < self.lookback_period:
            return None

        returns = (data['close'].iloc[index] / data['close'].iloc[index - self.lookback_period]) - 1
        price = data['close'].iloc[index]

        if returns > self.threshold:
            shares = self.calculate_position_size(price, 1)
            return {'action': 'buy', 'price': price, 'shares': shares, 'timestamp': data.index[index]}
        elif returns < -self.threshold:
            shares = self.calculate_position_size(price, -1)
            return {'action': 'sell', 'price': price, 'shares': shares, 'timestamp': data.index[index]}
        return None


class StrategyBuilder:
    """策略构建器 - 支持自然语言创建策略"""

    _strategy_templates: Dict[str, Type[BaseStrategy]] = {
        'ma_cross': MACrossStrategy,
        'momentum': MomentumStrategy,
        'rsi': RSIStrategy,
        'macd': MACDStrategy,
        'bollinger': BollingerStrategy,
        'dual_ma_volume': DualMAVolumeStrategy,
    }

    def __init__(self):
        self.parser = StrategyParser()

    @classmethod
    def from_natural_language(cls, description: str, **kwargs) -> BaseStrategy:
        """
        从自然语言描述创建策略

        Args:
            description: 策略的自然语言描述
            **kwargs: 额外参数

        Returns:
            策略实例

        Example:
            >>> strategy = StrategyBuilder.from_natural_language('''
            ... 当 5 日均线上穿 20 日均线时买入
            ... 当 5 日均线下穿 20 日均线时卖出
            ... 初始资金 10 万元
            ... ''')
        """
        builder = cls()
        parsed = builder.parser.parse(description)

        strategy_type = parsed.get('strategy_type', 'ma_cross')
        params = parsed.get('params', {})
        params.update(kwargs)

        if 'initial_capital' in parsed:
            params['initial_capital'] = parsed['initial_capital']
        if 'name' in parsed:
            params['name'] = parsed['name']

        strategy_class = cls._strategy_templates.get(strategy_type, MACrossStrategy)
        return strategy_class(**params)

    @classmethod
    def create(cls, strategy_type: str, **params) -> BaseStrategy:
        """
        直接创建策略

        Args:
            strategy_type: 策略类型
            **params: 策略参数

        Returns:
            策略实例
        """
        strategy_class = cls._strategy_templates.get(strategy_type)
        if not strategy_class:
            raise ValueError(f"未知策略类型：{strategy_type}")
        return strategy_class(**params)

    @classmethod
    def register_strategy(cls, name: str, strategy_class: type):
        """注册自定义策略"""
        cls._strategy_templates[name] = strategy_class

    @classmethod
    def list_strategies(cls) -> List[str]:
        """列出所有可用策略"""
        return list(cls._strategy_templates.keys())
