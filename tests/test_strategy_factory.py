"""
策略工厂模块测试

测试覆盖率目标：>80%

测试内容:
- StrategyCodeGenerator: 代码生成器测试
- StrategyOptimizer: 优化器测试
- StrategyFactory: 工厂核心类测试

作者：OpenFinAgent Team
版本：1.0.0
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from strategy_factory.generator import StrategyCodeGenerator
from strategy_factory.optimizer import StrategyOptimizer, Individual
from strategy_factory.factory import StrategyFactory


class TestStrategyCodeGenerator:
    """策略代码生成器测试"""
    
    def setup_method(self):
        """测试前 setup"""
        self.generator = StrategyCodeGenerator()
    
    def test_init(self):
        """测试初始化"""
        generator = StrategyCodeGenerator()
        assert len(generator.strategy_templates) == 4
        assert 'ma_cross' in generator.strategy_templates
        assert 'momentum' in generator.strategy_templates
        assert 'bollinger' in generator.strategy_templates
        assert 'rsi' in generator.strategy_templates
    
    def test_generate_ma_cross(self):
        """测试生成均线交叉策略代码"""
        params = {'short_window': 5, 'long_window': 20}
        code = self.generator.generate(
            strategy_type='ma_cross',
            params=params,
            name='测试均线策略',
            initial_capital=100000.0
        )
        
        assert isinstance(code, str)
        assert len(code) > 100
        assert 'class' in code
        assert 'BaseStrategy' in code
        assert 'generate_signals' in code
        assert 'on_bar' in code
        assert 'short_window' in code
        assert 'long_window' in code
    
    def test_generate_momentum(self):
        """测试生成动量策略代码"""
        params = {'lookback_period': 20, 'threshold': 0.05}
        code = self.generator.generate(
            strategy_type='momentum',
            params=params,
            name='测试动量策略',
            initial_capital=100000.0
        )
        
        assert isinstance(code, str)
        assert len(code) > 100
        assert 'lookback_period' in code
        assert 'threshold' in code
        assert 'momentum' in code.lower()
    
    def test_generate_bollinger(self):
        """测试生成布林带策略代码"""
        params = {'window': 20, 'num_std': 2.0}
        code = self.generator.generate(
            strategy_type='bollinger',
            params=params,
            name='测试布林带策略',
            initial_capital=100000.0
        )
        
        assert isinstance(code, str)
        assert len(code) > 100
        assert 'window' in code
        assert 'num_std' in code
        assert 'bollinger' in code.lower() or '布林带' in code
    
    def test_generate_rsi(self):
        """测试生成 RSI 策略代码"""
        params = {'period': 14, 'oversold': 30, 'overbought': 70}
        code = self.generator.generate(
            strategy_type='rsi',
            params=params,
            name='测试 RSI 策略',
            initial_capital=100000.0
        )
        
        assert isinstance(code, str)
        assert len(code) > 100
        assert 'period' in code
        assert 'oversold' in code
        assert 'overbought' in code
        assert 'rsi' in code.lower()
    
    def test_generate_invalid_type(self):
        """测试生成不支持的策略类型"""
        with pytest.raises(ValueError) as exc_info:
            self.generator.generate(
                strategy_type='invalid_type',
                params={},
                name='测试策略',
                initial_capital=100000.0
            )
        
        assert '不支持的策略类型' in str(exc_info.value)
        assert 'ma_cross' in str(exc_info.value)
    
    def test_generate_with_default_params(self):
        """测试使用默认参数生成"""
        code = self.generator.generate(
            strategy_type='ma_cross',
            params={},
            name='默认参数策略',
            initial_capital=100000.0
        )
        
        assert isinstance(code, str)
        assert 'short_window' in code
        assert 'long_window' in code
    
    def test_code_compilation(self):
        """测试生成的代码可以编译"""
        params = {'short_window': 5, 'long_window': 20}
        code = self.generator.generate(
            strategy_type='ma_cross',
            params=params,
            name='编译测试策略',
            initial_capital=100000.0
        )
        
        # 尝试编译代码
        try:
            compile(code, '<string>', 'exec')
            assert True
        except SyntaxError as e:
            pytest.fail(f"生成的代码无法编译：{e}")


class TestStrategyOptimizer:
    """策略优化器测试"""
    
    def setup_method(self):
        """测试前 setup"""
        self.optimizer = StrategyOptimizer(
            population_size=10,
            generations=5,
            mutation_rate=0.1,
            crossover_rate=0.7,
            elite_size=2
        )
    
    def test_init(self):
        """测试初始化"""
        assert self.optimizer.population_size == 10
        assert self.optimizer.generations == 5
        assert self.optimizer.mutation_rate == 0.1
        assert self.optimizer.crossover_rate == 0.7
        assert self.optimizer.elite_size == 2
    
    def test_optimize_simple(self):
        """测试简单优化问题"""
        # 定义简单的适应度函数：f(x) = -(x-5)^2，最大值在 x=5
        def fitness_func(params):
            x = params['x']
            return -(x - 5) ** 2
        
        param_ranges = {'x': (0, 10)}
        
        best_params, best_fitness = self.optimizer.optimize(
            strategy_code="dummy_code",
            param_ranges=param_ranges,
            fitness_func=fitness_func
        )
        
        assert 'x' in best_params
        assert 0 <= best_params['x'] <= 10
        assert best_fitness <= 0  # 最大值为 0
    
    def test_optimize_multi_params(self):
        """测试多参数优化"""
        def fitness_func(params):
            x = params['x']
            y = params['y']
            return -(x - 3) ** 2 - (y - 7) ** 2
        
        param_ranges = {
            'x': (0, 10),
            'y': (0, 10)
        }
        
        best_params, best_fitness = self.optimizer.optimize(
            strategy_code="dummy_code",
            param_ranges=param_ranges,
            fitness_func=fitness_func
        )
        
        assert 'x' in best_params
        assert 'y' in best_params
        assert 0 <= best_params['x'] <= 10
        assert 0 <= best_params['y'] <= 10
    
    def test_optimize_empty_ranges(self):
        """测试空参数范围"""
        with pytest.raises(ValueError) as exc_info:
            self.optimizer.optimize(
                strategy_code="dummy_code",
                param_ranges={},
                fitness_func=lambda x: 0
            )
        
        assert '参数范围不能为空' in str(exc_info.value)
    
    def test_initialize_population(self):
        """测试种群初始化"""
        param_ranges = {
            'x': (0, 10),
            'y': (0, 20)
        }
        
        population = self.optimizer._initialize_population(param_ranges)
        
        assert len(population) == self.optimizer.population_size
        for individual in population:
            assert isinstance(individual, Individual)
            assert 'x' in individual.params
            assert 'y' in individual.params
            assert 0 <= individual.params['x'] <= 10
            assert 0 <= individual.params['y'] <= 20
    
    def test_initialize_population_with_initial(self):
        """测试带初始参数的种群初始化"""
        param_ranges = {'x': (0, 10)}
        initial_params = {'x': 5}
        
        population = self.optimizer._initialize_population(
            param_ranges,
            initial_params
        )
        
        assert len(population) == self.optimizer.population_size
        # 第一个个体应该是初始参数
        assert population[0].params['x'] == 5
    
    def test_tournament_selection(self):
        """测试锦标赛选择"""
        population = [
            Individual(params={'x': 1}, fitness=10),
            Individual(params={'x': 2}, fitness=20),
            Individual(params={'x': 3}, fitness=30),
            Individual(params={'x': 4}, fitness=40),
        ]
        
        selected = self.optimizer._tournament_selection(population)
        
        assert selected in population
        # 锦标赛选择倾向于选择适应度高的个体
        assert selected.fitness >= min(ind.fitness for ind in population)
    
    def test_crossover(self):
        """测试交叉操作"""
        params1 = {'x': 1, 'y': 2, 'z': 3}
        params2 = {'x': 4, 'y': 5, 'z': 6}
        
        child = self.optimizer._crossover(params1, params2)
        
        assert isinstance(child, dict)
        assert len(child) == 3
        # 每个参数应该来自父代之一
        for key in child:
            assert child[key] in [params1[key], params2[key]]
    
    def test_mutate(self):
        """测试变异操作"""
        param_ranges = {'x': (0, 10), 'y': (0, 20)}
        params = {'x': 5, 'y': 10}
        
        mutated = self.optimizer._mutate(params, param_ranges)
        
        assert isinstance(mutated, dict)
        assert 'x' in mutated
        assert 'y' in mutated
        assert 0 <= mutated['x'] <= 10
        assert 0 <= mutated['y'] <= 20
    
    def test_evolve(self):
        """测试进化一代"""
        param_ranges = {'x': (0, 10)}
        population = [
            Individual(params={'x': i}, fitness=float(i))
            for i in range(10)
        ]
        
        new_population = self.optimizer._evolve(population, param_ranges)
        
        assert len(new_population) == self.optimizer.population_size
        # 精英应该被保留
        max_fitness = max(ind.fitness for ind in population)
        new_max_fitness = max(ind.fitness for ind in new_population)
        assert new_max_fitness >= max_fitness - 1  # 允许小幅波动


class TestStrategyFactory:
    """策略工厂核心类测试"""
    
    def setup_method(self):
        """测试前 setup"""
        with patch('strategy_factory.factory.MarketService'):
            self.factory = StrategyFactory(
                author_id='test_user',
                author_name='Test User'
            )
    
    def test_init(self):
        """测试初始化"""
        assert self.factory.author_id == 'test_user'
        assert self.factory.author_name == 'Test User'
        assert self.factory.parser is not None
        assert self.factory.generator is not None
        assert self.factory.optimizer is not None
        assert self.factory.market_service is not None
    
    def test_create_from_natural_language(self):
        """测试从自然语言创建策略"""
        description = "创建一个 5 日均线上穿 20 日均线的买入策略"
        
        with patch.object(self.factory, '_run_backtest_and_score', return_value=75.0):
            with patch.object(self.factory.market_service, 'upload_strategy') as mock_upload:
                mock_upload.return_value = Mock(
                    id='test-strategy-id',
                    name='自定义策略',
                    status=Mock(value='published')
                )
                
                strategy = self.factory.create_from_natural_language(
                    description=description,
                    auto_backtest=True
                )
                
                assert strategy is not None
                mock_upload.assert_called_once()
    
    def test_create_from_natural_language_low_score(self):
        """测试低评分策略保存为草稿"""
        description = "创建一个测试策略"
        
        with patch.object(self.factory, '_run_backtest_and_score', return_value=45.0):
            with patch.object(self.factory.market_service, 'upload_strategy') as mock_upload:
                mock_strategy = Mock()
                mock_strategy.status = Mock()
                mock_upload.return_value = mock_strategy
                
                self.factory.create_from_natural_language(
                    description=description,
                    auto_backtest=True
                )
                
                # 低评分应该保存为草稿
                call_args = mock_upload.call_args
                assert call_args[1]['status'] == 'draft'
    
    def test_search_and_create(self):
        """测试搜索并创建策略"""
        topic = "均线交叉"
        
        with patch.object(self.factory, '_run_backtest_and_score', return_value=70.0):
            with patch.object(self.factory.market_service, 'upload_strategy') as mock_upload:
                mock_upload.return_value = Mock(
                    id='test-strategy-id',
                    name='均线交叉变体 1'
                )
                
                strategies = self.factory.search_and_create(
                    topic=topic,
                    auto_backtest=True
                )
                
                assert isinstance(strategies, list)
                assert len(strategies) > 0
    
    def test_optimize_strategy(self):
        """测试优化策略"""
        strategy_id = 'test-strategy-id'
        
        # Mock 原策略
        mock_original = Mock()
        mock_original.id = strategy_id
        mock_original.name = '测试策略'
        mock_original.version = '1.0.0'
        mock_original.config = {
            'strategy_type': 'ma_cross',
            'params': {'short_window': 5, 'long_window': 20},
            'initial_capital': 100000.0
        }
        mock_original.backtest_report = {'score': 65.0}
        mock_original.tags = ['ma_cross']
        
        with patch.object(self.factory.market_service, 'get_strategy', return_value=mock_original):
            with patch.object(self.factory.optimizer, 'optimize', return_value=(
                {'short_window': 7, 'long_window': 25},
                75.0
            )):
                with patch.object(self.factory.market_service, 'update_strategy') as mock_update:
                    mock_update.return_value = mock_original
                    
                    result = self.factory.optimize_strategy(
                        strategy_id=strategy_id,
                        auto_backtest=True
                    )
                    
                    assert result is not None
    
    def test_optimize_strategy_not_found(self):
        """测试优化不存在的策略"""
        with patch.object(self.factory.market_service, 'get_strategy', return_value=None):
            with pytest.raises(ValueError) as exc_info:
                self.factory.optimize_strategy(
                    strategy_id='non-existent-id',
                    auto_backtest=True
                )
            
            assert '策略不存在' in str(exc_info.value)
    
    def test_calculate_backtest_score(self):
        """测试回测评分计算"""
        mock_results = Mock()
        mock_results.total_return = 0.15  # 15% 收益
        mock_results.sharpe_ratio = 1.5
        mock_results.max_drawdown = -0.10  # 10% 回撤
        mock_results.win_rate = 0.60  # 60% 胜率
        
        score = self.factory._calculate_backtest_score(mock_results)
        
        assert isinstance(score, float)
        assert 0 <= score <= 100
        
        # 收益评分：15 * 2 = 30 分
        # 夏普评分：1.5 * 15 = 22.5 分
        # 回撤评分：20 - 10 * 2 = 0 分 (最低 0 分)
        # 胜率评分：60 / 10 = 6 分
        # 总分：30 + 22.5 + 0 + 6 = 58.5 分
        assert score >= 50  # 至少应该有一定分数
    
    def test_generate_param_variants_ma_cross(self):
        """测试生成均线交叉参数变体"""
        variants = self.factory._generate_param_variants('ma_cross')
        
        assert isinstance(variants, list)
        assert len(variants) > 0
        
        for variant in variants:
            assert 'short_window' in variant
            assert 'long_window' in variant
    
    def test_generate_param_variants_momentum(self):
        """测试生成动量策略参数变体"""
        variants = self.factory._generate_param_variants('momentum')
        
        assert isinstance(variants, list)
        assert len(variants) > 0
        
        for variant in variants:
            assert 'lookback_period' in variant
            assert 'threshold' in variant
    
    def test_generate_param_variants_bollinger(self):
        """测试生成布林带参数变体"""
        variants = self.factory._generate_param_variants('bollinger')
        
        assert isinstance(variants, list)
        assert len(variants) > 0
        
        for variant in variants:
            assert 'window' in variant
            assert 'num_std' in variant
    
    def test_generate_param_variants_rsi(self):
        """测试生成 RSI 参数变体"""
        variants = self.factory._generate_param_variants('rsi')
        
        assert isinstance(variants, list)
        assert len(variants) > 0
        
        for variant in variants:
            assert 'period' in variant
            assert 'oversold' in variant
            assert 'overbought' in variant
    
    def test_extract_param_ranges(self):
        """测试提取参数范围"""
        mock_strategy = Mock()
        mock_strategy.config = {
            'strategy_type': 'ma_cross',
            'params': {'short_window': 5, 'long_window': 20}
        }
        
        ranges = self.factory._extract_param_ranges(mock_strategy)
        
        assert isinstance(ranges, dict)
        assert 'short_window' in ranges
        assert 'long_window' in ranges
        
        # 验证范围
        assert ranges['short_window'] == (3, 15)
        assert ranges['long_window'] == (15, 60)
    
    def test_create_strategy_object(self):
        """测试创建策略对象"""
        strategy = self.factory._create_strategy_object(
            name='测试策略',
            code='print("hello")',
            strategy_type='ma_cross',
            params={'short_window': 5},
            initial_capital=100000.0,
            description='测试描述'
        )
        
        assert strategy.name == '测试策略'
        assert strategy.description == '测试描述'
        assert strategy.author_id == self.factory.author_id
        assert strategy.author_name == self.factory.author_name
        assert strategy.config['strategy_type'] == 'ma_cross'
        assert strategy.config['params'] == {'short_window': 5}
        assert strategy.status.value == 'draft'


class TestIntegration:
    """集成测试"""
    
    def test_full_workflow(self):
        """测试完整工作流程"""
        with patch('strategy_factory.factory.MarketService'):
            factory = StrategyFactory(
                author_id='test_user',
                author_name='Test User'
            )
            
            # 1. 解析自然语言
            description = "创建一个 5 日均线上穿 20 日均线的策略"
            parsed = factory.parser.parse(description)
            
            assert parsed['strategy_type'] == 'ma_cross'
            assert 'short_window' in parsed['params']
            assert 'long_window' in parsed['params']
            
            # 2. 生成代码
            code = factory.generator.generate(
                strategy_type=parsed['strategy_type'],
                params=parsed['params'],
                name=parsed['name'],
                initial_capital=parsed['initial_capital']
            )
            
            assert isinstance(code, str)
            assert len(code) > 100
            
            # 3. 验证代码可编译
            try:
                compile(code, '<string>', 'exec')
                assert True
            except SyntaxError:
                pytest.fail("生成的代码无法编译")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=strategy_factory', '--cov-report=html'])
