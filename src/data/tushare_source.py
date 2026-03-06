"""
Tushare 数据源模块 (增强版)

支持 Tushare Pro API 的所有主要功能：
- 日线数据
- 分钟线数据
- 实时行情
- 股票基本信息
- 财务数据
- 指数数据
- 更多...

特性：
- Token 池管理 (多 Token 轮询)
- 本地缓存 (内存 + 磁盘)
- 错误处理 (限流、重试、降级)
- 完整的类型注解
- 详细的中文文档

@module: data.tushare_source
@author: OpenFinAgent Team
@version: 2.0.0
"""

from typing import Optional, Dict, Any, List, Union, Tuple
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
import time
import pandas as pd
import numpy as np

from .tushare_token_manager import TushareTokenManager, get_token_manager
from .tushare_cache import TushareCache, get_cache

logger = logging.getLogger(__name__)


class TushareAPIError(Exception):
    """Tushare API 错误"""
    pass


class TushareRateLimitError(TushareAPIError):
    """Tushare 限流错误"""
    pass


class TushareDataSource:
    """
    Tushare 数据源 (增强版)

    支持多种数据类型的获取，内置缓存和错误处理机制
    """

    # API 限流配置
    RATE_LIMIT_DELAY = 0.1  # 请求间隔 (秒)
    MAX_RETRIES = 3  # 最大重试次数
    RETRY_DELAY = 1.0  # 重试延迟 (秒)

    # 缓存配置
    DEFAULT_CACHE_TTL = 3600  # 默认缓存过期时间 (秒)

    def __init__(
        self,
        token: Optional[str] = None,
        token_manager: Optional[TushareTokenManager] = None,
        cache: Optional[TushareCache] = None,
        use_cache: bool = True,
        rate_limit_delay: float = 0.1,
        max_retries: int = 3
    ):
        """
        初始化 Tushare 数据源

        Args:
            token: Tushare Token (可选，会使用全局管理器)
            token_manager: Token 管理器 (可选)
            cache: 缓存实例 (可选)
            use_cache: 是否使用缓存
            rate_limit_delay: 请求间隔 (秒)
            max_retries: 最大重试次数
        """
        # Token 管理
        if token_manager:
            self.token_manager = token_manager
        else:
            self.token_manager = TushareTokenManager(token=token)

        # 缓存
        self.cache = cache if cache is not None else get_cache()
        self.use_cache = use_cache

        # 限流配置
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self._last_request_time = 0.0

        # Tushare Pro API 实例
        self._pro = None

        logger.info(
            f"Tushare 数据源初始化完成，"
            f"rate_limit={rate_limit_delay}s, max_retries={max_retries}"
        )

    def _get_pro(self):
        """获取 Tushare Pro API 实例"""
        if self._pro is None:
            try:
                import tushare as ts

                token = self.token_manager.get_token()
                if not token:
                    raise TushareAPIError("无法获取 Tushare Token")

                ts.set_token(token)
                self._pro = ts.pro_api()
                logger.info("Tushare Pro API 初始化成功")

            except ImportError:
                logger.error("Tushare 未安装，请运行：pip install tushare")
                raise
            except Exception as e:
                logger.error(f"Tushare Pro API 初始化失败：{e}")
                raise

        return self._pro

    def _rate_limit(self):
        """限流控制"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    def _request_with_retry(
        self,
        api_func: callable,
        api_name: str,
        **kwargs
    ) -> Any:
        """
        带重试的请求

        Args:
            api_func: API 函数
            api_name: API 名称
            **kwargs: API 参数

        Returns:
            API 响应数据
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                # 限流控制
                self._rate_limit()

                # 获取 Token
                token = self.token_manager.get_token()
                if not token:
                    raise TushareAPIError("无法获取 Token")

                # 重新初始化 pro (如果 Token 变化)
                self._pro = None
                pro = self._get_pro()

                # 调用 API
                result = api_func(**kwargs)

                # 重置错误计数
                self.token_manager.reset_token_errors(token)

                return result

            except Exception as e:
                last_error = e
                error_msg = str(e)

                # 记录错误
                token = self.token_manager.get_token()
                if token:
                    self.token_manager.record_error(token)

                # 判断错误类型
                if "权限不够" in error_msg or "积分不够" in error_msg:
                    logger.error(f"权限/积分不足：{api_name}, {kwargs}")
                    raise TushareAPIError(f"权限或积分不足：{error_msg}")

                if "流控" in error_msg or "limit" in error_msg.lower():
                    logger.warning(f"触发限流，等待重试：{api_name}")
                    time.sleep(self.RETRY_DELAY * (attempt + 1))
                    continue

                # 其他错误，重试
                logger.warning(
                    f"API 请求失败 (尝试 {attempt + 1}/{self.max_retries}): "
                    f"{api_name}, 错误：{e}"
                )

                if attempt < self.max_retries - 1:
                    time.sleep(self.RETRY_DELAY * (attempt + 1))
                else:
                    break

        # 所有重试失败
        raise TushareAPIError(f"API 请求失败：{api_name}, 最后错误：{last_error}")

    def _format_date(self, date: Union[str, datetime]) -> str:
        """格式化日期为 Tushare 格式 (YYYYMMDD)"""
        if isinstance(date, datetime):
            return date.strftime('%Y%m%d')
        elif isinstance(date, str):
            # 尝试解析多种格式
            for fmt in ['%Y-%m-%d', '%Y%m%d', '%Y/%m/%d']:
                try:
                    return datetime.strptime(date, fmt).strftime('%Y%m%d')
                except ValueError:
                    continue
            return date.replace('-', '').replace('/', '')
        else:
            raise ValueError(f"不支持的日期格式：{date}")

    def _cache_key(self, api_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """生成缓存参数"""
        return params

    # ==================== 日线数据 ====================

    def get_daily_data(
        self,
        ts_code: str,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        获取日线数据

        Args:
            ts_code: 股票代码 (如 '000001.SZ', '600000.SH')
            start_date: 开始日期
            end_date: 结束日期
            use_cache: 是否使用缓存

        Returns:
            OHLCV DataFrame
        """
        # 格式化日期
        start = self._format_date(start_date)
        end = self._format_date(end_date)

        # 缓存键
        cache_params = {
            'ts_code': ts_code,
            'start_date': start,
            'end_date': end
        }

        # 尝试从缓存获取
        if use_cache and self.use_cache:
            cached = self.cache.get('daily', cache_params)
            if cached is not None:
                logger.info(f"日线数据缓存命中：{ts_code}")
                return cached

        logger.info(f"获取日线数据：{ts_code}, {start} - {end}")

        def fetch():
            pro = self._get_pro()
            return pro.daily(ts_code=ts_code, start_date=start, end_date=end)

        df = self._request_with_retry(fetch, 'daily', **cache_params)

        if df is None or df.empty:
            logger.warning(f"日线数据为空：{ts_code}")
            return pd.DataFrame()

        # 处理数据
        df = self._process_daily_data(df)

        # 缓存
        if self.use_cache:
            self.cache.set('daily', cache_params, df)

        return df

    def _process_daily_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """处理日线数据"""
        # 重命名列
        rename_map = {
            'trade_date': 'date',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'vol': 'volume',
            'amount': 'amount'
        }

        df = df.rename(columns=rename_map)

        # 转换日期
        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        df.set_index('date', inplace=True)

        # 选择 OHLCV 列
        columns = ['open', 'high', 'low', 'close', 'volume']
        df = df[[col for col in columns if col in df.columns]]

        # 转换数据类型
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        return df

    # ==================== 分钟线数据 ====================

    def get_min_data(
        self,
        ts_code: str,
        freq: str = '5min',
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        获取分钟线数据

        Args:
            ts_code: 股票代码
            freq: 频率 ('1min', '5min', '15min', '30min', '60min')
            start_date: 开始日期 (可选，默认最近 5 天)
            end_date: 结束日期 (可选，默认今天)
            use_cache: 是否使用缓存

        Returns:
            分钟线 DataFrame
        """
        # 频率映射
        freq_map = {
            '1min': '1',
            '5min': '5',
            '15min': '15',
            '30min': '30',
            '60min': '60'
        }

        ts_freq = freq_map.get(freq, '5')

        # 默认日期范围
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=5)

        start = self._format_date(start_date)
        end = self._format_date(end_date)

        # 缓存键
        cache_params = {
            'ts_code': ts_code,
            'freq': freq,
            'start_date': start,
            'end_date': end
        }

        # 尝试缓存
        if use_cache and self.use_cache:
            cached = self.cache.get('min', cache_params)
            if cached is not None:
                logger.info(f"分钟线缓存命中：{ts_code}, {freq}")
                return cached

        logger.info(f"获取分钟线数据：{ts_code}, {freq}, {start} - {end}")

        def fetch():
            pro = self._get_pro()
            return pro.bar(
                ts_code=ts_code,
                freq=ts_freq,
                start_date=start,
                end_date=end
            )

        df = self._request_with_retry(fetch, 'bar', **cache_params)

        if df is None or df.empty:
            logger.warning(f"分钟线数据为空：{ts_code}")
            return pd.DataFrame()

        # 处理数据
        df = self._process_min_data(df, freq)

        # 缓存
        if self.use_cache:
            self.cache.set('min', cache_params, df)

        return df

    def _process_min_data(self, df: pd.DataFrame, freq: str) -> pd.DataFrame:
        """处理分钟线数据"""
        # 重命名列
        rename_map = {
            'trade_date': 'date',
            'trade_time': 'time',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'vol': 'volume',
            'amount': 'amount'
        }

        df = df.rename(columns=rename_map)

        # 合并日期和时间
        if 'date' in df.columns and 'time' in df.columns:
            df['datetime'] = df['date'].astype(str) + ' ' + df['time']
            df['datetime'] = pd.to_datetime(df['datetime'])
            df.set_index('datetime', inplace=True)

        # 选择 OHLCV 列
        columns = ['open', 'high', 'low', 'close', 'volume']
        df = df[[col for col in columns if col in df.columns]]

        # 转换数据类型
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        return df

    # ==================== 实时行情 ====================

    def get_realtime_quote(
        self,
        ts_code: str,
        use_cache: bool = False
    ) -> Dict[str, Any]:
        """
        获取实时行情

        Args:
            ts_code: 股票代码
            use_cache: 是否使用缓存 (默认 False，实时数据通常不需要缓存)

        Returns:
            行情字典
        """
        # 缓存键
        cache_params = {'ts_code': ts_code}

        # 尝试缓存
        if use_cache and self.use_cache:
            cached = self.cache.get('quote', cache_params)
            if cached is not None:
                return cached

        logger.info(f"获取实时行情：{ts_code}")

        def fetch():
            pro = self._get_pro()
            return pro.quote(ts_code=ts_code)

        df = self._request_with_retry(fetch, 'quote', **cache_params)

        if df is None or df.empty:
            logger.warning(f"实时行情为空：{ts_code}")
            return {}

        # 转换为字典
        result = df.iloc[0].to_dict()

        # 缓存
        if use_cache and self.use_cache:
            # 实时数据缓存时间短
            self.cache.set('quote', cache_params, result, ttl_seconds=60)

        return result

    def get_realtime_quotes_batch(
        self,
        ts_codes: List[str],
        use_cache: bool = False
    ) -> Dict[str, Dict[str, Any]]:
        """
        批量获取实时行情

        Args:
            ts_codes: 股票代码列表
            use_cache: 是否使用缓存

        Returns:
            行情字典 {ts_code: quote_data}
        """
        results = {}

        for ts_code in ts_codes:
            try:
                quote = self.get_realtime_quote(ts_code, use_cache)
                if quote:
                    results[ts_code] = quote
            except Exception as e:
                logger.error(f"获取行情失败：{ts_code}, 错误：{e}")

        return results

    # ==================== 股票基本信息 ====================

    def get_stock_basic(
        self,
        ts_code: Optional[str] = None,
        exchange: Optional[str] = None,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        获取股票基本信息

        Args:
            ts_code: 股票代码 (可选，不传则获取所有)
            exchange: 交易所 ('SSE'=上交所，'SZSE'=深交所，'BSE'=北交所)
            use_cache: 是否使用缓存

        Returns:
            股票信息 DataFrame
        """
        cache_params = {
            'ts_code': ts_code,
            'exchange': exchange
        }

        # 尝试缓存
        if use_cache and self.use_cache:
            cached = self.cache.get('stock_basic', cache_params)
            if cached is not None:
                return cached

        logger.info(f"获取股票基本信息：{ts_code or 'all'}, {exchange or 'all'}")

        def fetch():
            pro = self._get_pro()
            return pro.stock_basic(
                ts_code=ts_code,
                exchange=exchange,
                fields='ts_code,symbol,name,area,industry,market,list_date'
            )

        df = self._request_with_retry(fetch, 'stock_basic', **cache_params)

        if df is None or df.empty:
            logger.warning(f"股票基本信息为空")
            return pd.DataFrame()

        # 缓存
        if self.use_cache:
            self.cache.set('stock_basic', cache_params, df)

        return df

    def get_stock_info(self, ts_code: str) -> Optional[Dict[str, Any]]:
        """
        获取单只股票详细信息

        Args:
            ts_code: 股票代码

        Returns:
            股票信息字典
        """
        df = self.get_stock_basic(ts_code=ts_code)

        if df.empty:
            return None

        return df.iloc[0].to_dict()

    # ==================== 财务数据 ====================

    def get_income(
        self,
        ts_code: str,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        获取利润表

        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            use_cache: 是否使用缓存

        Returns:
            利润表 DataFrame
        """
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=365)

        start = self._format_date(start_date)
        end = self._format_date(end_date)

        cache_params = {
            'ts_code': ts_code,
            'start_date': start,
            'end_date': end
        }

        if use_cache and self.use_cache:
            cached = self.cache.get('income', cache_params)
            if cached is not None:
                return cached

        logger.info(f"获取利润表：{ts_code}")

        def fetch():
            pro = self._get_pro()
            return pro.income(
                ts_code=ts_code,
                start_date=start,
                end_date=end,
                fields='ts_code,ann_date,end_date,revenue,op,cost_tax,sales_exp,admin_exp,rd_exp,fin_exp,op_profit,total_profit,net_profit'
            )

        df = self._request_with_retry(fetch, 'income', **cache_params)

        if df is None or df.empty:
            return pd.DataFrame()

        if self.use_cache:
            self.cache.set('income', cache_params, df)

        return df

    def get_balance(
        self,
        ts_code: str,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        获取资产负债表

        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            use_cache: 是否使用缓存

        Returns:
            资产负债表 DataFrame
        """
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=365)

        start = self._format_date(start_date)
        end = self._format_date(end_date)

        cache_params = {
            'ts_code': ts_code,
            'start_date': start,
            'end_date': end
        }

        if use_cache and self.use_cache:
            cached = self.cache.get('balance', cache_params)
            if cached is not None:
                return cached

        logger.info(f"获取资产负债表：{ts_code}")

        def fetch():
            pro = self._get_pro()
            return pro.balancesheet(
                ts_code=ts_code,
                start_date=start,
                end_date=end,
                fields='ts_code,ann_date,end_date,total_assets,total_hld_shldr_equity,total_liab'
            )

        df = self._request_with_retry(fetch, 'balancesheet', **cache_params)

        if df is None or df.empty:
            return pd.DataFrame()

        if self.use_cache:
            self.cache.set('balance', cache_params, df)

        return df

    def get_cashflow(
        self,
        ts_code: str,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        获取现金流量表

        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            use_cache: 是否使用缓存

        Returns:
            现金流量表 DataFrame
        """
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=365)

        start = self._format_date(start_date)
        end = self._format_date(end_date)

        cache_params = {
            'ts_code': ts_code,
            'start_date': start,
            'end_date': end
        }

        if use_cache and self.use_cache:
            cached = self.cache.get('cashflow', cache_params)
            if cached is not None:
                return cached

        logger.info(f"获取现金流量表：{ts_code}")

        def fetch():
            pro = self._get_pro()
            return pro.cashflow(
                ts_code=ts_code,
                start_date=start,
                end_date=end,
                fields='ts_code,ann_date,end_date,oper_cash_in,oper_cash_out,invest_cash_in,invest_cash_out'
            )

        df = self._request_with_retry(fetch, 'cashflow', **cache_params)

        if df is None or df.empty:
            return pd.DataFrame()

        if self.use_cache:
            self.cache.set('cashflow', cache_params, df)

        return df

    def get_fina_indicator(
        self,
        ts_code: str,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        获取财务指标

        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            use_cache: 是否使用缓存

        Returns:
            财务指标 DataFrame
        """
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=365)

        start = self._format_date(start_date)
        end = self._format_date(end_date)

        cache_params = {
            'ts_code': ts_code,
            'start_date': start,
            'end_date': end
        }

        if use_cache and self.use_cache:
            cached = self.cache.get('fina_indicator', cache_params)
            if cached is not None:
                return cached

        logger.info(f"获取财务指标：{ts_code}")

        def fetch():
            pro = self._get_pro()
            return pro.fina_indicator(
                ts_code=ts_code,
                start_date=start,
                end_date=end,
                fields='ts_code,ann_date,end_date,eps,roe,roa,pe,pb'
            )

        df = self._request_with_retry(fetch, 'fina_indicator', **cache_params)

        if df is None or df.empty:
            return pd.DataFrame()

        if self.use_cache:
            self.cache.set('fina_indicator', cache_params, df)

        return df

    # ==================== 指数数据 ====================

    def get_index_daily(
        self,
        ts_code: str,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        获取指数日线数据

        Args:
            ts_code: 指数代码 (如 '000001.SH'=上证指数，'399001.SZ'=深证成指)
            start_date: 开始日期
            end_date: 结束日期
            use_cache: 是否使用缓存

        Returns:
            指数日线 DataFrame
        """
        start = self._format_date(start_date)
        end = self._format_date(end_date)

        cache_params = {
            'ts_code': ts_code,
            'start_date': start,
            'end_date': end
        }

        if use_cache and self.use_cache:
            cached = self.cache.get('index_daily', cache_params)
            if cached is not None:
                return cached

        logger.info(f"获取指数日线：{ts_code}, {start} - {end}")

        def fetch():
            pro = self._get_pro()
            return pro.index_daily(ts_code=ts_code, start_date=start, end_date=end)

        df = self._request_with_retry(fetch, 'index_daily', **cache_params)

        if df is None or df.empty:
            logger.warning(f"指数数据为空：{ts_code}")
            return pd.DataFrame()

        # 处理数据
        df = self._process_daily_data(df)

        if self.use_cache:
            self.cache.set('index_daily', cache_params, df)

        return df

    def get_index_basic(
        self,
        ts_code: Optional[str] = None,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        获取指数基本信息

        Args:
            ts_code: 指数代码 (可选)
            use_cache: 是否使用缓存

        Returns:
            指数信息 DataFrame
        """
        cache_params = {'ts_code': ts_code}

        if use_cache and self.use_cache:
            cached = self.cache.get('index_basic', cache_params)
            if cached is not None:
                return cached

        logger.info(f"获取指数基本信息：{ts_code or 'all'}")

        def fetch():
            pro = self._get_pro()
            return pro.index_basic(ts_code=ts_code)

        df = self._request_with_retry(fetch, 'index_basic', **cache_params)

        if df is None or df.empty:
            return pd.DataFrame()

        if self.use_cache:
            self.cache.set('index_basic', cache_params, df)

        return df

    def get_index_member(
        self,
        ts_code: str,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        获取指数成分股

        Args:
            ts_code: 指数代码
            use_cache: 是否使用缓存

        Returns:
            成分股 DataFrame
        """
        cache_params = {'ts_code': ts_code}

        if use_cache and self.use_cache:
            cached = self.cache.get('index_member', cache_params)
            if cached is not None:
                return cached

        logger.info(f"获取指数成分股：{ts_code}")

        def fetch():
            pro = self._get_pro()
            return pro.index_member(ts_code=ts_code)

        df = self._request_with_retry(fetch, 'index_member', **cache_params)

        if df is None or df.empty:
            return pd.DataFrame()

        if self.use_cache:
            self.cache.set('index_member', cache_params, df)

        return df

    # ==================== 其他数据 ====================

    def get_trade_cal(
        self,
        exchange: str = 'SSE',
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        获取交易日历

        Args:
            exchange: 交易所 ('SSE'=上交所，'SZSE'=深交所)
            start_date: 开始日期
            end_date: 结束日期
            use_cache: 是否使用缓存

        Returns:
            交易日历 DataFrame
        """
        if end_date is None:
            end_date = datetime.now() + timedelta(days=30)
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)

        start = self._format_date(start_date)
        end = self._format_date(end_date)

        cache_params = {
            'exchange': exchange,
            'start_date': start,
            'end_date': end
        }

        if use_cache and self.use_cache:
            cached = self.cache.get('trade_cal', cache_params)
            if cached is not None:
                return cached

        logger.info(f"获取交易日历：{exchange}, {start} - {end}")

        def fetch():
            pro = self._get_pro()
            return pro.trade_cal(exchange=exchange, start_date=start, end_date=end)

        df = self._request_with_retry(fetch, 'trade_cal', **cache_params)

        if df is None or df.empty:
            return pd.DataFrame()

        if self.use_cache:
            self.cache.set('trade_cal', cache_params, df)

        return df

    def get_stock_list(
        self,
        exchange: Optional[str] = None,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        获取股票列表

        Args:
            exchange: 交易所 (可选)
            use_cache: 是否使用缓存

        Returns:
            股票列表 DataFrame
        """
        cache_params = {'exchange': exchange}

        if use_cache and self.use_cache:
            cached = self.cache.get('stock_list', cache_params)
            if cached is not None:
                return cached

        logger.info(f"获取股票列表：{exchange or 'all'}")

        def fetch():
            pro = self._get_pro()
            return pro.stock_basic(exchange=exchange, list_status='L')

        df = self._request_with_retry(fetch, 'stock_list', **cache_params)

        if df is None or df.empty:
            return pd.DataFrame()

        if self.use_cache:
            self.cache.set('stock_list', cache_params, df)

        return df

    # ==================== 便捷方法 ====================

    def get_data(
        self,
        symbol: str,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        freq: str = 'D',
        **kwargs
    ) -> pd.DataFrame:
        """
        通用数据获取方法 (兼容基类接口)

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            freq: 频率 ('D'=日线，'1m'=1 分钟等)
            **kwargs: 其他参数

        Returns:
            OHLCV DataFrame
        """
        # 标准化股票代码
        ts_code = self._normalize_ts_code(symbol)

        if freq.upper() == 'D':
            return self.get_daily_data(ts_code, start_date, end_date, **kwargs)
        else:
            # 分钟线
            freq_map = {
                '1m': '1min',
                '5m': '5min',
                '15m': '15min',
                '30m': '30min',
                '60m': '60min'
            }
            min_freq = freq_map.get(freq.lower(), '5min')
            return self.get_min_data(ts_code, freq=min_freq, start_date=start_date, end_date=end_date, **kwargs)

    def _normalize_ts_code(self, symbol: str) -> str:
        """
        标准化股票代码

        Args:
            symbol: 原始股票代码

        Returns:
            标准化代码 (如 '000001.SZ')
        """
        # 如果已经有交易所后缀，直接返回
        if '.' in symbol:
            return symbol.upper()

        # 根据前缀判断交易所
        if symbol.startswith('6'):
            return f"{symbol}.SH"
        elif symbol.startswith('0') or symbol.startswith('3'):
            return f"{symbol}.SZ"
        elif symbol.startswith('4') or symbol.startswith('8'):
            return f"{symbol}.BJ"
        else:
            # 默认深交所
            return f"{symbol}.SZ"

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        return self.cache.get_stats()

    def get_token_stats(self) -> Dict[str, Any]:
        """获取 Token 统计"""
        return self.token_manager.get_stats()

    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        logger.info("缓存已清空")


# ==================== 便捷函数 ====================

def get_tushare_data(
    ts_code: str,
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    freq: str = 'D',
    token: Optional[str] = None,
    use_cache: bool = True
) -> pd.DataFrame:
    """
    便捷函数：获取 Tushare 数据

    Args:
        ts_code: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        freq: 频率
        token: Tushare Token (可选)
        use_cache: 是否使用缓存

    Returns:
        OHLCV DataFrame
    """
    source = TushareDataSource(token=token, use_cache=use_cache)
    return source.get_data(ts_code, start_date, end_date, freq=freq)


def get_daily(
    ts_code: str,
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    **kwargs
) -> pd.DataFrame:
    """便捷函数：获取日线数据"""
    source = TushareDataSource(**kwargs)
    return source.get_daily_data(ts_code, start_date, end_date)


def get_min(
    ts_code: str,
    freq: str = '5min',
    start_date: Optional[Union[str, datetime]] = None,
    end_date: Optional[Union[str, datetime]] = None,
    **kwargs
) -> pd.DataFrame:
    """便捷函数：获取分钟线数据"""
    source = TushareDataSource(**kwargs)
    return source.get_min_data(ts_code, freq=freq, start_date=start_date, end_date=end_date)


def get_quote(ts_code: str, **kwargs) -> Dict[str, Any]:
    """便捷函数：获取实时行情"""
    source = TushareDataSource(**kwargs)
    return source.get_realtime_quote(ts_code)
