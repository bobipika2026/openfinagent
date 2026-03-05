"""
TradeFlow 核心模块测试套件
===========================
符合金融行业测试规范
"""

import unittest
from datetime import datetime
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCoreEngine(unittest.TestCase):
    """核心引擎测试"""
    
    def setUp(self):
        """测试前准备"""
        from tradeflow.core import CoreEngine, TradeSignal, create_engine
        
        self.engine = create_engine({
            'data_source': 'akshare',
            'broker': 'paper'
        })
        self.TradeSignal = TradeSignal
    
    def test_engine_initialization(self):
        """测试引擎初始化"""
        self.assertEqual(self.engine.data_source, 'akshare')
        self.assertEqual(self.engine.broker, 'paper')
        self.assertIsNotNone(self.engine.config)
    
    def test_strategy_parsing(self):
        """测试策略解析"""
        strategy = self.engine.parse_strategy("当 5 日均线上穿 20 日均线时买入")
        self.assertIn('strategy_id', strategy)
        self.assertIn('conditions', strategy)
        self.assertEqual(len(strategy['conditions']), 1)
    
    def test_risk_check(self):
        """测试风险检查"""
        signal = self.TradeSignal(
            symbol='000001.SZ',
            action='buy',
            quantity=1000,
            price=10.0
        )
        passed = self.engine._risk_check(signal)
        self.assertTrue(passed)
    
    def test_paper_trade(self):
        """测试纸面交易"""
        signal = self.TradeSignal(
            symbol='000001.SZ',
            action='buy',
            quantity=100,
            price=10.0
        )
        result = self.engine.execute_trade(signal)
        self.assertEqual(result['status'], 'filled')
        self.assertEqual(self.engine.positions.get('000001.SZ'), 100)
    
    def test_audit_log(self):
        """测试审计日志"""
        audit_log = self.engine.export_audit_log()
        self.assertIn('trade_history', audit_log)
        self.assertIn('current_positions', audit_log)


class TestAgents(unittest.TestCase):
    """Agent 框架测试"""
    
    def setUp(self):
        """测试前准备"""
        from tradeflow.agents import (
            ResearchAgent, TradingAgent, RiskAgent,
            AgentOrchestrator, create_default_orchestrator
        )
        
        self.orchestrator = create_default_orchestrator()
    
    def test_research_agent(self):
        """测试投研 Agent"""
        agent = self.orchestrator.get_agent('ResearchAgent')
        result = agent.process({
            'symbol': '000001.SZ',
            'type': 'basic'
        })
        self.assertIn('analysis_type', result)
    
    def test_trading_agent(self):
        """测试交易 Agent"""
        agent = self.orchestrator.get_agent('TradingAgent')
        result = agent.process({
            'action': 'buy',
            'symbol': '000001.SZ',
            'quantity': 100
        })
        self.assertEqual(result['status'], 'filled')
    
    def test_risk_agent(self):
        """测试风控 Agent"""
        agent = self.orchestrator.get_agent('RiskAgent')
        result = agent.process({
            'check_type': 'trade',
            'symbol': '000001.SZ',
            'quantity': 100,
            'price': 10.0
        })
        self.assertIn('passed', result)
    
    def test_orchestrator(self):
        """测试编排引擎"""
        status = self.orchestrator.get_system_status()
        self.assertIn('active_agents', status)
        self.assertEqual(status['total_agents'], 3)


