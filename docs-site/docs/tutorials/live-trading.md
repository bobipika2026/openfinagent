# 实盘部署

本教程将指导你将策略从回测部署到实盘交易。

## 🎯 学习目标

- 理解实盘交易流程
- 配置交易账户
- 部署策略到生产环境
- 监控和管理实盘策略

## ⚠️ 风险提示

> **重要**: 实盘交易存在真实资金风险。在投入真金白银之前，请确保：
> 1. 策略经过充分回测
> 2. 进行了模拟交易验证
> 3. 投入资金在可承受范围内
> 4. 设置了严格的风控措施

## 📋 部署流程

```mermaid
graph LR
    A[策略开发] --> B[回测验证]
    B --> C[模拟交易]
    C --> D[小资金实盘]
    D --> E[逐步加仓]
    E --> F[正式运行]
```

## 🔧 账户配置

### 选择券商

```python
# 支持的券商
SUPPORTED_BROKERS = [
    'alpaca',      # 美股
    'ibkr',        # 盈透证券
    'binance',     # 币安
    'ftx'          # FTX
]
```

### 配置 API

```bash
# 创建配置文件
cp .env.example .env

# 编辑配置
vim .env
```

```ini
# .env 配置文件

# 券商配置
BROKER=alpaca
ALPACA_API_KEY=your_api_key
ALPACA_API_SECRET=your_api_secret

# 交易模式
PAPER_TRADING=false  # 实盘设为 false

# 风控配置
MAX_POSITION=10000
MAX_DAILY_LOSS=1000
MAX_DRAWDOWN=0.1

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/trading.log
```

## 🚀 部署策略

### 创建交易脚本

```python
# trading_bot.py
from openfinagent import Strategy, TradingBot, Config
from my_strategy import MyStrategy

# 加载配置
config = Config.from_env()

# 创建策略
strategy = MyStrategy(
    short_window=5,
    long_window=20
)

# 创建交易机器人
bot = TradingBot(
    strategy=strategy,
    config=config,
    symbol='AAPL',
    timeframe='1d'
)

# 运行
if __name__ == '__main__':
    bot.run()
```

### 运行模式

```bash
# 模拟交易
python trading_bot.py --paper

# 实盘交易
python trading_bot.py --live

# 后台运行
nohup python trading_bot.py --live &

# 使用 systemd 管理
sudo systemctl start openfinagent
```

## 📊 监控系统

### 实时状态

```python
# status.py
from openfinagent import Monitor

monitor = Monitor()

# 查看状态
print(monitor.get_status())
print(monitor.get_position())
print(monitor.get_pnl())
print(monitor.get_today_trades())
```

### 告警配置

```yaml
# alerts.yaml
alerts:
  - type: email
    trigger: daily_loss > 500
    recipient: your@email.com
  
  - type: sms
    trigger: drawdown > 0.1
    phone: +1234567890
  
  - type: webhook
    trigger: order_filled
    url: https://your-webhook.com
```

### 日志查看

```bash
# 实时查看日志
tail -f logs/trading.log

# 搜索错误
grep ERROR logs/trading.log

# 查看今日交易
grep "ORDER_FILLED" logs/trading_$(date +%Y%m%d).log
```

## 🔒 风控措施

### 仓位限制

```python
# 最大仓位
MAX_POSITION_VALUE = 10000

# 单品种限制
MAX_POSITION_PER_SYMBOL = 5000

# 总仓位限制
MAX_TOTAL_POSITION = 50000
```

### 止损规则

```python
# 单笔止损
STOP_LOSS_PER_TRADE = 0.05

# 单日止损
DAILY_LOSS_LIMIT = 1000

# 总回撤限制
MAX_DRAWDOWN = 0.1
```

### 紧急停止

```python
# 紧急平仓
def emergency_stop():
    bot.close_all_positions()
    bot.stop()

# 快捷键
# Ctrl+C 触发紧急停止
```

## 📈 性能跟踪

### 日报

```python
# daily_report.py
from openfinagent import ReportGenerator

report = ReportGenerator()
daily_report = report.generate_daily_report()

print(f"今日收益：{daily_report.pnl}")
print(f"今日交易：{daily_report.trade_count}")
print(f"当前仓位：{daily_report.position}")
```

### 周报/月报

```python
# 周度报告
weekly_report = report.generate_weekly_report()

# 月度报告
monthly_report = report.generate_monthly_report()
```

### 绩效分析

```python
# 绩效分析
analysis = report.analyze_performance(days=30)

print(f"30 日收益率：{analysis.return_30d:.2%}")
print(f"30 日夏普：{analysis.sharpe_30d:.2f}")
print(f"30 日最大回撤：{analysis.max_dd_30d:.2%}")
```

## 🐛 故障处理

### 常见问题

```bash
# 1. 连接失败
# 检查网络和 API 密钥
ping api.alpaca.markets
curl -H "APCA-API-KEY-ID: xxx" https://api.alpaca.markets/v2/account

# 2. 订单失败
# 检查账户状态和资金
python status.py

# 3. 数据异常
# 检查数据源
python scripts/check_data.py
```

### 恢复流程

```python
# 重启策略
def restart_strategy():
    bot.stop()
    time.sleep(5)
    bot.start()

# 恢复仓位
def recover_position():
    # 从数据库恢复状态
    bot.load_state()
```

## 📚 最佳实践

1. **从小开始**: 先用小资金测试
2. **逐步加仓**: 确认稳定后增加资金
3. **持续监控**: 每天检查策略状态
4. **定期复盘**: 每周/月分析绩效
5. **及时止损**: 触及止损线立即停止

## 📚 下一步

- [FAQ](../faq.md) - 常见问题解答
- [高级主题](../advanced/) - 深入学习

## ✅ 检查清单

部署前确认：

- [ ] 策略经过充分回测
- [ ] 模拟交易验证通过
- [ ] 风控参数设置合理
- [ ] 监控系统配置完成
- [ ] 紧急停止机制就绪
- [ ] 日志记录正常
- [ ] 告警通知测试通过

---

_谨慎交易，祝你好运！🍀_
