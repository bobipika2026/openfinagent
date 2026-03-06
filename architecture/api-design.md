# OpenFinAgent API 设计

**版本**: v1.0  
**最后更新**: 2026-03-06

---

## 1. 设计原则

### 1.1 API 风格

- **Pythonic**: 符合 Python 编程习惯
- **链式调用**: 支持流畅的链式 API
- **类型安全**: 完整的类型注解
- **文档完善**: 每个函数都有 docstring

### 1.2 命名规范

```python
# 类名：大驼峰
class BaseStrategy
class BacktestEngine

# 函数名：小写 + 下划线
def load_data()
def run_backtest()

# 常量：全大写
DEFAULT_INITIAL_CAPITAL = 100000

# 私有成员：单下划线前缀
self._context
self._data
```

---

## 2. 核心 API

### 2.1 策略构建器

```python
from openfinagent import StrategyBuilder

# 方式 1: 自然语言创建
strategy = StrategyBuilder.from_natural_language("""
当 5 日均线上穿 20 日均线时买入
当 5 日均线下穿 20 日均线时卖出
初始资金 10 万元
""")

# 方式 2: 模板创建
strategy = StrategyBuilder.create(
    strategy_type='ma_cross',
    short_window=5,
    long_window=20,
    initial_capital=100000,
    name='双均线策略'
)

# 方式 3: 自定义策略
class MyStrategy(BaseStrategy):
    name = 'my_strategy'
    parameters = {'param1': 10}
    
    def on_bar(self, context, bar):
        # 自定义逻辑
        pass

strategy = MyStrategy(param1=20)
```

### 2.2 数据加载

```python
from openfinagent import load_data

# A 股数据
data = load_data(
    symbol='600519.SH',
    start='2023-01-01',
    end='2023-12-31',
    interval='1d',
    source='akshare'  # akshare / yfinance / mock
)

# 多只股票
symbols = ['600519.SH', '000001.SZ', '300750.SZ']
data_dict = load_data(
    symbol=symbols,
    start='2023-01-01',
    end='2023-12-31'
)

# 数据格式
# DataFrame: [datetime, open, high, low, close, volume, amount]
```

### 2.3 回测引擎

```python
from openfinagent import BacktestEngine

# 创建引擎
engine = BacktestEngine(
    commission_rate=0.0003,  # 佣金率 (万三)
    slippage=0.001,          # 滑点 (0.1%)
    initial_capital=100000   # 初始资金
)

# 单次回测
result = engine.run(
    strategy=strategy,
    data=data
)

# 批量回测
strategies = [
    StrategyBuilder.create('ma_cross', short_window=5, long_window=20),
    StrategyBuilder.create('ma_cross', short_window=10, long_window=30),
    StrategyBuilder.create('momentum', lookback=20, threshold=0.05),
]

results = engine.run_multi(
    strategies=strategies,
    data=data,
    n_jobs=-1  # 并行回测
)
```

### 2.4 回测结果

```python
# 显示结果
result.show()

# 输出:
# ==================== 回测结果 ====================
# 策略名称：双均线策略
# 回测区间：2023-01-01 ~ 2023-12-31
# 初始资金：100,000.00
# 最终资金：115,230.50
# 
# 总收益：15.23%
# 年化收益：15.23%
# 夏普比率：1.85
# 最大回撤：-8.23%
# 胜率：62.50%
# 交易次数：24
# ================================================

# 获取指标
metrics = result.metrics
print(metrics['总收益'])      # 0.1523
print(metrics['年化收益'])    # 0.1523
print(metrics['夏普比率'])    # 1.85
print(metrics['最大回撤'])    # -0.0823

# 绘制图表
result.plot()  # 显示权益曲线、回撤图等

# 导出结果
result.to_csv('backtest_result.csv')
result.to_json('backtest_result.json')

# 获取交易记录
trades = result.trades
# DataFrame: [datetime, symbol, side, quantity, price, commission]

# 获取权益曲线
equity = result.equity_curve
# DataFrame: [datetime, total_asset, cash, market_value, daily_return]
```

---

## 3. 策略开发 API

### 3.1 策略基类

