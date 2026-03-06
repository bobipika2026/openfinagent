#!/usr/bin/env python3
"""
OpenFinAgent v0.3.0 性能基准测试

测试项目:
1. 优化回测引擎 vs 基础引擎 - 速度对比
2. 内存使用测试
3. 缓存机制性能
4. 并行回测性能
5. 大数据集扩展性测试
"""

import sys
import time
import tracemalloc
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pandas as pd
import numpy as np

results = {
    'benchmarks': [],
    'summary': {}
}

def generate_test_data(n_days: int, seed: int = 42) -> pd.DataFrame:
    """生成测试数据"""
    np.random.seed(seed)
    return pd.DataFrame({
        'open': np.random.rand(n_days) * 100 + 50,
        'high': np.random.rand(n_days) * 100 + 50,
        'low': np.random.rand(n_days) * 50,
        'close': np.random.rand(n_days) * 100 + 50,
        'volume': np.random.rand(n_days) * 10000
    }, index=pd.date_range('2020-01-01', periods=n_days, freq='D'))


class SimpleTestStrategy:
    """简单测试策略"""
    def __init__(self, window=20, initial_capital=100000):
        self.window = window
        self.initial_capital = initial_capital
    
    def generate_signals(self, data):
        signals = np.zeros(len(data), dtype=np.int8)
        if len(data) > self.window:
            ma = data['close'].rolling(self.window).mean()
            signals[data['close'] > ma] = 1
            signals[data['close'] < ma] = -1
        return signals


def benchmark_engine_speed():
    """测试 1: 优化引擎 vs 基础引擎速度对比"""
    print("\n" + "="*60)
    print("基准测试 1: 回测引擎速度对比")
    print("="*60)
    
    from backtest.optimized_engine import OptimizedBacktestEngine, optimized_backtest
    from backtest.engine import BacktestEngine
    
    test_data = generate_test_data(500)
    
    # 优化引擎
    class OptStrategy:
        def __init__(self, window=20):
            self.window = window
            self.initial_capital = 100000
        def generate_signals(self, data):
            signals = np.zeros(len(data), dtype=np.int8)
            if len(data) > self.window:
                ma = data['close'].rolling(self.window).mean()
                signals[data['close'] > ma] = 1
                signals[data['close'] < ma] = -1
            return signals
    
    opt_strategy = OptStrategy(window=20)
    start = time.time()
    opt_result = optimized_backtest(opt_strategy, test_data, initial_capital=100000)
    opt_time = time.time() - start
    
    # 基础引擎 (使用 MockDataSource 生成兼容数据)
    from strategy.base import BaseStrategy
    class BaseTestStrategy(BaseStrategy):
        def __init__(self, window=20):
            super().__init__(initial_capital=100000)
            self.window = window
        def generate_signals(self, data):
            signals = np.zeros(len(data), dtype=np.int8)
            if len(data) > self.window:
                ma = data['close'].rolling(self.window).mean()
                signals[data['close'] > ma] = 1
                signals[data['close'] < ma] = -1
            return signals
        def on_bar(self, data, index):
            return None
    
    base_strategy = BaseTestStrategy(window=20)
    base_engine = BacktestEngine(commission_rate=0.001)
    start = time.time()
    base_result = base_engine.run(base_strategy, test_data, show_progress=False)
    base_time = time.time() - start
    
    speedup = base_time / opt_time if opt_time > 0 else float('inf')
    
    print(f"优化引擎：{opt_time:.4f}s")
    print(f"基础引擎：{base_time:.4f}s")
    print(f"加速比：{speedup:.2f}x")
    
    results['benchmarks'].append({
        'name': '引擎速度对比',
        'optimized_sec': opt_time,
        'baseline_sec': base_time,
        'speedup': speedup,
        'data_points': 500
    })
    
    return speedup > 1.0


def benchmark_memory_usage():
    """测试 2: 内存使用测试"""
    print("\n" + "="*60)
    print("基准测试 2: 内存使用")
    print("="*60)
    
    from backtest.optimized_engine import optimized_backtest
    
    test_sizes = [100, 500, 1000, 2000]
    memory_results = []
    
    for size in test_sizes:
        test_data = generate_test_data(size)
        strategy = SimpleTestStrategy(window=20)
        
        tracemalloc.start()
        _ = optimized_backtest(strategy, test_data, initial_capital=100000)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        peak_mb = peak / (1024 * 1024)
        memory_results.append({'days': size, 'peak_mb': peak_mb})
        print(f"{size}天数据：峰值内存 {peak_mb:.2f}MB")
    
    results['benchmarks'].append({
        'name': '内存使用',
        'data': memory_results
    })
    
    # 检查是否都小于 100MB
    all_under_limit = all(m['peak_mb'] < 100 for m in memory_results)
    return all_under_limit


