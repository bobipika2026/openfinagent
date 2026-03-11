# 选股引擎模块 (Stock Selector)

自动化选股、批量回测、股票池管理功能模块

## 📋 功能特性

- **自动化选股**: 根据自定义条件从股票池中筛选优质股票
- **批量回测**: 对多只股票并行执行回测，生成汇总报告
- **股票池管理**: 创建、更新、删除股票池，支持持久化和导入导出
- **多维度评分**: 基于收益、夏普比率、回撤、胜率等多指标综合评分
- **灵活筛选**: 支持市值、行业、ST 股、次新股等多种筛选条件
- **并发处理**: 使用线程池并行处理，提升选股和回测效率

## 📁 模块结构

```
stock_selector/
├── __init__.py          # 模块初始化，导出公共接口
├── criteria.py          # 选股条件定义 (StockCriteria, StockScore)
├── pool_manager.py      # 股票池管理 (StockPool, PoolManager)
├── selector.py          # 选股引擎核心 (StockSelector, BatchBacktestReport)
└── README.md            # 本文档
```

## 🚀 快速开始

### 1. 基础选股

```python
from src.stock_selector import StockSelector, StockCriteria, create_selector
from src.strategy.dual_ma_volume_strategy import DualMAStrategy

# 初始化选股引擎
selector = create_selector()

# 定义选股条件
criteria = StockCriteria(
    top_n=10,           # 选前 10 只股票
    min_score=70,       # 最低评分 70 分
    min_sharpe=1.5,     # 最低夏普比率 1.5
    max_drawdown=0.15,  # 最大回撤不超过 15%
    min_return=0.20     # 最低收益率 20%
)

# 准备候选股票池
candidate_pool = ['000001.SZ', '000002.SZ', '600036.SH']

# 创建策略
strategy = DualMAStrategy(short_period=5, long_period=20)

# 执行选股
selected_pool = selector.select_stocks(
    strategy=strategy,
    stock_pool=candidate_pool,
    criteria=criteria,
    start_date='2023-01-01',
    end_date='2023-12-31'
)

print(f"入选股票：{selected_pool.stocks}")
```

### 2. 批量回测

```python
# 执行批量回测
report = selector.batch_backtest(
    strategy=strategy,
    stock_pool=selected_pool.stocks,
    start_date='2023-01-01',
    end_date='2023-12-31',
    initial_capital=100000.0
)

# 显示报告
report.show()

# 获取排名
top_stocks = report.rank_stocks(by='sharpe', top_n=10)
for symbol, metrics in top_stocks:
    print(f"{symbol}: 夏普={metrics['夏普比率']:.2f}, 收益={metrics['总收益 (%)']:.2f}%")
```

### 3. 股票池管理

```python
# 创建股票池
pool = selector.create_pool(
    name='科技成长股',
    stocks=['000001.SZ', '000002.SZ', '600036.SH'],
    strategy_id='growth_strategy',
    description='高成长的科技行业股票',
    tags=['科技', '成长']
)

# 添加股票
pool.add_stock('000063.SZ')

# 移除股票
pool.remove_stock('000001.SZ')

# 导出股票池
selector.export_pool('科技成长股', '/path/to/export.json')

# 导入股票池
imported_pool = selector.import_pool('/path/to/export.json')

# 删除股票池
selector.delete_pool('科技成长股')
```

## 📊 选股条件详解

### StockCriteria 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `top_n` | int | 10 | 选前 N 只股票 |
| `min_score` | float | 60.0 | 最低评分 (0-100) |
| `min_sharpe` | float | 1.0 | 最低夏普比率 |
| `max_drawdown` | float | 0.20 | 最大回撤 (0-1) |
| `min_return` | float | 0.10 | 最低收益率 (0-1) |
| `selection_method` | SelectionMethod | SCORE_BASED | 选股排序方法 |
| `exclude_st` | bool | True | 是否排除 ST 股票 |
| `exclude_new` | bool | False | 是否排除次新股 |
| `min_market_cap` | float | None | 最小市值 (亿元) |
| `max_market_cap` | float | None | 最大市值 (亿元) |
| `sectors` | List[str] | None | 行业筛选列表 |

### SelectionMethod 枚举

- `SCORE_BASED`: 基于综合评分排序
- `SHARPE_BASED`: 基于夏普比率排序
- `RETURN_BASED`: 基于收益率排序
- `CUSTOM`: 自定义排序

### 示例：不同风格的选股条件

```python
# 保守型（低风险）
conservative = StockCriteria(
    top_n=15,
    min_score=75,
    min_sharpe=1.8,
    max_drawdown=0.08,
    min_return=0.15,
    min_market_cap=200  # 只选大盘股
)

# 激进型（高风险高收益）
aggressive = StockCriteria(
    top_n=8,
    min_score=55,
    min_sharpe=0.8,
    max_drawdown=0.35,
    min_return=0.50,
    selection_method=SelectionMethod.RETURN_BASED
)

# 平衡型
balanced = StockCriteria(
    top_n=10,
    min_score=65,
    min_sharpe=1.2,
    max_drawdown=0.18,
    min_return=0.25
)
```

