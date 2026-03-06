#!/usr/bin/env python3
"""
OpenFinAgent v0.3.0 新功能演示

演示内容：
1. Binance 数据源获取加密货币数据
2. Tushare 分钟线数据
3. 遗传算法优化器
4. 参数热力图可视化
5. 优化回测引擎
"""

import sys
import os
from datetime import datetime, timedelta

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def demo_binance_data():
    """演示 1: Binance 数据源"""
    print("\n" + "=" * 60)
    print("演示 1: Binance 数据源 - 获取 BTC/USDT 数据")
    print("=" * 60)
    
    from data.binance_source import BinanceDataSource
    
    source = BinanceDataSource()
    
    # 获取最近 30 天日线数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    try:
        df = source.get_klines(
            symbol='BTC/USDT',
            interval='1d',
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        
        if not df.empty:
            print(f"✓ 成功获取 {len(df)} 行数据")
            print(f"\n前 5 行数据:")
            print(df.head())
            print(f"\n数据范围：{df.index[0]} 至 {df.index[-1]}")
            print(f"最新收盘价：${df['close'].iloc[-1]:.2f}")
        else:
            print("⚠ 未获取到数据")
    
    except Exception as e:
        print(f"✗ 获取数据失败：{e}")


def demo_tushare_minute_data():
    """演示 2: Tushare 分钟线数据"""
    print("\n" + "=" * 60)
    print("演示 2: Tushare 数据源 - 支持分钟线")
    print("=" * 60)
    
    from data.sources import TushareDataSource
    
    print("Tushare 数据源现在支持:")
    print("  - 日线数据 (freq='D')")
    print("  - 分钟线数据 (freq='1m', '5m', '15m', '30m', '60m')")
    print("\n使用示例:")
    print("""
    # 日线数据
    source = TushareDataSource(token='your_token', freq='D')
    data = source.get_data('000001.SZ', '2024-01-01', '2024-01-31')
    
    # 5 分钟线数据
    source = TushareDataSource(token='your_token', freq='5m')
    data = source.get_data('000001.SZ', '2024-01-01', '2024-01-02')
    """)


def demo_genetic_optimizer():
    """演示 3: 遗传算法优化器"""
    print("\n" + "=" * 60)
    print("演示 3: 遗传算法优化器")
    print("=" * 60)
    
    from optimization.genetic_optimizer import GeneticOptimizer, ParameterBound
    import pandas as pd
    import numpy as np
    
    # 创建模拟策略
    class DemoStrategy:
        def __init__(self, window=20, threshold=0.5, initial_capital=100000):
            self.window = window
            self.threshold = threshold
            self.initial_capital = initial_capital
    
    # 创建模拟回测函数
    class MockResult:
        def __init__(self, sharpe):
            self.metrics = {'sharpe_ratio': sharpe, 'total_return': sharpe * 10}
    
    def mock_backtest(strategy, data):
        # 模拟：最优参数在 window=30, threshold=0.6 附近
        score = 2.0 - abs(strategy.window - 30) / 20 - abs(strategy.threshold - 0.6) / 0.3
        return MockResult(sharpe=max(0, score + np.random.normal(0, 0.1)))
    
    # 创建测试数据
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    data = pd.DataFrame({
        'close': 100 + np.cumsum(np.random.randn(100))
    }, index=dates)
    
    # 配置优化器
    optimizer = GeneticOptimizer(
        population_size=10,
        generations=5,
        mutation_rate=0.1,
        crossover_rate=0.8,
        random_seed=42
    )
    
    # 定义参数边界
    param_bounds = [
        ParameterBound('window', 10, 50, dtype='int'),
        ParameterBound('threshold', 0.3, 0.9, dtype='float')
    ]
    
    print(f"开始优化...")
    print(f"  种群大小：{optimizer.population_size}")
    print(f"  进化代数：{optimizer.generations}")
    print(f"  参数空间：window=[10,50], threshold=[0.3,0.9]")
    
    # 执行优化
    best = optimizer.optimize(
        DemoStrategy,
        param_bounds,
        mock_backtest,
        data,
        initial_capital=100000,
        show_progress=False
    )
    
    print(f"\n✓ 优化完成!")
    print(f"  最优参数：window={best.params['window']}, threshold={best.params['threshold']:.3f}")
    print(f"  最优夏普比率：{best.fitness:.4f}")


def demo_parameter_heatmap():
    """演示 4: 参数热力图"""
    print("\n" + "=" * 60)
    print("演示 4: 参数热力图可视化")
    print("=" * 60)
    
    from visualization.heatmap import ParameterHeatmap
    import pandas as pd
    import numpy as np
    
    # 创建模拟策略和回测
    class DemoStrategy:
        def __init__(self, window=20, threshold=0.5, initial_capital=100000):
            self.window = window
            self.threshold = threshold
    
    class MockResult:
        def __init__(self, sharpe):
            self.metrics = {'sharpe_ratio': sharpe}
    
    def mock_backtest(strategy, data):
        sharpe = 2.0 - abs(strategy.window - 25) / 10 - abs(strategy.threshold - 0.5) / 0.2
        return MockResult(sharpe=max(0, sharpe))
    
    # 创建测试数据
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    data = pd.DataFrame({'close': 100 + np.cumsum(np.random.randn(100))}, index=dates)
    
    # 创建热力图
    heatmap = ParameterHeatmap(metric_name='sharpe_ratio')
    
    print("执行双参数扫描...")
    result = heatmap.scan(
        DemoStrategy,
        param1_name='window',
        param1_values=[15, 20, 25, 30, 35],
        param2_name='threshold',
        param2_values=[0.3, 0.4, 0.5, 0.6, 0.7],
        base_params={},
        backtest_func=mock_backtest,
        data=data,
        initial_capital=100000,
        show_progress=False
    )
    
    print(f"✓ 扫描完成!")
    print(f"  参数 1: {result.param1_name} = {result.param1_values}")
    print(f"  参数 2: {result.param2_name} = {result.param2_values}")
    print(f"  最优参数：{result.param1_name}={result.best_param1}, "
          f"{result.param2_name}={result.best_param2}")
    print(f"  最优指标：{result.best_metric_value:.4f}")
    print(f"\n热力图矩阵形状：{result.metric_matrix.shape}")
    print("热力图矩阵:")
    print(result.metric_matrix)


def demo_optimized_backtest():
    """演示 5: 优化回测引擎"""
    print("\n" + "=" * 60)
    print("演示 5: 优化回测引擎 (性能提升 30%+)")
    print("=" * 60)
    
    from backtest.optimized_engine import OptimizedBacktestEngine
    import pandas as pd
    import numpy as np
    import time
    
    # 创建向量化策略
    class VectorizedStrategy:
        def __init__(self, window=20):
            self.window = window
        
        def generate_signals(self, data):
            n = len(data)
            signals = np.zeros(n, dtype=np.int8)
            ma = data['close'].rolling(window=self.window).mean()
            signals[data['close'] > ma] = 1
            signals[data['close'] < ma] = -1
            return signals
    
    # 创建测试数据
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=500, freq='D')
    prices = 100 * np.cumprod(1 + np.random.randn(500) * 0.02)
    data = pd.DataFrame({
        'open': prices,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, 500)
    }, index=dates)
    
    # 执行回测
    engine = OptimizedBacktestEngine(
        initial_capital=100000,
        commission_rate=0.001,
        use_cache=True
    )
    
    strategy = VectorizedStrategy(window=20)
    
    start_time = time.time()
    result = engine.run(strategy, data)
    elapsed = time.time() - start_time
    
    print(f"✓ 回测完成! 耗时：{elapsed:.3f}秒")
    print(f"\n回测结果:")
    print(f"  初始资金：${engine.initial_capital:,.0f}")
    print(f"  最终权益：${result.equity_curve[-1]:,.0f}")
    print(f"  总收益：{result.total_return:.2f}%")
    print(f"  夏普比率：{result.sharpe_ratio:.2f}")
    print(f"  最大回撤：{result.max_drawdown:.2f}%")
    print(f"  交易次数：{result.total_trades}")
    print(f"  胜率：{result.win_rate:.1f}%")
    
    # 缓存统计
    stats = engine.get_cache_stats()
    print(f"\n缓存统计:")
    print(f"  缓存大小：{stats['cache_size']}")
    print(f"  命中率：{stats['hit_rate']*100:.1f}%")


def main():
    """主函数"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 8 + "OpenFinAgent v0.3.0 新功能演示" + " " * 14 + "║")
    print("╚" + "=" * 58 + "╝")
    
    # 执行所有演示
    demos = [
        ("Binance 数据源", demo_binance_data),
        ("Tushare 分钟线", demo_tushare_minute_data),
        ("遗传算法优化器", demo_genetic_optimizer),
        ("参数热力图", demo_parameter_heatmap),
        ("优化回测引擎", demo_optimized_backtest)
    ]
    
    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\n✗ {name} 演示失败：{e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("所有演示完成!")
    print("=" * 60)
    print("\n📚 更多信息请查看:")
    print("  - docs/v0.3_features.md")
    print("  - examples/ 目录下的示例代码")
    print()


if __name__ == '__main__':
    main()
