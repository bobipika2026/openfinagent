# TradeFlow AI 常见问题 (FAQ)

本文档收集了用户常见问题和解答。

---

## 📖 目录

- [安装与配置](#安装与配置)
- [策略创建](#策略创建)
- [回测相关](#回测相关)
- [数据问题](#数据问题)
- [性能优化](#性能优化)
- [错误排查](#错误排查)
- [其他问题](#其他问题)

---

## 安装与配置

### Q1: 安装时出现依赖冲突怎么办？

**A**: 尝试以下步骤：

```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 2. 升级 pip
pip install --upgrade pip

# 3. 重新安装
pip install -r requirements.txt
```

如果仍有问题，可以尝试逐个安装依赖：

```bash
pip install pandas numpy matplotlib jieba tqdm
```

### Q2: 支持哪些 Python 版本？

**A**: TradeFlow AI 支持 Python 3.9 及以上版本。

```bash
# 检查 Python 版本
python --version

# 推荐版本：Python 3.9 - 3.11
```

### Q3: 如何在 Windows 上安装？

**A**: Windows 用户请按以下步骤：

```bash
# 1. 安装 Python（从 python.org 下载）
# 2. 安装 Git（可选，用于克隆项目）
# 3. 打开命令提示符或 PowerShell

git clone https://github.com/your-org/tradeflow-ai.git
cd tradeflow-ai
pip install -r requirements.txt

# 验证安装
python -c "from tradeflow import StrategyBuilder; print('OK')"
```

### Q4: 需要 API 密钥吗？

**A**: 
- **不需要** - 使用模拟数据 (`source='mock'`) 可以立即开始
- **需要** - 如果要获取真实市场数据，需要相应数据源的 API 密钥

---

## 策略创建

### Q5: 自然语言描述不准确怎么办？

**A**: 有三种解决方案：

**方案 1**: 使用更简洁的描述
```python
# ❌ 过于复杂
strategy = StrategyBuilder.from_natural_language("""
当短期均线上穿长期均线并且成交量放大的时候买入，
但是如果 RSI 太高就不要买...
""")

# ✅ 简洁清晰
strategy = StrategyBuilder.from_natural_language("""
当 5 日均线上穿 20 日均线时买入
当 5 日均线下穿 20 日均线时卖出
""")
```

**方案 2**: 使用参数化方式
```python
strategy = StrategyBuilder.create(
    'ma_cross',
    short_window=5,
    long_window=20,
    initial_capital=100000
)
```

**方案 3**: 自定义策略类
```python
from tradeflow.strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def on_bar(self, data, index):
        # 你的交易逻辑
        return {'action': 'buy', 'price': price, 'shares': 100}
```

### Q6: 支持哪些策略类型？

**A**: 当前内置策略：

| 策略类型 | 说明 | 语法示例 |
|---------|------|---------|
| `ma_cross` | 均线交叉 | `当 5 日均线上穿 20 日均线时买入` |
| `momentum` | 动量策略 | `看 20 天收益率，超过 5% 买入` |

更多策略类型将在后续版本中添加。

### Q7: 如何查看策略参数？

**A**: 使用以下方法：

```python
# 查看策略参数
print(strategy.get_params())

# 查看策略摘要
print(strategy.summary())

# 查看策略名称
print(strategy.name)
```

### Q8: 可以组合多个条件吗？

**A**: 可以，使用"且"、"或"连接：

```python
strategy = StrategyBuilder.from_natural_language("""
当 5 日均线上穿 20 日均线 且 RSI < 30 时买入
当 5 日均线下穿 20 日均线 或 RSI > 70 时卖出
""")
```

---

## 回测相关

### Q9: 回测结果不准确怎么办？

**A**: 检查以下设置：

```python
# 1. 手续费设置（A 股约万三）
engine = BacktestEngine(commission_rate=0.0003)

# 2. 滑点设置（默认 0.1%）
engine = BacktestEngine(slippage=0.001)

# 3. 数据质量
data = load_data("600519.SH", "2023-01-01", "2023-12-31", source='akshare')

# 4. 回测周期（至少 1 年）
results = engine.run(strategy, data, "2023-01-01", "2023-12-31")
```

### Q10: 如何对比多个策略？

**A**: 使用 `run_multi()` 方法：

```python
strategies = [
    StrategyBuilder.create('ma_cross', short_window=5, long_window=20),
    StrategyBuilder.create('ma_cross', short_window=10, long_window=30),
    StrategyBuilder.create('momentum', lookback=20, threshold=0.05),
]

engine = BacktestEngine()
results = engine.run_multi(strategies, data)

# 对比结果
for name, result in results.items():
    print(f"{name}: 年化收益 {result.metrics['年化收益']:.2f}%")
```

### Q11: 回测需要多长时间？

**A**: 取决于：
- 数据量（年份长度）
- 策略复杂度
- 电脑性能

一般情况：
- 1 年数据，简单策略：1-5 秒
- 5 年数据，复杂策略：10-30 秒

### Q12: 如何保存回测结果？

**A**: 使用以下方法：

```python
# 保存交易记录到 CSV
results.to_csv('trades.csv')

# 保存为字典
data = results.to_dict()

# 保存图表
results.plot(save_path='backtest_result.png')
```

---

## 数据问题

### Q13: 如何获取真实股票数据？

**A**: TradeFlow AI 支持多种数据源：

```python
# A 股数据（AKShare - 免费）
data = load_data("600519.SH", "2023-01-01", "2023-12-31", source='akshare')

# 美股数据（Yahoo Finance - 免费）
data = load_data("AAPL", "2023-01-01", "2023-12-31", source='yfinance')

# 加密货币（Binance - 免费）
data = load_data("BTCUSDT", "2023-01-01", "2023-12-31", source='binance')

# 模拟数据（无需 API）
data = load_data("600519.SH", "2023-01-01", "2023-12-31", source='mock')
```

### Q14: AKShare 数据加载失败怎么办？

**A**: 

```bash
# 1. 确保安装 akshare
pip install akshare

# 2. 检查网络连接
ping www.akshare.org

# 3. 使用备用数据源
data = load_data("600519.SH", "2023-01-01", "2023-12-31", source='mock')
```

### Q15: 数据格式要求是什么？

**A**: 数据需要是 pandas DataFrame，包含以下列：

```python
import pandas as pd

data = pd.DataFrame({
    'open': [...],      # 开盘价
    'high': [...],      # 最高价
    'low': [...],       # 最低价
    'close': [...],     # 收盘价
    'volume': [...]     # 成交量
}, index=pd.date_range('2023-01-01', periods=252, freq='B'))
```

### Q16: 支持哪些市场？

**A**: 

| 市场 | 代码格式 | 数据源 |
|------|---------|--------|
| A 股 | `600519.SH` | AKShare |
| 美股 | `AAPL` | Yahoo Finance |
| 港股 | `0700.HK` | Yahoo Finance |
| 加密货币 | `BTCUSDT` | Binance |

---

## 性能优化

### Q17: 回测速度太慢怎么办？

**A**: 优化建议：

```python
# 1. 减少数据量（只回测必要的时间段）
data = load_data("600519.SH", "2023-01-01", "2023-06-30", source='akshare')

# 2. 关闭进度条
results = engine.run(strategy, data, show_progress=False)

# 3. 批量回测使用 run_multi
results = engine.run_multi(strategies, data)
```

### Q18: 内存占用过高怎么办？

**A**: 

```python
# 1. 分批次回测
for year in range(2020, 2024):
    data = load_data("600519.SH", f"{year}-01-01", f"{year}-12-31")
    results = engine.run(strategy, data)
    
# 2. 及时释放内存
del data
import gc
gc.collect()
```

### Q19: 如何优化策略性能？

**A**: 

1. **避免过度交易** - 添加过滤条件减少交易次数
2. **使用合适周期** - 过短的均线周期会导致频繁交易
3. **合理设置仓位** - 避免满仓操作

---

## 错误排查

### Q20: 出现 "ModuleNotFoundError" 怎么办？

**A**: 

```bash
# 确保在项目根目录
cd /path/to/tradeflow-ai

# 添加 src 到 Python 路径
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# 或者在代码中添加
import sys
sys.path.insert(0, 'src')

from tradeflow import StrategyBuilder
```

### Q21: 出现 "KeyError: 'close'" 怎么办？

**A**: 数据格式不正确：

```python
# 检查数据列
print(data.columns)

# 确保包含必要的列
required_columns = ['open', 'high', 'low', 'close', 'volume']
for col in required_columns:
    if col not in data.columns:
        print(f"缺少列：{col}")
```

### Q22: 绘图失败怎么办？

**A**: 

```bash
# 1. 确保安装 matplotlib
pip install matplotlib

# 2. 检查显示环境（服务器可能需要）
export MPLBACKEND=Agg

# 3. 保存为文件而非显示
results.plot(save_path='result.png')
```

### Q23: 策略解析失败怎么办？

**A**: 

```python
# 1. 简化策略描述
strategy = StrategyBuilder.from_natural_language("当 5 日均线上穿 20 日均线时买入")

# 2. 使用参数化方式
strategy = StrategyBuilder.create('ma_cross', short_window=5, long_window=20)

# 3. 查看错误信息
try:
    strategy = StrategyBuilder.from_natural_language(description)
except Exception as e:
    print(f"解析失败：{e}")
```

---

## 其他问题

### Q24: 有图形界面吗？

**A**: 当前版本为命令行工具，Web 界面正在开发中。

### Q25: 支持实时交易吗？

**A**: 当前版本仅支持回测，实盘交易功能计划中。

### Q26: 如何更新到最新版本？

**A**: 

```bash
# 如果使用 git 克隆
git pull origin main

# 重新安装依赖
pip install -r requirements.txt --upgrade
```

### Q27: 如何报告 Bug？

**A**: 

1. 访问 [GitHub Issues](https://github.com/your-org/tradeflow-ai/issues)
2. 点击 "New Issue"
3. 提供以下信息：
   - 问题描述
   - 复现步骤
   - 错误信息
   - 系统环境（Python 版本、操作系统）

### Q28: 如何贡献代码？

**A**: 

1. Fork 项目
2. 创建分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

详见 [CONTRIBUTING.md](../CONTRIBUTING.md)

### Q29: 商业使用需要授权吗？

**A**: TradeFlow AI 使用 MIT 许可证，允许免费商业使用。

### Q30: 有学习资源推荐吗？

**A**: 

- 📖 [快速入门](getting_started.md) - 5 分钟上手
- 🎓 [教程集合](tutorials/) - 系列教程
- 📝 [策略语法](strategy-syntax.md) - 语法参考
- 🔧 [API 参考](api_reference.md) - 接口文档

---

## 仍未解决？

如果以上 FAQ 没有解决你的问题：

- 💬 加入社区讨论
- 📧 发送邮件至 support@tradeflow.ai
- 🐛 提交 GitHub Issue

---

**Happy Trading!** 📈
