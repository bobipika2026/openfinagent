"""
监控中心模块测试

测试监控中心、信号检测器、行情订阅管理功能。

@module: tests.test_monitor
@author: OpenFinAgent Team
@version: 1.0.0
"""

import pytest
import pytest_asyncio
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, AsyncMock, patch

import sys
sys.path.insert(0, '/root/.openclaw/workspace/projects/tradeflow-ai/src')

from monitor.center import MonitorCenter, MonitoringTask, TaskStatus
from monitor.signal_detector import SignalDetector, Signal, SignalType
from monitor.subscription import (
    SubscriptionManager,
    StockSubscription,
    TickData
)


class TestSignalDetector:
    """信号检测器测试"""
    
    def test_signal_detector_init(self):
        """测试信号检测器初始化"""
        detector = SignalDetector(min_confidence=0.7, price_window=10)
        
        assert detector.min_confidence == 0.7
        assert detector.price_window == 10
        assert len(detector._signal_history) == 0
    
    def test_parse_signal_value(self):
        """测试信号值解析"""
        detector = SignalDetector()
        
        # 测试买入信号
        assert detector._parse_signal_value(1) == SignalType.BUY
        assert detector._parse_signal_value(1.0) == SignalType.BUY
        assert detector._parse_signal_value("1") == SignalType.BUY
        
        # 测试卖出信号
        assert detector._parse_signal_value(-1) == SignalType.SELL
        assert detector._parse_signal_value(-1.0) == SignalType.SELL
        
        # 测试持有信号
        assert detector._parse_signal_value(0) == SignalType.HOLD
        assert detector._parse_signal_value(0.0) == SignalType.HOLD
    
    def test_check_signal_with_mock_data(self):
        """测试信号检测（模拟数据）"""
        detector = SignalDetector(min_confidence=0.5)
        
        # 创建模拟策略
        mock_strategy = Mock()
        mock_strategy.name = "test_strategy"
        mock_strategy.generate_signals = Mock(return_value=pd.Series([1, 1, 1]))
        
        # 创建测试数据
        data = pd.DataFrame({
            'close': [10.0, 10.2, 10.5, 10.8, 11.0],
            'volume': [1000, 1200, 1500, 1800, 2000]
        })
        
        # 检测信号
        signal = detector.check_signal(mock_strategy, "000001.SZ", data)
        
        # 验证结果
        if signal:
            assert signal.symbol == "000001.SZ"
            assert signal.strategy_id == "test_strategy"
            assert signal.price == 11.0
            assert signal.confidence >= 0.5
    
    def test_check_signal_empty_data(self):
        """测试空数据信号检测"""
        detector = SignalDetector()
        mock_strategy = Mock()
        
        # 空 DataFrame
        data = pd.DataFrame()
        signal = detector.check_signal(mock_strategy, "000001.SZ", data)
        assert signal is None
    
    def test_signal_to_dict(self):
        """测试信号转换为字典"""
        signal = Signal(
            symbol="000001.SZ",
            signal_type=SignalType.BUY,
            strategy_id="test_strategy",
            price=10.5,
            confidence=0.85
        )
        
        signal_dict = signal.to_dict()
        
        assert signal_dict['symbol'] == "000001.SZ"
        assert signal_dict['signal_type'] == "buy"
        assert signal_dict['strategy_id'] == "test_strategy"
        assert signal_dict['price'] == 10.5
        assert signal_dict['confidence'] == 0.85
        assert 'id' in signal_dict
        assert 'timestamp' in signal_dict
    
    def test_get_signal_history(self):
        """测试获取信号历史"""
        detector = SignalDetector()
        
        # 添加模拟信号
        signal = Signal(symbol="000001.SZ", signal_type=SignalType.BUY)
        detector._signal_history["000001.SZ"] = signal
        
        # 获取历史
        history = detector.get_signal_history()
        assert "000001.SZ" in history
        
        # 获取单个股票历史
        single = detector.get_signal_history("000001.SZ")
        assert "000001.SZ" in single
    
    def test_clear_history(self):
        """测试清除信号历史"""
        detector = SignalDetector()
        detector._signal_history["000001.SZ"] = Signal()
        
        detector.clear_history()
        assert len(detector._signal_history) == 0


