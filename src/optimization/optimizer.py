"""
策略优化器模块

提供策略参数优化功能，包括：
- 网格搜索
- 参数敏感性分析
- 最优参数组合推荐
- 过拟合检测

@module: optimization.optimizer
@author: OpenFinAgent Team
@version: 1.0.0
"""

from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from itertools import product
import pandas as pd
import numpy as np
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ParameterRange:
    """参数范围定义"""
    name: str
    values: List[Any]
    step: Optional[float] = None  # 用于连续参数


@dataclass
class OptimizationResult:
    """优化结果"""
    params: Dict[str, Any]
    metrics: Dict[str, float]
    rank: int
    sharpe_ratio: float
    total_return: float
    max_drawdown: float


class StrategyOptimizer:
    """
    策略参数优化器

    支持网格搜索和参数敏感性分析。
    """

    def __init__(
        self,
        optimization_metric: str = 'sharpe_ratio',
        maximize: bool = True,
        n_jobs: int = -1
    ):
        """
        初始化优化器

        Args:
            optimization_metric: 优化目标指标
            maximize: 是否最大化目标 (False 表示最小化)
            n_jobs: 并行工作进程数 (-1 表示使用所有 CPU)
        """
        self.optimization_metric = optimization_metric
        self.maximize = maximize
        self.n_jobs = n_jobs

        self.results: List[OptimizationResult] = []
        self.best_result: Optional[OptimizationResult] = None

        logger.info(
            f"策略优化器初始化：目标={optimization_metric}, "
            f"优化方向={'max' if maximize else 'min'}, n_jobs={n_jobs}"
        )

    def grid_search(
        self,
        strategy_class: type,
        parameter_ranges: List[ParameterRange],
        backtest_func: Callable,
        data: pd.DataFrame,
        initial_capital: float = 100000.0,
        show_progress: bool = True
    ) -> List[OptimizationResult]:
        """
        网格搜索最优参数

        Args:
            strategy_class: 策略类
            parameter_ranges: 参数范围列表
            backtest_func: 回测函数 (接收策略实例和数据，返回结果对象)
            data: 回测数据
            initial_capital: 初始资金
            show_progress: 显示进度

        Returns:
            优化结果列表 (按目标指标排序)
        """
        # 生成所有参数组合
        param_names = [p.name for p in parameter_ranges]
        param_values = [p.values for p in parameter_ranges]
        all_combinations = list(product(*param_values))

        total_combos = len(all_combinations)
        logger.info(f"开始网格搜索：{total_combos} 个参数组合")

        results = []

        # 执行回测
        if self.n_jobs != 1 and total_combos > 10:
            # 并行执行
            results = self._parallel_grid_search(
                strategy_class,
                param_names,
                all_combinations,
                backtest_func,
                data,
                initial_capital,
                show_progress
            )
        else:
            # 串行执行
            results = self._serial_grid_search(
                strategy_class,
                param_names,
                all_combinations,
                backtest_func,
                data,
                initial_capital,
                show_progress
            )

        # 排序结果
        if results:
            reverse = self.maximize
            results.sort(key=lambda x: x.metrics.get(self.optimization_metric, 0), reverse=reverse)

            # 添加排名
            for i, result in enumerate(results):
                result.rank = i + 1

            self.results = results
            self.best_result = results[0] if results else None

            logger.info(
                f"网格搜索完成：最佳参数={self.best_result.params}, "
                f"{self.optimization_metric}={self.best_result.metrics.get(self.optimization_metric, 0):.4f}"
            )

        return results

    def _serial_grid_search(
        self,
        strategy_class: type,
        param_names: List[str],
        combinations: List[Tuple],
        backtest_func: Callable,
        data: pd.DataFrame,
        initial_capital: float,
        show_progress: bool
    ) -> List[OptimizationResult]:
        """串行网格搜索"""
        results = []

        for i, combo in enumerate(combinations):
            params = dict(zip(param_names, combo))

            try:
                # 创建策略实例
                strategy = strategy_class(**params, initial_capital=initial_capital)

                # 执行回测
                result = backtest_func(strategy, data)

                # 提取指标
                metrics = result.metrics if hasattr(result, 'metrics') else {}

                opt_result = OptimizationResult(
                    params=params,
                    metrics=metrics,
                    rank=0,
                    sharpe_ratio=metrics.get('夏普比率', 0),
                    total_return=metrics.get('总收益 (%)', 0),
                    max_drawdown=metrics.get('最大回撤 (%)', 0)
                )
                results.append(opt_result)

                if show_progress and (i + 1) % 10 == 0:
                    logger.info(f"进度：{i + 1}/{len(combinations)}")

            except Exception as e:
                logger.warning(f"参数组合 {params} 回测失败：{e}")
                continue

        return results

    def _parallel_grid_search(
        self,
        strategy_class: type,
        param_names: List[str],
        combinations: List[Tuple],
        backtest_func: Callable,
        data: pd.DataFrame,
        initial_capital: float,
        show_progress: bool
    ) -> List[OptimizationResult]:
        """并行网格搜索"""
        import multiprocessing

        n_workers = multiprocessing.cpu_count() if self.n_jobs == -1 else self.n_jobs
        logger.info(f"使用 {n_workers} 个工作进程并行搜索")

        results = []

        # 使用线程池 (避免进程间数据传输开销)
        with ThreadPoolExecutor(max_workers=n_workers) as executor:
            futures = []

            for combo in combinations:
                params = dict(zip(param_names, combo))
                future = executor.submit(
                    self._backtest_single_combo,
                    strategy_class,
                    params,
                    backtest_func,
                    data,
                    initial_capital
                )
                futures.append((future, params))

            # 收集结果
            for i, (future, params) in enumerate(futures):
                try:
                    result = future.result(timeout=300)  # 5 分钟超时
                    if result:
                        results.append(result)

                    if show_progress and (i + 1) % 10 == 0:
                        logger.info(f"进度：{i + 1}/{len(combinations)}")

                except Exception as e:
                    logger.warning(f"参数组合 {params} 执行失败：{e}")

        return results

    def _backtest_single_combo(
        self,
        strategy_class: type,
        params: Dict[str, Any],
        backtest_func: Callable,
        data: pd.DataFrame,
        initial_capital: float
    ) -> Optional[OptimizationResult]:
        """单个参数组合的回测"""
        try:
            strategy = strategy_class(**params, initial_capital=initial_capital)
            result = backtest_func(strategy, data)

            metrics = result.metrics if hasattr(result, 'metrics') else {}

            return OptimizationResult(
                params=params,
                metrics=metrics,
                rank=0,
                sharpe_ratio=metrics.get('夏普比率', 0),
                total_return=metrics.get('总收益 (%)', 0),
                max_drawdown=metrics.get('最大回撤 (%)', 0)
            )
        except Exception as e:
            logger.debug(f"回测失败 {params}: {e}")
            return None

    def sensitivity_analysis(
        self,
        strategy_class: type,
        base_params: Dict[str, Any],
        parameter_to_vary: str,
        parameter_range: ParameterRange,
        backtest_func: Callable,
        data: pd.DataFrame,
        initial_capital: float = 100000.0
    ) -> pd.DataFrame:
        """
        参数敏感性分析

        Args:
            strategy_class: 策略类
            base_params: 基础参数
            parameter_to_vary: 要变化的参数名
            parameter_range: 参数范围
            backtest_func: 回测函数
            data: 回测数据
            initial_capital: 初始资金

        Returns:
            敏感性分析结果 DataFrame
        """
        logger.info(f"开始参数敏感性分析：{parameter_to_vary}")

        results = []

        for value in parameter_range.values:
            params = base_params.copy()
            params[parameter_to_vary] = value

            try:
                strategy = strategy_class(**params, initial_capital=initial_capital)
                result = backtest_func(strategy, data)

                metrics = result.metrics if hasattr(result, 'metrics') else {}

                results.append({
                    parameter_to_vary: value,
                    'sharpe_ratio': metrics.get('夏普比率', 0),
                    'total_return': metrics.get('总收益 (%)', 0),
                    'max_drawdown': metrics.get('最大回撤 (%)', 0),
                    'win_rate': metrics.get('胜率 (%)', 0),
                    'trade_count': metrics.get('交易次数', 0)
                })

            except Exception as e:
                logger.warning(f"参数值 {value} 回测失败：{e}")
                continue

        df = pd.DataFrame(results)
        return df

    def get_best_params(self) -> Dict[str, Any]:
        """获取最优参数"""
        if self.best_result:
            return self.best_result.params
        return {}

    def get_top_results(self, n: int = 10) -> List[OptimizationResult]:
        """获取前 N 个结果"""
        return self.results[:n]

    def export_results(self, filepath: str):
        """导出优化结果到 CSV"""
        if not self.results:
            logger.warning("无优化结果可导出")
            return

        # 转换为 DataFrame
        rows = []
        for result in self.results:
            row = {'rank': result.rank}
            row.update(result.params)
            row.update(result.metrics)
            rows.append(row)

        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        logger.info(f"优化结果已导出：{filepath}")

    def detect_overfitting(self) -> Dict[str, Any]:
        """
        检测过拟合

        通过分析参数组合的表现分布来判断是否存在过拟合。

        Returns:
            过拟合检测指标
        """
        if len(self.results) < 10:
            return {'reliable': False, 'reason': '样本数量不足'}

        sharpe_ratios = [r.sharpe_ratio for r in self.results]

        # 计算统计指标
        mean_sharpe = np.mean(sharpe_ratios)
        std_sharpe = np.std(sharpe_ratios)
        best_sharpe = max(sharpe_ratios)

        # 过拟合指标
        # 如果最佳值远高于平均值，可能存在过拟合
        overfitting_score = (best_sharpe - mean_sharpe) / std_sharpe if std_sharpe > 0 else 0

        return {
            'reliable': True,
            'mean_sharpe': mean_sharpe,
            'std_sharpe': std_sharpe,
            'best_sharpe': best_sharpe,
            'overfitting_score': overfitting_score,
            'overfitting_warning': overfitting_score > 3,  # 超过 3 倍标准差
            'sample_count': len(self.results)
        }
