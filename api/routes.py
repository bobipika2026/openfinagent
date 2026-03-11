"""
API 路由定义

将路由按功能模块组织，便于维护
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.schemas import (
    StrategyFromTextRequest,
    StrategyFromTextResponse,
    StrategySearchRequest,
    StrategySearchResponse,
    StrategyOptimizeRequest,
    StrategyOptimizeResponse,
    StockPoolCreateRequest,
    StockPoolResponse,
    StockPoolListResponse,
    MonitoringStartRequest,
    MonitoringStopRequest,
    MonitoringSignalsResponse,
    APIResponse,
)

# 创建路由器
strategy_router = APIRouter(prefix="/api/v1/strategies", tags=["策略工厂"])
stock_router = APIRouter(prefix="/api/v1/stock-pools", tags=["选股引擎"])
monitoring_router = APIRouter(prefix="/api/v1/monitoring", tags=["监控中心"])


# ==================== 策略工厂路由 ====================
@strategy_router.post("/from-text", response_model=StrategyFromTextResponse)
async def create_strategy_from_text(request: StrategyFromTextRequest):
    """通过自然语言描述创建策略"""
    try:
        from src.strategy_factory import StrategyFactory
        
        factory = StrategyFactory()
        result = factory.create_from_natural_language(
            description=request.description,
            initial_capital=request.initial_capital,
            auto_backtest=True
        )
        
        return StrategyFromTextResponse(
            success=True,
            message="策略创建成功",
            strategy_id=result.get('id'),
            strategy_name=result.get('name'),
            backtest_result=result.get('backtest_result'),
            stored=result.get('stored', False)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建策略失败：{str(e)}"
        )


@strategy_router.post("/from-search", response_model=StrategySearchResponse)
async def create_strategy_from_search(request: StrategySearchRequest):
    """通过搜索关键词创建策略"""
    try:
        from src.strategy_factory import StrategyFactory
        
        factory = StrategyFactory()
        results = factory.search_and_create(
            keywords=request.keywords,
            initial_capital=request.initial_capital,
            auto_backtest=True
        )
        
        strategies = []
        for result in results:
            strategies.append({
                'strategy_id': result.get('id'),
                'strategy_name': result.get('name'),
                'backtest_result': result.get('backtest_result'),
                'stored': result.get('stored', False)
            })
        
        return StrategySearchResponse(
            success=True,
            message=f"找到 {len(strategies)} 个策略",
            strategies=strategies
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索策略失败：{str(e)}"
        )


@strategy_router.post("/{strategy_id}/optimize", response_model=StrategyOptimizeResponse)
async def optimize_strategy(strategy_id: str, request: StrategyOptimizeRequest):
    """优化策略参数"""
    try:
        from src.strategy_factory import StrategyFactory
        
        factory = StrategyFactory()
        result = factory.optimize_strategy(
            strategy_id=strategy_id,
            generations=request.generations,
            population_size=request.population_size,
            auto_backtest=True
        )
        
        return StrategyOptimizeResponse(
            success=True,
            message="策略优化完成",
            strategy_id=strategy_id,
            optimized_params=result.get('optimized_params'),
            backtest_result=result.get('backtest_result'),
            improvement=result.get('improvement')
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"优化策略失败：{str(e)}"
        )


# ==================== 选股引擎路由 ====================
@stock_router.post("", response_model=StockPoolResponse)
async def create_stock_pool(request: StockPoolCreateRequest):
    """创建股票池"""
    try:
        from src.stock_selector import StockSelector
        
        selector = StockSelector()
        result = selector.create_pool(
            name=request.name,
            strategy_id=request.strategy_id,
            conditions=request.conditions,
            market=request.market,
            max_stocks=request.max_stocks
        )
        
        return StockPoolResponse(
            success=True,
            message="股票池创建成功",
            pool_id=result.get('pool_id'),
            name=result.get('name'),
            stock_count=result.get('stock_count'),
            stocks=result.get('stocks', []),
            created_at=result.get('created_at')
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建股票池失败：{str(e)}"
        )


@stock_router.get("", response_model=StockPoolListResponse)
async def list_stock_pools():
    """获取所有股票池列表"""
    try:
        from src.stock_selector import StockSelector
        
        selector = StockSelector()
        pools = selector.list_pools()
        
        return StockPoolListResponse(
            success=True,
            message="获取成功",
            pools=pools
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取股票池列表失败：{str(e)}"
        )


@stock_router.get("/{pool_id}", response_model=StockPoolResponse)
async def get_stock_pool(pool_id: str):
    """获取指定股票池详情"""
    try:
        from src.stock_selector import StockSelector
        
        selector = StockSelector()
        result = selector.get_pool(pool_id)
        
        return StockPoolResponse(
            success=True,
            message="获取成功",
            pool_id=result.get('pool_id'),
            name=result.get('name'),
            stock_count=result.get('stock_count'),
            stocks=result.get('stocks', []),
            created_at=result.get('created_at')
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"股票池不存在：pool_id={pool_id}"
        )


# ==================== 监控中心路由 ====================
@monitoring_router.post("/start", response_model=APIResponse)
async def start_monitoring(request: MonitoringStartRequest):
    """启动监控任务"""
    try:
        from src.monitor import MonitorCenter
        
        center = MonitorCenter()
        task_id = center.start_task(
            task_name=request.task_name,
            strategy_id=request.strategy_id,
            symbols=request.symbols,
            interval=request.interval,
            notify_enabled=request.notify_enabled,
            notify_channels=request.notify_channels
        )
        
        return APIResponse(
            success=True,
            message=f"监控任务已启动：{task_id}",
            data={"task_id": task_id}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动监控失败：{str(e)}"
        )


@monitoring_router.post("/stop", response_model=APIResponse)
async def stop_monitoring(request: MonitoringStopRequest):
    """停止监控任务"""
    try:
        from src.monitor import MonitorCenter
        
        center = MonitorCenter()
        center.stop_task(task_id=request.task_id)
        
        return APIResponse(
            success=True,
            message=f"监控任务已停止：{request.task_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"停止监控失败：{str(e)}"
        )


@monitoring_router.get("/signals", response_model=MonitoringSignalsResponse)
async def get_monitoring_signals(task_id: str = None):
    """获取监控信号"""
    try:
        from src.monitor import MonitorCenter
        
        center = MonitorCenter()
        signals = center.get_signals(task_id=task_id)
        
        return MonitoringSignalsResponse(
            success=True,
            message="获取成功",
            signals=signals
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取信号失败：{str(e)}"
        )
