"""
数据源管理器

统一管理多个数据源，支持自动降级和故障切换

@module: data.manager
@author: OpenFinAgent Team
@version: 0.4.0
"""

from typing import Optional, Dict, Any, List, Type
from datetime import datetime
import pandas as pd
import logging
from abc import ABC, abstractmethod

from .sources import DataSource, AkShareDataSource, YahooFinanceDataSource, TushareDataSource, MockDataSource
from .alpha_vantage_source import AlphaVantageDataSource

logger = logging.getLogger(__name__)


class DataQualityReport:
    """数据质量报告"""
    
    def __init__(
        self,
        symbol: str,
        source: str,
        quality: str = 'unknown',
        missing_rate: float = 1.0,
        last_update: Optional[datetime] = None,
        error: Optional[str] = None
    ):
        self.symbol = symbol
        self.source = source
        self.quality = quality
        self.missing_rate = missing_rate
        self.last_update = last_update
        self.error = error
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'symbol': self.symbol,
            'source': self.source,
            'quality': self.quality,
            'missing_rate': self.missing_rate,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'error': self.error
        }


class DataManager:
    """
    数据源管理器
    
    统一管理多个数据源，提供：
    - 统一的数据访问接口
    - 自动故障切换和降级
    - 数据质量监控
    - 缓存优化
    
    Attributes:
        config: 数据源配置
        feeds: 数据源实例字典
        primary: 主数据源名称
        cache: 数据缓存
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化数据源管理器
        
        Args:
            config: 数据源配置字典
        
        Example config:
        ```python
        config = {
            'primary': 'akshare',
            'fallback_order': ['akshare', 'yfinance', 'alphavantage', 'mock'],
            'sources': {
                'tushare': {'api_key': 'xxx'},
                'alphavantage': {'api_key': 'xxx'},
                'akshare': {'adjust': 'qfq'},
            },
            'enable_cache': True,
            'cache_ttl': 3600  # 缓存有效期 (秒)
        }
        ```
        """
        self.config = config or {}
        self.primary = self.config.get('primary', 'akshare')
        self.fallback_order = self.config.get('fallback_order', [
            'akshare', 'yfinance', 'alphavantage', 'mock'
        ])
        
        # 初始化数据源
        self.feeds: Dict[str, DataSource] = {}
        self._init_feeds()
        
        # 缓存配置
        self.enable_cache = self.config.get('enable_cache', True)
        self.cache_ttl = self.config.get('cache_ttl', 3600)  # 默认 1 小时
        self._cache: Dict[str, tuple] = {}  # key -> (data, timestamp)
        
        # 数据源状态
        self._source_status: Dict[str, bool] = {name: True for name in self.fallback_order}
        
        logger.info(f"数据源管理器初始化完成，主数据源：{self.primary}")
    
    def _init_feeds(self) -> None:
        """初始化所有数据源"""
        sources_config = self.config.get('sources', {})
        
        # AkShare (A 股)
        try:
            ak_config = sources_config.get('akshare', {})
            self.feeds['akshare'] = AkShareDataSource(**ak_config)
            logger.debug("AkShare 数据源初始化成功")
        except Exception as e:
            logger.warning(f"AkShare 数据源初始化失败：{e}")
        
        # Yahoo Finance (美股/港股)
        try:
            self.feeds['yfinance'] = YahooFinanceDataSource()
            logger.debug("Yahoo Finance 数据源初始化成功")
        except Exception as e:
            logger.warning(f"Yahoo Finance 数据源初始化失败：{e}")
        
        # Tushare (A 股，需要 API key)
        try:
            ts_config = sources_config.get('tushare', {})
            if 'api_key' in ts_config or 'TUSHARE_TOKEN' in __import__('os').environ:
                self.feeds['tushare'] = TushareDataSource(**ts_config)
                logger.debug("Tushare 数据源初始化成功")
        except Exception as e:
            logger.debug(f"Tushare 数据源初始化失败 (可能缺少 API key): {e}")
        
        # Alpha Vantage (全球市场)
        try:
            av_config = sources_config.get('alphavantage', {})
            if 'api_key' in av_config or 'ALPHA_VANTAGE_API_KEY' in __import__('os').environ:
                self.feeds['alphavantage'] = AlphaVantageDataSource(**av_config)
                logger.debug("Alpha Vantage 数据源初始化成功")
        except Exception as e:
            logger.debug(f"Alpha Vantage 数据源初始化失败 (可能缺少 API key): {e}")
        
        # Mock (测试用)
        try:
            self.feeds['mock'] = MockDataSource()
            logger.debug("Mock 数据源初始化成功")
        except Exception as e:
            logger.warning(f"Mock 数据源初始化失败：{e}")
    
    def get_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        source: Optional[str] = None,
        use_cache: bool = True,
        **kwargs
    ) -> pd.DataFrame:
        """
        获取数据 (带自动降级)
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            source: 指定数据源 (不提供则自动选择)
            use_cache: 是否使用缓存
            **kwargs: 传递给数据源的额外参数
        
        Returns:
            OHLCV 数据 DataFrame
        
        Raises:
            ValueError: 当所有数据源都失败时
        """
        # 检查缓存
        cache_key = f"{symbol}:{start_date}:{end_date}:{source or 'auto'}"
        
        if use_cache and self.enable_cache:
            cached_data = self._get_from_cache(cache_key)
            if cached_data is not None:
                logger.debug(f"使用缓存数据：{cache_key}")
                return cached_data
        
        # 确定数据源顺序
        if source:
            # 使用指定数据源
            source_order = [source]
        else:
            # 使用降级顺序
            source_order = self.fallback_order
        
        # 尝试各个数据源
        last_error = None
        
        for source_name in source_order:
            # 检查数据源是否可用
            if not self._is_source_available(source_name):
                logger.debug(f"数据源 {source_name} 不可用，跳过")
                continue
            
            try:
                feed = self.feeds.get(source_name)
                
                if not feed:
                    logger.warning(f"数据源 {source_name} 未初始化")
                    continue
                
                # 获取数据
                logger.info(f"从 {source_name} 获取数据：{symbol}")
                
                # 调用数据源的 get_data 方法
                import inspect
                sig = inspect.signature(feed.get_data)
                
                # 根据方法签名决定调用方式
                if 'freq' in sig.parameters:
                    # Alpha Vantage 等支持 freq 参数
                    data = feed.get_data(symbol, start_date, end_date, **kwargs)
                else:
                    # 标准接口
                    data = feed.get_data(symbol, start_date, end_date)
                
                # 验证数据
                if data is None or data.empty:
                    logger.warning(f"{source_name} 返回空数据")
                    continue
                
                # 缓存数据
                if self.enable_cache:
                    self._save_to_cache(cache_key, data)
                
                # 标记数据源为可用
                self._source_status[source_name] = True
                
                logger.info(f"从 {source_name} 成功获取 {len(data)} 行数据")
                return data
                
            except Exception as e:
                last_error = e
                logger.warning(f"{source_name} 数据源失败：{e}")
                # 标记数据源为不可用 (临时)
                self._source_status[source_name] = False
        
        # 所有数据源都失败
        error_msg = f"所有数据源均失败，最后错误：{last_error}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    def get_realtime(self, symbol: str, source: Optional[str] = None) -> Dict[str, Any]:
        """
        获取实时行情
        
        Args:
            symbol: 股票代码
            source: 指定数据源
        
        Returns:
            实时行情字典
        """
        # 确定数据源
        if source:
            source_order = [source]
        else:
            source_order = self.fallback_order
        
        for source_name in source_order:
            try:
                feed = self.feeds.get(source_name)
                
                if not feed:
                    continue
                
                # 检查是否有 get_realtime 方法
                if hasattr(feed, 'get_realtime'):
                    data = feed.get_realtime(symbol)
                    if data:
                        return data
                
            except Exception as e:
                logger.warning(f"{source_name} 实时行情获取失败：{e}")
                continue
        
        return {}
    
    def check_quality(self, symbol: str) -> List[DataQualityReport]:
        """
        检查多个数据源的数据质量
        
        Args:
            symbol: 股票代码
        
        Returns:
            数据质量报告列表
        """
        reports = []
        
        for source_name, feed in self.feeds.items():
            try:
                if hasattr(feed, 'check_quality'):
                    quality = feed.check_quality(symbol)
                    report = DataQualityReport(
                        symbol=symbol,
                        source=source_name,
                        quality=quality.get('quality', 'unknown'),
                        missing_rate=quality.get('missing_rate', 1.0),
                        last_update=pd.to_datetime(quality.get('last_update')) if quality.get('last_update') else None,
                        error=quality.get('error')
                    )
                else:
                    # 尝试获取数据来评估质量
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - pd.Timedelta(days=30)).strftime('%Y-%m-%d')
                    
                    data = feed.get_data(symbol, start_date, end_date)
                    
                    if data.empty:
                        quality = 'poor'
                        missing_rate = 1.0
                    else:
                        quality = 'good'
                        missing_rate = 0.0
                    
                    report = DataQualityReport(
                        symbol=symbol,
                        source=source_name,
                        quality=quality,
                        missing_rate=missing_rate,
                        last_update=data.index[-1] if len(data) > 0 else None
                    )
                
                reports.append(report)
                
            except Exception as e:
                reports.append(DataQualityReport(
                    symbol=symbol,
                    source=source_name,
                    quality='error',
                    error=str(e)
                ))
        
        return reports
    
    def get_best_source(self, symbol: str) -> str:
        """
        获取最适合的数据源
        
        Args:
            symbol: 股票代码
        
        Returns:
            最佳数据源名称
        """
        reports = self.check_quality(symbol)
        
        # 过滤出质量好的数据源
        good_sources = [
            r for r in reports
            if r.quality == 'good' and self._is_source_available(r.source)
        ]
        
        if good_sources:
            # 选择缺失率最低的
            best = min(good_sources, key=lambda r: r.missing_rate)
            return best.source
        
        # 如果没有好的数据源，返回主数据源
        return self.primary
    
    def _get_from_cache(self, key: str) -> Optional[pd.DataFrame]:
        """从缓存获取数据"""
        if not self.enable_cache:
            return None
        
        if key in self._cache:
            data, timestamp = self._cache[key]
            
            # 检查是否过期
            age = (datetime.now() - timestamp).total_seconds()
            
            if age < self.cache_ttl:
                return data
            else:
                # 过期删除
                del self._cache[key]
        
        return None
    
    def _save_to_cache(self, key: str, data: pd.DataFrame) -> None:
        """保存数据到缓存"""
        if not self.enable_cache:
            return
        
        self._cache[key] = (data, datetime.now())
        
        # 清理旧缓存 (保留最近 100 条)
        if len(self._cache) > 100:
            # 按时间排序，删除最旧的
            sorted_items = sorted(
                self._cache.items(),
                key=lambda x: x[1][1]
            )
            
            for i in range(len(self._cache) - 100):
                del self._cache[sorted_items[i][0]]
    
    def _is_source_available(self, source_name: str) -> bool:
        """检查数据源是否可用"""
        return (
            source_name in self.feeds and
            self._source_status.get(source_name, False)
        )
    
    def get_available_sources(self) -> List[str]:
        """
        获取可用的数据源列表
        
        Returns:
            数据源名称列表
        """
        return [
            name for name, feed in self.feeds.items()
            if self._is_source_available(name)
        ]
    
    def clear_cache(self) -> None:
        """清空缓存"""
        self._cache.clear()
        logger.info("数据缓存已清空")


# 便捷函数
def create_data_manager(config: Optional[Dict[str, Any]] = None) -> DataManager:
    """
    创建数据源管理器
    
    Args:
        config: 数据源配置
    
    Returns:
        DataManager 实例
    """
    return DataManager(config)


def load_data(
    symbol: str,
    start_date: str,
    end_date: str,
    source: str = 'auto',
    config: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    便捷函数：加载数据
    
    Args:
        symbol: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        source: 数据源 ('auto'=自动选择)
        config: 数据源配置
    
    Returns:
        OHLCV 数据 DataFrame
    """
    manager = DataManager(config)
    
    if source == 'auto':
        return manager.get_data(symbol, start_date, end_date)
    else:
        return manager.get_data(symbol, start_date, end_date, source=source)
