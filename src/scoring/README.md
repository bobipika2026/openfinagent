# 回测评分系统

证券行业标准的策略回测评分和评级系统。

## 功能特性

- **多维度评分**: 收益率、夏普比率、最大回撤、稳定性、风险调整
- **综合评级**: S/A/B/C/D 五级评级体系
- **指标计算**: 总收益、年化收益、夏普比率、最大回撤、Calmar 比率、索提诺比率等
- **策略比较**: 多策略评分对比分析
- **高度可配置**: 支持自定义评分权重和评级阈值

## 快速开始

### 基本使用

```python
from src.scoring import BacktestScorer, BacktestReport, EvaluationMetrics
import pandas as pd
from datetime import datetime

# 1. 准备数据
equity_curve = pd.Series([100, 105, 110, 108, 115, 120, 125, 130])
daily_returns = equity_curve.pct_change().dropna()

# 2. 创建回测报告
report = BacktestReport(
    strategy_name="均线策略",
    initial_capital=100000,
    final_capital=130000,
    equity_curve=equity_curve,
    trades=[],  # 交易记录列表
    daily_returns=daily_returns,
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31),
)

# 3. 创建评分器并评分
scorer = BacktestScorer()
score = scorer.score(report)

# 4. 查看结果
print(f"综合评分：{score.total_score}")
print(f"评级等级：{score.rating.level.value}")
score.show()
```

### 输出示例

```
============================================================
📊 均线策略 回测评分报告
============================================================
综合评分：85.50 分
评级等级：A 级 - 良好 - 策略表现稳定，推荐
------------------------------------------------------------
维度评分:
  收益率         80.00 分 (权重 25%)
  夏普比率       90.00 分 (权重 25%)
  最大回撤       85.00 分 (权重 20%)
  稳定性         75.00 分 (权重 15%)
  风险调整       88.00 分 (权重 15%)
------------------------------------------------------------
核心指标:
  total_return           30.000
  sharpe_ratio            1.850
  max_drawdown           -8.500
  calmar_ratio            3.529
  win_rate               55.000
  profit_factor           2.100
------------------------------------------------------------
评价:
  • 收益率表现良好，值得肯定
  • 风险控制优秀，回撤控制得当
  • 风险收益比良好
  • 综合评级良好，推荐该策略
============================================================
```

## 评分标准

### 评分维度及权重

| 维度 | 权重 | 说明 |
|------|------|------|
| 收益率 | 25% | 总收益率，>50% 得 100 分 |
| 夏普比率 | 25% | 风险调整收益，>2.0 得 100 分 |
| 最大回撤 | 20% | 风险控制，<10% 得 100 分 |
| 稳定性 | 15% | 月度收益标准差，<5% 得 100 分 |
| 风险调整 | 15% | Calmar、Sortino、盈亏比综合 |

### 评级标准

| 等级 | 分数要求 | 说明 |
|------|----------|------|
| S | ≥90 | 优秀 - 策略表现卓越，强烈推荐 |
| A | ≥80 | 良好 - 策略表现稳定，推荐 |
| B | ≥70 | 中等 - 策略表现一般，可考虑 |
| C | ≥60 | 及格 - 策略表现勉强，需谨慎 |
| D | <60 | 不及格 - 策略表现差，不推荐 |

## 高级用法

### 自定义权重

```python
custom_weights = {
    'return': 0.4,        # 提高收益率权重
    'sharpe': 0.3,
    'drawdown': 0.15,
    'stability': 0.10,
    'risk_adjusted': 0.05,
}

scorer = BacktestScorer(weights=custom_weights)
```

### 自定义评级阈值

```python
from src.scoring import RatingSystem, RatingLevel

custom_thresholds = {
    RatingLevel.S: 95.0,  # 提高 S 级门槛
    RatingLevel.A: 85.0,
    RatingLevel.B: 75.0,
    RatingLevel.C: 65.0,
    RatingLevel.D: 0.0,
}

rating_system = RatingSystem(thresholds=custom_thresholds)
scorer = BacktestScorer(rating_system=rating_system)
```

### 策略比较

