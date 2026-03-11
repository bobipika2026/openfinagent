"""
评分核心模块

实现回测评分的核心逻辑，包括多维度评分计算、加权综合评分、
等级评定等功能。
"""

import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .metrics import EvaluationMetrics, Trade
from .rating import RatingSystem, RatingLevel, RatingResult


@dataclass
class BacktestReport:
    """
    回测报告数据类

    包含回测结果的所有必要信息，用于评分计算。
    """
    strategy_name: str
    initial_capital: float
    final_capital: float
    equity_curve: pd.Series
    trades: List[Trade]
    daily_returns: pd.Series
    start_date: datetime
    end_date: datetime
    benchmark_return: float = 0.0  # 基准收益率 (如沪深 300)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'strategy_name': self.strategy_name,
            'initial_capital': self.initial_capital,
            'final_capital': self.final_capital,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'benchmark_return': self.benchmark_return,
        }


@dataclass
class DimensionScore:
    """维度评分数据类"""
    name: str
    score: float
    weight: float
    description: str

    def weighted_score(self) -> float:
        """计算加权分数"""
        return self.score * self.weight


@dataclass
class BacktestScore:
    """
    回测评分结果数据类

    包含各维度评分、综合评分、评级结果等完整信息。
    """
    strategy_name: str
    total_score: float
    rating: RatingResult
    dimension_scores: List[DimensionScore] = field(default_factory=list)
    metrics: Dict = field(default_factory=dict)
    evaluation_date: datetime = field(default_factory=datetime.now)
    comments: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'strategy_name': self.strategy_name,
            'total_score': round(self.total_score, 2),
            'rating': self.rating.to_dict(),
            'dimension_scores': [
                {
                    'name': ds.name,
                    'score': round(ds.score, 2),
                    'weight': ds.weight,
                    'weighted_score': round(ds.weighted_score(), 2),
                    'description': ds.description,
                }
                for ds in self.dimension_scores
            ],
            'metrics': {k: round(v, 3) if isinstance(v, float) else v for k, v in self.metrics.items()},
            'evaluation_date': self.evaluation_date.isoformat(),
            'comments': self.comments,
        }

    def show(self):
        """显示评分结果"""
        print("\n" + "=" * 60)
        print(f"📊 {self.strategy_name} 回测评分报告")
        print("=" * 60)
        print(f"综合评分：{self.total_score:.2f} 分")
        print(f"评级等级：{self.rating.level.value} 级 - {self.rating.description}")
        print("-" * 60)
        print("维度评分:")
        for ds in self.dimension_scores:
            print(f"  {ds.name:12} {ds.score:6.2f} 分 (权重 {ds.weight:.0%})")
        print("-" * 60)
        print("核心指标:")
        for key, value in self.metrics.items():
            if isinstance(value, float):
                print(f"  {key:20} {value:10.3f}")
            else:
                print(f"  {key:20} {value}")
        if self.comments:
            print("-" * 60)
            print("评价:")
            for comment in self.comments:
                print(f"  • {comment}")
        print("=" * 60)