## 📈 批量回测报告

### BatchBacktestReport 方法

```python
# 显示报告
report.show()

# 计算汇总统计
summary = report.calculate_summary()
print(summary)

# 按不同指标排名
top_by_return = report.rank_stocks(by='total_return', top_n=10)
top_by_sharpe = report.rank_stocks(by='sharpe', top_n=10)
top_by_winrate = report.rank_stocks(by='win_rate', top_n=10)

# 转换为字典
data = report.to_dict()
```

### 报告内容

- **总览**: 回测股票总数、成功数、失败数
- **汇总统计**: 平均收益、平均夏普、平均回撤、胜率分布
- **排名**: 按收益、夏普、回撤等指标的股票排名
- **个股详情**: 每只股票的详细回测指标

## 🛠️ 高级用法

### 1. 自定义评分权重

```python
selector = StockSelector()

# 自定义权重（更看重收益率）
custom_weights = {
    'return': 0.50,      # 收益率权重 50%
    'sharpe': 0.15,      # 夏普比率 15%
    'drawdown': 0.15,    # 回撤控制 15%
    'win_rate': 0.10,    # 胜率 10%
    'stability': 0.10    # 稳定性 10%
}

score = selector._calculate_score(
    total_return=0.30,
    sharpe_ratio=1.5,
    max_drawdown=0.15,
    win_rate=0.60,
    annual_return=0.35,
    volatility=0.20,
    weights=custom_weights
)
```

### 2. 并发控制

```python
# 增加并发数提升性能
selector = create_selector(max_workers=8)

# 对于资源受限的环境，减少并发
selector = create_selector(max_workers=2)
```

### 3. 股票池合并

```python
# 合并多个股票池
merged_pool = selector.pool_manager.merge_pools(
    pool_names=['池 1', '池 2', '池 3'],
    new_pool_name='合并池',
    remove_duplicates=True  # 去重
)
```

### 4. 股票池统计

```python
# 获取股票池统计信息
stats = selector.pool_manager.get_pool_stats('科技成长股')
print(stats)
# 输出：
# {
#     'name': '科技成长股',
#     'stock_count': 15,
#     'strategy_id': 'growth_strategy',
#     'created_at': '2024-01-01T00:00:00',
#     'updated_at': '2024-01-02T00:00:00',
#     'tags': ['科技', '成长'],
#     'description': '高成长的科技行业股票'
# }
```

## 🧪 测试

运行测试套件：

```bash
cd /root/.openclaw/workspace/projects/tradeflow-ai
python3 -m pytest tests/test_stock_selector.py -v
```

运行覆盖率测试：

```bash
python3 -m pytest tests/test_stock_selector.py --cov=src/stock_selector --cov-report=html
```

查看覆盖率报告：

```bash
# 终端报告
python3 -m pytest tests/test_stock_selector.py --cov=src/stock_selector --cov-report=term-missing

# HTML 报告
open htmlcov/index.html
```

## 📝 使用示例

完整示例请参考：

- `examples/stock_selector_demo.py` - 完整使用示例

## ⚠️ 注意事项

1. **数据源依赖**: 选股和回测需要数据源支持，确保已配置数据管理器
2. **并发控制**: 根据系统资源调整 `max_workers`，避免过度消耗
3. **缓存使用**: 重复选股时可启用 `use_cache=True` 提升性能
4. **异常处理**: 数据获取可能失败，建议添加异常处理逻辑
5. **股票池持久化**: 股票池自动保存到 `~/.tradeflow/pools/` 目录

## 🔧 配置选项

### 数据管理器配置

```python
data_config = {
    'primary': 'akshare',
    'fallback_order': ['akshare', 'yfinance', 'mock'],
    'sources': {
        'akshare': {'adjust': 'qfq'},
    },
    'enable_cache': True,
    'cache_ttl': 3600
}

selector = StockSelector(data_config=data_config)
```

### 股票池存储路径

```python
# 自定义存储路径
selector = StockSelector(pool_storage_path='/path/to/pools')

# 使用默认路径 (~/.tradeflow/pools)
selector = StockSelector()
```

## 📚 相关模块

- `src/data/manager.py` - 数据管理器
- `src/backtest/engine.py` - 回测引擎
- `src/strategy/` - 策略模块
- `src/scoring/` - 评分系统（待开发）

## 📄 版本历史

- **v1.0.0** (2024-03): 初始版本，实现基础选股、批量回测、股票池管理功能

---

**作者**: OpenFinAgent Team  
**版本**: 1.0.0  
**许可**: MIT
