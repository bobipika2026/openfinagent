"""
回测评分系统测试模块

测试覆盖率目标：>80%
测试范围:
- EvaluationMetrics: 指标计算正确性
- RatingSystem: 评级逻辑正确性
- BacktestScorer: 评分逻辑和综合评分
- 边界条件和异常情况

运行测试:
    pytest tests/test_scoring.py -v --cov=src/scoring --cov-report=html
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List

import sys
sys.path.insert(0, '/root/.openclaw/workspace/projects/tradeflow-ai')

from src.scoring.metrics import EvaluationMetrics, Trade
from src.scoring.rating import RatingSystem, RatingLevel, RatingResult
from src.scoring.scorer import (
    BacktestScorer,
    BacktestScore,
    BacktestReport,
    DimensionScore,
)


class TestEvaluationMetrics:
    """测试评估指标计算"""

    @pytest.fixture
    def metrics(self):
        """创建指标计算器实例"""
        return EvaluationMetrics()

    @pytest.fixture
    def sample_equity_data(self):
        """创建示例权益数据"""
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        equity = pd.Series(
            [100 * (1.001 ** i) for i in range(100)],
            index=dates,
        )
        return pd.DataFrame({'equity': equity})

    @pytest.fixture
    def sample_trades(self) -> List[Trade]:
        """创建示例交易记录"""
        trades = []
        base_date = datetime(2024, 1, 1)

        for i in range(10):
            is_win = i % 2 == 0  # 50% 胜率
            pnl = 1000 if is_win else -500

            trades.append(Trade(
                timestamp=base_date + timedelta(days=i),
                trade_type='sell',
                price=100 + i,
                shares=100,
                cost=10000,
                revenue=10000 + pnl,
                pnl=pnl,
            ))

        return trades

    def test_total_return(self, metrics, sample_equity_data):
        """测试总收益率计算"""
        total_return = metrics.total_return(sample_equity_data)

        # 验证收益率在合理范围内
        assert total_return > 0
        assert isinstance(total_return, float)

        # 手动计算验证
        initial = sample_equity_data['equity'].iloc[0]
        final = sample_equity_data['equity'].iloc[-1]
        expected = (final / initial - 1) * 100
        assert abs(total_return - expected) < 0.01

    def test_total_return_empty(self, metrics):
        """测试空数据的总收益率"""
        empty_data = pd.DataFrame()
        result = metrics.total_return(empty_data)
        assert result == 0.0

    def test_sharpe_ratio(self, metrics):
        """测试夏普比率计算"""
        returns = pd.Series([0.01, -0.005, 0.02, 0.015, -0.01, 0.005])
        sharpe = metrics.sharpe_ratio(returns)

        assert isinstance(sharpe, float)
        # 夏普比率应该是一个有限值
        assert not np.isnan(sharpe)
        assert not np.isinf(sharpe)

    def test_sharpe_ratio_empty(self, metrics):
        """测试空收益率序列的夏普比率"""
        empty_returns = pd.Series()
        result = metrics.sharpe_ratio(empty_returns)
        assert result == 0.0

    def test_max_drawdown(self, metrics):
        """测试最大回撤计算"""
        equity = pd.Series([100, 110, 105, 120, 115, 130, 125, 140])
        max_dd = metrics.max_drawdown(equity)

        assert isinstance(max_dd, float)
        assert max_dd <= 0  # 回撤应该是负数或 0

        # 验证最大回撤发生在从 140 之前的某个高点
        # 最大回撤应该是从 120 到 115: (115-120)/120 = -4.17%
        # 或从 130 到 125: (125-130)/130 = -3.85%
        assert max_dd > -10  # 回撤不应该太大

    def test_max_drawdown_empty(self, metrics):
        """测试空权益曲线的最大回撤"""
        empty_equity = pd.Series()
        result = metrics.max_drawdown(empty_equity)
        assert result == 0.0

    def test_calmar_ratio(self, metrics):
        """测试 Calmar 比率计算"""
        returns = pd.Series([0.01, 0.015, 0.02, 0.005])
        max_dd = -15.5  # 15.5% 回撤

        calmar = metrics.calmar_ratio(returns, max_dd)

        assert isinstance(calmar, float)
        assert calmar >= 0  # Calmar 比率应该非负

    def test_calmar_ratio_positive_drawdown(self, metrics):
        """测试正回撤的 Calmar 比率 (应该返回 0)"""
        returns = pd.Series([0.01, 0.015])
        calmar = metrics.calmar_ratio(returns, 5.0)  # 正的回撤
        assert calmar == 0.0

    def test_win_rate(self, metrics, sample_trades):
        """测试胜率计算"""
        win_rate = metrics.win_rate(sample_trades)

        assert isinstance(win_rate, float)
        assert 0 <= win_rate <= 100

        # 50% 胜率
        assert win_rate == 50.0

    def test_win_rate_empty(self, metrics):
        """测试空交易列表的胜率"""
        result = metrics.win_rate([])
        assert result == 0.0

    def test_profit_factor(self, metrics, sample_trades):
        """测试盈亏比计算"""
        profit_factor = metrics.profit_factor(sample_trades)

        assert isinstance(profit_factor, float)
        assert profit_factor >= 0

        # 5 笔盈利 (5000) / 5 笔亏损 (2500) = 2.0
        assert abs(profit_factor - 2.0) < 0.01

    def test_profit_factor_no_loss(self, metrics):
        """测试无亏损的盈亏比"""
        trades = [
            Trade(
                timestamp=datetime(2024, 1, 1),
                trade_type='sell',
                price=100,
                shares=100,
                cost=10000,
                revenue=12000,
                pnl=2000,
            ),
        ]
        pf = metrics.profit_factor(trades)
        assert pf == float('inf')

    def test_monthly_volatility(self, metrics):
        """测试月度波动率计算"""
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        equity = pd.Series(
            [100 * (1.001 ** i) for i in range(100)],
            index=dates,
        )

        monthly_vol = metrics.monthly_volatility(equity)

        assert isinstance(monthly_vol, float)
        assert monthly_vol >= 0

    def test_sortino_ratio(self, metrics):
        """测试索提诺比率计算"""
        returns = pd.Series([0.01, -0.005, 0.02, 0.015, -0.01, 0.005])
        sortino = metrics.sortino_ratio(returns)

        assert isinstance(sortino, float)
        assert not np.isnan(sortino)

    def test_calculate_all_metrics(self, metrics, sample_equity_data, sample_trades):
        """测试全部指标计算"""
        all_metrics = metrics.calculate_all_metrics(
            sample_equity_data,
            sample_trades,
        )

        assert isinstance(all_metrics, dict)
        assert 'total_return' in all_metrics
        assert 'sharpe_ratio' in all_metrics
        assert 'max_drawdown' in all_metrics
        assert 'calmar_ratio' in all_metrics
        assert 'win_rate' in all_metrics
        assert 'profit_factor' in all_metrics


class TestRatingSystem:
    """测试评级系统"""

    @pytest.fixture
    def rating_system(self):
        """创建评级系统实例"""
        return RatingSystem()

    def test_get_level_s(self, rating_system):
        """测试 S 级评级"""
        level = rating_system.get_level(95.0)
        assert level == RatingLevel.S

    def test_get_level_a(self, rating_system):
        """测试 A 级评级"""
        level = rating_system.get_level(85.0)
        assert level == RatingLevel.A

    def test_get_level_b(self, rating_system):
        """测试 B 级评级"""
        level = rating_system.get_level(75.0)
        assert level == RatingLevel.B

    def test_get_level_c(self, rating_system):
        """测试 C 级评级"""
        level = rating_system.get_level(65.0)
        assert level == RatingLevel.C

    def test_get_level_d(self, rating_system):
        """测试 D 级评级"""
        level = rating_system.get_level(50.0)
        assert level == RatingLevel.D

    def test_get_level_boundary_s(self, rating_system):
        """测试 S 级边界"""
        level = rating_system.get_level(90.0)
        assert level == RatingLevel.S

    def test_get_level_boundary_a(self, rating_system):
        """测试 A 级边界"""
        level = rating_system.get_level(80.0)
        assert level == RatingLevel.A

    def test_get_level_boundary_c(self, rating_system):
        """测试 C 级边界"""
        level = rating_system.get_level(60.0)
        assert level == RatingLevel.C

    def test_get_level_invalid_score(self, rating_system):
        """测试无效评分"""
        with pytest.raises(ValueError):
            rating_system.get_level(105.0)

        with pytest.raises(ValueError):
            rating_system.get_level(-5.0)

    def test_get_rating(self, rating_system):
        """测试获取完整评级结果"""
        result = rating_system.get_rating(85.5)

        assert isinstance(result, RatingResult)
        assert result.level == RatingLevel.A
        assert result.score == 85.5
        assert result.is_pass is True
        assert "良好" in result.description

    def test_is_passing(self, rating_system):
        """测试及格判断"""
        assert rating_system.is_passing(60.0) is True
        assert rating_system.is_passing(59.9) is False
        assert rating_system.is_passing(90.0) is True

    def test_get_threshold(self, rating_system):
        """测试获取阈值"""
        assert rating_system.get_threshold(RatingLevel.S) == 90.0
        assert rating_system.get_threshold(RatingLevel.A) == 80.0
        assert rating_system.get_threshold(RatingLevel.B) == 70.0
        assert rating_system.get_threshold(RatingLevel.C) == 60.0

    def test_rating_distribution(self, rating_system):
        """测试评级分布统计"""
        scores = [95, 85, 75, 65, 55, 92, 88, 72]
        distribution = rating_system.get_rating_distribution(scores)

        assert distribution['S'] == 2
        assert distribution['A'] == 2
        assert distribution['B'] == 2
        assert distribution['C'] == 1
        assert distribution['D'] == 1

    def test_pass_rate(self, rating_system):
        """测试通过率计算"""
        scores = [90, 80, 70, 60, 50]  # 4 个及格，1 个不及格
        pass_rate = rating_system.get_pass_rate(scores)

        assert pass_rate == 80.0

    def test_pass_rate_empty(self, rating_system):
        """测试空列表的通过率"""
        pass_rate = rating_system.get_pass_rate([])
        assert pass_rate == 0.0

    def test_to_dict(self, rating_system):
        """测试转换为字典"""
        config = rating_system.to_dict()

        assert isinstance(config, dict)
        assert 'thresholds' in config
        assert 'descriptions' in config


class TestBacktestScorer:
    """测试回测评分器"""

    @pytest.fixture
    def scorer(self):
        """创建评分器实例"""
        return BacktestScorer()

    @pytest.fixture
    def sample_report(self):
        """创建示例回测报告"""
        dates = pd.date_range(start='2024-01-01', periods=252, freq='D')
        equity = pd.Series(
            [100000 * (1.0005 ** i) for i in range(252)],
            index=dates,
        )
        daily_returns = equity.pct_change().dropna()

        trades = []
        for i in range(20):
            is_win = i % 2 == 0
            pnl = 2000 if is_win else -1000
            trades.append(Trade(
                timestamp=dates[i * 10],
                trade_type='sell',
                price=100 + i,
                shares=100,
                cost=10000,
                revenue=10000 + pnl,
                pnl=pnl,
            ))

        return BacktestReport(
            strategy_name="测试策略",
            initial_capital=100000,
            final_capital=equity.iloc[-1],
            equity_curve=equity,
            trades=trades,
            daily_returns=daily_returns,
            start_date=dates[0],
            end_date=dates[-1],
            benchmark_return=10.0,
        )

    def test_score_return(self, scorer):
        """测试收益率评分"""
        assert scorer.score_return(60.0) == 100.0
        assert scorer.score_return(40.0) == 80.0
        assert scorer.score_return(20.0) == 60.0
        assert scorer.score_return(5.0) == 40.0
        assert scorer.score_return(-5.0) == 20.0

    def test_score_sharpe(self, scorer):
        """测试夏普比率评分"""
        assert scorer.score_sharpe(2.5) == 100.0
        assert scorer.score_sharpe(1.8) == 80.0
        assert scorer.score_sharpe(1.2) == 60.0
        assert scorer.score_sharpe(0.8) == 40.0
        assert scorer.score_sharpe(0.3) == 20.0

    def test_score_drawdown(self, scorer):
        """测试回撤评分"""
        assert scorer.score_drawdown(-8.0) == 100.0
        assert scorer.score_drawdown(-12.0) == 80.0
        assert scorer.score_drawdown(-18.0) == 60.0
        assert scorer.score_drawdown(-25.0) == 40.0
        assert scorer.score_drawdown(-35.0) == 20.0

    def test_score_stability(self, scorer):
        """测试稳定性评分"""
        assert scorer.score_stability(4.0) == 100.0
        assert scorer.score_stability(8.0) == 80.0
        assert scorer.score_stability(12.0) == 60.0
        assert scorer.score_stability(18.0) == 40.0
        assert scorer.score_stability(25.0) == 20.0

    def test_score_risk_adjusted(self, scorer):
        """测试风险调整评分"""
        score = scorer.score_risk_adjusted(
            calmar_ratio=2.5,
            sortino_ratio=2.0,
            profit_factor=2.5,
        )
        assert isinstance(score, float)
        assert 0 <= score <= 100

    def test_score(self, scorer, sample_report):
        """测试完整评分流程"""
        score_result = scorer.score(sample_report)

        assert isinstance(score_result, BacktestScore)
        assert score_result.strategy_name == "测试策略"
        assert isinstance(score_result.total_score, float)
        assert 0 <= score_result.total_score <= 100
        assert isinstance(score_result.rating, RatingResult)
        assert len(score_result.dimension_scores) == 5
        assert isinstance(score_result.comments, list)
        assert len(score_result.comments) > 0

    def test_score_dimension_weights(self, scorer, sample_report):
        """测试维度权重总和"""
        score_result = scorer.score(sample_report)

        total_weight = sum(ds.weight for ds in score_result.dimension_scores)
        assert abs(total_weight - 1.0) < 0.001

    def test_get_level(self, scorer):
        """测试获取等级"""
        assert scorer.get_level(95.0) == 'S'
        assert scorer.get_level(85.0) == 'A'
        assert scorer.get_level(75.0) == 'B'
        assert scorer.get_level(65.0) == 'C'
        assert scorer.get_level(50.0) == 'D'

    def test_compare_strategies(self, scorer, sample_report):
        """测试策略比较"""
        score1 = scorer.score(sample_report)

        # 创建第二个策略报告
        dates = pd.date_range(start='2024-01-01', periods=252, freq='D')
        equity2 = pd.Series(
            [100000 * (1.0003 ** i) for i in range(252)],
            index=dates,
        )
        report2 = BacktestReport(
            strategy_name="保守策略",
            initial_capital=100000,
            final_capital=equity2.iloc[-1],
            equity_curve=equity2,
            trades=[],
            daily_returns=equity2.pct_change().dropna(),
            start_date=dates[0],
            end_date=dates[-1],
        )
        score2 = scorer.score(report2)

        comparison = scorer.compare_strategies([score1, score2])

        assert isinstance(comparison, dict)
        assert len(comparison['strategies']) == 2
        assert comparison['best_strategy'] is not None
        assert comparison['average_score'] > 0
        assert 0 <= comparison['pass_rate'] <= 100

    def test_compare_strategies_empty(self, scorer):
        """测试空列表的策略比较"""
        comparison = scorer.compare_strategies([])
        assert comparison == {}

    def test_backtest_score_to_dict(self, scorer, sample_report):
        """测试评分结果转字典"""
        score_result = scorer.score(sample_report)
        score_dict = score_result.to_dict()

        assert isinstance(score_dict, dict)
        assert 'strategy_name' in score_dict
        assert 'total_score' in score_dict
        assert 'rating' in score_dict
        assert 'dimension_scores' in score_dict
        assert 'metrics' in score_dict

    def test_custom_weights(self, sample_report):
        """测试自定义权重"""
        custom_weights = {
            'return': 0.4,
            'sharpe': 0.3,
            'drawdown': 0.15,
            'stability': 0.10,
            'risk_adjusted': 0.05,
        }

        scorer = BacktestScorer(weights=custom_weights)
        score_result = scorer.score(sample_report)

        # 验证权重已应用
        return_score = next(
            ds for ds in score_result.dimension_scores if ds.name == '收益率'
        )
        assert return_score.weight == 0.4

    def test_invalid_weights(self):
        """测试无效权重"""
        invalid_weights = {
            'return': 0.5,
            'sharpe': 0.5,
            'drawdown': 0.5,  # 总和超过 1.0
        }

        with pytest.raises(ValueError):
            BacktestScorer(weights=invalid_weights)


class TestBacktestReport:
    """测试回测报告数据类"""

    def test_to_dict(self):
        """测试报告转字典"""
        dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
        equity = pd.Series([100 * (1.01 ** i) for i in range(10)], index=dates)

        report = BacktestReport(
            strategy_name="测试",
            initial_capital=100000,
            final_capital=110000,
            equity_curve=equity,
            trades=[],
            daily_returns=equity.pct_change().dropna(),
            start_date=dates[0],
            end_date=dates[-1],
        )

        report_dict = report.to_dict()

        assert report_dict['strategy_name'] == "测试"
        assert report_dict['initial_capital'] == 100000
        assert report_dict['final_capital'] == 110000


class TestDimensionScore:
    """测试维度评分数据类"""

    def test_weighted_score(self):
        """测试加权分数计算"""
        ds = DimensionScore(
            name='测试维度',
            score=80.0,
            weight=0.25,
            description='测试描述',
        )

        weighted = ds.weighted_score()
        assert weighted == 20.0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=src/scoring', '--cov-report=term-missing'])
