#!/usr/bin/env python3
"""
选股引擎使用示例

演示如何使用 StockSelector 进行自动化选股、批量回测和股票池管理

@module: examples.stock_selector_demo
@author: OpenFinAgent Team
@version: 1.0.0
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.stock_selector import (
    StockSelector,
    StockCriteria,
    SelectionMethod,
    create_selector
)
from src.strategy.dual_ma_volume_strategy import DualMAStrategy


def example_basic_selection():
    """
    示例 1: 基础选股
    
    使用默认条件从股票池中筛选优质股票
    """
    print("\n" + "=" * 70)
    print("示例 1: 基础选股")
    print("=" * 70)
    
    # 初始化选股引擎
    selector = create_selector()
    
    # 定义选股条件
    criteria = StockCriteria(
        top_n=10,           # 选前 10 只股票
        min_score=70,       # 最低评分 70 分
        min_sharpe=1.5,     # 最低夏普比率 1.5
        max_drawdown=0.15,  # 最大回撤不超过 15%
        min_return=0.20     # 最低收益率 20%
    )
    
    # 准备候选股票池（示例使用少量股票）
    candidate_pool = [
        '000001.SZ',  # 平安银行
        '000002.SZ',  # 万科 A
        '600000.SH',  # 浦发银行
        '600036.SH',  # 招商银行
        '000063.SZ',  # 中兴通讯
    ]
    
    # 创建策略实例
    strategy = DualMAStrategy(
        short_period=5,
        long_period=20,
        volume_factor=1.5
    )
    
    # 执行选股
    print(f"\n开始选股...")
    print(f"候选股票数：{len(candidate_pool)}")
    print(f"选股条件：{criteria}")
    
    selected_pool = selector.select_stocks(
        strategy=strategy,
        stock_pool=candidate_pool,
        criteria=criteria,
        start_date='2023-01-01',
        end_date='2023-12-31'
    )
    
    print(f"\n✅ 选股完成！")
    print(f"入选股票数：{len(selected_pool.stocks)}")
    print(f"入选股票：{selected_pool.stocks}")
    
    return selected_pool


def example_batch_backtest():
    """
    示例 2: 批量回测
    
    对多只股票并行执行回测，生成汇总报告
    """
    print("\n" + "=" * 70)
    print("示例 2: 批量回测")
    print("=" * 70)
    
    # 初始化选股引擎
    selector = create_selector(max_workers=4)  # 使用 4 个并发线程
    
    # 准备股票池
    stock_pool = [
        '000001.SZ',
        '000002.SZ',
        '600000.SH',
        '600036.SH',
    ]
    
    # 创建策略
    strategy = DualMAStrategy(
        short_period=10,
        long_period=30,
        volume_factor=2.0
    )
    
    print(f"\n开始批量回测...")
    print(f"回测股票数：{len(stock_pool)}")
    print(f"回测区间：2023-01-01 至 2023-12-31")
    
    # 执行批量回测
    report = selector.batch_backtest(
        strategy=strategy,
        stock_pool=stock_pool,
        start_date='2023-01-01',
        end_date='2023-12-31',
        initial_capital=100000.0,
        show_progress=True
    )
    
    # 显示报告
    report.show()
    
    # 获取排名
    print("\n📊 按夏普比率排名 Top 3:")
    top_stocks = report.rank_stocks(by='sharpe', top_n=3)
    for i, (symbol, metrics) in enumerate(top_stocks, 1):
        sharpe = metrics.get('夏普比率', 0)
        return_pct = metrics.get('总收益 (%)', 0)
        print(f"  {i}. {symbol:12} 夏普：{sharpe:6.2f}  收益：{return_pct:7.2f}%")
    
    return report


def example_pool_management():
    """
    示例 3: 股票池管理
    
    演示股票池的创建、更新、导入导出等操作
    """
    print("\n" + "=" * 70)
    print("示例 3: 股票池管理")
    print("=" * 70)
    
    # 初始化选股引擎
    selector = create_selector()
    
    # 1. 创建股票池
    print("\n1️⃣  创建股票池...")
    pool = selector.create_pool(
        name='科技成长股',
        stocks=['000001.SZ', '000002.SZ', '600036.SH'],
        strategy_id='growth_strategy',
        description='高成长的科技行业股票',
        tags=['科技', '成长', '龙头']
    )
    print(f"   创建成功：{pool.name}, 包含 {pool.count()} 只股票")
    
    # 2. 添加股票
    print("\n2️⃣  添加股票...")
    pool.add_stock('000063.SZ')
    pool.add_stock('600519.SH')
    print(f"   添加后股票数：{pool.count()}")
    
    # 3. 移除股票
    print("\n3️⃣  移除股票...")
    pool.remove_stock('000001.SZ')
    print(f"   移除后股票数：{pool.count()}")
    
    # 4. 列出所有股票池
    print("\n4️⃣  所有股票池:")
    pools = selector.list_pools()
    for name in pools:
        print(f"   - {name}")
    
    # 5. 导出股票池
    print("\n5️⃣  导出股票池...")
    export_path = '/tmp/tech_growth_pool.json'
    selector.export_pool('科技成长股', export_path)
    print(f"   已导出到：{export_path}")
    
    # 6. 获取股票池统计
    print("\n6️⃣  股票池统计:")
    stats = selector.pool_manager.get_pool_stats('科技成长股')
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # 7. 删除股票池
    print("\n7️⃣  删除股票池...")
    selector.delete_pool('科技成长股')
    print(f"   删除成功")
    
    print("\n✅ 股票池管理示例完成！")


def example_advanced_criteria():
    """
    示例 4: 高级选股条件
    
    使用不同的选股方法和自定义条件
    """
    print("\n" + "=" * 70)
    print("示例 4: 高级选股条件")
    print("=" * 70)
    
    # 初始化选股引擎
    selector = create_selector()
    
    # 1. 基于夏普比率的选股
    print("\n1️⃣  基于夏普比率选股...")
    criteria_sharpe = StockCriteria(
        top_n=5,
        min_score=60,
        min_sharpe=2.0,
        max_drawdown=0.10,
        selection_method=SelectionMethod.SHARPE_BASED,  # 按夏普比率排序
        exclude_st=True,
        min_market_cap=100,  # 市值大于 100 亿
        max_market_cap=5000  # 市值小于 5000 亿
    )
    print(f"   条件：{criteria_sharpe}")
    
    # 2. 基于收益率的选股
    print("\n2️⃣  基于收益率选股...")
    criteria_return = StockCriteria(
        top_n=10,
        min_score=65,
        min_sharpe=1.0,
        max_drawdown=0.25,
        min_return=0.30,  # 要求收益率大于 30%
        selection_method=SelectionMethod.RETURN_BASED  # 按收益率排序
    )
    print(f"   条件：{criteria_return}")
    
    # 3. 保守型选股（低风险）
    print("\n3️⃣  保守型选股（低风险偏好）...")
    criteria_conservative = StockCriteria(
        top_n=15,
        min_score=75,
        min_sharpe=1.8,
        max_drawdown=0.08,  # 最大回撤不超过 8%
        min_return=0.15,
        exclude_st=True,
        exclude_new=True,    # 排除次新股
        min_market_cap=200   # 只选大盘股
    )
    print(f"   条件：{criteria_conservative}")
    
    # 4. 激进型选股（高风险高收益）
    print("\n4️⃣  激进型选股（高风险偏好）...")
    criteria_aggressive = StockCriteria(
        top_n=8,
        min_score=55,
        min_sharpe=0.8,
        max_drawdown=0.35,  # 可承受 35% 回撤
        min_return=0.50,    # 要求收益率大于 50%
        selection_method=SelectionMethod.RETURN_BASED
    )
    print(f"   条件：{criteria_aggressive}")
    
    print("\n✅ 高级选股条件示例完成！")


def main():
    """主函数 - 运行所有示例"""
    print("\n" + "🚀" * 35)
    print("OpenFinAgent 选股引擎使用示例")
    print("🚀" * 35)
    
    try:
        # 运行示例
        example_basic_selection()
        example_batch_backtest()
        example_pool_management()
        example_advanced_criteria()
        
        print("\n" + "🎉" * 35)
        print("所有示例运行完成！")
        print("🎉" * 35)
        
    except Exception as e:
        print(f"\n❌ 示例运行出错：{e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
