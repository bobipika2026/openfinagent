"""
用户系统模块

提供用户注册、登录、认证、授权等完整功能

@module: user
@author: OpenFinAgent Team
@version: 0.4.0
"""

from .models import User, UserStatus, UserRole, PasswordResetToken, EmailVerificationToken
from .auth import AuthService
from .permissions import (
    Permission,
    PermissionManager,
    PermissionDenied,
    ROLE_PERMISSIONS,
    check_token_permission
)

__all__ = [
    # 模型
    'User',
    'UserStatus',
    'UserRole',
    'PasswordResetToken',
    'EmailVerificationToken',
    
    # 认证服务
    'AuthService',
    
    # 权限管理
    'Permission',
    'PermissionManager',
    'PermissionDenied',
    'ROLE_PERMISSIONS',
    'check_token_permission',
]
