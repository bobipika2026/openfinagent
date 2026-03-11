"""
通知服务模块测试

测试通知服务、通知渠道、通知模板功能。

@module: tests.test_notification
@author: OpenFinAgent Team
@version: 1.0.0
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, MagicMock, AsyncMock, patch

import sys
sys.path.insert(0, '/root/.openclaw/workspace/projects/tradeflow-ai/src')

from notification.service import (
    NotificationService,
    Notification,
    NotificationType,
    NotificationPriority
)
from notification.channels import (
    FeishuChannel,
    EmailChannel,
    SMSChannel,
    ChannelConfig
)
from notification.templates import (
    NotificationTemplate,
    TemplateManager,
    TemplateType
)
from monitor.signal_detector import Signal, SignalType


class TestNotificationTemplate:
    """通知模板测试"""
    
    def test_template_init(self):
        """测试模板初始化"""
        template = NotificationTemplate(
            id="test_001",
            name="测试模板",
            template_type=TemplateType.CUSTOM,
            subject_template="测试：{title}",
            content_template="内容：{content}",
            variables=['title', 'content']
        )
        
        assert template.id == "test_001"
        assert template.name == "测试模板"
        assert template.template_type == TemplateType.CUSTOM
    
    def test_template_render(self):
        """测试模板渲染"""
        template = NotificationTemplate(
            id="test_001",
            name="测试模板",
            subject_template="📈 买入信号：{symbol}",
            content_template="股票：{symbol}, 价格：{price:.2f}",
            variables=['symbol', 'price']
        )
        
        rendered = template.render(symbol="000001.SZ", price=10.5)
        
        assert rendered['subject'] == "📈 买入信号：000001.SZ"
        assert "股票：000001.SZ" in rendered['content']
        assert "价格：10.50" in rendered['content']
    
    def test_template_render_missing_variables(self):
        """测试模板渲染（缺少变量）"""
        template = NotificationTemplate(
            subject_template="测试：{title}",
            content_template="内容：{content}"
        )
        
        # 缺少变量时回退到原始模板
        rendered = template.render(title="测试")
        
        # 当有变量缺失时，返回原始模板
        assert rendered['subject'] == "测试：{title}"
        assert rendered['content'] == "内容：{content}"
    
    def test_template_render_with_formatting(self):
        """测试模板渲染（格式化）"""
        template = NotificationTemplate(
            subject_template="报告",
            content_template="收益率：{rate:.2%}"
        )
        
        rendered = template.render(rate=0.1234)
        
        assert "收益率：12.34%" in rendered['content']


class TestTemplateManager:
    """模板管理器测试"""
    
    def test_template_manager_init(self):
        """测试模板管理器初始化"""
        manager = TemplateManager()
        
        # 应该有内置模板
        assert len(manager.templates) > 0
        
        # 检查内置模板是否存在
        templates = manager.list_templates()
        template_types = [t.template_type for t in templates]
        
        assert TemplateType.BUY_SIGNAL in template_types
        assert TemplateType.SELL_SIGNAL in template_types
        assert TemplateType.TAKE_PROFIT in template_types
        assert TemplateType.STOP_LOSS in template_types
    
    def test_register_template(self):
        """测试注册模板"""
        manager = TemplateManager()
        
        template = NotificationTemplate(
            id="custom_001",
            name="自定义模板",
            subject_template="自定义",
            content_template="内容"
        )
        
        result = manager.register(template)
        assert result is True
        assert "custom_001" in manager.templates
    
    def test_get_template(self):
        """测试获取模板"""
        manager = TemplateManager()
        
        template = manager.get_template("buy_signal_001")
        assert template is not None
        assert template.template_type == TemplateType.BUY_SIGNAL
    
    def test_get_template_not_found(self):
        """测试获取不存在的模板"""
        manager = TemplateManager()
        
        template = manager.get_template("non_existent")
        assert template is None
    
    def test_get_template_by_type(self):
        """测试根据类型获取模板"""
        manager = TemplateManager()
        
        template = manager.get_template_by_type(TemplateType.BUY_SIGNAL)
        assert template is not None
        assert template.template_type == TemplateType.BUY_SIGNAL
    
    def test_render_template(self):
        """测试渲染模板"""
        manager = TemplateManager()
        
        rendered = manager.render(
            "buy_signal_001",
            symbol="000001.SZ",
            price=10.5,
            strategy="test_strategy",
            confidence=0.85,
            timestamp="2024-01-01 10:00:00",
            stop_loss=10.0,
            target_price=11.0
        )
        
        assert rendered is not None
        assert "000001.SZ" in rendered['subject']
        assert "买入信号" in rendered['content']
    
    def test_delete_template(self):
        """测试删除模板"""
        manager = TemplateManager()
        
        # 注册自定义模板
        template = NotificationTemplate(
            id="to_delete",
            name="待删除",
            subject_template="测试",
            content_template="内容"
        )
        manager.register(template)
        
        # 删除
        result = manager.delete_template("to_delete")
        assert result is True
        assert "to_delete" not in manager.templates
        
        # 删除不存在的模板
        result = manager.delete_template("non_existent")
        assert result is False


class TestNotificationChannels:
    """通知渠道测试"""
    
    def test_feishu_channel_init(self):
        """测试飞书渠道初始化"""
        config = ChannelConfig(
            channel_type="feishu",
            enabled=True,
            config={
                'webhook_url': 'https://example.com/webhook'
            }
        )
        
        channel = FeishuChannel(config)
        
        assert channel.get_type() == "feishu"
        assert channel.enabled is True
        assert channel.webhook_url == 'https://example.com/webhook'
    
    def test_email_channel_init(self):
        """测试邮件渠道初始化"""
        config = ChannelConfig(
            channel_type="email",
            enabled=True,
            config={
                'smtp_server': 'smtp.example.com',
                'smtp_port': 587,
                'username': 'test@example.com',
                'password': 'password'
            }
        )
        
        channel = EmailChannel(config)
        
        assert channel.get_type() == "email"
        assert channel.smtp_server == 'smtp.example.com'
        assert channel.smtp_port == 587
    
    def test_sms_channel_init(self):
        """测试短信渠道初始化"""
        config = ChannelConfig(
            channel_type="sms",
            enabled=True,
            config={
                'provider': 'aliyun',
                'access_key': 'test_key',
                'secret_key': 'test_secret',
                'sign_name': '测试签名'
            }
        )
        
        channel = SMSChannel(config)
        
        assert channel.get_type() == "sms"
        assert channel.provider == 'aliyun'
    
    @pytest.mark.asyncio
    async def test_feishu_channel_send_disabled(self):
        """测试飞书渠道发送（未启用）"""
        config = ChannelConfig(channel_type="feishu", enabled=False)
        channel = FeishuChannel(config)
        
        result = await channel.send("user_001", "标题", "内容")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_email_channel_send_disabled(self):
        """测试邮件渠道发送（未启用）"""
        config = ChannelConfig(channel_type="email", enabled=False)
        channel = EmailChannel(config)
        
        result = await channel.send("test@example.com", "标题", "内容")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_sms_channel_send_disabled(self):
        """测试短信渠道发送（未启用）"""
        config = ChannelConfig(channel_type="sms", enabled=False)
        channel = SMSChannel(config)
        
        result = await channel.send("13800138000", "标题", "内容")
        assert result is False


class TestNotification:
    """通知数据模型测试"""
    
    def test_notification_init(self):
        """测试通知初始化"""
        notification = Notification(
            user_id="user_001",
            notification_type=NotificationType.SIGNAL,
            priority=NotificationPriority.HIGH,
            title="测试通知",
            content="测试内容"
        )
        
        assert notification.user_id == "user_001"
        assert notification.notification_type == NotificationType.SIGNAL
        assert notification.priority == NotificationPriority.HIGH
        assert notification.status == "pending"
        assert notification.sent_at is None
    
    def test_notification_to_dict(self):
        """测试通知转换为字典"""
        notification = Notification(
            id="notif_001",
            user_id="user_001",
            notification_type=NotificationType.SIGNAL,
            priority=NotificationPriority.HIGH,
            title="测试",
            content="内容"
        )
        
        notif_dict = notification.to_dict()
        
        assert notif_dict['id'] == "notif_001"
        assert notif_dict['user_id'] == "user_001"
        assert notif_dict['notification_type'] == "signal"
        assert notif_dict['priority'] == "high"
        assert notif_dict['title'] == "测试"
        assert notif_dict['content'] == "内容"
        assert 'created_at' in notif_dict


class TestNotificationService:
    """通知服务测试"""
    
    def test_notification_service_init(self):
        """测试通知服务初始化"""
        service = NotificationService()
        
        assert len(service.channels) == 0
        assert service.template_manager is not None
        assert len(service.notification_history) == 0
    
    def test_register_channel(self):
        """测试注册渠道"""
        service = NotificationService()
        
        config = ChannelConfig(
            channel_type="feishu",
            enabled=True,
            config={'webhook_url': 'https://example.com/webhook'}
        )
        
        result = service.register_channel("feishu", config)
        assert result is True
        assert "feishu" in service.channels
    
    def test_register_invalid_channel(self):
        """测试注册无效渠道"""
        service = NotificationService()
        
        config = ChannelConfig(channel_type="invalid")
        
        result = service.register_channel("invalid", config)
        assert result is False
    
    def test_set_user_preference(self):
        """测试设置用户偏好"""
        service = NotificationService()
        
        preferences = {
            'channels': ['feishu', 'email'],
            'quiet_hours': {'start': '22:00', 'end': '08:00'}
        }
        
        service.set_user_preference("user_001", preferences)
        
        retrieved = service.get_user_preference("user_001")
        assert retrieved == preferences
    
    def test_get_user_preference_default(self):
        """测试获取默认用户偏好"""
        service = NotificationService()
        
        preferences = service.get_user_preference("non_existent")
        assert preferences == {}
    
    @pytest.mark.asyncio
    async def test_send_notification_no_channels(self):
        """测试发送通知（无渠道）"""
        service = NotificationService()
        
        notification = Notification(
            user_id="user_001",
            title="测试",
            content="内容",
            channels=['feishu']
        )
        
        result = await service.send(notification)
        assert result is False
        assert notification.status == "failed"
    
    @pytest.mark.asyncio
    async def test_send_feishu(self):
        """测试发送飞书通知"""
        service = NotificationService()
        
        # 注册禁用的渠道（避免实际发送）
        config = ChannelConfig(channel_type="feishu", enabled=False)
        service.register_channel("feishu", config)
        
        result = await service.send_feishu("user_001", "测试内容")
        assert result is False  # 渠道禁用
    
    @pytest.mark.asyncio
    async def test_send_email(self):
        """测试发送邮件通知"""
        service = NotificationService()
        
        # 注册禁用的渠道
        config = ChannelConfig(channel_type="email", enabled=False)
        service.register_channel("email", config)
        
        result = await service.send_email("user_001", "主题", "内容")
        assert result is False  # 渠道禁用
    
    @pytest.mark.asyncio
    async def test_send_sms(self):
        """测试发送短信通知"""
        service = NotificationService()
        
        # 注册禁用的渠道
        config = ChannelConfig(channel_type="sms", enabled=False)
        service.register_channel("sms", config)
        
        result = await service.send_sms("user_001", "测试内容")
        assert result is False  # 渠道禁用
    
    def test_get_notification_history(self):
        """测试获取通知历史"""
        service = NotificationService()
        
        # 添加模拟通知
        notif1 = Notification(user_id="user_001", title="通知 1")
        notif2 = Notification(user_id="user_001", title="通知 2")
        notif3 = Notification(user_id="user_002", title="通知 3")
        
        service.notification_history = [notif1, notif2, notif3]
        
        # 获取所有
        all_history = service.get_notification_history(limit=10)
        assert len(all_history) == 3
        
        # 按用户过滤
        user1_history = service.get_notification_history(user_id="user_001")
        assert len(user1_history) == 2
        
        # 限制数量
        limited = service.get_notification_history(limit=1)
        assert len(limited) == 1
    
    @pytest.mark.asyncio
    async def test_send_signal_notification(self):
        """测试发送信号通知"""
        service = NotificationService()
        
        # 创建模拟信号
        signal = Signal(
            symbol="000001.SZ",
            signal_type=SignalType.BUY,
            strategy_id="test_strategy",
            price=10.5,
            confidence=0.85
        )
        
        # 注册禁用的渠道
        config = ChannelConfig(channel_type="feishu", enabled=False)
        service.register_channel("feishu", config)
        
        result = await service.send_signal_notification(signal, "user_001")
        assert result is False  # 渠道禁用
    
    @pytest.mark.asyncio
    async def test_send_take_profit_notification(self):
        """测试发送止盈通知"""
        service = NotificationService()
        
        # 注册禁用的渠道
        config = ChannelConfig(channel_type="feishu", enabled=False)
        service.register_channel("feishu", config)
        
        result = await service.send_take_profit_notification(
            symbol="000001.SZ",
            price=11.0,
            target_price=10.5,
            profit_rate=0.05,
            profit_amount=500.0,
            user_id="user_001"
        )
        
        assert result is False  # 渠道禁用
    
    @pytest.mark.asyncio
    async def test_send_stop_loss_notification(self):
        """测试发送止损通知"""
        service = NotificationService()
        
        # 注册禁用的渠道
        config = ChannelConfig(channel_type="feishu", enabled=False)
        service.register_channel("feishu", config)
        
        result = await service.send_stop_loss_notification(
            symbol="000001.SZ",
            price=9.5,
            stop_loss=10.0,
            loss_rate=-0.05,
            loss_amount=-500.0,
            user_id="user_001"
        )
        
        assert result is False  # 渠道禁用


class TestNotificationTypes:
    """通知类型枚举测试"""
    
    def test_notification_type_enum(self):
        """测试通知类型枚举"""
        assert NotificationType.SIGNAL.value == "signal"
        assert NotificationType.TRADE.value == "trade"
        assert NotificationType.RISK.value == "risk"
        assert NotificationType.REPORT.value == "report"
        assert NotificationType.SYSTEM.value == "system"
        assert NotificationType.CUSTOM.value == "custom"
    
    def test_notification_priority_enum(self):
        """测试通知优先级枚举"""
        assert NotificationPriority.LOW.value == "low"
        assert NotificationPriority.NORMAL.value == "normal"
        assert NotificationPriority.HIGH.value == "high"
        assert NotificationPriority.URGENT.value == "urgent"


class TestTemplateTypes:
    """模板类型枚举测试"""
    
    def test_template_type_enum(self):
        """测试模板类型枚举"""
        assert TemplateType.BUY_SIGNAL.value == "buy_signal"
        assert TemplateType.SELL_SIGNAL.value == "sell_signal"
        assert TemplateType.TAKE_PROFIT.value == "take_profit"
        assert TemplateType.STOP_LOSS.value == "stop_loss"
        assert TemplateType.DAILY_REPORT.value == "daily_report"
        assert TemplateType.WEEKLY_REPORT.value == "weekly_report"
        assert TemplateType.CUSTOM.value == "custom"


class TestIntegration:
    """集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_notification_flow(self):
        """测试完整通知流程"""
        # 创建服务
        service = NotificationService()
        
        # 注册渠道（禁用状态）
        config = ChannelConfig(channel_type="feishu", enabled=False)
        service.register_channel("feishu", config)
        
        # 设置用户偏好
        service.set_user_preference("user_001", {
            'channels': ['feishu']
        })
        
        # 创建通知
        notification = Notification(
            user_id="user_001",
            notification_type=NotificationType.SIGNAL,
            priority=NotificationPriority.HIGH,
            title="测试信号",
            content="测试内容",
            channels=['feishu']
        )
        
        # 发送通知
        result = await service.send(notification)
        
        # 验证（渠道禁用应该失败）
        assert result is False
        assert notification.status == "failed"
    
    def test_template_and_notification_integration(self):
        """测试模板和通知集成"""
        service = NotificationService()
        
        # 渲染买入信号模板
        rendered = service.template_manager.render(
            "buy_signal_001",
            symbol="000001.SZ",
            price=10.5,
            strategy="momentum",
            confidence=0.85,
            timestamp="2024-01-01 10:00:00",
            stop_loss=10.0,
            target_price=11.0
        )
        
        assert rendered is not None
        
        # 创建通知
        notification = Notification(
            user_id="user_001",
            notification_type=NotificationType.SIGNAL,
            title=rendered['subject'],
            content=rendered['content']
        )
        
        assert "买入信号" in notification.title
        assert "000001.SZ" in notification.content


