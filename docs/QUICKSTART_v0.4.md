# OpenFinAgent v0.4.0 快速入门

**版本**: v0.4.0  
**更新日期**: 2026-03-06

---

## 🚀 快速开始

### 1. 安装

```bash
# 克隆项目
cd /root/.openclaw/workspace/projects/tradeflow-ai

# 安装依赖
pip install -e .

# 安装可选依赖
pip install yfinance tushare akshare
```

### 2. 配置环境变量

```bash
# Tushare API Key (可选)
export TUSHARE_TOKEN="your_tushare_token"

# Alpha Vantage API Key (可选)
export ALPHA_VANTAGE_API_KEY="your_api_key"
```

---

## 📚 核心功能示例

### 1. 用户系统

```python
from openfinagent.user import AuthService, PermissionManager

# 初始化认证服务
auth = AuthService(secret_key="your_secret_key")

# 注册新用户
user, verification_token = auth.register(
    email="trader@example.com",
    password="secure_password123",
    username="quant_trader"
)

# 验证邮箱
auth.verify_email(verification_token)

# 登录
jwt_token = auth.login(
    email="trader@example.com",
    password="secure_password123"
)

# 验证 Token 获取用户信息
user = auth.verify_token(jwt_token)
print(f"欢迎，{user.username}!")

# 权限管理
perm_manager = PermissionManager(auth)

# 检查权限
if perm_manager.has_permission(user, 'strategy:write'):
    print("可以创建策略")
```

---

### 2. 多数据源

```python
from openfinagent.data import DataManager
from datetime import datetime, timedelta

# 配置数据源
config = {
    'primary': 'akshare',
    'fallback_order': ['akshare', 'yfinance', 'mock'],
    'sources': {
        'tushare': {'api_key': 'your_token'},
        'alphavantage': {'api_key': 'your_key'}
    },
    'enable_cache': True,
    'cache_ttl': 3600
}

# 创建管理器
manager = DataManager(config)

# 获取 A 股数据
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

data = manager.get_data(
    symbol='000001.SZ',
    start_date=start_date,
    end_date=end_date
)

print(f"获取到 {len(data)} 行数据")
print(data.head())

# 获取实时行情
realtime = manager.get_realtime('AAPL')
print(f"AAPL 当前价格：{realtime.get('price')}")

# 检查数据质量
reports = manager.check_quality('000001.SZ')
for report in reports:
    print(f"{report.source}: {report.quality}")
```

---

### 3. 模拟盘交易

```python
from openfinagent.paper_trading import (
    PaperTradingEngine,
    OrderSide, OrderType, OrderStatus
)

# 创建模拟盘引擎
engine = PaperTradingEngine(
    initial_cash=1000000.0,  # 100 万初始资金
    commission_rate=0.0003,   # 万分之三手续费
    slippage_rate=0.001       # 0.1% 滑点
)

# 启动模拟盘
engine.start()

# 提交市价买单
order = engine.submit_order(
    symbol='000001.SZ',
    side=OrderSide.BUY,
    quantity=1000,
    order_type=OrderType.MARKET
)

print(f"订单状态：{order.status.value}")
print(f"成交价格：{order.filled_price}")

# 查询持仓
position = engine.get_position('000001.SZ')
if position:
    print(f"持仓数量：{position.quantity}")
    print(f"平均成本：{position.avg_price}")
    print(f"浮动盈亏：{position.unrealized_pnl}")

# 更新价格 (模拟实时行情)
engine.update_prices({'000001.SZ': 15.5})

# 提交卖出订单
sell_order = engine.submit_order(
    symbol='000001.SZ',
    side=OrderSide.SELL,
    quantity=500,
    order_type=OrderType.MARKET
)

# 获取组合总价值
total_value = engine.get_portfolio_value()
return_rate = engine.get_return_rate()

print(f"组合总价值：{total_value:,.2f}")
print(f"收益率：{return_rate*100:.2f}%")

# 获取交易记录
trades = engine.get_trades()
for trade in trades:
    print(f"{trade.timestamp}: {trade.side.value} {trade.quantity} @ {trade.price}")

# 获取摘要
summary = engine.get_summary()
print(summary)

# 停止模拟盘
engine.stop()
```

---

### 4. 策略市场

