# TradeFlow AI 系统架构设计

**版本**: v1.0  
**最后更新**: 2026-03-06  
**状态**: 架构设计文档

---

## 1. 系统概述

TradeFlow AI 是一个**自然语言驱动的量化策略开发平台**，让用户能够用中文描述交易想法，AI 自动将其转换为可执行的量化策略代码，并提供专业的回测和可视化分析。

### 1.1 核心价值主张

| 用户群体 | 痛点 | TradeFlow AI 解决方案 |
|----------|------|----------------------|
| 股票交易者 | 不会编程，无法验证交易想法 | 自然语言描述→自动代码生成 |
| 量化爱好者 | 学习曲线陡峭，框架复杂 | 零代码基础，5 分钟上手 |
| 开发者 | 重复造轮子，效率低 | 快速原型，专注策略逻辑 |
| 学生/研究者 | 缺乏专业工具 | 内置回测引擎和可视化 |

### 1.2 设计原则

1. **极简主义**: 5 分钟上手，无需编程基础
2. **中文优先**: 完整的中文支持和文档
3. **可扩展性**: 模块化设计，支持自定义扩展
4. **准确性**: 策略解析准确率 > 95%
5. **性能**: 回测速度 > 10 年数据/秒

---

## 2. 整体架构

### 2.1 架构分层

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户接口层 (User Interface)                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Python SDK │  │   CLI 工具   │  │  Web 界面    │ (Phase 3)   │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        应用服务层 (Application)                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ 策略构建器  │  │  回测服务   │  │  可视化服务  │             │
│  │  Builder    │  │  Backtest   │  │  Plotter    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        核心引擎层 (Core Engine)                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  NLP 解析器  │  │  策略引擎   │  │  交易引擎   │             │
│  │   Parser    │  │  Strategy   │  │   Trader    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据访问层 (Data Access)                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ 数据适配器  │  │  指标库     │  │  数据存储   │             │
│  │  Adapter    │  │  Indicators │  │   Storage   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        基础设施层 (Infrastructure)                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  AKShare    │  │ Yahoo Finance│  │  模拟数据   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 模块依赖关系

```
                    ┌─────────────────┐
                    │   User Interface│
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌────────────┐ ┌────────────┐ ┌────────────┐
     │  Builder   │ │  Backtest  │ │  Plotter   │
     └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
           │              │              │
           │      ┌───────┴───────┐      │
           │      │               │      │
           ▼      ▼               ▼      ▼
     ┌─────────────────────────────────────────┐
     │           Strategy Engine               │
     │    (BaseStrategy + Strategy Registry)   │
     └─────────────────┬───────────────────────┘
                       │
           ┌───────────┼───────────┐
           ▼           ▼           ▼
     ┌──────────┐ ┌──────────┐ ┌──────────┐
     │   NLP    │ │ Indicators│ │  Trader  │
     │  Parser  │ │   Library │ │  Engine  │
     └──────────┘ └──────────┘ └──────────┘
                       │
                       ▼
     ┌─────────────────────────────────────────┐
     │           Data Access Layer             │
     │  (AKShare / Yahoo / Mock / Cache)       │
     └─────────────────────────────────────────┘
```

---

## 3. 核心模块设计

### 3.1 NLP 解析器模块 (`src/nlp/`)

**职责**: 将自然语言策略描述转换为结构化策略配置

#### 3.1.1 解析流程

```
用户输入: "当 5 日均线上穿 20 日均线时买入，下穿时卖出"
    │
    ▼
┌─────────────────┐
│  1. 文本预处理   │  → 分词、去停用词、标准化
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. 意图识别    │  → 识别策略类型 (MA Cross / Momentum / RSI ...)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. 参数提取    │  → 提取参数 (short_window=5, long_window=20)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. 规则构建    │  → 构建买入/卖出规则
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  5. 策略生成    │  → 生成策略对象
└─────────────────┘

输出：StrategyConfig {
  type: "ma_cross",
  parameters: { short_window: 5, long_window: 20 },
  rules: {
    buy: "cross_above(ma5, ma20)",
    sell: "cross_below(ma5, ma20)"
  }
}
```

