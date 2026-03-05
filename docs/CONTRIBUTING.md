# 🤝 贡献指南

> 欢迎加入 TradeFlow AI 开源社区，一起打造最好的量化交易平台

---

## 🎯 目录

- [贡献方式](#贡献方式)
- [开发环境搭建](#开发环境搭建)
- [提交流程](#提交流程)
- [代码规范](#代码规范)
- [策略贡献](#策略贡献)
- [文档贡献](#文档贡献)
- [社区角色](#社区角色)

---

## 🌟 贡献方式

你可以用多种方式参与贡献：

### 1️⃣ 代码贡献
- 🐛 修复 Bug
- ✨ 开发新功能
- 🔧 优化性能
- 🧪 编写测试用例

### 2️⃣ 策略贡献
- 📈 提交原创策略
- 📊 优化现有策略
- 💡 分享策略思路

### 3️⃣ 文档贡献
- 📚 改进文档
- 📝 翻译文档（中英互译）
- 🎥 制作教程视频

### 4️⃣ 社区贡献
- 💬 帮助回答社区问题
- 📢 推广项目
- 🎯 组织线上/线下活动

### 5️⃣ 反馈建议
- 🐛 报告 Bug
- 💡 提出功能建议
- 📊 分享使用体验

---

## 🛠️ 开发环境搭建

### Step 1: Fork 项目
```bash
# 在 GitHub 上点击 Fork 按钮
# 然后克隆你的 fork
git clone https://github.com/YOUR_USERNAME/tradeflow-ai.git
cd tradeflow-ai
```

### Step 2: 安装依赖
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -e ".[dev]"
```

### Step 3: 配置 Git
```bash
# 添加上游仓库
git remote add upstream https://github.com/tradeflow-ai/tradeflow-ai.git

# 验证配置
git remote -v
```

---

## 📝 提交流程

### 1. 创建分支
```bash
# 从 main 分支创建新分支
git checkout -b feature/your-feature-name

# 分支命名规范：
# feature/xxx - 新功能
# bugfix/xxx  - Bug 修复
# docs/xxx    - 文档更新
# refactor/xxx - 代码重构
# test/xxx    - 测试相关
```

### 2. 开发并提交
```bash
# 编写代码...

# 添加更改
git add .

# 提交（使用 Conventional Commits 规范）
git commit -m "feat: 添加 RSI 指标支持"
git commit -m "fix: 修复回测结果计算错误"
git commit -m "docs: 更新快速开始指南"
```

### 3. 同步上游代码
```bash
# 获取上游最新代码
git fetch upstream

# 变基到最新 main 分支
git rebase upstream/main
```

### 4. 推送并创建 PR
```bash
# 推送到你的 fork
git push origin feature/your-feature-name

# 在 GitHub 上创建 Pull Request
# 访问：https://github.com/tradeflow-ai/tradeflow-ai/compare
```

### 5. PR 模板
创建 PR 时，请填写以下信息：

```markdown
## 描述
简要说明这个 PR 做了什么

## 相关 Issue
Closes #123

## 改动类型
- [ ] 新功能
- [ ] Bug 修复
- [ ] 文档更新
- [ ] 性能优化
- [ ] 代码重构

## 测试
- [ ] 已添加单元测试
- [ ] 已手动测试
- [ ] 回测验证通过

## 截图（如适用）
[添加截图或 GIF]

## 检查清单
- [ ] 代码符合规范
- [ ] 文档已更新
- [ ] 无破坏性变更
```

---

## 📐 代码规范

### Python 代码规范

遵循 [PEP 8](https://pep8.org/) 标准：

```python
# ✅ 好的命名
class StrategyExecutor:
    def calculate_sharpe_ratio(self, returns):
        pass

# ❌ 避免的命名
class se:
    def calc(self, r):
        pass
```

### 类型注解
```python
# ✅ 使用类型注解
def backtest(
    start_date: str,
    end_date: str,
    initial_capital: float = 100000
) -> BacktestResult:
    pass
```

### 文档字符串
```python
# ✅ 完整的 docstring
def calculate_ma(prices: List[float], period: int) -> List[float]:
    """
    计算移动平均线
    
    Args:
        prices: 价格序列
        period: 均线周期
        
    Returns:
        均线值序列
        
    Example:
        >>> calculate_ma([1, 2, 3, 4, 5], 3)
        [None, None, 2.0, 3.0, 4.0]
    """
    pass
```

### 代码检查工具
```bash
# 运行代码检查
flake8 tradeflow/
black tradeflow/ --check
mypy tradeflow/

# 自动格式化
black tradeflow/
isort tradeflow/
```

---

## 📈 策略贡献

### 提交新策略

#### Step 1: 创建策略文件
```python
# tradeflow/strategies/my_strategy.py
from tradeflow import Strategy

class MyStrategy(Strategy):
    """
    策略名称：双均线增强版
    作者：Your Name
    描述：在传统双均线基础上增加成交量确认
    """
    
    def __init__(self, short_ma=5, long_ma=20):
        self.short_ma = short_ma
        self.long_ma = long_ma
    
    def on_bar(self, bar):
        # 策略逻辑
        if self.golden_cross() and self.volume_confirm():
            self.buy()
        elif self.dead_cross():
            self.sell()
    
    def golden_cross(self):
        # 金叉逻辑
        pass
    
    def volume_confirm(self):
        # 成交量确认
        pass
```

#### Step 2: 编写回测报告
```python
# strategies/my_strategy_backtest.py
from my_strategy import MyStrategy

strategy = MyStrategy()
results = strategy.backtest("2020-01-01", "2024-01-01")

print("=" * 50)
print("策略回测报告")
print("=" * 50)
print(f"年化收益：{results.annual_return:.2f}%")
print(f"最大回撤：{results.max_drawdown:.2f}%")
print(f"夏普比率：{results.sharpe_ratio:.2f}")
print(f"交易次数：{results.total_trades}")
print(f"胜率：{results.win_rate:.2f}%")
```

#### Step 3: 提交 PR
```bash
git add tradeflow/strategies/my_strategy.py
git add tests/test_my_strategy.py
git commit -m "feat(strategy): 添加双均线增强策略"
git push origin feature/strategy-my-strategy
```

### 策略审核标准

| 标准 | 要求 |
|------|------|
| 代码质量 | 符合规范，有注释 |
| 回测数据 | 至少 3 年历史数据 |
| 风险控制 | 包含止损机制 |
| 文档完整 | 策略说明、参数说明 |
| 测试覆盖 | 单元测试通过 |

---

## 📚 文档贡献

### 改进现有文档

1. 找到文档文件（`docs/` 目录）
2. 进行修改
3. 提交 PR

### 添加新文档

```markdown
# 文档标题

简要介绍

## 章节 1

内容...

## 章节 2

内容...

## 示例

```python
# 代码示例
```

## 参考链接

- [相关链接](url)
```

### 翻译文档

我们欢迎多语言文档：

```bash
docs/
├── QUICKSTART.md          # 英文原版
├── QUICKSTART.zh-CN.md    # 简体中文
├── QUICKSTART.ja.md       # 日文
└── QUICKSTART.es.md       # 西班牙文
```

---

## 🎭 社区角色

### Contributor（贡献者）
- 提交过至少 1 个 PR
- 获得 [Contributor Badge](https://github.com/tradeflow-ai/tradeflow-ai/graphs/contributors)

### Core Contributor（核心贡献者）
- 提交过 10+ 个高质量 PR
- 深度参与项目开发
- 获得仓库 Write 权限

### Maintainer（维护者）
- 负责特定模块的审核和维护
- 参与项目决策
- 获得仓库 Admin 权限

### Ambassador（大使）
- 积极推广项目
- 组织社区活动
- 制作教程内容

---

## 🏆 贡献者权益

### 所有贡献者
- ✅ GitHub Contributor Badge
- ✅ 项目 README 署名
- ✅ Discord 专属角色
- ✅ 优先获得技术支持

### 核心贡献者
- ✅ TradeFlow AI 周边礼品
- ✅ 受邀参加线下活动
- ✅ 推荐信（如需）
- ✅ 实习/工作内推机会

### 月度贡献之星
每月评选最活跃贡献者：
- 🏆 荣誉证书
- 🎁 精美礼品
- 📢 官方社交媒体宣传

---

## 💬 沟通渠道

### Discord
- 💬 [加入服务器](https://discord.gg/tradeflow)
- #contributors - 贡献者讨论
- #help - 求助问答
- #showcase - 成果展示

### GitHub
- 🐛 [Issues](https://github.com/tradeflow-ai/tradeflow-ai/issues) - Bug 报告和功能建议
- 💬 [Discussions](https://github.com/tradeflow-ai/tradeflow-ai/discussions) - 讨论交流
- 🔀 [Pull Requests](https://github.com/tradeflow-ai/tradeflow-ai/pulls) - 代码贡献

### 邮件
- 📧 contributors@tradeflow.ai - 贡献者相关
- 📧 support@tradeflow.ai - 技术支持

---

## ❓ 常见问题

### Q: 我没有量化经验，能贡献代码吗？
**A**: 当然可以！我们欢迎各种背景的贡献者。你可以从文档、测试、UI 等方向入手，逐步深入学习。

### Q: PR 多久会被审核？
**A**: 通常 2-3 个工作日内会有回复。如果超过一周未回复，可以在 Discord 或 Issue 中提醒。

### Q: 我的策略会被商用吗？
**A**: TradeFlow AI 使用 MIT 许可证，所有贡献的代码都遵循相同协议。策略作者享有署名权。

### Q: 如何成为核心贡献者？
**A**: 持续贡献高质量代码，积极参与社区建设。我们会主动邀请表现突出的贡献者加入核心团队。

### Q: 可以同时参与多个 Issue 吗？
**A**: 可以！但建议先完成手头的任务，再开始新的工作，避免分散精力。

---

## 🎯 当前需要帮助的领域

### 🔥 高优先级
- [ ] 完善单元测试（目标：覆盖率 80%+）
- [ ] 添加更多策略示例
- [ ] 改进文档（特别是中文文档）
- [ ] 性能优化（回测速度提升）

### 📋 中等优先级
- [ ] 前端界面优化
- [ ] 添加更多数据源支持
- [ ] 移动端适配
- [ ] 视频教程制作

### 💡 欢迎提议
- [ ] 新功能创意
- [ ] 策略创新
- [ ] 社区活动
- [ ] 合作伙伴关系

---

## 🙏 致谢

感谢所有为 TradeFlow AI 做出贡献的开发者们！

<!-- 这里将自动插入贡献者列表 -->

---

<div align="center">

**🚀 开始你的第一次贡献吧！**

[← 返回主页](../README.md) · [策略示例](EXAMPLES.md)

有任何问题？[加入 Discord](https://discord.gg/tradeflow) 或 [提交 Issue](https://github.com/tradeflow-ai/tradeflow-ai/issues)

</div>
