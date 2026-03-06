# Binance 数据源使用指南

> 📊 获取全球最大加密货币交易所的实时和历史数据

---

## 📋 概述

OpenFinAgent v0.3.0 新增了 **Binance 数据源**，支持获取加密货币的 OHLCV（开高低收量）数据。该数据源使用 Binance 公开 API，**无需 API Key** 即可使用。

### 核心特性

- ✅ **免 API Key** - 使用公开接口，开箱即用
- ✅ **多交易对** - 支持 BTC/USDT、ETH/USDT 等所有 Binance 交易对
- ✅ **多时间周期** - 14 种时间周期（1m ~ 1M）
- ✅ **历史数据** - 可获取任意时间范围的历史 K 线
- ✅ **自动分页** - 大数据量自动分批请求

---

## 🚀 快速开始

### 1. 基础使用

```python
from data.binance_source import BinanceDataSource

# 创建数据源实例
source = BinanceDataSource()

# 获取 BTC/USDT 日线数据
data = source.get_klines(
    symbol='BTC/USDT',
    interval='1d',
    start_date='2024-01-01',
    end_date='2024-01-31'
)

# 查看数据
print(data.head())
print(f"共获取 {len(data)} 行数据")
```

**输出示例：**

```
            open     high      low    close   volume
timestamp                                           
2024-01-01  42265   42890   42100   42650   15234.56
2024-01-02  42650   43200   42500   43100   18456.78
2024-01-03  43100   43500   42800   43350   16789.23
...
```

### 2. 便捷函数

```python
from data.binance_source import get_binance_data

# 一行代码获取数据
data = get_binance_data(
    symbol='ETH/USDT',
    interval='1h',
    start_date='2024-01-01',
    end_date='2024-01-07'
)
```

---

## 📊 支持的交易对

### 主流币种

| 交易对 | 代码 | 说明 |
|--------|------|------|
| BTC/USDT | `BTCUSDT` | 比特币 - 美元稳定币 |
| ETH/USDT | `ETHUSDT` | 以太坊 - 美元稳定币 |
| BNB/USDT | `BNBUSDT` | 币安币 - 美元稳定币 |
| XRP/USDT | `XRPUSDT` | 瑞波币 - 美元稳定币 |
| SOL/USDT | `SOLUSDT` | Solana - 美元稳定币 |

### 获取所有可用交易对

```python
source = BinanceDataSource()
symbols = source.get_available_symbols()

print(f"可用交易对数量：{len(symbols)}")
print(f"前 10 个：{symbols[:10]}")
```

---

## ⏱️ 时间周期

### 支持的时间周期

| 周期 | 代码 | 说明 |
|------|------|------|
| 1 分钟 | `1m` | 高频交易 |
| 3 分钟 | `3m` | 超短线 |
| 5 分钟 | `5m` | 短线交易 |
| 15 分钟 | `15m` | 日内交易 |
| 30 分钟 | `30m` | 日内交易 |
| 1 小时 | `1h` | 短线趋势 |
| 2 小时 | `2h` | 短线趋势 |
| 4 小时 | `4h` | 中线趋势 |
| 6 小时 | `6h` | 中线趋势 |
| 12 小时 | `12h` | 中线趋势 |
| 1 天 | `1d` | 日线级别 |
| 3 天 | `3d` | 多日趋势 |
| 1 周 | `1w` | 周线级别 |
| 1 月 | `1M` | 月线级别 |

### 使用示例

```python
# 获取 4 小时线
data_4h = source.get_klines('BTC/USDT', '4h', '2024-01-01', '2024-01-31')

# 获取 1 小时线
data_1h = source.get_klines('BTC/USDT', '1h', '2024-01-01', '2024-01-07')

# 获取周线
data_1w = source.get_klines('BTC/USDT', '1w', '2023-01-01', '2024-01-01')
```

---

## 💡 实战示例

### 示例 1：双均线策略回测

```python
from data.binance_source import BinanceDataSource
from backtest.engine import BacktestEngine
from strategy.dual_ma import DualMAStrategy

# 1. 获取数据
source = BinanceDataSource()
data = source.get_klines(
    symbol='BTC/USDT',
    interval='1d',
    start_date='2023-01-01',
    end_date='2023-12-31'
)

# 2. 创建策略
strategy = DualMAStrategy(
    short_window=10,
    long_window=30,
    initial_capital=10000
)

# 3. 运行回测
engine = BacktestEngine()
result = engine.run(strategy, data)

# 4. 查看结果
print(result.summary())
result.plot()
```

### 示例 2：多币种批量回测

```python
from data.binance_source import BinanceDataSource
from backtest.batch import BatchBacktester

# 定义交易对列表
symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT']

# 批量回测配置
config = {
    'symbols': symbols,
    'strategy_class': DualMAStrategy,
    'strategy_params': {'short_window': 10, 'long_window': 30},
    'interval': '1d',
    'start_date': '2023-01-01',
    'end_date': '2023-12-31',
    'initial_capital': 10000,
    'n_jobs': 4  # 并行处理
}

# 执行批量回测
batch = BatchBacktester(config)
results = batch.run()

# 查看汇总
print(results.summary())
```

