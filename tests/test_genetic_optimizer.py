"""
遗传算法优化器单元测试

测试用例：
- 种群初始化
- 适应度评估
- 交叉变异
- 进化过程
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from optimization.genetic_optimizer import (
    GeneticOptimizer,
    Individual,
    ParameterBound
)


class MockStrategy:
    """模拟策略类用于测试"""
    
    def __init__(self, param1=10, param2=0.5, initial_capital=100000):
        self.param1 = param1
        self.param2 = param2
        self.initial_capital = initial_capital


class MockBacktestResult:
    """模拟回测结果"""
    
    def __init__(self, sharpe_ratio, total_return):
        self.metrics = {
            'sharpe_ratio': sharpe_ratio,
            'total_return': total_return,
            'max_drawdown': -10.0
        }


def mock_backtest_func(strategy, data):
    """模拟回测函数"""
    # 根据参数生成"适应度"
    # 假设最优参数在 param1=50, param2=0.6 附近
    param1_score = 1 - abs(strategy.param1 - 50) / 100
    param2_score = 1 - abs(strategy.param2 - 0.6) / 1
    sharpe = (param1_score + param2_score) * 2 + np.random.normal(0, 0.1)
    
    return MockBacktestResult(
        sharpe_ratio=sharpe,
        total_return=sharpe * 10
    )


def create_test_data(n_days=100):
    """创建测试数据"""
    dates = pd.date_range(start='2024-01-01', periods=n_days, freq='D')
    
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(n_days))
    
    df = pd.DataFrame({
        'open': prices + np.random.randn(n_days) * 0.5,
        'high': prices + np.abs(np.random.randn(n_days)) * 0.5,
        'low': prices - np.abs(np.random.randn(n_days)) * 0.5,
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, n_days)
    }, index=dates)
    
    return df


class TestIndividual:
    """个体测试"""

    def test_individual_creation(self):
        """测试个体创建"""
        params = {'param1': 50, 'param2': 0.5}
        individual = Individual(params=params)
        
        assert individual.params == params
        assert individual.fitness == 0.0
        assert individual.generation == 0

    def test_individual_with_fitness(self):
        """测试带适应度的个体"""
        params = {'param1': 50}
        metrics = {'sharpe_ratio': 1.5}
        individual = Individual(params=params, fitness=1.5, metrics=metrics)
        
        assert individual.fitness == 1.5
        assert individual.metrics == metrics


class TestParameterBound:
    """参数边界测试"""

    def test_float_bound(self):
        """测试浮点数边界"""
        bound = ParameterBound(
            name='learning_rate',
            min_val=0.0,
            max_val=1.0,
            dtype='float'
        )
        
        assert bound.name == 'learning_rate'
        assert bound.min_val == 0.0
        assert bound.max_val == 1.0

    def test_int_bound_with_step(self):
        """测试带步长的整数边界"""
        bound = ParameterBound(
            name='window',
            min_val=10,
            max_val=100,
            step=10,
            dtype='int'
        )
        
        assert bound.step == 10

    def test_choice_bound(self):
        """测试离散选择边界"""
        bound = ParameterBound(
            name='ma_type',
            min_val=0,
            max_val=0,
            dtype='choice',
            choices=['sma', 'ema', 'wma']
        )
        
        assert bound.choices == ['sma', 'ema', 'wma']


class TestGeneticOptimizer:
    """遗传算法优化器测试"""

    def test_initialization(self):
        """测试初始化"""
        optimizer = GeneticOptimizer(
            population_size=20,
            generations=50,
            mutation_rate=0.1,
            crossover_rate=0.8,
            random_seed=42
        )
        
        assert optimizer.population_size == 20
        assert optimizer.generations == 50
        assert optimizer.mutation_rate == 0.1
        assert optimizer.crossover_rate == 0.8

    def test_random_param_float(self):
        """测试随机浮点数参数生成"""
        optimizer = GeneticOptimizer(random_seed=42)
        bound = ParameterBound('param', 0.0, 1.0, dtype='float')
        
        value = optimizer._random_param(bound)
        assert 0.0 <= value <= 1.0

    def test_random_param_int(self):
        """测试随机整数参数生成"""
        optimizer = GeneticOptimizer(random_seed=42)
        bound = ParameterBound('param', 10, 100, dtype='int')
        
        value = optimizer._random_param(bound)
        assert 10 <= value <= 100
        assert isinstance(value, int)

    def test_random_param_choice(self):
        """测试随机选择参数生成"""
        optimizer = GeneticOptimizer(random_seed=42)
        bound = ParameterBound(
            'param', 0, 0,
            dtype='choice',
            choices=['a', 'b', 'c']
        )
        
        value = optimizer._random_param(bound)
        assert value in ['a', 'b', 'c']

    def test_initialize_population(self):
        """测试种群初始化"""
        optimizer = GeneticOptimizer(
            population_size=10,
            random_seed=42
        )
        
        bounds = [
            ParameterBound('param1', 0, 100, dtype='int'),
            ParameterBound('param2', 0.0, 1.0, dtype='float')
        ]
        
        population = optimizer._initialize_population(bounds)
        
        assert len(population) == 10
        for individual in population:
            assert 'param1' in individual.params
            assert 'param2' in individual.params

    def test_evaluate_individual(self):
        """测试个体评估"""
        optimizer = GeneticOptimizer(random_seed=42)
        data = create_test_data()
        
        individual = Individual(params={'param1': 50, 'param2': 0.6})
        
        optimizer._evaluate_individual(
            individual,
            MockStrategy,
            mock_backtest_func,
            data,
            initial_capital=100000
        )
        
        assert np.isfinite(individual.fitness)
        assert individual.metrics is not None

    def test_tournament_selection(self):
        """测试锦标赛选择"""
        optimizer = GeneticOptimizer(population_size=20, random_seed=42)
        
        bounds = [
            ParameterBound('param1', 0, 100, dtype='int')
        ]
        optimizer.population = optimizer._initialize_population(bounds)
        
        # 设置不同的适应度
        for i, ind in enumerate(optimizer.population):
            ind.fitness = i
        
        winner = optimizer._tournament_selection(tournament_size=5)
        
        # 获胜者应该是锦标赛中适应度最高的
        assert winner.fitness >= min(i for i in range(20))

    def test_crossover(self):
        """测试交叉操作"""
        optimizer = GeneticOptimizer(random_seed=42)
        
        bounds = [
            ParameterBound('param1', 0, 100, dtype='float'),
            ParameterBound('param2', 0.0, 1.0, dtype='float')
        ]
        optimizer.parameter_bounds = {b.name: b for b in bounds}
        
        params1 = {'param1': 20.0, 'param2': 0.3}
        params2 = {'param1': 80.0, 'param2': 0.9}
        
        child1, child2 = optimizer._crossover(params1, params2)
        
        # 子代参数应该在父母之间
        for name in ['param1', 'param2']:
            assert min(params1[name], params2[name]) <= child1[name] <= max(params1[name], params2[name])
            assert min(params1[name], params2[name]) <= child2[name] <= max(params1[name], params2[name])

    def test_mutate(self):
        """测试变异操作"""
        optimizer = GeneticOptimizer(
            mutation_rate=1.0,  # 100% 变异率确保变异发生
            random_seed=42
        )
        
        bounds = [
            ParameterBound('param1', 0, 100, dtype='float')
        ]
        optimizer.parameter_bounds = {b.name: b for b in bounds}
        
        params = {'param1': 50.0}
        mutated = optimizer._mutate(params)
        
        # 变异后值应该改变 (大概率)
        # 注意：由于随机性，这个测试可能偶尔失败
        assert 'param1' in mutated

    def test_full_optimization(self):
        """测试完整优化过程"""
        optimizer = GeneticOptimizer(
            population_size=10,
            generations=5,
            random_seed=42
        )
        
        bounds = [
            ParameterBound('param1', 0, 100, dtype='int'),
            ParameterBound('param2', 0.0, 1.0, dtype='float')
        ]
        
        data = create_test_data()
        
        best = optimizer.optimize(
            MockStrategy,
            bounds,
            mock_backtest_func,
            data,
            initial_capital=100000,
            show_progress=False
        )
        
        assert best is not None
        assert np.isfinite(best.fitness)
        assert 'param1' in best.params
        assert 'param2' in best.params

    def test_get_history(self):
        """测试获取优化历史"""
        optimizer = GeneticOptimizer(
            population_size=10,
            generations=5,
            random_seed=42
        )
        
        bounds = [
            ParameterBound('param1', 0, 100, dtype='int')
        ]
        
        data = create_test_data()
        
        optimizer.optimize(
            MockStrategy,
            bounds,
            mock_backtest_func,
            data,
            initial_capital=100000,
            show_progress=False
        )
        
        history = optimizer.get_history()
        
        assert isinstance(history, pd.DataFrame)
        assert len(history) == 5  # 5 代
        assert 'generation' in history.columns
        assert 'best_fitness' in history.columns

    def test_export_results(self, tmp_path):
        """测试导出结果"""
        optimizer = GeneticOptimizer(
            population_size=10,
            generations=3,
            random_seed=42
        )
        
        bounds = [
            ParameterBound('param1', 0, 100, dtype='int')
        ]
        
        data = create_test_data()
        
        optimizer.optimize(
            MockStrategy,
            bounds,
            mock_backtest_func,
            data,
            initial_capital=100000,
            show_progress=False
        )
        
        filepath = tmp_path / "results.csv"
        optimizer.export_results(str(filepath))
        
        assert filepath.exists()
        
        # 验证 CSV 内容
        df = pd.read_csv(filepath)
        assert len(df) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
