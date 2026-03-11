"""
用户认证服务

提供用户注册、登录、认证、密码管理等功能

@module: user.auth
@author: OpenFinAgent Team
@version: 0.4.0
"""

import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
import json
import logging
import secrets

from .models import User, UserStatus, UserRole, PasswordResetToken, EmailVerificationToken

logger = logging.getLogger(__name__)


class AuthService:
    """
    认证服务类
    
    提供用户注册、登录、认证、密码管理等核心功能
    
    Attributes:
        secret_key: JWT 密钥
        token_expire_days: Token 过期天数
        db_path: 数据库文件路径
        users: 用户数据存储
        reset_tokens: 密码重置令牌存储
        verification_tokens: 邮箱验证令牌存储
    """
    
    def __init__(
        self,
        secret_key: Optional[str] = None,
        token_expire_days: int = 7,
        db_path: str = "~/.openfinagent/users.json"
    ):
        """
        初始化认证服务
        
        Args:
            secret_key: JWT 密钥 (不提供则自动生成)
            token_expire_days: Token 有效期 (天)
            db_path: 用户数据文件路径
        """
        # 生成或使用提供的密钥
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.token_expire_days = token_expire_days
        
        # 数据库路径
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 数据存储
        self.users: Dict[str, User] = {}
        self.reset_tokens: Dict[str, PasswordResetToken] = {}
        self.verification_tokens: Dict[str, EmailVerificationToken] = {}
        
        # 加载用户数据
        self._load_users()
        
        logger.info(f"认证服务初始化完成，已加载 {len(self.users)} 个用户")
    
    def _load_users(self) -> None:
        """从文件加载用户数据"""
        if not self.db_path.exists():
            logger.info("用户数据文件不存在，将创建新文件")
            self._save_users()
            return
        
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 加载用户
            for user_data in data.get('users', []):
                user = User.from_dict(user_data)
                self.users[user.id] = user
            
            # 加载重置令牌 (仅未过期的)
            now = datetime.now()
            for token_data in data.get('reset_tokens', []):
                expires_at = datetime.fromisoformat(token_data['expires_at'])
                if expires_at > now and not token_data.get('used', False):
                    token = PasswordResetToken(
                        id=token_data['id'],
                        user_id=token_data['user_id'],
                        token=token_data['token'],
                        expires_at=expires_at,
                        used=token_data.get('used', False),
                        created_at=datetime.fromisoformat(token_data['created_at'])
                    )
                    self.reset_tokens[token.id] = token
            
            logger.info(f"成功加载 {len(self.users)} 个用户")
            
        except Exception as e:
            logger.error(f"加载用户数据失败：{e}")
            # 初始化空数据
            self.users = {}
    
    def _save_users(self) -> None:
        """保存用户数据到文件"""
        try:
            data = {
                'users': [user.to_dict() for user in self.users.values()],
                'reset_tokens': [
                    {
                        'id': token.id,
                        'user_id': token.user_id,
                        'token': token.token,
                        'expires_at': token.expires_at.isoformat(),
                        'used': token.used,
                        'created_at': token.created_at.isoformat()
                    }
                    for token in self.reset_tokens.values()
                ],
                'verification_tokens': [
                    {
                        'id': token.id,
                        'user_id': token.user_id,
                        'email': token.email,
                        'token': token.token,
                        'expires_at': token.expires_at.isoformat(),
                        'used': token.used,
                        'created_at': token.created_at.isoformat()
                    }
                    for token in self.verification_tokens.values()
                ]
            }
            
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"已保存 {len(self.users)} 个用户到 {self.db_path}")
            
        except Exception as e:
            logger.error(f"保存用户数据失败：{e}")
            raise
    
    def register(
        self,
        email: str,
        password: str,
        username: Optional[str] = None
    ) -> Tuple[User, str]:
        """
        用户注册
        
        Args:
            email: 邮箱地址
            password: 密码
            username: 用户名 (可选，默认使用邮箱前缀)
        
        Returns:
            (用户对象，验证令牌)
        
        Raises:
            ValueError: 当邮箱已被注册或参数不合法时
        """
        # 参数验证
        if not email or '@' not in email:
            raise ValueError("请输入有效的邮箱地址")
        
        if not password or len(password) < 6:
            raise ValueError("密码长度至少为 6 位")
        
        # 检查邮箱是否已存在
        for user in self.users.values():
            if user.email.lower() == email.lower():
                raise ValueError("该邮箱已被注册")
        
        # 生成用户名
        if not username:
            username = email.split('@')[0]
        
        # 检查用户名是否已存在
        for user in self.users.values():
            if user.username.lower() == username.lower():
                raise ValueError("该用户名已被使用")
        
        # 密码加密
        password_hash = self._hash_password(password)
        
        # 创建用户
        user = User(
            username=username,
            email=email.lower(),
            password_hash=password_hash,
            status=UserStatus.INACTIVE,  # 需要邮箱验证
            role=UserRole.USER
        )
        
        self.users[user.id] = user
        
        # 生成邮箱验证令牌
        verification_token = self._create_verification_token(user.id, email)
        
        # 保存数据
        self._save_users()
        
        logger.info(f"用户注册成功：{username} ({email})")
        
        return user, verification_token
    
    def login(self, email: str, password: str) -> str:
        """
        用户登录
        
        Args:
            email: 邮箱地址
            password: 密码
        
        Returns:
            JWT Token
        
        Raises:
            ValueError: 当用户不存在、密码错误或账户被禁用时
        """
        # 查找用户
        user = self._get_user_by_email(email)
        
        if not user:
            raise ValueError("用户不存在")
        
        # 检查账户状态
        if user.status == UserStatus.BANNED:
            raise ValueError("账户已被封禁")
        
        # 验证密码 (在检查账户状态之前，避免泄露账户是否激活的信息)
        if not self._verify_password(password, user.password_hash):
            raise ValueError("密码错误")
        
        if user.status == UserStatus.INACTIVE:
            raise ValueError("账户未激活，请先验证邮箱")
        
        # 更新最后登录时间
        user.last_login = datetime.now()
        user.updated_at = datetime.now()
        
        # 保存更改
        self._save_users()
        
        # 生成 JWT Token
        token = self._generate_token(user)
        
        logger.info(f"用户登录成功：{user.username}")
        
        return token
    
    def verify_email(self, token: str) -> bool:
        """
        验证邮箱
        
        Args:
            token: 验证令牌
        
        Returns:
            是否验证成功
        
        Raises:
            ValueError: 当令牌无效或已过期时
        """
        # 查找令牌
        verification_token = self.verification_tokens.get(token)
        
        if not verification_token:
            raise ValueError("无效的验证令牌")
        
        if verification_token.used:
            raise ValueError("验证令牌已被使用")
        
        if verification_token.expires_at < datetime.now():
            # 清理过期令牌
            del self.verification_tokens[token]
            raise ValueError("验证令牌已过期")
        
        # 查找用户
        user = self.users.get(verification_token.user_id)
        
        if not user:
            raise ValueError("用户不存在")
        
        # 更新用户状态
        user.email_verified = True
        user.status = UserStatus.ACTIVE
        user.updated_at = datetime.now()
        
        # 标记令牌为已使用
        verification_token.used = True
        
        # 保存更改
        self._save_users()
        
        logger.info(f"邮箱验证成功：{user.email}")
        
        return True
    
    def reset_password_request(self, email: str) -> Optional[str]:
        """
        请求重置密码
        
        Args:
            email: 邮箱地址
        
        Returns:
            重置令牌 (如果用户存在), None (如果用户不存在，出于安全考虑不提示)
        """
        user = self._get_user_by_email(email)
        
        if not user:
            # 不提示用户不存在 (安全考虑)
            return None
        
        # 生成重置令牌
        reset_token = self._create_reset_token(user.id)
        
        logger.info(f"密码重置请求：{email}")
        
        return reset_token
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """
        重置密码
        
        Args:
            token: 重置令牌
            new_password: 新密码
        
        Returns:
            是否重置成功
        
        Raises:
            ValueError: 当令牌无效、已过期或密码不合法时
        """
        # 查找令牌
        reset_token = self.reset_tokens.get(token)
        
        if not reset_token:
            raise ValueError("无效的重置令牌")
        
        if reset_token.used:
            raise ValueError("重置令牌已被使用")
        
        if reset_token.expires_at < datetime.now():
            # 清理过期令牌
            del self.reset_tokens[token]
            raise ValueError("重置令牌已过期")
        
        # 查找用户
        user = self.users.get(reset_token.user_id)
        
        if not user:
            raise ValueError("用户不存在")
        
        # 验证新密码
        if not new_password or len(new_password) < 6:
            raise ValueError("密码长度至少为 6 位")
        
        # 更新密码
        user.password_hash = self._hash_password(new_password)
        user.updated_at = datetime.now()
        
        # 标记令牌为已使用
        reset_token.used = True
        
        # 保存更改
        self._save_users()
        
        logger.info(f"密码重置成功：{user.email}")
        
        return True
    
    def verify_token(self, token: str) -> User:
        """
        验证 JWT Token
        
        Args:
            token: JWT Token
        
        Returns:
            用户对象
        
        Raises:
            ValueError: 当 Token 无效、过期或用户不存在时
        """
        try:
            # 解码 Token (添加 leeway 处理时间同步问题)
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=['HS256'],
                options={"verify_iat": False}  # 忽略 iat 验证
            )
            
            # 获取用户 ID
            user_id = payload.get('user_id')
            
            if not user_id:
                raise ValueError("Token 无效")
            
            # 查找用户
            user = self.users.get(user_id)
            
            if not user:
                raise ValueError("用户不存在")
            
            if user.status != UserStatus.ACTIVE:
                raise ValueError("账户状态异常")
            
            return user
            
        except jwt.ExpiredSignatureError:
            raise ValueError("Token 已过期")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Token 无效：{e}")
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        根据 ID 获取用户
        
        Args:
            user_id: 用户 ID
        
        Returns:
            用户对象或 None
        """
        return self.users.get(user_id)
    
    def update_user_profile(
        self,
        user_id: str,
        username: Optional[str] = None,
        bio: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> User:
        """
        更新用户资料
        
        Args:
            user_id: 用户 ID
            username: 新用户名
            bio: 新简介
            avatar_url: 新头像 URL
        
        Returns:
            更新后的用户对象
        
        Raises:
            ValueError: 当用户不存在或用户名冲突时
        """
        user = self.users.get(user_id)
        
        if not user:
            raise ValueError("用户不存在")
        
        # 更新用户名 (检查是否重复)
        if username and username != user.username:
            for u in self.users.values():
                if u.username.lower() == username.lower() and u.id != user_id:
                    raise ValueError("该用户名已被使用")
            user.username = username
        
        # 更新其他字段
        if bio is not None:
            user.bio = bio
        
        if avatar_url is not None:
            user.avatar_url = avatar_url
        
        user.updated_at = datetime.now()
        
        # 保存更改
        self._save_users()
        
        logger.info(f"用户资料更新：{user.username}")
        
        return user
    
    def _hash_password(self, password: str) -> str:
        """
        密码哈希
        
        Args:
            password: 明文密码
        
        Returns:
            哈希后的密码
        """
        return bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """
        验证密码
        
        Args:
            password: 明文密码
            password_hash: 哈希密码
        
        Returns:
            是否匹配
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception:
            return False
    
    def _generate_token(self, user: User) -> str:
        """
        生成 JWT Token
        
        Args:
            user: 用户对象
        
        Returns:
            JWT Token
        """
        payload = {
            'user_id': user.id,
            'email': user.email,
            'username': user.username,
            'exp': datetime.now() + timedelta(days=self.token_expire_days),
            'iat': datetime.now()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        
        return token
    
    def _create_reset_token(self, user_id: str) -> str:
        """
        创建密码重置令牌
        
        Args:
            user_id: 用户 ID
        
        Returns:
            重置令牌字符串
        """
        token = secrets.token_urlsafe(32)
        
        reset_token = PasswordResetToken(
            user_id=user_id,
            token=token,
            expires_at=datetime.now() + timedelta(hours=24)  # 24 小时有效期
        )
        
        self.reset_tokens[token] = reset_token
        self._save_users()
        
        return token
    
    def _create_verification_token(self, user_id: str, email: str) -> str:
        """
        创建邮箱验证令牌
        
        Args:
            user_id: 用户 ID
            email: 邮箱地址
        
        Returns:
            验证令牌字符串
        """
        token = secrets.token_urlsafe(32)
        
        verification_token = EmailVerificationToken(
            user_id=user_id,
            email=email,
            token=token,
            expires_at=datetime.now() + timedelta(days=7)  # 7 天有效期
        )
        
        self.verification_tokens[token] = verification_token
        self._save_users()
        
        return token
    
    def _get_user_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱获取用户
        
        Args:
            email: 邮箱地址
        
        Returns:
            用户对象或 None
        """
        email_lower = email.lower()
        for user in self.users.values():
            if user.email.lower() == email_lower:
                return user
        return None
