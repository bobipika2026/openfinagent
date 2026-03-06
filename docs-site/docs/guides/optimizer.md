# 优化器使用指南

> 🧠 智能参数优化，让策略性能更上一层楼

---

## 📋 概述

OpenFinAgent v0.3.0 引入了强大的**策略优化器**，包括**遗传算法优化器**和**参数热力图**工具。这些工具可以帮助你自动搜索最优参数组合，提升策略性能。

### 核心功能

| 工具 | 适用场景 | 优势 |
|------|---------|------|
| **遗传算法** | 多参数优化（3+ 参数） | 智能搜索、全局最优、并行计算 |
| **参数热力图** | 双参数可视化分析 | 直观展示、交互图表、敏感性分析 |

---

## 🧬 遗传算法优化器

### 原理简介

遗传算法（Genetic Algorithm）是一种模拟生物进化过程的优化算法：

```
初始化种群 → 评估适应度 → 选择 → 交叉 → 变异 → 新一代
     ↓
   循环迭代 N 代
     ↓
   输出最优个体
```

### 核心概念

- **个体（Individual）**：一组参数组合
- **种群（Population）**：多个个体的集合
- **适应度（Fitness）**：评估指标（如夏普比率）
- **选择（Selection）**：保留优秀个体
- **交叉（Crossover）**：父母参数组合生成子代
- **变异（Mutation）**：随机改变参数，增加多样性
- **精英保留（Elite）**：直接保留最优个体到下一代

---

## 🚀 快速开始

### 基础示例

```python
from optimization.genetic_optimizer import GeneticOptimizer, ParameterBound
from backtest.engine import BacktestEngine
from strategy.dual_ma import DualMAStrategy

# 1. 准备数据
data = ...  # 你的历史数据

# 2. 定义参数范围
param_bounds = [
    ParameterBound('short_window', 5, 20, dtype='int'),    # 短周期 5-20
    ParameterBound('long_window', 20, 60, dtype='int'),    # 长周期 20-60
]

# 3. 创建优化器
optimizer = GeneticOptimizer(
    population_size=50,      # 种群大小
    generations=100,         # 进化代数
    mutation_rate=0.1,       # 变异率
    crossover_rate=0.8,      # 交叉率
    elite_ratio=0.1,         # 精英保留比例
    optimization_metric='sharpe_ratio',  # 优化目标
    maximize=True,           # 最大化目标
    n_jobs=4,                # 并行进程数
)

# 4. 执行优化
best = optimizer.optimize(
    strategy_class=DualMAStrategy,
    parameter_bounds=param_bounds,
    backtest_func=lambda s, d: BacktestEngine().run(s, d),
    data=data,
    initial_capital=100000,
    show_progress=True
)

# 5. 查看结果
print(f"最优参数：{best.params}")
print(f"最优适应度：{best.fitness:.4f}")
print(f"详细指标：{best.metrics}")
```

### 输出示例

```
遗传算法优化器初始化：种群=50, 代数=100, 变异率=0.1
初始化种群...
代数 0/100: 最佳适应度=1.2345, 平均适应度=0.8765
代数 10/100: 最佳适应度=1.4567, 平均适应度=1.1234
代数 20/100: 最佳适应度=1.6789, 平均适应度=1.3456
...
优化完成：最佳适应度=1.8765, 参数={'short_window': 12, 'long_window': 35}

最优参数：{'short_window': 12, 'long_window': 35}
最优适应度：1.8765
详细指标：{'sharpe_ratio': 1.8765, 'total_return': 0.2345, 'max_drawdown': 0.0876}
```

---

## 📊 参数配置详解

### ParameterBound 参数边界

```python
ParameterBound(
    name='param_name',      # 参数名（必须与策略__init__参数名一致）
    min_val=10,             # 最小值
    max_val=100,            # 最大值
    step=5,                 # 步长（可选）
    dtype='int',            # 数据类型：'int', 'float', 'choice'
    choices=None            # 离散选择列表（当 dtype='choice' 时使用）
)
```

### 数据类型示例

```python
# 整数类型
ParameterBound('window', 10, 100, dtype='int')
ParameterBound('window', 10, 100, step=5, dtype='int')  # 带步长：10,15,20...100

# 浮点类型
ParameterBound('threshold', 0.1, 1.0, dtype='float')
ParameterBound('threshold', 0.1, 1.0, step=0.1, dtype='float')

# 离散选择
ParameterBound('ma_type', 0, 2, dtype='choice', choices=['sma', 'ema', 'wma'])
```

