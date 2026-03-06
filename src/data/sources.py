"""
数据源模块

支持多种数据源：
- AkShare (A 股)
- Yahoo Finance (美股)
- Tushare (A 股，需要 API key)
- 本地 CSV 文件
- 模拟数据

@module: data.sources
@author: OpenFinAgent Team
@version: 1.0.0
"""

from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class DataSource(ABC):
    """数据源基类"""

    @abstractmethod
    def get_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        获取数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            OHLCV 数据 DataFrame
        """
        pass


class AkShareDataSource(DataSource):
    """
    AkShare 数据源 (A 股)

    免费 A 股数据源，无需 API key
    """

    def __init__(self, adjust: str = 'qfq'):
        """
        初始化

        Args:
            adjust: 复权类型 ('qfq'=前复权，'hfq'=后复权，''=不复权)
        """
        self.adjust = adjust

    def get_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        获取 A 股数据

        Args:
            symbol: 股票代码 (如 '000001' 或 '000001.SZ')
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            OHLCV 数据 DataFrame
        """
        try:
            import akshare as ak

            # 清理股票代码
            clean_symbol = symbol.replace('.SH', '').replace('.SZ', '')

            # 格式化日期
            start = start_date.replace('-', '')
            end = end_date.replace('-', '')

            logger.info(f"从 AkShare 获取数据：{clean_symbol}, {start} - {end}")

            df = ak.stock_zh_a_hist(
                symbol=clean_symbol,
                period="daily",
                start_date=start,
                end_date=end,
                adjust=self.adjust
            )

            # 重命名列
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'change_pct',
                '涨跌额': 'change',
                '换手率': 'turnover'
            })

            # 转换日期
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

            # 选择 OHLCV 列
            columns = ['open', 'high', 'low', 'close', 'volume']
            df = df[[col for col in columns if col in df.columns]]

            logger.info(f"AkShare 数据获取成功：{len(df)} 行")
            return df

        except ImportError:
            logger.error("AkShare 未安装，请运行：pip install akshare")
            raise
        except Exception as e:
            logger.error(f"AkShare 数据获取失败：{e}")
            raise


class YahooFinanceDataSource(DataSource):
    """
    Yahoo Finance 数据源 (美股/港股)
    """

    def get_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        获取美股数据

        Args:
            symbol: 股票代码 (如 'AAPL', '0700.HK')
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            OHLCV 数据 DataFrame
        """
        try:
            import yfinance as yf

            logger.info(f"从 Yahoo Finance 获取数据：{symbol}")

            df = yf.download(symbol, start=start_date, end=end_date, progress=False)

            if df.empty:
                logger.warning(f"Yahoo Finance 无数据：{symbol}")
                return pd.DataFrame()

            # 处理 MultiIndex 列
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # 标准化列名
            df.columns = df.columns.str.lower()

            # 重命名列
            rename_map = {
                'adj close': 'close',
                'volume': 'volume'
            }
            df = df.rename(columns=rename_map)

            logger.info(f"Yahoo Finance 数据获取成功：{len(df)} 行")
            return df

        except ImportError:
            logger.error("yfinance 未安装，请运行：pip install yfinance")
            raise
        except Exception as e:
            logger.error(f"Yahoo Finance 数据获取失败：{e}")
            raise


class TushareDataSource(DataSource):
    """
    Tushare 数据源 (A 股)

    需要 API token，可在 tushare.pro 注册获取
    支持日线、分钟线数据
    """

    def __init__(
        self,
        token: Optional[str] = None,
        freq: str = 'D'
    ):
        """
        初始化

        Args:
            token: Tushare API token
            freq: 数据频率 ('D'=日线，'1m'=1 分钟，'5m'=5 分钟等)
        """
        import os
        self.token = token or os.getenv('TUSHARE_TOKEN')
        self.freq = freq

        if not self.token:
            raise ValueError(
                "Tushare token 未提供，请设置 TUSHARE_TOKEN 环境变量或在初始化时传入"
            )

    def get_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        获取 A 股数据

        Args:
            symbol: 股票代码 (如 '000001.SZ')
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            OHLCV 数据 DataFrame
        """
        try:
            import tushare as ts

            # 初始化
            ts.set_token(self.token)
            pro = ts.pro_api()

            # 格式化日期
            start = start_date.replace('-', '')
            end = end_date.replace('-', '')

            logger.info(f"从 Tushare 获取数据：{symbol}, 频率={self.freq}")

            # 根据频率选择 API
            if self.freq == 'D':
                # 日线数据
                df = pro.daily(
                    ts_code=symbol,
                    start_date=start,
                    end_date=end
                )
            elif self.freq in ['1m', '5m', '15m', '30m', '60m']:
                # 分钟线数据
                df = self._get_min_data(pro, symbol, start, end)
            else:
                raise ValueError(f"不支持的频率：{self.freq}")

            if df.empty:
                logger.warning(f"Tushare 无数据：{symbol}")
                return pd.DataFrame()

            # 重命名列
            df = df.rename(columns={
                'trade_date': 'date',
                'trade_time': 'time',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'vol': 'volume',
                'amount': 'amount'
            })

            # 转换日期
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                if 'time' in df.columns:
                    # 分钟线需要合并日期和时间
                    df['datetime'] = df['date'].dt.strftime('%Y-%m-%d') + ' ' + df['time']
                    df['datetime'] = pd.to_datetime(df['datetime'])
                    df.set_index('datetime', inplace=True)
                else:
                    df.set_index('date', inplace=True)

            # 选择 OHLCV 列
            columns = ['open', 'high', 'low', 'close', 'volume']
            df = df[[col for col in columns if col in df.columns]]

            logger.info(f"Tushare 数据获取成功：{len(df)} 行")
            return df

        except ImportError:
            logger.error("Tushare 未安装，请运行：pip install tushare")
            raise
        except Exception as e:
            logger.error(f"Tushare 数据获取失败：{e}")
            raise

    def _get_min_data(
        self,
        pro: Any,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        获取分钟线数据

        Args:
            pro: Tushare pro API 实例
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            分钟线 DataFrame
        """
        # 映射频率到 Tushare 周期
        freq_map = {
            '1m': '1',
            '5m': '5',
            '15m': '15',
            '30m': '30',
            '60m': '60'
        }

        ts_freq = freq_map.get(self.freq, '5')

        # 获取分钟线数据
        df = pro.bar(
            ts_code=symbol,
            freq=ts_freq,
            start_date=start_date,
            end_date=end_date
        )

        return df


class CSVDataSource(DataSource):
    """
    本地 CSV 文件数据源
    """

    def __init__(self, data_dir: str):
        """
        初始化

        Args:
            data_dir: CSV 文件目录
        """
        self.data_dir = data_dir

    def get_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        从 CSV 文件加载数据

        Args:
            symbol: 股票代码 (文件名)
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            OHLCV 数据 DataFrame
        """
        from pathlib import Path

        # 尝试不同格式的文件名
        possible_files = [
            Path(self.data_dir) / f'{symbol}.csv',
            Path(self.data_dir) / f'{symbol.replace(".", "_")}.csv',
            Path(self.data_dir) / f'{symbol.replace(".", "")}.csv',
        ]

        file_path = None
        for path in possible_files:
            if path.exists():
                file_path = path
                break

        if file_path is None:
            raise FileNotFoundError(f"未找到股票 {symbol} 的 CSV 文件")

        logger.info(f"从 CSV 加载数据：{file_path}")

        # 读取 CSV
        df = pd.read_csv(file_path)

        # 尝试识别日期列
        date_cols = ['date', 'Date', 'DATE', 'datetime', 'time']
        date_col = None
        for col in date_cols:
            if col in df.columns:
                date_col = col
                break

        if date_col:
            df[date_col] = pd.to_datetime(df[date_col])
            df.set_index(date_col, inplace=True)

        # 筛选日期范围
        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]

        logger.info(f"CSV 数据加载成功：{len(df)} 行")
        return df


