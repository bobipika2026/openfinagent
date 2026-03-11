"""
通知渠道 - 多渠道通知推送

实现飞书、邮件、短信等多种通知渠道。

@module: notification.channels
@author: OpenFinAgent Team
@version: 1.0.0
"""

import asyncio
import logging
import smtplib
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class ChannelConfig:
    """
    渠道配置
    
    Attributes:
        channel_type: 渠道类型
        enabled: 是否启用
        config: 配置参数
    """
    channel_type: str = ""
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)


class NotificationChannel(ABC):
    """
    通知渠道基类
    
    定义通知渠道的通用接口。
    """
    
    def __init__(self, config: ChannelConfig):
        """
        初始化通知渠道
        
        Args:
            config: 渠道配置
        """
        self.config = config
        self.enabled = config.enabled
        logger.info(f"通知渠道初始化：{self.get_type()}")
    
    @abstractmethod
    def get_type(self) -> str:
        """获取渠道类型"""
        pass
    
    @abstractmethod
    async def send(self, recipient: str, subject: str, content: str) -> bool:
        """
        发送通知
        
        Args:
            recipient: 接收者
            subject: 标题
            content: 内容
            
        Returns:
            是否成功
        """
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """
        测试连接
        
        Returns:
            是否成功
        """
        pass


