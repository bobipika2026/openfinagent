# OpenFinAgent v0.4.0 功能规格书

**版本**: v1.0  
**日期**: 2026-03-06  
**状态**: 评审中  
**关联文档**: [ROADMAP_v0.4.md](./ROADMAP_v0.4.md)

---

## 📋 目录

1. [概述](#1-概述)
2. [P0 功能规格](#2-p0-功能规格)
3. [P1 功能规格](#3-p1-功能规格)
4. [P2 功能规格](#4-p2-功能规格)
5. [技术架构](#5-技术架构)
6. [API 设计](#6-api 设计)
7. [数据模型](#7-数据模型)
8. [测试策略](#8-测试策略)
9. [部署方案](#9-部署方案)

---

## 1. 概述

### 1.1 文档目的

本文档定义 OpenFinAgent v0.4.0 的详细功能规格，包括：
- 功能描述和验收标准
- 技术实现方案
- API 接口设计
- 数据模型设计
- 测试策略

### 1.2 范围

**包含**:
- P0 功能 (4 个): 模拟盘、多数据源、策略市场、用户系统
- P1 功能 (4 个): ML 增强、风控增强、性能监控、日志系统
- P2 功能 (4 个): 移动端、API 服务化、插件系统、多语言

**不包含**:
- 商业化功能 (付费策略、订阅制)
- 企业级功能 (多租户、复杂权限)
- 深度 AI 集成 (AutoML)

### 1.3 目标读者

- 开发团队：实现参考
- 测试团队：测试用例编写
- 产品团队：功能验收
- 文档团队：文档编写

---

## 2. P0 功能规格

### 2.1 P0-1: 实盘对接设计 (模拟盘)

#### 2.1.1 功能描述

模拟盘 (Paper Trading) 是介于回测和实盘之间的交易模式，使用实时数据但不下实单，用于验证策略在真实市场环境中的表现。

**核心价值**:
- 零风险验证策略
- 发现回测未考虑的问题
- 降低实盘试错成本

#### 2.1.2 用户故事

```
作为 量化交易者
我希望 用实时数据运行策略但不实际下单
以便于 验证策略在真实环境中的表现

作为 新手
我希望 模拟盘和回测使用相同的接口
以便于 从回测平滑过渡到模拟盘

作为 进阶用户
我希望 查看模拟盘的实时持仓和收益
以便于 监控策略表现
```

#### 2.1.3 功能需求

| ID | 需求 | 优先级 | 验收标准 |
|----|------|--------|----------|
| FR-001 | 实时数据接入 | P0 | 支持至少 3 个数据源实时行情 |
| FR-002 | 模拟订单执行 | P0 | 支持市价单/限价单，含滑点手续费模拟 |
| FR-003 | 持仓管理 | P0 | 实时持仓更新，准确无误 |
| FR-004 | 收益计算 | P0 | 实时收益计算，误差 < 0.1% |
| FR-005 | 策略控制 | P0 | 支持暂停/恢复/停止策略 |
| FR-006 | 交易记录 | P0 | 完整记录所有模拟交易 |
| FR-007 | 与回测接口一致 | P0 | 同一策略无需修改代码 |

#### 2.1.4 技术设计

##### 架构设计
```
┌─────────────────────────────────────────────────────────┐
│                    策略层 (Strategy)                     │
│                   (与回测相同接口)                        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                 模拟盘引擎 (PaperEngine)                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ 订单管理器  │  │ 持仓管理器  │  │ 收益计算器  │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│  ┌─────────────┐  ┌─────────────┐                       │
│  │ 滑点模拟器  │  │ 手续费计算器 │                      │
│  └─────────────┘  └─────────────┘                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  实时数据层 (DataFeed)                   │
│     Tushare    │    Yahoo    │    AlphaVantage         │
└─────────────────────────────────────────────────────────┘
```

##### 核心类设计
```python
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"

@dataclass
class Order:
    id: str
    symbol: str
    direction: str  # buy/sell
    quantity: float
    price: Optional[float]  # 限价单价格
    order_type: OrderType
    status: OrderStatus
    filled_price: Optional[float]
    filled_quantity: float
    created_at: datetime
    filled_at: Optional[datetime]

@dataclass
class Position:
    symbol: str
    quantity: float
    avg_price: float
    unrealized_pnl: float
    realized_pnl: float

class PaperEngine:
    """模拟盘引擎"""
    
    def __init__(
        self,
        strategy,
        data_feed,
        initial_cash: float = 1000000,
        commission_rate: float = 0.0003,
        slippage_rate: float = 0.001
    ):
        self.strategy = strategy
        self.data_feed = data_feed
        self.cash = initial_cash
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        
        self.positions: Dict[str, Position] = {}
        self.orders: List[Order] = []
        self.trades: List[Dict] = []
        
        self.running = False
        self.paused = False
    
    def start(self):
        """启动模拟盘"""
        self.running = True
        self.paused = False
        self.strategy.on_start()
        
        # 订阅实时数据
        self.data_feed.subscribe(self.on_tick)
    
    def stop(self):
        """停止模拟盘"""
        self.running = False
        self.data_feed.unsubscribe()
        self.strategy.on_stop()
    
    def pause(self):
        """暂停模拟盘"""
        self.paused = True
    
    def resume(self):
        """恢复模拟盘"""
        self.paused = False
    
    def on_tick(self, tick_data):
        """处理实时行情"""
        if not self.running or self.paused:
            return
        
        # 推送数据给策略
        signals = self.strategy.on_tick(tick_data)
        
        # 处理策略信号
        for signal in signals:
            order = self.create_order(signal, tick_data)
            self.execute_order(order)
        
        # 更新持仓和收益
        self.update_positions(tick_data)
    
    def create_order(self, signal, tick_data) -> Order:
        """创建订单"""
        order = Order(
            id=self.generate_order_id(),
            symbol=signal.symbol,
            direction=signal.direction,
            quantity=signal.quantity,
            price=signal.price if hasattr(signal, 'price') else None,
            order_type=OrderType.MARKET if signal.type == 'market' else OrderType.LIMIT,
            status=OrderStatus.PENDING,
            filled_price=None,
            filled_quantity=0,
            created_at=datetime.now(),
            filled_at=None
        )
        return order
    
    def execute_order(self, order: Order):
        """执行订单 (模拟)"""
        # 获取当前市场价格
        current_price = self.get_current_price(order.symbol)
        
        # 模拟滑点
        if order.direction == 'buy':
            fill_price = current_price * (1 + self.slippage_rate)
        else:
            fill_price = current_price * (1 - self.slippage_rate)
        
        # 计算手续费
        commission = fill_price * order.quantity * self.commission_rate
        
        # 检查资金是否充足
        if order.direction == 'buy':
            required_cash = fill_price * order.quantity + commission
            if required_cash > self.cash:
                order.status = OrderStatus.REJECTED
                return
        
        # 执行订单
        order.filled_price = fill_price
        order.filled_quantity = order.quantity
        order.status = OrderStatus.FILLED
        order.filled_at = datetime.now()
        
        # 更新资金
        if order.direction == 'buy':
            self.cash -= required_cash
        else:
            self.cash += fill_price * order.quantity - commission
        
        # 更新持仓
        self.update_position_after_fill(order)
        
        # 记录交易
        self.trades.append({
            'order_id': order.id,
            'symbol': order.symbol,
            'direction': order.direction,
            'price': fill_price,
            'quantity': order.quantity,
            'commission': commission,
            'time': order.filled_at
        })
        
        self.orders.append(order)
    
    def get_portfolio_value(self) -> float:
        """获取组合总价值"""
        position_value = sum(
            pos.quantity * self.get_current_price(pos.symbol)
            for pos in self.positions.values()
        )
        return self.cash + position_value
    
    def get_return_rate(self) -> float:
        """获取收益率"""
        initial_value = 1000000  # 初始资金
        current_value = self.get_portfolio_value()
        return (current_value - initial_value) / initial_value
    
    def update_positions(self, tick_data):
        """更新持仓盈亏"""
        for symbol, position in self.positions.items():
            current_price = self.get_current_price(symbol)
            position.unrealized_pnl = (
                (current_price - position.avg_price) * position.quantity
            )
    
    # ... 其他辅助方法
```

#### 2.1.5 验收测试

```python
def test_paper_trading_basic():
    """测试模拟盘基本功能"""
    # 准备策略
    strategy = SimpleMovingAverageStrategy()
    
    # 创建模拟盘引擎
    engine = PaperEngine(
        strategy=strategy,
        data_feed=YahooFinanceFeed(),
        initial_cash=1000000
    )
    
    # 启动模拟盘
    engine.start()
    
    # 运行 1 分钟
    time.sleep(60)
    
    # 验证
    assert len(engine.trades) > 0, "应该有成交记录"
    assert engine.get_portfolio_value() > 0, "组合价值应该大于 0"
    
    # 停止模拟盘
    engine.stop()

def test_order_execution():
    """测试订单执行"""
    engine = PaperEngine(...)
    
    # 创建市价买单
    order = Order(
        symbol='000001.SZ',
        direction='buy',
        quantity=100,
        order_type=OrderType.MARKET
    )
    
    engine.execute_order(order)
    
    # 验证订单状态
    assert order.status == OrderStatus.FILLED
    assert order.filled_quantity == 100
    assert order.filled_price > 0
    
    # 验证持仓
    assert '000001.SZ' in engine.positions
    assert engine.positions['000001.SZ'].quantity == 100

def test_risk_control():
    """测试风控"""
    engine = PaperEngine(..., initial_cash=100000)
    
    # 尝试买入超过资金的订单
    order = Order(
        symbol='000001.SZ',
        direction='buy',
        quantity=100000,  # 超过资金
        order_type=OrderType.MARKET
    )
    
    engine.execute_order(order)
    
    # 验证订单被拒绝
    assert order.status == OrderStatus.REJECTED
```

---

### 2.2 P0-2: 更多数据源

#### 2.2.1 功能描述

扩展数据源支持，降低数据获取门槛，提供多数据源降级方案。

**支持的数据源**:
1. Tushare (已有) - A 股为主
2. Yahoo Finance (新增) - 全球市场
3. Alpha Vantage (新增) - 全球市场

#### 2.2.2 用户故事

```
作为 量化交易者
我希望 使用免费的数据源
以便于 降低交易成本

作为 用户
我希望 一个数据源失败时自动切换备用
以便于 策略稳定运行

作为 开发者
我希望 统一的数据源接口
以便于 轻松切换数据源
```

#### 2.2.3 功能需求

| ID | 需求 | 优先级 | 验收标准 |
|----|------|--------|----------|
| FR-010 | Yahoo Finance 集成 | P0 | 支持 A 股/美股/港股日线 |
| FR-011 | Alpha Vantage 集成 | P0 | 支持日线/分钟线 |
| FR-012 | 统一数据接口 | P0 | 切换数据源无需修改策略 |
| FR-013 | 数据源自动降级 | P0 | 主数据源失败自动切换备用 |
| FR-014 | 数据质量监控 | P1 | 检测数据缺失和异常 |

#### 2.2.4 技术设计

##### 数据源统一接口
```python
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
import pandas as pd

class DataFeed(ABC):
    """数据源抽象基类"""
    
    @abstractmethod
    def get_history(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        frequency: str = '1d'
    ) -> pd.DataFrame:
        """获取历史数据"""
        pass
    
    @abstractmethod
    def get_realtime(self, symbol: str) -> dict:
        """获取实时行情"""
        pass
    
    @abstractmethod
    def check_quality(self, symbol: str) -> dict:
        """检查数据质量"""
        pass
    
    @abstractmethod
    def get_supported_symbols(self) -> List[str]:
        """获取支持的标的列表"""
        pass

class YahooFinanceFeed(DataFeed):
    """Yahoo Finance 数据源"""
    
    def __init__(self):
        import yfinance as yf
        self.yf = yf
    
    def get_history(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        frequency: str = '1d'
    ) -> pd.DataFrame:
        """获取历史数据"""
        # 映射频率
        interval_map = {
            '1m': '1m',
            '5m': '5m',
            '15m': '15m',
            '30m': '30m',
            '60m': '1h',
            '1d': '1d',
            '1w': '1wk',
            '1M': '1mo'
        }
        interval = interval_map.get(frequency, '1d')
        
        # 获取数据
        ticker = self.yf.Ticker(symbol)
        df = ticker.history(start=start, end=end, interval=interval)
        
        # 标准化列名
        df = df.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        return df[['open', 'high', 'low', 'close', 'volume']]
    
    def get_realtime(self, symbol: str) -> dict:
        """获取实时行情"""
        ticker = self.yf.Ticker(symbol)
        info = ticker.info
        
        return {
            'symbol': symbol,
            'price': info.get('regularMarketPrice', 0),
            'open': info.get('regularMarketOpen', 0),
            'high': info.get('regularMarketDayHigh', 0),
            'low': info.get('regularMarketDayLow', 0),
            'volume': info.get('regularMarketVolume', 0),
            'timestamp': datetime.now()
        }
    
    def check_quality(self, symbol: str) -> dict:
        """检查数据质量"""
        # 获取最近 30 天数据
        end = datetime.now()
        start = end - pd.Timedelta(days=30)
        
        df = self.get_history(symbol, start, end)
        
        # 计算缺失率
        expected_days = 30
        actual_days = len(df)
        missing_rate = 1 - actual_days / expected_days
        
        return {
            'symbol': symbol,
            'missing_rate': missing_rate,
            'last_update': df.index[-1] if len(df) > 0 else None,
            'quality': 'good' if missing_rate < 0.1 else 'poor'
        }
    
    def get_supported_symbols(self) -> List[str]:
        """获取支持的标的列表"""
        # Yahoo Finance 支持全球市场，这里返回示例
        return ['AAPL', 'GOOGL', 'MSFT', '000001.SZ', '0700.HK']

class AlphaVantageFeed(DataFeed):
    """Alpha Vantage 数据源"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://www.alphavantage.co/query'
    
    def get_history(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        frequency: str = '1d'
    ) -> pd.DataFrame:
        """获取历史数据"""
        import requests
        
        # 根据频率选择 API
        if frequency in ['1m', '5m', '15m', '30m', '60m']:
            function = 'TIME_SERIES_INTRADAY'
            interval = frequency
        else:
            function = 'TIME_SERIES_DAILY'
            interval = None
        
        params = {
            'function': function,
            'symbol': symbol,
            'apikey': self.api_key,
            'datatype': 'json'
        }
        
        if interval:
            params['interval'] = interval
        
        response = requests.get(self.base_url, params=params)
        data = response.json()
        
        # 解析数据 (简化示例)
        # 实际实现需要处理 API 返回的嵌套结构
        
        return pd.DataFrame()
    
    def get_realtime(self, symbol: str) -> dict:
        """获取实时行情"""
        import requests
        
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        data = response.json()
        
        quote = data.get('Global Quote', {})
        
        return {
            'symbol': symbol,
            'price': float(quote.get('05. price', 0)),
            'volume': int(quote.get('06. volume', 0)),
            'timestamp': datetime.now()
        }
    
    def check_quality(self, symbol: str) -> dict:
        """检查数据质量"""
        # 类似 Yahoo Finance 实现
        pass
    
    def get_supported_symbols(self) -> List[str]:
        """获取支持的标的列表"""
        # Alpha Vantage 支持美股为主
        return ['AAPL', 'GOOGL', 'MSFT', 'TSLA']

class DataManager:
    """数据源管理器"""
    
    def __init__(self, config: dict):
        self.feeds = {}
        self.primary = config.get('primary', 'tushare')
        
        # 初始化数据源
        if 'tushare' in config:
            self.feeds['tushare'] = TushareFeed(config['tushare'])
        if 'yahoo' in config:
            self.feeds['yahoo'] = YahooFinanceFeed()
        if 'alphavantage' in config:
            self.feeds['alphavantage'] = AlphaVantageFeed(
                config['alphavantage']['api_key']
            )
    
    def get_history(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        frequency: str = '1d'
    ) -> pd.DataFrame:
        """获取历史数据 (带降级)"""
        # 尝试主数据源
        try:
            return self.feeds[self.primary].get_history(
                symbol, start, end, frequency
            )
        except Exception as e:
            print(f"主数据源 {self.primary} 失败：{e}")
        
        # 尝试备用数据源
        for feed_name in self.feeds:
            if feed_name == self.primary:
                continue
            try:
                return self.feeds[feed_name].get_history(
                    symbol, start, end, frequency
                )
            except Exception as e:
                print(f"备用数据源 {feed_name} 失败：{e}")
        
        raise Exception("所有数据源均不可用")
    
    def get_realtime(self, symbol: str) -> dict:
        """获取实时行情 (带降级)"""
        # 类似 get_history 实现
        pass
```

#### 2.2.5 配置示例

```yaml
# config/data_sources.yaml
data_sources:
  primary: tushare
  
  tushare:
    api_key: ${TUSHARE_API_KEY}
    enabled: true
  
  yahoo:
    enabled: true
  
  alphavantage:
    api_key: ${ALPHA_VANTAGE_API_KEY}
    enabled: true

# 使用示例
from openfinagent import DataManager

config = {
    'primary': 'tushare',
    'tushare': {'api_key': 'xxx'},
    'yahoo': {},
    'alphavantage': {'api_key': 'xxx'}
}

data_manager = DataManager(config)

# 获取历史数据 (自动降级)
df = data_manager.get_history(
    symbol='000001.SZ',
    start=datetime(2024, 1, 1),
    end=datetime(2024, 12, 31)
)
```

---

### 2.3 P0-3: 策略市场 (分享/下载)

#### 2.3.1 功能描述

内置策略分享和下载平台，支持用户上传、浏览、搜索、下载策略。

**核心价值**:
- 降低策略学习门槛
- 促进社区交流
- 构建生态壁垒

#### 2.3.2 用户故事

```
作为 策略开发者
我希望 分享我的策略给社区
以便于 获得反馈和认可

作为 学习者
我希望 下载他人的优秀策略学习
以便于 快速上手

作为 用户
我希望 查看策略的回测表现
以便于 判断策略质量
```

#### 2.3.3 功能需求

| ID | 需求 | 优先级 | 验收标准 |
|----|------|--------|----------|
| FR-020 | 策略上传 | P0 | 支持代码 + 描述 + 回测报告上传 |
| FR-021 | 策略浏览 | P0 | 支持列表/卡片视图 |
| FR-022 | 策略搜索 | P0 | 支持按名称/标签/作者搜索 |
| FR-023 | 策略下载 | P0 | 一键下载策略包 |
| FR-024 | 策略评级 | P0 | 支持 Star 和评论 |
| FR-025 | 策略分类 | P1 | CTA/套利/机器学习等分类 |
| FR-026 | 下载量统计 | P1 | 统计并展示下载量 |

#### 2.3.4 技术设计

##### 数据模型
```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Strategy:
    """策略数据模型"""
    id: str
    name: str
    description: str
    author_id: str
    author_name: str
    
    # 策略内容
    code: str
    config: dict
    backtest_report: dict
    
    # 分类
    category: str  # CTA/套利/机器学习/其他
    tags: List[str]
    
    # 统计信息
    downloads: int
    stars: int
    views: int
    
    # 版本管理
    version: str
    created_at: datetime
    updated_at: datetime
    
    # 状态
    status: str  # draft/published/archived

@dataclass
class Comment:
    """评论数据模型"""
    id: str
    strategy_id: str
    user_id: str
    user_name: str
    content: str
    created_at: datetime
    parent_id: Optional[str]  # 回复评论

@dataclass
class Star:
    """收藏数据模型"""
    strategy_id: str
    user_id: str
    created_at: datetime
```

##### API 设计
```python
from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional

app = FastAPI()

class StrategyMarketAPI:
    
    @app.post("/strategies")
    async def upload_strategy(
        strategy: StrategyCreate,
        current_user: User = Depends(get_current_user)
    ):
        """上传策略"""
        # 验证策略代码
        if not validate_strategy_code(strategy.code):
            raise HTTPException(400, "策略代码无效")
        
        # 保存策略
        strategy_id = save_strategy(strategy, current_user.id)
        
        return {"id": strategy_id, "message": "策略上传成功"}
    
    @app.get("/strategies")
    async def list_strategies(
        category: Optional[str] = None,
        tag: Optional[str] = None,
        author: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ):
        """浏览策略列表"""
        strategies = search_strategies(
            category=category,
            tag=tag,
            author=author,
            search=search,
            page=page,
            page_size=page_size
        )
        
        return {
            "strategies": strategies,
            "total": len(strategies),
            "page": page,
            "page_size": page_size
        }
    
    @app.get("/strategies/{strategy_id}")
    async def get_strategy(strategy_id: str):
        """获取策略详情"""
        strategy = get_strategy_by_id(strategy_id)
        
        if not strategy:
            raise HTTPException(404, "策略不存在")
        
        # 增加浏览量
        increment_views(strategy_id)
        
        return strategy
    
    @app.post("/strategies/{strategy_id}/download")
    async def download_strategy(
        strategy_id: str,
        current_user: User = Depends(get_current_user)
    ):
        """下载策略"""
        strategy = get_strategy_by_id(strategy_id)
        
        if not strategy:
            raise HTTPException(404, "策略不存在")
        
        # 增加下载量
        increment_downloads(strategy_id)
        
        # 记录下载历史
        record_download(strategy_id, current_user.id)
        
        return {
            "code": strategy.code,
            "config": strategy.config,
            "backtest_report": strategy.backtest_report
        }
    
    @app.post("/strategies/{strategy_id}/star")
    async def star_strategy(
        strategy_id: str,
        current_user: User = Depends(get_current_user)
    ):
        """收藏策略"""
        # 检查是否已收藏
        if is_starred(strategy_id, current_user.id):
            raise HTTPException(400, "已收藏")
        
        # 添加收藏
        add_star(strategy_id, current_user.id)
        
        return {"message": "收藏成功"}
    
    @app.post("/strategies/{strategy_id}/comments")
    async def add_comment(
        strategy_id: str,
        comment: CommentCreate,
        current_user: User = Depends(get_current_user)
    ):
        """添加评论"""
        comment_id = save_comment(
            strategy_id=strategy_id,
            user_id=current_user.id,
            content=comment.content,
            parent_id=comment.parent_id
        )
        
        return {"id": comment_id, "message": "评论成功"}
```

#### 2.3.5 策略包格式

```yaml
# strategy_package.yaml
# 策略包结构

strategy.yaml:          # 策略元数据
  name: "双均线策略"
  version: "1.0.0"
  author: "张三"
  description: "简单的双均线交叉策略"
  category: "CTA"
  tags: ["均线", "趋势跟踪"]
  
code/:
  strategy.py:          # 策略代码
  indicators.py:        # 自定义指标 (可选)
  
config.yaml:            # 策略配置
  params:
    short_period: 10
    long_period: 30
  
backtest/:
  report.json:          # 回测报告
  equity_curve.csv:     # 权益曲线
  trades.csv:           # 交易记录
  
README.md:              # 策略说明
```

---

### 2.4 P0-4: 用户系统 (认证/授权)

#### 2.4.1 功能描述

基础用户系统，支持注册、登录、认证、授权。

#### 2.4.2 功能需求

| ID | 需求 | 优先级 | 验收标准 |
|----|------|--------|----------|
| FR-030 | 用户注册 | P0 | 邮箱 + 密码注册 |
| FR-031 | 用户登录 | P0 | 邮箱 + 密码登录 |
| FR-032 | JWT 认证 | P0 | Token 有效期管理 |
| FR-033 | 密码加密 | P0 | bcrypt 加密存储 |
| FR-034 | 密码找回 | P0 | 邮箱验证重置密码 |
| FR-035 | 用户资料 | P1 | 可编辑个人信息 |
| FR-036 | 收藏关注 | P1 | 收藏策略、关注用户 |

#### 2.4.3 技术设计

##### 数据模型
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    """用户数据模型"""
    id: str
    username: str
    email: str
    password_hash: str
    
    # 个人信息
    bio: Optional[str]
    avatar_url: Optional[str]
    
    # 统计信息
    strategies_uploaded: int
    strategies_downloaded: int
    followers: int
    following: int
    
    # 状态
    is_active: bool
    is_verified: bool
    
    # 时间
    created_at: datetime
    last_login: Optional[datetime]
```

##### 认证服务
```python
import bcrypt
import jwt
from datetime import datetime, timedelta

class AuthService:
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def register(self, email: str, password: str, username: str) -> User:
        """用户注册"""
        # 检查邮箱是否已存在
        if user_exists(email):
            raise Exception("邮箱已被注册")
        
        # 密码加密
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # 创建用户
        user = User(
            id=generate_uuid(),
            username=username,
            email=email,
            password_hash=password_hash,
            bio=None,
            avatar_url=None,
            strategies_uploaded=0,
            strategies_downloaded=0,
            followers=0,
            following=0,
            is_active=True,
            is_verified=False,
            created_at=datetime.now(),
            last_login=None
        )
        
        save_user(user)
        
        # 发送验证邮件
        send_verification_email(email)
        
        return user
    
    def login(self, email: str, password: str) -> str:
        """用户登录"""
        # 查找用户
        user = get_user_by_email(email)
        
        if not user:
            raise Exception("用户不存在")
        
        if not user.is_active:
            raise Exception("账户已被禁用")
        
        # 验证密码
        if not bcrypt.checkpw(
            password.encode('utf-8'),
            user.password_hash.encode('utf-8')
        ):
            raise Exception("密码错误")
        
        # 更新最后登录时间
        user.last_login = datetime.now()
        update_user(user)
        
        # 生成 JWT Token
        token = self.generate_token(user)
        
        return token
    
    def generate_token(self, user: User) -> str:
        """生成 JWT Token"""
        payload = {
            'user_id': user.id,
            'email': user.email,
            'exp': datetime.now() + timedelta(days=7),
            'iat': datetime.now()
        }
        
        token = jwt.encode(
            payload,
            self.secret_key,
            algorithm='HS256'
        )
        
        return token
    
    def verify_token(self, token: str) -> User:
        """验证 JWT Token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=['HS256']
            )
            
            user_id = payload['user_id']
            user = get_user_by_id(user_id)
            
            if not user or not user.is_active:
                raise Exception("用户不存在或已被禁用")
            
            return user
            
        except jwt.ExpiredSignatureError:
            raise Exception("Token 已过期")
        except jwt.InvalidTokenError:
            raise Exception("Token 无效")
    
    def reset_password(self, email: str):
        """密码找回"""
        user = get_user_by_email(email)
        
        if not user:
            # 不提示用户不存在 (安全考虑)
            return
        
        # 生成重置 Token
        reset_token = generate_reset_token(user.id)
        
        # 发送重置邮件
        send_reset_email(email, reset_token)
```

---

## 3. P1 功能规格

### 3.1 P1-1: 机器学习策略增强

#### 3.1.1 功能描述

集成主流机器学习库，支持特征工程、模型训练、策略信号生成。

#### 3.1.2 功能需求

| ID | 需求 | 优先级 | 验收标准 |
|----|------|--------|----------|
| FR-040 | LightGBM 集成 | P1 | 支持训练和预测 |
| FR-041 | 特征工程工具 | P1 | 内置常用因子计算 |
| FR-042 | 模型评估 | P1 | 准确率/召回率等指标 |
| FR-043 | 特征重要性 | P1 | 可视化展示 |

#### 3.1.3 技术设计

```python
import lightgbm as lgb
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

class MLStrategy:
    """机器学习策略"""
    
    def __init__(self):
        self.model = None
        self.features = []
    
    def create_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """创建特征"""
        features = pd.DataFrame(index=data.index)
        
        # 技术指标
        features['ma_10'] = data['close'].rolling(10).mean()
        features['ma_30'] = data['close'].rolling(30).mean()
        features['rsi'] = self.calculate_rsi(data['close'], 14)
        features['volatility'] = data['close'].pct_change().rolling(20).std()
        
        # 价格特征
        features['return_1d'] = data['close'].pct_change(1)
        features['return_5d'] = data['close'].pct_change(5)
        features['return_10d'] = data['close'].pct_change(10)
        
        # 成交量特征
        features['volume_ma_10'] = data['volume'].rolling(10).mean()
        features['volume_ratio'] = data['volume'] / features['volume_ma_10']
        
        return features.dropna()
    
    def train(self, data: pd.DataFrame, target_col: str = 'next_day_return'):
        """训练模型"""
        # 创建特征
        features = self.create_features(data)
        
        # 创建标签 (次日收益率)
        target = data['close'].pct_change(1).shift(-1)
        target = (target > 0).astype(int)  # 二分类：涨/跌
        
        # 对齐特征和标签
        common_index = features.index.intersection(target.index)
        X = features.loc[common_index]
        y = target.loc[common_index]
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # 训练 LightGBM 模型
        self.model = lgb.LGBMClassifier(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=5,
            random_state=42
        )
        
        self.model.fit(X_train, y_train)
        
        # 评估
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"模型准确率：{accuracy:.4f}")
        print(classification_report(y_test, y_pred))
        
        # 特征重要性
        importance = pd.DataFrame({
            'feature': X.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n特征重要性 Top 10:")
        print(importance.head(10))
        
        return self.model
    
    def predict(self, data: pd.DataFrame) -> int:
        """预测"""
        if self.model is None:
            raise Exception("模型未训练")
        
        features = self.create_features(data)
        prediction = self.model.predict(features.iloc[-1:].values)[0]
        
        return prediction  # 1=涨，0=跌
```

---

## 4. P2 功能规格

(P2 功能为可选功能，时间不足可砍掉，此处简要描述)

### 4.1 P2-1: 移动端适配
- 响应式 Web 界面
- 移动端策略监控

### 4.2 P2-2: API 服务化
- RESTful API
- Swagger 文档

### 4.3 P2-3: 插件系统
- 插件接口定义
- 热加载机制

### 4.4 P2-4: 多语言支持
- 国际化框架
- 中英文切换

---

## 5. 技术架构

### 5.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                     应用层 (Application)                 │
│  CLI  │  Web UI  │  Jupyter  │  API Server              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                     服务层 (Services)                    │
│  策略引擎  │  回测引擎  │  模拟盘  │  数据管理  │  用户   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                     核心层 (Core)                        │
│  订单管理  │  持仓管理  │  风控  │  日志  │  配置       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                     基础设施层 (Infrastructure)          │
│  数据源  │  数据库  │  缓存  │  消息队列               │
└─────────────────────────────────────────────────────────┘
```

### 5.2 技术栈

| 层级 | 技术选型 |
|------|----------|
| 前端 | React + TypeScript + Ant Design |
| 后端 | Python 3.10+ + FastAPI |
| 数据库 | PostgreSQL + Redis |
| 消息队列 | RabbitMQ (可选) |
| 部署 | Docker + Docker Compose |
| CI/CD | GitHub Actions |

---

## 6. API 设计

### 6.1 RESTful API 规范

```
Base URL: /api/v1

认证：Bearer Token (JWT)

响应格式:
{
    "code": 200,
    "message": "success",
    "data": {...}
}
```

### 6.2 核心 API

详见各功能模块的 API 设计部分。

---

## 7. 数据模型

### 7.1 数据库设计

```sql
-- 用户表
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    bio TEXT,
    avatar_url VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- 策略表
CREATE TABLE strategies (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    author_id VARCHAR(36) REFERENCES users(id),
    code TEXT NOT NULL,
    config JSONB,
    backtest_report JSONB,
    category VARCHAR(50),
    tags TEXT[],
    downloads INT DEFAULT 0,
    stars INT DEFAULT 0,
    views INT DEFAULT 0,
    version VARCHAR(20),
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 策略收藏表
CREATE TABLE strategy_stars (
    strategy_id VARCHAR(36) REFERENCES strategies(id),
    user_id VARCHAR(36) REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (strategy_id, user_id)
);

-- 评论表
CREATE TABLE comments (
    id VARCHAR(36) PRIMARY KEY,
    strategy_id VARCHAR(36) REFERENCES strategies(id),
    user_id VARCHAR(36) REFERENCES users(id),
    content TEXT NOT NULL,
    parent_id VARCHAR(36) REFERENCES comments(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 8. 测试策略

### 8.1 测试金字塔

```
           /\
          /  \
         / E2E \       端到端测试 (10%)
        /______\
       /        \
      /Integration\    集成测试 (20%)
     /____________\
    /              \
   /    Unit Tests   \ 单元测试 (70%)
  /__________________\
```

### 8.2 测试覆盖率目标

| 模块 | 覆盖率目标 |
|------|------------|
| 核心引擎 | 90%+ |
| 数据源 | 85%+ |
| 用户系统 | 85%+ |
| 策略市场 | 80%+ |
| 总体 | 80%+ |

### 8.3 测试工具

- 单元测试：pytest
- 集成测试：pytest + testcontainers
- E2E 测试：Playwright
- 性能测试：locust

---

## 9. 部署方案

### 9.1 开发环境

```bash
# 本地开发
docker-compose -f docker-compose.dev.yml up
```

### 9.2 生产环境

```bash
# 生产部署
docker-compose -f docker-compose.prod.yml up -d
```

### 9.3 配置管理

- 环境变量：敏感信息 (API Key、密码)
- 配置文件：非敏感配置
- 密钥管理：使用 Vault 或云服务商密钥管理服务

---

**文档状态**: 评审中  
**最后更新**: 2026-03-06  
**下一步**: 开发团队评审 → 开始实现
