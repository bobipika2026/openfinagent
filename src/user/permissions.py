"""
用户权限控制

提供基于角色的访问控制 (RBAC) 功能

@module: user.permissions
@author: OpenFinAgent Team
@version: 0.4.0
"""

from functools import wraps
from typing import Optional, List, Callable, Any
from enum import Enum
import logging

from .models import User, UserRole
from .auth import AuthService

logger = logging.getLogger(__name__)


class Permission(Enum):
    """权限枚举"""
    # 基础权限
    USER_READ = "user:read"  # 查看用户信息
    USER_WRITE = "user:write"  # 修改用户信息
    USER_DELETE = "user:delete"  # 删除用户
    
    # 策略权限
    STRATEGY_READ = "strategy:read"  # 查看策略
    STRATEGY_WRITE = "strategy:write"  # 创建/修改策略
    STRATEGY_DELETE = "strategy:delete"  # 删除策略
    STRATEGY_PUBLISH = "strategy:publish"  # 发布策略
    
    # 市场权限
    MARKET_READ = "market:read"  # 浏览市场
    MARKET_DOWNLOAD = "market:download"  # 下载策略
    MARKET_COMMENT = "market:comment"  # 评论策略
    MARKET_STAR = "market:star"  # 收藏策略
    
    # 模拟盘权限
    PAPER_TRADING_READ = "paper:read"  # 查看模拟盘
    PAPER_TRADING_WRITE = "paper:write"  # 创建模拟盘
    PAPER_TRADING_TRADE = "paper:trade"  # 执行模拟交易
    
    # 管理权限
    ADMIN_USER_MANAGE = "admin:user_manage"  # 用户管理
    ADMIN_STRATEGY_MANAGE = "admin:strategy_manage"  # 策略管理
    ADMIN_SYSTEM = "admin:system"  # 系统管理


# 角色权限映射
ROLE_PERMISSIONS = {
    UserRole.USER: {
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.STRATEGY_READ,
        Permission.STRATEGY_WRITE,
        Permission.STRATEGY_PUBLISH,
        Permission.MARKET_READ,
        Permission.MARKET_DOWNLOAD,
        Permission.MARKET_COMMENT,
        Permission.MARKET_STAR,
        Permission.PAPER_TRADING_READ,
        Permission.PAPER_TRADING_WRITE,
        Permission.PAPER_TRADING_TRADE,
    },
    UserRole.PREMIUM: {
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.STRATEGY_READ,
        Permission.STRATEGY_WRITE,
        Permission.STRATEGY_DELETE,
        Permission.STRATEGY_PUBLISH,
        Permission.MARKET_READ,
        Permission.MARKET_DOWNLOAD,
        Permission.MARKET_COMMENT,
        Permission.MARKET_STAR,
        Permission.PAPER_TRADING_READ,
        Permission.PAPER_TRADING_WRITE,
        Permission.PAPER_TRADING_TRADE,
    },
    UserRole.ADMIN: {
        # 管理员拥有所有权限
        *Permission,
    }
}


class PermissionDenied(Exception):
    """权限拒绝异常"""
    pass


class PermissionManager:
    """
    权限管理器
    
    提供权限检查、角色管理等功能
    """
    
    def __init__(self, auth_service: AuthService):
        """
        初始化权限管理器
        
        Args:
            auth_service: 认证服务实例
        """
        self.auth_service = auth_service
    
    def has_permission(self, user: User, permission: Permission) -> bool:
        """
        检查用户是否有指定权限
        
        Args:
            user: 用户对象
            permission: 权限
        
        Returns:
            是否有权限
        """
        # 获取用户角色的权限集合
        allowed_permissions = ROLE_PERMISSIONS.get(user.role, set())
        
        return permission in allowed_permissions
    
    def has_role(self, user: User, role: UserRole) -> bool:
        """
        检查用户是否有指定角色
        
        Args:
            user: 用户对象
            role: 角色
        
        Returns:
            是否有该角色
        """
        return user.role == role
    
    def has_any_role(self, user: User, roles: List[UserRole]) -> bool:
        """
        检查用户是否有任一指定角色
        
        Args:
            user: 用户对象
            roles: 角色列表
        
        Returns:
            是否有任一角色
        """
        return user.role in roles
    
    def require_permission(self, permission: Permission):
        """
        权限检查装饰器
        
        Args:
            permission: 需要的权限
        
        Returns:
            装饰器函数
        
        Usage:
            @permission_manager.require_permission(Permission.STRATEGY_WRITE)
            def create_strategy(user, ...):
                ...
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                # 尝试从参数中获取 user 对象
                user = kwargs.get('user')
                if not user:
                    # 尝试从位置参数获取 (假设第一个参数是 user)
                    if args and isinstance(args[0], User):
                        user = args[0]
                
                if not user:
                    raise PermissionDenied("未提供用户信息")
                
                # 检查权限
                if not self.has_permission(user, permission):
                    logger.warning(f"用户 {user.username} 缺少权限 {permission.value}")
                    raise PermissionDenied(f"缺少权限：{permission.value}")
                
                return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def require_role(self, *required_roles: UserRole):
        """
        角色检查装饰器
        
        Args:
            *required_roles: 需要的角色列表
        
        Returns:
            装饰器函数
        
        Usage:
            @permission_manager.require_role(UserRole.ADMIN, UserRole.PREMIUM)
            def premium_feature(user, ...):
                ...
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                # 尝试从参数中获取 user 对象
                user = kwargs.get('user')
                if not user:
                    if args and isinstance(args[0], User):
                        user = args[0]
                
                if not user:
                    raise PermissionDenied("未提供用户信息")
                
                # 检查角色
                if user.role not in required_roles:
                    logger.warning(f"用户 {user.username} 角色 {user.role.value} 不满足要求")
                    raise PermissionDenied(f"需要角色：{[r.value for r in required_roles]}")
                
                return func(*args, **kwargs)
            
            return wrapper
        return decorator


def check_token_permission(
    auth_service: AuthService,
    token: str,
    permission: Permission
) -> User:
    """
    检查 Token 是否有指定权限
    
    Args:
        auth_service: 认证服务
        token: JWT Token
        permission: 权限
    
    Returns:
        用户对象
    
    Raises:
        PermissionDenied: 当权限不足时
        ValueError: 当 Token 无效时
    """
    # 验证 Token 获取用户
    user = auth_service.verify_token(token)
    
    # 检查权限
    permission_manager = PermissionManager(auth_service)
    
    if not permission_manager.has_permission(user, permission):
        raise PermissionDenied(f"缺少权限：{permission.value}")
    
    return user
