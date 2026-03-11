"""
回测评分模块

提供证券行业标准的策略回测评分和评级功能。
支持多维度评分、综合评级、策略比较等功能。

主要功能:
- 多维度评分：收益率、夏普比率、最大回撤、稳定性、风险调整
- 综合评级：S/A/B/C/D 五级评级体系
- 指标计算：总收益、年化收益、夏普比率、最大回撤、Calmar 比率等
- 策略比较：多策略评分对比分析

使用示例:
    >>> from src.scoring import BacktestScorer, BacktestReport, EvaluationMetrics
    >>> import pandas as pd
    >>> from datetime import datetime
    >>> 
    >>> # 创建回测报告
    >>> equity_curve = pd.Series([100, 105, 110, 108, 115, 120, 125, 130])
    >>> daily_returns = equity_curve.pct_change().dropna()
    >>> report = BacktestReport(
    ...     strategy_name="均线策略",
    ...     initial_capital=100000,
    ...     final_capital=130000,
    ...     equity_curve=equity_curve,
    ...     trades=[],
    ...     daily_returns=daily_returns,
    ...     start_date=datetime(2024, 1, 1),
    ...     end_date=datetime(2024, 12, 31),
    ... )
    >>> 
    >>> # 创建评分器并评分
    >>> scorer = BacktestScorer()
    >>> score = scorer.score(report)
    >>> 
    >>> # 查看结果
    >>> print(f"综合评分：{score.total_score}")
    >>> print(f"评级等级：{score.rating.level.value}")
    >>> score.show()

模块结构:
- scorer: 评分核心类 (BacktestScorer)
- metrics: 评估指标计算 (EvaluationMetrics)
- rating: 评级系统 (RatingSystem, RatingLevel)

作者：TradeFlow AI Team
版本：1.0.0
"""

from .scorer import BacktestScorer, BacktestScore, BacktestReport, DimensionScore
from .metrics import EvaluationMetrics, Trade
from .rating import RatingSystem, RatingLevel, RatingResult

__all__ = [
    # 评分核心
    'BacktestScorer',
    'BacktestScore',
    'BacktestReport',
    'DimensionScore',
    
    # 评估指标
    'EvaluationMetrics',
    'Trade',
    
    # 评级系统
    'RatingSystem',
    'RatingLevel',
    'RatingResult',
]

__version__ = '1.0.0'
__author__ = 'TradeFlow AI Team'