class TestSubscriptionManager:
    """行情订阅管理器测试"""
    
    @pytest.mark.asyncio
    async def test_subscribe(self):
        """测试订阅股票"""
        manager = SubscriptionManager()
        
        symbols = ["000001.SZ", "600000.SH", "300001.SZ"]
        result = await manager.subscribe(symbols)
        
        assert result is True
        assert len(manager.subscriptions) == 3
        
        for symbol in symbols:
            assert symbol in manager.subscriptions
            assert manager.subscriptions[symbol].symbol == symbol
    
    @pytest.mark.asyncio
    async def test_unsubscribe(self):
        """测试取消订阅"""
        manager = SubscriptionManager()
        
        # 先订阅
        await manager.subscribe(["000001.SZ", "600000.SH"])
        assert len(manager.subscriptions) == 2
        
        # 取消订阅
        result = await manager.unsubscribe(["000001.SZ"])
        assert result is True
        assert len(manager.subscriptions) == 1
        assert "000001.SZ" not in manager.subscriptions
    
    @pytest.mark.asyncio
    async def test_on_tick(self):
        """测试 Tick 数据处理"""
        manager = SubscriptionManager(max_history_size=10)
        
        # 订阅
        await manager.subscribe(["000001.SZ"])
        
        # 创建 Tick 数据
        tick = TickData(
            symbol="000001.SZ",
            timestamp=datetime.now(),
            price=10.5,
            volume=1000
        )
        
        # 处理 Tick
        await manager.on_tick(tick)
        
        # 验证
        latest = manager.latest_ticks.get("000001.SZ")
        assert latest is not None
        assert latest.price == 10.5
        
        subscription = manager.subscriptions["000001.SZ"]
        assert subscription.tick_count == 1
    
    @pytest.mark.asyncio
    async def test_get_latest_tick(self):
        """测试获取最新 Tick"""
        manager = SubscriptionManager()
        
        await manager.subscribe(["000001.SZ"])
        
        tick = TickData(symbol="000001.SZ", price=10.5)
        await manager.on_tick(tick)
        
        latest = await manager.get_latest_tick("000001.SZ")
        assert latest is not None
        assert latest.price == 10.5
    
    @pytest.mark.asyncio
    async def test_get_ticks_dataframe(self):
        """测试获取 Tick 数据 DataFrame"""
        manager = SubscriptionManager()
        
        await manager.subscribe(["000001.SZ"])
        
        # 添加多个 Tick
        for i in range(5):
            tick = TickData(
                symbol="000001.SZ",
                price=10.0 + i * 0.1,
                volume=1000 + i * 100
            )
            await manager.on_tick(tick)
        
        # 获取 DataFrame
        df = manager.get_ticks_dataframe("000001.SZ")
        
        assert df is not None
        assert len(df) == 5
        assert 'price' in df.columns
        assert 'volume' in df.columns
    
    def test_get_all_subscriptions(self):
        """测试获取所有订阅"""
        manager = SubscriptionManager()
        
        asyncio.run(manager.subscribe(["000001.SZ", "600000.SH"]))
        
        subscriptions = manager.get_all_subscriptions()
        assert len(subscriptions) == 2
        
        for sub in subscriptions:
            assert isinstance(sub, StockSubscription)
    
    @pytest.mark.asyncio
    async def test_history_size_limit(self):
        """测试历史记录大小限制"""
        manager = SubscriptionManager(max_history_size=5)
        
        await manager.subscribe(["000001.SZ"])
        
        # 添加 10 个 Tick
        for i in range(10):
            tick = TickData(symbol="000001.SZ", price=10.0 + i)
            await manager.on_tick(tick)
        
        # 验证历史记录被限制
        history = manager.tick_history["000001.SZ"]
        assert len(history) == 5


