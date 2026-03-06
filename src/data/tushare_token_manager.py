"""
Tushare Token 管理器模块

提供 Tushare API Token 的管理功能：
- 环境变量支持
- 配置文件支持
- Token 池 (多 Token 轮询)
- Token 健康检查
- 自动切换降级

@module: data.tushare_token_manager
@author: OpenFinAgent Team
@version: 1.0.0
"""

from typing import Optional, List, Dict, Any
import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import threading

logger = logging.getLogger(__name__)


class TokenInfo:
    """Token 信息类"""

    def __init__(
        self,
        token: str,
        name: str = "default",
        priority: int = 0,
        api_count: int = 0,
        last_used: Optional[datetime] = None,
        is_active: bool = True,
        error_count: int = 0,
        last_error: Optional[datetime] = None
    ):
        """
        初始化 Token 信息

        Args:
            token: Token 字符串
            name: Token 名称/备注
            priority: 优先级 (数字越大优先级越高)
            api_count: 已调用 API 次数
            last_used: 最后使用时间
            is_active: 是否激活
            error_count: 错误次数
            last_error: 最后错误时间
        """
        self.token = token
        self.name = name
        self.priority = priority
        self.api_count = api_count
        self.last_used = last_used or datetime.now()
        self.is_active = is_active
        self.error_count = error_count
        self.last_error = last_error

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'token': self.token,
            'name': self.name,
            'priority': self.priority,
            'api_count': self.api_count,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'is_active': self.is_active,
            'error_count': self.error_count,
            'last_error': self.last_error.isoformat() if self.last_error else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TokenInfo':
        """从字典创建"""
        return cls(
            token=data.get('token', ''),
            name=data.get('name', 'default'),
            priority=data.get('priority', 0),
            api_count=data.get('api_count', 0),
            last_used=datetime.fromisoformat(data['last_used']) if data.get('last_used') else None,
            is_active=data.get('is_active', True),
            error_count=data.get('error_count', 0),
            last_error=datetime.fromisoformat(data['last_error']) if data.get('last_error') else None
        )

    def record_usage(self):
        """记录使用"""
        self.api_count += 1
        self.last_used = datetime.now()

    def record_error(self):
        """记录错误"""
        self.error_count += 1
        self.last_error = datetime.now()

        # 错误次数过多自动禁用
        if self.error_count >= 10:
            self.is_active = False
            logger.warning(f"Token '{self.name}' 因错误次数过多已自动禁用")

    def reset_error(self):
        """重置错误计数"""
        self.error_count = 0
        self.last_error = None


