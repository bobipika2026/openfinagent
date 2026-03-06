"""
参数热力图可视化模块

支持：
- 双参数扫描热力图
- 最优参数标记
- 多指标可视化
- 交互式图表

@module: visualization.heatmap
@author: OpenFinAgent Team
@version: 1.0.0
"""

from typing import Dict, List, Any, Optional, Tuple, Callable
import pandas as pd
import numpy as np
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class HeatmapResult:
    """热力图结果"""
    param1_name: str
    param2_name: str
    param1_values: List[Any]
    param2_values: List[Any]
    metric_matrix: np.ndarray
    best_param1: Any
    best_param2: Any
    best_metric_value: float


class ParameterHeatmap:
    """
    参数热力图生成器

    用于可视化双参数扫描结果。
    """

    def __init__(
        self,
        metric_name: str = 'sharpe_ratio',
        maximize: bool = True,
        cmap: str = 'RdYlGn'
    ):
        """
        初始化热力图生成器

        Args:
            metric_name: 要可视化的指标名称
            maximize: 是否最大化指标
            cmap: 颜色映射
        """
        self.metric_name = metric_name
        self.maximize = maximize
        self.cmap = cmap

        logger.info(f"参数热力图初始化：指标={metric_name}")

    def scan(
        self,
        strategy_class: type,
        param1_name: str,
        param1_values: List[Any],
        param2_name: str,
        param2_values: List[Any],
        base_params: Dict[str, Any],
        backtest_func: Callable,
        data: pd.DataFrame,
        initial_capital: float = 100000.0,
        show_progress: bool = True
    ) -> HeatmapResult:
        """
        双参数扫描

        Args:
            strategy_class: 策略类
            param1_name: 第一个参数名
            param1_values: 第一个参数值列表
            param2_name: 第二个参数名
            param2_values: 第二个参数值列表
            base_params: 其他固定参数
            backtest_func: 回测函数
            data: 回测数据
            initial_capital: 初始资金
            show_progress: 显示进度

        Returns:
            热力图结果
        """
        logger.info(
            f"开始双参数扫描：{param1_name} x {param2_name}, "
            f"共 {len(param1_values) * len(param2_values)} 个组合"
        )

        n_param1 = len(param1_values)
        n_param2 = len(param2_values)
        
        # 初始化结果矩阵
        metric_matrix = np.full((n_param1, n_param2), np.nan)

        best_value = -np.inf if self.maximize else np.inf
        best_p1 = None
        best_p2 = None

        total = n_param1 * n_param2
        count = 0

        # 执行扫描
        for i, p1_val in enumerate(param1_values):
            for j, p2_val in enumerate(param2_values):
                try:
                    # 构建参数
                    params = base_params.copy()
                    params[param1_name] = p1_val
                    params[param2_name] = p2_val

                    # 创建策略并回测
                    strategy = strategy_class(**params, initial_capital=initial_capital)
                    result = backtest_func(strategy, data)

                    # 提取指标
                    metrics = result.metrics if hasattr(result, 'metrics') else {}
                    metric_value = metrics.get(self.metric_name, 0)

                    metric_matrix[i, j] = metric_value
                    count += 1

                    # 更新最优值
                    if self.maximize:
                        if metric_value > best_value:
                            best_value = metric_value
                            best_p1 = p1_val
                            best_p2 = p2_val
                    else:
                        if metric_value < best_value:
                            best_value = metric_value
                            best_p1 = p1_val
                            best_p2 = p2_val

                    if show_progress and count % 10 == 0:
                        logger.info(f"扫描进度：{count}/{total}")

                except Exception as e:
                    logger.warning(f"参数组合 ({p1_val}, {p2_val}) 回测失败：{e}")
                    metric_matrix[i, j] = np.nan

        logger.info(
            f"扫描完成：最佳 {param1_name}={best_p1}, "
            f"{param2_name}={best_p2}, {self.metric_name}={best_value:.4f}"
        )

        return HeatmapResult(
            param1_name=param1_name,
            param2_name=param2_name,
            param1_values=param1_values,
            param2_values=param2_values,
            metric_matrix=metric_matrix,
            best_param1=best_p1,
            best_param2=best_p2,
            best_metric_value=best_value
        )

    def plot(
        self,
        result: HeatmapResult,
        figsize: Tuple[int, int] = (10, 8),
        title: Optional[str] = None,
        annotate: bool = True,
        save_path: Optional[str] = None,
        show: bool = True
    ):
        """
        绘制热力图

        Args:
            result: 热力图结果
            figsize: 图像大小
            title: 标题
            annotate: 是否标注数值
            save_path: 保存路径
            show: 是否显示
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')  # 非交互式后端
        except ImportError:
            logger.error("matplotlib 未安装，请运行：pip install matplotlib")
            raise

        fig, ax = plt.subplots(figsize=figsize)

        # 创建热力图
        im = ax.imshow(
            result.metric_matrix,
            cmap=self.cmap,
            aspect='auto',
            origin='lower'
        )

        # 设置坐标轴
        ax.set_xlabel(result.param2_name)
        ax.set_ylabel(result.param1_name)

        # 设置刻度标签
        ax.set_xticks(range(len(result.param2_values)))
        ax.set_yticks(range(len(result.param1_values)))
        ax.set_xticklabels([str(v) for v in result.param2_values])
        ax.set_yticklabels([str(v) for v in result.param1_values])

        # 旋转 x 轴标签
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        # 添加颜色条
        cbar = ax.figure.colorbar(im)
        cbar.ax.set_ylabel(self.metric_name, rotation=-90, va="bottom")

        # 标注最优参数位置
        if result.best_param1 is not None and result.best_param2 is not None:
            try:
                best_i = result.param1_values.index(result.best_param1)
                best_j = result.param2_values.index(result.best_param2)
                
                ax.plot(best_j, best_i, 'X', markersize=20, 
                       markeredgecolor='white', markeredgewidth=2,
                       markerfacecolor='red', label='最优参数')
                ax.legend(loc='upper right')
            except ValueError:
                logger.warning("无法标记最优参数位置")

        # 添加数值标注
        if annotate:
            for i in range(len(result.param1_values)):
                for j in range(len(result.param2_values)):
                    value = result.metric_matrix[i, j]
                    if np.isfinite(value):
                        text = ax.text(
                            j, i, f'{value:.2f}',
                            ha='center', va='center',
                            color='black', fontsize=8
                        )

        # 设置标题
        if title:
            ax.set_title(title)
        else:
            ax.set_title(
                f'{result.param1_name} vs {result.param2_name} - {self.metric_name}'
            )

        plt.tight_layout()

        # 保存图像
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            logger.info(f"热力图已保存：{save_path}")

        if show:
            plt.show()
        else:
            plt.close()

    def plot_contour(
        self,
        result: HeatmapResult,
        figsize: Tuple[int, int] = (10, 8),
        levels: int = 20,
        title: Optional[str] = None,
        save_path: Optional[str] = None,
        show: bool = True
    ):
        """
        绘制等高线图

        Args:
            result: 热力图结果
            figsize: 图像大小
            levels: 等高线级别数
            title: 标题
            save_path: 保存路径
            show: 是否显示
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')
        except ImportError:
            logger.error("matplotlib 未安装")
            raise

        fig, ax = plt.subplots(figsize=figsize)

        # 创建网格
        X, Y = np.meshgrid(
            range(len(result.param2_values)),
            range(len(result.param1_values))
        )

        # 绘制等高线
        contour = ax.contourf(
            X, Y, result.metric_matrix,
            levels=levels, cmap=self.cmap
        )

        # 添加等高线
        ax.contour(
            X, Y, result.metric_matrix,
            levels=levels, colors='black',
            linewidths=0.5, alpha=0.5
        )

        # 设置坐标轴
        ax.set_xlabel(result.param2_name)
        ax.set_ylabel(result.param1_name)
        ax.set_xticks(range(len(result.param2_values)))
        ax.set_yticks(range(len(result.param1_values)))
        ax.set_xticklabels([str(v) for v in result.param2_values])
        ax.set_yticklabels([str(v) for v in result.param1_values])

        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        # 添加颜色条
        cbar = ax.figure.colorbar(contour)
        cbar.ax.set_ylabel(self.metric_name, rotation=-90, va="bottom")

        # 标记最优参数
        if result.best_param1 is not None and result.best_param2 is not None:
            try:
                best_i = result.param1_values.index(result.best_param1)
                best_j = result.param2_values.index(result.best_param2)
                ax.plot(best_j, best_i, 'X', markersize=15,
                       markeredgecolor='white', markeredgewidth=2,
                       markerfacecolor='red')
            except ValueError:
                pass

        if title:
            ax.set_title(title)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            logger.info(f"等高线图已保存：{save_path}")

        if show:
            plt.show()
        else:
            plt.close()

    def create_interactive(
        self,
        result: HeatmapResult,
        title: Optional[str] = None
    ):
        """
        创建交互式热力图 (使用 plotly)

        Args:
            result: 热力图结果
            title: 标题

        Returns:
            plotly Figure 对象
        """
        try:
            import plotly.graph_objects as go
        except ImportError:
            logger.error("plotly 未安装，请运行：pip install plotly")
            raise

        # 创建热力图
        fig = go.Figure(data=go.Heatmap(
            z=result.metric_matrix,
            x=[str(v) for v in result.param2_values],
            y=[str(v) for v in result.param1_values],
            colorscale=self.cmap,
            colorbar=dict(title=self.metric_name)
        ))

        # 标记最优参数
        if result.best_param1 is not None and result.best_param2 is not None:
            fig.add_trace(go.Scatter(
                x=[str(result.best_param2)],
                y=[str(result.best_param1)],
                mode='markers',
                marker=dict(
                    symbol='x',
                    size=15,
                    color='red',
                    line=dict(color='white', width=2)
                ),
                name='最优参数'
            ))

        # 设置布局
        fig.update_layout(
            title=title or f'{result.param1_name} vs {result.param2_name}',
            xaxis_title=result.param2_name,
            yaxis_title=result.param1_name,
            width=800,
            height=600
        )

        return fig


def parameter_sweep(
    strategy_class: type,
    param1_name: str,
    param1_range: List[Any],
    param2_name: str,
    param2_range: List[Any],
    base_params: Dict[str, Any],
    backtest_func: Callable,
    data: pd.DataFrame,
    metric_name: str = 'sharpe_ratio',
    initial_capital: float = 100000.0
) -> HeatmapResult:
    """
    便捷函数：执行参数扫描

    Args:
        strategy_class: 策略类
        param1_name: 第一个参数名
        param1_range: 第一个参数范围
        param2_name: 第二个参数名
        param2_range: 第二个参数范围
        base_params: 其他固定参数
        backtest_func: 回测函数
        data: 回测数据
        metric_name: 目标指标
        initial_capital: 初始资金

    Returns:
        热力图结果
    """
    scanner = ParameterHeatmap(metric_name=metric_name)
    return scanner.scan(
        strategy_class=strategy_class,
        param1_name=param1_name,
        param1_values=param1_range,
        param2_name=param2_name,
        param2_values=param2_range,
        base_params=base_params,
        backtest_func=backtest_func,
        data=data,
        initial_capital=initial_capital
    )