### 示例 3：参数优化

```python
from data.binance_source import BinanceDataSource
from optimization.genetic_optimizer import GeneticOptimizer, ParameterBound

# 获取数据
source = BinanceDataSource()
data = source.get_klines('BTC/USDT', '1d', '2023-01-01', '2023-12-31')

# 定义参数范围
param_bounds = [
    ParameterBound('short_window', 5, 20, dtype='int'),
    ParameterBound('long_window', 20, 60, dtype='int')
]

# 执行优化
optimizer = GeneticOptimizer(
    population_size=30,
    generations=50,
    optimization_metric='sharpe_ratio'
)

best = optimizer.optimize(
    strategy_class=DualMAStrategy,
    parameter_bounds=param_bounds,
    backtest_func=lambda s, d: BacktestEngine().run(s, d),
    data=data
)

print(f"最优参数：{best.params}")
print(f"夏普比率：{best.fitness:.2f}")
```

---

## 🔧 高级配置

### 自定义 API 地址

```python
# 使用币安测试网
source = BinanceDataSource(base_url='https://testnet.binance.vision')

# 使用代理（如需要）
source = BinanceDataSource(base_url='https://api.binance.com')
```

### 调整请求频率

```python
# 降低请求频率（避免触发限流）
source = BinanceDataSource(rate_limit_delay=0.5)

# 激进模式（更快但可能触发限流）
source = BinanceDataSource(rate_limit_delay=0.05)
```

### 获取当前价格

```python
source = BinanceDataSource()

# 获取 BTC/USDT 当前价格
price = source.get_ticker_price('BTC/USDT')
print(f"BTC 当前价格：${price:,.2f}")
```

### 获取近期历史数据

```python
# 获取过去 365 天的数据
data = source.get_historical_data(
    symbol='BTC/USDT',
    interval='1d',
    days=365
)
```

---

## 📈 数据字段说明

返回的 DataFrame 包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `open` | float | 开盘价 |
| `high` | float | 最高价 |
| `low` | float | 最低价 |
| `close` | float | 收盘价 |
| `volume` | float | 成交量（基础货币） |

**索引：** `timestamp` (datetime 类型)

---

## ⚠️ 注意事项

### 1. 网络要求

Binance API 需要访问国际互联网。如果遇到连接问题：

```python
# 检查网络连接
import requests
try:
    response = requests.get('https://api.binance.com', timeout=5)
    print("网络连接正常")
except:
    print("无法访问 Binance API，请检查网络")
```

### 2. API 限流

Binance 对公开 API 有速率限制：

- **权重限制**：每个 IP 每分钟 1200 权重
- **K 线接口**：每次请求权重为 2

**建议：**

```python
# 自动限流控制（默认）
source = BinanceDataSource(rate_limit_delay=0.1)

# 大数据量时分批获取
data = source.get_klines(
    symbol='BTC/USDT',
    interval='1d',
    start_date='2020-01-01',  # 跨度不要太大
    end_date='2023-12-31',
    limit=1000  # 单次最多 1000 条
)
```

### 3. 交易对格式

支持多种格式，会自动标准化：

```python
# 以下格式都等价
source.get_klines('BTC/USDT', ...)   # 推荐
source.get_klines('BTCUSDT', ...)
source.get_klines('BTC_USDT', ...)
```

### 4. 数据质量

- 数据来自 Binance 官方 API
- 自动去重和排序
- 缺失数据会返回空 DataFrame

---

## 🐛 常见问题

### Q1: 获取数据时返回空 DataFrame

**原因：** 交易对不存在或日期范围无数据

**解决：**

```python
# 检查交易对是否存在
symbols = source.get_available_symbols()
if 'BTCUSDT' not in symbols:
    print("交易对不存在")

# 检查日期范围
data = source.get_klines('BTC/USDT', '1d', '2024-01-01', '2024-01-31')
if data.empty:
    print("该日期范围无数据")
```

### Q2: 请求失败或超时

**原因：** 网络问题或 API 限流

**解决：**

```python
# 增加请求间隔
source = BinanceDataSource(rate_limit_delay=0.5)

# 添加重试逻辑
import time
for attempt in range(3):
    try:
        data = source.get_klines(...)
        break
    except Exception as e:
        print(f"尝试 {attempt + 1} 失败：{e}")
        time.sleep(2)
```

### Q3: 如何获取分钟线数据？

```python
# 获取 5 分钟线
data = source.get_klines(
    symbol='BTC/USDT',
    interval='5m',
    start_date='2024-01-01',
    end_date='2024-01-02'  # 分钟线数据量大，建议日期范围小一些
)
```

---

## 📚 相关文档

- [Tushare 数据源](tushare-data.md) - A 股数据获取
- [优化器指南](optimizer.md) - 参数优化
- [回测教程](../tutorials/backtesting.md) - 回测实战

---

## 🔗 参考链接

- [Binance API 文档](https://binance-docs.github.io/apidocs/)
- [Binance 官网](https://www.binance.com)
- [OpenFinAgent GitHub](https://github.com/bobipika2026/openfinagent)

---

_最后更新：2026 年 3 月 6 日_
