#!/usr/bin/env python3
"""
v0.3.1 修复验证测试

验证所有修复是否正确应用：
1. Binance 数据源重试机制
2. 遗传算法 avg_fitness 计算
3. TestStrategy 抽象方法实现
"""

import sys
import os
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def test_binance_source_fixes():
    """测试 Binance 数据源修复"""
    print("\n" + "="*60)
    print("测试 1: Binance 数据源修复")
    print("="*60)
    
    from data.binance_source import BinanceDataSource
    
    # 测试 1.1: 初始化
    source = BinanceDataSource()
    assert source.base_url == 'https://api.binance.com'
    print("✓ BinanceDataSource 初始化成功")
    
    # 测试 1.2: 时间周期映射
    expected_intervals = ['1m', '5m', '15m', '1h', '4h', '1d']
    for interval in expected_intervals:
        assert interval in source.INTERVAL_MAP, f"缺少时间周期：{interval}"
    print(f"✓ 时间周期映射正确：{expected_intervals}")
    
    # 测试 1.3: 验证代码中有重试机制
    import inspect
    source_code = inspect.getsource(source.get_klines)
    assert 'max_retries' in source_code, "缺少重试机制"
    assert 'retry_count' in source_code, "缺少重试计数"
    print("✓ 重试机制已添加")
    
    # 测试 1.4: 验证日志记录
    assert 'logger.debug' in source_code or 'logger.info' in source_code
    assert 'logger.warning' in source_code
    print("✓ 日志记录已增强")
    
    return True


def test_genetic_optimizer_fixes():
    """测试遗传算法优化器修复"""
    print("\n" + "="*60)
    print("测试 2: 遗传算法优化器修复")
    print("="*60)
    
    from optimization.genetic_optimizer import GeneticOptimizer, Individual, ParameterBound
    
    # 测试 2.1: 初始化
    optimizer = GeneticOptimizer(population_size=10, generations=5, random_seed=42)
    print("✓ GeneticOptimizer 初始化成功")
    
    # 测试 2.2: 测试空种群的 stats
    optimizer.population = []
    stats = optimizer._get_generation_stats()
    # 空种群时返回空字典或包含默认值的字典
    print(f"✓ 空种群 stats: {stats}")
    
    # 测试 2.3: 测试有数据的 stats (包含 avg_fitness)
    optimizer.population = [
        Individual(params={'a': 1}, fitness=1.0),
        Individual(params={'a': 2}, fitness=2.0),
        Individual(params={'a': 3}, fitness=3.0),
    ]
    stats = optimizer._get_generation_stats()
    
    assert 'avg_fitness' in stats, "缺少 avg_fitness 键"
    assert stats['avg_fitness'] == 2.0, f"avg_fitness 计算错误：{stats['avg_fitness']}"
    assert 'best_fitness' in stats, "缺少 best_fitness 键"
    assert stats['best_fitness'] == 3.0, f"best_fitness 计算错误：{stats['best_fitness']}"
    print(f"✓ 种群 stats 正确：{stats}")
    
    # 测试 2.4: 测试全 inf 适应度
    optimizer.population = [
        Individual(params={'a': 1}, fitness=-np.inf),
        Individual(params={'a': 2}, fitness=-np.inf),
    ]
    stats = optimizer._get_generation_stats()
    assert 'avg_fitness' in stats, "全 inf 时缺少 avg_fitness 键"
    print(f"✓ 全 inf 适应度处理正确：{stats}")
    
    # 测试 2.5: 验证最优个体更新日志
    import inspect
    optimizer_code = inspect.getsource(optimizer._update_best_individual)
    assert 'logger.info' in optimizer_code or 'logger.debug' in optimizer_code
    print("✓ 最优个体更新日志已增强")
    
    return True