class MockDataSource(DataSource):
    """
    模拟数据源 (用于测试)
    """

    def __init__(
        self,
        initial_price: float = 100.0,
        volatility: float = 0.02,
        drift: float = 0.0005,
        seed: Optional[int] = 42
    ):
        """
        初始化

        Args:
            initial_price: 初始价格
            volatility: 日波动率
            drift: 日漂移 (预期收益)
            seed: 随机种子
        """
        self.initial_price = initial_price
        self.volatility = volatility
        self.drift = drift
        self.seed = seed

    def get_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        生成模拟数据

        Args:
            symbol: 股票代码 (仅用于日志)
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            OHLCV 数据 DataFrame
        """
        logger.info(f"生成模拟数据：{symbol}, {start_date} - {end_date}")

        # 生成日期序列
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        n_days = len(dates)

        if n_days == 0:
            return pd.DataFrame()

        # 设置随机种子
        if self.seed is not None:
            np.random.seed(self.seed)

        # 生成价格序列 (几何布朗运动)
        returns = np.random.normal(self.drift, self.volatility, n_days)
        prices = self.initial_price * np.cumprod(1 + returns)

        # 生成 OHLCV
        df = pd.DataFrame(index=dates)
        df['close'] = prices
        df['open'] = prices * (1 + np.random.uniform(-0.01, 0.01, n_days))
        df['high'] = df[['open', 'close']].max(axis=1) * (1 + np.random.uniform(0, 0.02, n_days))
        df['low'] = df[['open', 'close']].min(axis=1) * (1 - np.random.uniform(0, 0.02, n_days))
        df['volume'] = np.random.randint(1000000, 10000000, n_days)

        logger.info(f"模拟数据生成成功：{len(df)} 行")
        return df


def get_data_source(source_type: str, **kwargs) -> DataSource:
    """
    工厂函数：获取数据源实例

    Args:
        source_type: 数据源类型 ('akshare', 'yfinance', 'tushare', 'csv', 'mock')
        **kwargs: 数据源特定参数

    Returns:
        数据源实例
    """
    sources = {
        'akshare': AkShareDataSource,
        'yfinance': YahooFinanceDataSource,
        'tushare': TushareDataSource,
        'csv': CSVDataSource,
        'mock': MockDataSource
    }

    if source_type not in sources:
        raise ValueError(f"未知数据源类型：{source_type}")

    return sources[source_type](**kwargs)


def load_data_from_source(
    source_type: str,
    symbol: str,
    start_date: str,
    end_date: str,
    **kwargs
) -> pd.DataFrame:
    """
    便捷函数：从指定数据源加载数据

    Args:
        source_type: 数据源类型
        symbol: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        **kwargs: 数据源特定参数

    Returns:
        OHLCV 数据 DataFrame
    """
    source = get_data_source(source_type, **kwargs)
    return source.get_data(symbol, start_date, end_date)
