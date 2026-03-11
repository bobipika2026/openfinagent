"""
策略工厂核心类 - 自然语言创建策略、自动回测、自动入库

提供以下核心功能:
1. 从自然语言描述创建策略
2. 搜索并创建策略
3. 优化策略参数
4. 自动回测和评分
5. 评分>=60 自动入库到策略商店

作者：OpenFinAgent Team
版本：1.0.0
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import logging
import sys
import importlib.util
import tempfile
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from .generator import StrategyCodeGenerator
from .optimizer import StrategyOptimizer

try:
    from nlp.parser import StrategyParser
    from market.models import Strategy as MarketStrategy, StrategyCategory, StrategyStatus
    from market.service import MarketService
except ImportError:
    from ..nlp.parser import StrategyParser
    from ..market.models import Strategy as MarketStrategy, StrategyCategory, StrategyStatus
    from ..market.service import MarketService

logger = logging.getLogger(__name__)


class StrategyFactory:
    """
    策略工厂核心类
    
    实现自然语言创建策略、自动回测、自动入库功能。
    
    Attributes:
        parser: NLP 解析器
        generator: 代码生成器
        optimizer: 优化器
        market_service: 策略市场服务
        author_id: 作者 ID
        author_name: 作者名称
    """
    
    def __init__(
        self,
        author_id: str = "system",
        author_name: str = "Strategy Factory",
        market_db_path: str = "~/.openfinagent/market.json"
    ):
        """
        初始化策略工厂
        
        Args:
            author_id: 作者 ID
            author_name: 作者名称
            market_db_path: 策略市场数据库路径
        """
        self.parser = StrategyParser()
        self.generator = StrategyCodeGenerator()
        self.optimizer = StrategyOptimizer()
        self.market_service = MarketService(db_path=market_db_path)
        
        self.author_id = author_id
        self.author_name = author_name
        
        logger.info(f"策略工厂初始化完成，作者：{author_name}")
    
    def create_from_natural_language(
        self,
        description: str,
        auto_backtest: bool = True
    ) -> MarketStrategy:
        """
        从自然语言描述创建策略
        
        Args:
            description: 策略自然语言描述
            auto_backtest: 是否自动回测 (默认 True)
        
        Returns:
            创建的策略对象
        
        Raises:
            ValueError: 当描述无法解析或代码生成失败时
            RuntimeError: 当回测或入库失败时
        
        Example:
            >>> factory = StrategyFactory()
            >>> strategy = factory.create_from_natural_language(
            ...     "创建一个 5 日均线上穿 20 日均线的买入策略"
            ... )
        """
        logger.info(f"解析自然语言描述：{description}")
        
        # 1. 解析自然语言
        parsed = self.parser.parse(description)
        strategy_type = parsed['strategy_type']
        params = parsed['params']
        name = parsed['name']
        initial_capital = parsed['initial_capital']
        
        logger.info(
            f"解析结果：类型={strategy_type}, "
            f"参数={params}, 名称={name}"
        )
        
        # 2. 生成策略代码
        code = self.generator.generate(
            strategy_type=strategy_type,
            params=params,
            name=name,
            initial_capital=initial_capital
        )
        
        # 3. 创建策略对象
        strategy = self._create_strategy_object(
            name=name,
            code=code,
            strategy_type=strategy_type,
            params=params,
            initial_capital=initial_capital,
            description=description
        )
        
        # 4. 自动回测
        if auto_backtest:
            backtest_score = self._run_backtest_and_score(strategy)
            strategy.backtest_report['score'] = backtest_score
            strategy.backtest_report['auto_backtest'] = True
            
            logger.info(f"回测评分：{backtest_score}")
            
            # 5. 评分>=60 自动入库
            if backtest_score >= 60:
                strategy.status = StrategyStatus.PUBLISHED
                logger.info(f"评分>=60，自动入库到策略商店")
            else:
                strategy.status = StrategyStatus.DRAFT
                logger.info(f"评分<60，保存为草稿")
        
        # 6. 保存到策略市场
        saved_strategy = self.market_service.upload_strategy(
            name=strategy.name,
            code=strategy.code,
            author_id=self.author_id,
            author_name=self.author_name,
            description=strategy.description,
            config=strategy.config,
            backtest_report=strategy.backtest_report,
            category=strategy.category.value,
            tags=strategy.tags,
            status=strategy.status.value
        )
        
        logger.info(f"策略创建完成：{saved_strategy.name} (ID: {saved_strategy.id})")
        
        return saved_strategy
    
    def search_and_create(
        self,
        topic: str,
        auto_backtest: bool = True
    ) -> List[MarketStrategy]:
        """
        搜索并创建策略
        
        根据主题搜索相关策略模板，创建多个变体策略。
        
        Args:
            topic: 搜索主题 (如"均线交叉"、"动量策略")
            auto_backtest: 是否自动回测 (默认 True)
        
        Returns:
            创建的策略列表
        
        Example:
            >>> factory = StrategyFactory()
            >>> strategies = factory.search_and_create("均线交叉")
        """
        logger.info(f"搜索并创建策略，主题：{topic}")
        
        # 解析主题，确定策略类型
        parsed = self.parser.parse(topic)
        strategy_type = parsed['strategy_type']
        
        # 生成多个参数变体
        param_variants = self._generate_param_variants(strategy_type)
        
        strategies = []
        
        for i, params in enumerate(param_variants):
            try:
                # 生成策略名称
                name = f"{topic}变体{i + 1}"
                
                # 生成代码
                code = self.generator.generate(
                    strategy_type=strategy_type,
                    params=params,
                    name=name,
                    initial_capital=100000.0
                )
                
                # 创建策略对象
                strategy = self._create_strategy_object(
                    name=name,
                    code=code,
                    strategy_type=strategy_type,
                    params=params,
                    initial_capital=100000.0,
                    description=f"基于主题'{topic}'自动生成的策略变体"
                )
                
                # 自动回测
                if auto_backtest:
                    backtest_score = self._run_backtest_and_score(strategy)
                    strategy.backtest_report['score'] = backtest_score
                    
                    if backtest_score >= 60:
                        strategy.status = StrategyStatus.PUBLISHED
                    else:
                        strategy.status = StrategyStatus.DRAFT
                
                # 保存策略
                saved_strategy = self.market_service.upload_strategy(
                    name=strategy.name,
                    code=strategy.code,
                    author_id=self.author_id,
                    author_name=self.author_name,
                    description=strategy.description,
                    config=strategy.config,
                    backtest_report=strategy.backtest_report,
                    category=strategy.category.value,
                    tags=strategy.tags + [topic, 'auto-generated'],
                    status=strategy.status.value
                )
                
                strategies.append(saved_strategy)
                logger.info(f"创建策略变体：{name}, 评分：{backtest_score if auto_backtest else 'N/A'}")
                
            except Exception as e:
                logger.error(f"创建策略变体失败：{e}")
                continue
        
        logger.info(f"共创建 {len(strategies)} 个策略变体")
        
        return strategies
    
    def optimize_strategy(
        self,
        strategy_id: str,
        auto_backtest: bool = True
    ) -> MarketStrategy:
        """
        优化策略参数
        
        使用遗传算法优化策略参数，优化后自动回测验证。
        如果评分提升则更新策略版本。
        
        Args:
            strategy_id: 策略 ID
            auto_backtest: 是否自动回测 (默认 True)
        
        Returns:
            优化后的策略对象
        
        Raises:
            ValueError: 当策略不存在时
            RuntimeError: 当优化失败时
        
        Example:
            >>> factory = StrategyFactory()
            >>> optimized = factory.optimize_strategy("strategy-uuid-xxx")
        """
        logger.info(f"优化策略：{strategy_id}")
        
        # 1. 获取原策略
        original_strategy = self.market_service.get_strategy(strategy_id)
        
        if not original_strategy:
            raise ValueError(f"策略不存在：{strategy_id}")
        
        logger.info(f"原策略：{original_strategy.name}, 版本：{original_strategy.version}")
        
        # 2. 提取策略参数范围
        param_ranges = self._extract_param_ranges(original_strategy)
        
        if not param_ranges:
            raise ValueError("无法提取策略参数范围")
        
        # 3. 定义适应度函数
        def fitness_func(params: Dict[str, Any]) -> float:
            """适应度函数：回测评分"""
            try:
                # 更新策略参数
                temp_strategy = self._create_strategy_object(
                    name=original_strategy.name,
                    code="",  # 会重新生成
                    strategy_type=original_strategy.config.get('strategy_type', 'ma_cross'),
                    params=params,
                    initial_capital=original_strategy.config.get('initial_capital', 100000.0),
                    description=original_strategy.description
                )
                
                # 回测评分
                score = self._run_backtest_and_score(temp_strategy)
                return score
                
            except Exception as e:
                logger.error(f"适应度评估失败：{e}")
                return 0.0
        
        # 4. 执行优化
        original_params = original_strategy.config.get('params', {})
        original_score = original_strategy.backtest_report.get('score', 0)
        
        logger.info(f"原参数：{original_params}, 原评分：{original_score}")
        
        best_params, best_score = self.optimizer.optimize(
            strategy_code=original_strategy.code,
            param_ranges=param_ranges,
            fitness_func=fitness_func,
            initial_params=original_params
        )
        
        logger.info(f"优化后参数：{best_params}, 优化后评分：{best_score}")
        
        # 5. 如果评分提升，更新策略
        if best_score > original_score:
            # 生成新代码
            new_code = self.generator.generate(
                strategy_type=original_strategy.config.get('strategy_type', 'ma_cross'),
                params=best_params,
                name=original_strategy.name,
                initial_capital=original_strategy.config.get('initial_capital', 100000.0)
            )
            
            # 更新策略
            updated_strategy = self.market_service.update_strategy(
                strategy_id=strategy_id,
                author_id=self.author_id,
                code=new_code,
                config={
                    **original_strategy.config,
                    'params': best_params
                },
                tags=original_strategy.tags + ['optimized']
            )
            
            # 更新回测报告
            updated_strategy.backtest_report['score'] = best_score
            updated_strategy.backtest_report['optimized_at'] = datetime.now().isoformat()
            updated_strategy.backtest_report['original_score'] = original_score
            updated_strategy.backtest_report['improvement'] = best_score - original_score
            
            if auto_backtest and best_score >= 60:
                updated_strategy.status = StrategyStatus.PUBLISHED
            
            # 保存更新
            self.market_service._save_data()
            
            logger.info(
                f"策略优化成功，评分提升：{original_score} -> {best_score} "
                f"(+{best_score - original_score:.2f})"
            )
            
            return updated_strategy
        
        else:
            logger.info(f"优化未带来提升，保持原策略")
            return original_strategy
    
    def _create_strategy_object(
        self,
        name: str,
        code: str,
        strategy_type: str,
        params: Dict[str, Any],
        initial_capital: float,
        description: str
    ) -> MarketStrategy:
        """
        创建策略对象
        
        Args:
            name: 策略名称
            code: 策略代码
            strategy_type: 策略类型
            params: 策略参数
            initial_capital: 初始资金
            description: 策略描述
        
        Returns:
            策略对象
        """
        # 映射策略类型到分类
        category_map = {
            'ma_cross': StrategyCategory.OTHER,
            'momentum': StrategyCategory.MOMENTUM,
            'bollinger': StrategyCategory.MEAN_REVERSION,
            'rsi': StrategyCategory.MEAN_REVERSION,
        }
        
        strategy = MarketStrategy(
            name=name,
            description=description,
            author_id=self.author_id,
            author_name=self.author_name,
            code=code,
            config={
                'strategy_type': strategy_type,
                'params': params,
                'initial_capital': initial_capital
            },
            backtest_report={},
            category=category_map.get(strategy_type, StrategyCategory.OTHER),
            tags=[strategy_type, 'auto-generated'],
            status=StrategyStatus.DRAFT
        )
        
        return strategy
    
    def _run_backtest_and_score(self, strategy: MarketStrategy) -> float:
        """
        运行回测并计算评分
        
        Args:
            strategy: 策略对象
        
        Returns:
            回测评分 (0-100)
        
        Raises:
            RuntimeError: 当回测失败时
        """
        try:
            # 动态加载策略代码
            strategy_class = self._load_strategy_class(strategy.code, strategy.name)
            
            # 创建策略实例
            params = strategy.config.get('params', {})
            initial_capital = strategy.config.get('initial_capital', 100000.0)
            
            strategy_instance = strategy_class(
                name=strategy.name,
                initial_capital=initial_capital,
                **params
            )
            
            # 运行回测
            from ..backtest.engine import BacktestEngine, generate_mock_data
            
            # 生成模拟数据 (1 年)
            data = generate_mock_data(
                start_date='2023-01-01',
                end_date='2023-12-31'
            )
            
            engine = BacktestEngine()
            results = engine.run(
                strategy=strategy_instance,
                data=data,
                show_progress=False
            )
            
            # 计算评分
            score = self._calculate_backtest_score(results)
            
            # 保存回测报告
            strategy.backtest_report = {
                'total_return': results.total_return,
                'sharpe_ratio': results.sharpe_ratio,
                'max_drawdown': results.max_drawdown,
                'win_rate': results.win_rate,
                'total_trades': len(results.trades),
                'score': score,
                'backtest_date': datetime.now().isoformat()
            }
            
            return score
            
        except Exception as e:
            logger.error(f"回测失败：{e}", exc_info=True)
            raise RuntimeError(f"回测失败：{e}")
    
    def _load_strategy_class(self, code: str, name: str):
        """
        动态加载策略类
        
        Args:
            code: 策略代码
            name: 策略名称
        
        Returns:
            策略类
        """
        # 创建临时文件
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            # 加载模块
            spec = importlib.util.spec_from_file_location(
                f"strategy_{name.replace(' ', '_').lower()}",
                temp_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 获取策略类 (假设类名与策略名相关)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and attr_name.endswith('Strategy'):
                    return attr
            
            raise ValueError(f"未找到策略类")
            
        finally:
            # 清理临时文件
            os.unlink(temp_path)
    
    def _calculate_backtest_score(self, results) -> float:
        """
        计算回测评分
        
        评分标准:
        - 总收益 (40 分): 基于总收益率
        - 夏普比率 (30 分): 基于风险调整收益
        - 最大回撤 (20 分): 基于最大回撤
        - 胜率 (10 分): 基于交易胜率
        
        Args:
            results: 回测结果对象
        
        Returns:
            综合评分 (0-100)
        """
        score = 0.0
        
        # 总收益评分 (40 分)
        total_return = results.total_return * 100  # 转换为百分比
        return_score = min(40, max(0, total_return * 2))
        score += return_score
        
        # 夏普比率评分 (30 分)
        sharpe = results.sharpe_ratio
        sharpe_score = min(30, max(0, sharpe * 15))
        score += sharpe_score
        
        # 最大回撤评分 (20 分)
        max_dd = abs(results.max_drawdown) * 100  # 转换为百分比
        dd_score = min(20, max(0, 20 - max_dd * 2))
        score += dd_score
        
        # 胜率评分 (10 分)
        win_rate = results.win_rate * 100  # 转换为百分比
        win_score = min(10, max(0, win_rate / 10))
        score += win_score
        
        return min(100, max(0, score))
    
    def _generate_param_variants(
        self,
        strategy_type: str
    ) -> List[Dict[str, Any]]:
        """
        生成参数变体
        
        Args:
            strategy_type: 策略类型
        
        Returns:
            参数变体列表
        """
        variants = []
        
        if strategy_type == 'ma_cross':
            variants = [
                {'short_window': 5, 'long_window': 20},
                {'short_window': 10, 'long_window': 30},
                {'short_window': 5, 'long_window': 30},
                {'short_window': 10, 'long_window': 20},
            ]
        elif strategy_type == 'momentum':
            variants = [
                {'lookback_period': 10, 'threshold': 0.05},
                {'lookback_period': 20, 'threshold': 0.05},
                {'lookback_period': 10, 'threshold': 0.10},
                {'lookback_period': 20, 'threshold': 0.10},
            ]
        elif strategy_type == 'bollinger':
            variants = [
                {'window': 20, 'num_std': 2.0},
                {'window': 20, 'num_std': 2.5},
                {'window': 30, 'num_std': 2.0},
                {'window': 30, 'num_std': 2.5},
            ]
        elif strategy_type == 'rsi':
            variants = [
                {'period': 14, 'oversold': 30, 'overbought': 70},
                {'period': 14, 'oversold': 20, 'overbought': 80},
                {'period': 21, 'oversold': 30, 'overbought': 70},
                {'period': 21, 'oversold': 20, 'overbought': 80},
            ]
        
        return variants
    
    def _extract_param_ranges(
        self,
        strategy: MarketStrategy
    ) -> Dict[str, Tuple[Any, Any]]:
        """
        从策略中提取参数范围
        
        Args:
            strategy: 策略对象
        
        Returns:
            参数范围字典
        """
        strategy_type = strategy.config.get('strategy_type', 'ma_cross')
        params = strategy.config.get('params', {})
        
        ranges = {}
        
        if strategy_type == 'ma_cross':
            ranges = {
                'short_window': (3, 15),
                'long_window': (15, 60),
            }
        elif strategy_type == 'momentum':
            ranges = {
                'lookback_period': (5, 30),
                'threshold': (0.02, 0.15),
            }
        elif strategy_type == 'bollinger':
            ranges = {
                'window': (10, 40),
                'num_std': (1.5, 3.0),
            }
        elif strategy_type == 'rsi':
            ranges = {
                'period': (7, 28),
                'oversold': (20, 40),
                'overbought': (60, 80),
            }
        
        return ranges
