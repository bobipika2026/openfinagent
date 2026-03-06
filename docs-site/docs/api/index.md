# API 参考

OpenFinAgent 提供了完整的 API 接口，支持策略开发、回测、交易等功能。

## 📚 API 分类

| 分类 | 描述 | 文档 |
|------|------|------|
| 交易接口 | 订单管理、仓位管理 | [trading.md](trading.md) |
| 数据接口 | 市场数据、历史数据 | [data.md](data.md) |
| 策略接口 | 策略基类、信号生成 | [strategy.md](strategy.md) |

## 🚀 快速开始

```python
from openfinagent import Strategy, Backtester, Signal

# 创建策略
class MyStrategy(Strategy):
    def on_bar(self, bar):
        # 策略逻辑
        pass

# 运行回测
strategy = MyStrategy()
backtester = Backtester(strategy, data_file='data.csv')
results = backtester.run()
```

## 📦 核心模块

```
openfinagent/
├── strategy/      # 策略模块
├── backtest/      # 回测模块
├── trading/       # 交易模块
├── data/          # 数据模块
├── risk/          # 风控模块
└── utils/         # 工具函数
```

## 🔧 环境配置

```python
from openfinagent import Config

config = Config(
    api_key='your_api_key',
    api_secret='your_api_secret',
    paper_trading=True,
    log_level='INFO'
)
```

## 📊 数据格式

### K 线数据

```python
{
    'timestamp': '2024-01-01 10:00:00',
    'open': 100.0,
    'high': 102.0,
    'low': 99.0,
    'close': 101.0,
    'volume': 1000000
}
```

### 订单数据

```python
{
    'order_id': '123456',
    'symbol': 'AAPL',
    'side': 'BUY',
    'quantity': 100,
    'price': 100.0,
    'status': 'FILLED'
}
```

## 📚 相关文档

- [交易接口](trading.md) - 订单和仓位管理
- [数据接口](data.md) - 市场数据访问
- [策略接口](strategy.md) - 策略开发指南

---

_详细 API 文档请参考各分类页面。_