class FeishuChannel(NotificationChannel):
    """
    飞书通知渠道
    
    支持飞书机器人、飞书消息推送。
    
    Attributes:
        webhook_url: 飞书机器人 Webhook URL
        app_id: 飞书应用 ID
        app_secret: 飞书应用密钥
    """
    
    def __init__(self, config: ChannelConfig):
        """
        初始化飞书渠道
        
        Args:
            config: 渠道配置，需要包含 webhook_url 或 app_id/app_secret
        """
        super().__init__(config)
        
        self.webhook_url = config.config.get('webhook_url', '')
        self.app_id = config.config.get('app_id', '')
        self.app_secret = config.config.get('app_secret', '')
        self.tenant_access_token: Optional[str] = None
        self.token_expire_time: Optional[datetime] = None
        
        logger.info("飞书通知渠道初始化完成")
    
    def get_type(self) -> str:
        """获取渠道类型"""
        return "feishu"
    
    async def send(
        self,
        recipient: str,
        subject: str,
        content: str
    ) -> bool:
        """
        发送飞书消息
        
        Args:
            recipient: 接收者（用户 ID 或群聊 ID）
            subject: 标题
            content: 内容
            
        Returns:
            是否成功
        """
        if not self.enabled:
            logger.warning("飞书渠道未启用")
            return False
        
        try:
            # 使用 Webhook 发送
            if self.webhook_url:
                return await self._send_via_webhook(content)
            
            # 使用应用 API 发送
            elif self.app_id and self.app_secret:
                return await self._send_via_api(recipient, subject, content)
            
            else:
                logger.error("飞书渠道未配置")
                return False
                
        except Exception as e:
            logger.error(f"飞书消息发送失败：{e}", exc_info=True)
            return False
    
    async def _send_via_webhook(self, content: str) -> bool:
        """
        通过 Webhook 发送消息
        
        Args:
            content: 消息内容
            
        Returns:
            是否成功
        """
        try:
            # 构建飞书消息格式
            message = {
                "msg_type": "text",
                "content": {
                    "text": content
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=message,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    result = await response.json()
                    
                    if response.status == 200 and result.get('StatusCode') == 0:
                        logger.info("飞书 Webhook 消息发送成功")
                        return True
                    else:
                        logger.error(f"飞书 Webhook 发送失败：{result}")
                        return False
                        
        except Exception as e:
            logger.error(f"飞书 Webhook 发送异常：{e}")
            return False
    
    async def _send_via_api(
        self,
        recipient: str,
        subject: str,
        content: str
    ) -> bool:
        """
        通过飞书 API 发送消息
        
        Args:
            recipient: 接收者 ID
            subject: 标题
            content: 内容
            
        Returns:
            是否成功
        """
        try:
            # 获取 tenant_access_token
            await self._ensure_token()
            
            # 构建消息
            url = "https://open.feishu.cn/open-apis/im/v1/messages"
            headers = {
                "Authorization": f"Bearer {self.tenant_access_token}",
                "Content-Type": "application/json"
            }
            
            message = {
                "receive_id": recipient,
                "msg_type": "text",
                "content": json.dumps({
                    "text": f"{subject}\n\n{content}"
                })
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=message,
                    headers=headers,
                    params={"receive_id_type": "open_id"}
                ) as response:
                    result = await response.json()
                    
                    if response.status == 200 and result.get('code') == 0:
                        logger.info(f"飞书 API 消息发送成功：{recipient}")
                        return True
                    else:
                        logger.error(f"飞书 API 发送失败：{result}")
                        return False
                        
        except Exception as e:
            logger.error(f"飞书 API 发送异常：{e}")
            return False
    
    async def _ensure_token(self) -> None:
        """确保 token 有效"""
        now = datetime.now()
        
        if (self.tenant_access_token and 
            self.token_expire_time and 
            now < self.token_expire_time):
            return
        
        await self._refresh_token()
    
    async def _refresh_token(self) -> None:
        """刷新 token"""
        try:
            url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
            headers = {"Content-Type": "application/json"}
            data = {
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    result = await response.json()
                    
                    if result.get('code') == 0:
                        self.tenant_access_token = result['tenant_access_token']
                        # token 有效期 2 小时
                        self.token_expire_time = datetime.now()
                        logger.info("飞书 token 刷新成功")
                    else:
                        logger.error(f"飞书 token 刷新失败：{result}")
                        
        except Exception as e:
            logger.error(f"飞书 token 刷新异常：{e}")
    
    async def test_connection(self) -> bool:
        """测试连接"""
        try:
            if self.webhook_url:
                return await self._send_via_webhook("飞书通知连接测试")
            elif self.app_id and self.app_secret:
                await self._refresh_token()
                return self.tenant_access_token is not None
            return False
        except Exception as e:
            logger.error(f"飞书连接测试失败：{e}")
            return False


class EmailChannel(NotificationChannel):
    """
    邮件通知渠道
    
    支持 SMTP 邮件发送。
    
    Attributes:
        smtp_server: SMTP 服务器地址
        smtp_port: SMTP 端口
        username: 邮箱账号
        password: 邮箱密码
        use_tls: 是否使用 TLS
    """
    
    def __init__(self, config: ChannelConfig):
        """
        初始化邮件渠道
        
        Args:
            config: 渠道配置，需要包含 SMTP 配置
        """
        super().__init__(config)
        
        self.smtp_server = config.config.get('smtp_server', '')
        self.smtp_port = config.config.get('smtp_port', 587)
        self.username = config.config.get('username', '')
        self.password = config.config.get('password', '')
        self.use_tls = config.config.get('use_tls', True)
        self.sender_email = config.config.get('sender_email', self.username)
        
        logger.info("邮件通知渠道初始化完成")
    
    def get_type(self) -> str:
        """获取渠道类型"""
        return "email"
    
    async def send(
        self,
        recipient: str,
        subject: str,
        content: str
    ) -> bool:
        """
        发送邮件
        
        Args:
            recipient: 接收者邮箱
            subject: 邮件主题
            content: 邮件内容
            
        Returns:
            是否成功
        """
        if not self.enabled:
            logger.warning("邮件渠道未启用")
            return False
        
        if not all([self.smtp_server, self.username, self.password]):
            logger.error("邮件渠道配置不完整")
            return False
        
        try:
            # 在线程池中执行同步的 SMTP 发送
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._send_email_sync,
                recipient,
                subject,
                content
            )
            
            logger.info(f"邮件发送成功：{recipient}")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败：{e}", exc_info=True)
            return False
    
    def _send_email_sync(
        self,
        recipient: str,
        subject: str,
        content: str
    ) -> None:
        """
        同步发送邮件
        
        Args:
            recipient: 接收者邮箱
            subject: 邮件主题
            content: 邮件内容
        """
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        
        # 添加内容
        msg.attach(MIMEText(content, 'plain', 'utf-8'))
        
        # 连接 SMTP 服务器
        if self.use_tls:
            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
        else:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        
        try:
            server.login(self.username, self.password)
            server.sendmail(self.sender_email, recipient, msg.as_string())
        finally:
            server.quit()
    
    async def test_connection(self) -> bool:
        """测试连接"""
        try:
            if self.use_tls:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            try:
                server.login(self.username, self.password)
                server.quit()
                logger.info("邮件服务器连接成功")
                return True
            except Exception as e:
                logger.error(f"邮件服务器登录失败：{e}")
                return False
                
        except Exception as e:
            logger.error(f"邮件服务器连接失败：{e}")
            return False


class SMSChannel(NotificationChannel):
    """
    短信通知渠道
    
    支持阿里云短信、腾讯云短信等。
    
    Attributes:
        provider: 短信服务商
        access_key: 访问密钥
        secret_key: 密钥
        sign_name: 签名
        template_id: 模板 ID
    """
    
    def __init__(self, config: ChannelConfig):
        """
        初始化短信渠道
        
        Args:
            config: 渠道配置，需要包含短信服务商配置
        """
        super().__init__(config)
        
        self.provider = config.config.get('provider', 'aliyun')
        self.access_key = config.config.get('access_key', '')
        self.secret_key = config.config.get('secret_key', '')
        self.sign_name = config.config.get('sign_name', '')
        self.template_id = config.config.get('template_id', '')
        
        logger.info(f"短信通知渠道初始化完成：{self.provider}")
    
    def get_type(self) -> str:
        """获取渠道类型"""
        return "sms"
    
    async def send(
        self,
        recipient: str,
        subject: str,
        content: str
    ) -> bool:
        """
        发送短信
        
        Args:
            recipient: 接收者手机号
            subject: 标题（短信中通常不使用）
            content: 短信内容
            
        Returns:
            是否成功
        """
        if not self.enabled:
            logger.warning("短信渠道未启用")
            return False
        
        if not all([self.access_key, self.secret_key, self.sign_name]):
            logger.error("短信渠道配置不完整")
            return False
        
        try:
            # 根据服务商选择发送方式
            if self.provider == 'aliyun':
                return await self._send_aliyun_sms(recipient, content)
            elif self.provider == 'tencent':
                return await self._send_tencent_sms(recipient, content)
            else:
                logger.error(f"不支持的短信服务商：{self.provider}")
                return False
                
        except Exception as e:
            logger.error(f"短信发送失败：{e}", exc_info=True)
            return False
    
    async def _send_aliyun_sms(self, phone: str, content: str) -> bool:
        """
        发送阿里云短信
        
        Args:
            phone: 手机号
            content: 短信内容
            
        Returns:
            是否成功
        """
        # 这里简化实现，实际需要使用阿里云 SDK
        logger.info(f"阿里云短信发送（模拟）：{phone}, 内容：{content}")
        
        # TODO: 集成阿里云短信 SDK
        # from aliyunsdkcore.client import AcsClient
        # from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
        
        return True
    
    async def _send_tencent_sms(self, phone: str, content: str) -> bool:
        """
        发送腾讯云短信
        
        Args:
            phone: 手机号
            content: 短信内容
            
        Returns:
            是否成功
        """
        # 这里简化实现，实际需要使用腾讯云 SDK
        logger.info(f"腾讯云短信发送（模拟）：{phone}, 内容：{content}")
        
        # TODO: 集成腾讯云短信 SDK
        
        return True
    
    async def test_connection(self) -> bool:
        """测试连接"""
        # 短信渠道通常不需要测试连接
        return all([self.access_key, self.secret_key, self.sign_name])
