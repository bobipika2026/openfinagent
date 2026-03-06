# TradeFlow AI 🚀

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.2.0-green.svg)](https://github.com/bobipika2026/openfinagent)
[![Stars](https://img.shields.io/github/stars/bobipika2026/openfinagent)](https://github.com/bobipika2026/openfinagent)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**AI 量化交易助手 - 用自然语言写量化策略**

> 🎯 **用中文描述你的交易想法，AI 自动生成可执行的量化策略代码**

---

## 📖 目录

- [项目简介](#-项目简介)
- [核心特性](#-核心特性)
- [快速开始](#-快速开始)
- [使用示例](#-使用示例)
- [文档导航](#-文档导航)
- [项目结构](#-项目结构)
- [截图展示](#-截图展示)
- [贡献指南](#-贡献指南)
- [许可证](#-许可证)

---

## 📖 项目简介

TradeFlow AI 是一个**革命性的量化交易开发平台**，让没有编程背景的交易者也能轻松创建量化策略。

传统的量化交易需要掌握编程、数据处理、回测框架等复杂技能。TradeFlow AI 通过**自然语言处理技术**，让你只需用中文描述交易规则，AI 就会自动将其转换为可执行的策略代码，并提供专业的回测和可视化分析。

### 🎯 适用人群

- 📈 **股票交易者** - 验证交易想法，回测历史表现
- 💼 **量化爱好者** - 零代码基础也能创建策略
- 👨‍💻 **开发者** - 快速原型，专注策略逻辑而非框架
- 🎓 **学生/研究者** - 学习量化交易，进行策略研究

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🎯 **自然语言策略** | 用中文描述交易规则，AI 自动解析生成策略代码 |
| 📊 **智能回测引擎** | 支持 A 股/美股/加密货币，内置手续费和滑点模拟 |
| 📈 **可视化分析** | 权益曲线、回撤分析、指标雷达图一键生成 |
| 🔧 **灵活扩展** | 支持自定义指标、数据源和交易规则 |
| 🌐 **中文友好** | 完整的中文文档、示例和社区支持 |
| 🧪 **多策略对比** | 同时回测多个策略，直观对比性能 |
| 📦 **开箱即用** | 内置模拟数据，无需 API 密钥即可开始 |

---

## 🚀 快速开始

### 1️⃣ 安装依赖

```bash
# 克隆项目
git clone https://github.com/your-org/tradeflow-ai.git
cd tradeflow-ai

# 安装依赖
pip install -r requirements.txt

# 验证安装
python -c "from tradeflow import StrategyBuilder; print('✅ 安装成功！')"
```

### 2️⃣ 第一个策略（5 分钟）

创建文件 `my_strategy.py`：

```python
from tradeflow import StrategyBuilder, BacktestEngine
from tradeflow.backtest.engine import load_data

# 用自然语言描述策略
strategy = StrategyBuilder.from_natural_language("""
当 5 日均线上穿 20 日均线时买入
当 5 日均线下穿 20 日均线时卖出
初始资金 10 万元
""")

# 加载数据并运行回测
data = load_data("600519.SH", "2023-01-01", "2023-12-31", source='mock')
engine = BacktestEngine()
results = engine.run(strategy, data)

# 查看结果
results.show()
results.plot()
```

运行：

```bash
python my_strategy.py
```

### 3️⃣ 运行示例

```bash
# 基础示例 - 均线交叉策略
python examples/basic/01_ma_cross_strategy.py

# 高级示例 - 多策略对比
python examples/advanced/01_multi_strategy_compare.py

# 实战示例 - A 股回测
python examples/real_world/01_a_stock_backtest.py
```

---

## 💡 使用示例

### 示例 1: 均线交叉策略

```python
strategy = StrategyBuilder.from_natural_language("""
当 5 日均线上穿 20 日均线时买入
当 5 日均线下穿 20 日均线时卖出
初始资金 10 万元
""")
```

### 示例 2: 动量策略

```python
strategy = StrategyBuilder.from_natural_language("""
动量策略
看 20 天收益率
超过 5% 买入
低于 -5% 卖出
初始资金 50 万元
""")
```

### 示例 3: 参数化创建策略

```python
strategy = StrategyBuilder.create(
    'ma_cross',
    short_window=10,
    long_window=30,
    initial_capital=200000,
    name='双均线策略 (10/30)'
)
```

### 示例 4: 多策略对比

```python
from tradeflow import StrategyBuilder, BacktestEngine

# 创建多个策略
strategies = [
    StrategyBuilder.create('ma_cross', short_window=5, long_window=20),
    StrategyBuilder.create('ma_cross', short_window=10, long_window=30),
    StrategyBuilder.create('momentum', lookback=20, threshold=0.05),
]

# 批量回测
engine = BacktestEngine()
results = engine.run_multi(strategies, data)

# 对比结果
for name, result in results.items():
    print(f"{name}: 年化收益 {result.metrics['年化收益']:.2f}%")
```

---

## 📚 文档导航

| 文档 | 说明 |
|------|------|
| 📖 [快速入门](docs/getting_started.md) | 5 分钟上手指南 |
| 📝 [策略语法参考](docs/strategy-syntax.md) | 自然语言策略语法详解 |
| 🔧 [API 参考](docs/api_reference.md) | 完整 API 接口文档 |
| 🎓 [教程集合](docs/tutorials/) | 从零开始的系列教程 |
| ❓ [常见问题](docs/faq.md) | FAQ 与问题解答 |
| 🌟 [用户案例](docs/showcase.md) | 真实用户策略分享 |

---

## 📁 项目结构

```
tradeflow-ai/
├── README.md                    # 项目说明（本文件）
├── CONTRIBUTING.md              # 贡献指南
├── requirements.txt             # Python 依赖包
├── setup.py                     # 安装脚本
├── run_demo.py                  # 快速演示脚本
│
├── src/                         # 核心源代码
│   ├── __init__.py
│   ├── strategy/                # 策略引擎
│   │   ├── base.py              # 策略基类
│   │   └── builder.py           # 策略构建器
│   ├── nlp/                     # 自然语言处理
│   │   └── parser.py            # 策略解析器
│   ├── backtest/                # 回测引擎
│   │   ├── engine.py            # 回测引擎
│   │   └── results.py           # 回测结果
│   ├── visualization/           # 可视化模块
│   │   └── plotter.py           # 策略绘图器
│   └── utils/                   # 工具函数
│
├── examples/                    # 示例代码
│   ├── basic/                   # 基础示例
│   ├── advanced/                # 高级示例
│   └── real_world/              # 实战示例
│
├── docs/                        # 文档
│   ├── getting_started.md       # 快速入门
│   ├── strategy-syntax.md       # 策略语法
│   ├── api_reference.md         # API 参考
│   ├── faq.md                   # 常见问题
│   ├── showcase.md              # 用户案例
│   └── tutorials/               # 教程
│       ├── 01-first-strategy.md
│       ├── 02-custom-strategy.md
│       └── 03-real-backtest.md
│
└── tests/                       # 测试文件
    ├── test_strategy.py
    └── test_backtest.py
```

---

## 🖼️ 截图展示

### 回测结果展示

![回测结果示例](docs/images/backtest_result.png)
*回测结果包含权益曲线、性能指标和交易记录*

### 策略对比图

![策略对比](docs/images/strategy_comparison.png)
*多策略性能对比，直观展示各策略优劣*

### 指标雷达图

![指标雷达图](docs/images/metrics_radar.png)
*多维度指标雷达图，全面评估策略表现*

> 📸 **截图位置**: 所有截图位于 `docs/images/` 目录
> 
> 🎬 **动图演示**: 查看 `docs/gifs/` 目录获取操作演示动图

---

## 📊 回测指标

系统自动计算以下专业指标：

| 指标 | 说明 | 合理范围 |
|------|------|----------|
| 总收益 (%) | 策略总收益率 | > 0% |
| 年化收益 (%) | 年化收益率 | > 10% |
| 夏普比率 | 风险调整后收益 | > 1.0 |
| 最大回撤 (%) | 最大亏损幅度 | < 20% |
| 胜率 (%) | 盈利交易比例 | > 50% |
| 交易次数 | 总交易次数 | - |

---

## 🤝 贡献指南

欢迎贡献代码、文档、示例策略或问题反馈！

- 🐛 报告问题 → [GitHub Issues](https://github.com/your-org/tradeflow-ai/issues)
- 💡 提交建议 → [GitHub Discussions](https://github.com/your-org/tradeflow-ai/discussions)
- 🔧 贡献代码 → 阅读 [CONTRIBUTING.md](CONTRIBUTING.md)
- 📝 改进文档 → 提交 PR

### 贡献者

感谢所有为 TradeFlow AI 做出贡献的开发者！

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🔗 相关链接

- 🏠 官方网站：https://tradeflow.ai
- 📚 文档中心：https://docs.tradeflow.ai
- 💬 社区论坛：https://community.tradeflow.ai
- 🐦 关注更新：https://twitter.com/tradeflow_ai

---

<div align="center">

**开始你的量化交易之旅吧！** 🚀

[快速入门](docs/getting_started.md) · [查看示例](examples/) · [加入社区](#)

</div>
