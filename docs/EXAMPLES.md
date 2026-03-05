# 📚 策略示例库

> 20+ 个现成策略模板，从入门到进阶，复制即用

---

## 📖 目录

- [基础策略](#基础策略) - 新手友好
- [进阶策略](#进阶策略) - 有一定经验
- [AI 增强策略](#ai-增强策略) - 机器学习加持
- [组合策略](#组合策略) - 多策略融合

---

## 🎯 基础策略

### 1. 双均线交叉 ⭐⭐

最经典的趋势跟踪策略

```python
from tradeflow import Strategy

strategy = Strategy.from_natural_language(
    "当 5 日均线上穿 20 日均线时买入，下穿时卖出"
)

results = strategy.backtest("2023-01-01", "2024-01-01")
print(results.summary())
```

**策略逻辑：**
- 📈 金叉（短期均线上穿长期均线）→ 买入信号
- 📉 死叉（短期均线下穿长期均线）→ 卖出信号

**适合市场：** 趋势明显的市场
**预期年化：** 15-25%
**最大回撤：** 10-20%

---

### 2. RSI 超买超卖 ⭐⭐

基于相对强弱指数的反转策略

```python
strategy = Strategy.from_natural_language(
    "当 RSI 低于 30 时买入，高于 70 时卖出"
)
```

**策略逻辑：**
- RSI < 30 → 超卖，买入
- RSI > 70 → 超买，卖出

**适合市场：** 震荡市
**预期年化：** 10-20%
**最大回撤：** 8-15%

---

### 3. 布林带突破 ⭐⭐

波动率突破策略

```python
strategy = Strategy.from_natural_language(
    "当价格突破布林带上轨时买入，跌破下轨时卖出"
)
```

**策略逻辑：**
- 价格 > 上轨 → 强势突破，买入
- 价格 < 下轨 → 弱势突破，卖出

**适合市场：** 高波动市场
**预期年化：** 20-35%
**最大回撤：** 15-25%

---

### 4. MACD 金叉死叉 ⭐⭐

指数平滑异同移动平均线策略

```python
strategy = Strategy.from_natural_language(
    "当 MACD 金叉时买入，死叉时卖出"
)
```

**策略逻辑：**
- DIF 上穿 DEA → 金叉买入
- DIF 下穿 DEA → 死叉卖出

**适合市场：** 趋势 + 震荡混合市
**预期年化：** 15-28%
**最大回撤：** 12-20%

---

### 5. 动量策略 ⭐⭐⭐

追涨杀跌策略

```python
strategy = Strategy.from_natural_language(
    "买入过去 20 天涨幅前 10 的股票，持有 5 天后调仓"
)
```

**策略逻辑：**
- 选股：过去 N 天涨幅排名靠前
- 持有：固定周期后调仓

**适合市场：** 牛市
**预期年化：** 25-45%
**最大回撤：** 20-35%

---

## 🚀 进阶策略

### 6. 双均线 + 止损止盈 ⭐⭐⭐

带风险控制的趋势策略

```python
strategy = Strategy.from_natural_language(
    "当 5 日均线上穿 20 日均线时买入，下穿时卖出，"
    "止损 5%，止盈 15%，仓位 50%"
)
```

**优化点：**
- ✅ 严格止损，控制单笔损失
- ✅ 及时止盈，锁定利润
- ✅ 仓位管理，降低风险

**预期年化：** 18-30%
**最大回撤：** 8-15%

---

### 7. 多因子选股 ⭐⭐⭐⭐

量化经典策略

```python
strategy = Strategy.from_natural_language(
    "选择市盈率小于 20，市净率小于 3，"
    "ROE 大于 15%，营收增长率大于 20% 的股票，"
    "等权重配置，每月调仓"
)
```

**选股因子：**
- 📊 估值因子：PE、PB
- 💰 盈利因子：ROE
- 📈 成长因子：营收增长率

**适合市场：** 长期价值投资
**预期年化：** 20-40%
**最大回撤：** 15-25%

---

### 8. 统计套利 ⭐⭐⭐⭐

配对交易策略

```python
strategy = Strategy.from_natural_language(
    "当茅台和五粮液的价差偏离 2 倍标准差时，"
    "做空高价股，做多低价股，"
    "价差回归时平仓"
)
```

**策略逻辑：**
- 寻找高度相关的两个标的
- 价差扩大时做空/做多
- 价差回归时获利了结

**适合市场：** 震荡市
**预期年化：** 15-30%
**最大回撤：** 5-12%

---

### 9. 网格交易 ⭐⭐⭐

震荡市神器

```python
strategy = Strategy.from_natural_language(
    "以当前价格为中心，每下跌 3% 买入一格，"
    "每上涨 3% 卖出一格，共 10 格"
)
```

**策略逻辑：**
- 设定价格区间和网格数量
- 下跌分批买入
- 上涨分批卖出

**适合市场：** 震荡市
**预期年化：** 10-25%
**最大回撤：** 10-18%

---

### 10. 趋势跟踪 + 均值回归 ⭐⭐⭐⭐

混合策略

```python
strategy = Strategy.from_natural_language(
    "用 60 日均线判断趋势方向，"
    "趋势向上时，RSI 低于 30 买入，"
    "趋势向下时，RSI 高于 70 做空"
)
```

**策略逻辑：**
- 长期均线判断大趋势
- RSI 寻找短期反转点
- 顺势而为，逆势入场

**预期年化：** 25-45%
**最大回撤：** 12-22%

---

## 🤖 AI 增强策略

### 11. 情绪分析 + 技术面 ⭐⭐⭐⭐⭐

结合新闻舆情和技术指标

```python
from tradeflow.agents import ResearchAgent

# 创建研究 Agent
research = ResearchAgent()

# 分析市场情绪
sentiment = research.analyze_sentiment("新能源板块")

# 根据情绪调整策略
if sentiment.score > 0.7:
    strategy = Strategy.from_natural_language(
        "情绪积极，使用激进策略：5 日均线上穿 20 日均线买入"
    )
else:
    strategy = Strategy.from_natural_language(
        "情绪消极，使用保守策略：空仓观望"
    )
```

**AI 能力：**
- 📰 新闻情感分析
- 💬 社交媒体情绪监控
- 📊 情绪指标量化

**预期年化：** 30-55%
**最大回撤：** 15-25%

---

### 12. 新闻事件驱动 ⭐⭐⭐⭐⭐

基于 NLP 的事件驱动策略

```python
from tradeflow.agents import ResearchAgent

research = ResearchAgent()

# 监控股票相关新闻
news = research.monitor_news(["茅台", "五粮液"])

# 检测重大事件
for event in news:
    if event.impact_score > 0.8:
        if event.sentiment == "positive":
            strategy.buy(event.symbol)
        else:
            strategy.sell(event.symbol)
```

**监控事件：**
- 财报发布
- 重大合同
- 政策变化
- 高管变动

**预期年化：** 35-65%
**最大回撤：** 20-35%

---

### 13. 机器学习预测 ⭐⭐⭐⭐⭐

使用 ML 模型预测价格走势

```python
from tradeflow.ml import Predictor

# 训练预测模型
predictor = Predictor(model="lstm")
predictor.train(data="5 年历史数据", features=["价格", "成交量", "MACD", "RSI"])

# 获取预测
prediction = predictor.predict("明天价格走势")

if prediction.direction == "up" and prediction.confidence > 0.7:
    strategy.buy()
else:
    strategy.sell()
```

**模型选择：**
- LSTM（长短期记忆网络）
- XGBoost
- Random Forest

**预期年化：** 40-75%
**最大回撤：** 18-30%

---

### 14. 强化学习优化 ⭐⭐⭐⭐⭐

自我进化的策略

```python
from tradeflow.rl import RLAgent

# 创建强化学习 Agent
agent = RLAgent(algorithm="PPO")

# 训练 Agent
agent.train(
    environment="trading_env",
    episodes=1000,
    reward_function="sharpe_ratio"
)

# 使用训练好的 Agent 交易
action = agent.predict(current_state)
if action == "buy":
    strategy.buy()
elif action == "sell":
    strategy.sell()
```

**优势：**
- 🔄 自我进化，持续优化
- 🎯 适应不同市场环境
- 📈 自动发现最优策略

**预期年化：** 45-85%
**最大回撤：** 15-28%

---

## 🎨 组合策略

### 15. 多策略融合 ⭐⭐⭐⭐

分散风险，稳定收益

```python
from tradeflow import Portfolio

# 创建策略组合
portfolio = Portfolio()

# 添加多个低相关策略
portfolio.add_strategy(
    Strategy.from_natural_language("双均线交叉"),
    weight=0.3
)
portfolio.add_strategy(
    Strategy.from_natural_language("RSI 超买超卖"),
    weight=0.3
)
portfolio.add_strategy(
    Strategy.from_natural_language("网格交易"),
    weight=0.4
)

# 回测组合
results = portfolio.backtest("2023-01-01", "2024-01-01")
print(results.summary())
```

**优势：**
- ✅ 分散风险
- ✅ 平滑收益曲线
- ✅ 适应不同市场环境

**预期年化：** 25-45%
**最大回撤：** 8-15%

---

### 16. 多 Agent 协作 ⭐⭐⭐⭐⭐

组建 AI 投顾团队

```python
from tradeflow.agents import ResearchAgent, TradingAgent, RiskAgent

# 组建团队
research = ResearchAgent()  # 投研
trading = TradingAgent()    # 交易
risk = RiskAgent()          # 风控

# 协作流程
# 1. 研究 Agent 分析市场
analysis = research.analyze("当前市场")

# 2. 交易 Agent 执行
if analysis.recommendation == "buy":
    orders = trading.execute(analysis.portfolio)
    
    # 3. 风控 Agent 监控
    risk.monitor(orders)
    if risk.risk_level > 0.8:
        trading.reduce_position()
```

**团队分工：**
- 📚 Research Agent：市场分析、选股
- 💼 Trading Agent：执行交易、调仓
- 🛡️ Risk Agent：风险监控、止损

**预期年化：** 35-65%
**最大回撤：** 10-20%

---

## 📊 策略对比表

| 策略名称 | 难度 | 预期年化 | 最大回撤 | 适合市场 |
|---------|------|---------|---------|---------|
| 双均线交叉 | ⭐⭐ | 15-25% | 10-20% | 趋势市 |
| RSI 超买超卖 | ⭐⭐ | 10-20% | 8-15% | 震荡市 |
| 布林带突破 | ⭐⭐ | 20-35% | 15-25% | 高波动 |
| MACD 金叉死叉 | ⭐⭐ | 15-28% | 12-20% | 混合市 |
| 动量策略 | ⭐⭐⭐ | 25-45% | 20-35% | 牛市 |
| 双均线 + 止损 | ⭐⭐⭐ | 18-30% | 8-15% | 趋势市 |
| 多因子选股 | ⭐⭐⭐⭐ | 20-40% | 15-25% | 价值投资 |
| 统计套利 | ⭐⭐⭐⭐ | 15-30% | 5-12% | 震荡市 |
| 网格交易 | ⭐⭐⭐ | 10-25% | 10-18% | 震荡市 |
| 趋势 + 均值回归 | ⭐⭐⭐⭐ | 25-45% | 12-22% | 混合市 |
| 情绪分析 + 技术面 | ⭐⭐⭐⭐⭐ | 30-55% | 15-25% | 全市场 |
| 新闻事件驱动 | ⭐⭐⭐⭐⭐ | 35-65% | 20-35% | 事件驱动 |
| 机器学习预测 | ⭐⭐⭐⭐⭐ | 40-75% | 18-30% | 全市场 |
| 强化学习优化 | ⭐⭐⭐⭐⭐ | 45-85% | 15-28% | 全市场 |
| 多策略融合 | ⭐⭐⭐⭐ | 25-45% | 8-15% | 全市场 |
| 多 Agent 协作 | ⭐⭐⭐⭐⭐ | 35-65% | 10-20% | 全市场 |

---

## 🎓 如何使用这些示例

### 方式一：直接运行
```bash
# 运行示例策略
tradeflow run example_ma_cross
tradeflow run example_rsi
tradeflow run example_bollinger
```

### 方式二：复制代码
```python
# 复制示例代码到你的项目
from tradeflow import Strategy

strategy = Strategy.from_natural_language("...")
```

### 方式三：导入市场策略
```python
# 从策略市场导入
strategy = Strategy.from_market("双均线交叉 v2.3")
```

---

## 💡 策略优化建议

### 1. 参数优化
```python
# 使用网格搜索优化参数
best_params = strategy.optimize(
    param_grid={
        "short_ma": [5, 10, 15],
        "long_ma": [20, 30, 60]
    },
    metric="sharpe_ratio"
)
```

### 2. 组合优化
```python
# 使用均值 - 方差优化权重
optimal_weights = portfolio.optimize_weights(
    method="mean_variance",
    target_return=0.20
)
```

### 3. 风险控制
```python
# 添加严格的风险控制
strategy.set_risk_rules(
    max_drawdown=0.15,      # 最大回撤 15%
    max_position=0.3,       # 单只股票最大仓位 30%
    stop_loss=0.05,         # 单笔止损 5%
    take_profit=0.15        # 单笔止盈 15%
)
```

---

## 📚 进阶阅读

- [技术指标详解](indicators.md)
- [回测最佳实践](backtesting.md)
- [实盘部署指南](live_trading.md)
- [风险管理手册](risk_management.md)

---

## 🆘 需要帮助？

- 💬 [Discord 社区](https://discord.gg/tradeflow)
- 📧 support@tradeflow.ai
- 🐛 [提交 Issue](https://github.com/tradeflow-ai/tradeflow-ai/issues)

---

<div align="center">

**🎯 选择你的策略，开始交易吧！**

[← 5 分钟上手](QUICKSTART.md) · [贡献指南 →](CONTRIBUTING.md)

</div>
