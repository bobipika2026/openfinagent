"""
选股引擎模块

提供自动化选股、批量回测、股票池管理功能

@module: stock_selector
@author: OpenFinAgent Team
@version: 1.0.0

Example:
    ```python
    from src.stock_selector import StockSelector, StockCriteria, create_selector
    
    # 初始化选股引擎
    selector = create_selector()
    
    # 定义选股条件
    criteria = StockCriteria(
        top_n=20,
        min_score=70,
        min_sharpe=1.5,
        max_drawdown=0.15
    )
    
    # 执行选股
    pool = selector.select_stocks(
        strategy=my_strategy,
        stock_pool=stock_list,
        criteria=criteria
    )
    
    # 批量回测
    report = selector.batch_backtest(
        strategy=my_strategy,
        stock_pool=pool.stocks
    )
    
    # 查看报告
    report.show()
    ```
"""

from .criteria import (
    StockCriteria,
    StockScore,
    SelectionMethod,
    FilterResult
)

from .pool_manager import (
    StockPool,
    PoolManager,
    create_pool_manager
)

from .selector import (
    StockSelector,
    BatchBacktestReport,
    create_selector
)

__all__ = [
    # 选股条件
    'StockCriteria',
    'StockScore',
    'SelectionMethod',
    'FilterResult',
    
    # 股票池管理
    'StockPool',
    'PoolManager',
    'create_pool_manager',
    
    # 选股引擎
    'StockSelector',
    'BatchBacktestReport',
    'create_selector',
]

__version__ = '1.0.0'
__author__ = 'OpenFinAgent Team'
