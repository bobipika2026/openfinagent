# 教程 2: 创建自定义策略

在本教程中，你将学习如何创建 OpenFinAgent 内置策略之外的自定义策略。

---

## 📖 教程目录

- [学习目标](#学习目标)
- [前置知识](#前置知识)
- [策略基类介绍](#策略基类介绍)
- [示例 1: 简单自定义策略](#示例 1-简单自定义策略)
- [示例 2: 带技术指标的策略](#示例 2-带技术指标的策略)
- [示例 3: 多条件复合策略](#示例 3-多条件复合策略)
- [注册和使用自定义策略](#注册和使用自定义策略)
- [调试和测试](#调试和测试)
- [下一步](#下一步)

---

## 🎯 学习目标

完成本教程后，你将能够：

- ✅ 理解 OpenFinAgent 的策略架构
- ✅ 继承 `BaseStrategy` 创建自定义策略
- ✅ 实现 `on_bar()` 方法定义交易逻辑
- ✅ 使用技术指标生成交易信号
- ✅ 注册和复用自定义策略

---

## 📋 前置知识

建议先完成：
- [教程 1: 创建你的第一个策略](01-first-strategy.md)

需要了解：
- Python 基础语法
- 类和继承的概念
- 基本的量化交易知识

---

## 策略基类介绍

### BaseStrategy 结构

OpenFinAgent 的所有策略都继承自 `BaseStrategy` 基类：

```python
from tradeflow.strategy import BaseStrategy

class BaseStrategy:
    """策略基类"""
    
    def __init__(self, name: str, initial_capital: float = 100000):
        self.name = name
        self.initial_capital = initial_capital
        self.position = 0  # 当前持仓
        self.cash = initial_capital  # 当前现金
    
    def on_bar(self, data, index: int) -> dict:
        """
        每个 K 线周期调用一次
        
        参数:
            data: pandas DataFrame，包含历史数据
            index: 当前 K 线索引
        
        返回:
            dict: 交易指令，格式如下：
            {
                'action': 'buy' | 'sell' | 'hold',
                'price': float,      # 价格
                'shares': int,       # 数量
            }
        """
        raise NotImplementedError
```

### on_bar() 方法

这是策略的核心方法，每个交易周期（如每天）都会被调用。

**输入参数**:
- `data`: 包含历史 OHLCV 数据的 DataFrame
- `index`: 当前 K 线的索引位置

**返回值**:
- `dict`: 交易指令，包含动作、价格、数量

---

## 示例 1: 简单自定义策略

### 策略逻辑

> **收盘价突破策略**:
> - 当收盘价突破 20 日最高价时 → 买入
> - 当收盘价跌破 20 日最低价时 → 卖出

### 代码实现

创建文件 `custom_strategy_1.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义策略 1: 收盘价突破策略
"""

import pandas as pd
from tradeflow.strategy import BaseStrategy
from tradeflow import BacktestEngine
from tradeflow.backtest.engine import load_data


class BreakoutStrategy(BaseStrategy):
    """收盘价突破策略"""
    
    def __init__(self, lookback: int = 20, initial_capital: float = 100000):
        super().__init__(name='收盘价突破策略', initial_capital=initial_capital)
        self.lookback = lookback  # 回看周期
    
    def on_bar(self, data, index: int) -> dict:
        # 确保有足够的数据
        if index < self.lookback:
            return {'action': 'hold'}
        
        # 获取当前数据
        current_close = data['close'].iloc[index]
        
        # 计算过去 N 日的最高价和最低价
        high_window = data['high'].iloc[index-self.lookback:index]
        low_window = data['low'].iloc[index-self.lookback:index]
        
        highest_high = high_window.max()
        lowest_low = low_window.min()
        
        # 生成交易信号
        if current_close > highest_high:
            # 突破买入
            return {
                'action': 'buy',
                'price': current_close,
                'shares': self.calculate_shares(current_close)
            }
        elif current_close < lowest_low:
            # 跌破卖出
            return {
                'action': 'sell',
                'price': current_close,
                'shares': self.position
            }
        
        return {'action': 'hold'}
    
    def calculate_shares(self, price: float) -> int:
        """计算买入股数（使用 90% 仓位）"""
        available_cash = self.cash * 0.9
        shares = int(available_cash / price / 100) * 100  # A 股 100 股一手
        return max(shares, 0)


def main():
    print("=" * 60)
    print("🚀 自定义策略 1: 收盘价突破策略")
    print("=" * 60)
    
    # 创建策略
    strategy = BreakoutStrategy(lookback=20, initial_capital=100000)
    print(f"✅ 策略创建成功：{strategy.name}")
    
    # 加载数据
    data = load_data("600519.SH", "2023-01-01", "2023-12-31", source='mock')
    print(f"✅ 数据加载完成：{len(data)} 条")
    
    # 运行回测
    engine = BacktestEngine(commission_rate=0.0003, slippage=0.001)
    results = engine.run(strategy, data, show_progress=True)
    
    # 显示结果
    results.show()
    
    # 保存结果
    results.to_csv('breakout_strategy_trades.csv')
    print("\n✅ 回测完成！交易记录已保存。")


if __name__ == "__main__":
    main()
```

### 运行回测

```bash
python custom_strategy_1.py
```

---

## 示例 2: 带技术指标的策略

### 策略逻辑

> **RSI 超买超卖策略**:
> - 当 RSI < 30（超卖）时 → 买入
> - 当 RSI > 70（超买）时 → 卖出

### 代码实现

创建文件 `custom_strategy_2.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义策略 2: RSI 超买超卖策略
"""

import pandas as pd
import numpy as np
from tradeflow.strategy import BaseStrategy
from tradeflow import BacktestEngine
from tradeflow.backtest.engine import load_data


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    计算 RSI 指标
    
    参数:
        prices: 价格序列
        period: RSI 周期（默认 14）
    
    返回:
        RSI 值序列
    """
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


class RSIStrategy(BaseStrategy):
    """RSI 超买超卖策略"""
    
    def __init__(self, rsi_period: int = 14, 
                 oversold: float = 30, 
                 overbought: float = 70,
                 initial_capital: float = 100000):
        super().__init__(name='RSI 超买超卖策略', initial_capital=initial_capital)
        self.rsi_period = rsi_period
        self.oversold = oversold      # 超卖阈值
        self.overbought = overbought  # 超买阈值
    
    def on_bar(self, data, index: int) -> dict:
        # 确保有足够的数据计算 RSI
        if index < self.rsi_period + 10:
            return {'action': 'hold'}
        
        # 获取收盘价序列
        closes = data['close'].iloc[:index+1]
        
        # 计算 RSI
        rsi = calculate_rsi(closes, self.rsi_period)
        current_rsi = rsi.iloc[-1]
        
        # 获取当前价格
        current_price = data['close'].iloc[index]
        
        # 生成交易信号
        if current_rsi < self.oversold and self.position == 0:
            # RSI 超卖，买入
            return {
                'action': 'buy',
                'price': current_price,
                'shares': self.calculate_shares(current_price)
            }
        elif current_rsi > self.overbought and self.position > 0:
            # RSI 超买，卖出
            return {
                'action': 'sell',
                'price': current_price,
                'shares': self.position
            }
        
        return {'action': 'hold'}
    
    def calculate_shares(self, price: float) -> int:
        """计算买入股数（使用 80% 仓位）"""
        available_cash = self.cash * 0.8
        shares = int(available_cash / price / 100) * 100
        return max(shares, 0)


def main():
    print("=" * 60)
    print("🚀 自定义策略 2: RSI 超买超卖策略")
    print("=" * 60)
    
    # 创建策略
    strategy = RSIStrategy(
        rsi_period=14,
        oversold=30,
        overbought=70,
        initial_capital=100000
    )
    print(f"✅ 策略创建成功：{strategy.name}")
    
    # 加载数据
    data = load_data("600519.SH", "2023-01-01", "2023-12-31", source='mock')
    print(f"✅ 数据加载完成：{len(data)} 条")
    
    # 运行回测
    engine = BacktestEngine()
    results = engine.run(strategy, data, show_progress=True)
    
    # 显示结果
    results.show()
    
    print("\n✅ 回测完成！")


if __name__ == "__main__":
    main()
```

### 运行回测

```bash
python custom_strategy_2.py
```

---

## 示例 3: 多条件复合策略

### 策略逻辑

> **均线 + RSI 复合策略**:
> - 条件 1: 5 日均线上穿 20 日均线（趋势向上）
> - 条件 2: RSI < 40（未超买）
> - 当两个条件同时满足时 → 买入
> - 当 5 日均线下穿 20 日均线时 → 卖出

### 代码实现

创建文件 `custom_strategy_3.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义策略 3: 均线 + RSI 复合策略
"""

import pandas as pd
import numpy as np
from tradeflow.strategy import BaseStrategy
from tradeflow import BacktestEngine
from tradeflow.backtest.engine import load_data


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """计算 RSI 指标"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_ma(prices: pd.Series, period: int) -> pd.Series:
    """计算均线"""
    return prices.rolling(window=period).mean()


class CompositeStrategy(BaseStrategy):
    """均线 + RSI 复合策略"""
    
    def __init__(self, 
                 short_window: int = 5,
                 long_window: int = 20,
                 rsi_period: int = 14,
                 rsi_threshold: float = 40,
                 initial_capital: float = 100000):
        super().__init__(name='均线+RSI 复合策略', initial_capital=initial_capital)
        self.short_window = short_window
        self.long_window = long_window
        self.rsi_period = rsi_period
        self.rsi_threshold = rsi_threshold
    
    def on_bar(self, data, index: int) -> dict:
        # 确保有足够的数据
        min_data_needed = max(self.long_window, self.rsi_period) + 10
        if index < min_data_needed:
            return {'action': 'hold'}
        
        # 获取收盘价序列
        closes = data['close'].iloc[:index+1]
        
        # 计算均线
        ma_short = calculate_ma(closes, self.short_window)
        ma_long = calculate_ma(closes, self.long_window)
        
        # 计算 RSI
        rsi = calculate_rsi(closes, self.rsi_period)
        
        # 当前值
        current_price = closes.iloc[-1]
        current_ma_short = ma_short.iloc[-1]
        current_ma_long = ma_long.iloc[-1]
        current_rsi = rsi.iloc[-1]
        
        # 前一个值（用于判断交叉）
        prev_ma_short = ma_short.iloc[-2]
        prev_ma_long = ma_long.iloc[-2]
        
        # 判断金叉：短期均线上穿长期均线
        golden_cross = (prev_ma_short <= prev_ma_long) and (current_ma_short > current_ma_long)
        
        # 判断死叉：短期均线下穿长期均线
        death_cross = (prev_ma_short >= prev_ma_long) and (current_ma_short < current_ma_long)
        
        # 生成交易信号
        if golden_cross and current_rsi < self.rsi_threshold and self.position == 0:
            # 金叉 + RSI 未超买，买入
            return {
                'action': 'buy',
                'price': current_price,
                'shares': self.calculate_shares(current_price)
            }
        elif death_cross and self.position > 0:
            # 死叉，卖出
            return {
                'action': 'sell',
                'price': current_price,
                'shares': self.position
            }
        
        return {'action': 'hold'}
    
    def calculate_shares(self, price: float) -> int:
        """计算买入股数"""
        available_cash = self.cash * 0.8
        shares = int(available_cash / price / 100) * 100
        return max(shares, 0)


def main():
    print("=" * 60)
    print("🚀 自定义策略 3: 均线+RSI 复合策略")
    print("=" * 60)
    
    # 创建策略
    strategy = CompositeStrategy(
        short_window=5,
        long_window=20,
        rsi_period=14,
        rsi_threshold=40,
        initial_capital=100000
    )
    print(f"✅ 策略创建成功：{strategy.name}")
    
    # 加载数据
    data = load_data("600519.SH", "2023-01-01", "2023-12-31", source='mock')
    
    # 运行回测
    engine = BacktestEngine()
    results = engine.run(strategy, data, show_progress=True)
    
    # 显示结果
    results.show()
    
    print("\n✅ 回测完成！")


if __name__ == "__main__":
    main()
```

### 运行回测

```bash
python custom_strategy_3.py
```

---

## 注册和使用自定义策略

### 注册自定义策略

你可以将自定义策略注册到 `StrategyBuilder`，然后用自然语言方式调用：

```python
from tradeflow import StrategyBuilder
from custom_strategy_3 import CompositeStrategy

# 注册策略
StrategyBuilder.register_strategy('composite', CompositeStrategy)

# 使用注册的战略
strategy = StrategyBuilder.create(
    'composite',
    short_window=5,
    long_window=20,
    rsi_period=14,
    rsi_threshold=40,
    initial_capital=100000
)
```

### 查看已注册策略

```python
# 列出所有可用策略
available_strategies = StrategyBuilder.list_strategies()
print("可用策略:", available_strategies)
```

---

## 调试和测试

### 打印调试信息

在 `on_bar()` 中添加打印语句：

```python
def on_bar(self, data, index: int) -> dict:
    # 每 50 个交易日打印一次状态
    if index % 50 == 0:
        print(f"Day {index}: 价格={data['close'].iloc[index]:.2f}, "
              f"仓位={self.position}, 现金={self.cash:.2f}")
    
    # ... 策略逻辑
```

### 回测中间状态

```python
# 运行回测时显示进度
results = engine.run(strategy, data, show_progress=True)

# 查看交易记录
print("交易记录:")
for trade in results.trades:
    print(f"{trade['timestamp']}: {trade['type']} {trade['shares']}股 @ ¥{trade['price']:.2f}")
```

### 单元测试

创建文件 `test_custom_strategy.py`：

```python
import unittest
import pandas as pd
import numpy as np
from custom_strategy_1 import BreakoutStrategy


class TestBreakoutStrategy(unittest.TestCase):
    
    def setUp(self):
        """准备测试数据"""
        self.strategy = BreakoutStrategy(lookback=20, initial_capital=100000)
        
        # 创建模拟数据
        dates = pd.date_range('2023-01-01', periods=100, freq='B')
        self.data = pd.DataFrame({
            'open': np.random.uniform(100, 110, 100),
            'high': np.random.uniform(110, 115, 100),
            'low': np.random.uniform(95, 100, 100),
            'close': np.random.uniform(100, 110, 100),
            'volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
    
    def test_initial_state(self):
        """测试初始状态"""
        self.assertEqual(self.strategy.position, 0)
        self.assertEqual(self.strategy.cash, 100000)
    
    def test_no_signal_insufficient_data(self):
        """测试数据不足时无信号"""
        signal = self.strategy.on_bar(self.data, 10)
        self.assertEqual(signal['action'], 'hold')
    
    def test_buy_signal(self):
        """测试买入信号"""
        # 创建一个突破场景
        self.data.loc[50:, 'close'] = 150  # 价格突然上涨
        self.data.loc[50:, 'high'] = 155
        
        signal = self.strategy.on_bar(self.data, 60)
        # 应该产生买入信号或持有（取决于具体实现）
        self.assertIn(signal['action'], ['buy', 'hold'])


if __name__ == '__main__':
    unittest.main()
```

运行测试：

```bash
python test_custom_strategy.py
```

---

## 📝 练习任务

### 任务 1: 修改 RSI 阈值

尝试不同的 RSI 超买超卖阈值（如 20/80、25/75），观察对回测结果的影响。

### 任务 2: 添加止损功能

在策略中添加止损逻辑：

```python
def on_bar(self, data, index: int) -> dict:
    # 检查持仓是否有止损
    if self.position > 0:
        current_price = data['close'].iloc[index]
        if current_price < self.entry_price * 0.9:  # 10% 止损
            return {
                'action': 'sell',
                'price': current_price,
                'shares': self.position
            }
    
    # ... 其他逻辑
```

### 任务 3: 实现双均线策略

使用自定义策略的方式实现双均线交叉策略，对比与内置策略的差异。

### 任务 4: 添加成交量过滤

在买入条件中添加成交量放大过滤：

```python
# 成交量放大 20%
avg_volume = data['volume'].iloc[index-20:index].mean()
current_volume = data['volume'].iloc[index]
volume_confirmed = current_volume > avg_volume * 1.2
```

---

## 💡 最佳实践

1. **保持逻辑清晰**: 策略逻辑应该简单明了，避免过度复杂
2. **充分测试**: 在不同市场环境下测试策略
3. **风险控制**: 始终设置止损和仓位限制
4. **代码复用**: 将通用逻辑封装成函数
5. **文档注释**: 为策略添加清晰的注释和文档

---

## ❓ 常见问题

### Q: on_bar() 返回的 dict 有哪些字段？

A: 

```python
# 买入
{'action': 'buy', 'price': 100.5, 'shares': 1000}

# 卖出
{'action': 'sell', 'price': 102.3, 'shares': 1000}

# 持有
{'action': 'hold'}
```

### Q: 如何获取实时数据？

A: 当前版本仅支持历史数据回测。实时数据功能计划中。

### Q: 可以在策略中使用机器学习吗？

A: 可以！在 `on_bar()` 中调用机器学习模型生成信号即可。

---

## 🎓 下一步

- 📊 [教程 3: 真实数据回测](03-real-backtest.md)
- 📚 [策略语法参考](../strategy-syntax.md)
- 🔧 [API 参考](../api_reference.md)
- 💬 [用户案例](../showcase.md)

---

**继续进阶，创建属于你的量化策略！** 🚀