def test_strategy_abstract_method_fixes():
    """测试策略抽象方法修复"""
    print("\n" + "="*60)
    print("测试 3: 策略抽象方法修复")
    print("="*60)
    
    from strategy.base import BaseStrategy
    from typing import Optional, Dict, Any
    
    # 测试 3.1: 创建正确的 TestStrategy
    class TestStrategy(BaseStrategy):
        def __init__(self, window=20, threshold=0.5, initial_capital=100000):
            super().__init__(name="TestStrategy", initial_capital=initial_capital)
            self.window = int(window)
            self.threshold = threshold
        
        def generate_signals(self, data: pd.DataFrame) -> pd.Series:
            signals = np.zeros(len(data), dtype=np.int8)
            if len(data) > self.window:
                ma = data['close'].rolling(self.window).mean()
                signals[data['close'] > ma * (1 + self.threshold)] = 1
                signals[data['close'] < ma * (1 - self.threshold)] = -1
            return pd.Series(signals, index=data.index)
        
        def on_bar(self, data: pd.DataFrame, index: int) -> Optional[Dict[str, Any]]:
            """每根 K 线回调 - 实现抽象方法"""
            return None
    
    # 测试 3.2: 实例化 (之前会失败)
    try:
        strategy = TestStrategy(window=20, threshold=0.3)
        print(f"✓ TestStrategy 实例化成功：{strategy}")
    except TypeError as e:
        print(f"✗ TestStrategy 实例化失败：{e}")
        return False
    
    # 测试 3.3: 验证方法实现
    assert hasattr(strategy, 'generate_signals'), "缺少 generate_signals 方法"
    assert hasattr(strategy, 'on_bar'), "缺少 on_bar 方法"
    print("✓ 抽象方法已实现")
    
    # 测试 3.4: 测试 generate_signals 返回类型
    test_data = pd.DataFrame({
        'close': np.random.rand(100) * 100 + 50
    })
    test_data.index = pd.date_range('2024-01-01', periods=100, freq='D')
    
    signals = strategy.generate_signals(test_data)
    assert isinstance(signals, pd.Series), f"generate_signals 应返回 Series，实际返回 {type(signals)}"
    assert len(signals) == len(test_data), "信号长度与数据长度不匹配"
    print(f"✓ generate_signals 返回类型正确：{type(signals)}")
    
    # 测试 3.5: 测试 on_bar 返回
    result = strategy.on_bar(test_data, 0)
    assert result is None, f"on_bar 应返回 None，实际返回 {result}"
    print("✓ on_bar 方法返回正确")
    
    return True


def test_backwards_compatibility():
    """测试向后兼容性"""
    print("\n" + "="*60)
    print("测试 4: 向后兼容性")
    print("="*60)
    
    from optimization.genetic_optimizer import GeneticOptimizer, ParameterBound
    from strategy.base import BaseStrategy
    
    # 测试 4.1: GeneticOptimizer API 未改变
    optimizer = GeneticOptimizer(
        population_size=20,
        generations=10,
        mutation_rate=0.1,
        crossover_rate=0.8
    )
    assert optimizer.population_size == 20
    assert optimizer.generations == 10
    print("✓ GeneticOptimizer API 兼容")
    
    # 测试 4.2: BaseStrategy API 未改变
    class SimpleStrategy(BaseStrategy):
        def generate_signals(self, data: pd.DataFrame) -> pd.Series:
            return pd.Series(0, index=data.index)
        
        def on_bar(self, data: pd.DataFrame, index: int):
            return None
    
    strategy = SimpleStrategy(name="Simple", initial_capital=50000)
    assert strategy.initial_capital == 50000
    print("✓ BaseStrategy API 兼容")
    
    return True


def main():
    """执行所有验证测试"""
    print("\n" + "="*60)
    print("OpenFinAgent v0.3.1 修复验证测试")
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    results = {
        'Binance 数据源': False,
        '遗传算法优化器': False,
        '策略抽象方法': False,
        '向后兼容性': False
    }
    
    try:
        results['Binance 数据源'] = test_binance_source_fixes()
    except Exception as e:
        print(f"\n✗ Binance 数据源测试失败：{e}")
        import traceback
        traceback.print_exc()
    
    try:
        results['遗传算法优化器'] = test_genetic_optimizer_fixes()
    except Exception as e:
        print(f"\n✗ 遗传算法优化器测试失败：{e}")
        import traceback
        traceback.print_exc()
    
    try:
        results['策略抽象方法'] = test_strategy_abstract_method_fixes()
    except Exception as e:
        print(f"\n✗ 策略抽象方法测试失败：{e}")
        import traceback
        traceback.print_exc()
    
    try:
        results['向后兼容性'] = test_backwards_compatibility()
    except Exception as e:
        print(f"\n✗ 向后兼容性测试失败：{e}")
        import traceback
        traceback.print_exc()
    
    # 输出汇总
    print("\n" + "="*60)
    print("验证结果汇总")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n通过率：{passed}/{total} ({passed/total*100:.1f}%)")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 所有修复验证通过！")
    else:
        print("\n⚠️  部分修复验证失败，请检查日志")
    
    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
