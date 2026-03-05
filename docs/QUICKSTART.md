# ⚡ 5 分钟上手 TradeFlow AI

> 从 0 到 1，用自然语言创建你的第一个量化策略

---

## 📋 前置要求

- ✅ Python 3.11+ 
- ✅ 基础命令行知识
- ✅ 无需量化交易经验
- ✅ 无需编程基础

---

## 🚀 Step 1: 安装（1 分钟）

### 方式一：pip 安装（推荐）
```bash
pip install tradeflow-ai
```

### 方式二：源码安装
```bash
git clone https://github.com/tradeflow-ai/tradeflow-ai.git
cd tradeflow-ai
pip install -e .
```

### 验证安装
```bash
tradeflow --version
# 应输出：TradeFlow AI v0.1.0
```

---

## 🎯 Step 2: 创建第一个策略（2 分钟）

### 打开 Python
```bash
python
```

### 输入以下代码
```python
from tradeflow import Strategy

# 用自然语言描述你的策略
strategy = Strategy.from_natural_language(
    "当 5 日均线上穿 20 日均线时买入，下穿时卖出"
)

# 查看生成的策略代码
print(strategy.code)
```

### 你会看到类似输出
```python
# 自动生成的策略代码
class MAStrategy(Strategy):
    def __init__(self):
        self.short_ma = 5   # 短期均线
        self.long_ma = 20   # 长期均线
    
    def on_bar(self, bar):
        if self.cross_over(self.short_ma, self.long_ma):
            self.buy()      # 金叉买入
        elif self.cross_under(self.short_ma, self.long_ma):
            self.sell()     # 死叉卖出
```

---

## 📊 Step 3: 回测策略（2 分钟）

### 执行回测
```python
# 回测过去一年的表现
results = strategy.backtest(
    start_date="2023-01-01",
    end_date="2024-01-01",
    symbol="000001.SZ",  # 平安银行
    initial_capital=100000  # 初始资金 10 万
)

# 查看回测结果
print(results.summary())
```

### 回测输出示例
```
═══════════════════════════════════════
         策略回测报告
═══════════════════════════════════════
初始资金：     ¥100,000
最终资金：     ¥123,500
总收益率：     23.50%
年化收益：     23.50%
最大回撤：     -12.30%
夏普比率：     1.85
交易次数：     24
胜率：         58.33%
盈亏比：       2.1:1
═══════════════════════════════════════
```

### 可视化回测曲线
```python
# 绘制资金曲线
results.plot_equity_curve()

# 绘制交易信号
results.plot_trades()
```

---

## 🎨 Step 4: 优化策略（可选）

### 添加止损止盈
```python
strategy = Strategy.from_natural_language(
    "当 5 日均线上穿 20 日均线时买入，下穿时卖出，"
    "止损 5%，止盈 15%，仓位 50%"
)
```

### 添加多个条件
```python
strategy = Strategy.from_natural_language(
    "当 5 日均线上穿 20 日均线，且 RSI 小于 70 时买入，"
    "下穿时卖出，止损 5%，止盈 15%"
)
```

---

## 📦 Step 5: 保存和分享策略

### 保存策略到本地
```python
# 保存策略
strategy.save("my_ma_strategy.json")

# 加载策略
strategy = Strategy.load("my_ma_strategy.json")
```

### 导出为 Python 文件
```python
# 导出为可独立运行的 Python 文件
strategy.export_to_file("my_strategy.py")
```

### 分享到策略市场
```python
# 发布到社区策略市场
strategy.publish_to_market(
    name="双均线策略 v1.0",
    description="基于 5 日/20 日均线的趋势跟踪策略",
    tags=["均线", "趋势跟踪", "A 股"]
)
```

---

## 🎓 下一步学习

### 基础教程
- [策略示例库](EXAMPLES.md) - 20+ 现成策略模板
- [指标大全](indicators.md) - 所有可用技术指标
- [数据源配置](data_sources.md) - 连接不同市场数据

### 进阶教程
- [多 Agent 协作](multi_agent.md) - 组建 AI 投顾团队
- [自定义指标](custom_indicators.md) - 创建自己的指标
- [实盘部署](live_trading.md) - 连接真实交易账户

### 社区资源
- [Discord 社区](https://discord.gg/tradeflow) - 实时问答
- [策略排行榜](https://tradeflow.ai/leaderboard) - 学习优秀策略
- [月度挑战](https://tradeflow.ai/challenges) - 参与策略比赛

---

## ❓ 常见问题

### Q: 我没有编程基础，能学会吗？
**A**: 完全可以！TradeFlow AI 的核心设计理念就是"会说话就能写策略"。你只需用自然语言描述想法，AI 会自动生成代码。

### Q: 回测收益高，实盘也能赚这么多吗？
**A**: 不一定。回测是历史数据的表现，实盘受滑点、手续费、市场冲击等因素影响。建议：
1. 充分回测（至少 3-5 年数据）
2. 模拟盘测试 1-3 个月
3. 小资金实盘验证
4. 逐步增加仓位

### Q: 支持哪些市场？
**A**: 目前支持：
- ✅ A 股（沪深京）
- ✅ 美股
- ✅ 加密货币（BTC/ETH 等主流币种）
- 🚧 外汇（开发中）
- 🚧 期货（开发中）

### Q: 需要付费吗？
**A**: TradeFlow AI 核心功能完全开源免费。策略市场部分高级策略可能需要付费，但基础功能永久免费。

### Q: 如何获取实时数据？
**A**: 
- A 股：AkShare（免费）、Tushare（部分免费）
- 美股：YFinance（免费）、AlphaVantage（免费额度）
- 加密货币：Binance/OKX API（免费）

详细配置见 [数据源配置指南](data_sources.md)

---

## 🆘 遇到问题？

### 获取帮助
1. 📚 查看 [完整文档](https://tradeflow.ai/docs)
2. 💬 加入 [Discord 社区](https://discord.gg/tradeflow)
3. 🐛 提交 [GitHub Issue](https://github.com/tradeflow-ai/tradeflow-ai/issues)
4. 📧 发送邮件至 support@tradeflow.ai

### 常见错误排查
```bash
# 检查 Python 版本
python --version  # 需要 3.11+

# 检查依赖安装
pip list | grep tradeflow

# 重新安装
pip install --upgrade tradeflow-ai

# 清除缓存重试
tradeflow cache clear
```

---

## 🎉 恭喜你！

你已经完成了 TradeFlow AI 的入门教程！

**接下来你可以：**
1. ⭐ Star 项目支持我们
2. 🎯 尝试 [策略示例库](EXAMPLES.md) 中的模板
3. 💡 创建你自己的原创策略
4. 🤝 加入社区，和其他量化爱好者交流
5. 📢 分享你的第一个策略成果

---

<div align="center">

**🚀 开始你的量化交易之旅吧！**

[← 返回主页](../README.md) · [策略示例 →](EXAMPLES.md)

</div>
