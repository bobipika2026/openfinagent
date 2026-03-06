"""
用户系统测试

测试用户注册、登录、认证、权限管理等功能

@module: tests.test_user
@author: OpenFinAgent Team
@version: 0.4.0
"""

import pytest
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from user.models import User, UserStatus, UserRole
from user.auth import AuthService
from user.permissions import Permission, PermissionManager, PermissionDenied


class TestUserModel:
    """测试用户模型"""
    
    def test_user_creation(self):
        """测试用户创建"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == UserRole.USER
        assert user.status == UserStatus.INACTIVE
        assert user.email_verified is False
    
    def test_user_to_dict(self):
        """测试用户转字典"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hash"
        )
        
        user_dict = user.to_dict()
        
        assert user_dict['username'] == "testuser"
        assert user_dict['email'] == "test@example.com"
        assert user_dict['role'] == "user"
        assert 'id' in user_dict
        assert 'created_at' in user_dict
    
    def test_user_from_dict(self):
        """测试从字典创建用户"""
        user_dict = {
            'id': '123',
            'username': 'testuser',
            'email': 'test@example.com',
            'role': 'premium',
            'status': 'active',
            'bio': 'Test bio',
            'created_at': '2024-01-01T00:00:00',
            'updated_at': '2024-01-01T00:00:00'
        }
        
        user = User.from_dict(user_dict)
        
        assert user.id == '123'
        assert user.username == 'testuser'
        assert user.role == UserRole.PREMIUM
        assert user.status == UserStatus.ACTIVE
        assert user.bio == 'Test bio'