def benchmark_cache_performance():
    """测试 3: 缓存机制性能"""
    print("\n" + "="*60)
    print("基准测试 3: 缓存性能")
    print("="*60)
    
    from backtest.optimized_engine import OptimizedBacktestEngine
    
    test_data = generate_test_data(500)
    strategy = SimpleTestStrategy(window=20)
    
    engine = OptimizedBacktestEngine(initial_capital=100000, use_cache=True)
    
    # 第一次运行 (缓存未命中)
    start = time.time()
    _ = engine.run(strategy, test_data)
    first_time = time.time() - start
    
    # 第二次运行 (缓存命中)
    start = time.time()
    _ = engine.run(strategy, test_data)
    second_time = time.time() - start
    
    cache_stats = engine.get_cache_stats()
    speedup = first_time / second_time if second_time > 0 else float('inf')
    
    print(f"首次运行：{first_time:.4f}s (缓存未命中)")
    print(f"缓存命中：{second_time:.4f}s")
    print(f"缓存加速比：{speedup:.2f}x")
    print(f"缓存命中率：{cache_stats['hit_rate']:.2%}")
    
    results['benchmarks'].append({
        'name': '缓存性能',
        'first_run_sec': first_time,
        'cached_run_sec': second_time,
        'speedup': speedup,
        'hit_rate': cache_stats['hit_rate']
    })
    
    return speedup > 2.0


def benchmark_parallel_backtest():
    """测试 4: 并行回测性能"""
    print("\n" + "="*60)
    print("基准测试 4: 并行回测")
    print("="*60)
    
    from backtest.optimized_engine import OptimizedBacktestEngine
    
    test_data = generate_test_data(500)
    engine = OptimizedBacktestEngine(initial_capital=100000)
    
    # 生成参数组合
    param_combinations = [
        {'window': 10},
        {'window': 20},
        {'window': 30},
        {'window': 40},
        {'window': 50}
    ]
    
    # 串行回测
    start = time.time()
    serial_results = []
    for params in param_combinations:
        strategy = SimpleTestStrategy(**params)
        result = engine.run(strategy, test_data)
        serial_results.append(result)
    serial_time = time.time() - start
    
    # 并行回测
    start = time.time()
    parallel_results = engine.run_parallel(
        strategy_class=SimpleTestStrategy,
        param_combinations=param_combinations,
        data=test_data,
        n_jobs=2
    )
    parallel_time = time.time() - start
    
    speedup = serial_time / parallel_time if parallel_time > 0 else float('inf')
    
    print(f"串行回测：{serial_time:.4f}s")
    print(f"并行回测 (2 进程): {parallel_time:.4f}s")
    print(f"加速比：{speedup:.2f}x")
    
    results['benchmarks'].append({
        'name': '并行回测',
        'serial_sec': serial_time,
        'parallel_sec': parallel_time,
        'speedup': speedup,
        'combinations': len(param_combinations)
    })
    
    return speedup > 1.0


def benchmark_scalability():
    """测试 5: 大数据集扩展性测试"""
    print("\n" + "="*60)
    print("基准测试 5: 扩展性测试")
    print("="*60)
    
    from backtest.optimized_engine import optimized_backtest
    
    test_sizes = [100, 500, 1000, 2000, 5000]
    time_results = []
    
    for size in test_sizes:
        test_data = generate_test_data(size)
        strategy = SimpleTestStrategy(window=20)
        
        start = time.time()
        result = optimized_backtest(strategy, test_data, initial_capital=100000)
        elapsed = time.time() - start
        
        time_results.append({'days': size, 'elapsed_sec': elapsed})
        print(f"{size}天数据：{elapsed:.4f}s, 交易次数：{result.total_trades}")
    
    results['benchmarks'].append({
        'name': '扩展性',
        'data': time_results
    })
    
    # 检查 5000 天数据是否在 5 秒内完成
    return time_results[-1]['elapsed_sec'] < 5.0


