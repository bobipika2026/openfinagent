"""
缓存工具 - 数据缓存和性能优化
"""

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
import pickle
from typing import Any, Optional


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: str = ".streamlit/cache", ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        self._memory_cache = {}
    
    def _generate_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = json.dumps({
            'args': args,
            'kwargs': kwargs
        }, sort_keys=True, default=str)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """从缓存获取数据"""
        # 先检查内存缓存
        if key in self._memory_cache:
            data, timestamp = self._memory_cache[key]
            if datetime.now() - timestamp < self.ttl:
                return data
            else:
                del self._memory_cache[key]
        
        # 检查磁盘缓存
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    data, timestamp = pickle.load(f)
                if datetime.now() - timestamp < self.ttl:
                    # 加载到内存缓存
                    self._memory_cache[key] = (data, timestamp)
                    return data
                else:
                    # 过期删除
                    cache_file.unlink()
            except Exception:
                pass
        
        return None
    
    def set(self, key: str, data: Any) -> None:
        """设置缓存"""
        timestamp = datetime.now()
        
        # 内存缓存
        self._memory_cache[key] = (data, timestamp)
        
        # 磁盘缓存
        cache_file = self.cache_dir / f"{key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump((data, timestamp), f)
        except Exception:
            pass
    
    def clear(self) -> None:
        """清空缓存"""
        self._memory_cache.clear()
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()
    
    def cleanup(self) -> int:
        """清理过期缓存，返回删除的文件数"""
        count = 0
        now = datetime.now()
        
        # 清理磁盘缓存
        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                with open(cache_file, 'rb') as f:
                    _, timestamp = pickle.load(f)
                if now - timestamp > self.ttl:
                    cache_file.unlink()
                    count += 1
            except Exception:
                cache_file.unlink()
                count += 1
        
        # 清理内存缓存
        expired_keys = [
            key for key, (_, timestamp) in self._memory_cache.items()
            if now - timestamp > self.ttl
        ]
        for key in expired_keys:
            del self._memory_cache[key]
        
        return count


# 全局缓存实例
cache = CacheManager()


def cached(ttl_hours: int = 24):
    """缓存装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{CacheManager()._generate_key(*args, **kwargs)}"
            
            # 尝试从缓存获取
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            
            return result
        return wrapper
    return decorator
