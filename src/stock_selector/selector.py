"""
选股引擎核心类

实现自动化选股、批量回测功能

@module: stock_selector.selector
@author: OpenFinAgent Team
@version: 1.0.0
"""

import logging
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
import pandas as pd
import numpy as np

from .criteria import StockCriteria, StockScore, SelectionMethod, FilterResult
from .pool_manager import PoolManager, StockPool

# 尝试导入依赖模块
try:
    from ..data.manager import DataManager
    from ..backtest.engine import BacktestEngine, load_data
    from ..backtest.results import BacktestResults
    from ..strategy.base import BaseStrategy
except ImportError:
    from data.manager import DataManager
    from backtest.engine import BacktestEngine, load_data
    from backtest.results import BacktestResults
    from strategy.base import BaseStrategy

logger = logging.getLogger(__name__)


@dataclass
class BatchBacktestReport:
    """
    批量回测报告
    
    存储多只股票的回测结果汇总
    
    Attributes:
        strategy_name: 策略名称
        total_stocks: 回测股票总数
        successful_stocks: 成功回测数量
        failed_stocks: 失败回测数量
        results: 个股回测结果字典
        summary_stats: 汇总统计
        top_stocks: 排名靠前的股票
        generated_at: 生成时间
    
    Example:
        ```python
        report = BatchBacktestReport(
            strategy_name='双均线策略',
            total_stocks=100,
            successful_stocks=95,
            failed_stocks=5
        )
        ```
    """
    
    strategy_name: str
    total_stocks: int = 0
    successful_stocks: int = 0
    failed_stocks: int = 0
    results: Dict[str, Any] = field(default_factory=dict)
    summary_stats: Dict[str, Any] = field(default_factory=dict)
    top_stocks: List[StockScore] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_result(
        self,
        symbol: str,
        backtest_result: Optional[BacktestResults],
        error: Optional[str] = None
    ) -> None:
        """
        添加个股回测结果
        
        Args:
            symbol: 股票代码
            backtest_result: 回测结果
            error: 错误信息
        """
        if error:
            self.results[symbol] = {
                'success': False,
                'error': error
            }
            self.failed_stocks += 1
        elif backtest_result:
            self.results[symbol] = {
                'success': True,
                'metrics': backtest_result.metrics,
                'trades': len(backtest_result.trades),
                'final_capital': backtest_result.final_capital
            }
            self.successful_stocks += 1
        
        self.total_stocks += 1
    
    def calculate_summary(self) -> Dict[str, Any]:
        """
        计算汇总统计
        
        Returns:
            汇总统计字典
        """
        if not self.results:
            return {}
        
        # 提取成功的回测结果
        successful_results = [
            r for r in self.results.values()
            if r.get('success', False)
        ]
        
        if not successful_results:
            return {'error': '没有成功的回测结果'}
        
        # 计算各项指标的平均值
        metrics_list = [r['metrics'] for r in successful_results]
        
        # 提取关键指标
        total_returns = []
        sharpe_ratios = []
        max_drawdowns = []
        win_rates = []
        
        for metrics in metrics_list:
            if isinstance(metrics, dict):
                total_returns.append(
                    metrics.get('总收益 (%)', 0) or 0
                )
                sharpe_ratios.append(
                    metrics.get('夏普比率', 0) or 0
                )
                max_drawdowns.append(
                    metrics.get('最大回撤 (%)', 0) or 0
                )
                win_rates.append(
                    metrics.get('胜率 (%)', 0) or 0
                )
        
        # 计算统计值
        self.summary_stats = {
            '成功率': f"{self.successful_stocks / self.total_stocks * 100:.2f}%" if self.total_stocks > 0 else "0%",
            '平均总收益 (%)': np.mean(total_returns) if total_returns else 0,
            '收益中位数 (%)': np.median(total_returns) if total_returns else 0,
            '最佳收益 (%)': max(total_returns) if total_returns else 0,
            '最差收益 (%)': min(total_returns) if total_returns else 0,
            '平均夏普比率': np.mean(sharpe_ratios) if sharpe_ratios else 0,
            '平均最大回撤 (%)': np.mean(max_drawdowns) if max_drawdowns else 0,
            '平均胜率 (%)': np.mean(win_rates) if win_rates else 0,
            '盈利股票数': sum(1 for r in total_returns if r > 0),
            '亏损股票数': sum(1 for r in total_returns if r < 0)
        }
        
        return self.summary_stats
    
    def rank_stocks(
        self,
        by: str = 'total_return',
        top_n: int = 10
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        对股票进行排名
        
        Args:
            by: 排名依据 ('total_return', 'sharpe', 'win_rate')
            top_n: 返回前 N 只
        
        Returns:
            排名列表 [(symbol, metrics), ...]
        """
        successful = [
            (symbol, r['metrics'])
            for symbol, r in self.results.items()
            if r.get('success', False) and r.get('metrics')
        ]
        
        # 定义排序键
        key_map = {
            'total_return': lambda x: x[1].get('总收益 (%)', 0) or 0,
            'sharpe': lambda x: x[1].get('夏普比率', 0) or 0,
            'win_rate': lambda x: x[1].get('胜率 (%)', 0) or 0,
            'min_drawdown': lambda x: -(x[1].get('最大回撤 (%)', 0) or 0)  # 回撤越小越好
        }
        
        key_func = key_map.get(by, key_map['total_return'])
        
        # 排序
        ranked = sorted(successful, key=key_func, reverse=True)
        
        return ranked[:top_n]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'strategy_name': self.strategy_name,
            'total_stocks': self.total_stocks,
            'successful_stocks': self.successful_stocks,
            'failed_stocks': self.failed_stocks,
            'results': self.results,
            'summary_stats': self.summary_stats,
            'top_stocks': [s.to_dict() for s in self.top_stocks],
            'generated_at': self.generated_at
        }
    
    def show(self) -> None:
        """显示回测报告"""
        print("\n" + "=" * 70)
        print(f"📊 批量回测报告 - {self.strategy_name}")
        print("=" * 70)
        print(f"回测股票总数：{self.total_stocks}")
        print(f"成功：{self.successful_stocks}, 失败：{self.failed_stocks}")
        print(f"生成时间：{self.generated_at}")
        print("-" * 70)
        
        if self.summary_stats:
            print("\n📈 汇总统计:")
            for key, value in self.summary_stats.items():
                if isinstance(value, float):
                    print(f"  {key:20} {value:15.2f}")
                else:
                    print(f"  {key:20} {value}")
        
        print("-" * 70)
        
        # 显示前 10 只股票
        top = self.rank_stocks(by='total_return', top_n=10)
        if top:
            print("\n🏆 Top 10 股票:")
            for i, (symbol, metrics) in enumerate(top, 1):
                total_return = metrics.get('总收益 (%)', 0) or 0
                sharpe = metrics.get('夏普比率', 0) or 0
                print(f"  {i:2}. {symbol:12} 收益：{total_return:8.2f}%  夏普：{sharpe:6.2f}")
        
        print("=" * 70)


class StockSelector:
    """
    选股引擎核心类
    
    提供自动化选股、批量回测、股票池管理功能
    
    Attributes:
        data_manager: 数据管理器
        backtest_engine: 回测引擎
        pool_manager: 股票池管理器
    
    Example:
        ```python
        # 初始化选股引擎
        selector = StockSelector()
        
        # 定义选股条件
        criteria = StockCriteria(
            top_n=20,
            min_score=70,
            min_sharpe=1.5,
            max_drawdown=0.15
        )
        
        # 执行选股
        stock_pool = selector.select_stocks(
            strategy=my_strategy,
            stock_pool=['000001.SZ', '000002.SZ'],
            criteria=criteria
        )
        
        # 批量回测
        report = selector.batch_backtest(
            strategy=my_strategy,
            stock_pool=stock_pool.stocks
        )
        ```
    """
    
    def __init__(
        self,
        data_config: Optional[Dict[str, Any]] = None,
        pool_storage_path: Optional[str] = None,
        max_workers: int = 4
    ):
        """
        初始化选股引擎
        
        Args:
            data_config: 数据管理器配置
            pool_storage_path: 股票池存储路径
            max_workers: 最大并发工作线程数
        """
        # 初始化数据管理器
        self.data_manager = DataManager(data_config)
        
        # 初始化回测引擎
        self.backtest_engine = BacktestEngine()
        
        # 初始化股票池管理器
        self.pool_manager = PoolManager(pool_storage_path)
        
        # 并发配置
        self.max_workers = max_workers
        
        # 缓存
        self._score_cache: Dict[str, StockScore] = {}
        
        logger.info(
            f"选股引擎初始化完成，最大并发数：{max_workers}"
        )
    
    def select_stocks(
        self,
        strategy: BaseStrategy,
        stock_pool: List[str],
        criteria: StockCriteria,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        use_cache: bool = True
    ) -> StockPool:
        """
        执行选股
        
        根据给定的策略和条件，从股票池中筛选出符合条件的股票
        
        Args:
            strategy: 交易策略实例
            stock_pool: 待筛选的股票池列表
            criteria: 选股条件
            start_date: 回测开始日期 (默认：1 年前)
            end_date: 回测结束日期 (默认：今天)
            use_cache: 是否使用缓存
        
        Returns:
            筛选后的 StockPool
        
        Raises:
            ValueError: 当参数不合法时
        """
        # 验证条件
        criteria.validate()
        
        # 设置默认日期范围
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        logger.info(
            f"开始选股，策略：{strategy.name}, "
            f"股票池：{len(stock_pool)} 只股票，"
            f"条件：{criteria}"
        )
        
        # 对每只股票进行评分
        scores: List[StockScore] = []
        
        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_symbol = {
                executor.submit(
                    self._evaluate_stock,
                    symbol,
                    strategy,
                    criteria,
                    start_date,
                    end_date,
                    use_cache
                ): symbol
                for symbol in stock_pool
            }
            
            # 收集结果
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    score = future.result()
                    if score:
                        scores.append(score)
                except Exception as e:
                    logger.warning(f"评估股票 {symbol} 失败：{e}")
        
        # 根据选股方法排序
        if criteria.selection_method == SelectionMethod.SCORE_BASED:
            scores.sort(key=lambda x: x.total_score, reverse=True)
        elif criteria.selection_method == SelectionMethod.SHARPE_BASED:
            scores.sort(key=lambda x: x.sharpe_ratio, reverse=True)
        elif criteria.selection_method == SelectionMethod.RETURN_BASED:
            scores.sort(key=lambda x: x.total_return, reverse=True)
        
        # 筛选前 N 只
        selected_scores = scores[:criteria.top_n]
        selected_symbols = [s.symbol for s in selected_scores]
        
        # 创建股票池
        pool_name = f"selected_{strategy.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        selected_pool = self.pool_manager.create_pool(
            name=pool_name,
            stocks=selected_symbols,
            strategy_id=strategy.name,
            description=f"基于 {criteria.selection_method.value} 方法选股，共 {len(selected_symbols)} 只",
            metadata={
                'criteria': criteria.to_dict(),
                'start_date': start_date,
                'end_date': end_date,
                'total_candidates': len(stock_pool),
                'scores': [s.to_dict() for s in selected_scores]
            }
        )
        
        logger.info(
            f"选股完成，从 {len(stock_pool)} 只股票中筛选出 {len(selected_symbols)} 只"
        )
        
        return selected_pool
    
    def batch_backtest(
        self,
        strategy: BaseStrategy,
        stock_pool: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        initial_capital: float = 100000.0,
        show_progress: bool = True
    ) -> BatchBacktestReport:
        """
        批量回测
        
        对多只股票并行执行回测，生成汇总报告
        
        Args:
            strategy: 交易策略实例
            stock_pool: 股票池列表
            start_date: 回测开始日期
            end_date: 回测结束日期
            initial_capital: 初始资金
            show_progress: 显示进度
        
        Returns:
            BatchBacktestReport 回测报告
        
        Example:
            ```python
            report = selector.batch_backtest(
                strategy=strategy,
                stock_pool=['000001.SZ', '000002.SZ'],
                start_date='2023-01-01',
                end_date='2024-01-01'
            )
            
            report.show()
            top_stocks = report.rank_stocks(by='sharpe', top_n=10)
            ```
        """
        # 设置默认日期范围
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        logger.info(
            f"开始批量回测，策略：{strategy.name}, "
            f"股票数：{len(stock_pool)}"
        )
        
        # 创建回测报告
        report = BatchBacktestReport(strategy_name=strategy.name)
        
        # 使用线程池并行回测
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_symbol = {
                executor.submit(
                    self._backtest_single_stock,
                    symbol,
                    strategy,
                    start_date,
                    end_date,
                    initial_capital
                ): symbol
                for symbol in stock_pool
            }
            
            # 收集结果
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    result, error = future.result()
                    report.add_result(symbol, result, error)
                    
                    if show_progress:
                        completed = report.successful_stocks + report.failed_stocks
                        progress = completed / len(stock_pool) * 100
                        logger.debug(
                            f"回测进度：{completed}/{len(stock_pool)} ({progress:.1f}%), "
                            f"成功：{report.successful_stocks}, 失败：{report.failed_stocks}"
                        )
                        
                except Exception as e:
                    logger.error(f"回测股票 {symbol} 异常：{e}")
                    report.add_result(symbol, None, str(e))
        
        # 计算汇总统计
        report.calculate_summary()
        
        # 生成评分并排序
        report.top_stocks = self._generate_scores_from_report(report)
        
        logger.info(
            f"批量回测完成，成功：{report.successful_stocks}, "
            f"失败：{report.failed_stocks}"
        )
        
        return report
    
    def create_pool(
        self,
        name: str,
        stocks: List[str],
        strategy_id: str = "",
        description: str = "",
        tags: Optional[List[str]] = None
    ) -> StockPool:
        """
        创建股票池
        
        Args:
            name: 股票池名称
            stocks: 股票代码列表
            strategy_id: 关联的策略 ID
            description: 描述信息
            tags: 标签列表
        
        Returns:
            创建的 StockPool
        
        Example:
            ```python
            pool = selector.create_pool(
                name='科技龙头',
                stocks=['000001.SZ', '000002.SZ', '600000.SH'],
                strategy_id='momentum_strategy',
                description='科技行业龙头股票',
                tags=['科技', '龙头', '成长']
            )
            ```
        """
        return self.pool_manager.create_pool(
            name=name,
            stocks=stocks,
            strategy_id=strategy_id,
            description=description,
            tags=tags
        )
    
    def get_pool(self, name: str) -> Optional[StockPool]:
        """
        获取股票池
        
        Args:
            name: 股票池名称
        
        Returns:
            StockPool 实例，不存在返回 None
        """
        return self.pool_manager.get_pool(name)
    
    def delete_pool(self, name: str) -> bool:
        """
        删除股票池
        
        Args:
            name: 股票池名称
        
        Returns:
            是否删除成功
        """
        return self.pool_manager.delete_pool(name)
    
    def list_pools(self) -> List[str]:
        """
        列出所有股票池
        
        Returns:
            股票池名称列表
        """
        return self.pool_manager.list_pools()
    
    def export_pool(self, name: str, filepath: str) -> bool:
        """
        导出股票池
        
        Args:
            name: 股票池名称
            filepath: 导出文件路径
        
        Returns:
            是否导出成功
        """
        return self.pool_manager.export_pool(name, filepath)
    
    def import_pool(self, filepath: str, overwrite: bool = False) -> Optional[StockPool]:
        """
        导入股票池
        
        Args:
            filepath: 导入文件路径
            overwrite: 是否覆盖同名股票池
        
        Returns:
            导入的 StockPool，失败返回 None
        """
        return self.pool_manager.import_pool(filepath, overwrite)
    
    def _evaluate_stock(
        self,
        symbol: str,
        strategy: BaseStrategy,
        criteria: StockCriteria,
        start_date: str,
        end_date: str,
        use_cache: bool
    ) -> Optional[StockScore]:
        """
        评估单只股票
        
        Args:
            symbol: 股票代码
            strategy: 策略实例
            criteria: 选股条件
            start_date: 开始日期
            end_date: 结束日期
            use_cache: 是否使用缓存
        
        Returns:
            StockScore 评分，失败返回 None
        """
        # 检查缓存
        cache_key = f"{symbol}:{strategy.name}:{start_date}:{end_date}"
        
        if use_cache and cache_key in self._score_cache:
            logger.debug(f"使用缓存评分：{symbol}")
            return self._score_cache[cache_key]
        
        try:
            # 获取数据
            data = load_data(symbol, start_date, end_date)
            
            if data.empty:
                logger.warning(f"股票 {symbol} 无数据")
                return None
            
            # 运行回测
            strategy.reset()
            result = self.backtest_engine.run(
                strategy=strategy,
                data=data,
                show_progress=False
            )
            
            # 提取指标
            metrics = result.metrics
            
            total_return = metrics.get('总收益 (%)', 0) or 0
            sharpe = metrics.get('夏普比率', 0) or 0
            max_drawdown = metrics.get('最大回撤 (%)', 0) or 0
            win_rate = metrics.get('胜率 (%)', 0) or 0
            annual_return = metrics.get('年化收益 (%)', 0) or 0
            volatility = metrics.get('波动率 (%)', 0) or 0
            
            # 计算综合评分 (0-100)
            score = self._calculate_score(
                total_return=total_return / 100,
                sharpe_ratio=sharpe,
                max_drawdown=max_drawdown / 100,
                win_rate=win_rate / 100,
                annual_return=annual_return / 100,
                volatility=volatility / 100
            )
            
            # 创建评分对象
            stock_score = StockScore(
                symbol=symbol,
                name=symbol,  # TODO: 从数据源获取股票名称
                total_score=score,
                sharpe_ratio=sharpe,
                max_drawdown=max_drawdown / 100,
                total_return=total_return / 100,
                annual_return=annual_return / 100,
                volatility=volatility / 100,
                win_rate=win_rate / 100,
                details={
                    'total_return': total_return,
                    'sharpe': sharpe,
                    'max_drawdown': max_drawdown,
                    'win_rate': win_rate
                }
            )
            
            # 检查是否满足条件
            if not stock_score.meets_criteria(criteria):
                logger.debug(f"股票 {symbol} 不满足选股条件")
                # 仍然返回评分，由上层决定是否筛选
            
            # 缓存结果
            if use_cache:
                self._score_cache[cache_key] = stock_score
            
            return stock_score
            
        except Exception as e:
            logger.warning(f"评估股票 {symbol} 失败：{e}")
            return None
    
    def _calculate_score(
        self,
        total_return: float,
        sharpe_ratio: float,
        max_drawdown: float,
        win_rate: float,
        annual_return: float,
        volatility: float,
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        计算综合评分
        
        Args:
            total_return: 总收益率
            sharpe_ratio: 夏普比率
            max_drawdown: 最大回撤
            win_rate: 胜率
            annual_return: 年化收益率
            volatility: 波动率
            weights: 各项权重 (默认均衡权重)
        
        Returns:
            综合评分 (0-100)
        """
        if weights is None:
            weights = {
                'return': 0.30,      # 收益率权重 30%
                'sharpe': 0.25,      # 夏普比率 25%
                'drawdown': 0.20,    # 回撤控制 20%
                'win_rate': 0.15,    # 胜率 15%
                'stability': 0.10    # 稳定性 10%
            }
        
        # 归一化各项指标到 0-100
        
        # 收益率评分 (假设 100% 收益为满分)
        return_score = min(100, max(0, total_return * 100))
        
        # 夏普比率评分 (假设 3.0 为满分)
        sharpe_score = min(100, max(0, sharpe_ratio / 3.0 * 100))
        
        # 回撤评分 (回撤越小越好，0 回撤为满分)
        drawdown_score = min(100, max(0, (1 - max_drawdown) * 100))
        
        # 胜率评分 (假设 70% 胜率为满分)
        win_rate_score = min(100, max(0, win_rate / 0.7 * 100))
        
        # 稳定性评分 (波动率越小越稳定)
        stability_score = min(100, max(0, (1 - volatility) * 100))
        
        # 加权计算
        total_score = (
            return_score * weights['return'] +
            sharpe_score * weights['sharpe'] +
            drawdown_score * weights['drawdown'] +
            win_rate_score * weights['win_rate'] +
            stability_score * weights['stability']
        )
        
        return round(total_score, 2)
    
    def _backtest_single_stock(
        self,
        symbol: str,
        strategy: BaseStrategy,
        start_date: str,
        end_date: str,
        initial_capital: float
    ) -> Tuple[Optional[BacktestResults], Optional[str]]:
        """
        回测单只股票
        
        Args:
            symbol: 股票代码
            strategy: 策略实例
            start_date: 开始日期
            end_date: 结束日期
            initial_capital: 初始资金
        
        Returns:
            (回测结果，错误信息) 元组
        """
        try:
            # 获取数据
            data = load_data(symbol, start_date, end_date)
            
            if data.empty:
                return None, f"无数据：{symbol}"
            
            # 重置策略
            strategy.reset()
            strategy.initial_capital = initial_capital
            strategy.cash = initial_capital
            
            # 运行回测
            result = self.backtest_engine.run(
                strategy=strategy,
                data=data,
                show_progress=False
            )
            
            return result, None
            
        except Exception as e:
            logger.debug(f"回测股票 {symbol} 失败：{e}")
            return None, str(e)
    
    def _generate_scores_from_report(
        self,
        report: BatchBacktestReport
    ) -> List[StockScore]:
        """
        从回测报告生成评分列表
        
        Args:
            report: 批量回测报告
        
        Returns:
            StockScore 列表
        """
        scores = []
        
        for symbol, result_data in report.results.items():
            if not result_data.get('success', False):
                continue
            
            metrics = result_data.get('metrics', {})
            
            if not metrics:
                continue
            
            total_return = metrics.get('总收益 (%)', 0) or 0
            sharpe = metrics.get('夏普比率', 0) or 0
            max_drawdown = metrics.get('最大回撤 (%)', 0) or 0
            win_rate = metrics.get('胜率 (%)', 0) or 0
            annual_return = metrics.get('年化收益 (%)', 0) or 0
            volatility = metrics.get('波动率 (%)', 0) or 0
            
            score = self._calculate_score(
                total_return=total_return / 100,
                sharpe_ratio=sharpe,
                max_drawdown=max_drawdown / 100,
                win_rate=win_rate / 100,
                annual_return=annual_return / 100,
                volatility=volatility / 100
            )
            
            stock_score = StockScore(
                symbol=symbol,
                name=symbol,
                total_score=score,
                sharpe_ratio=sharpe,
                max_drawdown=max_drawdown / 100,
                total_return=total_return / 100,
                annual_return=annual_return / 100,
                volatility=volatility / 100,
                win_rate=win_rate / 100
            )
            
            scores.append(stock_score)
        
        # 按评分排序
        scores.sort(key=lambda x: x.total_score, reverse=True)
        
        return scores
    
    def clear_cache(self) -> None:
        """清空评分缓存"""
        self._score_cache.clear()
        logger.info("选股引擎缓存已清空")


# 便捷函数
def create_selector(
    data_config: Optional[Dict[str, Any]] = None,
    pool_storage_path: Optional[str] = None,
    max_workers: int = 4
) -> StockSelector:
    """
    创建选股引擎实例
    
    Args:
        data_config: 数据管理器配置
        pool_storage_path: 股票池存储路径
        max_workers: 最大并发数
    
    Returns:
        StockSelector 实例
    """
    return StockSelector(
        data_config=data_config,
        pool_storage_path=pool_storage_path,
        max_workers=max_workers
    )
