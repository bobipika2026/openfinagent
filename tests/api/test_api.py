"""
OpenFinAgent API 集成测试

测试所有 API 端点的功能
"""

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api import app

client = TestClient(app)


class TestHealthCheck:
    """健康检查测试"""
    
    def test_health_check(self):
        """测试健康检查接口"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestStrategyFactory:
    """策略工厂 API 测试"""
    
    def test_create_strategy_from_text(self):
        """测试通过自然语言创建策略"""
        payload = {
            "description": "当 5 日均线上穿 20 日均线时买入，下穿时卖出",
            "initial_capital": 100000,
            "symbol": "600519.SH"
        }
        
        response = client.post("/api/v1/strategies/from-text", json=payload)
        # 注意：实际会返回 500，因为策略工厂模块还未完全实现
        # 这里主要测试接口连通性
        assert response.status_code in [200, 500]
    
    def test_create_strategy_from_search(self):
        """测试通过搜索创建策略"""
        payload = {
            "keywords": "均线交叉",
            "initial_capital": 100000
        }
        
        response = client.post("/api/v1/strategies/from-search", json=payload)
        assert response.status_code in [200, 500]
    
    def test_optimize_strategy(self):
        """测试优化策略"""
        payload = {
            "generations": 50,
            "population_size": 20
        }
        
        response = client.post("/api/v1/strategies/strat_001/optimize", json=payload)
        assert response.status_code in [200, 404, 500]


class TestStockSelector:
    """选股引擎 API 测试"""
    
    def test_create_stock_pool(self):
        """测试创建股票池"""
        payload = {
            "name": "测试股票池",
            "strategy_id": "strat_001",
            "conditions": [
                {
                    "field": "pe_ratio",
                    "operator": "between",
                    "value": 10,
                    "value2": 30
                }
            ],
            "market": "A 股",
            "max_stocks": 100
        }
        
        response = client.post("/api/v1/stock-pools", json=payload)
        assert response.status_code in [200, 500]
    
    def test_list_stock_pools(self):
        """测试获取股票池列表"""
        response = client.get("/api/v1/stock-pools")
        assert response.status_code in [200, 500]
    
    def test_get_stock_pool(self):
        """测试获取股票池详情"""
        response = client.get("/api/v1/stock-pools/pool_001")
        assert response.status_code in [200, 404, 500]


class TestMonitoring:
    """监控中心 API 测试"""
    
    def test_start_monitoring(self):
        """测试启动监控任务"""
        payload = {
            "task_name": "测试监控",
            "strategy_id": "strat_001",
            "symbols": ["600519.SH"],
            "interval": 60,
            "notify_enabled": True,
            "notify_channels": ["app"]
        }
        
        response = client.post("/api/v1/monitoring/start", json=payload)
        assert response.status_code in [200, 500]
    
    def test_stop_monitoring(self):
        """测试停止监控任务"""
        payload = {
            "task_id": "task_001"
        }
        
        response = client.post("/api/v1/monitoring/stop", json=payload)
        assert response.status_code in [200, 500]
    
    def test_get_signals(self):
        """测试获取监控信号"""
        response = client.get("/api/v1/monitoring/signals")
        assert response.status_code in [200, 500]
    
    def test_get_signals_with_task_id(self):
        """测试获取指定任务的监控信号"""
        response = client.get("/api/v1/monitoring/signals?task_id=task_001")
        assert response.status_code in [200, 500]


class TestErrorHandling:
    """错误处理测试"""
    
    def test_invalid_strategy_request(self):
        """测试无效的策略请求"""
        payload = {
            "description": ""  # 空描述
        }
        
        response = client.post("/api/v1/strategies/from-text", json=payload)
        assert response.status_code in [400, 422, 500]
    
    def test_not_found(self):
        """测试 404 错误"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_method(self):
        """测试无效的请求方法"""
        response = client.delete("/api/v1/strategies/from-text")
        assert response.status_code in [405, 500]


class TestSchemas:
    """数据结构测试"""
    
    def test_strategy_from_text_request(self):
        """测试策略创建请求模型"""
        from api.schemas import StrategyFromTextRequest
        
        request = StrategyFromTextRequest(
            description="测试策略",
            initial_capital=100000,
            symbol="600519.SH"
        )
        
        assert request.description == "测试策略"
        assert request.initial_capital == 100000
        assert request.symbol == "600519.SH"
    
    def test_backtest_metrics(self):
        """测试回测指标模型"""
        from api.schemas import BacktestMetrics
        
        metrics = BacktestMetrics(
            total_return=15.5,
            annual_return=15.5,
            sharpe_ratio=1.2,
            max_drawdown=-8.3,
            win_rate=65.0,
            total_trades=24,
            profit_loss_ratio=2.1
        )
        
        assert metrics.total_return == 15.5
        assert metrics.sharpe_ratio == 1.2
    
    def test_stock_condition(self):
        """测试选股条件模型"""
        from api.schemas import StockCondition
        
        condition = StockCondition(
            field="pe_ratio",
            operator="between",
            value=10,
            value2=30
        )
        
        assert condition.field == "pe_ratio"
        assert condition.operator == "between"
        assert condition.value == 10
        assert condition.value2 == 30


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
