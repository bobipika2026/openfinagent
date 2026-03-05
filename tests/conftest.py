"""
Pytest 配置文件
提供共享的 fixtures 和配置
"""

import pytest
from unittest.mock import Mock, MagicMock


@pytest.fixture
def sample_strategy_data():
    """示例策略数据"""
    return {
        "name": "均线交叉策略",
        "description": "当 5 日均线上穿 20 日均线时买入，下穿时卖出",
        "conditions": ["MA5 > MA20"],
        "actions": ["BUY"]
    }


@pytest.fixture
def sample_market_data():
    """示例市场数据"""
    return {
        "symbol": "600519.SH",
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
        "open": [100.0, 101.0, 102.0, 103.0, 104.0],
        "high": [102.0, 103.0, 104.0, 105.0, 106.0],
        "low": [99.0, 100.0, 101.0, 102.0, 103.0],
        "close": [101.0, 102.0, 103.0, 104.0, 105.0],
        "volume": [1000000, 1100000, 1200000, 1300000, 1400000]
    }


@pytest.fixture
def mock_strategy():
    """模拟策略实例"""
    from tradeflow.strategy import Strategy
    return Strategy(name="测试策略")


@pytest.fixture
def mock_analyzer():
    """模拟分析器实例"""
    from tradeflow.analyzer import Analyzer
    return Analyzer()


@pytest.fixture
def mock_executor():
    """模拟执行器实例"""
    from tradeflow.executor import Executor
    return Executor(broker="paper")


@pytest.fixture
def mock_broker_connection():
    """模拟经纪商连接"""
    mock_conn = Mock()
    mock_conn.connect.return_value = True
    mock_conn.buy.return_value = {"order_id": "TEST001", "status": "filled"}
    mock_conn.sell.return_value = {"order_id": "TEST002", "status": "filled"}
    mock_conn.get_positions.return_value = {}
    return mock_conn


@pytest.fixture
def temp_data_dir(tmp_path):
    """临时数据目录"""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def sample_backtest_config():
    """示例回测配置"""
    return {
        "initial_capital": 100000,
        "commission_rate": 0.0003,
        "slippage": 0.001,
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "symbols": ["600519.SH", "000001.SZ"]
    }
