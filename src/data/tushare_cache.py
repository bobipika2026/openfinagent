"""
Tushare 缓存模块

提供数据缓存功能：
- 本地内存缓存
- 磁盘缓存 (可选)
- 缓存过期策略
- 缓存清理
- 缓存统计

@module: data.tushare_cache
@author: OpenFinAgent Team
@version: 1.0.0
"""

from typing import Optional, Dict, Any, List, Tuple
import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
import threading
import pickle
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """缓存条目"""

    key: str
    data: Any
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    size_bytes: int = 0

    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def touch(self):
        """更新访问时间"""
        self.access_count += 1
        self.last_accessed = datetime.now()


class TushareCache:
    """
    Tushare 数据缓存

    支持：
    - 内存缓存 (LRU)
    - 磁盘缓存 (可选)
    - 多种过期策略
    - 自动清理
    """

    def __init__(
        self,
        max_size: int = 1000,
        ttl_seconds: int = 3600,
        disk_cache: bool = False,
        disk_cache_dir: Optional[Path] = None,
        auto_cleanup: bool = True,
        cleanup_interval: int = 300
    ):
        """
        初始化缓存

        Args:
            max_size: 最大缓存条目数
            ttl_seconds: 默认过期时间 (秒)
            disk_cache: 是否启用磁盘缓存
            disk_cache_dir: 磁盘缓存目录
            auto_cleanup: 是否自动清理
            cleanup_interval: 自动清理间隔 (秒)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.disk_cache = disk_cache
        self.disk_cache_dir = disk_cache_dir
        self.auto_cleanup = auto_cleanup
        self.cleanup_interval = cleanup_interval

        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._last_cleanup = datetime.now()

        # 磁盘缓存初始化
        if self.disk_cache:
            self._init_disk_cache()

        logger.info(
            f"缓存初始化完成：max_size={max_size}, ttl={ttl_seconds}s, "
            f"disk_cache={disk_cache}"
        )

    def _init_disk_cache(self):
        """初始化磁盘缓存"""
        if self.disk_cache_dir is None:
            self.disk_cache_dir = Path.home() / '.tradeflow' / 'tushare_cache'

        self.disk_cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"磁盘缓存目录：{self.disk_cache_dir}")

    def _generate_key(
        self,
        api_name: str,
        params: Dict[str, Any]
    ) -> str:
        """
        生成缓存键

        Args:
            api_name: API 名称
            params: API 参数

        Returns:
            缓存键
        """
        # 序列化参数
        params_str = json.dumps(params, sort_keys=True, ensure_ascii=False)

        # 生成哈希
        key_str = f"{api_name}:{params_str}"
        key_hash = hashlib.md5(key_str.encode('utf-8')).hexdigest()

        return f"tushare:{api_name}:{key_hash}"

    def get(
        self,
        api_name: str,
        params: Dict[str, Any],
        use_disk: bool = True
    ) -> Optional[Any]:
        """
        从缓存获取数据

        Args:
            api_name: API 名称
            params: API 参数
            use_disk: 是否查找磁盘缓存

        Returns:
            缓存数据或 None
        """
        key = self._generate_key(api_name, params)

        with self._lock:
            # 检查内存缓存
            if key in self._cache:
                entry = self._cache[key]

                # 检查是否过期
                if entry.is_expired():
                    logger.debug(f"缓存过期：{key}")
                    self._remove(key)
                    return None

                entry.touch()
                logger.debug(f"缓存命中 (内存): {key}")
                return entry.data

            # 检查磁盘缓存
            if self.disk_cache and use_disk:
                data = self._load_from_disk(key)
                if data is not None:
                    # 加载到内存
                    self._store_in_memory(key, data)
                    logger.debug(f"缓存命中 (磁盘): {key}")
                    return data

            logger.debug(f"缓存未命中：{key}")
            return None

    def set(
        self,
        api_name: str,
        params: Dict[str, Any],
        data: Any,
        ttl_seconds: Optional[int] = None,
        save_to_disk: bool = True
    ):
        """
        存储数据到缓存

        Args:
            api_name: API 名称
            params: API 参数
            data: 数据
            ttl_seconds: 自定义过期时间
            save_to_disk: 是否保存到磁盘
        """
        key = self._generate_key(api_name, params)

        with self._lock:
            # 计算过期时间
            ttl = ttl_seconds if ttl_seconds is not None else self.ttl_seconds
            expires_at = datetime.now() + timedelta(seconds=ttl) if ttl > 0 else None

            # 计算大小
            try:
                size_bytes = len(pickle.dumps(data))
            except Exception:
                size_bytes = 0

            # 创建缓存条目
            entry = CacheEntry(
                key=key,
                data=data,
                expires_at=expires_at,
                size_bytes=size_bytes
            )

            # 存储到内存
            self._store_in_memory(key, entry)

            # 存储到磁盘
            if self.disk_cache and save_to_disk:
                self._save_to_disk(key, entry)

            # 检查是否需要清理
            if self.auto_cleanup:
                self._maybe_cleanup()

    def _store_in_memory(self, key: str, entry: CacheEntry):
        """存储到内存"""
        # 如果缓存已满，移除最久未使用的
        if len(self._cache) >= self.max_size:
            self._evict_lru()

        self._cache[key] = entry

    def _evict_lru(self):
        """移除最久未使用的条目"""
        if not self._cache:
            return

        # 找到最久未使用的
        lru_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_accessed
        )

        logger.debug(f"移除 LRU 缓存：{lru_key}")
        self._remove(lru_key)

    def _remove(self, key: str):
        """移除缓存条目"""
        if key in self._cache:
            del self._cache[key]

        # 同时移除磁盘缓存
        if self.disk_cache:
            self._remove_from_disk(key)

    def delete(
        self,
        api_name: str,
        params: Dict[str, Any]
    ):
        """
        删除缓存

        Args:
            api_name: API 名称
            params: API 参数
        """
        key = self._generate_key(api_name, params)

        with self._lock:
            self._remove(key)
            logger.debug(f"删除缓存：{key}")

    def clear(self):
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()

            if self.disk_cache:
                self._clear_disk_cache()

            logger.info("缓存已清空")

    def _maybe_cleanup(self):
        """检查是否需要清理"""
        now = datetime.now()
        if (now - self._last_cleanup).total_seconds() >= self.cleanup_interval:
            self.cleanup()
            self._last_cleanup = now

    def cleanup(self):
        """清理过期缓存"""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]

            for key in expired_keys:
                self._remove(key)

            if expired_keys:
                logger.info(f"清理了 {len(expired_keys)} 个过期缓存")

    def _save_to_disk(self, key: str, entry: CacheEntry):
        """保存到磁盘"""
        try:
            # 使用 key 的哈希作为文件名
            file_name = f"{hashlib.sha256(key.encode()).hexdigest()[:16]}.pkl"
            file_path = self.disk_cache_dir / file_name

            # 序列化并保存
            with open(file_path, 'wb') as f:
                pickle.dump(entry, f)

            logger.debug(f"保存到磁盘：{file_path}")
        except Exception as e:
            logger.error(f"磁盘缓存保存失败：{e}")

    def _load_from_disk(self, key: str) -> Optional[Any]:
        """从磁盘加载"""
        try:
            file_name = f"{hashlib.sha256(key.encode()).hexdigest()[:16]}.pkl"
            file_path = self.disk_cache_dir / file_name

            if not file_path.exists():
                return None

            with open(file_path, 'rb') as f:
                entry = pickle.load(f)

            # 检查是否过期
            if entry.is_expired():
                file_path.unlink(missing_ok=True)
                return None

            return entry.data

        except Exception as e:
            logger.error(f"磁盘缓存加载失败：{e}")
            return None

    def _remove_from_disk(self, key: str):
        """从磁盘移除"""
        try:
            file_name = f"{hashlib.sha256(key.encode()).hexdigest()[:16]}.pkl"
            file_path = self.disk_cache_dir / file_name

            if file_path.exists():
                file_path.unlink()
                logger.debug(f"删除磁盘缓存：{file_path}")
        except Exception as e:
            logger.error(f"删除磁盘缓存失败：{e}")

    def _clear_disk_cache(self):
        """清空磁盘缓存"""
        try:
            if self.disk_cache_dir and self.disk_cache_dir.exists():
                for file_path in self.disk_cache_dir.glob('*.pkl'):
                    file_path.unlink()

                logger.info("磁盘缓存已清空")
        except Exception as e:
            logger.error(f"清空磁盘缓存失败：{e}")

    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            统计信息
        """
        with self._lock:
            total_size = sum(e.size_bytes for e in self._cache.values())
            expired_count = sum(1 for e in self._cache.values() if e.is_expired())

            disk_count = 0
            if self.disk_cache and self.disk_cache_dir:
                disk_count = len(list(self.disk_cache_dir.glob('*.pkl')))

            return {
                'memory_entries': len(self._cache),
                'memory_size_bytes': total_size,
                'memory_size_mb': round(total_size / 1024 / 1024, 2),
                'expired_entries': expired_count,
                'disk_entries': disk_count,
                'max_size': self.max_size,
                'ttl_seconds': self.ttl_seconds,
                'hit_rate': self._calculate_hit_rate()
            }

    def _calculate_hit_rate(self) -> float:
        """计算命中率 (近似值)"""
        total_access = sum(e.access_count for e in self._cache.values())
        if total_access == 0:
            return 0.0

        # 简化计算：平均访问次数
        avg_access = total_access / len(self._cache) if self._cache else 0
        return min(1.0, avg_access / 10)  # 归一化到 0-1

    def get_cached_keys(self) -> List[str]:
        """
        获取所有缓存键

        Returns:
            缓存键列表
        """
        with self._lock:
            return list(self._cache.keys())

    def warm_up(
        self,
        api_name: str,
        params_list: List[Dict[str, Any]],
        fetch_func: callable
    ):
        """
        预热缓存

        Args:
            api_name: API 名称
            params_list: 参数列表
            fetch_func: 数据获取函数
        """
        logger.info(f"开始预热缓存：{api_name}, {len(params_list)} 个请求")

        success_count = 0
        for params in params_list:
            try:
                # 检查是否已缓存
                if self.get(api_name, params) is None:
                    # 获取数据
                    data = fetch_func(params)
                    if data is not None:
                        self.set(api_name, params, data)
                        success_count += 1
            except Exception as e:
                logger.error(f"预热失败：{params}, 错误：{e}")

        logger.info(f"缓存预热完成：{success_count}/{len(params_list)} 成功")


