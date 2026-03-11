"""
OpenFinAgent RESTful API 服务

提供策略工厂、选股引擎、监控中心的 API 接口

版本：v1.0.0
作者：OpenFinAgent Team
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    print("🚀 OpenFinAgent API 启动中...")
    yield
    # 关闭时清理
    print("👋 OpenFinAgent API 关闭中...")


# 创建 FastAPI 应用
app = FastAPI(
    title="OpenFinAgent API",
    description="AI 驱动的量化交易平台 API - 提供策略工厂、选股引擎、监控中心功能",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 健康检查 ====================
@app.get("/health", tags=["Health"])
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "version": "1.0.0"}


# ==================== 策略工厂 ====================
@app.post(
    "/api/v1/strategies/from-text",
    response_model=StrategyFromTextResponse,
    tags=["策略工厂"]
)
async def create_strategy_from_text(request: StrategyFromTextRequest):
    """
    通过自然语言描述创建策略
    
    - **description**: 策略的自然语言描述
    - **initial_capital**: 初始资金（可选，默认 100000）
    - **symbol**: 回测标的（可选，默认 '600519.SH'）
    """
    try:
        # TODO: 调用策略工厂核心逻辑
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


@app.post(
    "/api/v1/strategies/from-search",
    response_model=StrategySearchResponse,
    tags=["策略工厂"]
)
async def create_strategy_from_search(request: StrategySearchRequest):
    """
    通过搜索关键词创建策略
    
    - **keywords**: 搜索关键词
    - **initial_capital**: 初始资金（可选）
    """
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


@app.post(
    "/api/v1/strategies/{strategy_id}/optimize",
    response_model=StrategyOptimizeResponse,
    tags=["策略工厂"]
)
async def optimize_strategy(strategy_id: str, request: StrategyOptimizeRequest):
    """
    优化策略参数
    
    - **strategy_id**: 策略 ID
    - **generations**: 遗传算法代数（可选，默认 50）
    - **population_size**: 种群大小（可选，默认 20）
    """
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


# ==================== 选股引擎 ====================
@app.post(
    "/api/v1/stock-pools",
    response_model=StockPoolResponse,
    tags=["选股引擎"]
)
async def create_stock_pool(request: StockPoolCreateRequest):
    """
    创建股票池
    
    - **name**: 股票池名称
    - **strategy_id**: 策略 ID
    - **conditions**: 选股条件
    - **market**: 市场（可选，默认 'A 股'）
    """
    try:
        # TODO: 调用选股引擎核心逻辑
        from src.stock_selector import StockSelector
        
        selector = StockSelector()
        result = selector.create_pool(
            name=request.name,
            strategy_id=request.strategy_id,
            conditions=request.conditions,
            market=request.market
        )
        
        return StockPoolResponse(
            success=True,
            message="股票池创建成功",
            pool_id=result.get('pool_id'),
            name=result.get('name'),
            stock_count=result.get('stock_count'),
            stocks=result.get('stocks', [])
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建股票池失败：{str(e)}"
        )


@app.get(
    "/api/v1/stock-pools",
    response_model=StockPoolListResponse,
    tags=["选股引擎"]
)
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


@app.get(
    "/api/v1/stock-pools/{pool_id}",
    response_model=StockPoolResponse,
    tags=["选股引擎"]
)
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
            stocks=result.get('stocks', [])
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"股票池不存在：{str(e)}"
        )


# ==================== 监控中心 ====================
@app.post(
    "/api/v1/monitoring/start",
    response_model=APIResponse,
    tags=["监控中心"]
)
async def start_monitoring(request: MonitoringStartRequest):
    """
    启动监控任务
    
    - **task_name**: 任务名称
    - **strategy_id**: 策略 ID
    - **symbols**: 监控标的列表
    - **interval**: 监控间隔（秒，默认 60）
    """
    try:
        from src.monitor import MonitorCenter
        
        center = MonitorCenter()
        task_id = center.start_task(
            task_name=request.task_name,
            strategy_id=request.strategy_id,
            symbols=request.symbols,
            interval=request.interval
        )
        
        return APIResponse(
            success=True,
            message=f"监控任务已启动：{task_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动监控失败：{str(e)}"
        )


@app.post(
    "/api/v1/monitoring/stop",
    response_model=APIResponse,
    tags=["监控中心"]
)
async def stop_monitoring(request: MonitoringStopRequest):
    """
    停止监控任务
    
    - **task_id**: 任务 ID
    """
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


@app.get(
    "/api/v1/monitoring/signals",
    response_model=MonitoringSignalsResponse,
    tags=["监控中心"]
)
async def get_monitoring_signals(task_id: str = None):
    """
    获取监控信号
    
    - **task_id**: 任务 ID（可选，不传则返回所有）
    """
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


# ==================== 异常处理 ====================
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP 异常处理"""
    return {
        "success": False,
        "message": exc.detail,
        "status_code": exc.status_code
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    return {
        "success": False,
        "message": f"服务器内部错误：{str(exc)}",
        "status_code": 500
    }


# 导入路由
from api.routes import strategy_router, stock_router, monitoring_router

# 注册路由
app.include_router(strategy_router)
app.include_router(stock_router)
app.include_router(monitoring_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
