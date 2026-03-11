"""
评估指标计算模块

提供回测评估所需的各类指标计算功能，包括收益率、夏普比率、最大回撤、
Calmar 比率、胜率、盈亏比等核心指标。
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class Trade:
    """交易记录数据结构"""
    timestamp: pd.Timestamp
    trade_type: str  # 'buy' or 'sell'
    price: float
    shares: int
    cost: float
    revenue: float
    pnl: float = 0.0

    def __post_init__(self):
        """计算盈亏"""
        if self.trade_type == 'sell':
            self.pnl = self.revenue - self.cost


class EvaluationMetrics:
    """
    评估指标计算器

    提供证券行业标准的回测评估指标计算，包括收益、风险、稳定性等维度。
    所有计算均符合金融行业规范。
    """

    def __init__(self, risk_free_rate: float = 0.02):
        """
        初始化评估指标计算器

        Args:
            risk_free_rate: 无风险利率，默认 2% (中国国债收益率参考值)
        """
        self.risk_free_rate = risk_free_rate

    def total_return(self, data: pd.DataFrame) -> float:
        """
        计算总收益率

        Args:
            data: 包含'equity'列的 DataFrame，表示权益曲线

        Returns:
            总收益率 (百分比形式，如 50.5 表示 50.5%)

        Example:
            >>> data = pd.DataFrame({'equity': [100, 110, 120, 150]})
            >>> metrics = EvaluationMetrics()
            >>> metrics.total_return(data)
            50.0
        """
        if data.empty or 'equity' not in data.columns:
            return 0.0

        initial_equity = data['equity'].iloc[0]
        final_equity = data['equity'].iloc[-1]

        if initial_equity <= 0:
            return 0.0

        return (final_equity / initial_equity - 1) * 100

    def annualized_return(self, data: pd.DataFrame) -> float:
        """
        计算年化收益率

        Args:
            data: 包含'equity'列和 datetime index 的 DataFrame

        Returns:
            年化收益率 (百分比形式)
        """
        if data.empty or 'equity' not in data.columns:
            return 0.0

        total_return = self.total_return(data) / 100

        if isinstance(data.index, pd.DatetimeIndex):
            days = (data.index[-1] - data.index[0]).days
        else:
            days = len(data) - 1

        if days <= 0:
            return 0.0

        annualized = (1 + total_return) ** (365 / days) - 1
        return annualized * 100

    def sharpe_ratio(self, returns: pd.Series) -> float:
        """
        计算夏普比率

        夏普比率 = (年化收益率 - 无风险利率) / 年化波动率

        Args:
            returns: 收益率序列 (日收益率)

        Returns:
            夏普比率

        Example:
            >>> returns = pd.Series([0.01, -0.005, 0.02, 0.015])
            >>> metrics = EvaluationMetrics()
            >>> metrics.sharpe_ratio(returns)
            1.23  # 示例值
        """
        if returns.empty or returns.std() == 0:
            return 0.0

        # 年化收益率
        annual_return = returns.mean() * 252

        # 年化波动率
        annual_volatility = returns.std() * np.sqrt(252)

        if annual_volatility == 0:
            return 0.0

        sharpe = (annual_return - self.risk_free_rate) / annual_volatility
        return round(sharpe, 3)

    def max_drawdown(self, equity: pd.Series) -> float:
        """
        计算最大回撤

        最大回撤表示从历史最高点下跌的最大幅度，是重要的风险指标。

        Args:
            equity: 权益曲线序列

        Returns:
            最大回撤 (百分比形式，如 -15.5 表示最大回撤 15.5%)

        Example:
            >>> equity = pd.Series([100, 110, 105, 120, 115, 130])
            >>> metrics = EvaluationMetrics()
            >>> metrics.max_drawdown(equity)
            -4.55  # 从 110 跌到 105
        """
        if equity.empty:
            return 0.0

        # 计算累计最大值
        peak = equity.cummax()

        # 计算回撤
        drawdown = (equity - peak) / peak * 100

        return round(drawdown.min(), 2)

    def calmar_ratio(self, returns: pd.Series, max_dd: float) -> float:
        """
        计算 Calmar 比率

        Calmar 比率 = 年化收益率 / |最大回撤|
        用于衡量风险调整后的收益表现

        Args:
            returns: 收益率序列
            max_dd: 最大回撤 (百分比形式，如 -15.5)

        Returns:
            Calmar 比率

        Example:
            >>> returns = pd.Series([0.01, 0.015, 0.02])
            >>> metrics = EvaluationMetrics()
            >>> metrics.calmar_ratio(returns, -15.5)
            2.5  # 示例值
        """
        if max_dd >= 0:
            return 0.0

        annual_return = self.annualized_return_from_series(returns)

        if annual_return <= 0:
            return 0.0

        calmar = annual_return / abs(max_dd)
        return round(calmar, 3)

    def annualized_return_from_series(self, returns: pd.Series) -> float:
        """
        从收益率序列计算年化收益率

        Args:
            returns: 日收益率序列

        Returns:
            年化收益率 (百分比形式)
        """
        if returns.empty:
            return 0.0

        return returns.mean() * 252 * 100

    def win_rate(self, trades: List[Trade]) -> float:
        """
        计算胜率

        胜率 = 盈利交易数 / 总交易数

        Args:
            trades: 交易记录列表

        Returns:
            胜率 (百分比形式)

        Example:
            >>> trades = [
            ...     Trade(timestamp=pd.Timestamp('2024-01-01'), trade_type='sell',
            ...           price=100, shares=100, cost=10000, revenue=11000, pnl=1000),
            ...     Trade(timestamp=pd.Timestamp('2024-01-02'), trade_type='sell',
            ...           price=100, shares=100, cost=10000, revenue=9500, pnl=-500)
            ... ]
            >>> metrics = EvaluationMetrics()
            >>> metrics.win_rate(trades)
            50.0
        """
        if not trades:
            return 0.0

        # 只统计卖出交易 (完整的交易)
        sell_trades = [t for t in trades if t.trade_type == 'sell']

        if not sell_trades:
            return 0.0

        winning_trades = sum(1 for t in sell_trades if t.pnl > 0)
        win_rate = (winning_trades / len(sell_trades)) * 100

        return round(win_rate, 2)

    def profit_factor(self, trades: List[Trade]) -> float:
        """
        计算盈亏比

        盈亏比 = 总盈利 / |总亏损|

        Args:
            trades: 交易记录列表

        Returns:
            盈亏比

        Example:
            >>> trades = [
            ...     Trade(timestamp=pd.Timestamp('2024-01-01'), trade_type='sell',
            ...           price=100, shares=100, cost=10000, revenue=12000, pnl=2000),
            ...     Trade(timestamp=pd.Timestamp('2024-01-02'), trade_type='sell',
            ...           price=100, shares=100, cost=10000, revenue=9000, pnl=-1000)
            ... ]
            >>> metrics = EvaluationMetrics()
            >>> metrics.profit_factor(trades)
            2.0
        """
        if not trades:
            return 0.0

        # 只统计卖出交易
        sell_trades = [t for t in trades if t.trade_type == 'sell']

        if not sell_trades:
            return 0.0

        total_profit = sum(t.pnl for t in sell_trades if t.pnl > 0)
        total_loss = abs(sum(t.pnl for t in sell_trades if t.pnl < 0))

        if total_loss == 0:
            return float('inf') if total_profit > 0 else 0.0

        return round(total_profit / total_loss, 3)

    def monthly_volatility(self, equity: pd.Series) -> float:
        """
        计算月度收益标准差 (稳定性指标)

        Args:
            equity: 权益曲线序列

        Returns:
            月度收益标准差 (百分比形式)
        """
        if equity.empty or len(equity) < 2:
            return 0.0

        # 计算日收益率
        daily_returns = equity.pct_change().dropna()

        if daily_returns.empty:
            return 0.0

        # 转换为月度收益率
        monthly_returns = daily_returns.resample('ME').apply(lambda x: (1 + x).prod() - 1)

        if len(monthly_returns) < 2:
            return daily_returns.std() * np.sqrt(21) * 100

        return round(monthly_returns.std() * 100, 3)

    def sortino_ratio(self, returns: pd.Series) -> float:
        """
        计算索提诺比率

        索提诺比率只考虑下行波动率，更适合评估下行风险

        Args:
            returns: 收益率序列

        Returns:
            索提诺比率
        """
        if returns.empty:
            return 0.0

        annual_return = returns.mean() * 252

        # 只计算负收益的标准差 (下行波动率)
        downside_returns = returns[returns < 0]

        if downside_returns.empty or downside_returns.std() == 0:
            return 0.0

        downside_deviation = downside_returns.std() * np.sqrt(252)

        sortino = (annual_return - self.risk_free_rate) / downside_deviation
        return round(sortino, 3)

    def calculate_all_metrics(self, data: pd.DataFrame, trades: List[Trade]) -> Dict:
        """
        计算所有评估指标

        Args:
            data: 包含'equity'列的 DataFrame
            trades: 交易记录列表

        Returns:
            包含所有指标的字典
        """
        if data.empty or 'equity' not in data.columns:
            return {}

        equity = data['equity']
        returns = equity.pct_change().dropna()

        max_dd = self.max_drawdown(equity)

        return {
            'total_return': self.total_return(data),
            'annualized_return': self.annualized_return(data),
            'sharpe_ratio': self.sharpe_ratio(returns),
            'max_drawdown': max_dd,
            'calmar_ratio': self.calmar_ratio(returns, max_dd),
            'win_rate': self.win_rate(trades),
            'profit_factor': self.profit_factor(trades),
            'monthly_volatility': self.monthly_volatility(equity),
            'sortino_ratio': self.sortino_ratio(returns),
        }
