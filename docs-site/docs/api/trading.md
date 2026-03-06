# 交易接口

交易接口提供了完整的订单管理和仓位管理功能。

## 📦 订单管理

### 下单

```python
from openfinagent import Order, OrderType, OrderSide

# 市价单
order = Order(
    symbol='AAPL',
    side=OrderSide.BUY,
    type=OrderType.MARKET,
    quantity=100
)
order_id = self.submit_order(order)

# 限价单
order = Order(
    symbol='AAPL',
    side=OrderSide.BUY,
    type=OrderType.LIMIT,
    quantity=100,
    price=150.0
)
order_id = self.submit_order(order)

# 止损单
order = Order(
    symbol='AAPL',
    side=OrderSide.SELL,
    type=OrderType.STOP,
    quantity=100,
    stop_price=140.0
)
order_id = self.submit_order(order)
```

### 撤单

```python
# 撤销订单
self.cancel_order(order_id)

# 撤销所有订单
self.cancel_all_orders()

# 撤销指定品种的订单
self.cancel_orders(symbol='AAPL')
```

### 订单查询

```python
# 查询订单状态
order = self.get_order(order_id)
print(order.status)

# 查询所有订单
orders = self.get_orders()

# 查询未成交订单
pending_orders = self.get_pending_orders()

# 查询历史订单
history = self.get_order_history(days=7)
```

## 💼 仓位管理

### 仓位查询

```python
# 查询所有仓位
positions = self.get_positions()

# 查询指定品种仓位
position = self.get_position('AAPL')
print(position.quantity)
print(position.avg_price)

# 查询仓位总值
total_value = self.get_position_value()

# 查询可用资金
available_cash = self.get_available_cash()
```

### 仓位计算

```python
# 计算盈亏
pnl = self.get_pnl()
unrealized_pnl = self.get_unrealized_pnl()
realized_pnl = self.get_realized_pnl()

# 计算仓位占比
weight = self.get_position_weight('AAPL')

# 计算总仓位
total_position = self.get_total_position()
```

## 🎯 交易执行

### 直接交易

```python
# 买入
self.buy(symbol='AAPL', quantity=100)
self.buy(symbol='AAPL', value=10000)  # 按金额买入

# 卖出
self.sell(symbol='AAPL', quantity=100)
self.sell(symbol='AAPL', percent=0.5)  # 卖出 50%

# 平仓
self.close_position('AAPL')
self.close_all_positions()
```

### 条件交易

```python
# 止盈止损
self.buy(symbol='AAPL', quantity=100)
self.set_stop_loss('AAPL', stop_price=140.0)
self.set_take_profit('AAPL', take_price=170.0)

# 追踪止损
self.set_trailing_stop('AAPL', trail_percent=0.05)
```

## 📊 交易统计

```python
# 今日交易统计
today_stats = self.get_today_stats()
print(today_stats.trade_count)
print(today_stats.trade_volume)

# 交易历史
trades = self.get_trades(days=30)

# 交易分析
analysis = self.analyze_trades()
print(analysis.win_rate)
print(analysis.avg_profit)
print(analysis.avg_loss)
```

## ⚙️ 交易配置

```yaml
trading:
  paper_trading: true      # 模拟交易
  max_position: 100000     # 最大仓位
  max_order_value: 50000   # 单笔最大订单
  commission_rate: 0.001   # 手续费率
  slippage: 0.001          # 滑点
```

## 🔒 风控规则

```python
# 设置风控规则
self.set_risk_rule('max_position', 100000)
self.set_risk_rule('max_daily_loss', 5000)
self.set_risk_rule('max_drawdown', 0.1)

# 检查风控
if self.check_risk_limit(order):
    self.submit_order(order)
else:
    print("触发风控限制")
```

## 📈 示例代码

```python
from openfinagent import Strategy

class TradingExample(Strategy):
    def on_bar(self, bar):
        # 获取仓位
        position = self.get_position('AAPL')
        
        if not position:
            # 开仓
            self.buy('AAPL', quantity=100)
            self.set_stop_loss('AAPL', stop_price=bar.close * 0.95)
            self.set_take_profit('AAPL', take_price=bar.close * 1.10)
        else:
            # 检查是否需要平仓
            if self.get_pnl() > 1000:
                self.close_position('AAPL')
```

## 📚 相关文档

- [API 索引](index.md)
- [数据接口](data.md)
- [策略接口](strategy.md)

---

_交易接口是策略执行的核心，请谨慎使用。_
