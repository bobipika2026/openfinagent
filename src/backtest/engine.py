"""
回测引擎 - 执行策略回测
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict
from datetime import datetime
from tqdm import tqdm

from backtest.results import BacktestResults
from strategy.base import BaseStrategy


class BacktestEngine:
    """回测引擎"""

    def __init__(self, commission_rate: float = 0.0003, slippage: float = 0.001):
        """
        初始化回测引擎

        Args:
            commission_rate: 手续费率 (默认万分之三)
            slippage: 滑点 (默认 0.1%)
        """
        self.commission_rate = commission_rate
        self.slippage = slippage

    def run(self, strategy: BaseStrategy, data: pd.DataFrame,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
            show_progress: bool = True) -> BacktestResults:
        """
        运行回测

        Args:
            strategy: 策略实例
            data: 市场数据 DataFrame
            start_date: 开始日期
            end_date: 结束日期
            show_progress: 显示进度条

        Returns:
            回测结果
        """
        # 重置策略状态
        strategy.reset()

        # 筛选日期范围
        if start_date:
            data = data[data.index >= start_date]
        if end_date:
            data = data[data.index <= end_date]

        if len(data) == 0:
            raise ValueError("筛选后无数据，请检查日期范围")

        # 初始化结果
        results = BacktestResults(strategy.name, strategy.initial_capital)

        # 运行回测
        iterator = tqdm(range(len(data)), desc="回测中", ncols=80) if show_progress else range(len(data))

        for i in iterator:
            # 获取交易信号
            trade_order = strategy.on_bar(data, i)

            if trade_order:
                # 执行交易
                price = trade_order['price']
                shares = trade_order['shares']
                action = trade_order['action']

                # 应用滑点
                if action == 'buy':
                    exec_price = price * (1 + self.slippage)
                else:
                    exec_price = price * (1 - self.slippage)

                # 计算手续费
                commission = exec_price * shares * self.commission_rate

                # 执行交易
                if action == 'buy':
                    total_cost = exec_price * shares + commission
                    if total_cost <= strategy.cash:
                        strategy.cash -= total_cost
                        strategy.positions['shares'] = strategy.positions.get('shares', 0) + shares
                        results.add_trade({
                            'timestamp': trade_order['timestamp'],
                            'type': 'buy',
                            'price': exec_price,
                            'shares': shares,
                            'commission': commission,
                            'cost': total_cost
                        })
                else:  # sell
                    if strategy.positions.get('shares', 0) >= shares:
                        revenue = exec_price * shares - commission
                        strategy.cash += revenue
                        strategy.positions['shares'] -= shares
                        results.add_trade({
                            'timestamp': trade_order['timestamp'],
                            'type': 'sell',
                            'price': exec_price,
                            'shares': shares,
                            'commission': commission,
                            'revenue': revenue
                        })

            # 记录权益
            current_price = data['close'].iloc[i]
            portfolio_value = strategy.cash + strategy.positions.get('shares', 0) * current_price
            results.add_equity_point(data.index[i], portfolio_value)

        # 计算指标
        results.calculate_metrics(data['close'])

        return results

    def run_multi(self, strategies: list, data: pd.DataFrame,
                  start_date: Optional[str] = None,
                  end_date: Optional[str] = None) -> Dict[str, BacktestResults]:
        """
        运行多个策略回测

        Args:
            strategies: 策略列表
            data: 市场数据
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            策略名称到结果的映射
        """
        results = {}
        for strategy in strategies:
            print(f"\n🔄 回测策略：{strategy.name}")
            result = self.run(strategy, data, start_date, end_date)
            results[strategy.name] = result
        return results


def load_data(symbol: str, start_date: str, end_date: str, source: str = 'akshare') -> pd.DataFrame:
    """
    加载市场数据

    Args:
        symbol: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        source: 数据源 (akshare/yfinance)

    Returns:
        DataFrame with OHLCV data
    """
    try:
        if source == 'akshare':
            # A 股数据
            import akshare as ak
            df = ak.stock_zh_a_hist(
                symbol=symbol.replace('.SH', '').replace('.SZ', ''),
                period="daily",
                start_date=start_date.replace('-', ''),
                end_date=end_date.replace('-', ''),
                adjust="qfq"
            )
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount'
            })
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

        elif source == 'yfinance':
            # 美股数据
            import yfinance as yf
            df = yf.download(symbol, start=start_date, end=end_date)
            df.columns = df.columns.str.lower()

        elif source == 'mock':
            # 模拟数据
            return generate_mock_data(start_date, end_date)

        else:
            raise ValueError(f"未知数据源：{source}")

        return df[['open', 'high', 'low', 'close', 'volume']]

    except Exception as e:
        print(f"⚠️  数据加载失败：{e}")
        print("📝 使用模拟数据...")
        return generate_mock_data(start_date, end_date)


def generate_mock_data(start_date: str, end_date: str, initial_price: float = 100.0) -> pd.DataFrame:
    """
    生成模拟数据用于测试

    Args:
        start_date: 开始日期
        end_date: 结束日期
        initial_price: 初始价格

    Returns:
        模拟数据 DataFrame
    """
    dates = pd.date_range(start=start_date, end=end_date, freq='B')  # 工作日
    n_days = len(dates)

    # 生成随机价格序列 (几何布朗运动)
    np.random.seed(42)
    returns = np.random.normal(0.0005, 0.02, n_days)  # 日均收益 0.05%, 波动 2%
    prices = initial_price * np.cumprod(1 + returns)

    # 生成 OHLCV
    df = pd.DataFrame(index=dates)
    df['close'] = prices
    df['open'] = prices * (1 + np.random.uniform(-0.01, 0.01, n_days))
    df['high'] = df[['open', 'close']].max(axis=1) * (1 + np.random.uniform(0, 0.02, n_days))
    df['low'] = df[['open', 'close']].min(axis=1) * (1 - np.random.uniform(0, 0.02, n_days))
    df['volume'] = np.random.randint(1000000, 10000000, n_days)

    return df
