"""
OpenFinAgent - AI 量化交易助手

用自然语言写量化策略

版本：2.0.0
更新内容:
- 新增 4 个策略模板 (RSI, MACD, Bollinger, DualMA_Volume)
- 新增风险控制模块
- 新增策略优化器
- 新增批量回测
- 新增多数据源支持
- 全面代码优化 (类型注解、错误处理、日志)
"""

__version__ = "2.0.0"
__author__ = "OpenFinAgent Team"

# 策略模块
from .strategy import (
    BaseStrategy,
    MACrossStrategy,
    MomentumStrategy,
    RSIStrategy,
    MACDStrategy,
    BollingerStrategy,
    DualMAVolumeStrategy,
    StrategyBuilder,
)

# 回测模块
from .backtest import (
    BacktestEngine,
    BacktestResults,
    BatchBacktester,
    MultiStrategyBacktester,
)

# 数据模块
from .data import (
    AkShareDataSource,
    YahooFinanceDataSource,
    MockDataSource,
    load_data_from_source,
)

# 可视化
from .visualization import StrategyPlotter

__all__ = [
    # 策略
    "BaseStrategy",
    "MACrossStrategy",
    "MomentumStrategy",
    "RSIStrategy",
    "MACDStrategy",
    "BollingerStrategy",
    "DualMAVolumeStrategy",
    "StrategyBuilder",
    
    # 回测
    "BacktestEngine",
    "BacktestResults",
    "BatchBacktester",
    "MultiStrategyBacktester",
    
    # 数据
    "AkShareDataSource",
    "YahooFinanceDataSource",
    "MockDataSource",
    "load_data_from_source",
    
    # 可视化
    "StrategyPlotter",
]
