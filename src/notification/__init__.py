"""
通知服务模块 - 实时通知推送

提供多渠道通知推送功能，支持飞书、邮件、短信等。

@module: notification
@author: OpenFinAgent Team
@version: 1.0.0
"""

from .service import NotificationService, Notification, NotificationType, NotificationPriority
from .channels import NotificationChannel, FeishuChannel, EmailChannel, SMSChannel
from .templates import NotificationTemplate, TemplateManager

__all__ = [
    # 通知服务
    'NotificationService',
    'Notification',
    'NotificationType',
    'NotificationPriority',
    
    # 通知渠道
    'NotificationChannel',
    'FeishuChannel',
    'EmailChannel',
    'SMSChannel',
    
    # 通知模板
    'NotificationTemplate',
    'TemplateManager',
]