```python
from openfinagent.market import MarketService, StrategyCategory

# 创建市场服务
market = MarketService()

# 上传策略
strategy = market.upload_strategy(
    name="双均线策略",
    code="""
class DualMAStrategy:
    def __init__(self, short_period=10, long_period=30):
        self.short_period = short_period
        self.long_period = long_period
    
    def generate_signals(self, data):
        # 生成交易信号
        pass
""",
    author_id="user123",
    author_name="张三",
    description="简单的双均线交叉策略，短期均线上穿长期均线时买入",
    category="cta",
    tags=["均线", "趋势跟踪", "CTA"],
    config={
        "short_period": 10,
        "long_period": 30
    },
    backtest_report={
        "return_rate": 0.15,
        "sharpe_ratio": 1.5,
        "max_drawdown": 0.08
    }
)

print(f"策略上传成功，ID: {strategy.id}")

# 发布策略
market.publish_strategy(strategy.id, author_id="user123")

# 浏览策略
strategies, total = market.list_strategies(
    category="cta",
    page=1,
    page_size=10
)

print(f"共 {total} 个 CTA 策略")
for s in strategies:
    print(f"- {s.name} by {s.author_name} ⭐{s.stars}")

# 搜索策略
strategies, total = market.list_strategies(search="均线")
print(f"找到 {total} 个相关策略")

# 获取策略详情
strategy = market.get_strategy(strategy_id)
print(f"浏览量：{strategy.views}")

# 下载策略
package = market.download_strategy(
    strategy_id=strategy.id,
    user_id="user456"
)

print(f"策略包包含：{list(package.code_files.keys())}")

# 收藏策略
market.star_strategy(strategy.id, user_id="user456")
print(f"策略收藏数：{strategy.stars}")

# 添加评论
comment = market.add_comment(
    strategy_id=strategy.id,
    user_id="user456",
    user_name="李四",
    content="很好的策略，回测表现不错！"
)

# 回复评论
reply = market.add_comment(
    strategy_id=strategy.id,
    user_id="user123",
    user_name="张三",
    content="谢谢支持！",
    parent_id=comment.id
)

# 获取统计信息
stats = market.get_statistics()
print(f"总策略数：{stats['total_strategies']}")
print(f"总下载量：{stats['total_downloads']}")
```

---

## 🔧 高级用法

### 1. 自定义数据源配置

```python
# 仅使用特定数据源
config = {
    'primary': 'yfinance',
    'fallback_order': ['yfinance', 'mock'],
    'enable_cache': True,
    'cache_ttl': 1800  # 30 分钟
}

manager = DataManager(config)
```

### 2. 限价单交易

```python
# 提交限价单
order = engine.submit_order(
    symbol='AAPL',
    side=OrderSide.BUY,
    quantity=100,
    order_type=OrderType.LIMIT,
    price=150.0  # 限价 150 美元
)

# 取消订单
if order.status == OrderStatus.PENDING:
    engine.cancel_order(order.id)
```

### 3. 权限控制

```python
from openfinagent.user import Permission, PermissionDenied

# 创建装饰器
@perm_manager.require_permission(Permission.STRATEGY_PUBLISH)
def publish_strategy(user, strategy_id):
    market.publish_strategy(strategy_id, user.id)

# 使用
try:
    publish_strategy(current_user, strategy_id)
except PermissionDenied as e:
    print(f"权限不足：{e}")
```

---

## 🧪 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_user.py -v
pytest tests/test_paper_trading.py -v
pytest tests/test_market.py -v
pytest tests/test_data_manager.py -v

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html
```

---

## 📖 更多文档

- [P0 开发报告](./P0_DEVELOPMENT_REPORT.md)
- [API 文档](./api_reference.md) - 待完善
- [示例代码](../examples/) - 待添加

---

## ❓ 常见问题

### 1. 如何获取 Tushare API Key?

访问 [tushare.pro](https://tushare.pro) 注册并获取免费 API Token。

### 2. 如何获取 Alpha Vantage API Key?

访问 [alphavantage.co](https://www.alphavantage.co/support/#api-key) 免费申请。

### 3. 模拟盘和回测有什么区别？

- **回测**: 使用历史数据，快速验证策略
- **模拟盘**: 使用实时数据，模拟真实交易环境

### 4. 如何上传自己的策略？

使用 `MarketService.upload_strategy()` 方法，详见上方示例。

---

## 🎯 下一步

完成 P0 功能学习后，可以继续:

1. 查看 P1 功能规划 (机器学习增强、风控增强)
2. 贡献代码到 GitHub
3. 分享你的策略到策略市场

---

**Happy Trading! 📈**