class TestMonitorCenter:
    """监控中心测试"""
    
    def test_monitor_center_init(self):
        """测试监控中心初始化"""
        center = MonitorCenter()
        
        assert len(center.tasks) == 0
        assert len(center.strategies) == 0
        assert center.on_signal_callback is None
    
    def test_register_strategy(self):
        """测试注册策略"""
        center = MonitorCenter()
        
        # 创建模拟策略
        mock_strategy = Mock()
        mock_strategy.name = "test_strategy"
        
        center.register_strategy("strategy_001", mock_strategy)
        
        assert "strategy_001" in center.strategies
        assert center.strategies["strategy_001"] == mock_strategy
    
    def test_set_signal_callback(self):
        """测试设置信号回调"""
        center = MonitorCenter()
        
        callback = Mock()
        center.set_signal_callback(callback)
        
        assert center.on_signal_callback == callback
    
    def test_get_monitoring_tasks(self):
        """测试获取监控任务"""
        center = MonitorCenter()
        
        # 添加模拟任务
        task1 = MonitoringTask(id="task_001", strategy_ids=["strategy_001"])
        task2 = MonitoringTask(id="task_002", strategy_ids=["strategy_002"])
        
        center.tasks["task_001"] = task1
        center.tasks["task_002"] = task2
        
        tasks = center.get_monitoring_tasks()
        assert len(tasks) == 2
        
        task_ids = [t.id for t in tasks]
        assert "task_001" in task_ids
        assert "task_002" in task_ids
    
    def test_get_task(self):
        """测试获取指定任务"""
        center = MonitorCenter()
        
        task = MonitoringTask(id="task_001")
        center.tasks["task_001"] = task
        
        retrieved = center.get_task("task_001")
        assert retrieved is not None
        assert retrieved.id == "task_001"
        
        # 不存在的任务
        not_found = center.get_task("task_999")
        assert not_found is None
    
    def test_pause_monitoring(self):
        """测试暂停监控"""
        center = MonitorCenter()
        
        task = MonitoringTask(id="task_001", status=TaskStatus.RUNNING)
        center.tasks["task_001"] = task
        
        result = center.pause_monitoring("task_001")
        assert result is True
        assert task.status == TaskStatus.PAUSED
    
    def test_resume_monitoring(self):
        """测试恢复监控"""
        center = MonitorCenter()
        
        task = MonitoringTask(id="task_001", status=TaskStatus.PAUSED)
        center.tasks["task_001"] = task
        
        result = center.resume_monitoring("task_001")
        assert result is True
        assert task.status == TaskStatus.RUNNING
    
    @pytest.mark.asyncio
    async def test_start_monitoring_invalid_strategy(self):
        """测试启动监控（无效策略）"""
        center = MonitorCenter()
        
        # 尝试使用不存在的策略
        with pytest.raises(ValueError, match="策略不存在"):
            await center.start_monitoring(
                strategy_ids=["non_existent"],
                stock_pool_id="pool_001"
            )
    
    @pytest.mark.asyncio
    async def test_stop_monitoring(self):
        """测试停止监控"""
        center = MonitorCenter()
        
        # 添加模拟任务
        task = MonitoringTask(
            id="task_001",
            strategy_ids=["strategy_001"],
            status=TaskStatus.RUNNING,
            symbols=["000001.SZ"]
        )
        center.tasks["task_001"] = task
        
        result = await center.stop_monitoring("task_001")
        assert result is True
        assert task.status == TaskStatus.STOPPED
    
    def test_monitoring_task_to_dict(self):
        """测试监控任务转换为字典"""
        task = MonitoringTask(
            id="task_001",
            strategy_ids=["strategy_001", "strategy_002"],
            stock_pool_id="pool_001",
            status=TaskStatus.RUNNING
        )
        
        task_dict = task.to_dict()
        
        assert task_dict['id'] == "task_001"
        assert len(task_dict['strategy_ids']) == 2
        assert task_dict['stock_pool_id'] == "pool_001"
        assert task_dict['status'] == "running"
        assert 'created_at' in task_dict
        assert 'updated_at' in task_dict
    
    def test_task_status_enum(self):
        """测试任务状态枚举"""
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.PAUSED.value == "paused"
        assert TaskStatus.STOPPED.value == "stopped"
        assert TaskStatus.ERROR.value == "error"


