# OpenFinAgent 快速入门

欢迎使用 OpenFinAgent！本指南将帮助你在 **10 分钟内** 开始第一个量化策略回测。

---

## 📖 目录

- [快速安装](#快速安装)
- [第一个策略](#第一个策略)
- [运行示例](#运行示例)
- [核心概念](#核心概念)
- [性能指标](#性能指标)
- [常见问题](#常见问题)
- [下一步](#下一步)

---

## 📦 快速安装

### 方法 1: 使用 Git（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/bobipika2026/openfinagent.git
cd openfinagent

# 2. 安装依赖
pip install -r requirements.txt

# 3. 验证安装
python -c "from openfinagent import StrategyBuilder; print('✅ 安装成功！')"
```

### 方法 2: 使用 pip

```bash
# 直接从 PyPI 安装（如已发布）
pip install openfinagent
```

### 方法 3: 下载源码

```bash
# 1. 下载 ZIP 文件
# 访问 https://github.com/bobipika2026/openfinagent 下载源码

# 2. 解压并安装
cd openfinagent
pip install -r requirements.txt
```

### 环境要求

- ✅ Python 3.9 或更高版本
- ✅ 操作系统：Windows / macOS / Linux
- ✅ 内存：至少 2GB

---

## 🚀 第一个策略

### 5 分钟快速开始

创建文件 `my_first_strategy.py`：

```python
from openfinagent import StrategyBuilder, BacktestEngine
from openfinagent.backtest.engine import load_data

# 步骤 1: 用自然语言创建策略
strategy = StrategyBuilder.from_natural_language("""
当 5 日均线上穿 20 日均线时买入
当 5 日均线下穿 20 日均线时卖出
初始资金 10 万元
""")

# 步骤 2: 加载数据（使用模拟数据，无需 API）
data = load_data(
    symbol="600519.SH",
    start_date="2023-01-01",
    end_date="2023-12-31",
    source='mock'
)

# 步骤 3: 运行回测
engine = BacktestEngine()
results = engine.run(strategy, data)

# 步骤 4: 查看结果
results.show()

# 步骤 5: 生成图表
results.plot()
```

运行：

```bash
python my_first_strategy.py
```

### 预期输出

```
============================================================
📊 均线交叉策略 回测结果
============================================================
总收益 (%)              15.23
年化收益 (%)            15.23
波动率 (%)              18.45
夏普比率                0.83
最大回撤 (%)            -12.34
交易次数                24
胜率 (%)                58.33
初始资金            100,000.00
最终资金            115,230.00
============================================================
```

---

## 📊 运行示例

项目包含丰富的示例代码：

### 基础示例

```bash
# 均线交叉策略
cd examples/basic
python 01_ma_cross_strategy.py

# 动量策略
python 02_momentum_strategy.py
```

### 高级示例

```bash
# 多策略对比
cd examples/advanced
python 01_multi_strategy_compare.py
```

### 实战示例

```bash
# A 股回测
cd examples/real_world
python 01_a_stock_backtest.py
```

---

## 🔧 核心概念

### 策略 (Strategy)

策略是交易规则的定义。OpenFinAgent 提供两种创建方式：

#### 1. 自然语言创建

适合快速原型和新手：

```python
strategy = StrategyBuilder.from_natural_language("""
当 5 日均线上穿 20 日均线时买入
当 5 日均线下穿 20 日均线时卖出
初始资金 10 万元
""")
```

#### 2. 参数化创建

适合精确控制和高级用户：

```python
strategy = StrategyBuilder.create(
    'ma_cross',
    short_window=5,
    long_window=20,
    initial_capital=100000
)
```

### 回测引擎 (BacktestEngine)

回测引擎模拟真实交易环境：

```python
engine = BacktestEngine(
    commission_rate=0.0003,  # 手续费率：万分之三
    slippage=0.001,          # 滑点：0.1%
)
```

支持功能：

- ✅ 手续费设置
- ✅ 滑点模拟
- ✅ 仓位管理
- ✅ 交易记录
- ✅ 进度条显示

### 结果分析 (BacktestResults)

回测结果包含：

```python
# 显示结果
results.show()

# 绘制图表
results.plot()

# 保存交易记录
results.to_csv('trades.csv')

# 获取指标
print(results.metrics)
```

---

## 📈 性能指标

### 核心指标说明

| 指标 | 说明 | 计算公式 | 合理范围 |
|------|------|---------|---------|
| 总收益 | 策略总收益率 | (最终资金 - 初始资金) / 初始资金 | > 0% |
| 年化收益 | 年化收益率 | (1 + 总收益)^(365/天数) - 1 | > 10% |
| 波动率 | 收益波动程度 | 日收益率的标准差 × √252 | - |
| 夏普比率 | 风险调整后收益 | (年化收益 - 无风险利率) / 波动率 | > 1.0 |
| 最大回撤 | 最大亏损幅度 | 最大峰值到谷底的跌幅 | < 20% |
| 交易次数 | 总交易次数 | 买入 + 卖出次数 | - |
| 胜率 | 盈利交易比例 | 盈利交易数 / 总交易数 | > 50% |

### 指标解读示例

```
总收益：15.23%
→ 策略全年盈利 15.23%，跑赢银行理财

年化收益：15.23%
→ 如果每年都能获得同样收益，年化为 15.23%

夏普比率：0.83
→ 每承担 1 单位风险，获得 0.83 单位超额收益
→ >1.0 为优秀，0.5-1.0 为良好

最大回撤：-12.34%
→ 历史上最大亏损幅度为 12.34%
→ <10% 低风险，10-20% 中等风险

胜率：58.33%
→ 58.33% 的交易盈利
→ >50% 说明策略逻辑有效
```

---

## ❓ 常见问题

### Q1: 如何获取真实股票数据？

**A**: OpenFinAgent 支持多种数据源：

```python
# A 股数据（AKShare - 免费）
data = load_data("600519.SH", "2023-01-01", "2023-12-31", source='akshare')

# 美股数据（Yahoo Finance - 免费）
data = load_data("AAPL", "2023-01-01", "2023-12-31", source='yfinance')

# 模拟数据（无需 API）
data = load_data("600519.SH", "2023-01-01", "2023-12-31", source='mock')
```

### Q2: 如何自定义策略？

**A**: 继承 `BaseStrategy` 类：

```python
from openfinagent.strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def on_bar(self, data, index):
        # 你的交易逻辑
        if condition:
            return {'action': 'buy', 'price': price, 'shares': 100}
        return {'action': 'hold'}
```

详见：[教程 2: 创建自定义策略](tutorials/02-custom-strategy.md)

### Q3: 回测结果不准确怎么办？

**A**: 检查以下设置：

1. **手续费率**: A 股约万分之三
   ```python
   engine = BacktestEngine(commission_rate=0.0003)
   ```

2. **滑点设置**: 默认 0.1%
   ```python
   engine = BacktestEngine(slippage=0.001)
   ```

3. **数据质量**: 使用可靠数据源
   ```python
   data = load_data("600519.SH", "2023-01-01", "2023-12-31", source='akshare')
   ```

4. **回测周期**: 至少 1 年数据
   ```python
   data = load_data("600519.SH", "2020-01-01", "2023-12-31", source='akshare')
   ```

### Q4: 支持哪些市场？

**A**: 

| 市场 | 代码格式 | 数据源 |
|------|---------|--------|
| A 股 | `600519.SH` | AKShare |
| 美股 | `AAPL` | Yahoo Finance |
| 港股 | `0700.HK` | Yahoo Finance |
| 加密货币 | `BTCUSDT` | Binance |

### Q5: 需要 API 密钥吗？

**A**: 

- **不需要**: 使用模拟数据 (`source='mock'`) 可以立即开始
- **需要**: 如果要获取真实市场数据，需要相应数据源的 API 密钥

### Q6: 回测需要多长时间？

**A**: 取决于数据量和策略复杂度：

- 1 年数据，简单策略：1-5 秒
- 5 年数据，复杂策略：10-30 秒

---

## 🎓 下一步

### 学习路径

```
1. ✅ 快速入门（本页面）
   ↓
2. 📖 [教程 1: 第一个策略](tutorials/01-first-strategy.md)
   ↓
3. 📝 [策略语法参考](strategy-syntax.md)
   ↓
4. 🔧 [API 参考](api_reference.md)
   ↓
5. 🎓 [教程 2: 自定义策略](tutorials/02-custom-strategy.md)
   ↓
6. 📊 [教程 3: 真实数据回测](tutorials/03-real-backtest.md)
```

### 推荐资源

- 📚 [完整教程集合](tutorials/) - 从零开始的系列教程
- 💡 [策略语法](strategy-syntax.md) - 自然语言策略语法详解
- 🔧 [API 参考](api_reference.md) - 完整接口文档
- ❓ [常见问题](faq.md) - FAQ 与问题解答
- 🌟 [用户案例](showcase.md) - 真实用户策略分享

### 获取帮助

- 📖 文档：[docs/](./)
- 💬 示例：[examples/](../examples/)
- 🐛 问题：[GitHub Issues](https://github.com/bobipika2026/openfinagent/issues)
- 💬 讨论：[GitHub Discussions](https://github.com/bobipika2026/openfinagent/discussions)

---

<div align="center">

**开始你的量化交易之旅吧！** 🚀

[运行第一个策略](#第一个策略) · [查看示例](#运行示例) · [阅读教程](tutorials/)

</div>
