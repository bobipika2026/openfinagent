"""
Alpha Vantage 数据源

提供全球市场数据支持 (美股、外汇、加密货币等)

@module: data.alpha_vantage_source
@author: OpenFinAgent Team
@version: 0.4.0
"""

from typing import Optional, Dict, Any, List
import pandas as pd
import requests
from datetime import datetime
import logging

from .sources import DataSource

logger = logging.getLogger(__name__)


class AlphaVantageDataSource(DataSource):
    """
    Alpha Vantage 数据源
    
    支持全球市场数据，包括美股、外汇、加密货币等
    免费账户限制：每分钟 5 次请求，每天 500 次请求
    
    Attributes:
        api_key: API 密钥
        base_url: API 基础 URL
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://www.alphavantage.co/query"):
        """
        初始化 Alpha Vantage 数据源
        
        Args:
            api_key: Alpha Vantage API 密钥 (可从 https://www.alphavantage.co/support/#api-key 免费获取)
            base_url: API 基础 URL
        """
        import os
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY')
        self.base_url = base_url
        
        if not self.api_key:
            raise ValueError(
                "Alpha Vantage API key 未提供，请设置 ALPHA_VANTAGE_API_KEY 环境变量或在初始化时传入"
            )
        
        logger.info("Alpha Vantage 数据源初始化完成")
    
    def get_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        freq: str = 'D'
    ) -> pd.DataFrame:
        """
        获取历史数据
        
        Args:
            symbol: 股票代码 (如 'AAPL', 'IBM')
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            freq: 数据频率 ('D'=日线，'1min'='1 分钟', '5min'='5 分钟', '15min'='15 分钟', '30min'='30 分钟', '60min'='60 分钟')
        
        Returns:
            OHLCV 数据 DataFrame
        
        Raises:
            ValueError: 当 API 密钥无效或数据获取失败时
        """
        try:
            # 根据频率选择 API 函数
            if freq == 'D':
                function = 'TIME_SERIES_DAILY'
                data_key = 'Time Series (Daily)'
            elif freq in ['1min', '5min', '15min', '30min', '60min']:
                function = 'TIME_SERIES_INTRADAY'
                data_key = f'Time Series ({freq})'
            else:
                raise ValueError(f"不支持的频率：{freq}")
            
            # 构建请求参数
            params = {
                'function': function,
                'symbol': symbol,
                'apikey': self.api_key,
                'datatype': 'json',
                'outputsize': 'full'  # 获取全部数据
            }
            
            # 对于分钟线需要指定 interval
            if freq != 'D':
                params['interval'] = freq
            
            logger.info(f"从 Alpha Vantage 获取数据：{symbol}, 频率={freq}")
            
            # 发送请求
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # 检查错误信息
            if 'Error Message' in data:
                raise ValueError(f"Alpha Vantage 错误：{data['Error Message']}")
            
            if 'Note' in data:
                # API 限流提示
                logger.warning(f"Alpha Vantage API 限流：{data['Note']}")
                raise ValueError("API 请求频率超限，请稍后重试")
            
            # 解析数据
            time_series = data.get(data_key, {})
            
            if not time_series:
                logger.warning(f"Alpha Vantage 无数据：{symbol}")
                return pd.DataFrame()
            
            # 转换为 DataFrame
            df_data = []
            for date_str, values in time_series.items():
                try:
                    date = pd.to_datetime(date_str)
                    
                    # 筛选日期范围
                    if start_date and date < pd.to_datetime(start_date):
                        continue
                    if end_date and date > pd.to_datetime(end_date):
                        continue
                    
                    df_data.append({
                        'date': date,
                        'open': float(values.get('1. open', 0)),
                        'high': float(values.get('2. high', 0)),
                        'low': float(values.get('3. low', 0)),
                        'close': float(values.get('4. close', 0)),
                        'volume': int(values.get('5. volume', 0))
                    })
                except (ValueError, KeyError) as e:
                    logger.warning(f"解析数据行失败 {date_str}: {e}")
                    continue
            
            if not df_data:
                return pd.DataFrame()
            
            df = pd.DataFrame(df_data)
            df.set_index('date', inplace=True)
            df.sort_index(inplace=True)
            
            logger.info(f"Alpha Vantage 数据获取成功：{len(df)} 行")
            
            return df[['open', 'high', 'low', 'close', 'volume']]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Alpha Vantage 网络请求失败：{e}")
            raise
        except Exception as e:
            logger.error(f"Alpha Vantage 数据获取失败：{e}")
            raise
    
    def get_realtime(self, symbol: str) -> Dict[str, Any]:
        """
        获取实时行情
        
        Args:
            symbol: 股票代码
        
        Returns:
            实时行情字典，包含 price/open/high/low/volume 等
        """
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            quote = data.get('Global Quote', {})
            
            if not quote:
                return {}
            
            return {
                'symbol': symbol,
                'price': float(quote.get('05. price', 0)),
                'open': float(quote.get('02. open', 0)),
                'high': float(quote.get('03. high', 0)),
                'low': float(quote.get('04. low', 0)),
                'volume': int(quote.get('06. volume', 0)),
                'change': float(quote.get('09. change', 0)),
                'change_percent': quote.get('10. change percent', '0%'),
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"获取实时行情失败：{e}")
            return {}
    
    def get_supported_symbols(self) -> List[str]:
        """
        获取支持的标的列表 (示例)
        
        Returns:
            支持的股票代码列表
        """
        # Alpha Vantage 主要支持美股
        return [
            'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META', 'TSLA',
            'NVDA', 'JPM', 'V', 'JNJ', 'WMT', 'PG',
            'MA', 'UNH', 'HD', 'DIS', 'PYPL', 'BAC',
            'VZ', 'ADBE', 'NFLX', 'CMCSA', 'XOM', 'KO',
            'NKE', 'PFE', 'T', 'MRK', 'PEP', 'INTC'
        ]
    
    def check_quality(self, symbol: str) -> Dict[str, Any]:
        """
        检查数据质量
        
        Args:
            symbol: 股票代码
        
        Returns:
            数据质量报告
        """
        try:
            # 获取最近 30 天数据
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - pd.Timedelta(days=30)).strftime('%Y-%m-%d')
            
            df = self.get_data(symbol, start_date, end_date)
            
            if df.empty:
                return {
                    'symbol': symbol,
                    'quality': 'poor',
                    'missing_rate': 1.0,
                    'last_update': None,
                    'message': '无数据'
                }
            
            # 计算缺失率 (预期约 20-22 个交易日)
            expected_days = 22
            actual_days = len(df)
            missing_rate = max(0, 1 - actual_days / expected_days)
            
            # 检查数据完整性
            has_all_columns = all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume'])
            has_nulls = df.isnull().any().any()
            
            quality = 'good' if missing_rate < 0.1 and has_all_columns and not has_nulls else 'poor'
            
            return {
                'symbol': symbol,
                'quality': quality,
                'missing_rate': missing_rate,
                'last_update': df.index[-1].isoformat() if len(df) > 0 else None,
                'total_records': len(df),
                'has_nulls': has_nulls
            }
            
        except Exception as e:
            logger.error(f"检查数据质量失败：{e}")
            return {
                'symbol': symbol,
                'quality': 'unknown',
                'error': str(e)
            }


def load_alpha_vantage_data(
    symbol: str,
    start_date: str,
    end_date: str,
    api_key: Optional[str] = None,
    freq: str = 'D'
) -> pd.DataFrame:
    """
    便捷函数：从 Alpha Vantage 加载数据
    
    Args:
        symbol: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        api_key: API 密钥
        freq: 数据频率
    
    Returns:
        OHLCV 数据 DataFrame
    """
    source = AlphaVantageDataSource(api_key=api_key)
    return source.get_data(symbol, start_date, end_date, freq=freq)
