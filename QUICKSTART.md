# OpenFinAgent 快速使用指南

## ⚡ 30 秒快速体验

```bash
# 进入项目目录
cd openfinagent

# 运行演示
python3 run_demo.py
```

## 📝 5 分钟创建第一个策略

### 步骤 1: 导入模块

```python
from strategy.builder import StrategyBuilder
from backtest.engine import BacktestEngine, load_data
```

### 步骤 2: 创建策略

```python
# 用自然语言描述
strategy = StrategyBuilder.from_natural_language("""
当 5 日均线上穿 20 日均线时买入
当 5 日均线下穿 20 日均线时卖出
初始资金 10 万元
""")
```

### 步骤 3: 加载数据

```python
# 使用模拟数据（无需 API 密钥）
data = load_data(
    symbol="600519.SH",
    start_date="2023-01-01",
    end_date="2023-12-31",
    source='mock'
)
```

### 步骤 4: 运行回测

```python
engine = BacktestEngine()
results = engine.run(strategy, data)
```

### 步骤 5: 查看结果

```python
results.show()  # 显示文本报告
results.to_csv('trades.csv')  # 保存交易记录
```

## 🎯 常用策略模板

### 均线交叉策略

```python
strategy = StrategyBuilder.create(
    'ma_cross',
    short_window=5,    # 短期均线
    long_window=20,    # 长期均线
    initial_capital=100000
)
```

### 动量策略

```python
strategy = StrategyBuilder.create(
    'momentum',
    lookback_period=20,  # 回看周期
    threshold=0.05,      # 阈值 5%
    initial_capital=100000
)
```

## 📊 支持的数据源

```python
# A 股数据（需要安装 akshare）
data = load_data("600519.SH", "2023-01-01", "2023-12-31", source='akshare')

# 美股数据（需要安装 yfinance）
data = load_data("AAPL", "2023-01-01", "2023-12-31", source='yfinance')

# 模拟数据（无需安装）
data = load_data("TEST", "2023-01-01", "2023-12-31", source='mock')
```

## 🔧 自定义回测参数

```python
engine = BacktestEngine(
    commission_rate=0.0003,  # 手续费万三
    slippage=0.001           # 滑点 0.1%
)
```

## 📈 查看回测指标

```python
metrics = results.metrics
print(f"总收益：{metrics['总收益 (%)']}%")
print(f"夏普比率：{metrics['夏普比率']}")
print(f"最大回撤：{metrics['最大回撤 (%)']}%")
```

## 🎨 可视化（需要 matplotlib）

```python
results.plot()  # 绘制权益曲线、回撤等
```

## 💡 提示

1. **首次使用**: 先运行 `python3 run_demo.py` 体验完整流程
2. **学习示例**: 查看 `examples/` 目录下的示例代码
3. **阅读文档**: `docs/getting_started.md` 详细教程
4. **修改参数**: 调整均线周期、资金等参数观察效果
5. **保存结果**: 使用 `results.to_csv()` 保存交易记录

## ❓ 遇到问题？

- 查看 `docs/` 目录的文档
- 运行 `examples/` 中的示例代码
- 检查 `requirements.txt` 是否已安装所有依赖

---

**Happy Trading!** 📈