class TestIntegration:
    """集成测试"""
    
    @pytest.mark.asyncio
    async def test_signal_detection_flow(self):
        """测试信号检测流程"""
        # 创建组件
        detector = SignalDetector(min_confidence=0.5)
        manager = SubscriptionManager()
        
        # 订阅股票
        await manager.subscribe(["000001.SZ"])
        
        # 模拟策略
        mock_strategy = Mock()
        mock_strategy.name = "momentum_strategy"
        mock_strategy.generate_signals = Mock(return_value=pd.Series([1, 1, 1]))
        
        # 创建测试数据
        data = pd.DataFrame({
            'close': [10.0, 10.2, 10.5, 10.8, 11.0],
            'volume': [1000, 1200, 1500, 1800, 2000]
        })
        
        # 检测信号
        signal = detector.check_signal(mock_strategy, "000001.SZ", data)
        
        # 验证
        if signal:
            assert signal.signal_type == SignalType.BUY
            assert signal.confidence >= 0.5
    
    def test_monitor_center_with_mock_strategy(self):
        """测试监控中心与模拟策略集成"""
        center = MonitorCenter()
        
        # 创建模拟策略
        mock_strategy = Mock()
        mock_strategy.name = "test_strategy"
        mock_strategy.generate_signals = Mock(return_value=pd.Series([1]))
        
        # 注册策略
        center.register_strategy("test_strategy", mock_strategy)
        
        # 验证注册
        assert "test_strategy" in center.strategies
        
        # 设置信号回调
        callback_received = []
        
        def signal_callback(signal):
            callback_received.append(signal)
        
        center.set_signal_callback(signal_callback)
        
        # 验证回调设置
        assert center.on_signal_callback is not None


class TestSignalDetectorAdvanced:
    """信号检测器高级测试"""
    
    def test_calculate_confidence_with_volume(self):
        """测试置信度计算（成交量确认）"""
        detector = SignalDetector()
        
        data = pd.DataFrame({
            'close': [10.0, 10.2, 10.5, 10.8, 11.0],
            'volume': [1000, 1200, 1500, 1800, 3000]  # 最后一条放量
        })
        
        confidence = detector._calculate_confidence(data, SignalType.BUY)
        assert confidence > 0.5  # 放量应该提高置信度
    
    def test_calculate_confidence_with_trend(self):
        """测试置信度计算（趋势确认）"""
        detector = SignalDetector()
        
        data = pd.DataFrame({
            'close': [10.0, 10.2, 10.5, 10.8, 11.0],  # 上涨趋势
            'volume': [1000, 1000, 1000, 1000, 1000]
        })
        
        confidence = detector._calculate_confidence(data, SignalType.BUY)
        assert confidence > 0.5  # 上涨趋势应该提高买入置信度
    
    def test_detect_price_signal(self):
        """测试价格信号检测"""
        detector = SignalDetector()
        
        data = pd.DataFrame({
            'close': [10.0, 10.2, 10.5, 10.8, 11.5],  # 大幅上涨
            'volume': [1000, 1000, 1000, 1000, 1000]
        })
        
        signal = detector._detect_price_signal("000001.SZ", data, 11.5)
        
        if signal:
            assert signal.signal_type == SignalType.BUY
            assert signal.symbol == "000001.SZ"
    
    def test_check_signal_insufficient_data(self):
        """测试信号检测（数据不足）"""
        detector = SignalDetector()
        mock_strategy = Mock()
        
        # 只有一条数据
        data = pd.DataFrame({'close': [10.0]})
        
        signal = detector.check_signal(mock_strategy, "000001.SZ", data)
        assert signal is None