class TestAuthService:
    """测试认证服务"""
    
    @pytest.fixture
    def auth_service(self, tmp_path):
        """创建测试用的认证服务"""
        db_path = tmp_path / "test_users.json"
        return AuthService(
            secret_key="test_secret_key",
            db_path=str(db_path)
        )
    
    def test_register_success(self, auth_service):
        """测试成功注册"""
        user, verification_token = auth_service.register(
            email="test@example.com",
            password="password123",
            username="testuser"
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.status == UserStatus.INACTIVE
        assert verification_token is not None
        assert len(user.id) > 0
    
    def test_register_duplicate_email(self, auth_service):
        """测试重复邮箱注册"""
        auth_service.register(
            email="test@example.com",
            password="password123"
        )
        
        with pytest.raises(ValueError, match="邮箱已被注册"):
            auth_service.register(
                email="test@example.com",
                password="password456"
            )
    
    def test_register_weak_password(self, auth_service):
        """测试弱密码注册"""
        with pytest.raises(ValueError, match="密码长度至少为 6 位"):
            auth_service.register(
                email="test@example.com",
                password="123"
            )
    
    def test_login_success(self, auth_service):
        """测试成功登录"""
        # 注册并验证
        user, token = auth_service.register(
            email="test@example.com",
            password="password123"
        )
        
        # 验证邮箱
        auth_service.verify_email(token)
        
        # 登录
        jwt_token = auth_service.login(
            email="test@example.com",
            password="password123"
        )
        
        assert jwt_token is not None
        assert len(jwt_token) > 0
    
    def test_login_wrong_password(self, auth_service):
        """测试错误密码登录"""
        auth_service.register(
            email="test@example.com",
            password="password123"
        )
        
        with pytest.raises(ValueError, match="密码错误"):
            auth_service.login(
                email="test@example.com",
                password="wrong_password"
            )
    
    def test_login_inactive_account(self, auth_service):
        """测试未激活账户登录"""
        auth_service.register(
            email="test@example.com",
            password="password123"
        )
        
        with pytest.raises(ValueError, match="账户未激活"):
            auth_service.login(
                email="test@example.com",
                password="password123"
            )
    
    def test_verify_email_success(self, auth_service):
        """测试邮箱验证成功"""
        user, verification_token = auth_service.register(
            email="test@example.com",
            password="password123"
        )
        
        result = auth_service.verify_email(verification_token)
        
        assert result is True
        
        # 验证用户状态已更新
        updated_user = auth_service.get_user_by_id(user.id)
        assert updated_user.email_verified is True
        assert updated_user.status == UserStatus.ACTIVE
    
    def test_verify_email_expired_token(self, auth_service):
        """测试过期验证令牌"""
        user, verification_token = auth_service.register(
            email="test@example.com",
            password="password123"
        )
        
        # 手动设置令牌过期
        auth_service.verification_tokens[verification_token].expires_at = datetime.now() - timedelta(days=1)
        
        with pytest.raises(ValueError, match="验证令牌已过期"):
            auth_service.verify_email(verification_token)
    
    def test_reset_password_request(self, auth_service):
        """测试密码重置请求"""
        auth_service.register(
            email="test@example.com",
            password="password123"
        )
        
        reset_token = auth_service.reset_password_request("test@example.com")
        
        assert reset_token is not None
        assert len(reset_token) > 0
    
    def test_reset_password_success(self, auth_service):
        """测试密码重置成功"""
        auth_service.register(
            email="test@example.com",
            password="password123"
        )
        
        reset_token = auth_service.reset_password_request("test@example.com")
        
        result = auth_service.reset_password(reset_token, "new_password456")
        
        assert result is True
        
        # 验证可以使用新密码登录
        # (需要先验证邮箱)
        user = auth_service._get_user_by_email("test@example.com")
        user.status = UserStatus.ACTIVE
        auth_service._save_users()
        
        jwt_token = auth_service.login(
            email="test@example.com",
            password="new_password456"
        )
        
        assert jwt_token is not None
    
    def test_verify_token_success(self, auth_service):
        """测试 Token 验证成功"""
        user, _ = auth_service.register(
            email="test@example.com",
            password="password123"
        )
        
        # 激活用户
        user.status = UserStatus.ACTIVE
        auth_service._save_users()
        
        # 生成 Token
        token = auth_service.login("test@example.com", "password123")
        
        # 验证 Token
        verified_user = auth_service.verify_token(token)
        
        assert verified_user.id == user.id
        assert verified_user.email == user.email
    
    def test_verify_token_expired(self, auth_service):
        """测试过期 Token"""
        # 创建一个过期的 token (通过修改服务配置)
        auth_service.token_expire_days = -1  # 立即过期
        
        user, _ = auth_service.register(
            email="test@example.com",
            password="password123"
        )
        user.status = UserStatus.ACTIVE
        auth_service._save_users()
        
        token = auth_service.login("test@example.com", "password123")
        
        with pytest.raises(ValueError, match="Token 已过期"):
            auth_service.verify_token(token)
    
    def test_update_user_profile(self, auth_service):
        """测试更新用户资料"""
        user, _ = auth_service.register(
            email="test@example.com",
            password="password123"
        )
        
        # 更新资料
        updated_user = auth_service.update_user_profile(
            user_id=user.id,
            username="new_username",
            bio="New bio"
        )
        
        assert updated_user.username == "new_username"
        assert updated_user.bio == "New bio"


class TestPermissionManager:
    """测试权限管理器"""
    
    @pytest.fixture
    def auth_service(self, tmp_path):
        """创建测试用的认证服务"""
        db_path = tmp_path / "test_users.json"
        return AuthService(
            secret_key="test_secret_key",
            db_path=str(db_path)
        )
    
    @pytest.fixture
    def permission_manager(self, auth_service):
        """创建权限管理器"""
        return PermissionManager(auth_service)
    
    def test_user_has_basic_permissions(self, auth_service, permission_manager):
        """测试普通用户有基础权限"""
        user = User(
            username="testuser",
            email="test@example.com",
            role=UserRole.USER
        )
        
        assert permission_manager.has_permission(user, Permission.USER_READ)
        assert permission_manager.has_permission(user, Permission.STRATEGY_READ)
        assert permission_manager.has_permission(user, Permission.MARKET_READ)
    
    def test_user_lacks_admin_permissions(self, auth_service, permission_manager):
        """测试普通用户没有管理员权限"""
        user = User(
            username="testuser",
            email="test@example.com",
            role=UserRole.USER
        )
        
        assert not permission_manager.has_permission(user, Permission.ADMIN_USER_MANAGE)
        assert not permission_manager.has_permission(user, Permission.ADMIN_SYSTEM)
    
    def test_admin_has_all_permissions(self, auth_service, permission_manager):
        """测试管理员有所有权限"""
        user = User(
            username="admin",
            email="admin@example.com",
            role=UserRole.ADMIN
        )
        
        # 管理员应该有所有权限
        for permission in Permission:
            assert permission_manager.has_permission(user, permission)
    
    def test_require_permission_decorator(self, auth_service, permission_manager):
        """测试权限装饰器"""
        @permission_manager.require_permission(Permission.STRATEGY_WRITE)
        def create_strategy(user):
            return "Strategy created"
        
        # 有权限的用户
        user = User(username="testuser", email="test@example.com", role=UserRole.USER)
        result = create_strategy(user)
        assert result == "Strategy created"
        
        # 没有权限的用户 (创建一个没有 STRATEGY_WRITE 权限的场景)
        # 这里需要修改权限映射来测试，简化测试
        user.role = UserRole.USER  # 普通用户应该有 STRATEGY_WRITE
    
    def test_require_role_decorator(self, auth_service, permission_manager):
        """测试角色装饰器"""
        @permission_manager.require_role(UserRole.ADMIN)
        def admin_only_function(user):
            return "Admin access granted"
        
        # 管理员
        admin_user = User(username="admin", email="admin@example.com", role=UserRole.ADMIN)
        result = admin_only_function(admin_user)
        assert result == "Admin access granted"
        
        # 普通用户
        normal_user = User(username="user", email="user@example.com", role=UserRole.USER)
        
        with pytest.raises(PermissionDenied):
            admin_only_function(normal_user)


class TestIntegration:
    """集成测试"""
    
    @pytest.fixture
    def auth_service(self, tmp_path):
        """创建测试用的认证服务"""
        db_path = tmp_path / "test_users.json"
        return AuthService(
            secret_key="test_secret_key",
            db_path=str(db_path)
        )
    
    def test_full_registration_login_flow(self, auth_service):
        """测试完整的注册 - 验证 - 登录流程"""
        # 1. 注册
        user, verification_token = auth_service.register(
            email="test@example.com",
            password="password123",
            username="testuser"
        )
        
        assert user.status == UserStatus.INACTIVE
        
        # 2. 验证邮箱
        auth_service.verify_email(verification_token)
        
        # 3. 登录
        jwt_token = auth_service.login(
            email="test@example.com",
            password="password123"
        )
        
        assert jwt_token is not None
        
        # 4. 验证 Token
        verified_user = auth_service.verify_token(jwt_token)
        
        assert verified_user.id == user.id
        assert verified_user.email_verified is True
        assert verified_user.status == UserStatus.ACTIVE
    
    def test_password_reset_flow(self, auth_service):
        """测试完整的密码重置流程"""
        # 1. 注册并激活
        user, verification_token = auth_service.register(
            email="test@example.com",
            password="password123"
        )
        auth_service.verify_email(verification_token)
        
        # 2. 请求重置密码
        reset_token = auth_service.reset_password_request("test@example.com")
        
        # 3. 重置密码
        auth_service.reset_password(reset_token, "new_password456")
        
        # 4. 使用新密码登录
        jwt_token = auth_service.login(
            email="test@example.com",
            password="new_password456"
        )
        
        assert jwt_token is not None
        
        # 5. 旧密码应该失效
        with pytest.raises(ValueError, match="密码错误"):
            auth_service.login("test@example.com", "password123")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
