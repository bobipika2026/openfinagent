# 快速开始

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

### 4. 环境配置

```bash
# 复制环境配置模板
cp .env.example .env

# 编辑配置文件
vim .env  # 或使用你喜欢的编辑器
```

### 5. 配置文件说明

```ini
# .env 配置文件示例

# API 密钥配置
ALPACA_API_KEY=your_api_key
ALPACA_API_SECRET=your_api_secret

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

## ✅ 验证安装

### 运行测试

```bash
# 运行单元测试
pytest tests/

# 运行示例脚本
python examples/hello_world.py
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

## 📁 项目结构

```
openfinagent/
├── openfinagent/          # 核心代码
│   ├── strategy/         # 策略模块
│   ├── backtest/         # 回测模块
│   ├── trading/          # 交易模块
│   ├── data/             # 数据模块
│   └── risk/             # 风控模块
├── strategies/            # 内置策略
├── examples/              # 示例代码
├── tests/                 # 测试文件
├── data/                  # 数据文件
├── logs/                  # 日志文件
├── docs/                  # 文档
├── requirements.txt       # 依赖列表
└── README.md              # 项目说明
```

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

## 📚 下一步

- [策略文档](strategies/) - 了解 6 种内置策略
- [API 参考](api/) - 查看完整 API 文档
- [教程](tutorials/) - 跟随实战教程

## 🆘 获取帮助

遇到问题？

1. 查看 [FAQ](faq.md)
2. 搜索 [GitHub Issues](https://github.com/bobipika2026/openfinagent/issues)
3. 提交新的 [Issue](https://github.com/bobipika2026/openfinagent/issues/new)

---

_祝你交易顺利！📈_