#### 3.1.2 模块结构

```
src/nlp/
├── __init__.py
├── parser.py           # 主解析器
├── tokenizer.py        # 分词器 (扩展)
├── intent_classifier.py # 意图分类器 (扩展)
├── parameter_extractor.py # 参数提取器 (扩展)
└── rules/
    ├── __init__.py
    ├── ma_rules.py     # 均线规则
    ├── momentum_rules.py # 动量规则
    └── rsi_rules.py    # RSI 规则
```

#### 3.1.3 关键类设计

```python
class StrategyParser:
    """策略解析器"""
    
    def parse(self, text: str) -> StrategyConfig:
        """解析自然语言为策略配置"""
        pass
    
    def validate(self, config: StrategyConfig) -> bool:
        """验证策略配置合法性"""
        pass


class IntentClassifier:
    """意图分类器"""
    
    def classify(self, tokens: List[str]) -> StrategyType:
        """识别策略类型"""
        pass


class ParameterExtractor:
    """参数提取器"""
    
    def extract(self, tokens: List[str], strategy_type: StrategyType) -> Dict:
        """提取策略参数"""
        pass
```

### 3.2 策略引擎模块 (`src/strategy/`)

**职责**: 策略定义、注册、执行

#### 3.2.1 策略基类

```python
class BaseStrategy:
    """策略基类"""
    
    name: str = "base_strategy"
    parameters: Dict[str, Any] = {}
    
    def __init__(self, **kwargs):
        """初始化策略"""
        pass
    
    def on_init(self, context: StrategyContext):
        """策略初始化回调"""
        pass
    
    def on_bar(self, context: StrategyContext, bar: BarData) -> Optional[Signal]:
        """K 线回调 - 核心逻辑"""
        pass
    
    def on_order(self, context: StrategyContext, order: Order):
        """订单回调"""
        pass
    
    def on_trade(self, context: StrategyContext, trade: Trade):
        """成交回调"""
        pass
```

#### 3.2.2 策略注册表

```python
class StrategyRegistry:
    """策略注册表"""
    
    _strategies: Dict[str, Type[BaseStrategy]] = {}
    
    @classmethod
    def register(cls, strategy_class: Type[BaseStrategy]):
        """注册策略"""
        cls._strategies[strategy_class.name] = strategy_class
    
    @classmethod
    def get(cls, name: str) -> Type[BaseStrategy]:
        """获取策略类"""
        pass
    
    @classmethod
    def list(cls) -> List[str]:
        """列出所有策略"""
        pass
```

#### 3.2.3 模块结构

```
src/strategy/
├── __init__.py
├── base.py             # 策略基类
├── builder.py          # 策略构建器
├── registry.py         # 策略注册表 (扩展)
├── context.py          # 策略上下文 (扩展)
├── indicators.py       # 技术指标
├── signals.py          # 信号定义 (扩展)
└── builtins/
    ├── __init__.py
    ├── ma_cross.py     # 均线交叉策略
    ├── momentum.py     # 动量策略
    ├── rsi.py          # RSI 策略
    └── macd.py         # MACD 策略
```

### 3.3 回测引擎模块 (`src/backtest/`)

**职责**: 历史数据回测、性能计算

#### 3.3.1 回测流程

```
┌─────────────────┐
│  1. 加载数据     │  → 从数据源加载历史 K 线
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. 初始化策略   │  → 创建策略实例、设置初始资金
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. 逐 K 线回放  │  → 调用 strategy.on_bar()
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. 信号处理    │  → 生成订单、检查风控
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  5. 订单撮合    │  → 模拟成交、更新持仓
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  6. 记录结果    │  → 交易记录、权益曲线
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  7. 性能分析    │  → 计算指标、生成报告
└─────────────────┘
```

#### 3.3.2 核心类设计

