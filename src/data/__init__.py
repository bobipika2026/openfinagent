"""
数据模块 - 市场数据源

包含：
- 多数据源支持 (AkShare, Yahoo Finance, Tushare, Binance, CSV, Mock)
- 数据加载器
- 数据预处理
"""

from .sources import (
    DataSource,
    AkShareDataSource,
    YahooFinanceDataSource,
    TushareDataSource,
    CSVDataSource,
    MockDataSource,
    get_data_source,
    load_data_from_source
)

from .binance_source import (
    BinanceDataSource,
    get_binance_data
)

__all__ = [
    'DataSource',
    'AkShareDataSource',
    'YahooFinanceDataSource',
    'TushareDataSource',
    'BinanceDataSource',
    'CSVDataSource',
    'MockDataSource',
    'get_data_source',
    'load_data_from_source',
    'get_binance_data',
]
