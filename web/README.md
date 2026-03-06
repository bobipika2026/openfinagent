# OpenFinAgent Web UI

AI 驱动的量化交易平台 Web 界面

## 📋 项目简介

OpenFinAgent Web UI 是一个基于 Streamlit 构建的量化交易平台前端界面，提供策略创建、回测分析、策略对比等功能。

### ✨ 主要功能

- **🏠 首页** - 项目介绍、快速入口、示例策略展示
- **✨ 创建策略** - 支持自然语言创建和参数配置两种方式
- **📈 回测分析** - 选择股票和时间范围，运行策略回测，查看详细指标和图表
- **⚖️ 策略对比** - 同时对比多个策略表现，找到最优方案

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /root/.openclaw/workspace/projects/tradeflow-ai/web

# 安装 Python 依赖
pip install -r requirements.txt
```

### 2. 运行应用

```bash
# 方式 1：直接运行
streamlit run app.py

# 方式 2：指定端口和地址
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### 3. 访问界面

打开浏览器访问：`http://localhost:8501`

## 📁 项目结构

```
web/
├── app.py                 # 主应用入口
├── requirements.txt       # Python 依赖
├── README.md             # 使用说明
└── pages/
    ├── home.py           # 首页
    ├── create.py         # 策略创建页面
    ├── backtest.py       # 回测分析页面
    └── compare.py        # 策略对比页面
```

## 🎯 使用指南

### 创建策略

**方式 1：自然语言创建**

在创建策略页面，输入你的策略想法，例如：

```
当 5 日均线上穿 20 日均线时买入
当 5 日均线下穿 20 日均线时卖出
初始资金 10 万元
```

AI 会自动解析并创建策略。

**方式 2：参数配置**

选择策略类型（均线交叉、动量、RSI、MACD、布林带等），然后配置具体参数。

### 运行回测

1. 确保已创建策略（或从示例策略中选择）
2. 进入回测分析页面
3. 选择股票代码（如 000001）
4. 设置时间范围
5. 配置手续费率和滑点（可选）
6. 点击"运行回测"

### 策略对比

1. 进入策略对比页面
2. 选择股票和时间范围
3. 选择要对比的策略（2-5 个）
4. 点击"运行对比"
5. 查看对比图表和指标表格

## 📊 支持策略类型

| 策略类型 | 说明 | 关键参数 |
|---------|------|---------|
| 均线交叉 (ma_cross) | 短期均线上穿长期均线买入 | short_window, long_window |
| 动量策略 (momentum) | 追涨杀跌 | lookback_period, threshold |
| RSI 策略 (rsi) | 超买超卖反转 | period, oversold, overbought |
| MACD 策略 (macd) | MACD 金叉死叉 | fast_period, slow_period, signal_period |
| 布林带策略 (bollinger) | 价格突破布林带 | window, std_dev |
| 双均线 + 成交量 (dual_ma_volume) | 均线交叉 + 成交量确认 | short_window, long_window, volume_ma_period, volume_multiplier |

## 📈 回测指标

### 收益指标
- 总收益率
- 年化收益率
- 绝对收益

### 风险指标
- 最大回撤
- 夏普比率
- 索提诺比率
- 年化波动率

### 交易统计
- 交易次数
- 胜率
- 盈亏比
- 平均持仓天数

## 🔧 配置选项

### 数据源

- **akshare** - A 股数据（默认）
- **mock** - 模拟数据（用于测试）

### 交易参数

- **手续费率** - 默认万分之三（0.0003）
- **滑点** - 默认 0.1%（0.001）

## 🐛 常见问题

### 1. 数据加载失败

**问题**：回测时提示数据加载失败

**解决**：
- 检查股票代码是否正确（6 位数字）
- 检查时间范围是否合理
- 切换到"模拟数据"模式测试

### 2. matplotlib 中文显示问题

**问题**：图表中文显示为方块

**解决**：
```bash
# 安装中文字体
sudo apt-get install fonts-wqy-zenhei  # Ubuntu/Debian
# 或
sudo yum install wqy-zenhei-fonts      # CentOS/RHEL
```

### 3. Streamlit 端口被占用

**问题**：端口 8501 已被占用

**解决**：
```bash
# 使用其他端口
streamlit run app.py --server.port 8502
```

## 📝 技术栈

- **前端框架**: Streamlit
- **图表库**: Plotly, Matplotlib
- **数据处理**: Pandas, NumPy
- **数据源**: Akshare (A 股), Yahoo Finance (美股)

## 🔗 相关链接

- **GitHub**: [bobipika2026/openfinagent](https://github.com/bobipika2026/openfinagent)
- **Streamlit 文档**: [docs.streamlit.io](https://docs.streamlit.io)
- **Akshare 文档**: [akshare.akfamily.xyz](https://akshare.akfamily.xyz)

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

---

**开发时间**: 2026-03-06  
**版本**: 0.1.0
