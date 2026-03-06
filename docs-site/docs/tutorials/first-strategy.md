# 第一个策略

本教程将带你创建第一个交易策略，了解 OpenFinAgent 的基本用法。

## 🎯 学习目标

- 理解策略的基本结构
- 学会使用策略基类
- 掌握信号生成方法
- 运行简单的回测

## 📝 步骤 1: 导入模块

```python
from openfinagent import Strategy, Signal, SignalType
from openfinagent import Backtester
```

## 📝 步骤 2: 创建策略类

```python
class FirstStrategy(Strategy):
    """我的第一个策略"""
    
    def __init__(self, window=20):
        """初始化策略"""
        super().__init__(name="FirstStrategy")
        self.window = window
    
    def on_bar(self, bar):
        """处理每个 K 线"""
        # 获取历史收盘价
        closes = self.get_closes(self.window + 1)
        
        # 数据不足时跳过
        if len(closes) < self.window + 1:
            return
        
        # 计算移动平均
        ma = sum(closes[-self.window:]) / self.window
        current_price = closes[-1]
        
        # 生成交易信号
        if current_price > ma * 1.02:
            # 价格高于均线 2%，买入
            self.emit_signal(Signal(
                type=SignalType.BUY,
                strength=0.8,
                reason="价格突破均线"
            ))
        elif current_price < ma * 0.98:
            # 价格低于均线 2%，卖出
            self.emit_signal(Signal(
                type=SignalType.SELL,
                strength=1.0,
                reason="价格跌破均线"
            ))
```

## 📝 步骤 3: 运行回测

```python
# 创建策略实例
strategy = FirstStrategy(window=20)

# 配置回测
backtester = Backtester(
    strategy=strategy,
    data_file='data/stock_data.csv',
    initial_capital=100000,  # 初始资金
    commission=0.001,        # 手续费率
    start_date='2023-01-01',
    end_date='2023-12-31'
)

# 运行回测
results = backtester.run()
```

## 📝 步骤 4: 查看结果

```python
# 输出回测报告
print(results.summary())

# 关键指标
print(f"总收益率：{results.total_return:.2%}")
print(f"年化收益率：{results.annual_return:.2%}")
print(f"最大回撤：{results.max_drawdown:.2%}")
print(f"夏普比率：{results.sharpe_ratio:.2f}")
print(f"交易次数：{results.trade_count}")
print(f"胜率：{results.win_rate:.2%}")

# 绘制资金曲线
results.plot()
```

## 📊 完整代码

```python
from openfinagent import Strategy, Signal, SignalType, Backtester

class FirstStrategy(Strategy):
    """我的第一个策略"""
    
    def __init__(self, window=20):
        super().__init__(name="FirstStrategy")
        self.window = window
    
    def on_bar(self, bar):
        closes = self.get_closes(self.window + 1)
        
        if len(closes) < self.window + 1:
            return
        
        ma = sum(closes[-self.window:]) / self.window
        current_price = closes[-1]
        
        if current_price > ma * 1.02:
            self.emit_signal(Signal(
                type=SignalType.BUY,
                strength=0.8,
                reason="价格突破均线"
            ))
        elif current_price < ma * 0.98:
            self.emit_signal(Signal(
                type=SignalType.SELL,
                strength=1.0,
                reason="价格跌破均线"
            ))

# 运行回测
if __name__ == '__main__':
    strategy = FirstStrategy(window=20)
    
    backtester = Backtester(
        strategy=strategy,
        data_file='data/stock_data.csv',
        initial_capital=100000,
        commission=0.001
    )
    
    results = backtester.run()
    print(results.summary())
    results.plot()
```

## 🔧 参数调优

```python
# 尝试不同的参数
for window in [10, 20, 30, 50]:
    strategy = FirstStrategy(window=window)
    backtester = Backtester(strategy, data_file='data.csv')
    results = backtester.run()
    
    print(f"Window={window}: "
          f"Return={results.total_return:.2%}, "
          f"Sharpe={results.sharpe_ratio:.2f}")
```

## 💡 改进建议

1. **添加止损**: 控制单笔损失
2. **添加止盈**: 锁定利润
3. **仓位管理**: 不要全仓进出
4. **多指标结合**: 使用更多技术指标

## 📚 下一步

- [回测实战](backtesting.md) - 学习高级回测技巧
- [策略文档](../strategies/) - 了解更多策略
- [API 参考](../api/strategy.md) - 查看完整 API

## ✅ 练习

1. 修改阈值（1.02 和 0.98）
2. 添加成交量过滤
3. 添加止损逻辑
4. 尝试不同的均线周期

---

_恭喜你完成了第一个策略！继续学习下一个教程。_
