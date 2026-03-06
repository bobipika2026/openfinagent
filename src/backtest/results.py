"""
回测结果 - 存储和展示回测结果
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime


class BacktestResults:
    """回测结果类"""

    def __init__(self, strategy_name: str, initial_capital: float):
        self.strategy_name = strategy_name
        self.initial_capital = initial_capital
        self.final_capital = initial_capital
        self.trades = []
        self.equity_curve = []
        self.daily_returns = []
        self.metrics = {}

    def add_trade(self, trade: Dict):
        """添加交易记录"""
        self.trades.append(trade)

    def add_equity_point(self, timestamp: datetime, equity: float):
        """添加权益点"""
        self.equity_curve.append({
            'timestamp': timestamp,
            'equity': equity
        })

    def calculate_metrics(self, prices: pd.Series):
        """
        计算回测指标

        Args:
            prices: 价格序列
        """
        if not self.equity_curve:
            return

        equity_df = pd.DataFrame(self.equity_curve)
        equity_df.set_index('timestamp', inplace=True)
        equity_df['daily_return'] = equity_df['equity'].pct_change()

        # 总收益
        total_return = (self.equity_curve[-1]['equity'] / self.initial_capital - 1) * 100

        # 年化收益
        days = (equity_df.index[-1] - equity_df.index[0]).days
        annual_return = ((1 + total_return / 100) ** (365 / days) - 1) * 100 if days > 0 else 0

        # 波动率
        volatility = equity_df['daily_return'].std() * np.sqrt(252) * 100

        # 夏普比率
        risk_free_rate = 0.02  # 假设无风险利率 2%
        sharpe_ratio = (annual_return / 100 - risk_free_rate) / volatility * 100 if volatility > 0 else 0

        # 最大回撤
        equity_df['peak'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['peak']) / equity_df['peak']
        max_drawdown = equity_df['drawdown'].min() * 100

        # 胜率
        winning_trades = sum(1 for t in self.trades if t.get('type') == 'sell' and t.get('revenue', 0) > t.get('cost', 0))
        total_trades = len([t for t in self.trades if t.get('type') == 'sell'])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        self.metrics = {
            '总收益 (%)': round(total_return, 2),
            '年化收益 (%)': round(annual_return, 2),
            '波动率 (%)': round(volatility, 2),
            '夏普比率': round(sharpe_ratio, 2),
            '最大回撤 (%)': round(max_drawdown, 2),
            '交易次数': len(self.trades),
            '胜率 (%)': round(win_rate, 2),
            '初始资金': self.initial_capital,
            '最终资金': round(self.equity_curve[-1]['equity'], 2) if self.equity_curve else self.initial_capital,
        }

        self.final_capital = self.metrics['最终资金']
        self.daily_returns = equity_df['daily_return'].dropna().tolist()

    def show(self):
        """显示回测结果"""
        print("\n" + "=" * 60)
        print(f"📊 {self.strategy_name} 回测结果")
        print("=" * 60)

        for key, value in self.metrics.items():
            if isinstance(value, float):
                print(f"{key:15} {value:15,.2f}")
            else:
                print(f"{key:15} {value:15}")

        print("=" * 60)

        if self.trades:
            print(f"\n最近 5 笔交易:")
            print("-" * 60)
            for trade in self.trades[-5:]:
                timestamp = trade.get('timestamp', '')
                if hasattr(timestamp, 'strftime'):
                    timestamp = timestamp.strftime('%Y-%m-%d')
                trade_type = '买入' if trade.get('type') == 'buy' else '卖出'
                price = trade.get('price', 0)
                shares = trade.get('shares', 0)
                print(f"{timestamp}  {trade_type:4}  价格：{price:8.2f}  数量：{shares:6}")
            print("-" * 60)

    def plot(self):
        """绘制回测结果"""
        try:
            from ..visualization.plotter import StrategyPlotter
            plotter = StrategyPlotter()
            plotter.plot_backtest(self)
        except ImportError:
            print("⚠️  可视化模块未安装，无法绘图")

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'strategy_name': self.strategy_name,
            'metrics': self.metrics,
            'trades': self.trades,
            'equity_curve': self.equity_curve,
        }

    def to_csv(self, filepath: str):
        """保存为 CSV"""
        trades_df = pd.DataFrame(self.trades)
        trades_df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"✅ 交易记录已保存至：{filepath}")
