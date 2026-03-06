#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例 2: 动量策略

基于价格动量的策略：
- 当 20 日收益率超过 5% 时买入
- 当 20 日收益率低于 -5% 时卖出
"""

import sys
sys.path.insert(0, '../../src')

from src import StrategyBuilder, BacktestEngine
from src.backtest.engine import load_data


def main():
    print("=" * 60)
    print("📈 示例 2: 动量策略")
    print("=" * 60)

    # 创建动量策略
    print("\n🎯 创建策略...")
    strategy = StrategyBuilder.from_natural_language("""
    动量策略
    看 20 天收益率
    超过 5% 买入
    低于 -5% 卖出
    初始资金 50 万元
    """)

    print(f"策略名称：{strategy.name}")
    print(f"回看周期：{strategy.lookback_period}天")
    print(f"阈值：{strategy.threshold * 100:.1f}%")

    # 加载数据
    print("\n📊 加载数据...")
    data = load_data(
        symbol="000001.SZ",
        start_date="2023-01-01",
        end_date="2023-12-31",
        source='mock'
    )
    print(f"数据范围：{data.index[0].date()} 至 {data.index[-1].date()}")

    # 运行回测
    print("\n🔄 运行回测...")
    engine = BacktestEngine(
        commission_rate=0.0003,  # 万分之三手续费
        slippage=0.001  # 0.1% 滑点
    )
    results = engine.run(strategy, data)

    # 显示结果
    results.show()

    # 保存交易记录
    print("\n💾 保存交易记录...")
    results.to_csv('momentum_trades.csv')

    print("\n✅ 示例完成！")


if __name__ == "__main__":
    main()
