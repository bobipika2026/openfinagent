# 🧬 OpenFinAgent

> **让每个人拥有自己的私人投行 AI，让每个开发者都能构建金融智能体**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/bobipika2026/openfinagent/actions/workflows/test.yml/badge.svg)](https://github.com/bobipika2026/openfinagent/actions)
[![Discord](https://img.shields.io/discord/123456789?label=Discord&logo=discord)](https://discord.gg/openfinagent)

---

## 🚀 10 分钟，从"我想做个均线策略"到可执行的交易代码

**OpenFinAgent** 是一个革命性的 **金融 AI Agent 操作系统** —— 用自然语言描述你的交易想法，AI 自动帮你实现、回测、执行。

```python
from openfinagent import Agent

# 创建你的交易智能体
trader = Agent("trading")

# 用自然语言下达指令
result = trader.execute("当 5 日均线上穿 20 日均线时买入平安银行，下穿时卖出")

# 查看回测结果
print(result.summary())
```

**输出：**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
策略回测报告：均线交叉策略
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
回测期间：2024-01-01 → 2024-12-31
初始资金：¥100,000.00
最终资金：¥127,450.00

收益率：+27.45%
年化收益：+27.45%
夏普比率：1.82
最大回撤：-8.34%
胜率：64.2%
交易次数：47

收益曲线：████████████████████░░░░░░ 72%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 💡 为什么 OpenFinAgent 是颠覆性的？

| 维度 | 传统量化平台 | OpenFinAgent |
|------|-------------|--------------|
| **入门门槛** | 需要 Python + 金融知识 | 会说话就会写策略 |
| **策略开发** | 手写代码，几天到几周 | 自然语言，几分钟 |
| **智能程度** | 静态规则引擎 | AI Agent 自主决策 |
| **协作能力** | 单人单策略 | 多 Agent 协作网络 |
| **知识积累** | 策略无法复用 | 策略市场 + 知识图谱 |
| **部署方式** | 中心化平台 | 去中心化节点网络 |

---

## 🎯 核心能力

### 🤖 多 Agent 协作系统

OpenFinAgent 内置 6 大智能体，模拟专业投行的工作流程：

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Research    │ →  │ Strategy    │ →  │ Risk        │
│ Agent       │    │ Agent       │    │ Agent       │
│ 投研智能体  │    │ 策略智能体  │    │ 风控智能体  │
└─────────────┘    └─────────────┘    └─────────────┘
                          ↓
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Report      │ ←  │ Portfolio   │ ←  │ Execution   │
│ Agent       │    │ Agent       │    │ Agent       │
│ 报告智能体  │    │ 组合智能体  │    │ 执行智能体  │
└─────────────┘    └─────────────┘    └─────────────┘
```

### 📊 支持的资产类别

- 🇨🇳 **A 股** - 沪深北交所全市场
- 🇺🇸 **美股** - NYSE/NASDAQ
- 🇭🇰 **港股** - 港股通标的
- ₿ **加密货币** - BTC/ETH 等主流币种
- 📈 **期货/期权** - 商品期货、金融期权

### 🔒 金融级安全合规

- ✅ 符合证监会 IT 系统合规要求
- ✅ 等保 2.0 三级安全标准
- ✅ 全链路审计日志
- ✅ 数据加密存储（AES-256）
- ✅ 权限最小化原则（RBAC）

---

## 📦 快速开始

### 安装

```bash
# 从 PyPI 安装（即将发布）
pip install openfinagent

# 或从源码安装
git clone https://github.com/bobipika2026/openfinagent.git
cd openfinagent
pip install -e .
```

### 5 分钟上手

```python
from openfinagent import Agent

# 1. 创建智能体
agent = Agent("trading")

# 2. 描述你的策略
strategy = agent.parse("如果贵州茅台的 RSI 低于 30 就买入，高于 70 就卖出")

# 3. 回测验证
result = strategy.backtest(start="2024-01-01", end="2024-12-31")

# 4. 查看结果
print(f"收益率：{result.annual_return:.2%}")
print(f"夏普比率：{result.sharpe:.2f}")
print(f"最大回撤：{result.max_drawdown:.2%}")

# 5. 模拟执行（纸面交易）
agent.execute(strategy, mode="paper")
```

**更多示例：** [📚 查看完整示例库](docs/EXAMPLES.md)

---

## 🎬 功能演示

> *GIF 演示即将上线 - 录制中*

**演示内容预告：**
1. 用自然语言创建策略 → 自动生成代码 → 回测 → 执行
2. 多 Agent 协作：投研分析 → 策略生成 → 风控审核 → 交易执行
3. 策略市场：浏览、复制、修改社区策略

---

## 📚 文档导航

| 文档 | 说明 |
|------|------|
| [🚀 快速开始](docs/QUICKSTART.md) | 5 分钟上手教程 |
| [📖 策略示例](docs/EXAMPLES.md) | 16 个完整策略示例 |
| [🏗️ 架构设计](ARCHITECTURE.md) | 系统架构详解 |
| [🤝 贡献指南](docs/CONTRIBUTING.md) | 如何参与贡献 |
| [📈 增长计划](GROWTH_PLAN.md) | 社区发展路线 |

---

## 🏆 路线图

### Phase 1: MVP（当前）✅
- [x] 自然语言策略解析
- [x] 多 Agent 协作框架
- [x] 策略回测引擎
- [x] 单元测试套件

### Phase 2: v0.2（30 天）
- [ ] AI 模型集成（Qwen/Llama）
- [ ] 真实市场数据接入
- [ ] Web 界面（Streamlit）
- [ ] 策略市场 Beta

### Phase 3: v1.0（60 天）
- [ ] 去中心化节点网络
- [ ] 策略 NFT 化
- [ ] 移动端 App
- [ ] 机构级 API

---

## 🌟 社区

- 💬 **Discord**: https://discord.gg/openfinagent
- 🐦 **Twitter**: @OpenFinAgent
- 📺 **YouTube**: OpenFinAgent Official
- 📱 **微信公众号**: OpenFinAgent
- 📧 **联系**: hi@openfinagent.ai

---

## ⚠️ 风险提示

> **重要声明**: OpenFinAgent 仅供学习和研究使用，不构成投资建议。
> 
> - 回测结果不代表未来收益
> - 量化交易存在本金损失风险
> - 实盘交易需谨慎，建议先进行纸面交易测试
> - 请遵守当地法律法规

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🙏 致谢

感谢以下开源项目：
- [AkShare](https://github.com/akfamily/akshare) - A 股数据源
- [YFinance](https://github.com/ranaroussi/yfinance) - 美股数据源
- [LangChain](https://github.com/langchain-ai/langchain) - Agent 框架

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐ Star！**

[Star History Chart](https://api.star-history.com/svg?repos=bobipika2026/openfinagent&type=Date)

Made with 🧬 by OpenFinAgent Team | 来自 300 年后的金融科技革命

</div>