class TestNotificationAdvanced:
    """通知高级测试"""
    
    def test_notification_repr(self):
        """测试通知字符串表示"""
        notification = Notification(
            id="test_001",
            notification_type=NotificationType.SIGNAL,
            priority=NotificationPriority.HIGH
        )
        
        repr_str = repr(notification)
        
        assert "test_001" in repr_str
        assert "signal" in repr_str
        assert "high" in repr_str
    
    def test_notification_with_metadata(self):
        """测试带元数据的通知"""
        notification = Notification(
            user_id="user_001",
            metadata={'key': 'value', 'count': 123}
        )
        
        notif_dict = notification.to_dict()
        
        assert notif_dict['metadata']['key'] == 'value'
        assert notif_dict['metadata']['count'] == 123


class TestChannelConfig:
    """渠道配置测试"""
    
    def test_channel_config_default(self):
        """测试渠道配置默认值"""
        config = ChannelConfig()
        
        assert config.channel_type == ""
        assert config.enabled is True
        assert len(config.config) == 0
    
    def test_channel_config_custom(self):
        """测试自定义渠道配置"""
        config = ChannelConfig(
            channel_type="custom",
            enabled=False,
            config={'key': 'value'}
        )
        
        assert config.channel_type == "custom"
        assert config.enabled is False
        assert config.config['key'] == 'value'


