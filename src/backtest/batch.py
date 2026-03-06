"""
批量回测模块

支持：
- 多股票批量回测
- 多策略对比回测
- 参数组合批量回测
- 回测结果汇总分析

@module: backtest.batch
@author: TradeFlow AI Team
@version: 1.0.0
"""

from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class BatchBacktestConfig:
    """批量回测配置"""
    # 股票列表
    symbols: List[str] = field(default_factory=list)

    # 策略配置
    strategy_class: Optional[type] = None
    strategy_params: Dict[str, Any] = field(default_factory=dict)

    # 回测配置
    initial_capital: float = 100000.0
    start_date: str = '2020-01-01'
    end_date: str = '2023-12-31'

    # 数据源配置
    data_source: str = 'akshare'
    data_dir: Optional[str] = None  # 本地数据目录

    # 并行配置
    n_jobs: int = 4
    show_progress: bool = True


@dataclass
class BatchBacktestResult:
    """批量回测结果"""
    symbol: str
    success: bool
    metrics: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    trades_count: int = 0
    backtest_result: Optional[Any] = None  # 原始回测结果


class BatchBacktester:
    """
    批量回测执行器
    """

    def __init__(self, config: Optional[BatchBacktestConfig] = None):
        """
        初始化批量回测器

        Args:
            config: 批量回测配置
        """
        self.config = config or BatchBacktestConfig()
        self.results: List[BatchBacktestResult] = []
        self.summary: Optional[pd.DataFrame] = None

        logger.info("批量回测器初始化完成")

    def run(
        self,
        config: Optional[BatchBacktestConfig] = None,
        load_data_func: Optional[Callable] = None
    ) -> List[BatchBacktestResult]:
        """
        执行批量回测

        Args:
            config: 批量回测配置 (可选，覆盖初始化配置)
            load_data_func: 数据加载函数 (可选)

        Returns:
            批量回测结果列表
        """
        if config:
            self.config = config

        symbols = self.config.symbols
        if not symbols:
            raise ValueError("未指定股票列表")

        logger.info(f"开始批量回测：{len(symbols)} 只股票")

        # 执行回测
        if self.config.n_jobs > 1 and len(symbols) > 5:
            self.results = self._run_parallel(load_data_func)
        else:
            self.results = self._run_serial(load_data_func)

        # 生成汇总
        self._generate_summary()

        return self.results

    def _run_serial(
        self,
        load_data_func: Optional[Callable] = None
    ) -> List[BatchBacktestResult]:
        """串行执行批量回测"""
        results = []

        for i, symbol in enumerate(self.config.symbols):
            logger.info(f"[{i + 1}/{len(self.config.symbols)}] 回测股票：{symbol}")

            try:
                result = self._backtest_single_symbol(
                    symbol,
                    load_data_func
                )
                results.append(result)

            except Exception as e:
                logger.error(f"股票 {symbol} 回测失败：{e}")
                results.append(BatchBacktestResult(
                    symbol=symbol,
                    success=False,
                    error_message=str(e)
                ))

        return results

    def _run_parallel(
        self,
        load_data_func: Optional[Callable] = None
    ) -> List[BatchBacktestResult]:
        """并行执行批量回测"""
        results = []
        n_workers = min(self.config.n_jobs, len(self.config.symbols))

        logger.info(f"使用 {n_workers} 个工作进程并行回测")

        with ThreadPoolExecutor(max_workers=n_workers) as executor:
            future_to_symbol = {
                executor.submit(
                    self._backtest_single_symbol,
                    symbol,
                    load_data_func
                ): symbol
                for symbol in self.config.symbols
            }

            for i, future in enumerate(as_completed(future_to_symbol)):
                symbol = future_to_symbol[future]
                try:
                    result = future.result(timeout=300)  # 5 分钟超时
                    results.append(result)

                    if self.config.show_progress:
                        logger.info(
                            f"[{i + 1}/{len(self.config.symbols)}] "
                            f"完成：{symbol}, 成功={result.success}"
                        )

                except Exception as e:
                    logger.error(f"股票 {symbol} 回测失败：{e}")
                    results.append(BatchBacktestResult(
                        symbol=symbol,
                        success=False,
                        error_message=str(e)
                    ))

        return results

    def _backtest_single_symbol(
        self,
        symbol: str,
        load_data_func: Optional[Callable] = None
    ) -> BatchBacktestResult:
        """
        回测单只股票

        Args:
            symbol: 股票代码
            load_data_func: 数据加载函数

        Returns:
            单只股票回测结果
        """
        try:
            # 加载数据
            if load_data_func:
                data = load_data_func(
                    symbol,
                    self.config.start_date,
                    self.config.end_date
                )
            else:
                # 使用默认加载函数
                from .engine import load_data
                data = load_data(
                    symbol,
                    self.config.start_date,
                    self.config.end_date,
                    self.config.data_source
                )

            if data is None or len(data) == 0:
                return BatchBacktestResult(
                    symbol=symbol,
                    success=False,
                    error_message="无数据"
                )

            # 创建策略
            if self.config.strategy_class is None:
                raise ValueError("未指定策略类")

            strategy = self.config.strategy_class(
                **self.config.strategy_params,
                initial_capital=self.config.initial_capital,
                name=f"{self.config.strategy_class.__name__}_{symbol}"
            )

            # 执行回测
            from .engine import BacktestEngine
            engine = BacktestEngine()
            backtest_result = engine.run(
                strategy,
                data,
                show_progress=False
            )

            # 提取结果
            return BatchBacktestResult(
                symbol=symbol,
                success=True,
                metrics=backtest_result.metrics,
                trades_count=len(backtest_result.trades),
                backtest_result=backtest_result
            )

        except Exception as e:
            logger.error(f"股票 {symbol} 回测异常：{e}", exc_info=True)
            return BatchBacktestResult(
                symbol=symbol,
                success=False,
                error_message=str(e)
            )

    def _generate_summary(self):
        """生成汇总统计"""
        if not self.results:
            return

        # 筛选成功的回测
        successful = [r for r in self.results if r.success]

        if not successful:
            logger.warning("无成功的回测结果")
            return

        # 构建汇总 DataFrame
        rows = []
        for result in successful:
            row = {
                'symbol': result.symbol,
                'trades_count': result.trades_count,
            }
            row.update(result.metrics)
            rows.append(row)

        self.summary = pd.DataFrame(rows)

        # 计算统计指标
        if '总收益 (%)' in self.summary.columns:
            stats = {
                'avg_return': self.summary['总收益 (%)'].mean(),
                'median_return': self.summary['总收益 (%)'].median(),
                'std_return': self.summary['总收益 (%)'].std(),
                'max_return': self.summary['总收益 (%)'].max(),
                'min_return': self.summary['总收益 (%)'].min(),
                'positive_count': (self.summary['总收益 (%)'] > 0).sum(),
                'negative_count': (self.summary['总收益 (%)'] < 0).sum(),
                'win_rate': (self.summary['总收益 (%)'] > 0).mean() * 100
            }

            logger.info("批量回测汇总:")
            logger.info(f"  平均收益：{stats['avg_return']:.2f}%")
            logger.info(f"  中位收益：{stats['median_return']:.2f}%")
            logger.info(f"  胜率：{stats['win_rate']:.2f}%")
            logger.info(f"  成功/总数：{stats['positive_count']}/{len(successful)}")

    def get_summary(self) -> Optional[pd.DataFrame]:
        """获取汇总结果"""
        return self.summary

    def get_top_symbols(self, metric: str = '总收益 (%)', n: int = 10) -> pd.DataFrame:
        """
        获取表现最好的股票

        Args:
            metric: 排序指标
            n: 返回数量

        Returns:
            前 N 只股票的结果
        """
        if self.summary is None:
            return pd.DataFrame()

        return self.summary.nlargest(n, metric)

    def export_results(self, output_dir: str):
        """
        导出回测结果

        Args:
            output_dir: 输出目录
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 导出汇总
        if self.summary is not None:
            summary_path = output_path / 'batch_summary.csv'
            self.summary.to_csv(summary_path, index=False, encoding='utf-8-sig')
            logger.info(f"汇总结果已导出：{summary_path}")

        # 导出详细结果
        for result in self.results:
            if result.success and result.backtest_result:
                symbol_safe = result.symbol.replace('.', '_')
                trades_path = output_path / f'{symbol_safe}_trades.csv'
                result.backtest_result.to_csv(str(trades_path))

        logger.info(f"批量回测结果已导出到：{output_dir}")


class MultiStrategyBacktester:
    """
    多策略对比回测器

    在相同数据上回测多个策略，进行对比分析。
    """

    def __init__(self, initial_capital: float = 100000.0):
        """
        初始化多策略回测器

        Args:
            initial_capital: 初始资金
        """
        self.initial_capital = initial_capital
        self.results: Dict[str, Any] = {}

    def run(
        self,
        strategies: List[Any],
        data: pd.DataFrame,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        运行多策略对比回测

        Args:
            strategies: 策略实例列表
            data: 市场数据
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            策略名称到结果的映射
        """
        from .engine import BacktestEngine

        engine = BacktestEngine()
        results = {}

        for strategy in strategies:
            strategy_name = strategy.name

            logger.info(f"回测策略：{strategy_name}")

            try:
                result = engine.run(
                    strategy,
                    data,
                    start_date=start_date,
                    end_date=end_date,
                    show_progress=False
                )
                results[strategy_name] = result

            except Exception as e:
                logger.error(f"策略 {strategy_name} 回测失败：{e}")
                results[strategy_name] = None

        self.results = results
        return results

    def compare(self) -> pd.DataFrame:
        """
        对比策略表现

        Returns:
            对比结果 DataFrame
        """
        rows = []

        for name, result in self.results.items():
            if result is None:
                continue

            row = {'strategy': name}
            row.update(result.metrics)
            rows.append(row)

        df = pd.DataFrame(rows)
        return df

    def plot_comparison(self, save_path: Optional[str] = None):
        """
        绘制策略对比图

        Args:
            save_path: 保存路径
        """
        try:
            from ..visualization.plotter import StrategyPlotter

            plotter = StrategyPlotter()
            results_list = [r for r in self.results.values() if r is not None]

            if results_list:
                plotter.plot_comparison(results_list, save_path)

        except Exception as e:
            logger.warning(f"无法绘制对比图：{e}")
