#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级示例 1: 多策略对比

同时回测多个策略并对比表现
"""

import sys
sys.path.insert(0, '../../src')

from src import StrategyBuilder, BacktestEngine
from src.backtest.engine import load_data
from src.visualization.plotter import StrategyPlotter


def main():
    print("=" * 60)
    print("📊 高级示例 1: 多策略对比")
    print("=" * 60)

    # 创建多个策略
    print("\n🎯 创建策略组合...")

    strategies = [
        StrategyBuilder.create('ma_cross', short_window=5, long_window=20,
                               initial_capital=100000, name='均线 (5/20)'),
        StrategyBuilder.create('ma_cross', short_window=10, long_window=30,
                               initial_capital=100000, name='均线 (10/30)'),
        StrategyBuilder.create('ma_cross', short_window=20, long_window=60,
                               initial_capital=100000, name='均线 (20/60)'),
        StrategyBuilder.create('momentum', lookback_period=20, threshold=0.05,
                               initial_capital=100000, name='动量 (20 日)'),
    ]

    print(f"共创建 {len(strategies)} 个策略")
    for s in strategies:
        print(f"  - {s.name}")

    # 加载数据
    print("\n📊 加载数据...")
    data = load_data(
        symbol="600519.SH",
        start_date="2023-01-01",
        end_date="2023-12-31",
        source='mock'
    )
    print(f"数据条数：{len(data)}")

    # 运行回测
    print("\n🔄 运行回测...")
    engine = BacktestEngine()
    results_dict = engine.run_multi(strategies, data)

    # 对比结果
    print("\n" + "=" * 60)
    print("📈 策略对比结果")
    print("=" * 60)
    print(f"{'策略名称':15} {'总收益 (%)':>12} {'夏普比率':>10} {'最大回撤 (%)':>12}")
    print("-" * 60)

    results_list = []
    for name, results in results_dict.items():
        metrics = results.metrics
        results_list.append(results)
        print(f"{name:15} {metrics.get('总收益 (%)', 0):>12.2f} "
              f"{metrics.get('夏普比率', 0):>10.2f} "
              f"{metrics.get('最大回撤 (%)', 0):>12.2f}")

    print("=" * 60)

    # 找出最佳策略
    best_strategy = max(results_list, key=lambda r: r.metrics.get('总收益 (%)', 0))
    print(f"\n🏆 最佳策略：{best_strategy.strategy_name}")
    print(f"   总收益：{best_strategy.metrics.get('总收益 (%)', 0):.2f}%")

    # 绘制对比图
    print("\n📊 生成对比图表...")
    plotter = StrategyPlotter()
    plotter.plot_comparison(results_list, save_path='strategy_comparison.png')

    print("\n✅ 示例完成！")


if __name__ == "__main__":
    main()