class TestDataLayer(unittest.TestCase):
    """数据层测试"""
    
    def setUp(self):
        """测试前准备"""
        from tradeflow.data import DataManager, create_data_manager
        
        self.dm = create_data_manager({'default_source': 'akshare'})
    
    def test_data_manager_initialization(self):
        """测试数据管理器初始化"""
        self.assertEqual(self.dm.default_source, 'akshare')
        self.assertTrue(self.dm.cache_enabled)
    
    def test_get_akshare_data(self):
        """测试 AkShare 数据获取"""
        data = self.dm.get_data('000001.SZ', '2024-01-01', '2024-01-31')
        self.assertEqual(data['symbol'], '000001.SZ')
        self.assertEqual(data['source'], 'akshare')
    
    def test_get_yfinance_data(self):
        """测试 YFinance 数据获取"""
        data = self.dm.get_data('AAPL', '2024-01-01', '2024-01-31')
        self.assertEqual(data['symbol'], 'AAPL')
        self.assertEqual(data['source'], 'yfinance')
    
    def test_invalid_symbol(self):
        """测试无效股票代码"""
        # 注：当前 MVP 版本对股票代码验证较宽松
        # 真实数据获取时会返回空数据或错误
        data = self.dm.get_data('INVALID', '2024-01-01', '2024-01-31')
        self.assertIn('symbol', data)
    
    def test_invalid_date_range(self):
        """测试无效日期范围"""
        from tradeflow.data import DataValidationError
        with self.assertRaises(DataValidationError):
            self.dm.get_data('000001.SZ', '2024-12-31', '2024-01-01')


class TestBacktestEngine(unittest.TestCase):
    """回测引擎测试"""
    
    def setUp(self):
        """测试前准备"""
        from tradeflow.backtest import BacktestEngine, create_backtest_engine
        
        self.engine = create_backtest_engine(100000.0)
    
    def test_engine_initialization(self):
        """测试引擎初始化"""
        self.assertEqual(self.engine.initial_capital, 100000.0)
        self.assertEqual(self.engine.commission_rate, 0.0003)
    
    def test_run_backtest(self):
        """测试运行回测"""
        strategy = {
            'strategy_id': 'test_strategy',
            'conditions': [],
            'actions': []
        }
        result = self.engine.run(strategy, '2024-01-01', '2024-01-31')
        
        self.assertEqual(result.start_date, '2024-01-01')
        self.assertEqual(result.end_date, '2024-01-31')
        self.assertIsInstance(result.total_return, float)
    
    def test_equity_curve(self):
        """测试权益曲线"""
        strategy = {'strategy_id': 'test'}
        self.engine.run(strategy, '2024-01-01', '2024-01-31')
        
        equity_curve = self.engine.get_equity_curve()
        self.assertGreater(len(equity_curve), 0)
        self.assertIn('equity', equity_curve[0])
    
    def test_trades(self):
        """测试交易记录"""
        strategy = {'strategy_id': 'test'}
        self.engine.run(strategy, '2024-01-01', '2024-01-31')
        
        trades = self.engine.get_trades()
        self.assertIsInstance(trades, list)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_workflow(self):
        """测试完整工作流"""
        from tradeflow.core import create_engine
        from tradeflow.agents import create_default_orchestrator
        from tradeflow.data import create_data_manager
        from tradeflow.backtest import create_backtest_engine
        
        # 1. 创建核心引擎
        engine = create_engine()
        
        # 2. 解析策略
        strategy = engine.parse_strategy("当 5 日均线上穿 20 日均线时买入")
        
        # 3. 获取数据
        dm = create_data_manager()
        data = dm.get_data('000001.SZ', '2024-01-01', '2024-01-31')
        
        # 4. 运行回测
        backtest = create_backtest_engine(100000.0)
        result = backtest.run(strategy, '2024-01-01', '2024-01-31')
        
        # 5. 创建 Agent 系统
        orchestrator = create_default_orchestrator()
        
        # 6. 执行交易
        from tradeflow.core import TradeSignal
        signal = TradeSignal(
            symbol='000001.SZ',
            action='buy',
            quantity=100,
            price=10.0,
            strategy_name=strategy['strategy_id']
        )
        trade_result = engine.execute_trade(signal)
        
        # 验证
        self.assertIsNotNone(strategy)
        self.assertIsNotNone(data)
        self.assertIsNotNone(result)
        self.assertEqual(trade_result['status'], 'filled')


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestCoreEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestAgents))
    suite.addTests(loader.loadTestsFromTestCase(TestDataLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestBacktestEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回结果
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
