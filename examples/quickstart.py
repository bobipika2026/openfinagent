#!/usr/bin/env python3
"""
TradeFlow AI - 快速开始示例
============================
演示如何使用 TradeFlow 核心功能
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime


def example_1_basic_usage():
    """示例 1: 基本使用"""
    print("\n" + "="*60)
    print("示例 1: 基本使用 - 自然语言策略解析")
    print("="*60)
    
    from tradeflow.core import create_engine
    
    # 创建核心引擎
    engine = create_engine({
        'data_source': 'akshare',
        'broker': 'paper'
    })
    
    # 解析自然语言策略
    strategy = engine.parse_strategy("当 5 日均线上穿 20 日均线时买入，下穿时卖出")
    
    print(f"策略 ID: {strategy['strategy_id']}")
    print(f"策略描述：{strategy['description']}")
    print(f"条件数量：{len(strategy['conditions'])}")
    print(f"动作数量：{len(strategy['actions'])}")
    
    return engine, strategy


def example_2_market_data():
    """示例 2: 获取市场数据"""
    print("\n" + "="*60)
    print("示例 2: 获取市场数据")
    print("="*60)
    
    from tradeflow.data import create_data_manager
    
    # 创建数据管理器
    dm = create_data_manager({'default_source': 'akshare'})
    
    # 获取 A 股数据
    print("\n获取 A 股数据 (000001.SZ)...")
    data = dm.get_data('000001.SZ', '2024-01-01', '2024-01-31')
    print(f"数据源：{data['source']}")
    print(f"交易天数：{len(data['data'])}")
    if data['data']:
        print(f"首日数据：{data['data'][0]}")
    
    # 获取美股数据
    print("\n获取美股数据 (AAPL)...")
    data = dm.get_data('AAPL', '2024-01-01', '2024-01-31')
    print(f"数据源：{data['source']}")
    print(f"交易天数：{len(data['data'])}")
    
    return dm


def example_3_backtest():
    """示例 3: 策略回测"""
    print("\n" + "="*60)
    print("示例 3: 策略回测")
    print("="*60)
    
    from tradeflow.core import create_engine
    from tradeflow.backtest import create_backtest_engine
    
    # 创建引擎
    engine = create_engine()
    
    # 解析策略
    strategy = engine.parse_strategy("当 5 日均线上穿 20 日均线时买入")
    
    # 创建回测引擎
    backtest = create_backtest_engine(
        initial_capital=100000.0,
        config={
            'commission_rate': 0.0003,
            'slippage_rate': 0.001
        }
    )
    
    # 运行回测
    print("\n运行回测...")
    result = backtest.run(strategy, '2024-01-01', '2024-01-31')
    
    # 显示结果
    print("\n" + result.summary())
    print(f"\n详细指标:")
    print(f"  年化收益率：{result.details.get('annualized_return', 0):.2%}")
    print(f"  盈利交易：{result.details.get('winning_trades', 0)}")
    print(f"  亏损交易：{result.details.get('losing_trades', 0)}")
    print(f"  平均盈利：{result.details.get('avg_win', 0):.2f}")
    print(f"  平均亏损：{result.details.get('avg_loss', 0):.2f}")
    
    return result


def example_4_agents():
    """示例 4: 多 Agent 协作"""
    print("\n" + "="*60)
    print("示例 4: 多 Agent 协作")
    print("="*60)
    
    from tradeflow.agents import create_default_orchestrator
    
    # 创建编排引擎
    orchestrator = create_default_orchestrator()
    
    # 查看系统状态
    status = orchestrator.get_system_status()
    print(f"\n活跃 Agent 数量：{status['active_agents']}/{status['total_agents']}")
    
    # 投研分析
    print("\n1. 投研分析...")
    research_result = orchestrator.process_task('research', {
        'symbol': '000001.SZ',
        'type': 'technical'
    })
    print(f"   分析类型：{research_result.get('analysis_type')}")
    print(f"   信号：{research_result.get('signal')}")
    
    # 交易执行（自动风控检查）
    print("\n2. 交易执行（含风控检查）...")
    trade_result = orchestrator.process_task('trade', {
        'action': 'buy',
        'symbol': '000001.SZ',
        'quantity': 100,
        'price': 10.0
    })
    print(f"   订单状态：{trade_result.get('status')}")
    print(f"   订单 ID: {trade_result.get('order_id')}")
    
    # 风控检查
    print("\n3. 独立风控检查...")
    risk_result = orchestrator.process_task('risk_check', {
        'check_type': 'trade',
        'symbol': '000001.SZ',
        'quantity': 100,
        'price': 10.0
    })
    print(f"   风控结果：{'通过' if risk_result.get('passed') else '拒绝'}")
    
    return orchestrator


def example_5_trading():
    """示例 5: 交易执行"""
    print("\n" + "="*60)
    print("示例 5: 交易执行与持仓管理")
    print("="*60)
    
    from tradeflow.core import create_engine, TradeSignal
    
    # 创建引擎
    engine = create_engine({'broker': 'paper'})
    
    # 执行买入
    print("\n执行买入订单...")
    buy_signal = TradeSignal(
        symbol='000001.SZ',
        action='buy',
        quantity=100,
        price=10.0,
        strategy_name='test_strategy'
    )
    buy_result = engine.execute_trade(buy_signal)
    print(f"买入结果：{buy_result['status']}")
    print(f"订单 ID: {buy_result['order_id']}")
    
    # 查看持仓
    positions = engine.get_positions()
    print(f"\n当前持仓：{positions}")
    
    # 执行卖出
    print("\n执行卖出订单...")
    sell_signal = TradeSignal(
        symbol='000001.SZ',
        action='sell',
        quantity=50,
        price=11.0,
        strategy_name='test_strategy'
    )
    sell_result = engine.execute_trade(sell_signal)
    print(f"卖出结果：{sell_result['status']}")
    
    # 查看更新后的持仓
    positions = engine.get_positions()
    print(f"当前持仓：{positions}")
    
    # 查看交易历史
    history = engine.get_trade_history()
    print(f"\n交易历史（共 {len(history)} 笔）:")
    for i, trade in enumerate(history, 1):
        print(f"  {i}. {trade['signal']['action']} {trade['signal']['symbol']} @ {trade['signal']['price']}")
    
    # 导出审计日志
    audit_log = engine.export_audit_log()
    print(f"\n审计日志已导出（{len(audit_log)} 字符）")
    
    return engine


def main():
    """主函数 - 运行所有示例"""
    print("\n" + "="*60)
    print("TradeFlow AI - 快速开始示例")
    print("="*60)
    print(f"运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 运行所有示例
        engine, strategy = example_1_basic_usage()
        dm = example_2_market_data()
        result = example_3_backtest()
        orchestrator = example_4_agents()
        engine = example_5_trading()
        
        print("\n" + "="*60)
        print("✅ 所有示例运行完成!")
        print("="*60)
        print("\n下一步:")
        print("1. 修改策略描述，尝试不同的交易逻辑")
        print("2. 更改回测日期范围和数据源")
        print("3. 集成真实 AI API 实现自然语言理解")
        print("4. 连接真实数据源（AkShare/YFinance）")
        print("5. 开发自定义 Agent 和策略")
        print("\n文档：参考 MVP_REPORT.md 和 STRATEGY.md")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 运行错误：{e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