### 优化器参数

```python
GeneticOptimizer(
    # 种群相关
    population_size=50,      # 种群大小（建议 30-100）
    generations=100,         # 进化代数（建议 50-200）
    
    # 进化参数
    mutation_rate=0.1,       # 变异率（建议 0.05-0.2）
    crossover_rate=0.8,      # 交叉率（建议 0.7-0.9）
    elite_ratio=0.1,         # 精英保留比例（建议 0.05-0.2）
    
    # 优化目标
    optimization_metric='sharpe_ratio',  # 优化指标
    maximize=True,           # True=最大化，False=最小化
    
    # 性能
    n_jobs=4,                # 并行进程数（-1=所有 CPU 核心）
    random_seed=42,          # 随机种子（保证结果可复现）
)
```

---

## 💡 实战示例

### 示例 1：RSI 策略参数优化

```python
from optimization.genetic_optimizer import GeneticOptimizer, ParameterBound
from strategy.rsi_strategy import RSIStrategy
from backtest.engine import BacktestEngine
from data.sources import TushareDataSource

# 1. 获取数据
source = TushareDataSource(freq='5m')
data = source.get_data('000001.SZ', '2024-01-01', '2024-03-31')

# 2. 定义参数范围
param_bounds = [
    ParameterBound('rsi_period', 10, 25, dtype='int'),
    ParameterBound('oversold_threshold', 20, 40, dtype='int'),
    ParameterBound('overbought_threshold', 60, 80, dtype='int'),
]

# 3. 创建优化器
optimizer = GeneticOptimizer(
    population_size=30,
    generations=80,
    optimization_metric='sharpe_ratio',
    n_jobs=-1  # 使用所有 CPU 核心
)

# 4. 执行优化
best = optimizer.optimize(
    strategy_class=RSIStrategy,
    parameter_bounds=param_bounds,
    backtest_func=lambda s, d: BacktestEngine().run(s, d),
    data=data,
    initial_capital=100000
)

# 5. 使用最优参数回测
strategy = RSIStrategy(**best.params, initial_capital=100000)
result = BacktestEngine().run(strategy, data)

print(f"最优参数：{best.params}")
print(f"回测结果：{result.summary()}")
```

### 示例 2：多指标优化

```python
from optimization.genetic_optimizer import GeneticOptimizer, ParameterBound

# 优化多个指标
param_bounds = [
    ParameterBound('short_window', 5, 20, dtype='int'),
    ParameterBound('long_window', 20, 60, dtype='int'),
    ParameterBound('stop_loss', 0.05, 0.15, dtype='float'),
    ParameterBound('take_profit', 0.10, 0.30, dtype='float'),
]

optimizer = GeneticOptimizer(
    population_size=50,
    generations=100,
    optimization_metric='sharpe_ratio',  # 可以改为 'total_return', 'calmar_ratio' 等
)

best = optimizer.optimize(...)

# 查看不同指标的表现
print(f"夏普比率：{best.metrics.get('sharpe_ratio', 0):.2f}")
print(f"总收益率：{best.metrics.get('total_return', 0):.2%}")
print(f"最大回撤：{best.metrics.get('max_drawdown', 0):.2%}")
print(f"胜率：{best.metrics.get('win_rate', 0):.2%}")
```

### 示例 3：导出优化结果

```python
# 导出所有个体的详细数据
optimizer.export_results('optimization_results.csv')

# 读取结果
import pandas as pd
results = pd.read_csv('optimization_results.csv')

# 分析
print(results.describe())
print(results.nlargest(10, 'fitness'))  # 前 10 名

# 可视化
import matplotlib.pyplot as plt

# 适应度随进化代数的变化
history = optimizer.get_history()
plt.figure(figsize=(12, 6))
plt.plot(history['generation'], history['best_fitness'], label='最佳适应度')
plt.plot(history['generation'], history['avg_fitness'], label='平均适应度')
plt.xlabel('代数')
plt.ylabel('适应度')
plt.title('遗传算法进化过程')
plt.legend()
plt.grid(True)
plt.savefig('evolution.png')
plt.show()
```

---

## 🔥 参数热力图

### 双参数扫描