class BacktestScorer:
    """
    回测评分器

    对回测结果进行多维度评分，生成综合评分和评级。
    评分维度包括收益率、夏普比率、最大回撤、稳定性、风险调整等。
    """

    # 默认评分权重
    DEFAULT_WEIGHTS = {
        'return': 0.25,        # 收益率评分 25%
        'sharpe': 0.25,        # 夏普比率评分 25%
        'drawdown': 0.20,      # 最大回撤评分 20%
        'stability': 0.15,     # 稳定性评分 15%
        'risk_adjusted': 0.15, # 风险调整评分 15%
    }

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        rating_system: Optional[RatingSystem] = None,
    ):
        """
        初始化回测评分器

        Args:
            weights: 评分权重配置，如不传则使用默认权重
            rating_system: 评级系统，如不传则使用默认评级系统

        Example:
            >>> scorer = BacktestScorer()
            >>> score = scorer.score(report)
            >>> print(score.total_score)
            85.5
        """
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self.rating_system = rating_system or RatingSystem()
        self.metrics_calculator = EvaluationMetrics()
        self._validate_weights()

    def _validate_weights(self):
        """验证权重配置的有效性"""
        total_weight = sum(self.weights.values())
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError(f"权重总和必须为 1.0，当前总和：{total_weight}")

    def score_return(self, total_return: float) -> float:
        """
        收益率评分

        评分标准:
        - >50%: 100 分
        - >30%: 80 分
        - >10%: 60 分
        - >0%: 40 分
        - <=0%: 20 分

        Args:
            total_return: 总收益率 (百分比形式)

        Returns:
            评分 (0-100)
        """
        if total_return > 50:
            return 100.0
        elif total_return > 30:
            return 80.0
        elif total_return > 10:
            return 60.0
        elif total_return > 0:
            return 40.0
        else:
            return 20.0

    def score_sharpe(self, sharpe_ratio: float) -> float:
        """
        夏普比率评分

        评分标准:
        - >2.0: 100 分
        - >1.5: 80 分
        - >1.0: 60 分
        - >0.5: 40 分
        - <=0.5: 20 分

        Args:
            sharpe_ratio: 夏普比率

        Returns:
            评分 (0-100)
        """
        if sharpe_ratio > 2.0:
            return 100.0
        elif sharpe_ratio > 1.5:
            return 80.0
        elif sharpe_ratio > 1.0:
            return 60.0
        elif sharpe_ratio > 0.5:
            return 40.0
        else:
            return 20.0

    def score_drawdown(self, max_drawdown: float) -> float:
        """
        最大回撤评分

        评分标准 (回撤越小越好):
        - <10%: 100 分
        - <15%: 80 分
        - <20%: 60 分
        - <30%: 40 分
        - >=30%: 20 分

        Args:
            max_drawdown: 最大回撤 (百分比形式，如 -15.5)

        Returns:
            评分 (0-100)
        """
        # 转换为绝对值
        abs_drawdown = abs(max_drawdown)

        if abs_drawdown < 10:
            return 100.0
        elif abs_drawdown < 15:
            return 80.0
        elif abs_drawdown < 20:
            return 60.0
        elif abs_drawdown < 30:
            return 40.0
        else:
            return 20.0

    def score_stability(self, monthly_volatility: float) -> float:
        """
        稳定性评分

        基于月度收益标准差，波动越小越稳定
        评分标准:
        - <5%: 100 分
        - <10%: 80 分
        - <15%: 60 分
        - <20%: 40 分
        - >=20%: 20 分

        Args:
            monthly_volatility: 月度收益标准差 (百分比形式)

        Returns:
            评分 (0-100)
        """
        if monthly_volatility < 5:
            return 100.0
        elif monthly_volatility < 10:
            return 80.0
        elif monthly_volatility < 15:
            return 60.0
        elif monthly_volatility < 20:
            return 40.0
        else:
            return 20.0

    def score_risk_adjusted(
        self,
        calmar_ratio: float,
        sortino_ratio: float,
        profit_factor: float,
    ) -> float:
        """
        风险调整评分

        综合 Calmar 比率、索提诺比率、盈亏比进行评分
        权重：Calmar 40%, Sortino 30%, Profit Factor 30%

        评分标准 (各项满分 100):
        Calmar:
        - >3.0: 100 分
        - >2.0: 80 分
        - >1.0: 60 分
        - >0.5: 40 分
        - <=0.5: 20 分

        Sortino:
        - >3.0: 100 分
        - >2.0: 80 分
        - >1.0: 60 分
        - >0.5: 40 分
        - <=0.5: 20 分

        Profit Factor:
        - >3.0: 100 分
        - >2.0: 80 分
        - >1.5: 60 分
        - >1.0: 40 分
        - <=1.0: 20 分

        Args:
            calmar_ratio: Calmar 比率
            sortino_ratio: 索提诺比率
            profit_factor: 盈亏比

        Returns:
            评分 (0-100)
        """
        # Calmar 评分
        if calmar_ratio > 3.0:
            calmar_score = 100.0
        elif calmar_ratio > 2.0:
            calmar_score = 80.0
        elif calmar_ratio > 1.0:
            calmar_score = 60.0
        elif calmar_ratio > 0.5:
            calmar_score = 40.0
        else:
            calmar_score = 20.0

        # Sortino 评分
        if sortino_ratio > 3.0:
            sortino_score = 100.0
        elif sortino_ratio > 2.0:
            sortino_score = 80.0
        elif sortino_ratio > 1.0:
            sortino_score = 60.0
        elif sortino_ratio > 0.5:
            sortino_score = 40.0
        else:
            sortino_score = 20.0

        # Profit Factor 评分
        if profit_factor > 3.0:
            pf_score = 100.0
        elif profit_factor > 2.0:
            pf_score = 80.0
        elif profit_factor > 1.5:
            pf_score = 60.0
        elif profit_factor > 1.0:
            pf_score = 40.0
        else:
            pf_score = 20.0

        # 加权平均
        total_score = (
            calmar_score * 0.4 +
            sortino_score * 0.3 +
            pf_score * 0.3
        )

        return total_score

    def score(self, report: BacktestReport) -> BacktestScore:
        """
        对回测报告进行评分

        Args:
            report: 回测报告

        Returns:
            评分结果

        Example:
            >>> scorer = BacktestScorer()
            >>> score = scorer.score(report)
            >>> print(score.total_score)
            85.5
            >>> print(score.rating.level.value)
            'A'
        """
        # 计算基础指标
        metrics = self.metrics_calculator.calculate_all_metrics(
            pd.DataFrame({'equity': report.equity_curve}),
            report.trades,
        )

        # 各维度评分
        return_score = self.score_return(metrics.get('total_return', 0))
        sharpe_score = self.score_sharpe(metrics.get('sharpe_ratio', 0))
        drawdown_score = self.score_drawdown(metrics.get('max_drawdown', 0))
        stability_score = self.score_stability(metrics.get('monthly_volatility', 0))
        risk_adjusted_score = self.score_risk_adjusted(
            metrics.get('calmar_ratio', 0),
            metrics.get('sortino_ratio', 0),
            metrics.get('profit_factor', 0),
        )

        # 创建维度评分对象
        dimension_scores = [
            DimensionScore(
                name='收益率',
                score=return_score,
                weight=self.weights['return'],
                description=f"总收益 {metrics.get('total_return', 0):.2f}%",
            ),
            DimensionScore(
                name='夏普比率',
                score=sharpe_score,
                weight=self.weights['sharpe'],
                description=f"夏普比率 {metrics.get('sharpe_ratio', 0):.3f}",
            ),
            DimensionScore(
                name='最大回撤',
                score=drawdown_score,
                weight=self.weights['drawdown'],
                description=f"最大回撤 {metrics.get('max_drawdown', 0):.2f}%",
            ),
            DimensionScore(
                name='稳定性',
                score=stability_score,
                weight=self.weights['stability'],
                description=f"月度波动 {metrics.get('monthly_volatility', 0):.3f}%",
            ),
            DimensionScore(
                name='风险调整',
                score=risk_adjusted_score,
                weight=self.weights['risk_adjusted'],
                description=f"Calmar {metrics.get('calmar_ratio', 0):.3f}",
            ),
        ]

        # 计算综合评分
        total_score = sum(ds.weighted_score() for ds in dimension_scores)

        # 获取评级
        rating = self.rating_system.get_rating(total_score)

        # 生成评价
        comments = self._generate_comments(metrics, dimension_scores, rating)

        return BacktestScore(
            strategy_name=report.strategy_name,
            total_score=total_score,
            rating=rating,
            dimension_scores=dimension_scores,
            metrics=metrics,
            comments=comments,
        )

    def _generate_comments(
        self,
        metrics: Dict,
        dimension_scores: List[DimensionScore],
        rating: RatingResult,
    ) -> List[str]:
        """
        生成评价意见

        Args:
            metrics: 指标字典
            dimension_scores: 维度评分列表
            rating: 评级结果

        Returns:
            评价意见列表
        """
        comments = []

        # 收益率评价
        total_return = metrics.get('total_return', 0)
        if total_return > 50:
            comments.append("收益率表现卓越，远超市场平均水平")
        elif total_return > 30:
            comments.append("收益率表现良好，值得肯定")
        elif total_return > 10:
            comments.append("收益率表现一般，有提升空间")
        elif total_return > 0:
            comments.append("收益率为正，但表现较弱")
        else:
            comments.append("收益率为负，需要优化策略")

        # 风险控制评价
        max_dd = abs(metrics.get('max_drawdown', 0))
        if max_dd < 10:
            comments.append("风险控制优秀，回撤控制得当")
        elif max_dd < 20:
            comments.append("风险控制良好，在可接受范围内")
        else:
            comments.append("回撤较大，建议加强风险控制")

        # 夏普比率评价
        sharpe = metrics.get('sharpe_ratio', 0)
        if sharpe > 2.0:
            comments.append("风险收益比极佳")
        elif sharpe > 1.0:
            comments.append("风险收益比良好")
        else:
            comments.append("风险收益比有待提升")

        # 评级总结
        if rating.level == RatingLevel.S:
            comments.append("综合评级优秀，强烈推荐该策略")
        elif rating.level == RatingLevel.A:
            comments.append("综合评级良好，推荐该策略")
        elif rating.level == RatingLevel.B:
            comments.append("综合评级中等，建议进一步优化")
        elif rating.level == RatingLevel.C:
            comments.append("综合评级及格，存在较大改进空间")
        else:
            comments.append("综合评级不及格，不建议使用该策略")

        return comments

    def get_level(self, score: float) -> str:
        """
        根据评分获取等级

        Args:
            score: 综合评分 (0-100)

        Returns:
            等级字符串 (S/A/B/C/D)

        Example:
            >>> scorer = BacktestScorer()
            >>> scorer.get_level(92.5)
            'S'
        """
        level = self.rating_system.get_level(score)
        return level.value

    def compare_strategies(
        self,
        scores: List[BacktestScore],
    ) -> Dict:
        """
        比较多个策略的评分

        Args:
            scores: 评分结果列表

        Returns:
            比较结果字典
        """
        if not scores:
            return {}

        comparison = {
            'strategies': [],
            'best_strategy': None,
            'best_score': 0,
            'average_score': 0,
            'pass_rate': 0,
        }

        total_score = 0
        passing_count = 0

        for score in scores:
            comparison['strategies'].append({
                'name': score.strategy_name,
                'total_score': round(score.total_score, 2),
                'rating': score.rating.level.value,
            })

            total_score += score.total_score

            if score.rating.is_pass:
                passing_count += 1

            if score.total_score > comparison['best_score']:
                comparison['best_score'] = score.total_score
                comparison['best_strategy'] = score.strategy_name

        comparison['average_score'] = round(total_score / len(scores), 2)
        comparison['pass_rate'] = round((passing_count / len(scores)) * 100, 2)

        return comparison