```python
class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, config: BacktestConfig):
        """初始化回测引擎"""
        pass
    
    def run(self, strategy: BaseStrategy, data: DataFrame) -> BacktestResult:
        """运行回测"""
        pass
    
    def run_multi(
        self, 
        strategies: List[BaseStrategy], 
        data: DataFrame
    ) -> Dict[str, BacktestResult]:
        """批量回测"""
        pass


class BacktestResult:
    """回测结果"""
    
    metrics: Dict[str, float]  # 性能指标
    equity_curve: DataFrame    # 权益曲线
    trades: List[Trade]        # 交易记录
    
    def show(self):
        """显示结果"""
        pass
    
    def plot(self):
        """绘制图表"""
        pass
    
    def to_csv(self, path: str):
        """导出 CSV"""
        pass
```

#### 3.3.3 模块结构

```
src/backtest/
├── __init__.py
├── engine.py           # 回测引擎
├── results.py          # 回测结果
├── config.py           # 回测配置 (扩展)
├── executor.py         # 订单执行器 (扩展)
├── matcher.py          # 撮合引擎 (扩展)
└── metrics/
    ├── __init__.py
    ├── returns.py      # 收益指标
    ├── risk.py         # 风险指标
    └── statistics.py   # 统计指标
```

### 3.4 数据访问模块 (`src/data/`)

**职责**: 数据加载、缓存、适配

#### 3.4.1 数据适配器模式

```python
class DataAdapter(ABC):
    """数据适配器基类"""
    
    @abstractmethod
    def get_klines(
        self, 
        symbol: str, 
        start: str, 
        end: str,
        interval: str = "1d"
    ) -> DataFrame:
        """获取 K 线数据"""
        pass
    
    @abstractmethod
    def get_symbol_list(self, market: str) -> List[str]:
        """获取证券列表"""
        pass


class AKShareAdapter(DataAdapter):
    """AKShare 数据适配器"""
    pass


class YahooAdapter(DataAdapter):
    """Yahoo Finance 适配器"""
    pass


class MockAdapter(DataAdapter):
    """模拟数据适配器"""
    pass
```

#### 3.4.2 模块结构

```
src/data/
├── __init__.py
├── base.py             # 数据适配器基类 (扩展)
├── akshare_adapter.py  # AKShare 适配器 (扩展)
├── yahoo_adapter.py    # Yahoo 适配器 (扩展)
├── mock_adapter.py     # 模拟数据适配器 (扩展)
├── cache.py            # 数据缓存 (扩展)
└── models/
    ├── __init__.py
    ├── bar.py          # K 线数据模型 (扩展)
    └── tick.py         # Tick 数据模型 (扩展)
```

### 3.5 可视化模块 (`src/visualization/`)

**职责**: 结果可视化、图表生成

#### 3.5.1 图表类型

| 图表类型 | 用途 | 实现 |
|----------|------|------|
| 权益曲线图 | 展示策略净值走势 | matplotlib |
| 回撤分析图 | 展示回撤幅度和持续时间 | matplotlib |
| 交易分布图 | 展示交易盈亏分布 | matplotlib + seaborn |
| 策略对比图 | 多策略性能对比 | matplotlib |
| 指标雷达图 | 多维度指标展示 | matplotlib |
| K 线 + 信号图 | K 线叠加买卖信号 | mplfinance |

#### 3.5.2 模块结构

```
src/visualization/
├── __init__.py
├── plotter.py          # 主绘图器
├── styles/             # 图表样式 (扩展)
│   ├── __init__.py
│   ├── default.py
│   └── dark.py
└── templates/          # 图表模板 (扩展)
    ├── equity_curve.py
    ├── drawdown.py
    └── comparison.py
```

---

## 4. 数据流设计

### 4.1 策略创建流程

```
用户输入自然语言
       │
       ▼
┌───────────────┐
│ StrategyBuilder│
│ .from_natural_language() │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ StrategyParser│ ──► 分词 → 意图识别 → 参数提取
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ StrategyConfig│
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ StrategyRegistry│ ──► 获取策略类
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ BaseStrategy  │ ──► 实例化策略
└───────────────┘
```

### 4.2 回测执行流程

