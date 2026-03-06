#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradeFlow AI 快速演示

运行此脚本快速体验 TradeFlow AI 的核心功能
"""

import sys
import os

# 添加 src 到路径
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# 直接导入模块
import pandas as pd
import numpy as np
from strategy.base import BaseStrategy
from strategy.builder import StrategyBuilder, MACrossStrategy, MomentumStrategy
from backtest.engine import BacktestEngine, load_data


def demo():
    """运行演示"""
    print("\n" + "=" * 70)
    print("🚀 TradeFlow AI 快速演示")
    print("=" * 70)

    # 1. 创建策略
    print("\n📝 步骤 1: 用自然语言创建策略")
    print("-" * 70)

    strategy_text = """
    当 5 日均线上穿 20 日均线时买入
    当 5 日均线下穿 20 日均线时卖出
    初始资金 10 万元
    """

    print("策略描述:")
    print(strategy_text)

    strategy = StrategyBuilder.from_natural_language(strategy_text)
    print(f"✅ 策略创建成功：{strategy.name}")
    print(f"   短期均线：{strategy.short_window}日")
    print(f"   长期均线：{strategy.long_window}日")
    print(f"   初始资金：¥{strategy.initial_capital:,.0f}")

    # 2. 加载数据
    print("\n📊 步骤 2: 加载市场数据")
    print("-" * 70)

    data = load_data(
        symbol="600519.SH",
        start_date="2023-01-01",
        end_date="2023-12-31",
        source='mock'
    )

    print(f"✅ 数据加载完成")
    print(f"   时间范围：{data.index[0].date()} 至 {data.index[-1].date()}")
    print(f"   数据条数：{len(data)}")
    print(f"   价格区间：¥{data['close'].min():.2f} - ¥{data['close'].max():.2f}")

    # 3. 运行回测
    print("\n🔄 步骤 3: 运行回测")
    print("-" * 70)

    engine = BacktestEngine(
        commission_rate=0.0003,
        slippage=0.001
    )

    results = engine.run(strategy, data, show_progress=True)

    # 4. 显示结果
    print("\n📈 步骤 4: 回测结果")
    print("-" * 70)

    results.show()

    # 5. 保存结果
    print("\n💾 步骤 5: 保存结果")
    print("-" * 70)

    results.to_csv('demo_trades.csv')

    print("\n" + "=" * 70)
    print("✅ 演示完成！")
    print("=" * 70)
    print("\n💡 下一步:")
    print("   1. 查看 examples/ 目录了解更多示例")
    print("   2. 阅读 docs/ 目录学习详细文档")
    print("   3. 修改策略参数重新回测")
    print("   4. 创建你自己的自定义策略")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    demo()