def save_report(path: str):
    """保存性能基准报告"""
    report = f"""# OpenFinAgent v0.3.0 性能基准测试报告

**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**测试版本**: v0.3.0

---

## 测试汇总

"""
    
    for benchmark in results['benchmarks']:
        report += f"### {benchmark['name']}\n\n"
        
        if benchmark['name'] == '引擎速度对比':
            report += f"- **优化引擎**: {benchmark['optimized_sec']:.4f}s\n"
            report += f"- **基础引擎**: {benchmark['baseline_sec']:.4f}s\n"
            report += f"- **加速比**: {benchmark['speedup']:.2f}x\n"
            report += f"- **测试数据**: {benchmark['data_points']} 天\n\n"
        
        elif benchmark['name'] == '内存使用':
            report += "| 数据量 (天) | 峰值内存 (MB) |\n"
            report += "|-----------|---------------|\n"
            for item in benchmark['data']:
                report += f"| {item['days']} | {item['peak_mb']:.2f} |\n"
            report += "\n"
        
        elif benchmark['name'] == '缓存性能':
            report += f"- **首次运行**: {benchmark['first_run_sec']:.4f}s\n"
            report += f"- **缓存命中**: {benchmark['cached_run_sec']:.4f}s\n"
            report += f"- **加速比**: {benchmark['speedup']:.2f}x\n"
            report += f"- **命中率**: {benchmark['hit_rate']:.2%}\n\n"
        
        elif benchmark['name'] == '并行回测':
            report += f"- **串行回测**: {benchmark['serial_sec']:.4f}s\n"
            report += f"- **并行回测**: {benchmark['parallel_sec']:.4f}s\n"
            report += f"- **加速比**: {benchmark['speedup']:.2f}x\n"
            report += f"- **参数组合数**: {benchmark['combinations']}\n\n"
        
        elif benchmark['name'] == '扩展性':
            report += "| 数据量 (天) | 耗时 (秒) |\n"
            report += "|-----------|----------|\n"
            for item in benchmark['data']:
                report += f"| {item['days']} | {item['elapsed_sec']:.4f} |\n"
            report += "\n"
    
    # 总体评价
    report += """---

## 性能评价

### 回测引擎优化
"""
    engine_benchmark = next((b for b in results['benchmarks'] if b['name'] == '引擎速度对比'), None)
    if engine_benchmark:
        if engine_benchmark['speedup'] >= 1.5:
            report += f"✅ **优秀**: 优化引擎速度提升 {engine_benchmark['speedup']:.1f}x，达到预期目标 (50%+)\n"
        elif engine_benchmark['speedup'] >= 1.2:
            report += f"⚠️ **良好**: 优化引擎速度提升 {engine_benchmark['speedup']:.1f}x，基本达到预期\n"
        else:
            report += f"❌ **待改进**: 优化引擎仅提升 {engine_benchmark['speedup']:.1f}x，未达预期\n"
    
    report += "\n### 内存使用\n"
    memory_benchmark = next((b for b in results['benchmarks'] if b['name'] == '内存使用'), None)
    if memory_benchmark:
        max_memory = max(item['peak_mb'] for item in memory_benchmark['data'])
        if max_memory < 50:
            report += f"✅ **优秀**: 峰值内存 {max_memory:.1f}MB，非常高效\n"
        elif max_memory < 100:
            report += f"⚠️ **良好**: 峰值内存 {max_memory:.1f}MB，符合预期\n"
        else:
            report += f"❌ **待改进**: 峰值内存 {max_memory:.1f}MB，超出预期\n"
    
    report += "\n### 缓存机制\n"
    cache_benchmark = next((b for b in results['benchmarks'] if b['name'] == '缓存性能'), None)
    if cache_benchmark:
        if cache_benchmark['speedup'] >= 5:
            report += f"✅ **优秀**: 缓存加速 {cache_benchmark['speedup']:.1f}x，效果显著\n"
        elif cache_benchmark['speedup'] >= 2:
            report += f"⚠️ **良好**: 缓存加速 {cache_benchmark['speedup']:.1f}x，有效优化\n"
        else:
            report += f"❌ **待改进**: 缓存加速仅 {cache_benchmark['speedup']:.1f}x\n"
    
    report += "\n### 并行处理\n"
    parallel_benchmark = next((b for b in results['benchmarks'] if b['name'] == '并行回测'), None)
    if parallel_benchmark:
        if parallel_benchmark['speedup'] >= 1.5:
            report += f"✅ **优秀**: 并行加速 {parallel_benchmark['speedup']:.1f}x，效果良好\n"
        else:
            report += f"⚠️ **一般**: 并行加速 {parallel_benchmark['speedup']:.1f}x，有优化空间\n"
    
    report += "\n---\n"
    report += f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(report, encoding='utf-8')


def main():
    """执行所有基准测试"""
    print("\n" + "="*60)
    print("OpenFinAgent v0.3.0 性能基准测试")
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    start_time = time.time()
    
    results_list = []
    
    # 执行测试
    results_list.append(("引擎速度对比", benchmark_engine_speed()))
    results_list.append(("内存使用", benchmark_memory_usage()))
    results_list.append(("缓存性能", benchmark_cache_performance()))
    results_list.append(("并行回测", benchmark_parallel_backtest()))
    results_list.append(("扩展性", benchmark_scalability()))
    
    total_elapsed = time.time() - start_time
    
    # 汇总
    passed = sum(1 for _, result in results_list if result)
    total = len(results_list)
    
    print("\n" + "="*60)
    print("基准测试汇总")
    print("="*60)
    print(f"通过：{passed}/{total}")
    print(f"总耗时：{total_elapsed:.2f}s")
    
    for name, result in results_list:
        status = "✓" if result else "✗"
        print(f"  {status} {name}")
    
    # 保存报告
    report_path = '/root/.openclaw/workspace/projects/tradeflow-ai/tests/reports/performance_benchmark.md'
    save_report(report_path)
    print(f"\n报告已保存：{report_path}")
    
    results['summary'] = {
        'passed': passed,
        'total': total,
        'elapsed_sec': total_elapsed,
        'timestamp': datetime.now().isoformat()
    }
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