```python
from openfinagent.strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    """自定义策略示例"""
    
    name = 'my_strategy'
    parameters = {
        'short_window': 5,
        'long_window': 20,
        'stop_loss': 0.05,
        'take_profit': 0.10
    }
    
    def on_init(self, context):
        """策略初始化"""
        # 注册指标
        self.register_indicator('ma5', self.ma_short)
        self.register_indicator('ma20', self.ma_long)
        
        # 日志
        self.log.info(f"策略初始化：{self.name}")
    
    def on_bar(self, context, bar):
        """K 线回调 - 核心逻辑"""
        # 获取指标
        ma5 = context.get_indicator('ma5')
        ma20 = context.get_indicator('ma20')
        
        # 获取持仓
        position = context.get_position(bar.symbol)
        
        # 交易逻辑
        if self.cross_above(ma5, ma20) and position.quantity == 0:
            # 金叉且空仓 → 买入
            self.buy(bar.symbol, bar.close, 100)
        
        elif self.cross_below(ma5, ma20) and position.quantity > 0:
            # 死叉且持仓 → 卖出
            self.sell(bar.symbol, bar.close, position.quantity)
    
    def on_order(self, context, order):
        """订单回调"""
        self.log.info(f"订单状态：{order.status}")
    
    def on_trade(self, context, trade):
        """成交回调"""
        self.log.info(f"成交：{trade.symbol} {trade.side} {trade.quantity}@{trade.price}")
```

### 3.2 上下文 API

```python
class StrategyContext:
    """策略上下文"""
    
    # 获取数据
    def get_data(self, symbol: str) -> DataFrame:
        """获取历史数据"""
        pass
    
    def get_bar(self, symbol: str, index: int = -1) -> BarData:
        """获取 K 线 (默认最新)"""
        pass
    
    # 获取指标
    def get_indicator(self, name: str, **params) -> Series:
        """获取指标值"""
        pass
    
    # 获取持仓
    def get_position(self, symbol: str) -> Position:
        """获取持仓"""
        pass
    
    def get_all_positions(self) -> List[Position]:
        """获取所有持仓"""
        pass
    
    # 获取资金
    def get_account(self) -> Account:
        """获取账户信息"""
        pass
    
    # 交易操作
    def buy(self, symbol: str, price: float, quantity: int) -> Order:
        """买入"""
        pass
    
    def sell(self, symbol: str, price: float, quantity: int) -> Order:
        """卖出"""
        pass
    
    def order_target(self, symbol: str, target_quantity: int) -> Order:
        """目标仓位"""
        pass
    
    # 日志
    def log(self, message: str, level: str = 'info'):
        """记录日志"""
        pass
```

### 3.3 技术指标 API

```python
from openfinagent.strategy import indicators

# 移动平均线
ma5 = indicators.SMA(data['close'], period=5)
ema20 = indicators.EMA(data['close'], period=20)

# MACD
macd_line, signal_line, hist = indicators.MACD(
    data['close'],
    fast=12,
    slow=26,
    signal=9
)

# RSI
rsi = indicators.RSI(data['close'], period=14)

# 布林带
upper, middle, lower = indicators.BOLL(
    data['close'],
    period=20,
    std=2.0
)

# KDJ
k, d, j = indicators.KDJ(
    data['high'],
    data['low'],
    data['close'],
    n=9
)

# 自定义指标
def my_indicator(data: DataFrame) -> Series:
    return (data['close'] - data['open']) / data['open']

# 注册指标
from openfinagent.strategy import IndicatorRegistry
IndicatorRegistry.register('my_indicator', my_indicator)
```

---

## 4. 数据 API

### 4.1 数据加载器

```python
from openfinagent.data import DataAdapter

# 使用 AKShare
adapter = DataAdapter.create('akshare')
data = adapter.get_klines(
    symbol='600519.SH',
    start='2023-01-01',
    end='2023-12-31',
    interval='1d'
)

# 使用 Yahoo Finance
adapter = DataAdapter.create('yfinance')
data = adapter.get_klines(
    symbol='AAPL',
    start='2023-01-01',
    end='2023-12-31'
)

# 使用模拟数据
adapter = DataAdapter.create('mock')
data = adapter.get_klines(
    symbol='TEST.SH',
    start='2023-01-01',
    end='2023-12-31'
)
```

### 4.2 数据模型

```python
from openfinagent.data import BarData, TickData

# K 线数据
class BarData:
    symbol: str
    datetime: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: float
    open_interest: float  # 持仓量 (期货)
    
    def to_series(self) -> Series:
        """转换为 Series"""
        pass

# Tick 数据
class TickData:
    symbol: str
    datetime: datetime
    last_price: float
    volume: float
    open_interest: float
    bid_price_1: float
    bid_volume_1: float
    ask_price_1: float
    ask_volume_1: float
```

---

## 5. 可视化 API

### 5.1 基础绘图

```python
from openfinagent.visualization import Plotter

# 创建绘图器
plotter = Plotter()

# 绘制权益曲线
plotter.plot_equity_curve(result.equity_curve)

# 绘制回撤图
plotter.plot_drawdown(result.drawdown)

# 绘制交易分布
plotter.plot_trade_distribution(result.trades)

# 绘制指标雷达图
plotter.plot_radar(result.metrics)

# 多策略对比
plotter.plot_comparison(results)

# 保存图表
plotter.save('result.png', dpi=300)
```

