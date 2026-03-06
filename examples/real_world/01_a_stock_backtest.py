#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实战示例 1: A 股回测

使用真实 A 股数据进行回测
"""

import sys
sys.path.insert(0, '../../src')

from tradeflow import StrategyBuilder, BacktestEngine
from tradeflow.backtest.engine import load_data
from tradeflow.visualization.plotter import StrategyPlotter


def main():
    print("=" * 60)
    print("🇨🇳 实战示例 1: A 股回测 - 贵州茅台")
    print("=" * 60)

    # 创建策略
    print("\n🎯 创建策略...")
    strategy = StrategyBuilder.from_natural_language("""
    均线交叉策略
    当 10 日均线上穿 30 日均线时买入
    当 10 日均线下穿 30 日均线时卖出
    初始资金 50 万元
    """)

    # 加载真实数据
    print("\n📊 加载 A 股数据...")
    try:
        data = load_data(
            symbol="600519.SH",  # 贵州茅台
            start_date="2022-01-01",
            end_date="2023-12-31",
            source='akshare'  # 使用 AKShare 获取真实数据
        )
        print(f"✅ 数据加载成功")
        print(f"数据范围：{data.index[0].date()} 至 {data.index[-1].date()}")
        print(f"数据条数：{len(data)}")
        print(f"价格区间：¥{data['close'].min():.2f} - ¥{data['close'].max():.2f}")
    except Exception as e:
        print(f"⚠️  真实数据加载失败：{e}")
        print("📝 使用模拟数据...")
        data = load_data(
            symbol="600519.SH",
            start_date="2022-01-01",
            end_date="2023-12-31",
            source='mock'
        )

    # 运行回测
    print("\n🔄 运行回测...")
    engine = BacktestEngine(
        commission_rate=0.0003,  # A 股佣金万三
        slippage=0.001
    )
    results = engine.run(strategy, data, show_progress=True)

    # 显示结果
    results.show()

    # 生成图表
    print("\n📊 生成分析图表...")
    plotter = StrategyPlotter()

    # 保存图表
    try:
        plotter.plot_backtest(results, save_path='maotai_backtest.png')
        plotter.plot_metrics_radar(results, save_path='maotai_radar.png')
    except Exception as e:
        print(f"⚠️  图表生成失败：{e}")

    # 导出结果
    print("\n💾 导出结果...")
    results.to_csv('maotai_trades.csv')

    print("\n✅ 回测完成！")


if __name__ == "__main__":
    main()
