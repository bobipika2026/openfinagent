#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例 1: 均线交叉策略

最简单的均线交叉策略：
- 当 5 日均线上穿 20 日均线时买入
- 当 5 日均线下穿 20 日均线时卖出
"""

import sys
sys.path.insert(0, '../../src')

from tradeflow import StrategyBuilder, BacktestEngine
from tradeflow.backtest.engine import load_data


def main():
    print("=" * 60)
    print("📈 示例 1: 均线交叉策略")
    print("=" * 60)

    # 方法 1: 使用自然语言创建策略
    print("\n🎯 方法 1: 自然语言描述")
    strategy1 = StrategyBuilder.from_natural_language("""
    当 5 日均线上穿 20 日均线时买入
    当 5 日均线下穿 20 日均线时卖出
    初始资金 10 万元
    """)
    print(f"策略名称：{strategy1.name}")
    print(f"短期均线：{strategy1.short_window}日")
    print(f"长期均线：{strategy1.long_window}日")

    # 方法 2: 直接创建策略
    print("\n🎯 方法 2: 直接参数化创建")
    strategy2 = StrategyBuilder.create(
        'ma_cross',
        short_window=10,
        long_window=30,
        initial_capital=200000,
        name='双均线策略 (10/30)'
    )
    print(f"策略名称：{strategy2.name}")
    print(f"短期均线：{strategy2.short_window}日")
    print(f"长期均线：{strategy2.long_window}日")

    # 加载数据 (使用模拟数据)
    print("\n📊 加载数据...")
    data = load_data(
        symbol="600519.SH",
        start_date="2023-01-01",
        end_date="2023-12-31",
        source='mock'  # 使用模拟数据
    )
    print(f"数据范围：{data.index[0].date()} 至 {data.index[-1].date()}")
    print(f"数据条数：{len(data)}")

    # 运行回测
    print("\n🔄 运行回测...")
    engine = BacktestEngine()
    results = engine.run(strategy1, data)

    # 显示结果
    results.show()

    # 绘图
    print("\n📊 生成图表...")
    try:
        results.plot()
    except Exception as e:
        print(f"⚠️  绘图失败：{e}")

    print("\n✅ 示例完成！")


if __name__ == "__main__":
    main()
