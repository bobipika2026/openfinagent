# OpenFinAgent v0.5.0 重构方案

**版本**: v0.5.0 - 自动化量化交易平台  
**创建时间**: 2026-03-11  
**负责人**: 智渊 (AI 开发助手)  
**目标**: 从"回测工具"升级为"自动化量化交易平台"

---

## 📋 目录

1. [重构目标](#1-重构目标)
2. [新架构设计](#2-新架构设计)
3. [核心模块](#3-核心模块)
4. [数据流设计](#4-数据流设计)
5. [技术实现](#5-技术实现)
6. [开发计划](#6-开发计划)

---

## 1. 重构目标

### 1.1 核心需求

| 模块 | 功能 | 优先级 |
|------|------|--------|
| **策略商店** | 自然语言创建策略 + 自动回测 + 自动入库 | P0 |
| **策略商店** | 互联网经验搜索 + 策略生成 + 回测验证 | P0 |
| **策略商店** | 策略持续自动化优化 | P1 |
| **选股模块** | 自动化选股 + 批量回测 + 股票池生成 | P0 |
| **回测模块** | 自动化策略回测 + 评分系统 | P0 |
| **监控模块** | 行情监控 + 信号识别 + 实时通知 | P0 |

### 1.2 核心价值

- **零门槛**: 用自然语言创建策略，无需编程
- **自动化**: 策略创建→回测→入库→监控→通知全流程自动化
- **智能化**: AI 搜索互联网经验，自动生成和优化策略
- **实时性**: 7x24 小时监控行情，信号出现立即通知

---

## 2. 新架构设计

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        Web UI / API                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway                                 │
│              (路由、认证、限流、日志)                             │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ 策略工厂     │    │ 选股引擎     │    │ 监控中心     │
│ Strategy     │    │ Stock        │    │ Monitor      │
│ Factory      │    │ Selector     │    │ Center       │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ 回测引擎     │    │ 批量回测     │    │ 信号识别     │
│ Backtest     │    │ Batch        │    │ Signal       │
│ Engine       │    │ Runner       │    │ Detector     │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      策略商店                                    │
│                  Strategy Store                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ 策略库   │  │ 策略评分 │  │ 策略版本 │  │ 策略统计 │       │
│  │ Library  │  │ Rating   │  │ Version  │  │ Stats    │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      数据层                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ 行情数据 │  │ 股票池   │  │ 回测结果 │  │ 通知记录 │       │
│  │ Market   │  │ Pool     │  │ Results  │  │ Alerts   │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 模块职责

| 模块 | 职责 | 关键功能 |
|------|------|----------|
| **策略工厂** | 策略创建与优化 | 自然语言解析、互联网搜索、策略生成、自动优化 |
| **选股引擎** | 股票筛选 | 条件选股、批量回测、股票池管理 |
| **监控中心** | 实时监控 | 行情订阅、信号检测、通知推送 |
| **回测引擎** | 策略验证 | 历史回测、性能评估、评分系统 |
| **策略商店** | 策略管理 | 策略存储、版本管理、评分统计 |

---

## 3. 核心模块设计

### 3.1 策略工厂 (Strategy Factory)

#### 3.1.1 自然语言创建策略

```python
class StrategyFactory:
    """策略工厂 - 创建和优化策略"""
    
    def create_from_natural_language(
        self,
        description: str,
        auto_backtest: bool = True
    ) -> Strategy:
        """
        从自然语言创建策略
        
        Args:
            description: 策略描述 (如"5 日均线上穿 20 日均线时买入")
            auto_backtest: 是否自动回测
        
        Returns:
            策略对象
        """
        # 1. 解析自然语言
        parser = StrategyParser()
        params = parser.parse(description)
        
        # 2. 生成策略代码
        generator = StrategyGenerator()
        strategy = generator.generate(params)
        
        # 3. 自动回测
        if auto_backtest:
            report = self._auto_backtest(strategy)
            
            # 4. 回测成功则入库
            if report['score'] >= 60:  # 评分阈值
                store.add_strategy(strategy, report)
        
        return strategy
    
    def search_and_create(
        self,
        topic: str,
        auto_backtest: bool = True
    ) -> List[Strategy]:
        """
        搜索互联网经验并创建策略
        
        Args:
            topic: 策略主题 (如"均线策略"、"动量策略")
            auto_backtest: 是否自动回测
        
        Returns:
            策略列表
        """
        # 1. 搜索互联网经验
        searcher = InternetSearcher()
        experiences = searcher.search(topic)
        
        # 2. 从经验提取策略
        strategies = []
        for exp in experiences:
            strategy = self._extract_strategy_from_experience(exp)
            
            # 3. 回测验证
            if auto_backtest:
                report = self._auto_backtest(strategy)
                if report['score'] >= 60:
                    store.add_strategy(strategy, report)
                    strategies.append(strategy)
        
        return strategies
    
    def optimize_strategy(
        self,
        strategy_id: str,
        auto_backtest: bool = True
    ) -> Strategy:
        """
        优化现有策略
        
        Args:
            strategy_id: 策略 ID
            auto_backtest: 是否自动回测
        
        Returns:
            优化后的策略
        """
        # 1. 获取原策略
        strategy = store.get_strategy(strategy_id)
        
        # 2. 参数优化
        optimizer = GeneticOptimizer()
        optimized_params = optimizer.optimize(strategy)
        
        # 3. 应用优化
        strategy.params = optimized_params
        
        # 4. 回测验证
        if auto_backtest:
            report = self._auto_backtest(strategy)
            if report['score'] > strategy.backtest_report['score']:
                # 5. 更新策略
                strategy.version += 1
                store.update_strategy(strategy, report)
        
        return strategy
```

#### 3.1.2 互联网经验搜索

```python
class InternetSearcher:
    """互联网经验搜索器"""
    
    def __init__(self):
        self.search_engines = [
            'duckduckgo',
            'brave_search',
            'google_custom'
        ]
    
    def search(self, topic: str) -> List[StrategyExperience]:
        """
        搜索互联网上的策略经验
        
        Args:
            topic: 搜索主题
        
        Returns:
            经验列表
        """
        queries = self._generate_queries(topic)
        results = []
        
        for query in queries:
            for engine in self.search_engines:
                search_results = self._search(engine, query)
                for result in search_results:
                    exp = self._parse_experience(result)
                    if exp:
                        results.append(exp)
        
        return results
    
    def _generate_queries(self, topic: str) -> List[str]:
        """生成搜索查询"""
        templates = [
            f"{topic} 交易策略",
            f"{topic} 量化策略 参数",
            f"{topic} 策略 回测 经验",
            f"best {topic} trading strategy parameters",
        ]
        return templates
    
    def _parse_experience(self, content: str) -> Optional[StrategyExperience]:
        """从网页内容提取策略经验"""
        # 使用 NLP 提取关键信息
        # - 策略类型
        # - 参数范围
        # - 适用市场
        # - 风险提示
        pass
```

### 3.2 选股引擎 (Stock Selector)

```python
class StockSelector:
    """选股引擎 - 自动化选股"""
    
    def __init__(self):
        self.data_manager = DataManager()
        self.backtest_engine = BacktestEngine()
    
    def select_stocks(
        self,
        strategy: Strategy,
        stock_pool: List[str],
        criteria: StockCriteria
    ) -> StockPool:
        """
        根据策略选股
        
        Args:
            strategy: 策略对象
            stock_pool: 候选股票池
            criteria: 选股条件
        
        Returns:
            选出的股票池
        """
        selected = []
        
        for symbol in stock_pool:
            # 1. 获取数据
            data = self.data_manager.get_data(symbol)
            
            # 2. 快速回测
            report = self.backtest_engine.quick_backtest(
                strategy, data
            )
            
            # 3. 筛选条件
            if self._meet_criteria(report, criteria):
                selected.append({
                    'symbol': symbol,
                    'score': report['score'],
                    'metrics': report['metrics']
                })
        
        # 4. 排序
        selected.sort(key=lambda x: x['score'], reverse=True)
        
        return StockPool(
            stocks=selected[:criteria.top_n],
            created_at=datetime.now()
        )
    
    def batch_backtest(
        self,
        strategy: Strategy,
        stock_pool: List[str]
    ) -> BatchBacktestReport:
        """
        批量回测
        
        Args:
            strategy: 策略对象
            stock_pool: 股票池
        
        Returns:
            批量回测报告
        """
        reports = {}
        
        for symbol in stock_pool:
            data = self.data_manager.get_data(symbol)
            report = self.backtest_engine.backtest(strategy, data)
            reports[symbol] = report
        
        return BatchBacktestReport(
            strategy_id=strategy.id,
            reports=reports,
            summary=self._generate_summary(reports)
        )
```

### 3.3 回测评分系统 (Backtest Scoring)

```python
class BacktestScorer:
    """回测评分系统"""
    
    def score(self, report: BacktestReport) -> BacktestScore:
        """
        对回测结果进行评分
        
        Args:
            report: 回测报告
        
        Returns:
            评分结果
        """
        scores = {
            'return': self._score_return(report.total_return),
            'sharpe': self._score_sharpe(report.sharpe_ratio),
            'drawdown': self._score_drawdown(report.max_drawdown),
            'stability': self._score_stability(report),
            'risk_adjusted': self._score_risk_adjusted(report)
        }
        
        # 加权总分
        total_score = (
            scores['return'] * 0.25 +
            scores['sharpe'] * 0.25 +
            scores['drawdown'] * 0.20 +
            scores['stability'] * 0.15 +
            scores['risk_adjusted'] * 0.15
        )
        
        return BacktestScore(
            total=total_score,
            subscores=scores,
            level=self._get_level(total_score)
        )
    
    def _score_return(self, total_return: float) -> float:
        """收益率评分"""
        if total_return > 0.50:
            return 100
        elif total_return > 0.30:
            return 80
        elif total_return > 0.10:
            return 60
        elif total_return > 0:
            return 40
        else:
            return 20
    
    def _score_sharpe(self, sharpe: float) -> float:
        """夏普比率评分"""
        if sharpe > 2.0:
            return 100
        elif sharpe > 1.5:
            return 80
        elif sharpe > 1.0:
            return 60
        elif sharpe > 0.5:
            return 40
        else:
            return 20
    
    def _score_drawdown(self, max_dd: float) -> float:
        """最大回撤评分"""
        if max_dd < 0.10:
            return 100
        elif max_dd < 0.15:
            return 80
        elif max_dd < 0.20:
            return 60
        elif max_dd < 0.30:
            return 40
        else:
            return 20
    
    def _get_level(self, score: float) -> str:
        """获取评级"""
        if score >= 90:
            return 'S'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        else:
            return 'D'
```

### 3.4 监控中心 (Monitor Center)

```python
class MonitorCenter:
    """监控中心 - 实时监控和通知"""
    
    def __init__(self):
        self.strategies: List[Strategy] = []
        self.stock_pool: StockPool = None
        self.notifications: NotificationService = None
    
    def start_monitoring(
        self,
        strategies: List[str],
        stock_pool: str
    ):
        """
        开始监控
        
        Args:
            strategies: 策略 ID 列表
            stock_pool: 股票池 ID
        """
        # 1. 加载策略
        self.strategies = [
            store.get_strategy(sid) for sid in strategies
        ]
        
        # 2. 加载股票池
        self.stock_pool = pool_manager.get(stock_pool)
        
        # 3. 订阅行情
        for symbol in self.stock_pool.symbols:
            market_data.subscribe(symbol, self._on_tick)
        
        # 4. 启动监控循环
        self._start_monitoring_loop()
    
    def _on_tick(self, symbol: str, tick: TickData):
        """
        处理实时行情
        
        Args:
            symbol: 股票代码
            tick: 实时行情数据
        """
        # 1. 更新缓存数据
        self._update_cache(symbol, tick)
        
        # 2. 检查每个策略
        for strategy in self.strategies:
            signal = self._check_signal(strategy, symbol)
            
            # 3. 发现信号，发送通知
            if signal:
                self.notifications.send({
                    'type': 'signal',
                    'strategy': strategy.name,
                    'symbol': symbol,
                    'signal': signal,
                    'price': tick.price,
                    'time': tick.timestamp
                })
    
    def _check_signal(
        self,
        strategy: Strategy,
        symbol: str
    ) -> Optional[Signal]:
        """
        检查交易信号
        
        Args:
            strategy: 策略对象
            symbol: 股票代码
        
        Returns:
            交易信号 (如果有)
        """
        # 获取最新数据
        data = self._get_recent_data(symbol)
        
        # 运行策略
        signal = strategy.generate_signal(data)
        
        return signal
```

### 3.5 通知服务 (Notification Service)

```python
class NotificationService:
    """通知服务"""
    
    def __init__(self):
        self.channels = [
            'feishu',
            'email',
            'sms',
            'wechat'
        ]
    
    def send(self, notification: Notification):
        """
        发送通知
        
        Args:
            notification: 通知对象
        """
        # 根据用户偏好选择渠道
        user = user_service.get(notification.user_id)
        
        for channel in user.notification_channels:
            self._send_via_channel(channel, notification)
    
    def _send_via_feishu(self, notification: Notification):
        """通过飞书发送通知"""
        # 使用飞书机器人 API
        pass
    
    def _send_via_email(self, notification: Notification):
        """通过邮件发送通知"""
        # 使用 SMTP 或 SendGrid
        pass
```

---

## 4. 数据流设计

### 4.1 策略创建流程

```
用户输入自然语言
      │
      ▼
策略解析器 (NLP)
      │
      ▼
策略生成器 (代码生成)
      │
      ▼
回测引擎 (自动验证)
      │
      ├───── 评分 < 60 ─────► 拒绝/优化
      │
      ▼ 评分 >= 60
策略商店 (自动入库)
      │
      ▼
通知用户 (策略创建成功)
```

### 4.2 选股流程

```
选择策略
      │
      ▼
定义选股条件
      │
      ▼
批量回测 (所有候选股票)
      │
      ▼
评分排序
      │
      ▼
生成股票池 (Top N)
      │
      ▼
保存并通知用户
```

### 4.3 监控流程

```
启动监控
      │
      ▼
订阅行情数据
      │
      ▼
实时接收 Tick 数据
      │
      ▼
运行策略信号检测
      │
      ├───── 无信号 ─────► 继续监控
      │
      ▼ 有信号
生成通知
      │
      ▼
推送给用户 (飞书/邮件/短信)
      │
      ▼
记录通知历史
```

---

## 5. 技术实现

### 5.1 新增模块结构

```
src/
├── strategy_factory/       # 策略工厂
│   ├── __init__.py
│   ├── factory.py         # 策略工厂核心
│   ├── generator.py       # 策略代码生成
│   └── optimizer.py       # 策略优化器
│
├── stock_selector/        # 选股引擎
│   ├── __init__.py
│   ├── selector.py        # 选股核心
│   ├── criteria.py        # 选股条件
│   └── pool_manager.py    # 股票池管理
│
├── monitor/               # 监控中心
│   ├── __init__.py
│   ├── center.py          # 监控中心核心
│   ├── signal_detector.py # 信号检测
│   └── subscription.py    # 行情订阅
│
├── scoring/               # 评分系统
│   ├── __init__.py
│   ├── scorer.py          # 评分核心
│   ├── metrics.py         # 评估指标
│   └── rating.py          # 评级系统
│
├── notification/          # 通知服务
│   ├── __init__.py
│   ├── service.py         # 通知服务核心
│   ├── channels.py        # 通知渠道
│   └── templates.py       # 通知模板
│
└── search/                # 互联网搜索
    ├── __init__.py
    ├── searcher.py        # 搜索核心
    ├── parser.py          # 经验解析
    └── knowledge_base.py  # 知识库
```

### 5.2 数据库设计

```sql
-- 策略表
CREATE TABLE strategies (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    code TEXT NOT NULL,
    params JSON,
    author_id VARCHAR(64),
    score FLOAT,
    rating VARCHAR(2),
    version INT DEFAULT 1,
    status VARCHAR(20),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 股票池表
CREATE TABLE stock_pools (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    strategy_id VARCHAR(64),
    stocks JSON,  -- [{symbol, score, metrics}]
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 回测结果表
CREATE TABLE backtest_results (
    id VARCHAR(64) PRIMARY KEY,
    strategy_id VARCHAR(64),
    symbol VARCHAR(20),
    report JSON,
    score FLOAT,
    created_at TIMESTAMP
);

-- 监控任务表
CREATE TABLE monitoring_tasks (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64),
    strategy_ids JSON,
    stock_pool_id VARCHAR(64),
    status VARCHAR(20),
    created_at TIMESTAMP
);

-- 通知记录表
CREATE TABLE notifications (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64),
    type VARCHAR(20),
    content JSON,
    channel VARCHAR(20),
    status VARCHAR(20),
    sent_at TIMESTAMP
);
```

### 5.3 API 设计

```python
# RESTful API 路由

# 策略工厂
POST   /api/v1/strategies/from-text      # 自然语言创建策略
POST   /api/v1/strategies/from-search    # 搜索互联网创建策略
POST   /api/v1/strategies/{id}/optimize  # 优化策略

# 选股
POST   /api/v1/stock-pools               # 创建股票池
GET    /api/v1/stock-pools               # 获取股票池列表
GET    /api/v1/stock-pools/{id}          # 获取股票池详情
DELETE /api/v1/stock-pools/{id}          # 删除股票池

# 回测
POST   /api/v1/backtest                  # 执行回测
GET    /api/v1/backtest/{id}             # 获取回测结果
POST   /api/v1/backtest/batch            # 批量回测

# 监控
POST   /api/v1/monitoring/start          # 启动监控
POST   /api/v1/monitoring/stop           # 停止监控
GET    /api/v1/monitoring/tasks          # 获取监控任务列表
GET    /api/v1/monitoring/signals        # 获取历史信号

# 通知
GET    /api/v1/notifications             # 获取通知列表
POST   /api/v1/notifications/test        # 测试通知渠道
PUT    /api/v1/notifications/settings    # 更新通知设置
```

---

## 6. 开发计划

### 6.1 阶段划分

| 阶段 | 时间 | 目标 | 交付物 |
|------|------|------|--------|
| **Phase 1** | 2026-03-11 ~ 2026-03-13 | 策略工厂 + 自然语言创建 | 可创建策略并自动入库 |
| **Phase 2** | 2026-03-14 ~ 2026-03-15 | 选股引擎 + 批量回测 | 可生成股票池 |
| **Phase 3** | 2026-03-16 ~ 2026-03-17 | 回测评分系统 | 策略自动评分 |
| **Phase 4** | 2026-03-18 ~ 2026-03-19 | 监控中心 + 通知 | 实时监控 + 信号通知 |
| **Phase 5** | 2026-03-20 | 集成测试 + 发布 | v0.5.0 正式发布 |

### 6.2 本周详细计划

#### Day 1-2 (2026-03-11 ~ 2026-03-12): 策略工厂

- [ ] 创建 `src/strategy_factory/` 模块
- [ ] 实现自然语言解析增强
- [ ] 实现策略代码生成器
- [ ] 集成自动回测流程
- [ ] 实现策略自动入库

#### Day 3-4 (2026-03-13 ~ 2026-03-14): 选股引擎

- [ ] 创建 `src/stock_selector/` 模块
- [ ] 实现选股条件定义
- [ ] 实现批量回测
- [ ] 实现股票池管理
- [ ] Web UI 选股页面

#### Day 5-6 (2026-03-15 ~ 2026-03-16): 回测评分

- [ ] 创建 `src/scoring/` 模块
- [ ] 实现评分算法
- [ ] 实现评级系统
- [ ] 集成到策略商店

#### Day 7-8 (2026-03-17 ~ 2026-03-18): 监控中心

- [ ] 创建 `src/monitor/` 模块
- [ ] 实现行情订阅
- [ ] 实现信号检测
- [ ] 实现通知服务
- [ ] 集成飞书通知

#### Day 9 (2026-03-19): 集成测试

- [ ] 端到端测试
- [ ] 性能测试
- [ ] Bug 修复

#### Day 10 (2026-03-20): 发布

- [ ] 文档完善
- [ ] Release Notes
- [ ] 正式发布 v0.5.0

---

## 7. 风险与应对

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| NLP 解析准确率低 | 中 | 高 | 提供模板 + 人工校验 |
| 互联网搜索质量不稳定 | 高 | 中 | 多引擎 + 质量过滤 |
| 实时监控性能问题 | 中 | 高 | 异步处理 + 缓存优化 |
| 通知延迟 | 中 | 高 | 多渠道 + 重试机制 |

---

## 8. 成功指标

| 指标 | 目标 | 测量方法 |
|------|------|----------|
| 策略创建时间 | < 5 分钟 | 用户操作到入库时间 |
| 选股准确率 | > 70% | 回测评分 C 级以上 |
| 监控延迟 | < 1 秒 | 信号出现到通知时间 |
| 用户满意度 | > 4.5/5 | 用户反馈评分 |

---

**下一步**: 开始 Phase 1 - 策略工厂开发