```
┌─────────────────────────────────────────────────────────────┐
│                    BacktestEngine.run()                      │
└─────────────────────────────────────────────────────────────┘
        │
        ├──► 1. 加载数据 (DataAdapter.get_klines)
        │
        ├──► 2. 初始化策略 (Strategy.on_init)
        │
        ├──► 3. 循环处理每根 K 线
        │       │
        │       ├──► strategy.on_bar() → 生成 Signal
        │       │
        │       ├──► 检查风控规则
        │       │
        │       ├──► 创建 Order
        │       │
        │       └──► 撮合成交 → 更新 Position
        │
        ├──► 4. 计算性能指标 (Metrics Calculator)
        │
        └──► 5. 生成 BacktestResult
```

### 4.3 数据流转

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  外部数据源   │────►│  DataAdapter │────►│  数据缓存    │
│ (AKShare 等)  │     │              │     │   (Redis)    │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                                  ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  策略引擎     │◄────│  数据访问层   │◄────│  DataFrame   │
│              │     │              │     │  (内存)      │
└──────────────┘     └──────────────┘     └──────────────┘
```

---

## 5. 扩展性设计

### 5.1 策略扩展

```python
# 1. 继承基类
class MyCustomStrategy(BaseStrategy):
    name = "my_custom"
    parameters = {"param1": 10, "param2": 0.05}
    
    def on_bar(self, context, bar):
        # 自定义逻辑
        pass

# 2. 注册策略
StrategyRegistry.register(MyCustomStrategy)

# 3. 使用策略
strategy = StrategyBuilder.create("my_custom", param1=20)
```

### 5.2 数据源扩展

```python
# 1. 实现适配器
class MyDataAdapter(DataAdapter):
    def get_klines(self, symbol, start, end, interval):
        # 自定义数据源
        pass

# 2. 注册适配器
DataAdapterRegistry.register("my_source", MyDataAdapter)

# 3. 使用适配器
data = load_data("600519.SH", source="my_source")
```

### 5.3 指标扩展

```python
# 1. 自定义指标
def my_indicator(data: DataFrame) -> Series:
    return data["close"].rolling(10).mean()

# 2. 注册指标
IndicatorRegistry.register("my_ma", my_indicator)

# 3. 在策略中使用
ma = context.get_indicator("my_ma", period=10)
```

---

## 6. 性能优化

### 6.1 回测性能

| 优化点 | 方案 | 预期提升 |
|--------|------|----------|
| 数据加载 | 本地缓存 + 预加载 | 5-10x |
| 指标计算 | 向量化 (numpy/pandas) | 10-100x |
| 循环优化 | Cython/Numba JIT | 10-50x |
| 并行回测 | 多进程批量回测 | N x (N=核心数) |

### 6.2 缓存策略

```python
# 数据缓存
@cache(ttl=3600)
def get_klines(symbol, start, end):
    return adapter.get_klines(symbol, start, end)

# 指标缓存
class IndicatorCache:
    def __init__(self):
        self._cache = {}
    
    def get(self, indicator_name, params):
        key = f"{indicator_name}:{hash(params)}"
        return self._cache.get(key)
```

---

## 7. 安全设计

### 7.1 代码执行安全

- **沙箱环境**: 用户策略在隔离环境执行
- **资源限制**: CPU/内存使用限制
- **禁用函数**: 禁止系统调用、文件写入等危险操作

### 7.2 数据安全

- **API Key 加密**: 敏感信息加密存储
- **数据脱敏**: 日志中脱敏处理
- **访问控制**: 用户数据隔离

---

## 8. 技术债务管理

### 8.1 已知限制

| 限制 | 影响 | 解决计划 |
|------|------|----------|
| NLP 解析准确率 | 复杂策略识别率低 | Phase 2 引入 ML 模型 |
| 单线程回测 | 大批量回测慢 | Phase 2 支持并行 |
| 内存数据 | 大数据集受限 | Phase 3 支持数据库 |

### 8.2 重构计划

```
Phase 1 (v0.2): 代码规范化、类型注解
Phase 2 (v0.3): 性能优化、并行回测
Phase 3 (v0.5): 架构升级、微服务化
```

---

*文档版本：v1.0 | 创建时间：2026-03-06*
