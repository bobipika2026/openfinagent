"""
回测模块 - 策略回测引擎

包含：
- 回测引擎
- 回测结果
- 批量回测
- 多策略对比
"""

from .engine import BacktestEngine, load_data, generate_mock_data
from .results import BacktestResults
from .batch import BatchBacktester, BatchBacktestConfig, BatchBacktestResult, MultiStrategyBacktester

__all__ = [
    # 核心引擎
    'BacktestEngine',
    'BacktestResults',

    # 数据加载
    'load_data',
    'generate_mock_data',

    # 批量回测
    'BatchBacktester',
    'BatchBacktestConfig',
    'BatchBacktestResult',
    'MultiStrategyBacktester',
]