class TushareTokenManager:
    """
    Tushare Token 管理器

    支持：
    - 单 Token 模式
    - 多 Token 池轮询
    - 配置文件持久化
    - 环境变量优先
    - 自动健康检查
    """

    DEFAULT_CONFIG_PATH = Path.home() / '.tradeflow' / 'tushare_config.json'

    def __init__(
        self,
        token: Optional[str] = None,
        tokens: Optional[List[TokenInfo]] = None,
        config_path: Optional[Path] = None,
        auto_save: bool = True,
        rotation_strategy: str = 'priority'  # 'priority' | 'round_robin' | 'least_used'
    ):
        """
        初始化 Token 管理器

        Args:
            token: 单个 Token (可选)
            tokens: Token 列表 (可选)
            config_path: 配置文件路径
            auto_save: 是否自动保存配置
            rotation_strategy: 轮询策略
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.auto_save = auto_save
        self.rotation_strategy = rotation_strategy
        self._lock = threading.RLock()
        self._current_index = 0

        # Token 池
        self._tokens: List[TokenInfo] = []

        # 初始化 Token
        if tokens:
            self._tokens = tokens
        elif token:
            self._tokens = [TokenInfo(token=token, name="default")]
        else:
            # 尝试从环境变量加载
            self._load_from_env()

        # 尝试从配置文件加载
        if self.config_path.exists():
            self._load_from_config()

        # 如果仍然没有 Token，尝试从环境变量获取
        if not self._tokens:
            env_token = os.getenv('TUSHARE_TOKEN')
            if env_token:
                self._tokens = [TokenInfo(token=env_token, name="env_default")]
                logger.info("从环境变量加载 Tushare Token")

        logger.info(f"Token 管理器初始化完成，当前有 {len(self._tokens)} 个 Token")

    def _load_from_env(self):
        """从环境变量加载 Token"""
        # 单个 Token
        token = os.getenv('TUSHARE_TOKEN')
        if token:
            self._tokens.append(TokenInfo(
                token=token,
                name=os.getenv('TUSHARE_TOKEN_NAME', 'env_default')
            ))

        # 多个 Token (TUSHARE_TOKEN_0, TUSHARE_TOKEN_1, ...)
        index = 0
        while True:
            env_token = os.getenv(f'TUSHARE_TOKEN_{index}')
            if not env_token:
                break

            token_name = os.getenv(f'TUSHARE_TOKEN_{index}_NAME', f'env_{index}')
            token_priority = int(os.getenv(f'TUSHARE_TOKEN_{index}_PRIORITY', '0'))

            self._tokens.append(TokenInfo(
                token=env_token,
                name=token_name,
                priority=token_priority
            ))
            index += 1

    def _load_from_config(self):
        """从配置文件加载 Token"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            tokens_data = config.get('tokens', [])
            if tokens_data:
                self._tokens = [TokenInfo.from_dict(t) for t in tokens_data]
                self.rotation_strategy = config.get('rotation_strategy', 'priority')
                logger.info(f"从配置文件加载 {len(self._tokens)} 个 Token")
        except Exception as e:
            logger.error(f"加载配置文件失败：{e}")

    def _save_to_config(self):
        """保存到配置文件"""
        if not self.auto_save:
            return

        try:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            config = {
                'tokens': [t.to_dict() for t in self._tokens],
                'rotation_strategy': self.rotation_strategy,
                'last_updated': datetime.now().isoformat()
            }

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            logger.debug(f"Token 配置已保存到：{self.config_path}")
        except Exception as e:
            logger.error(f"保存配置文件失败：{e}")

    def add_token(
        self,
        token: str,
        name: str = "default",
        priority: int = 0
    ):
        """
        添加 Token

        Args:
            token: Token 字符串
            name: Token 名称
            priority: 优先级
        """
        with self._lock:
            # 检查是否已存在
            for t in self._tokens:
                if t.token == token:
                    logger.warning(f"Token 已存在：{name}")
                    return

            self._tokens.append(TokenInfo(
                token=token,
                name=name,
                priority=priority
            ))

            logger.info(f"添加 Token: {name} (优先级={priority})")
            self._save_to_config()

    def remove_token(self, token: str) -> bool:
        """
        移除 Token

        Args:
            token: Token 字符串

        Returns:
            是否成功移除
        """
        with self._lock:
            for i, t in enumerate(self._tokens):
                if t.token == token:
                    removed = self._tokens.pop(i)
                    logger.info(f"移除 Token: {removed.name}")
                    self._save_to_config()
                    return True

            logger.warning(f"Token 不存在：{token}")
            return False

    def get_token(self) -> Optional[str]:
        """
        获取一个可用的 Token (根据轮询策略)

        Returns:
            Token 字符串或 None
        """
        with self._lock:
            # 筛选可用的 Token
            active_tokens = [t for t in self._tokens if t.is_active]

            if not active_tokens:
                logger.error("没有可用的 Token")
                return None

            # 根据策略选择 Token
            if self.rotation_strategy == 'priority':
                # 优先级最高的
                token = max(active_tokens, key=lambda t: t.priority)
            elif self.rotation_strategy == 'round_robin':
                # 轮询
                token = active_tokens[self._current_index % len(active_tokens)]
                self._current_index += 1
            elif self.rotation_strategy == 'least_used':
                # 最少使用的
                token = min(active_tokens, key=lambda t: t.api_count)
            else:
                token = active_tokens[0]

            token.record_usage()
            self._save_to_config()

            logger.debug(f"使用 Token: {token.name}")
            return token.token

    def get_token_info(self, token: str) -> Optional[TokenInfo]:
        """
        获取 Token 信息

        Args:
            token: Token 字符串

        Returns:
            TokenInfo 或 None
        """
        with self._lock:
            for t in self._tokens:
                if t.token == token:
                    return t
            return None

    def record_error(self, token: str):
        """
        记录 Token 错误

        Args:
            token: Token 字符串
        """
        with self._lock:
            for t in self._tokens:
                if t.token == token:
                    t.record_error()
                    break

            self._save_to_config()

    def reset_token_errors(self, token: str):
        """
        重置 Token 错误计数

        Args:
            token: Token 字符串
        """
        with self._lock:
            for t in self._tokens:
                if t.token == token:
                    t.reset_error()
                    t.is_active = True
                    logger.info(f"重置 Token 错误计数：{t.name}")
                    break

            self._save_to_config()

    def list_tokens(self) -> List[Dict[str, Any]]:
        """
        列出所有 Token (隐藏实际 Token 值)

        Returns:
            Token 信息列表
        """
        with self._lock:
            result = []
            for t in self._tokens:
                info = t.to_dict()
                info['token'] = '***HIDDEN***'
                result.append(info)
            return result

    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        with self._lock:
            active_count = sum(1 for t in self._tokens if t.is_active)
            total_calls = sum(t.api_count for t in self._tokens)
            total_errors = sum(t.error_count for t in self._tokens)

            return {
                'total_tokens': len(self._tokens),
                'active_tokens': active_count,
                'inactive_tokens': len(self._tokens) - active_count,
                'total_api_calls': total_calls,
                'total_errors': total_errors,
                'rotation_strategy': self.rotation_strategy
            }

    def health_check(self) -> Dict[str, bool]:
        """
        健康检查 (简单验证 Token 格式)

        Returns:
            Token 健康状态字典
        """
        results = {}

        for t in self._tokens:
            # 简单验证：Token 长度至少 32 位
            is_valid = len(t.token) >= 32 and t.is_active
            results[t.name] = is_valid

            if not is_valid and t.is_active:
                logger.warning(f"Token 可能无效：{t.name}")

        return results


# 全局单例
_global_manager: Optional[TushareTokenManager] = None


def get_token_manager() -> TushareTokenManager:
    """
    获取全局 Token 管理器实例

    Returns:
        Token 管理器实例
    """
    global _global_manager

    if _global_manager is None:
        _global_manager = TushareTokenManager()

    return _global_manager


def get_token() -> Optional[str]:
    """
    便捷函数：获取一个 Token

    Returns:
        Token 字符串或 None
    """
    return get_token_manager().get_token()


def init_token_manager(
    token: Optional[str] = None,
    tokens: Optional[List[TokenInfo]] = None,
    config_path: Optional[Path] = None,
    **kwargs
) -> TushareTokenManager:
    """
    初始化全局 Token 管理器

    Args:
        token: 单个 Token
        tokens: Token 列表
        config_path: 配置文件路径
        **kwargs: 其他参数

    Returns:
        Token 管理器实例
    """
    global _global_manager

    _global_manager = TushareTokenManager(
        token=token,
        tokens=tokens,
        config_path=config_path,
        **kwargs
    )

    return _global_manager
