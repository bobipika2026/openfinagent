"""
用户数据模型

定义用户系统的数据结构和模型

@module: user.models
@author: OpenFinAgent Team
@version: 0.4.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid


class UserStatus(Enum):
    """用户状态枚举"""
    ACTIVE = "active"  # 正常
    INACTIVE = "inactive"  # 未激活
    SUSPENDED = "suspended"  # 已停用
    BANNED = "banned"  # 已封禁


class UserRole(Enum):
    """用户角色枚举"""
    USER = "user"  # 普通用户
    PREMIUM = "premium"  # 高级用户
    ADMIN = "admin"  # 管理员


@dataclass
class User:
    """
    用户数据模型
    
    Attributes:
        id: 用户 ID (UUID)
        username: 用户名 (唯一)
        email: 邮箱 (唯一)
        password_hash: 密码哈希值
        role: 用户角色
        status: 用户状态
        bio: 个人简介
        avatar_url: 头像 URL
        created_at: 创建时间
        updated_at: 更新时间
        last_login: 最后登录时间
        email_verified: 邮箱是否已验证
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    email: str = ""
    password_hash: str = ""
    role: UserRole = field(default=UserRole.USER)
    status: UserStatus = field(default=UserStatus.INACTIVE)
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    email_verified: bool = False
    
    # 统计信息
    strategies_uploaded: int = 0
    strategies_downloaded: int = 0
    followers: int = 0
    following: int = 0
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'status': self.status.value,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'email_verified': self.email_verified,
            'strategies_uploaded': self.strategies_uploaded,
            'strategies_downloaded': self.strategies_downloaded,
            'followers': self.followers,
            'following': self.following
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """从字典创建"""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            username=data.get('username', ''),
            email=data.get('email', ''),
            password_hash=data.get('password_hash', ''),
            role=UserRole(data.get('role', 'user')),
            status=UserStatus(data.get('status', 'inactive')),
            bio=data.get('bio'),
            avatar_url=data.get('avatar_url'),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if 'updated_at' in data else datetime.now(),
            last_login=datetime.fromisoformat(data['last_login']) if data.get('last_login') else None,
            email_verified=data.get('email_verified', False),
            strategies_uploaded=data.get('strategies_uploaded', 0),
            strategies_downloaded=data.get('strategies_downloaded', 0),
            followers=data.get('followers', 0),
            following=data.get('following', 0)
        )


@dataclass
class PasswordResetToken:
    """
    密码重置令牌
    
    Attributes:
        id: 令牌 ID
        user_id: 用户 ID
        token: 令牌字符串
        expires_at: 过期时间
        used: 是否已使用
        created_at: 创建时间
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    token: str = ""
    expires_at: datetime = field(default_factory=lambda: datetime.now())
    used: bool = False
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class EmailVerificationToken:
    """
    邮箱验证令牌
    
    Attributes:
        id: 令牌 ID
        user_id: 用户 ID
        email: 待验证的邮箱
        token: 令牌字符串
        expires_at: 过期时间
        used: 是否已使用
        created_at: 创建时间
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    email: str = ""
    token: str = ""
    expires_at: datetime = field(default_factory=lambda: datetime.now())
    used: bool = False
    created_at: datetime = field(default_factory=datetime.now)
