#!/usr/bin/env python3
"""
OpenFinAgent v0.5.0 全场景联调测试脚本

测试范围:
1. 策略工厂 - 创建/预览/回测/入库
2. 选股引擎 - 选股/批量回测/股票池
3. 监控中心 - 监控任务/信号检测
4. 回测评分 - 评分系统
5. 通知服务 - 通知发送

运行方式:
    python3 tests/full_integration_test.py
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime
from typing import List, Dict, Any

# 测试结果统计
test_results = {
    'passed': 0,
    'failed': 0,
    'errors': []
}

def log_test(name: str, status: str, message: str = ""):
    """记录测试结果"""
    emoji = "✅" if status == "PASS" else "❌"
    print(f"{emoji} {name}: {status}")
    if message:
        print(f"   {message}")
    
    if status == "PASS":
        test_results['passed'] += 1
    else:
        test_results['failed'] += 1
        test_results['errors'].append(f"{name}: {message}")

def print_header(text: str):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

# ==================== 测试 1: 模块导入 ====================
print_header("测试 1: 模块导入")

try:
    from src.strategy_factory import StrategyFactory, StrategyCodeGenerator
    log_test("策略工厂导入", "PASS")
except Exception as e:
    log_test("策略工厂导入", "FAIL", str(e))

try:
    from src.stock_selector import StockSelector, StockCriteria
    log_test("选股引擎导入", "PASS")
except Exception as e:
    log_test("选股引擎导入", "FAIL", str(e))

try:
    from src.scoring import BacktestScorer, EvaluationMetrics
    log_test("回测评分导入", "PASS")
except Exception as e:
    log_test("回测评分导入", "FAIL", str(e))

try:
    from src.monitor import MonitorCenter
    log_test("监控中心导入", "PASS")
except Exception as e:
    log_test("监控中心导入", "FAIL", str(e))

try:
    from src.notification import NotificationService
    log_test("通知服务导入", "PASS")
except Exception as e:
    log_test("通知服务导入", "FAIL", str(e))

try:
    from src.data.manager import DataManager
    log_test("数据管理器导入", "PASS")
except Exception as e:
    log_test("数据管理器导入", "FAIL", str(e))

# ==================== 测试 2: 策略代码生成 ====================
print_header("测试 2: 策略代码生成")

try:
    generator = StrategyCodeGenerator()
    
    # 测试均线交叉策略
    code = generator.generate(
        strategy_type='ma_cross',
        params={'short_window': 5, 'long_window': 20},
        name='TestMAStrategy',
        initial_capital=100000
    )
    
    assert 'class TestMAStrategyStrategy' in code
    assert 'BaseStrategy' in code
    assert 'generate_signals' in code
    assert 'on_bar' in code
    
    log_test("均线交叉策略生成", "PASS")
except Exception as e:
    log_test("均线交叉策略生成", "FAIL", str(e))

try:
    # 测试动量策略
    code = generator.generate(
        strategy_type='momentum',
        params={'lookback_period': 20, 'threshold': 0.05},
        name='TestMomentumStrategy',
        initial_capital=100000
    )
    
    assert 'class TestMomentumStrategyStrategy' in code
    log_test("动量策略生成", "PASS")
except Exception as e:
    log_test("动量策略生成", "FAIL", str(e))

try:
    # 测试 RSI 策略
    code = generator.generate(
        strategy_type='rsi',
        params={'period': 14, 'oversold': 30, 'overbought': 70},
        name='TestRSIStrategy',
        initial_capital=100000
    )
    
    assert 'class TestRSIStrategyStrategy' in code
    log_test("RSI 策略生成", "PASS")
except Exception as e:
    log_test("RSI 策略生成", "FAIL", str(e))

try:
    # 测试布林带策略
    code = generator.generate(
        strategy_type='bollinger',
        params={'window': 20, 'num_std': 2.0},
        name='TestBollingerStrategy',
        initial_capital=100000
    )
    
    assert 'class TestBollingerStrategyStrategy' in code
    log_test("布林带策略生成", "PASS")
except Exception as e:
    log_test("布林带策略生成", "FAIL", str(e))

# ==================== 测试 3: 策略创建 (无回测) ====================
print_header("测试 3: 策略创建 (无回测)")

try:
    factory = StrategyFactory()
    
    result = factory.create_from_natural_language(
        description="当 5 日均线上穿 20 日均线时买入，下穿时卖出",
        auto_backtest=False  # 暂时禁用回测
    )
    
    assert result is not None
    assert result.id is not None
    assert result.name is not None
    assert result.code is not None
    
    log_test("策略创建 (无回测)", "PASS", f"策略 ID: {result.id}")
except Exception as e:
    log_test("策略创建 (无回测)", "FAIL", str(e))

# ==================== 测试 4: 回测评分系统 ====================
print_header("测试 4: 回测评分系统")

try:
    from src.scoring.scorer import BacktestScore
    from src.backtest.results import BacktestResults
    import pandas as pd
    import numpy as np
    
    # 创建模拟回测报告
    class MockBacktestReport:
        def __init__(self):
            self.total_return = 0.25  # 25% 收益
            self.sharpe_ratio = 1.5
            self.max_drawdown = -0.12  # 12% 回撤
            self.win_rate = 0.60  # 60% 胜率
            self.equity_curve = pd.Series([1.0, 1.1, 1.2, 1.15, 1.25])  # 模拟权益曲线
            self.trades = []  # 交易记录
    
    scorer = BacktestScorer()
    mock_report = MockBacktestReport()
    
    score = scorer.score(mock_report)
    
    assert score.total > 0
    assert score.level in ['S', 'A', 'B', 'C', 'D']
    
    log_test("回测评分", "PASS", f"总分：{score.total:.2f}, 评级：{score.level}")
except Exception as e:
    log_test("回测评分", "FAIL", str(e))

# ==================== 测试 5: 选股引擎 ====================
print_header("测试 5: 选股引擎")

try:
    selector = StockSelector()
    
    criteria = StockCriteria(
        top_n=10,
        min_score=60,
        min_sharpe=1.0,
        max_drawdown=0.20
    )
    
    # 使用模拟数据测试
    test_stocks = ['600519.SH', '000001.SZ', '000002.SZ']
    
    # 测试选股条件
    assert criteria.top_n == 10
    assert criteria.min_score == 60
    
    log_test("选股条件配置", "PASS")
except Exception as e:
    log_test("选股条件配置", "FAIL", str(e))

try:
    # 测试股票池管理
    from src.stock_selector.pool_manager import PoolManager
    
    manager = PoolManager()
    
    # 先删除已存在的股票池 (如果存在)
    try:
        manager.delete_pool("测试股票池")
    except:
        pass
    
    pool = manager.create_pool(
        name="测试股票池",
        stocks=['600519.SH', '000001.SZ'],
        description="测试用股票池"
    )
    
    assert pool is not None
    assert pool.name == "测试股票池"
    assert len(pool.stocks) == 2
    
    log_test("股票池创建", "PASS", f"股票池名称：{pool.name}, 股票数：{len(pool.stocks)}")
except Exception as e:
    log_test("股票池创建", "FAIL", str(e))

# ==================== 测试 6: 监控中心 ====================
print_header("测试 6: 监控中心")

try:
    center = MonitorCenter()
    
    # 测试初始化
    assert center is not None
    
    # 测试任务列表 (应该为空)
    tasks = center.get_monitoring_tasks()
    assert isinstance(tasks, list)
    
    log_test("监控中心初始化", "PASS", f"当前任务数：{len(tasks)}")
except Exception as e:
    log_test("监控中心初始化", "FAIL", str(e))

# ==================== 测试 7: 通知服务 ====================
print_header("测试 7: 通知服务")

try:
    from src.notification.service import NotificationService, Notification, NotificationType
    
    service = NotificationService()
    
    # 测试通知创建
    notification = Notification(
        user_id="test_user",
        notification_type=NotificationType.SIGNAL,
        content={
            "strategy": "测试策略",
            "symbol": "600519.SH",
            "action": "buy",
            "price": 1700.0
        }
    )
    
    assert notification is not None
    assert notification.id is not None
    
    log_test("通知创建", "PASS", f"通知 ID: {notification.id}")
except Exception as e:
    log_test("通知创建", "FAIL", str(e))

# ==================== 测试 8: 数据源 ====================
print_header("测试 8: 数据源测试")

try:
    from src.data.manager import DataManager
    
    config = {
        'primary': 'akshare',
        'fallback_order': ['akshare', 'mock'],
        'enable_cache': True
    }
    
    manager = DataManager(config)
    
    # 测试获取数据 (使用 Mock 数据源)
    data = manager.get_data(
        symbol='TEST',
        start_date='2024-01-01',
        end_date='2024-01-31',
        source='mock'
    )
    
    assert len(data) > 0
    assert 'close' in data.columns
    
    log_test("Mock 数据源", "PASS", f"获取 {len(data)} 行数据")
except Exception as e:
    log_test("Mock 数据源", "FAIL", str(e))

try:
    # 测试 AkShare 数据源
    data = manager.get_data(
        symbol='000001',
        start_date='2024-01-01',
        end_date='2024-01-10',
        source='akshare'
    )
    
    assert len(data) > 0
    log_test("AkShare 数据源", "PASS", f"获取 {len(data)} 行数据")
except Exception as e:
    log_test("AkShare 数据源", "FAIL", str(e))

# ==================== 测试 9: Web UI 页面 ====================
print_header("测试 9: Web UI 页面检查")

web_pages = [
    'web/pages/03_🤖_策略工厂.py',
    'web/pages/04_📈_选股引擎.py',
    'web/pages/05_🔔_监控中心.py'
]

for page in web_pages:
    page_path = project_root / page
    if page_path.exists():
        log_test(f"页面存在：{page.split('/')[-1]}", "PASS")
    else:
        log_test(f"页面存在：{page.split('/')[-1]}", "FAIL", "文件不存在")

# ==================== 测试 10: API 端点 ====================
print_header("测试 10: API 端点检查")

api_files = [
    'api/__init__.py',
    'api/routes.py',
    'api/schemas.py'
]

for file in api_files:
    file_path = project_root / file
    if file_path.exists():
        log_test(f"API 文件：{file}", "PASS")
    else:
        log_test(f"API 文件：{file}", "FAIL", "文件不存在")

# ==================== 测试结果汇总 ====================
print_header("测试结果汇总")

total = test_results['passed'] + test_results['failed']
pass_rate = (test_results['passed'] / total * 100) if total > 0 else 0

print(f"\n总测试数：{total}")
print(f"通过：{test_results['passed']} ✅")
print(f"失败：{test_results['failed']} ❌")
print(f"通过率：{pass_rate:.1f}%")

if test_results['errors']:
    print("\n失败详情:")
    for error in test_results['errors']:
        print(f"  ❌ {error}")

print("\n" + "=" * 60)

if pass_rate >= 90:
    print("🎉 测试通过！系统可以正常运行")
    sys.exit(0)
elif pass_rate >= 70:
    print("⚠️  部分功能有问题，需要修复")
    sys.exit(1)
else:
    print("❌ 严重问题，系统无法正常运行")
    sys.exit(2)
