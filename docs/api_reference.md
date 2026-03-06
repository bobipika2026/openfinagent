# OpenFinAgent API 参考

完整的 API 接口文档。

## 📦 核心模块

### StrategyBuilder - 策略构建器

创建和管理交易策略的主要入口。

#### 方法

##### `from_natural_language(description: str, **kwargs) -> BaseStrategy`

从自然语言描述创建策略。

**参数:**
- `description` (str): 策略的自然语言描述
- `**kwargs`: 额外参数

**返回:**
- `BaseStrategy`: 策略实例

**示例:**
```python
strategy = StrategyBuilder.from_natural_language("""
当 5 日均线上穿 20 日均线时买入
当 5 日均线下穿 20 日均线时卖出
初始资金 10 万元
""")
```

##### `create(strategy_type: str, **params) -> BaseStrategy`

直接创建策略。

**参数:**
- `strategy_type` (str): 策略类型 ('ma_cross', 'momentum')
- `**params`: 策略参数

**返回:**
- `BaseStrategy`: 策略实例

**示例:**
```python
strategy = StrategyBuilder.create(
    'ma_cross',
    short_window=10,
    long_window=30,
    initial_capital=100000
)
```

##### `register_strategy(name: str, strategy_class: type)`

注册自定义策略。

**参数:**
- `name` (str): 策略名称
- `strategy_class` (type): 策略类

**示例:**
```python
StrategyBuilder.register_strategy('my_strategy', MyStrategy)
```

##### `list_strategies() -> List[str]`

列出所有可用策略。

**返回:**
- `List[str]`: 策略名称列表

---

### BacktestEngine - 回测引擎

执行策略回测的核心引擎。

#### 初始化

```python
engine = BacktestEngine(
    commission_rate=0.0003,  # 手续费率
    slippage=0.001  # 滑点
)
```

#### 方法

##### `run(strategy, data, start_date=None, end_date=None, show_progress=True) -> BacktestResults`

运行单个策略回测。

**参数:**
- `strategy` (BaseStrategy): 策略实例
- `data` (DataFrame): 市场数据 (OHLCV)
- `start_date` (str, optional): 开始日期
- `end_date` (str, optional): 结束日期
- `show_progress` (bool): 显示进度条

**返回:**
- `BacktestResults`: 回测结果

**示例:**
```python
results = engine.run(strategy, data, "2023-01-01", "2023-12-31")
```

##### `run_multi(strategies, data, start_date=None, end_date=None) -> Dict`

运行多个策略回测。

**参数:**
- `strategies` (List[BaseStrategy]): 策略列表
- `data` (DataFrame): 市场数据
- `start_date` (str, optional): 开始日期
- `end_date` (str, optional): 结束日期

**返回:**
- `Dict[str, BacktestResults]`: 策略名称到结果的映射

---

### BacktestResults - 回测结果

存储和展示回测结果。

#### 属性

- `strategy_name` (str): 策略名称
- `initial_capital` (float): 初始资金
- `final_capital` (float): 最终资金
- `trades` (List[Dict]): 交易记录
- `equity_curve` (List[Dict]): 权益曲线
- `metrics` (Dict): 性能指标
- `daily_returns` (List[float]): 日收益率

#### 方法

##### `show()`

在控制台显示回测结果。

**示例:**
```python
results.show()
```

##### `plot()`

绘制回测图表。

**示例:**
```python
results.plot()
```

##### `to_csv(filepath: str)`

保存交易记录到 CSV。

**参数:**
- `filepath` (str): 文件路径

**示例:**
```python
results.to_csv('trades.csv')
```

##### `to_dict() -> Dict`

转换为字典。

**返回:**
- `Dict`: 结果字典

---

### StrategyPlotter - 策略绘图器

可视化回测结果。

#### 方法

##### `plot_backtest(results, save_path=None)`

绘制单个策略回测结果。

**参数:**
- `results` (BacktestResults): 回测结果
- `save_path` (str, optional): 保存路径

##### `plot_comparison(results_list, save_path=None)`

对比多个策略。

**参数:**
- `results_list` (List[BacktestResults]): 结果列表
- `save_path` (str, optional): 保存路径

##### `plot_metrics_radar(results, save_path=None)`

绘制指标雷达图。

**参数:**
- `results` (BacktestResults): 回测结果
- `save_path` (str, optional): 保存路径

---

## 📊 数据格式

### 市场数据 DataFrame

回测引擎需要的数据格式：

```python
import pandas as pd

data = pd.DataFrame({
    'open': [...],      # 开盘价
    'high': [...],      # 最高价
    'low': [...],       # 最低价
    'close': [...],     # 收盘价
    'volume': [...]     # 成交量
}, index=pd.date_range('2023-01-01', periods=252, freq='B'))
```

### 交易记录格式

```python
{
    'timestamp': datetime,  # 时间戳
    'type': 'buy'/'sell',   # 交易类型
    'price': float,         # 成交价格
    'shares': int,          # 交易数量
    'commission': float,    # 手续费
}
```

---

## 🔧 工具函数

### `load_data(symbol, start_date, end_date, source='akshare')`

加载市场数据。

**参数:**
- `symbol` (str): 股票代码
- `start_date` (str): 开始日期
- `end_date` (str): 结束日期
- `source` (str): 数据源 ('akshare', 'yfinance', 'mock')

**返回:**
- `DataFrame`: OHLCV 数据

---

## 📝 性能指标

回测结果包含以下指标：

| 指标 | 类型 | 说明 |
|------|------|------|
| 总收益 (%) | float | 策略总收益率 |
| 年化收益 (%) | float | 年化收益率 |
| 波动率 (%) | float | 收益波动率 |
| 夏普比率 | float | 风险调整后收益 |
| 最大回撤 (%) | float | 最大亏损幅度 |
| 交易次数 | int | 总交易次数 |
| 胜率 (%) | float | 盈利交易比例 |
| 初始资金 | float | 初始资金 |
| 最终资金 | float | 最终资金 |

---

## 🎯 最佳实践

1. **数据质量**: 使用可靠的数据源
2. **参数设置**: 合理设置手续费和滑点
3. **回测周期**: 至少 1 年以上数据
4. **风险控制**: 关注最大回撤
5. **过拟合**: 避免过度优化参数

---

**Happy Trading!** 📈
