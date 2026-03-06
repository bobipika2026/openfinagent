# 快速开始

> 🎉 v0.3.0 更新：新增 Binance 数据源、Tushare 分钟线、遗传算法优化器  
> [查看新特性 →](v0.3-whats-new.md)

---

本指南将帮助你快速搭建 OpenFinAgent 开发环境并开始使用。

## 📋 前置要求

### 系统要求

- **操作系统**: Linux / macOS / Windows 10+
- **Python**: 3.9 或更高版本
- **内存**: 至少 4GB RAM（推荐 8GB+）
- **磁盘空间**: 至少 2GB 可用空间

### 依赖软件

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip git curl

# macOS
brew install python3 git curl

# Windows
# 下载安装 Python 3.9+ 和 Git
```

---

## 🔧 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/bobipika2026/openfinagent.git
cd openfinagent
```

### 2. 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 安装依赖

```bash
# 安装核心依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install -r requirements-dev.txt

# 安装文档依赖（可选）
pip install -r docs-site/requirements.txt
```

### 4. 可选依赖（v0.3.0 新增）

```bash
# Binance 加密货币数据
pip install requests

# Tushare A 股分钟线
pip install tushare

# 交互式图表和热力图
pip install plotly matplotlib

# 完整安装（推荐）
pip install requests tushare plotly matplotlib
```

### 5. 环境配置

```bash
# 复制环境配置模板
cp .env.example .env

# 编辑配置文件
vim .env  # 或使用你喜欢的编辑器
```

### 6. 配置文件说明

```ini
# .env 配置文件示例

# API 密钥配置
ALPACA_API_KEY=your_api_key
ALPACA_API_SECRET=your_api_secret

# Tushare Token（v0.3.0 新增）
TUSHARE_TOKEN=your_tushare_token

# 数据库配置
DATABASE_URL=sqlite:///openfinagent.db

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/openfinagent.log

# 交易配置
PAPER_TRADING=true  # 模拟交易模式
MAX_POSITION_SIZE=10000  # 最大仓位
STOP_LOSS_PERCENT=0.05  # 止损比例
```

---

## ✅ 验证安装

### 运行测试

```bash
# 运行单元测试
pytest tests/

# 运行示例脚本
python examples/hello_world.py

# 验证 v0.3.0 新功能
python verify_features.py
```

### 检查系统状态

```bash
# 检查 Python 版本
python --version  # 应 >= 3.9

# 检查依赖包
pip list | grep openfinagent

# 运行系统诊断
python scripts/diagnose.py
```

---

## 🎯 第一个策略

### 创建策略文件

创建 `my_first_strategy.py`:

```python
from openfinagent import Strategy, Signal, SignalType

class MyFirstStrategy(Strategy):
    """我的第一个交易策略"""
    
    def __init__(self, window: int = 20):
        super().__init__(name="MyFirstStrategy")
        self.window = window
    
    def on_bar(self, bar):
        """处理每个 K 线数据"""
        # 获取历史收盘价
        closes = self.get_closes(self.window + 1)
        
        if len(closes) < self.window + 1:
            return
        
        # 计算简单移动平均
        sma = sum(closes[-self.window:]) / self.window
        current_price = closes[-1]
        
        # 生成交易信号
        if current_price > sma * 1.02:
            self.emit_signal(Signal(SignalType.BUY, strength=0.8))
        elif current_price < sma * 0.98:
            self.emit_signal(Signal(SignalType.SELL, strength=0.8))
```

### 运行回测

```python
from openfinagent import Backtester
from my_first_strategy import MyFirstStrategy

# 创建策略
strategy = MyFirstStrategy(window=20)

# 创建回测器
backtester = Backtester(
    strategy=strategy,
    data_file='data/test_data.csv',
    initial_capital=100000,
    commission=0.001
)

# 运行回测
results = backtester.run()

# 输出结果
print(results.summary())
results.plot()
```

---

## 🚀 v0.3.0 快速示例

### 示例 1：使用 Binance 数据源

```python
from data.binance_source import BinanceDataSource
from backtest.engine import BacktestEngine
from strategy.dual_ma import DualMAStrategy

# 1. 获取 BTC/USDT 数据
source = BinanceDataSource()
data = source.get_klines('BTC/USDT', '1d', '2023-01-01', '2023-12-31')

# 2. 创建策略
strategy = DualMAStrategy(short_window=10, long_window=30, initial_capital=10000)

# 3. 运行回测
engine = BacktestEngine()
result = engine.run(strategy, data)

# 4. 查看结果
print(result.summary())
```

📖 **详细文档**: [Binance 数据源指南](guides/binance-data.md)

---

