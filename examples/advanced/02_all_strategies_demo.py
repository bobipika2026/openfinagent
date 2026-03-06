#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全策略对比演示

演示如何使用 OpenFinAgent 进行：
1. 多策略对比回测
2. 策略参数优化
3. 批量回测
4. 风险控制集成
"""

import sys
sys.path.insert(0, '../../src')

import pandas as pd
import numpy as np
from datetime import datetime

from src.strategy import (
    MACrossStrategy,
    MomentumStrategy,
    RSIStrategy,
    MACDStrategy,
    BollingerStrategy,
    DualMAVolumeStrategy,
    StrategyBuilder
)
from src.backtest import (
    BacktestEngine,
    BacktestResults,
    MultiStrategyBacktester,
    BatchBacktester,
    BatchBacktestConfig
)
from src.optimization.optimizer import (
    StrategyOptimizer,
    ParameterRange
)
from src.risk.control import RiskController, RiskLimits
from src.data.sources import MockDataSource


def generate_demo_data(n_days=500, seed=42):
    """生成演示数据"""
    np.random.seed(seed)
    dates = pd.date_range(start='2022-01-01', periods=n_days, freq='B')
    
    returns = np.random.normal(0.0005, 0.02, n_days)
    prices = 100.0 * np.cumprod(1 + returns)
    
    df = pd.DataFrame(index=dates)
    df['close'] = prices
    df['open'] = prices * (1 + np.random.uniform(-0.01, 0.01, n_days))
    df['high'] = df[['open', 'close']].max(axis=1) * (1 + np.random.uniform(0, 0.02, n_days))
    df['low'] = df[['open', 'close']].min(axis=1) * (1 - np.random.uniform(0, 0.02, n_days))
    df['volume'] = np.random.randint(1000000, 10000000, n_days)
    
    return df


def demo_all_strategies_comparison():
    """演示 1: 全策略对比"""
    print("\n" + "="*70)
    print("📊 演示 1: 全策略对比回测")
    print("="*70)
    
    # 生成数据
    data = generate_demo_data(500)
    
    # 创建策略组合
    strategies = [
        MACrossStrategy(short_window=5, long_window=20, initial_capital=100000, name='均线交叉'),
        MomentumStrategy(lookback_period=20, threshold=0.05, initial_capital=100000, name='动量策略'),
        RSIStrategy(rsi_period=14, initial_capital=100000, name='RSI 策略'),
        MACDStrategy(fast_period=12, slow_period=26, initial_capital=100000, name='MACD 策略'),
        BollingerStrategy(window=20, initial_capital=100000, name='布林带策略'),
        DualMAVolumeStrategy(short_window=5, long_window=20, initial_capital=100000, name='双均线 + 成交量')
    ]
    
    # 多策略回测
    backtester = MultiStrategyBacktester(initial_capital=100000)
    results = backtester.run(strategies, data)
    
    # 对比结果
    comparison = backtester.compare()
    
    print("\n策略对比结果:")
    print("-" * 70)
    print(comparison.to_string(index=False))
    print("-" * 70)
    
    # 找出最佳策略
    if '夏普比率' in comparison.columns:
        best_sharpe = comparison.loc[comparison['夏普比率'].idxmax()]
        print(f"\n🏆 最佳夏普比率策略：{best_sharpe['strategy']} (夏普比率={best_sharpe['夏普比率']:.2f})")
    
    if '总收益 (%)' in comparison.columns:
        best_return = comparison.loc[comparison['总收益 (%)'].idxmax()]
        print(f"💰 最佳收益策略：{best_return['strategy']} (总收益={best_return['总收益 (%)']:.2f}%)")
    
    return comparison


def demo_strategy_optimization():
    """演示 2: 策略参数优化"""
    print("\n" + "="*70)
    print("🔧 演示 2: RSI 策略参数优化")
    print("="*70)
    
    # 生成数据
    data = generate_demo_data(500)
    
    # 定义回测函数
    def backtest_func(strategy, data):
        engine = BacktestEngine()
        return engine.run(strategy, data, show_progress=False)
    
    # 创建优化器
    optimizer = StrategyOptimizer(
        optimization_metric='sharpe_ratio',
        maximize=True,
        n_jobs=1
    )
    
    # 定义参数范围
    param_ranges = [
        ParameterRange(name='rsi_period', values=[10, 14, 18, 21]),
        ParameterRange(name='oversold_threshold', values=[25, 30, 35]),
        ParameterRange(name='overbought_threshold', values=[65, 70, 75])
    ]
    
    print(f"\n开始网格搜索，共 {len(param_ranges[0].values) * len(param_ranges[1].values) * len(param_ranges[2].values)} 个参数组合...")
    
    # 执行优化
    results = optimizer.grid_search(
        strategy_class=RSIStrategy,
        parameter_ranges=param_ranges,
        backtest_func=backtest_func,
        data=data,
        initial_capital=100000,
        show_progress=False
    )
    
    # 显示最优结果
    best = optimizer.get_best_params()
    print(f"\n✅ 最优参数:")
    print(f"  RSI 周期：{best.get('rsi_period', 'N/A')}")
    print(f"  超卖阈值：{best.get('oversold_threshold', 'N/A')}")
    print(f"  超买阈值：{best.get('overbought_threshold', 'N/A')}")
    
    if optimizer.best_result:
        print(f"\n📈 最优结果指标:")
        print(f"  夏普比率：{optimizer.best_result.sharpe_ratio:.2f}")
        print(f"  总收益：{optimizer.best_result.total_return:.2f}%")
        print(f"  最大回撤：{optimizer.best_result.max_drawdown:.2f}%")
    
    # 过拟合检测
    overfitting = optimizer.detect_overfitting()
    if overfitting.get('reliable'):
        print(f"\n⚠️  过拟合检测:")
        print(f"  过拟合分数：{overfitting['overfitting_score']:.2f}")
        if overfitting.get('overfitting_warning'):
            print(f"  ⚠️  警告：可能存在过拟合风险!")
        else:
            print(f"  ✅ 过拟合风险较低")
    
    return best


def demo_batch_backtest():
    """演示 3: 批量回测"""
    print("\n" + "="*70)
    print("📦 演示 3: 批量回测多只股票")
    print("="*70)
    
    # 使用最优参数
    best_params = {'rsi_period': 14, 'oversold_threshold': 30, 'overbought_threshold': 70}
    
    # 配置批量回测
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META', 'NVDA', 'TSLA', 'AMD', 'INTC', 'NFLX']
    
    config = BatchBacktestConfig(
        symbols=symbols,
        strategy_class=RSIStrategy,
        strategy_params=best_params,
        initial_capital=100000,
        start_date='2022-01-01',
        end_date='2023-12-31',
        data_source='mock',
        n_jobs=4,
        show_progress=True
    )
    
    # 执行批量回测
    batch_backtester = BatchBacktester(config)
    results = batch_backtester.run()
    
    # 显示汇总
    summary = batch_backtester.get_summary()
    
    if summary is not None:
        print("\n批量回测汇总:")
        print("-" * 70)
        print(summary.to_string(index=False))
        print("-" * 70)
        
        # 统计
        print(f"\n📊 统计信息:")
        print(f"  成功回测：{(summary['总收益 (%)'].notna()).sum()} / {len(symbols)}")
        print(f"  平均收益：{summary['总收益 (%)'].mean():.2f}%")
        print(f"  中位收益：{summary['总收益 (%)'].median():.2f}%")
        print(f"  胜率：{(summary['总收益 (%)'] > 0).mean() * 100:.1f}%")
        
        # 最佳表现
        if len(summary) > 0:
            best_stock = summary.loc[summary['总收益 (%)'].idxmax()]
            print(f"\n🏆 最佳表现股票：{best_stock['symbol']} (收益={best_stock['总收益 (%)']:.2f}%)")
    
    return summary


def demo_risk_control():
    """演示 4: 风险控制集成"""
    print("\n" + "="*70)
    print("🛡️  演示 4: 风险控制集成")
    print("="*70)
    
    # 创建风险限制
    limits = RiskLimits(
        max_position_ratio=0.3,  # 单只股票最大 30% 仓位
        stop_loss_pct=0.08,      # 8% 止损
        take_profit_pct=0.20,    # 20% 止盈
        max_drawdown_pct=0.15,   # 15% 最大回撤
        max_trades_per_day=10    # 单日最多 10 笔交易
    )
    
    # 创建风险控制器
    risk_controller = RiskController(limits)
    
    print("\n风险控制配置:")
    print(f"  单笔最大仓位：{limits.max_position_ratio*100:.0f}%")
    print(f"  止损阈值：{limits.stop_loss_pct*100:.0f}%")
    print(f"  止盈阈值：{limits.take_profit_pct*100:.0f}%")
    print(f"  最大回撤：{limits.max_drawdown_pct*100:.0f}%")
    print(f"  单日交易限制：{limits.max_trades_per_day}笔")
    
    # 模拟交易场景
    print("\n模拟交易场景:")
    
    # 场景 1: 正常买入
    print("\n1️⃣  场景 1: 正常买入")
    permission = risk_controller.check_trade_permission(
        action='buy',
        price=100.0,
        shares=200,
        current_cash=100000,
        current_positions={'shares': 0},
        current_equity=100000
    )
    print(f"  交易许可：{'✅ 通过' if permission['allowed'] else '❌ 拒绝'}")
    print(f"  原因：{permission['reason']}")
    
    # 场景 2: 止损触发
    print("\n2️⃣  场景 2: 止损触发测试")
    risk_controller.record_trade('buy', price=100.0, shares=1000, symbol='TEST')
    action = risk_controller.check_stop_loss_take_profit(current_price=90.0, symbol='TEST')
    print(f"  当前价格：90.0 (买入价 100.0)")
    print(f"  触发检查：{'止损' if action == 'stop_loss' else '无触发'}")
    
    # 场景 3: 止盈触发
    print("\n3️⃣  场景 3: 止盈触发测试")
    risk_controller.reset(100000)
    risk_controller.record_trade('buy', price=100.0, shares=1000, symbol='TEST')
    action = risk_controller.check_stop_loss_take_profit(current_price=125.0, symbol='TEST')
    print(f"  当前价格：125.0 (买入价 100.0)")
    print(f"  触发检查：{'止盈' if action == 'take_profit' else '无触发'}")
    
    # 场景 4: 仓位调整
    print("\n4️⃣  场景 4: 仓位调整")
    adjusted = risk_controller.adjust_position_size(
        proposed_shares=500,  # 提议买入 5 万元
        price=100.0,
        current_equity=100000,
        current_positions={'shares': 0}
    )
    print(f"  提议仓位：500 股 (5 万元)")
    print(f"  调整后仓位：{adjusted}股 (不超过 30% 限制)")


def demo_natural_language():
    """演示 5: 自然语言创建策略"""
    print("\n" + "="*70)
    print("💬 演示 5: 自然语言创建策略")
    print("="*70)
    
    # 示例 1: 均线策略
    print("\n1️⃣  示例：均线交叉策略")
    strategy1 = StrategyBuilder.from_natural_language("""
    当 5 日均线上穿 20 日均线时买入
    当 5 日均线下穿 20 日均线时卖出
    初始资金 10 万元
    """)
    print(f"  创建策略：{strategy1.name}")
    print(f"  短期均线：{strategy1.short_window}天")
    print(f"  长期均线：{strategy1.long_window}天")
    
    # 示例 2: 动量策略
    print("\n2️⃣  示例：动量策略")
    strategy2 = StrategyBuilder.from_natural_language("""
    动量策略
    看 20 天收益率
    超过 5% 买入
    初始资金 50 万元
    """)
    print(f"  创建策略：{strategy2.name}")
    print(f"  回看周期：{strategy2.lookback_period}天")
    print(f"  收益率阈值：{strategy2.threshold*100:.1f}%")
    
    # 示例 3: RSI 策略
    print("\n3️⃣  示例：RSI 策略")
    strategy3 = StrategyBuilder.create(
        'rsi',
        rsi_period=14,
        oversold_threshold=30,
        overbought_threshold=70,
        name='RSI 自定义策略'
    )
    print(f"  创建策略：{strategy3.name}")
    print(f"  RSI 周期：{strategy3.rsi_period}")
    print(f"  超卖阈值：{strategy3.oversold_threshold}")
    print(f"  超买阈值：{strategy3.overbought_threshold}")
    
    # 列出所有可用策略
    print("\n📋 所有可用策略:")
    strategies = StrategyBuilder.list_strategies()
    for i, s in enumerate(strategies, 1):
        print(f"  {i}. {s}")


def main():
    """主函数"""
    print("\n" + "="*70)
    print("🚀 OpenFinAgent - 全功能演示")
    print("="*70)
    print("\n本演示展示 OpenFinAgent 的核心功能:")
    print("  1. 多策略对比回测")
    print("  2. 策略参数优化")
    print("  3. 批量回测")
    print("  4. 风险控制")
    print("  5. 自然语言创建策略")
    
    # 运行所有演示
    demo_all_strategies_comparison()
    demo_strategy_optimization()
    demo_batch_backtest()
    demo_risk_control()
    demo_natural_language()
    
    print("\n" + "="*70)
    print("✅ 所有演示完成!")
    print("="*70)
    print("\n💡 提示:")
    print("  - 修改参数重新运行以观察不同结果")
    print("  - 查看 examples/ 目录获取更多示例")
    print("  - 阅读 docs/ 目录了解详细文档")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