```python
# 对多个策略评分
scores = [scorer.score(report1), scorer.score(report2), scorer.score(report3)]

# 比较分析
comparison = scorer.compare_strategies(scores)
print(f"最佳策略：{comparison['best_strategy']}")
print(f"平均分数：{comparison['average_score']}")
print(f"通过率：{comparison['pass_rate']}%")
```

### 单独使用指标计算器

```python
from src.scoring import EvaluationMetrics

metrics = EvaluationMetrics()

# 计算总收益
total_return = metrics.total_return(equity_df)

# 计算夏普比率
sharpe = metrics.sharpe_ratio(returns_series)

# 计算最大回撤
max_dd = metrics.max_drawdown(equity_series)

# 计算所有指标
all_metrics = metrics.calculate_all_metrics(equity_df, trades)
```

## API 参考

### BacktestScorer

核心评分类。

**方法:**
- `score(report: BacktestReport) -> BacktestScore`: 对回测报告评分
- `get_level(score: float) -> str`: 根据分数获取等级 (S/A/B/C/D)
- `compare_strategies(scores: List[BacktestScore]) -> Dict`: 比较多个策略

### BacktestReport

回测报告数据类。

**字段:**
- `strategy_name`: 策略名称
- `initial_capital`: 初始资金
- `final_capital`: 最终资金
- `equity_curve`: 权益曲线 (pd.Series)
- `trades`: 交易记录列表
- `daily_returns`: 日收益率序列
- `start_date`: 开始日期
- `end_date`: 结束日期
- `benchmark_return`: 基准收益率

### BacktestScore

评分结果数据类。

**字段:**
- `strategy_name`: 策略名称
- `total_score`: 综合评分
- `rating`: 评级结果
- `dimension_scores`: 维度评分列表
- `metrics`: 核心指标字典
- `comments`: 评价意见列表

**方法:**
- `to_dict() -> Dict`: 转换为字典
- `show()`: 打印评分报告

### EvaluationMetrics

评估指标计算器。

**方法:**
- `total_return(data: pd.DataFrame) -> float`: 总收益率
- `annualized_return(data: pd.DataFrame) -> float`: 年化收益率
- `sharpe_ratio(returns: pd.Series) -> float`: 夏普比率
- `max_drawdown(equity: pd.Series) -> float`: 最大回撤
- `calmar_ratio(returns: pd.Series, max_dd: float) -> float`: Calmar 比率
- `win_rate(trades: List[Trade]) -> float`: 胜率
- `profit_factor(trades: List[Trade]) -> float`: 盈亏比
- `monthly_volatility(equity: pd.Series) -> float`: 月度波动率
- `sortino_ratio(returns: pd.Series) -> float`: 索提诺比率

### RatingSystem

评级系统。

**方法:**
- `get_level(score: float) -> RatingLevel`: 获取等级
- `get_rating(score: float) -> RatingResult`: 获取完整评级结果
- `is_passing(score: float) -> bool`: 判断是否及格
- `get_rating_distribution(scores: list) -> Dict`: 统计评级分布
- `get_pass_rate(scores: list) -> float`: 计算通过率

## 运行测试

```bash
# 运行所有测试
pytest tests/test_scoring.py -v

# 查看测试覆盖率
pytest tests/test_scoring.py --cov=src/scoring --cov-report=html

# 生成覆盖率报告
pytest tests/test_scoring.py --cov=src/scoring --cov-report=term-missing
```

## 依赖

- Python >= 3.8
- pandas >= 1.3
- numpy >= 1.20
- pytest >= 6.0 (测试)
- pytest-cov >= 3.0 (测试覆盖率)

## 注意事项

1. **数据质量**: 确保权益曲线和收益率数据准确无误
2. **交易记录**: 完整的交易记录有助于更准确的胜率和盈亏比计算
3. **时间跨度**: 建议使用至少 3 个月以上的数据进行评估
4. **基准对比**: 可设置 `benchmark_return` 与市场基准对比
5. **权重调整**: 可根据策略类型调整评分权重 (如高频策略更看重稳定性)

## 版本历史

- **1.0.0** (2024-03): 初始版本，实现核心评分和评级功能