class TestTemplateRendering:
    """模板渲染高级测试"""
    
    def test_render_daily_report(self):
        """测试日报模板渲染"""
        manager = TemplateManager()
        
        rendered = manager.render(
            "daily_report_001",
            date="2024-01-01",
            total_assets=100000.0,
            cash=50000.0,
            position_value=50000.0,
            daily_pnl=1000.0,
            daily_pnl_rate=0.01,
            positions="000001.SZ: 1000 股",
            buy_signals=5,
            sell_signals=3,
            market_summary="市场震荡上涨"
        )
        
        assert rendered is not None
        assert "投资日报" in rendered['content']
        assert "2024-01-01" in rendered['content']
    
    def test_render_weekly_report(self):
        """测试周报模板渲染"""
        manager = TemplateManager()
        
        rendered = manager.render(
            "weekly_report_001",
            week_start="2024-01-01",
            week_end="2024-01-07",
            start_assets=100000.0,
            end_assets=105000.0,
            weekly_pnl=5000.0,
            weekly_pnl_rate=0.05,
            weekly_return=0.05,
            trade_count=10,
            buy_count=6,
            sell_count=4,
            win_rate=0.7,
            best_stock="000001.SZ",
            best_return=0.1,
            worst_stock="600000.SH",
            worst_return=-0.05,
            market_summary="市场上涨",
            next_week_strategy="继续持有"
        )
        
        assert rendered is not None
        assert "投资周报" in rendered['content']
    
    def test_render_take_profit(self):
        """测试止盈模板渲染"""
        manager = TemplateManager()
        
        rendered = manager.render(
            "take_profit_001",
            symbol="000001.SZ",
            price=11.0,
            target_price=10.5,
            profit_rate=0.05,
            profit_amount=500.0,
            timestamp="2024-01-01 10:00:00"
        )
        
        assert rendered is not None
        assert "止盈提醒" in rendered['content']
    
    def test_render_stop_loss(self):
        """测试止损模板渲染"""
        manager = TemplateManager()
        
        rendered = manager.render(
            "stop_loss_001",
            symbol="000001.SZ",
            price=9.5,
            stop_loss=10.0,
            loss_rate=-0.05,
            loss_amount=-500.0,
            timestamp="2024-01-01 10:00:00"
        )
        
        assert rendered is not None
        assert "止损提醒" in rendered['content']


class TestServiceCleanup:
    """服务清理测试"""
    
    def test_notification_service_cleanup(self):
        """测试通知服务清理"""
        service = NotificationService()
        
        # 注册渠道
        config = ChannelConfig(channel_type="feishu", enabled=False)
        service.register_channel("feishu", config)
        
        # 清理
        service.cleanup()
        
        # 验证清理完成
        assert len(service.channels) == 0 or not service.channels['feishu'].enabled


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
