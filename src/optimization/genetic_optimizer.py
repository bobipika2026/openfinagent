"""
遗传算法优化器模块

基于遗传算法的策略参数优化：
- 种群进化
- 交叉变异
- 适应度函数
- 精英保留策略

@module: optimization.genetic_optimizer
@author: OpenFinAgent Team
@version: 1.0.0
"""

from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass, field
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import logging
from datetime import datetime
import random
import copy

logger = logging.getLogger(__name__)


@dataclass
class Individual:
    """个体 (参数组合)"""
    params: Dict[str, Any]
    fitness: float = 0.0
    metrics: Dict[str, float] = field(default_factory=dict)
    generation: int = 0


@dataclass
class ParameterBound:
    """参数边界定义"""
    name: str
    min_val: Union[int, float]
    max_val: Union[int, float]
    step: Optional[Union[int, float]] = None
    dtype: str = 'float'  # 'int', 'float', 'choice'
    choices: Optional[List[Any]] = None  # 离散选择


class GeneticOptimizer:
    """
    遗传算法优化器

    使用进化算法搜索最优参数组合。
    """

    def __init__(
        self,
        population_size: int = 50,
        generations: int = 100,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.8,
        elite_ratio: float = 0.1,
        optimization_metric: str = 'sharpe_ratio',
        maximize: bool = True,
        n_jobs: int = -1,
        random_seed: Optional[int] = None
    ):
        """
        初始化遗传算法优化器

        Args:
            population_size: 种群大小
            generations: 进化代数
            mutation_rate: 变异率
            crossover_rate: 交叉率
            elite_ratio: 精英保留比例
            optimization_metric: 优化目标指标
            maximize: 是否最大化目标
            n_jobs: 并行工作进程数
            random_seed: 随机种子
        """
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_ratio = elite_ratio
        self.optimization_metric = optimization_metric
        self.maximize = maximize
        self.n_jobs = n_jobs
        self.random_seed = random_seed

        if random_seed is not None:
            np.random.seed(random_seed)
            random.seed(random_seed)

        self.population: List[Individual] = []
        self.best_individual: Optional[Individual] = None
        self.history: List[Dict[str, Any]] = []
        self.all_individuals: List[Individual] = []

        logger.info(
            f"遗传算法优化器初始化：种群={population_size}, "
            f"代数={generations}, 变异率={mutation_rate}"
        )

    def optimize(
        self,
        strategy_class: type,
        parameter_bounds: List[ParameterBound],
        backtest_func: Callable,
        data: pd.DataFrame,
        initial_capital: float = 100000.0,
        show_progress: bool = True
    ) -> Individual:
        """
        执行遗传算法优化

        Args:
            strategy_class: 策略类
            parameter_bounds: 参数边界列表
            backtest_func: 回测函数
            data: 回测数据
            initial_capital: 初始资金
            show_progress: 显示进度

        Returns:
            最优个体
        """
        self.parameter_bounds = {p.name: p for p in parameter_bounds}
        
        # 初始化种群
        logger.info("初始化种群...")
        self.population = self._initialize_population(parameter_bounds)

        # 进化循环
        for gen in range(self.generations):
            # 评估适应度
            self._evaluate_population(
                strategy_class,
                backtest_func,
                data,
                initial_capital
            )

            # 记录最优个体
            self._update_best_individual()

            # 记录历史
            gen_stats = self._get_generation_stats()
            gen_stats['generation'] = gen
            self.history.append(gen_stats)

            if show_progress and gen % 10 == 0:
                logger.info(
                    f"代数 {gen}/{self.generations}: "
                    f"最佳适应度={gen_stats['best_fitness']:.4f}, "
                    f"平均适应度={gen_stats['avg_fitness']:.4f}"
                )

            # 生成下一代
            if gen < self.generations - 1:
                self.population = self._evolve_population()

        # 最终评估
        self._evaluate_population(
            strategy_class,
            backtest_func,
            data,
            initial_capital
        )
        self._update_best_individual()

        logger.info(
            f"优化完成：最佳适应度={self.best_individual.fitness:.4f}, "
            f"参数={self.best_individual.params}"
        )

        return self.best_individual

    def _initialize_population(
        self,
        parameter_bounds: List[ParameterBound]
    ) -> List[Individual]:
        """初始化种群"""
        population = []

        for _ in range(self.population_size):
            params = {}
            for bound in parameter_bounds:
                params[bound.name] = self._random_param(bound)

            individual = Individual(params=params)
            population.append(individual)

        return population

    def _random_param(self, bound: ParameterBound) -> Any:
        """生成随机参数值"""
        if bound.dtype == 'choice' and bound.choices:
            return random.choice(bound.choices)
        elif bound.dtype == 'int':
            if bound.step:
                values = list(range(
                    int(bound.min_val),
                    int(bound.max_val) + 1,
                    int(bound.step)
                ))
                return random.choice(values)
            else:
                return random.randint(int(bound.min_val), int(bound.max_val))
        else:  # float
            if bound.step:
                values = np.arange(bound.min_val, bound.max_val + bound.step, bound.step)
                return random.choice(values)
            else:
                return random.uniform(bound.min_val, bound.max_val)

    def _evaluate_population(
        self,
        strategy_class: type,
        backtest_func: Callable,
        data: pd.DataFrame,
        initial_capital: float
    ):
        """评估种群适应度"""
        n_jobs = self.n_jobs
        if n_jobs == -1:
            import multiprocessing
            n_jobs = multiprocessing.cpu_count()

        with ThreadPoolExecutor(max_workers=min(n_jobs, len(self.population))) as executor:
            futures = []
            for individual in self.population:
                future = executor.submit(
                    self._evaluate_individual,
                    individual,
                    strategy_class,
                    backtest_func,
                    data,
                    initial_capital
                )
                futures.append(future)

            # 等待所有任务完成
            for future in futures:
                try:
                    future.result(timeout=300)
                except Exception as e:
                    logger.warning(f"个体评估失败：{e}")

    def _evaluate_individual(
        self,
        individual: Individual,
        strategy_class: type,
        backtest_func: Callable,
        data: pd.DataFrame,
        initial_capital: float
    ):
        """评估单个个体"""
        try:
            # 创建策略实例
            strategy = strategy_class(**individual.params, initial_capital=initial_capital)
            
            # 执行回测
            result = backtest_func(strategy, data)
            
            # 提取指标
            metrics = result.metrics if hasattr(result, 'metrics') else {}
            individual.metrics = metrics
            
            # 计算适应度
            fitness = metrics.get(self.optimization_metric, 0)
            
            # 如果是最小化问题，取负值
            if not self.maximize:
                fitness = -fitness
            
            individual.fitness = fitness

        except Exception as e:
            logger.debug(f"个体评估失败 {individual.params}: {e}")
            individual.fitness = -np.inf if self.maximize else np.inf

    def _update_best_individual(self):
        """更新最优个体"""
        if not self.population:
            logger.warning("种群为空，无法更新最优个体")
            return

        # 按适应度排序
        sorted_pop = sorted(
            self.population,
            key=lambda x: x.fitness,
            reverse=self.maximize
        )

        current_best = sorted_pop[0]

        # 更新全局最优
        if self.best_individual is None:
            self.best_individual = copy.deepcopy(current_best)
            logger.info(f"初始化最优个体：fitness={current_best.fitness:.4f}, params={current_best.params}")
        elif current_best.fitness > self.best_individual.fitness:
            old_fitness = self.best_individual.fitness
            self.best_individual = copy.deepcopy(current_best)
            logger.info(f"更新最优个体：fitness 从 {old_fitness:.4f} 提升到 {current_best.fitness:.4f}")
        else:
            logger.debug(f"当前代最优 fitness={current_best.fitness:.4f}, 未超过全局最优 {self.best_individual.fitness:.4f}")

        # 记录所有个体
        self.all_individuals.extend(copy.deepcopy(self.population))

    def _get_generation_stats(self) -> Dict[str, float]:
        """获取当前代统计信息"""
        if not self.population:
            return {}

        fitness_values = [i.fitness for i in self.population if np.isfinite(i.fitness)]

        if not fitness_values:
            # 如果所有适应度都是 inf/-inf，仍然返回统计信息
            all_fitness = [i.fitness for i in self.population]
            return {
                'best_fitness': max(all_fitness) if all_fitness else 0.0,
                'avg_fitness': 0.0,  # 无法计算平均值时返回 0
                'min_fitness': min(all_fitness) if all_fitness else 0.0,
                'std_fitness': 0.0
            }

        return {
            'best_fitness': max(fitness_values),
            'avg_fitness': float(np.mean(fitness_values)),  # 确保返回 Python float
            'min_fitness': min(fitness_values),
            'std_fitness': float(np.std(fitness_values))
        }

    def _evolve_population(self) -> List[Individual]:
        """进化新一代"""
        new_population = []

        # 精英保留
        elite_count = int(self.population_size * self.elite_ratio)
        sorted_pop = sorted(
            self.population,
            key=lambda x: x.fitness,
            reverse=self.maximize
        )
        elites = sorted_pop[:elite_count]
        new_population.extend(elites)

        # 生成剩余个体
        while len(new_population) < self.population_size:
            # 选择父母
            parent1 = self._tournament_selection()
            parent2 = self._tournament_selection()

            # 交叉
            if random.random() < self.crossover_rate:
                child1_params, child2_params = self._crossover(parent1.params, parent2.params)
            else:
                child1_params = parent1.params.copy()
                child2_params = parent2.params.copy()

            # 变异
            child1_params = self._mutate(child1_params)
            child2_params = self._mutate(child2_params)

            # 创建新个体
            child1 = Individual(
                params=child1_params,
                generation=sorted_pop[0].generation + 1 if sorted_pop else 1
            )
            child2 = Individual(
                params=child2_params,
                generation=sorted_pop[0].generation + 1 if sorted_pop else 1
            )

            new_population.append(child1)
            if len(new_population) < self.population_size:
                new_population.append(child2)

        return new_population[:self.population_size]

    def _tournament_selection(
        self,
        tournament_size: int = 5
    ) -> Individual:
        """锦标赛选择"""
        candidates = random.sample(self.population, min(tournament_size, len(self.population)))
        return max(candidates, key=lambda x: x.fitness)

    def _crossover(
        self,
        params1: Dict[str, Any],
        params2: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        算术交叉

        对于数值参数，使用加权平均
        """
        child1 = {}
        child2 = {}

        for name in params1.keys():
            bound = self.parameter_bounds.get(name)
            if not bound:
                continue

            val1 = params1[name]
            val2 = params2[name]

            if bound.dtype in ['int', 'float']:
                # 算术交叉
                alpha = random.uniform(0, 1)
                child1[name] = val1 * alpha + val2 * (1 - alpha)
                child2[name] = val1 * (1 - alpha) + val2 * alpha

                # 确保在边界内
                child1[name] = np.clip(child1[name], bound.min_val, bound.max_val)
                child2[name] = np.clip(child2[name], bound.min_val, bound.max_val)

                if bound.dtype == 'int':
                    child1[name] = int(round(child1[name]))
                    child2[name] = int(round(child2[name]))
            else:
                # 离散参数，随机选择一个
                child1[name] = random.choice([val1, val2])
                child2[name] = random.choice([val1, val2])

        return child1, child2

    def _mutate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        变异操作

        对每个参数以一定概率进行变异
        """
        mutated = params.copy()

        for name, value in params.items():
            if random.random() >= self.mutation_rate:
                continue

            bound = self.parameter_bounds.get(name)
            if not bound:
                continue

            if bound.dtype == 'choice' and bound.choices:
                # 离散选择，随机选择一个新值
                other_choices = [c for c in bound.choices if c != value]
                if other_choices:
                    mutated[name] = random.choice(other_choices)
            elif bound.dtype in ['int', 'float']:
                # 数值参数，高斯变异
                std = (bound.max_val - bound.min_val) * 0.1
                delta = np.random.normal(0, std)
                new_value = value + delta

                # 确保在边界内
                new_value = np.clip(new_value, bound.min_val, bound.max_val)

                if bound.dtype == 'int':
                    mutated[name] = int(round(new_value))
                else:
                    mutated[name] = float(new_value)

        return mutated

    def get_best_params(self) -> Dict[str, Any]:
        """获取最优参数"""
        if self.best_individual:
            return self.best_individual.params
        return {}

    def get_history(self) -> pd.DataFrame:
        """获取优化历史"""
        return pd.DataFrame(self.history)

    def export_results(self, filepath: str):
        """导出优化结果"""
        if not self.all_individuals:
            logger.warning("无优化结果可导出")
            return

        rows = []
        for ind in self.all_individuals:
            row = {
                'generation': ind.generation,
                'fitness': ind.fitness
            }
            row.update(ind.params)
            row.update(ind.metrics)
            rows.append(row)

        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        logger.info(f"优化结果已导出：{filepath}")
