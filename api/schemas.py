"""
API 请求/响应数据结构定义

遵循 Pydantic 规范，提供类型验证和文档生成
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ==================== 通用响应 ====================
class APIResponse(BaseModel):
    """通用 API 响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")


# ==================== 策略工厂 ====================
class StrategyFromTextRequest(BaseModel):
    """通过自然语言创建策略请求"""
    description: str = Field(..., description="策略的自然语言描述", min_length=1)
    initial_capital: float = Field(100000, description="初始资金", ge=0)
    symbol: str = Field("600519.SH", description="回测标的")
    start_date: Optional[str] = Field(None, description="回测开始日期")
    end_date: Optional[str] = Field(None, description="回测结束日期")


class BacktestMetrics(BaseModel):
    """回测指标"""
    total_return: float = Field(0.0, description="总收益率")
    annual_return: float = Field(0.0, description="年化收益率")
    sharpe_ratio: float = Field(0.0, description="夏普比率")
    max_drawdown: float = Field(0.0, description="最大回撤")
    win_rate: float = Field(0.0, description="胜率")
    total_trades: int = Field(0, description="总交易次数")
    profit_loss_ratio: float = Field(0.0, description="盈亏比")


class StrategyFromTextResponse(BaseModel):
    """通过自然语言创建策略响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    strategy_id: Optional[str] = Field(None, description="策略 ID")
    strategy_name: Optional[str] = Field(None, description="策略名称")
    backtest_result: Optional[BacktestMetrics] = Field(None, description="回测结果")
    stored: bool = Field(False, description="是否已入库")


class StrategySearchRequest(BaseModel):
    """搜索策略请求"""
    keywords: str = Field(..., description="搜索关键词", min_length=1)
    initial_capital: Optional[float] = Field(100000, description="初始资金", ge=0)


class StrategySearchResult(BaseModel):
    """搜索结果中的策略信息"""
    strategy_id: str = Field(..., description="策略 ID")
    strategy_name: str = Field(..., description="策略名称")
    backtest_result: Optional[BacktestMetrics] = Field(None, description="回测结果")
    stored: bool = Field(False, description="是否已入库")


class StrategySearchResponse(BaseModel):
    """搜索策略响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    strategies: List[StrategySearchResult] = Field(..., description="策略列表")


class StrategyOptimizeRequest(BaseModel):
    """优化策略请求"""
    generations: int = Field(50, description="遗传算法代数", ge=10, le=200)
    population_size: int = Field(20, description="种群大小", ge=10, le=100)


class StrategyOptimizeResponse(BaseModel):
    """优化策略响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    strategy_id: str = Field(..., description="策略 ID")
    optimized_params: Optional[Dict[str, Any]] = Field(None, description="优化后的参数")
    backtest_result: Optional[BacktestMetrics] = Field(None, description="回测结果")
    improvement: Optional[float] = Field(None, description="提升幅度（%）")


# ==================== 选股引擎 ====================
class StockCondition(BaseModel):
    """选股条件"""
    field: str = Field(..., description="字段名，如 'pe_ratio', 'market_cap'")
    operator: str = Field(..., description="操作符，如 '>', '<', '=', 'between'")
    value: Any = Field(..., description="条件值")
    value2: Optional[Any] = Field(None, description="第二个值（用于 between）")


class StockPoolCreateRequest(BaseModel):
    """创建股票池请求"""
    name: str = Field(..., description="股票池名称", min_length=1)
    strategy_id: Optional[str] = Field(None, description="关联的策略 ID")
    conditions: List[StockCondition] = Field(..., description="选股条件列表")
    market: str = Field("A 股", description="市场，如 'A 股', '港股', '美股'")
    max_stocks: int = Field(100, description="最大股票数量", ge=1, le=1000)


class StockInfo(BaseModel):
    """股票信息"""
    symbol: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    price: float = Field(0.0, description="当前价格")
    change_percent: float = Field(0.0, description="涨跌幅")
    market_cap: float = Field(0.0, description="市值")
    pe_ratio: float = Field(0.0, description="市盈率")


class StockPoolResponse(BaseModel):
    """股票池响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    pool_id: Optional[str] = Field(None, description="股票池 ID")
    name: Optional[str] = Field(None, description="股票池名称")
    stock_count: int = Field(0, description="股票数量")
    stocks: List[StockInfo] = Field(..., description="股票列表")
    created_at: Optional[datetime] = Field(None, description="创建时间")


class StockPoolListItem(BaseModel):
    """股票池列表项"""
    pool_id: str = Field(..., description="股票池 ID")
    name: str = Field(..., description="股票池名称")
    stock_count: int = Field(0, description="股票数量")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class StockPoolListResponse(BaseModel):
    """股票池列表响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    pools: List[StockPoolListItem] = Field(..., description="股票池列表")


# ==================== 监控中心 ====================
class MonitoringStartRequest(BaseModel):
    """启动监控请求"""
    task_name: str = Field(..., description="任务名称", min_length=1)
    strategy_id: str = Field(..., description="策略 ID")
    symbols: List[str] = Field(..., description="监控标的列表", min_items=1)
    interval: int = Field(60, description="监控间隔（秒）", ge=10, le=3600)
    notify_enabled: bool = Field(True, description="是否启用通知")
    notify_channels: List[str] = Field(["app"], description="通知渠道")


class MonitoringStopRequest(BaseModel):
    """停止监控请求"""
    task_id: str = Field(..., description="任务 ID")


class SignalInfo(BaseModel):
    """信号信息"""
    signal_id: str = Field(..., description="信号 ID")
    task_id: str = Field(..., description="任务 ID")
    symbol: str = Field(..., description="标的代码")
    signal_type: str = Field(..., description="信号类型，如 'buy', 'sell'")
    price: float = Field(0.0, description="信号价格")
    timestamp: datetime = Field(..., description="信号时间")
    strength: float = Field(0.0, description="信号强度", ge=0, le=1)
    message: Optional[str] = Field(None, description="信号说明")


class MonitoringSignalsResponse(BaseModel):
    """监控信号响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    signals: List[SignalInfo] = Field(..., description="信号列表")


class MonitoringTaskInfo(BaseModel):
    """监控任务信息"""
    task_id: str = Field(..., description="任务 ID")
    task_name: str = Field(..., description="任务名称")
    strategy_id: str = Field(..., description="策略 ID")
    symbols: List[str] = Field(..., description="监控标的列表")
    status: str = Field(..., description="任务状态，如 'running', 'stopped'")
    interval: int = Field(0, description="监控间隔（秒）")
    created_at: datetime = Field(..., description="创建时间")
    signal_count: int = Field(0, description="信号数量")


# ==================== 通知服务 ====================
class NotificationConfig(BaseModel):
    """通知配置"""
    channel: str = Field(..., description="通知渠道，如 'app', 'email', 'sms'")
    enabled: bool = Field(True, description="是否启用")
    config: Dict[str, Any] = Field(default_factory=dict, description="渠道配置")


class NotificationHistoryItem(BaseModel):
    """通知历史项"""
    notification_id: str = Field(..., description="通知 ID")
    task_id: str = Field(..., description="任务 ID")
    signal_id: str = Field(..., description="信号 ID")
    channel: str = Field(..., description="通知渠道")
    content: str = Field(..., description="通知内容")
    status: str = Field(..., description="发送状态，如 'sent', 'failed'")
    sent_at: datetime = Field(..., description="发送时间")


class NotificationHistoryResponse(BaseModel):
    """通知历史响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    notifications: List[NotificationHistoryItem] = Field(..., description="通知历史列表")
    total: int = Field(0, description="总数")
