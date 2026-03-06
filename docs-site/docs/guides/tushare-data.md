# Tushare 分钟线使用指南

> ⏱️ 获取 A 股高精度分钟级行情数据

---

## 📋 概述

**Tushare** 是国内知名的金融数据接口平台，提供 A 股、基金、期货、期权等金融产品的历史行情数据。OpenFinAgent v0.3.0 新增了 **Tushare 分钟线数据源**，支持获取 1 分钟、5 分钟、15 分钟、30 分钟、60 分钟等高精度数据。

### 核心特性

- ✅ **多周期支持** - 1m/5m/15m/30m/60m 分钟线
- ✅ **全市场覆盖** - A 股所有股票、指数
- ✅ **复权处理** - 支持前复权、后复权、不复权
- ✅ **Token 管理** - 安全的 Token 配置和管理
- ✅ **缓存机制** - 避免重复请求，提高效率

---

## 🔑 Token 配置

### 1. 获取 Token

1. 访问 [Tushare 官网](https://tushare.pro)
2. 注册账号
3. 进入个人中心 → 接口 Token
4. 复制 Token 备用

> 💡 **提示**：新用户默认有基础积分，可满足日常使用。更多数据需要提高积分。

### 2. 配置 Token

#### 方式一：环境变量（推荐）

```bash
# Linux/macOS
export TUSHARE_TOKEN='your_token_here'

# Windows
set TUSHARE_TOKEN=your_token_here

# 或添加到 ~/.bashrc / ~/.zshrc
echo "export TUSHARE_TOKEN='your_token_here'" >> ~/.bashrc
source ~/.bashrc
```

#### 方式二：代码中配置

```python
from data.sources import TushareDataSource

# 直接在代码中传入 Token
source = TushareDataSource(token='your_token_here')
```

#### 方式三：配置文件

```python
# .env 文件
TUSHARE_TOKEN=your_token_here

# 代码中读取
import os
from data.sources import TushareDataSource

token = os.getenv('TUSHARE_TOKEN')
source = TushareDataSource(token=token)
```

### 3. Token 安全管理

```python
from data.tushare_token_manager import TokenManager

# 创建 Token 管理器
manager = TokenManager()

# 保存 Token（加密存储）
manager.save_token('your_token_here')

# 获取 Token
token = manager.get_token()
if token:
    source = TushareDataSource(token=token)
else:
    print("请先配置 Tushare Token")
```

---

## 🚀 快速开始

### 1. 基础使用

```python
from data.sources import TushareDataSource

# 创建数据源（自动从环境变量读取 Token）
source = TushareDataSource()

# 获取 5 分钟线数据
data = source.get_data(
    symbol='000001.SZ',  # 平安银行
    start_date='2024-01-01',
    end_date='2024-01-31',
    freq='5m'
)

print(data.head())
print(f"共获取 {len(data)} 行数据")
```

### 2. 指定 Token

```python
source = TushareDataSource(token='your_token_here', freq='5m')
data = source.get_data('000001.SZ', '2024-01-01', '2024-01-31')
```

---

## ⏱️ 支持的时间周期

| 周期 | 代码 | 说明 | 适用场景 |
|------|------|------|----------|
| 1 分钟 | `1m` | 每分钟 K 线 | 超高频交易、做 T |
| 5 分钟 | `5m` | 每 5 分钟 K 线 | 日内短线交易 |
| 15 分钟 | `15m` | 每 15 分钟 K 线 | 日内波段 |
| 30 分钟 | `30m` | 每 30 分钟 K 线 | 短线趋势 |
| 60 分钟 | `60m` | 每小时 K 线 | 小时级别趋势 |

### 使用示例

```python
# 1 分钟线（数据量最大）
data_1m = source.get_data('000001.SZ', '2024-01-01', '2024-01-05', freq='1m')

# 5 分钟线（常用）
data_5m = source.get_data('000001.SZ', '2024-01-01', '2024-01-31', freq='5m')

# 60 分钟线
data_60m = source.get_data('000001.SZ', '2024-01-01', '2024-03-31', freq='60m')
```

> ⚠️ **注意**：分钟线数据量较大，建议合理设置日期范围。

---

## 📊 支持的证券类型

### A 股股票

```python
# 主板（沪深）
source.get_data('000001.SZ', ...)  # 平安银行
source.get_data('600000.SH', ...)  # 浦发银行

# 创业板
source.get_data('300001.SZ', ...)  # 特锐德

# 科创板
source.get_data('688001.SH', ...)  # 华兴源创
```

### 指数

```python
# 上证指数
source.get_data('000001.SH', ...)

# 深证成指
source.get_data('399001.SZ', ...)

# 创业板指
source.get_data('399006.SZ', ...)
```

### 基金

```python
# ETF 基金
source.get_data('510300.SH', ...)  # 沪深 300ETF
```

---

## 💡 实战示例

### 示例 1：日内交易策略回测

```python
from data.sources import TushareDataSource
from backtest.engine import BacktestEngine
from strategy.dual_ma import DualMAStrategy

# 1. 获取 5 分钟线数据
source = TushareDataSource(freq='5m')
data = source.get_data(
    symbol='000001.SZ',
    start_date='2024-01-01',
    end_date='2024-01-31'
)

# 2. 创建日内交易策略（小周期均线）
strategy = DualMAStrategy(
    short_window=5,   # 5 周期 = 25 分钟
    long_window=20,   # 20 周期 = 100 分钟
    initial_capital=100000
)

# 3. 运行回测
engine = BacktestEngine()
result = engine.run(strategy, data)

# 4. 查看结果
print(result.summary())
result.plot()
```

### 示例 2：多股票批量回测

```python
from data.sources import TushareDataSource
from backtest.batch import BatchBacktester

# 定义股票池
symbols = [
    '000001.SZ',  # 平安银行
    '000002.SZ',  # 万科 A
    '600000.SH',  # 浦发银行
    '600036.SH',  # 招商银行
]

# 批量回测配置
config = {
    'symbols': symbols,
    'strategy_class': DualMAStrategy,
    'strategy_params': {'short_window': 10, 'long_window': 30},
    'freq': '5m',
    'start_date': '2024-01-01',
    'end_date': '2024-01-31',
    'initial_capital': 100000,
    'n_jobs': 4  # 并行处理
}

# 执行批量回测
batch = BatchBacktester(config)
results = batch.run()

# 查看汇总
print(results.summary())
```

### 示例 3：参数热力图优化

```python
from data.sources import TushareDataSource
from optimization.heatmap import ParameterHeatmap
from backtest.engine import BacktestEngine

# 获取数据
source = TushareDataSource(freq='5m')
data = source.get_data('000001.SZ', '2024-01-01', '2024-01-31')

# 创建热力图扫描器
scanner = ParameterHeatmap(metric_name='sharpe_ratio')

# 双参数扫描
result = scanner.scan(
    strategy_class=DualMAStrategy,
    param1_name='short_window',
    param1_values=[5, 10, 15, 20],
    param2_name='long_window',
    param2_values=[20, 30, 40, 50],
    base_params={},
    backtest_func=lambda s, d: BacktestEngine().run(s, d),
    data=data,
    initial_capital=100000
)

# 绘制热力图
scanner.plot(result, save_path='heatmap.png')

print(f"最优参数：short_window={result.best_param1}, long_window={result.best_param2}")
```

---

## 🔧 高级功能

### 复权处理

```python
from data.sources import TushareDataSource

# 前复权（推荐，避免除权缺口）
source = TushareDataSource(adjust='qfq')

# 后复权
source = TushareDataSource(adjust='hfq')

# 不复权
source = TushareDataSource(adjust=None)
```

### 数据缓存

```python
from data.sources import TushareDataSource

# 启用缓存（避免重复请求）
source = TushareDataSource(use_cache=True, cache_dir='./cache')

# 第一次请求会下载并缓存
data1 = source.get_data('000001.SZ', '2024-01-01', '2024-01-31')

# 第二次请求直接从缓存读取
data2 = source.get_data('000001.SZ', '2024-01-01', '2024-01-31')
```

### 获取股票列表

```python
from data.sources import TushareDataSource

source = TushareDataSource()

# 获取所有 A 股列表
stock_list = source.get_stock_list()

# 筛选沪深 300 成分股
hs300 = stock_list[stock_list['index_name'] == '沪深 300']
print(f"沪深 300 成分股数量：{len(hs300)}")
```

---

## 📈 数据字段说明

返回的 DataFrame 包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `trade_time` | datetime | 交易时间 |
| `open` | float | 开盘价 |
| `high` | float | 最高价 |
| `low` | float | 最低价 |
| `close` | float | 收盘价 |
| `vol` | float | 成交量（手） |
| `amount` | float | 成交额（元） |

**索引：** `trade_time` (datetime 类型)

---

## ⚠️ 注意事项

### 1. Token 积分限制

Tushare 采用积分制，不同数据需要不同积分：

| 数据类型 | 所需积分 | 说明 |
|---------|---------|------|
| 日线 | 120 积分 | 免费用户可达 |
| 分钟线 | 2000 积分 | 需要付费或贡献 |
| 实时行情 | 5000 积分 | 高级用户 |

**获取积分方式：**

- 注册赠送 100 积分
- 每日签到
- 邀请好友
- 付费购买
- 数据贡献

### 2. 调用频率限制

```python
# Tushare 接口调用限制
# 基础用户：每分钟 500 次
# 高级用户：每分钟 1000 次

# 建议：启用缓存，避免重复请求
source = TushareDataSource(use_cache=True)
```

### 3. 交易时间

A 股交易时间：

- **上午**：9:30 - 11:30
- **下午**：13:00 - 15:00

分钟线数据仅在交易时间内有值。

### 4. 数据量估算

```python
# 5 分钟线数据量估算
# 每天 48 根 K 线（4 小时 × 12 根/小时）
# 每月约 1000 根（21 个交易日）
# 每年约 12000 根

# 示例：获取 1 个月的 5 分钟线
data = source.get_data('000001.SZ', '2024-01-01', '2024-01-31', freq='5m')
print(f"数据量：{len(data)} 行")  # 约 1000 行
```

---

## 🐛 常见问题

### Q1: Token 无效或积分不足

**错误信息：** `积分不足，需要 2000 积分`

**解决：**

```python
# 1. 检查 Token 是否正确
import os
print(f"Token: {os.getenv('TUSHARE_TOKEN')}")

# 2. 访问 Tushare 官网查看积分
# https://tushare.pro/user/token

# 3. 考虑使用日线数据（积分要求低）
source = TushareDataSource(freq='d')  # 日线
```

### Q2: 获取数据返回空

**原因：** 日期范围无交易或股票停牌

**解决：**

```python
# 检查日期是否为交易日
data = source.get_data('000001.SZ', '2024-01-01', '2024-01-31', freq='5m')

if data.empty:
    print("数据为空，可能原因：")
    print("1. 日期范围包含非交易日")
    print("2. 股票停牌")
    print("3. Token 积分不足")
```

### Q3: 如何获取最新数据？

```python
from datetime import datetime, timedelta

# 获取最近 7 天的数据
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

data = source.get_data(
    '000001.SZ',
    start_date.strftime('%Y-%m-%d'),
    end_date.strftime('%Y-%m-%d'),
    freq='5m'
)
```

---

## 📚 相关文档

- [Binance 数据源](binance-data.md) - 加密货币数据
- [Token 配置说明](#token-配置) - Token 管理
- [优化器指南](optimizer.md) - 参数优化

---

## 🔗 参考链接

- [Tushare 官网](https://tushare.pro)
- [Tushare 文档](https://tushare.pro/document/2)
- [Tushare 积分规则](https://tushare.pro/document/1?doc_id=13)
- [OpenFinAgent GitHub](https://github.com/bobipika2026/openfinagent)

---

_最后更新：2026 年 3 月 6 日_
