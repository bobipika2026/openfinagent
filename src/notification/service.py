"""
通知服务核心类 - 统一通知管理

提供通知发送、渠道管理、模板渲染等功能。

@module: notification.service
@author: OpenFinAgent Team
@version: 1.0.0
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import uuid

try:
    from ..monitor.signal_detector import Signal, SignalType
except ImportError:
    from monitor.signal_detector import Signal, SignalType

from .channels import (
    NotificationChannel,
    FeishuChannel,
    EmailChannel,
    SMSChannel,
    ChannelConfig
)
from .templates import TemplateManager, TemplateType

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """通知类型"""
    SIGNAL = "signal"  # 交易信号
    TRADE = "trade"  # 交易执行
    RISK = "risk"  # 风险预警
    REPORT = "report"  # 报告
    SYSTEM = "system"  # 系统通知
    CUSTOM = "custom"  # 自定义


class NotificationPriority(Enum):
    """通知优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Notification:
    """
    通知数据模型
    
    Attributes:
        id: 通知 ID
        user_id: 用户 ID
        notification_type: 通知类型
        priority: 优先级
        title: 标题
        content: 内容
        channels: 发送渠道列表
        created_at: 创建时间
        sent_at: 发送时间
        status: 发送状态
        metadata: 附加信息
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    notification_type: NotificationType = NotificationType.CUSTOM
    priority: NotificationPriority = NotificationPriority.NORMAL
    title: str = ""
    content: str = ""
    channels: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    sent_at: Optional[datetime] = None
    status: str = "pending"  # pending, sent, failed
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'notification_type': self.notification_type.value,
            'priority': self.priority.value,
            'title': self.title,
            'content': self.content,
            'channels': self.channels,
            'created_at': self.created_at.isoformat(),
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'status': self.status,
            'metadata': self.metadata
        }
    
    def __repr__(self) -> str:
        return (
            f"Notification(id={self.id}, type={self.notification_type.value}, "
            f"priority={self.priority.value}, status={self.status})"
        )


class NotificationService:
    """
    通知服务核心类
    
    统一管理通知发送，支持多渠道、多模板、优先级控制。
    
    Attributes:
        channels: 通知渠道字典
        template_manager: 模板管理器
        user_preferences: 用户偏好设置
        notification_history: 通知历史
    """
    
    def __init__(self):
        """初始化通知服务"""
        self.channels: Dict[str, NotificationChannel] = {}
        self.template_manager = TemplateManager()
        self.user_preferences: Dict[str, Dict[str, Any]] = {}
        self.notification_history: List[Notification] = []
        
        logger.info("通知服务初始化完成")
    
    def register_channel(
        self,
        channel_type: str,
        config: ChannelConfig
    ) -> bool:
        """
        注册通知渠道
        
        Args:
            channel_type: 渠道类型（feishu/email/sms）
            config: 渠道配置
            
        Returns:
            是否成功
        """
        try:
            if channel_type == 'feishu':
                channel = FeishuChannel(config)
            elif channel_type == 'email':
                channel = EmailChannel(config)
            elif channel_type == 'sms':
                channel = SMSChannel(config)
            else:
                logger.error(f"不支持的渠道类型：{channel_type}")
                return False
            
            self.channels[channel_type] = channel
            logger.info(f"通知渠道注册成功：{channel_type}")
            return True
            
        except Exception as e:
            logger.error(f"通知渠道注册失败：{channel_type}, {e}")
            return False
    
    def set_user_preference(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> None:
        """
        设置用户通知偏好
        
        Args:
            user_id: 用户 ID
            preferences: 偏好设置
        """
        self.user_preferences[user_id] = preferences
        logger.info(f"用户通知偏好设置：{user_id}")
    
    def get_user_preference(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户通知偏好
        
        Args:
            user_id: 用户 ID
            
        Returns:
            偏好设置
        """
        return self.user_preferences.get(user_id, {})
    
    async def send(self, notification: Notification) -> bool:
        """
        发送通知
        
        Args:
            notification: 通知对象
            
        Returns:
            是否成功
        """
        try:
            logger.info(
                f"发送通知：{notification.id}, "
                f"类型：{notification.notification_type.value}, "
                f"优先级：{notification.priority.value}"
            )
            
            # 获取用户偏好
            preferences = self.get_user_preference(notification.user_id)
            enabled_channels = preferences.get('channels', notification.channels)
            
            # 发送通知到各个渠道
            tasks = []
            for channel_type in enabled_channels:
                if channel_type in self.channels:
                    channel = self.channels[channel_type]
                    if channel.enabled:
                        task = self._send_to_channel(
                            channel,
                            notification.user_id,
                            notification.title,
                            notification.content
                        )
                        tasks.append(task)
            
            if not tasks:
                logger.warning("没有可用的通知渠道")
                notification.status = "failed"
                return False
            
            # 并发发送
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 检查结果
            success_count = sum(1 for r in results if r is True)
            
            if success_count > 0:
                notification.status = "sent"
                notification.sent_at = datetime.now()
                logger.info(f"通知发送成功：{notification.id}, {success_count}/{len(tasks)} 渠道")
            else:
                notification.status = "failed"
                logger.error(f"通知发送失败：{notification.id}")
            
            # 记录历史
            self.notification_history.append(notification)
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"通知发送异常：{notification.id}, {e}", exc_info=True)
            notification.status = "failed"
            return False
    
    async def _send_to_channel(
        self,
        channel: NotificationChannel,
        recipient: str,
        subject: str,
        content: str
    ) -> bool:
        """
        发送到指定渠道
        
        Args:
            channel: 通知渠道
            recipient: 接收者
            subject: 标题
            content: 内容
            
        Returns:
            是否成功
        """
        try:
            return await channel.send(recipient, subject, content)
        except Exception as e:
            logger.error(f"渠道发送失败：{channel.get_type()}, {e}")
            return False
    
    async def send_feishu(self, user_id: str, content: str) -> bool:
        """
        发送飞书通知
        
        Args:
            user_id: 用户 ID
            content: 内容
            
        Returns:
            是否成功
        """
        notification = Notification(
            user_id=user_id,
            notification_type=NotificationType.CUSTOM,
            title="飞书通知",
            content=content,
            channels=['feishu']
        )
        
        return await self.send(notification)
    
    async def send_email(
        self,
        user_id: str,
        subject: str,
        content: str
    ) -> bool:
        """
        发送邮件通知
        
        Args:
            user_id: 用户 ID
            subject: 邮件主题
            content: 邮件内容
            
        Returns:
            是否成功
        """
        notification = Notification(
            user_id=user_id,
            notification_type=NotificationType.CUSTOM,
            title=subject,
            content=content,
            channels=['email']
        )
        
        return await self.send(notification)
    
    async def send_sms(self, user_id: str, content: str) -> bool:
        """
        发送短信通知
        
        Args:
            user_id: 用户 ID
            content: 短信内容
            
        Returns:
            是否成功
        """
        notification = Notification(
            user_id=user_id,
            notification_type=NotificationType.CUSTOM,
            title="短信通知",
            content=content,
            channels=['sms'],
            priority=NotificationPriority.HIGH
        )
        
        return await self.send(notification)
    
    async def send_signal_notification(self, signal: Signal, user_id: str) -> bool:
        """
        发送交易信号通知
        
        Args:
            signal: 交易信号
            user_id: 用户 ID
            
        Returns:
            是否成功
        """
        # 根据信号类型选择模板
        if signal.signal_type == SignalType.BUY:
            template_id = "buy_signal_001"
            priority = NotificationPriority.HIGH
        elif signal.signal_type == SignalType.SELL:
            template_id = "sell_signal_001"
            priority = NotificationPriority.HIGH
        else:
            template_id = None
            priority = NotificationPriority.NORMAL
        
        if not template_id:
            logger.debug(f"忽略持有信号：{signal.symbol}")
            return False
        
        # 渲染模板
        rendered = self.template_manager.render(
            template_id,
            symbol=signal.symbol,
            price=signal.price,
            strategy=signal.strategy_id,
            confidence=signal.confidence,
            timestamp=signal.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            stop_loss=signal.price * 0.95,  # 示例止损位
            target_price=signal.price * 1.05  # 示例目标价
        )
        
        if not rendered:
            logger.error("模板渲染失败")
            return False
        
        # 创建通知
        notification = Notification(
            user_id=user_id,
            notification_type=NotificationType.SIGNAL,
            priority=priority,
            title=rendered['subject'],
            content=rendered['content'],
            channels=['feishu'],
            metadata=signal.to_dict()
        )
        
        return await self.send(notification)
    
    async def send_take_profit_notification(
        self,
        symbol: str,
        price: float,
        target_price: float,
        profit_rate: float,
        profit_amount: float,
        user_id: str
    ) -> bool:
        """
        发送止盈通知
        
        Args:
            symbol: 股票代码
            price: 当前价格
            target_price: 目标价格
            profit_rate: 收益率
            profit_amount: 盈利金额
            user_id: 用户 ID
            
        Returns:
            是否成功
        """
        rendered = self.template_manager.render(
            "take_profit_001",
            symbol=symbol,
            price=price,
            target_price=target_price,
            profit_rate=profit_rate,
            profit_amount=profit_amount,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        if not rendered:
            return False
        
        notification = Notification(
            user_id=user_id,
            notification_type=NotificationType.TRADE,
            priority=NotificationPriority.HIGH,
            title=rendered['subject'],
            content=rendered['content'],
            channels=['feishu', 'sms']
        )
        
        return await self.send(notification)
    
    async def send_stop_loss_notification(
        self,
        symbol: str,
        price: float,
        stop_loss: float,
        loss_rate: float,
        loss_amount: float,
        user_id: str
    ) -> bool:
        """
        发送止损通知
        
        Args:
            symbol: 股票代码
            price: 当前价格
            stop_loss: 止损价格
            loss_rate: 亏损率
            loss_amount: 亏损金额
            user_id: 用户 ID
            
        Returns:
            是否成功
        """
        rendered = self.template_manager.render(
            "stop_loss_001",
            symbol=symbol,
            price=price,
            stop_loss=stop_loss,
            loss_rate=loss_rate,
            loss_amount=loss_amount,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        if not rendered:
            return False
        
        notification = Notification(
            user_id=user_id,
            notification_type=NotificationType.RISK,
            priority=NotificationPriority.URGENT,
            title=rendered['subject'],
            content=rendered['content'],
            channels=['feishu', 'sms']
        )
        
        return await self.send(notification)
    
    async def send_daily_report(
        self,
        user_id: str,
        report_data: Dict[str, Any]
    ) -> bool:
        """
        发送日报
        
        Args:
            user_id: 用户 ID
            report_data: 报告数据
            
        Returns:
            是否成功
        """
        rendered = self.template_manager.render(
            "daily_report_001",
            date=datetime.now().strftime('%Y-%m-%d'),
            **report_data
        )
        
        if not rendered:
            return False
        
        notification = Notification(
            user_id=user_id,
            notification_type=NotificationType.REPORT,
            priority=NotificationPriority.NORMAL,
            title=rendered['subject'],
            content=rendered['content'],
            channels=['feishu', 'email']
        )
        
        return await self.send(notification)
    
    async def send_weekly_report(
        self,
        user_id: str,
        report_data: Dict[str, Any]
    ) -> bool:
        """
        发送周报
        
        Args:
            user_id: 用户 ID
            report_data: 报告数据
            
        Returns:
            是否成功
        """
        rendered = self.template_manager.render(
            "weekly_report_001",
            **report_data
        )
        
        if not rendered:
            return False
        
        notification = Notification(
            user_id=user_id,
            notification_type=NotificationType.REPORT,
            priority=NotificationPriority.NORMAL,
            title=rendered['subject'],
            content=rendered['content'],
            channels=['feishu', 'email']
        )
        
        return await self.send(notification)
    
    def get_notification_history(
        self,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Notification]:
        """
        获取通知历史
        
        Args:
            user_id: 用户 ID，为 None 则返回所有
            limit: 数量限制
            
        Returns:
            通知列表
        """
        if user_id:
            filtered = [n for n in self.notification_history if n.user_id == user_id]
            return filtered[-limit:]
        
        return self.notification_history[-limit:]
    
    def cleanup(self) -> None:
        """清理资源"""
        logger.info("通知服务清理资源")
        
        for channel in self.channels.values():
            if hasattr(channel, 'cleanup'):
                channel.cleanup()
        
        logger.info("通知服务清理完成")
    
    def __del__(self):
        """析构函数"""
        self.cleanup()
