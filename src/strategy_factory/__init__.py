"""
策略工厂模块 - 自然语言创建策略、自动回测、自动入库

功能:
- 通过自然语言描述自动生成策略代码
- 支持多种策略类型：均线交叉、动量策略、布林带、RSI
- 自动回测集成，评分>=60 自动入库
- 遗传算法优化策略参数

模块结构:
- factory: 策略工厂核心类
- generator: 策略代码生成器
- optimizer: 策略优化器

示例:
    >>> from strategy_factory import StrategyFactory
    >>> factory = StrategyFactory()
    >>> # 通过自然语言创建策略
    >>> strategy = factory.create_from_natural_language(
    ...     "创建一个 5 日均线上穿 20 日均线的买入策略",
    ...     auto_backtest=True
    ... )
    >>> # 搜索并创建策略
    >>> strategies = factory.search_and_create("均线交叉", auto_backtest=True)
    >>> # 优化策略
    >>> optimized = factory.optimize_strategy(strategy.id, auto_backtest=True)

作者：OpenFinAgent Team
版本：1.0.0
"""

from .factory import StrategyFactory
from .generator import StrategyCodeGenerator
from .optimizer import StrategyOptimizer

__all__ = [
    'StrategyFactory',
    'StrategyCodeGenerator',
    'StrategyOptimizer',
]
