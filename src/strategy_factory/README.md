# 策略工厂模块 (Strategy Factory)

策略工厂模块实现了自然语言创建策略、自动回测、自动入库功能。

## 功能特性

1. **自然语言创建策略** - 通过中文描述自动生成可执行的策略代码
2. **支持多种策略类型** - 均线交叉、动量策略、布林带、RSI
3. **自动回测集成** - 创建策略后自动调用回测引擎
4. **智能评分入库** - 评分>=60 自动发布到策略商店
5. **遗传算法优化** - 自动优化策略参数提升性能

## 快速开始

### 1. 从自然语言创建策略

```python
from strategy_factory import StrategyFactory

# 初始化工厂
factory = StrategyFactory(
    author_id='your_user_id',
    author_name='Your Name'
)

# 通过自然语言描述创建策略
strategy = factory.create_from_natural_language(
    description="创建一个 5 日均线上穿 20 日均线的买入策略，初始资金 10 万元",
    auto_backtest=True  # 自动回测
)

print(f"策略名称：{strategy.name}")
print(f"策略 ID: {strategy.id}")
print(f"策略状态：{strategy.status.value}")
print(f"回测评分：{strategy.backtest_report.get('score', 'N/A')}")
```

### 2. 搜索并创建多个策略变体

```python
# 基于主题创建多个参数变体
strategies = factory.search_and_create(
    topic="均线交叉",
    auto_backtest=True
)

print(f"创建了 {len(strategies)} 个策略变体")
for s in strategies:
    print(f"  - {s.name}: 评分 {s.backtest_report.get('score', 'N/A')}")
```

### 3. 优化现有策略

```python
# 优化策略参数
optimized_strategy = factory.optimize_strategy(
    strategy_id='strategy-uuid-xxx',
    auto_backtest=True
)

print(f"优化后评分：{optimized_strategy.backtest_report.get('score', 'N/A')}")
print(f"评分提升：{optimized_strategy.backtest_report.get('improvement', 0)}")
```

## 支持的策略类型

### 均线交叉策略 (ma_cross)
- **参数**: short_window, long_window
- **示例描述**: "创建一个 5 日均线上穿 20 日均线的买入策略"

### 动量策略 (momentum)
- **参数**: lookback_period, threshold
- **示例描述**: "创建一个看 20 日动量超过 5% 买入的趋势策略"

### 布林带策略 (bollinger)
- **参数**: window, num_std
- **示例描述**: "创建一个 20 日布林带触及下轨买入的策略"

### RSI 策略 (rsi)
- **参数**: period, oversold, overbought
- **示例描述**: "创建一个 14 日 RSI 低于 30 买入的超卖策略"

## 核心类说明

### StrategyFactory

策略工厂核心类，提供完整的策略创建、回测、优化功能。

```python
class StrategyFactory:
    def create_from_natural_language(
        self,
        description: str,
        auto_backtest: bool = True
    ) -> Strategy
    
    def search_and_create(
        self,
        topic: str,
        auto_backtest: bool = True
    ) -> List[Strategy]
    
    def optimize_strategy(
        self,
        strategy_id: str,
        auto_backtest: bool = True
    ) -> Strategy
```

### StrategyCodeGenerator

策略代码生成器，根据解析的参数生成可执行的策略代码。

```python
generator = StrategyCodeGenerator()
code = generator.generate(
    strategy_type='ma_cross',
    params={'short_window': 5, 'long_window': 20},
    name='我的均线策略',
    initial_capital=100000.0
)
```

### StrategyOptimizer

策略优化器，使用遗传算法优化策略参数。

```python
optimizer = StrategyOptimizer(
    population_size=20,
    generations=10,
    mutation_rate=0.1,
    crossover_rate=0.7
)

best_params, best_score = optimizer.optimize(
    strategy_code=code,
    param_ranges={'short_window': (3, 15), 'long_window': (15, 60)},
    fitness_func=backtest_score_function
)
```

## 回测评分标准

策略回测评分 (0-100 分) 由以下指标综合计算：

| 指标 | 权重 | 说明 |
|------|------|------|
| 总收益 | 40 分 | 基于总收益率，最高 40 分 |
| 夏普比率 | 30 分 | 基于风险调整收益，最高 30 分 |
| 最大回撤 | 20 分 | 基于最大回撤，最低 0 分 |
| 胜率 | 10 分 | 基于交易胜率，最高 10 分 |

- **评分 >= 60**: 自动发布到策略商店
- **评分 < 60**: 保存为草稿

## 高级用法

### 自定义回测参数

```python
# 创建策略时指定自定义回测参数
strategy = factory.create_from_natural_language(
    description="均线交叉策略",
    auto_backtest=False  # 先不回测
)

# 手动运行回测
from backtest.engine import BacktestEngine, generate_mock_data

engine = BacktestEngine()
data = generate_mock_data('2023-01-01', '2023-12-31')

# 加载策略代码并创建实例
# ... 加载代码 ...

results = engine.run(strategy_instance, data)
print(f"总收益：{results.total_return:.2%}")
print(f"夏普比率：{results.sharpe_ratio:.2f}")
print(f"最大回撤：{results.max_drawdown:.2%}")
```

### 自定义优化器配置

```python
# 使用更激进的优化配置
optimizer = StrategyOptimizer(
    population_size=50,  # 更大的种群
    generations=20,      # 更多代数
    mutation_rate=0.2,   # 更高变异率
    crossover_rate=0.8,  # 更高交叉率
    elite_size=5         # 更多精英
)
```

## 测试

运行测试并生成覆盖率报告：

```bash
# 运行测试
pytest tests/test_strategy_factory.py -v

# 生成覆盖率报告
pytest tests/test_strategy_factory.py --cov=strategy_factory --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

## 依赖模块

- `src/nlp/parser.py` - 自然语言解析
- `src/strategy/base.py` - 策略基类
- `src/backtest/engine.py` - 回测引擎
- `src/market/service.py` - 策略商店服务

## 注意事项

1. **策略代码安全**: 生成的策略代码会经过基本验证，但建议在沙箱环境中运行
2. **回测数据**: 默认使用模拟数据进行回测，可使用真实数据替换
3. **参数范围**: 优化时需要提供合理的参数范围，避免过拟合
4. **评分阈值**: 60 分是默认发布阈值，可根据实际需求调整

## 示例输出

```python
>>> strategy = factory.create_from_natural_language(
...     "创建一个 5 日均线上穿 20 日均线的买入策略"
... )

策略创建完成：自定义策略 (ID: 550e8400-e29b-41d4-a716-446655440000)
回测评分：75.5
策略状态：published
```

## 版本历史

- **v1.0.0** (2026-03-11): 初始版本
  - 支持 4 种策略类型
  - 自然语言解析
  - 自动回测和评分
  - 遗传算法优化