### 5.2 K 线图

```python
from openfinagent.visualization import plot_kline_with_signals

# K 线 + 买卖信号
plot_kline_with_signals(
    data=data,
    signals=result.signals,
    indicators={'MA5': ma5, 'MA20': ma20},
    title='双均线策略'
)
```

---

## 6. CLI API

### 6.1 命令行工具

```bash
# 运行回测
tradeflow backtest \
  --strategy ma_cross \
  --symbol 600519.SH \
  --start 2023-01-01 \
  --end 2023-12-31 \
  --capital 100000

# 参数扫描
tradeflow optimize \
  --strategy ma_cross \
  --symbol 600519.SH \
  --param short_window:5:20:5 \
  --param long_window:20:60:10 \
  --metric sharpe

# 策略对比
tradeflow compare \
  --strategies ma_cross,momentum,rsi \
  --symbol 600519.SH \
  --start 2023-01-01 \
  --end 2023-12-31

# 下载数据
tradeflow download \
  --symbol 600519.SH \
  --start 2023-01-01 \
  --end 2023-12-31 \
  --output data/
```

### 6.2 配置文件

```yaml
# config.yaml
strategy:
  type: ma_cross
  parameters:
    short_window: 5
    long_window: 20

backtest:
  symbol: 600519.SH
  start: 2023-01-01
  end: 2023-12-31
  initial_capital: 100000
  commission_rate: 0.0003
  slippage: 0.001

output:
  directory: ./results
  format: [csv, json, png]
```

---

## 7. 错误处理

### 7.1 异常类型

```python
from openfinagent.exceptions import (
    OpenFinAgentError,        # 基类异常
    DataError,             # 数据错误
    StrategyError,         # 策略错误
    BacktestError,         # 回测错误
    ValidationError,       # 验证错误
    InsufficientCapitalError,  # 资金不足
    InsufficientPositionError, # 持仓不足
)

# 示例
try:
    result = engine.run(strategy, data)
except DataError as e:
    print(f"数据错误：{e}")
except StrategyError as e:
    print(f"策略错误：{e}")
except InsufficientCapitalError as e:
    print(f"资金不足：{e}")
```

### 7.2 错误码

| 错误码 | 异常类型 | 说明 |
|--------|----------|------|
| 1001 | DataError | 数据加载失败 |
| 1002 | DataError | 数据格式错误 |
| 2001 | StrategyError | 策略参数错误 |
| 2002 | StrategyError | 指标计算失败 |
| 3001 | BacktestError | 回测配置错误 |
| 3002 | InsufficientCapitalError | 资金不足 |
| 3003 | InsufficientPositionError | 持仓不足 |
| 4001 | ValidationError | 参数验证失败 |

---

## 8. 配置管理

### 8.1 全局配置

```python
from openfinagent import config

# 设置数据源
config.set_data_source('akshare')

# 设置缓存
config.set_cache_enabled(True)
config.set_cache_dir('~/.openfinagent/cache')

# 设置日志级别
config.set_log_level('INFO')

# 获取配置
source = config.get_data_source()
cache_dir = config.get_cache_dir()
```

### 8.2 策略配置

```python
from pydantic import BaseModel

class StrategyConfig(BaseModel):
    """策略配置"""
    name: str
    type: str
    parameters: dict
    
    class Config:
        extra = 'forbid'  # 禁止额外字段

# 验证配置
config = StrategyConfig(
    name='双均线策略',
    type='ma_cross',
    parameters={'short_window': 5, 'long_window': 20}
)
```

---

## 9. 扩展 API

### 9.1 注册自定义组件

```python
# 注册自定义策略
from openfinagent.strategy import StrategyRegistry

@StrategyRegistry.register
class MyStrategy(BaseStrategy):
    name = 'my_strategy'
    # ...

# 注册自定义指标
from openfinagent.strategy import IndicatorRegistry

@IndicatorRegistry.register('my_ma')
def my_moving_average(data: DataFrame, period: int = 20) -> Series:
    return data['close'].rolling(period).mean()

# 注册自定义数据源
from openfinagent.data import DataAdapterRegistry

@DataAdapterRegistry.register('my_source')
class MyDataAdapter(DataAdapter):
    def get_klines(self, symbol, start, end, interval):
        # 自定义数据源
        pass
```

### 9.2 插件系统 (Phase 2)

```python
# 安装插件
# pip install tradeflow-plugin-xxx

# 加载插件
from openfinagent import load_plugin

load_plugin('tradeflow-plugin-ml')  # 机器学习策略
load_plugin('tradeflow-plugin-risk')  # 风控模块
```

---

*文档版本：v1.0 | 创建时间：2026-03-06*
