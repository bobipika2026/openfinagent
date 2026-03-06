"""
数据模块 - 市场数据源

包含：
- 多数据源支持 (AkShare, Yahoo Finance, Tushare, Binance, CSV, Mock)
- 数据加载器
- 数据预处理
- Tushare 增强版 (Token 管理、缓存、错误处理)
"""

from .sources import (
    DataSource,
    AkShareDataSource,
    YahooFinanceDataSource,
    TushareDataSource as LegacyTushareDataSource,
    CSVDataSource,
    MockDataSource,
    get_data_source,
    load_data_from_source
)

from .binance_source import (
    BinanceDataSource,
    get_binance_data
)

# Tushare 增强版
from .tushare_source import (
    TushareDataSource,
    TushareAPIError,
    TushareRateLimitError,
    get_daily,
    get_min,
    get_quote,
    get_tushare_data
)

from .tushare_token_manager import (
    TushareTokenManager,
    TokenInfo,
    get_token_manager,
    init_token_manager,
    get_token
)

from .tushare_cache import (
    TushareCache,
    CacheEntry,
    get_cache,
    init_cache,
    cache_data,
    get_cached_data
)

__all__ = [
    # 基础数据源
    'DataSource',
    'AkShareDataSource',
    'YahooFinanceDataSource',
    'LegacyTushareDataSource',  # 旧版 Tushare
    'BinanceDataSource',
    'CSVDataSource',
    'MockDataSource',
    'get_data_source',
    'load_data_from_source',
    'get_binance_data',
    
    # Tushare 增强版
    'TushareDataSource',  # 增强版 Tushare
    'TushareAPIError',
    'TushareRateLimitError',
    'get_daily',
    'get_min',
    'get_quote',
    'get_tushare_data',
    
    # Token 管理
    'TushareTokenManager',
    'TokenInfo',
    'get_token_manager',
    'init_token_manager',
    'get_token',
    
    # 缓存
    'TushareCache',
    'CacheEntry',
    'get_cache',
    'init_cache',
    'cache_data',
    'get_cached_data',
]
