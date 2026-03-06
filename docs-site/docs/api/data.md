# 数据接口

数据接口提供了市场数据、历史数据的访问功能。

## 📊 市场数据

### 实时行情

```python
# 获取实时报价
quote = self.get_quote('AAPL')
print(quote.bid)
print(quote.ask)
print(quote.last)

# 获取深度数据
depth = self.get_depth('AAPL', level=5)
print(depth.bids)  # 买盘
print(depth.asks)  # 卖盘

# 获取实时 K 线
bar = self.get_bar('AAPL', timeframe='1m')
```

### 行情订阅

```python
# 订阅行情
self.subscribe(['AAPL', 'GOOGL', 'MSFT'])

# 取消订阅
self.unsubscribe(['AAPL'])

# 获取订阅列表
symbols = self.get_subscriptions()
```

## 📈 历史数据

### K 线数据

```python
# 获取 K 线
bars = self.get_bars(
    symbol='AAPL',
    timeframe='1d',
    start='2024-01-01',
    end='2024-12-31'
)

# 获取收盘价
closes = self.get_closes(symbol='AAPL', count=100)

# 获取成交量
volumes = self.get_volumes(symbol='AAPL', count=100)
```

### 数据格式

```python
# K 线数据
{
    'timestamp': '2024-01-01 10:00:00',
    'open': 100.0,
    'high': 102.0,
    'low': 99.0,
    'close': 101.0,
    'volume': 1000000
}

# 日线数据
bars = self.get_daily_bars('AAPL', days=252)

# 分钟数据
bars = self.get_minute_bars('AAPL', days=5)
```

## 🔍 数据查询

### 股票列表

```python
# 获取所有股票
stocks = self.get_stocks()

# 获取指定市场股票
stocks = self.get_stocks(market='US')
stocks = self.get_stocks(market='CN')

# 搜索股票
results = self.search_stocks(keyword='Apple')
```

### 财务数据

```python
# 获取财务报表
financials = self.get_financials('AAPL')
print(financials.revenue)
print(financials.net_income)

# 获取估值指标
metrics = self.get_metrics('AAPL')
print(metrics.pe_ratio)
print(metrics.pb_ratio)
```

## 📉 技术指标

### 内置指标

```python
# 移动平均
sma = self.sma(period=20)
ema = self.ema(period=20)

# 动量指标
rsi = self.rsi(period=14)
macd = self.macd(fast=12, slow=26, signal=9)

# 波动率指标
bollinger = self.bollinger_bands(period=20, std=2)
atr = self.atr(period=14)

# 成交量指标
obv = self.obv()
vwap = self.vwap()
```

### 自定义指标

```python
def custom_indicator(prices):
    """自定义指标"""
    return (prices[-1] - prices[-10]) / prices[-10]

result = self.apply_indicator(custom_indicator)
```

## 💾 数据缓存

```python
# 加载缓存数据
data = self.load_cache('AAPL_daily')

# 保存缓存
self.save_cache('AAPL_daily', data)

# 清除缓存
self.clear_cache()

# 检查缓存
if self.is_cache_valid('AAPL_daily', max_age=3600):
    data = self.load_cache('AAPL_daily')
```

## 🌐 数据源配置

```yaml
data:
  source: 'alpaca'      # 数据源
  api_key: 'xxx'        # API 密钥
  cache_dir: './cache'  # 缓存目录
  update_freq: 60       # 更新频率（秒）
```

## 📚 示例代码

```python
from openfinagent import Strategy

class DataExample(Strategy):
    def on_bar(self, bar):
        # 获取历史数据
        closes = self.get_closes(100)
        
        # 计算指标
        sma20 = self.sma(20)
        rsi = self.rsi(14)
        
        # 获取实时行情
        quote = self.get_quote(self.symbol)
        
        # 使用数据
        if closes[-1] > sma20 and rsi < 30:
            self.buy()
```

## 📚 相关文档

- [API 索引](index.md)
- [交易接口](trading.md)
- [策略接口](strategy.md)

---

_数据是量化交易的基础，请确保数据质量。_
