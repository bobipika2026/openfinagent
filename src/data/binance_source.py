"""
Binance 数据源模块

支持加密货币数据获取：
- BTC/USDT 等主流币种
- 多时间周期 (1m, 5m, 15m, 1h, 4h, 1d 等)
- 无需 API key (使用公开 API)

@module: data.binance_source
@author: OpenFinAgent Team
@version: 1.0.0
"""

from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import logging
import time

logger = logging.getLogger(__name__)


class BinanceDataSource:
    """
    Binance 数据源 (加密货币)

    使用 Binance 公开 API，无需 API key
    支持多种时间周期和交易对
    """

    # 时间周期映射
    INTERVAL_MAP = {
        '1m': '1m',
        '3m': '3m',
        '5m': '5m',
        '15m': '15m',
        '30m': '30m',
        '1h': '1h',
        '2h': '2h',
        '4h': '4h',
        '6h': '6h',
        '12h': '12h',
        '1d': '1d',
        '3d': '3d',
        '1w': '1w',
        '1M': '1M'
    }

    def __init__(
        self,
        base_url: str = 'https://api.binance.com',
        rate_limit_delay: float = 0.1
    ):
        """
        初始化

        Args:
            base_url: Binance API 基础 URL
            rate_limit_delay: 请求间隔 (秒)，避免触发限流
        """
        self.base_url = base_url
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time = 0

        logger.info(f"Binance 数据源初始化完成：{base_url}")

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
        """
        发送 HTTP 请求 (带限流控制)

        Args:
            endpoint: API 端点
            params: 请求参数

        Returns:
            JSON 响应或 None
        """
        import requests

        # 限流控制
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)

        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, params=params, timeout=30)
            self._last_request_time = time.time()

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Binance API 错误：{response.status_code} - {response.text}")
                return None

        except requests.RequestException as e:
            logger.error(f"Binance API 请求失败：{e}")
            return None

    def get_klines(
        self,
        symbol: str,
        interval: str,
        start_date: str,
        end_date: str,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        获取 K 线数据

        Args:
            symbol: 交易对 (如 'BTCUSDT', 'ETHUSDT')
            interval: 时间周期 (1m, 5m, 1h, 1d 等)
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            limit: 单次请求最大条数 (最大 1000)

        Returns:
            OHLCV 数据 DataFrame
        """
        # 验证时间周期
        if interval not in self.INTERVAL_MAP:
            raise ValueError(f"不支持的时间周期：{interval}")

        # 标准化交易对 (移除分隔符)
        clean_symbol = symbol.replace('/', '').replace('_', '').upper()
        
        # 转换日期为时间戳
        start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
        end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)

        logger.info(f"从 Binance 获取数据：{clean_symbol}, {interval}, {start_date} - {end_date}")

        all_klines = []
        current_start = start_ts
        max_retries = 3
        retry_count = 0

        # 分页获取数据
        while current_start < end_ts and retry_count < max_retries:
            params = {
                'symbol': clean_symbol,
                'interval': self.INTERVAL_MAP[interval],
                'startTime': current_start,
                'endTime': end_ts,
                'limit': limit
            }

            logger.debug(f"Binance API 请求参数：{params}")
            klines = self._make_request('/api/v3/klines', params)

            if not klines:
                logger.warning(f"Binance API 返回空数据：{clean_symbol}, {interval}")
                retry_count += 1
                time.sleep(1.0)  # 重试前等待
                continue

            if len(klines) == 0:
                logger.warning(f"Binance 无数据：{clean_symbol}, {interval}")
                break

            all_klines.extend(klines)
            logger.debug(f"获取到 {len(klines)} 条 K 线数据，累计 {len(all_klines)} 条")

            # 更新起始时间 (最后一条 K 线的时间 + 1ms)
            current_start = klines[-1][0] + 1

            # 避免无限循环
            if len(klines) < limit:
                break

            # 延迟避免限流
            time.sleep(self.rate_limit_delay)

        if not all_klines:
            logger.warning(f"Binance 最终未获取到任何数据：{clean_symbol}, {interval}")
            return pd.DataFrame()

        # 转换为 DataFrame
        df = self._parse_klines(all_klines)

        logger.info(f"Binance 数据获取成功：{len(df)} 行")
        return df

    def _parse_klines(self, klines: List[List]) -> pd.DataFrame:
        """
        解析 K 线数据

        Args:
            klines: Binance K 线数据列表

        Returns:
            OHLCV DataFrame
        """
        columns = [
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ]

        df = pd.DataFrame(klines, columns=columns)

        # 转换数据类型
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        # 转换数值列
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # 选择 OHLCV 列
        df = df[numeric_cols]

        return df

    def get_historical_data(
        self,
        symbol: str,
        interval: str = '1d',
        days: int = 365
    ) -> pd.DataFrame:
        """
        获取历史数据 (便捷方法)

        Args:
            symbol: 交易对
            interval: 时间周期
            days: 获取天数

        Returns:
            OHLCV DataFrame
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.get_klines(
            symbol=symbol,
            interval=interval,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )

    def get_available_symbols(self) -> List[str]:
        """
        获取可用交易对列表

        Returns:
            交易对列表
        """
        response = self._make_request('/api/v3/exchangeInfo', {})

        if not response:
            return []

        symbols = []
        for item in response.get('symbols', []):
            if item.get('status') == 'TRADING':
                symbols.append(item['symbol'])

        logger.info(f"获取到 {len(symbols)} 个可用交易对")
        return symbols

    def get_ticker_price(self, symbol: str) -> Optional[float]:
        """
        获取当前价格

        Args:
            symbol: 交易对

        Returns:
            当前价格或 None
        """
        clean_symbol = symbol.replace('/', '').replace('_', '').upper()
        
        response = self._make_request(
            '/api/v3/ticker/price',
            {'symbol': clean_symbol}
        )

        if response and 'price' in response:
            return float(response['price'])
        
        return None


def get_binance_data(
    symbol: str,
    interval: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """
    便捷函数：从 Binance 获取数据

    Args:
        symbol: 交易对 (如 'BTC/USDT')
        interval: 时间周期
        start_date: 开始日期
        end_date: 结束日期

    Returns:
        OHLCV DataFrame
    """
    source = BinanceDataSource()
    return source.get_klines(symbol, interval, start_date, end_date)
