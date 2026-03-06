"""
策略模块 - 交易策略实现

包含：
- 策略基类
- 技术指标计算
- 内置策略模板 (MACross, Momentum, RSI, MACD, Bollinger, DualMA_Volume)
- 策略构建器
"""

from .base import BaseStrategy
from .builder import (
    MACrossStrategy,
    MomentumStrategy,
    StrategyBuilder
)
from .indicators import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_atr,
    detect_crossover,
    is_overbought,
    is_oversold
)
from .rsi_strategy import RSIStrategy
from .macd_strategy import MACDStrategy
from .bollinger_strategy import BollingerStrategy
from .dual_ma_volume_strategy import DualMAVolumeStrategy

__all__ = [
    # 基类
    'BaseStrategy',

    # 内置策略
    'MACrossStrategy',
    'MomentumStrategy',
    'RSIStrategy',
    'MACDStrategy',
    'BollingerStrategy',
    'DualMAVolumeStrategy',

    # 构建器
    'StrategyBuilder',

    # 指标
    'calculate_sma',
    'calculate_ema',
    'calculate_rsi',
    'calculate_macd',
    'calculate_bollinger_bands',
    'calculate_atr',
    'detect_crossover',
    'is_overbought',
    'is_oversold',
]
