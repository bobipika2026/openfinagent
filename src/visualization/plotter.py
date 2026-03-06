"""
策略绘图器 - 可视化回测结果
"""

import pandas as pd
import numpy as np
from typing import Optional
from datetime import datetime


class StrategyPlotter:
    """策略可视化工具"""

    def __init__(self, style: str = 'default'):
        """
        初始化绘图器

        Args:
            style: 图表风格
        """
        self.style = style
        self._setup_matplotlib()

    def _setup_matplotlib(self):
        """配置 matplotlib"""
        try:
            import matplotlib
            matplotlib.use('Agg')  # 非交互式后端
            import matplotlib.pyplot as plt
            plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']  # 支持中文
            plt.rcParams['axes.unicode_minus'] = False  # 支持负号
        except ImportError:
            pass

    def plot_backtest(self, results, save_path: Optional[str] = None):
        """
        绘制回测结果

        Args:
            results: BacktestResults 实例
            save_path: 保存路径
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("⚠️  matplotlib 未安装，无法绘图")
            return

        if not results.equity_curve:
            print("⚠️  无权益曲线数据")
            return

        # 创建图表
        fig, axes = plt.subplots(3, 1, figsize=(14, 10))
        fig.suptitle(f'{results.strategy_name} - 回测分析', fontsize=16, fontweight='bold')

        # 转换数据
        equity_df = pd.DataFrame(results.equity_curve)
        equity_df.set_index('timestamp', inplace=True)

        # 1. 权益曲线
        ax1 = axes[0]
        ax1.plot(equity_df.index, equity_df['equity'], linewidth=2, color='#2E86AB')
        ax1.axhline(y=results.initial_capital, color='gray', linestyle='--', alpha=0.5, label='初始资金')
        ax1.set_ylabel('资金 (元)', fontsize=12)
        ax1.set_title('权益曲线', fontsize=14)
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 添加收益标注
        final_equity = equity_df['equity'].iloc[-1]
        total_return = ((final_equity - results.initial_capital) / results.initial_capital) * 100
        color = 'green' if total_return > 0 else 'red'
        ax1.text(0.02, 0.98, f'总收益：{total_return:+.2f}%',
                transform=ax1.transAxes, fontsize=12,
                verticalalignment='top', color=color, fontweight='bold')

        # 2. 回撤曲线
        ax2 = axes[1]
        equity_df['peak'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['peak']) / equity_df['peak'] * 100
        ax2.fill_between(equity_df.index, equity_df['drawdown'], 0,
                        color='#E63946', alpha=0.3, label='回撤')
        ax2.set_ylabel('回撤 (%)', fontsize=12)
        ax2.set_title('最大回撤分析', fontsize=14)
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # 标注最大回撤
        max_dd = equity_df['drawdown'].min()
        max_dd_date = equity_df['drawdown'].idxmin()
        ax2.text(0.02, 0.05, f'最大回撤：{max_dd:.2f}%',
                transform=ax2.transAxes, fontsize=11,
                verticalalignment='bottom', color='#E63946', fontweight='bold')

        # 3. 交易分布
        ax3 = axes[2]
        if results.trades:
            buys = [t for t in results.trades if t.get('type') == 'buy']
            sells = [t for t in results.trades if t.get('type') == 'sell']

            # 按月统计交易次数
            if buys:
                buy_dates = pd.to_datetime([t['timestamp'] for t in buys])
                buy_monthly = buy_dates.to_series().resample('M').count()
                ax3.bar(buy_monthly.index, buy_monthly.values,
                       width=20, alpha=0.7, color='#2E86AB', label='买入')

            if sells:
                sell_dates = pd.to_datetime([t['timestamp'] for t in sells])
                sell_monthly = sell_dates.to_series().resample('M').count()
                ax3.bar(sell_monthly.index, sell_monthly.values,
                       width=20, alpha=0.7, color='#E63946', label='卖出')

        ax3.set_ylabel('交易次数', fontsize=12)
        ax3.set_xlabel('日期', fontsize=12)
        ax3.set_title('交易分布', fontsize=14)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        plt.xticks(rotation=45)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✅ 图表已保存：{save_path}")

        plt.show()

    def plot_comparison(self, results_list, save_path: Optional[str] = None):
        """
        对比多个策略

        Args:
            results_list: BacktestResults 列表
            save_path: 保存路径
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("⚠️  matplotlib 未安装")
            return

        fig, ax = plt.subplots(figsize=(14, 8))

        colors = ['#2E86AB', '#E63946', '#2A9D8F', '#F4A261', '#8338EC']

        for i, results in enumerate(results_list):
            if not results.equity_curve:
                continue

            equity_df = pd.DataFrame(results.equity_curve)
            equity_df.set_index('timestamp', inplace=True)

            # 归一化到 100
            normalized = equity_df['equity'] / results.initial_capital * 100
            color = colors[i % len(colors)]
            ax.plot(normalized.index, normalized,
                   label=f'{results.strategy_name}',
                   linewidth=2, color=color)

        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('归一化净值', fontsize=12)
        ax.set_title('策略对比', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✅ 对比图已保存：{save_path}")

        plt.show()

    def plot_metrics_radar(self, results, save_path: Optional[str] = None):
        """
        绘制指标雷达图

        Args:
            results: BacktestResults 实例
            save_path: 保存路径
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            return

        metrics = results.metrics
        if not metrics:
            return

        # 选择关键指标
        categories = ['收益', '夏普比率', '胜率', '回撤 (反向)']
        values = [
            min(metrics.get('总收益 (%)', 0), 100) / 100,
            min(metrics.get('夏普比率', 0), 3) / 3,
            min(metrics.get('胜率 (%)', 50), 100) / 100,
            max(1 + metrics.get('最大回撤 (%)', 0) / 100, 0),  # 回撤越小越好
        ]

        # 绘制雷达图
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))

        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]

        ax.plot(angles, values, 'o-', linewidth=2, color='#2E86AB')
        ax.fill(angles, values, alpha=0.25, color='#2E86AB')
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=12)
        ax.set_ylim(0, 1)
        ax.set_title(f'{results.strategy_name} - 策略指标', fontsize=14, pad=20)
        ax.grid(True)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✅ 雷达图已保存：{save_path}")

        plt.show()
