# 贡献指南

首先，感谢你愿意为 OpenFinAgent 做出贡献！🎉

本指南将帮助你了解如何参与项目贡献，包括报告问题、提交代码、改进文档等。

---

## 📖 目录

- [行为准则](#行为准则)
- [贡献方式](#贡献方式)
- [开发环境搭建](#开发环境搭建)
- [代码规范](#代码规范)
- [提交流程](#提交流程)
- [问题报告](#问题报告)
- [功能建议](#功能建议)
- [文档贡献](#文档贡献)
- [测试要求](#测试要求)
- [常见问题](#常见问题)

---

## 行为准则

在参与 OpenFinAgent 社区时，请遵守以下准则：

- 🤝 **友好包容**: 尊重不同背景、观点和经验的人
- 💬 **建设性沟通**: 提出批评时请提供改进建议
- 🎯 **专注主题**: 讨论围绕项目和技术展开
- 🚫 **零容忍**: 不允许骚扰、歧视或不当行为

---

## 贡献方式

你可以通过以下方式贡献：

### 1. 🐛 报告 Bug

发现 Bug？请提交 Issue：

- 使用清晰的标题
- 描述复现步骤
- 提供错误信息和截图
- 说明环境（Python 版本、操作系统）

### 2. 💡 功能建议

有新想法？欢迎提议：

- 描述功能需求和使用场景
- 说明为什么这个功能重要
- 如果可能，提供实现思路

### 3. 🔧 提交代码

修复 Bug 或添加功能：

- Fork 项目并创建分支
- 编写代码和测试
- 提交 Pull Request

### 4. 📝 改进文档

文档同样重要：

- 修正错别字和错误
- 补充缺失的说明
- 添加示例和教程
- 翻译文档（国际化）

### 5. 📢 推广项目

- 在社交媒体分享
- 写博客文章
- 在社区推荐
- 给朋友同事安利

---

## 开发环境搭建

### 1. Fork 和克隆

```bash
# 1. 在 GitHub 上 Fork 项目
# 访问 https://github.com/your-org/tradeflow-ai 点击 Fork

# 2. 克隆你的 Fork
git clone https://github.com/YOUR_USERNAME/tradeflow-ai.git
cd tradeflow-ai

# 3. 添加上游仓库（保持同步）
git remote add upstream https://github.com/your-org/tradeflow-ai.git
```

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install pytest pytest-cov black flake8 mypy
```

### 3. 创建分支

```bash
# 确保是最新代码
git checkout main
git pull upstream main

# 创建功能分支
git checkout -b feature/your-feature-name

# 或修复分支
git checkout -b fix/issue-123
```

---

## 代码规范

### Python 代码风格

遵循 PEP 8 规范：

```python
# ✅ 好的风格
def calculate_return(prices: list[float]) -> float:
    """计算收益率"""
    if len(prices) < 2:
        return 0.0
    return (prices[-1] - prices[0]) / prices[0]

# ❌ 避免
def calcRet(p):
    return (p[-1]-p[0])/p[0]
```

### 代码格式化

使用 Black 格式化代码：

```bash
# 安装 Black
pip install black

# 格式化代码
black src/ tests/ examples/

# 检查代码风格
flake8 src/ tests/
```

### 类型注解

使用类型注解提高代码可读性：

```python
from typing import Optional, Dict, List
import pandas as pd

def load_data(
    symbol: str,
    start_date: str,
    end_date: str,
    source: str = 'akshare'
) -> pd.DataFrame:
    """加载市场数据"""
    pass
```

### 注释和文档

- 函数必须有文档字符串（docstring）
- 复杂逻辑需要注释说明
- 使用中文注释（考虑国际化可中英双语）

```python
def on_bar(self, data: pd.DataFrame, index: int) -> dict:
    """
    每个 K 线周期调用一次，生成交易信号
    
    参数:
        data: 包含历史 OHLCV 数据的 DataFrame
        index: 当前 K 线的索引位置
    
    返回:
        dict: 交易指令，包含 action、price、shares
    
    交易指令格式:
        - 买入：{'action': 'buy', 'price': 100.5, 'shares': 1000}
        - 卖出：{'action': 'sell', 'price': 102.3, 'shares': 1000}
        - 持有：{'action': 'hold'}
    """
    pass
```

---

## 提交流程

### 1. 修改代码

```bash
# 编辑代码
code src/strategy/builder.py

# 查看修改
git status
git diff
```

### 2. 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_strategy.py -v

# 查看测试覆盖率
python -m pytest tests/ --cov=src --cov-report=html
```

### 3. 提交更改

```bash
# 添加修改的文件
git add src/strategy/builder.py

# 提交（使用规范的提交信息）
git commit -m "feat: 添加 RSI 指标支持

- 实现 RSI 计算函数
- 在策略中集成 RSI 指标
- 添加相关测试用例

Closes #123"
```

### 4. 推送分支

```bash
# 推送到你的 Fork
git push origin feature/your-feature-name
```

### 5. 创建 Pull Request

1. 访问你的 Fork 页面
2. 点击 "Compare & pull request"
3. 填写 PR 描述：
   - 说明修改内容
   - 关联 Issue（如 Closes #123）
   - 添加截图或示例（如适用）
4. 提交 PR

### 6. Code Review

- 等待维护者 Review
- 根据反馈修改代码
- 通过审核后合并

---

## 问题报告

### Bug 报告模板

```markdown
### 问题描述
简要描述遇到的问题

### 复现步骤
1. 步骤 1
2. 步骤 2
3. 步骤 3

### 预期行为
应该发生什么

### 实际行为
实际发生了什么

### 环境信息
- Python 版本：3.9.7
- 操作系统：Ubuntu 20.04
- OpenFinAgent 版本：0.1.0

### 错误信息
```
Traceback (most recent call last):
  ...
```

### 截图
（如有）
```

### 提交 Bug

1. 访问 [Issues](https://github.com/your-org/tradeflow-ai/issues)
2. 点击 "New Issue"
3. 选择 "Bug Report" 模板
4. 填写详细信息
5. 提交

---

## 功能建议

### 功能建议模板

```markdown
### 功能描述
简要描述你建议的功能

### 使用场景
为什么需要这个功能？解决什么问题？

### 实现思路
（可选）你建议如何实现这个功能

### 替代方案
（可选）是否考虑过其他解决方案

### 额外信息
任何相关的截图、示例代码等
```

### 提交建议

1. 访问 [Issues](https://github.com/your-org/tradeflow-ai/issues)
2. 点击 "New Issue"
3. 选择 "Feature Request" 模板
4. 填写详细信息
5. 提交

---

## 文档贡献

### 文档规范

- 使用 Markdown 格式
- 标题层级清晰（# → ## → ###）
- 代码块标注语言类型
- 图片添加说明文字

### 修改文档

```bash
# 修改文档
code docs/getting_started.md

# 预览效果（本地）
# 使用 VS Code Markdown Preview 或其他工具

# 提交
git add docs/
git commit -m "docs: 完善快速入门指南

- 补充安装步骤说明
- 添加常见问题解答
- 修正错别字"
git push origin main
```

### 添加教程

1. 在 `docs/tutorials/` 创建新文件
2. 遵循现有教程格式
3. 包含完整代码示例
4. 添加练习任务
5. 提交 PR

---

## 测试要求

### 编写测试

```python
# tests/test_strategy.py
import unittest
from tradeflow.strategy import MACrossStrategy


class TestMACrossStrategy(unittest.TestCase):
    
    def setUp(self):
        self.strategy = MACrossStrategy(
            short_window=5,
            long_window=20,
            initial_capital=100000
        )
    
    def test_initial_state(self):
        """测试初始状态"""
        self.assertEqual(self.strategy.short_window, 5)
        self.assertEqual(self.strategy.long_window, 20)
        self.assertEqual(self.strategy.initial_capital, 100000)
    
    def test_on_bar_insufficient_data(self):
        """测试数据不足时的行为"""
        # 准备测试数据
        import pandas as pd
        data = pd.DataFrame({
            'close': [100] * 10
        })
        
        # 数据不足，应该返回 hold
        signal = self.strategy.on_bar(data, 5)
        self.assertEqual(signal['action'], 'hold')


if __name__ == '__main__':
    unittest.main()
```

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试文件
python -m pytest tests/test_strategy.py -v

# 运行特定测试用例
python -m pytest tests/test_strategy.py::TestMACrossStrategy::test_initial_state -v

# 查看覆盖率
python -m pytest tests/ --cov=src --cov-report=term-missing
```

### 测试覆盖率

目标：核心模块覆盖率 > 80%

```bash
# 生成 HTML 报告
python -m pytest tests/ --cov=src --cov-report=html

# 在浏览器打开
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov\index.html  # Windows
```

---

## 常见问题

### Q: 我的 PR 多久会被审核？

A: 通常在 1-7 天内。如果超过一周没有回应，可以 @ 维护者。

### Q: 如何保持 Fork 与上游同步？

A: 

```bash
# 获取上游最新代码
git fetch upstream

# 合并到 main 分支
git checkout main
git merge upstream/main

# 推送到你的 Fork
git push origin main
```

### Q: 可以同时提交多个功能吗？

A: 建议一个 PR 只做一件事，这样更容易审核和合并。

### Q: 代码风格检查不通过怎么办？

A: 

```bash
# 自动格式化
black src/ tests/

# 手动修复 flake8 警告
flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
```

### Q: 如何添加新的数据源？

A: 

1. 在 `src/backtest/engine.py` 添加数据加载函数
2. 编写测试用例
3. 更新文档说明使用方法
4. 提交 PR

### Q: 可以添加付费功能吗？

A: 欢迎提议！请先在 Issue 中讨论，确保符合项目定位。

---

## 贡献者权益

- 🏆 名字出现在 README 贡献者列表
- 🎖️ 贡献突出可成为项目维护者
- 📬 优先获得项目更新通知
- 🎁 不定期收到项目周边礼品

---

## 贡献者列表

感谢所有为 OpenFinAgent 做出贡献的开发者！

<!-- 使用 all-contributors 自动更新 -->
<!-- ALL-CONTRIBUTORS-LIST:START -->
<!-- 这里会由工具自动插入贡献者列表 -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

---

## 许可证

提交代码即表示你同意将代码以 MIT 许可证发布。

---

## 需要帮助？

- 💬 在 [Discussions](https://github.com/your-org/tradeflow-ai/discussions) 提问
- 📧 发送邮件至 contributors@tradeflow.ai
- 🐦 在 Twitter 联系我们

---

<div align="center">

**再次感谢你的贡献！** 🚀

[开始贡献](#贡献方式) · [查看 Issue](https://github.com/your-org/tradeflow-ai/issues) · [加入讨论](https://github.com/your-org/tradeflow-ai/discussions)

</div>
