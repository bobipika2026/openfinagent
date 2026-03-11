"""
策略优化器 - 使用遗传算法优化策略参数

功能:
- 遗传算法优化策略参数
- 自动回测验证优化结果
- 如果评分提升则更新策略版本

优化流程:
1. 初始化参数种群
2. 评估每个个体的适应度 (回测评分)
3. 选择、交叉、变异生成新一代
4. 重复直到收敛或达到最大代数
5. 返回最优参数组合

作者：OpenFinAgent Team
版本：1.0.0
"""

from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass
import random
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Individual:
    """
    遗传算法个体
    
    Attributes:
        params: 参数组合
        fitness: 适应度 (回测评分)
    """
    params: Dict[str, Any]
    fitness: float = 0.0


class StrategyOptimizer:
    """
    策略优化器
    
    使用遗传算法优化策略参数，自动回测验证优化结果。
    
    Attributes:
        population_size: 种群大小
        generations: 迭代代数
        mutation_rate: 变异率
        crossover_rate: 交叉率
        elite_size: 精英个体数量
    """
    
    def __init__(
        self,
        population_size: int = 20,
        generations: int = 10,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.7,
        elite_size: int = 2
    ):
        """
        初始化策略优化器
        
        Args:
            population_size: 种群大小 (默认 20)
            generations: 迭代代数 (默认 10)
            mutation_rate: 变异率 (默认 0.1)
            crossover_rate: 交叉率 (默认 0.7)
            elite_size: 精英个体数量 (默认 2)
        """
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = elite_size
        
        logger.info(
            f"策略优化器初始化：种群={population_size}, "
            f"代数={generations}, 变异率={mutation_rate}"
        )
    
    def optimize(
        self,
        strategy_code: str,
        param_ranges: Dict[str, Tuple[Any, Any]],
        fitness_func: Callable[[Dict[str, Any]], float],
        initial_params: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], float]:
        """
        优化策略参数
        
        Args:
            strategy_code: 策略代码
            param_ranges: 参数范围字典 {param_name: (min, max)}
            fitness_func: 适应度函数 (接收参数返回评分)
            initial_params: 初始参数 (可选)
        
        Returns:
            (最优参数，最优评分)
        
        Raises:
            ValueError: 当参数范围不合法时
        """
        if not param_ranges:
            raise ValueError("参数范围不能为空")
        
        logger.info(f"开始优化策略参数：{list(param_ranges.keys())}")
        
        # 初始化种群
        population = self._initialize_population(param_ranges, initial_params)
        
        best_individual = None
        best_fitness = float('-inf')
        
        # 进化迭代
        for generation in range(self.generations):
            # 评估适应度
            for individual in population:
                try:
                    individual.fitness = fitness_func(individual.params)
                except Exception as e:
                    logger.warning(f"评估个体失败：{e}")
                    individual.fitness = 0.0
            
            # 更新最优解
            for individual in population:
                if individual.fitness > best_fitness:
                    best_fitness = individual.fitness
                    best_individual = individual
            
            logger.info(
                f"第 {generation + 1}/{self.generations} 代，"
                f"最优评分：{best_fitness:.2f}"
            )
            
            # 如果已经收敛，提前终止
            if best_fitness >= 100:
                logger.info("已达到最高评分，提前终止优化")
                break
            
            # 生成下一代
            population = self._evolve(population, param_ranges)
        
        if best_individual is None:
            raise RuntimeError("优化失败：未找到有效解")
        
        logger.info(
            f"优化完成，最优参数：{best_individual.params}, "
            f"评分：{best_individual.fitness:.2f}"
        )
        
        return best_individual.params, best_fitness
    
    def _initialize_population(
        self,
        param_ranges: Dict[str, Tuple[Any, Any]],
        initial_params: Optional[Dict[str, Any]] = None
    ) -> List[Individual]:
        """
        初始化种群
        
        Args:
            param_ranges: 参数范围
            initial_params: 初始参数
        
        Returns:
            初始种群
        """
        population = []
        
        # 如果有初始参数，加入种群
        if initial_params:
            population.append(Individual(params=initial_params.copy()))
        
        # 随机生成剩余个体
        while len(population) < self.population_size:
            params = {}
            for param_name, (min_val, max_val) in param_ranges.items():
                if isinstance(min_val, int) and isinstance(max_val, int):
                    params[param_name] = random.randint(min_val, max_val)
                else:
                    params[param_name] = random.uniform(min_val, max_val)
            
            population.append(Individual(params=params))
        
        return population
    
    def _evolve(
        self,
        population: List[Individual],
        param_ranges: Dict[str, Tuple[Any, Any]]
    ) -> List[Individual]:
        """
        进化一代
        
        Args:
            population: 当前种群
            param_ranges: 参数范围
        
        Returns:
            新一代种群
        """
        # 按适应度排序
        population.sort(key=lambda ind: ind.fitness, reverse=True)
        
        new_population = []
        
        # 保留精英
        for i in range(min(self.elite_size, len(population))):
            elite = population[i]
            new_population.append(Individual(
                params=elite.params.copy(),
                fitness=elite.fitness
            ))
        
        # 生成新个体直到填满种群
        while len(new_population) < self.population_size:
            # 选择父代 (锦标赛选择)
            parent1 = self._tournament_selection(population)
            parent2 = self._tournament_selection(population)
            
            # 交叉
            if random.random() < self.crossover_rate:
                child_params = self._crossover(parent1.params, parent2.params)
            else:
                child_params = parent1.params.copy()
            
            # 变异
            child_params = self._mutate(child_params, param_ranges)
            
            new_population.append(Individual(params=child_params))
        
        return new_population
    
    def _tournament_selection(
        self,
        population: List[Individual],
        tournament_size: int = 3
    ) -> Individual:
        """
        锦标赛选择
        
        Args:
            population: 种群
            tournament_size: 锦标赛大小
        
        Returns:
            选中的个体
        """
        tournament = random.sample(population, min(tournament_size, len(population)))
        return max(tournament, key=lambda ind: ind.fitness)
    
    def _crossover(
        self,
        params1: Dict[str, Any],
        params2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        交叉操作
        
        Args:
            params1: 父代 1 参数
            params2: 父代 2 参数
        
        Returns:
            子代参数
        """
        child_params = {}
        
        for key in params1.keys():
            if random.random() < 0.5:
                child_params[key] = params1[key]
            else:
                child_params[key] = params2[key]
        
        return child_params
    
    def _mutate(
        self,
        params: Dict[str, Any],
        param_ranges: Dict[str, Tuple[Any, Any]]
    ) -> Dict[str, Any]:
        """
        变异操作
        
        Args:
            params: 参数
            param_ranges: 参数范围
        
        Returns:
            变异后的参数
        """
        mutated_params = params.copy()
        
        for param_name in params.keys():
            if random.random() < self.mutation_rate:
                min_val, max_val = param_ranges[param_name]
                
                if isinstance(min_val, int) and isinstance(max_val, int):
                    mutated_params[param_name] = random.randint(min_val, max_val)
                else:
                    mutated_params[param_name] = random.uniform(min_val, max_val)
        
        return mutated_params