# 全局缓存实例
_global_cache: Optional[TushareCache] = None


def get_cache() -> TushareCache:
    """
    获取全局缓存实例

    Returns:
        缓存实例
    """
    global _global_cache

    if _global_cache is None:
        _global_cache = TushareCache()

    return _global_cache


def init_cache(
    max_size: int = 1000,
    ttl_seconds: int = 3600,
    **kwargs
) -> TushareCache:
    """
    初始化全局缓存

    Args:
        max_size: 最大缓存条目数
        ttl_seconds: 默认过期时间
        **kwargs: 其他参数

    Returns:
        缓存实例
    """
    global _global_cache

    _global_cache = TushareCache(
        max_size=max_size,
        ttl_seconds=ttl_seconds,
        **kwargs
    )

    return _global_cache


def cache_data(
    api_name: str,
    params: Dict[str, Any],
    data: Any,
    ttl_seconds: Optional[int] = None
):
    """
    便捷函数：缓存数据

    Args:
        api_name: API 名称
        params: 参数
        data: 数据
        ttl_seconds: 过期时间
    """
    get_cache().set(api_name, params, data, ttl_seconds)


def get_cached_data(
    api_name: str,
    params: Dict[str, Any]
) -> Optional[Any]:
    """
    便捷函数：获取缓存数据

    Args:
        api_name: API 名称
        params: 参数

    Returns:
        缓存数据或 None
    """
    return get_cache().get(api_name, params)
