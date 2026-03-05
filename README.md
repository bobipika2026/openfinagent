# TradeFlow AI

AI 量化交易助手 - 用自然语言写量化策略

## 简介

TradeFlow AI 是一个智能量化交易助手，允许用户使用自然语言描述交易策略，自动转换为可执行的量化交易代码。

## 特性

- 🤖 自然语言策略描述
- 📈 自动代码生成
- 🔍 策略回测
- 📊 实时市场分析
- 🛡️ 风险管理

## 支持的市场

- A 股 (Stock)
- 美股
- 加密货币
- 外汇

## 快速开始

```python
from tradeflow import Strategy

# 用自然语言定义策略
strategy = Strategy.from_natural_language(
    "当 5 日均线上穿 20 日均线时买入，下穿时卖出"
)

# 回测策略
results = strategy.backtest("2023-01-01", "2024-01-01")

# 执行交易
strategy.execute()
```

## 安装

```bash
pip install tradeflow-ai
```

## 话题

quantitative-trading, ai, trading, python, stock

## License

MIT License