class TestSubscriptionManagerAdvanced:
    """行情订阅管理器高级测试"""
    
    def test_tick_data_to_dict(self):
        """测试 Tick 数据转换为字典"""
        tick = TickData(
            symbol="000001.SZ",
            price=10.5,
            volume=1000
        )
        
        tick_dict = tick.to_dict()
        
        assert tick_dict['symbol'] == "000001.SZ"
        assert tick_dict['price'] == 10.5
        assert 'timestamp' in tick_dict
    
    def test_stock_subscription_to_dict(self):
        """测试股票订阅转换为字典"""
        sub = StockSubscription(
            symbol="000001.SZ",
            tick_count=100
        )
        
        sub_dict = sub.to_dict()
        
        assert sub_dict['symbol'] == "000001.SZ"
        assert sub_dict['tick_count'] == 100
        assert 'id' in sub_dict
    
    @pytest.mark.asyncio
    async def test_subscribe_empty_list(self):
        """测试订阅空列表"""
        manager = SubscriptionManager()
        
        result = await manager.subscribe([])
        assert result is False
    
    @pytest.mark.asyncio
    async def test_unsubscribe_empty_list(self):
        """测试取消订阅空列表"""
        manager = SubscriptionManager()
        
        result = await manager.unsubscribe([])
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_ticks_no_data(self):
        """测试获取不存在的 Tick 数据"""
        manager = SubscriptionManager()
        
        ticks = manager.get_ticks("non_existent")
        assert len(ticks) == 0
    
    @pytest.mark.asyncio
    async def test_get_ticks_dataframe_no_data(self):
        """测试获取不存在的 DataFrame"""
        manager = SubscriptionManager()
        
        df = manager.get_ticks_dataframe("non_existent")
        assert df is None
    
    def test_get_subscription_not_found(self):
        """测试获取不存在的订阅"""
        manager = SubscriptionManager()
        
        sub = manager.get_subscription("non_existent")
        assert sub is None
    
    def test_cleanup(self):
        """测试清理资源"""
        manager = SubscriptionManager()
        
        asyncio.run(manager.subscribe(["000001.SZ"]))
        
        manager.cleanup()
        
        assert len(manager.subscriptions) == 0
        assert len(manager.latest_ticks) == 0


class TestMonitorCenterAdvanced:
    """监控中心高级测试"""
    
    def test_register_duplicate_strategy(self):
        """测试注册重复策略"""
        center = MonitorCenter()
        
        mock_strategy1 = Mock()
        mock_strategy1.name = "strategy1"
        
        mock_strategy2 = Mock()
        mock_strategy2.name = "strategy2"
        
        center.register_strategy("same_id", mock_strategy1)
        center.register_strategy("same_id", mock_strategy2)
        
        # 应该覆盖
        assert center.strategies["same_id"] == mock_strategy2
    
    def test_stop_non_existent_task(self):
        """测试停止不存在的任务"""
        center = MonitorCenter()
        
        result = center.pause_monitoring("non_existent")
        assert result is False
        
        result = center.resume_monitoring("non_existent")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_stop_monitoring_non_existent(self):
        """测试停止不存在的任务（异步）"""
        center = MonitorCenter()
        
        result = await center.stop_monitoring("non_existent")
        assert result is False
    
    def test_cleanup(self):
        """测试清理资源"""
        center = MonitorCenter()
        
        center.register_strategy("test", Mock())
        
        center.cleanup()
        
        assert center._running is False
    
    def test_monitoring_task_status_enum(self):
        """测试任务状态枚举值"""
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.PAUSED.value == "paused"
        assert TaskStatus.STOPPED.value == "stopped"
        assert TaskStatus.ERROR.value == "error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