```python
from visualization.heatmap import ParameterHeatmap
from backtest.engine import BacktestEngine
from strategy.dual_ma import DualMAStrategy

# 1. 准备数据
data = ...  # 你的历史数据

# 2. 创建热力图生成器
heatmap = ParameterHeatmap(
    metric_name='sharpe_ratio',  # 要可视化的指标
    maximize=True,
    cmap='RdYlGn'  # 颜色映射
)

# 3. 执行双参数扫描
result = heatmap.scan(
    strategy_class=DualMAStrategy,
    param1_name='short_window',
    param1_values=[5, 10, 15, 20],
    param2_name='long_window',
    param2_values=[20, 30, 40, 50, 60],
    base_params={},  # 其他固定参数
    backtest_func=lambda s, d: BacktestEngine().run(s, d),
    data=data,
    initial_capital=100000,
    show_progress=True
)

# 4. 查看结果
print(f"最优 short_window: {result.best_param1}")
print(f"最优 long_window: {result.best_param2}")
print(f"最佳夏普比率：{result.best_metric_value:.2f}")
```

### 绘制热力图

```python
# 绘制标准热力图
heatmap.plot(
    result,
    figsize=(10, 8),
    title='双均线策略参数热力图',
    annotate=True,  # 标注数值
    save_path='heatmap.png',
    show=True
)
```

![参数热力图示例](../assets/images/heatmap-example.png)

### 绘制等高线图

```python
# 绘制等高线图
heatmap.plot_contour(
    result,
    figsize=(10, 8),
    levels=20,  # 等高线级别数
    title='参数敏感性分析',
    save_path='contour.png'
)
```

### 交互式热力图（Plotly）

```python
# 创建交互式图表
fig = heatmap.create_interactive(
    result,
    title='交互式参数热力图'
)

# 显示或保存
fig.show()
fig.write_html('interactive_heatmap.html')
```

---

## ⚡ 性能优化

### 并行计算

```python
# 使用多进程并行评估
optimizer = GeneticOptimizer(
    n_jobs=-1,  # 使用所有 CPU 核心
    population_size=50,
)

# 或者指定进程数
optimizer = GeneticOptimizer(n_jobs=4)
```

### 缓存机制

```python
from backtest.optimized_engine import OptimizedBacktestEngine

# 启用缓存，避免重复计算
engine = OptimizedBacktestEngine(use_cache=True)

def cached_backtest(strategy, data):
    return engine.run(strategy, data)

# 使用缓存的回测函数进行优化
best = optimizer.optimize(
    strategy_class=MyStrategy,
    parameter_bounds=param_bounds,
    backtest_func=cached_backtest,  # 使用缓存
    data=data
)
```

### 减少搜索空间

```python
# ❌ 搜索空间过大（100 × 100 × 100 = 1,000,000 种组合）
param_bounds = [
    ParameterBound('param1', 1, 100, dtype='int'),
    ParameterBound('param2', 1, 100, dtype='int'),
    ParameterBound('param3', 1, 100, dtype='int'),
]

# ✅ 使用步长减少搜索空间（10 × 10 × 10 = 1,000 种组合）
param_bounds = [
    ParameterBound('param1', 1, 100, step=10, dtype='int'),
    ParameterBound('param2', 1, 100, step=10, dtype='int'),
    ParameterBound('param3', 1, 100, step=10, dtype='int'),
]
```

---

## 📈 优化技巧

### 1. 选择合适的优化指标

```python
# 夏普比率（风险调整后收益）
optimizer = GeneticOptimizer(optimization_metric='sharpe_ratio')

# 总收益率
optimizer = GeneticOptimizer(optimization_metric='total_return')

# 卡玛比率（收益/最大回撤）
optimizer = GeneticOptimizer(optimization_metric='calmar_ratio')

# 索提诺比率（下行风险调整）
optimizer = GeneticOptimizer(optimization_metric='sortino_ratio')

# 最大回撤（最小化）
optimizer = GeneticOptimizer(
    optimization_metric='max_drawdown',
    maximize=False  # 最小化回撤
)
```

### 2. 分阶段优化

```python
# 第一阶段：粗调（大范围、大步长）
param_bounds_coarse = [
    ParameterBound('window', 5, 100, step=10, dtype='int'),
]

optimizer_coarse = GeneticOptimizer(generations=50)
best_coarse = optimizer_coarse.optimize(...)

# 第二阶段：精调（小范围、小步长）
best_window = best_coarse.params['window']
param_bounds_fine = [
    ParameterBound('window', best_window - 5, best_window + 5, step=1, dtype='int'),
]

optimizer_fine = GeneticOptimizer(generations=100)
best_fine = optimizer_fine.optimize(...)
```