### 示例 2：使用 Tushare 分钟线

```python
from data.sources import TushareDataSource
from backtest.engine import BacktestEngine
from strategy.rsi_strategy import RSIStrategy

# 1. 获取 5 分钟线数据
source = TushareDataSource(freq='5m')
data = source.get_data('000001.SZ', '2024-01-01', '2024-01-31')

# 2. 创建 RSI 策略
strategy = RSIStrategy(
    rsi_period=14,
    oversold_threshold=30,
    overbought_threshold=70,
    initial_capital=100000
)

# 3. 运行回测
engine = BacktestEngine()
result = engine.run(strategy, data)

# 4. 查看结果
print(result.summary())
```

📖 **详细文档**: [Tushare 数据源指南](guides/tushare-data.md)

---

### 示例 3：遗传算法参数优化

```python
from optimization.genetic_optimizer import GeneticOptimizer, ParameterBound
from backtest.engine import BacktestEngine
from strategy.dual_ma import DualMAStrategy
from data.binance_source import BinanceDataSource

# 1. 获取数据
source = BinanceDataSource()
data = source.get_klines('BTC/USDT', '1d', '2023-01-01', '2023-12-31')

# 2. 定义参数范围
param_bounds = [
    ParameterBound('short_window', 5, 20, dtype='int'),
    ParameterBound('long_window', 20, 60, dtype='int'),
]

# 3. 创建优化器
optimizer = GeneticOptimizer(
    population_size=30,
    generations=50,
    optimization_metric='sharpe_ratio',
    n_jobs=-1  # 使用所有 CPU 核心
)

# 4. 执行优化
best = optimizer.optimize(
    strategy_class=DualMAStrategy,
    parameter_bounds=param_bounds,
    backtest_func=lambda s, d: BacktestEngine().run(s, d),
    data=data,
    initial_capital=10000
)

# 5. 使用最优参数回测
strategy = DualMAStrategy(**best.params, initial_capital=10000)
result = BacktestEngine().run(strategy, data)

print(f"最优参数：{best.params}")
print(f"夏普比率：{best.fitness:.2f}")
```

📖 **详细文档**: [优化器使用指南](guides/optimizer.md)

---

## 📁 项目结构

```
openfinagent/
├── openfinagent/          # 核心代码
│   ├── strategy/         # 策略模块
│   ├── backtest/         # 回测模块
│   ├── trading/          # 交易模块
│   ├── data/             # 数据模块
│   ├── optimization/     # 优化器模块 (v0.3.0 新增)
│   ├── visualization/    # 可视化模块 (v0.3.0 新增)
│   └── risk/             # 风控模块
├── strategies/            # 内置策略
├── examples/              # 示例代码
├── tests/                 # 测试文件
├── data/                  # 数据文件
├── logs/                  # 日志文件
├── docs/                  # 文档
├── blog/                  # 博客文章 (v0.3.0 新增)
├── requirements.txt       # 依赖列表
└── README.md              # 项目说明
```

---

## 🔍 常见问题

### 安装失败

```bash
# 清除 pip 缓存
pip cache purge

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 依赖冲突

```bash
# 升级 pip
pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

### 权限问题

```bash
# Linux/macOS 权限问题
chmod +x scripts/*.sh

# Windows 以管理员身份运行
```

### Tushare Token 配置

```bash
# 方式一：环境变量（推荐）
export TUSHARE_TOKEN='your_token_here'

# 方式二：代码中配置
from data.sources import TushareDataSource
source = TushareDataSource(token='your_token_here')

# 方式三：Token 管理器（加密存储）
from data.tushare_token_manager import TokenManager
manager = TokenManager()
manager.save_token('your_token_here')
token = manager.get_token()
```

---

## 📚 下一步

- 📢 [v0.3.0 新特性](v0.3-whats-new.md) - 了解最新版本功能
- 📖 [策略文档](strategies/) - 了解 6 种内置策略
- 📖 [使用指南](guides/binance-data.md) - Binance/Tushare 数据源教程
- 🔧 [API 参考](api/) - 查看完整 API 文档
- 🎓 [教程](tutorials/) - 跟随实战教程
- 📝 [更新日志](changelog.md) - 版本更新记录

---

## 🆘 获取帮助

遇到问题？

1. 查看 [FAQ](faq.md)
2. 搜索 [GitHub Issues](https://github.com/bobipika2026/openfinagent/issues)
3. 提交新的 [Issue](https://github.com/bobipika2026/openfinagent/issues/new)
4. 阅读 [博客文章](/blog/)

---

_祝你交易顺利！📈_

_最后更新：2026 年 3 月 6 日 | 当前版本：v0.3.0_