### 3. 交叉验证

```python
from sklearn.model_selection import TimeSeriesSplit

# 将数据分为训练集和验证集
tscv = TimeSeriesSplit(n_splits=3)

def cv_backtest(strategy, data):
    scores = []
    for train_idx, test_idx in tscv.split(data):
        train_data = data.iloc[train_idx]
        test_data = data.iloc[test_idx]
        
        result = BacktestEngine().run(strategy, train_data)
        # 在测试集上验证
        scores.append(result.metrics.get('sharpe_ratio', 0))
    
    return np.mean(scores)  # 返回平均分数

# 使用交叉验证进行优化
best = optimizer.optimize(
    strategy_class=MyStrategy,
    parameter_bounds=param_bounds,
    backtest_func=cv_backtest,  # 使用交叉验证
    data=data
)
```

---

## ⚠️ 注意事项

### 1. 过拟合风险

遗传算法容易找到在历史数据上表现很好但在未来失效的参数。

**避免方法：**

- 使用足够长的历史数据
- 留出验证集进行测试
- 使用交叉验证
- 选择稳健的指标（如夏普比率而非总收益率）
- 限制参数搜索范围

```python
# ✅ 推荐做法
# 1. 使用 2-3 年数据
data = source.get_data('000001.SZ', '2021-01-01', '2023-12-31')

# 2. 分为训练集和测试集
train_data = data[data.index < '2023-01-01']
test_data = data[data.index >= '2023-01-01']

# 3. 在训练集上优化
best = optimizer.optimize(..., data=train_data)

# 4. 在测试集上验证
strategy = MyStrategy(**best.params)
test_result = BacktestEngine().run(strategy, test_data)
```

### 2. 计算资源

```python
# 估算计算量
# 总评估次数 = population_size × generations

# 示例：50 × 100 = 5000 次回测
# 假设每次回测 1 秒，总共需要 5000 秒 ≈ 1.4 小时

# 优化建议：
# 1. 使用并行计算（n_jobs=-1）
# 2. 减少种群大小和代数
# 3. 使用缓存
# 4. 使用优化后的回测引擎
```

### 3. 参数边界设置

```python
# ❌ 边界过大，搜索效率低
ParameterBound('window', 1, 1000, dtype='int')

# ✅ 基于经验设置合理边界
ParameterBound('window', 10, 100, dtype='int')

# ✅ 使用步长减少搜索空间
ParameterBound('window', 10, 100, step=5, dtype='int')
```

---

## 🐛 常见问题

### Q1: 优化结果不稳定

**原因：** 随机种子不同或种群太小

**解决：**

```python
# 设置随机种子保证可复现
optimizer = GeneticOptimizer(random_seed=42)

# 增加种群大小
optimizer = GeneticOptimizer(population_size=100)

# 增加进化代数
optimizer = GeneticOptimizer(generations=200)
```

### Q2: 优化速度太慢

**解决：**

```python
# 1. 使用并行计算
optimizer = GeneticOptimizer(n_jobs=-1)

# 2. 减少搜索空间
param_bounds = [
    ParameterBound('window', 10, 50, step=5, dtype='int'),  # 减少候选值
]

# 3. 使用缓存
engine = OptimizedBacktestEngine(use_cache=True)

# 4. 减少种群和代数
optimizer = GeneticOptimizer(population_size=30, generations=50)
```

### Q3: 最优参数在边界上

**原因：** 搜索范围不够

**解决：**

```python
# 如果最优参数在边界，扩大搜索范围
# 例如最优 short_window=20（边界也是 20）
param_bounds = [
    ParameterBound('short_window', 5, 30, dtype='int'),  # 扩大上限
]
```

---

## 📚 相关文档

- [Binance 数据源](binance-data.md) - 数据获取
- [Tushare 数据源](tushare-data.md) - A 股数据
- [回测教程](../tutorials/backtesting.md) - 回测基础

---

## 🔗 参考链接

- [遗传算法 Wikipedia](https://zh.wikipedia.org/wiki/遗传算法)
- [参数优化最佳实践](https://www.quantstart.com/articles/Strategy-Optimization-with-Genetic-Algorithms-in-Python/)
- [OpenFinAgent GitHub](https://github.com/bobipika2026/openfinagent)

---

_最后更新：2026 年 3 月 6 日_
