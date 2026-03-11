"""
股票池管理

管理股票池的创建、更新、删除和持久化

@module: stock_selector.pool_manager
@author: OpenFinAgent Team
@version: 1.0.0
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class StockPool:
    """
    股票池数据类
    
    存储股票池的完整信息
    
    Attributes:
        name: 股票池名称
        stocks: 股票代码列表
        strategy_id: 关联的策略 ID
        created_at: 创建时间
        updated_at: 更新时间
        description: 描述信息
        tags: 标签列表
        metadata: 元数据
    
    Example:
        ```python
        pool = StockPool(
            name='优质成长股',
            stocks=['000001.SZ', '000002.SZ', '600000.SH'],
            strategy_id='strategy_001',
            description='高成长性的优质股票池'
        )
        ```
    """
    
    name: str
    stocks: List[str] = field(default_factory=list)
    strategy_id: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    description: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_stock(self, symbol: str) -> bool:
        """
        添加股票到股票池
        
        Args:
            symbol: 股票代码
        
        Returns:
            是否添加成功 (False 表示已存在)
        """
        if symbol not in self.stocks:
            self.stocks.append(symbol)
            self.updated_at = datetime.now().isoformat()
            logger.info(f"股票 {symbol} 已添加到股票池 {self.name}")
            return True
        return False
    
    def remove_stock(self, symbol: str) -> bool:
        """
        从股票池移除股票
        
        Args:
            symbol: 股票代码
        
        Returns:
            是否移除成功 (False 表示不存在)
        """
        if symbol in self.stocks:
            self.stocks.remove(symbol)
            self.updated_at = datetime.now().isoformat()
            logger.info(f"股票 {symbol} 已从股票池 {self.name} 移除")
            return True
        return False
    
    def has_stock(self, symbol: str) -> bool:
        """检查股票是否在池中"""
        return symbol in self.stocks
    
    def count(self) -> int:
        """返回股票数量"""
        return len(self.stocks)
    
    def clear(self) -> None:
        """清空股票池"""
        self.stocks = []
        self.updated_at = datetime.now().isoformat()
        logger.info(f"股票池 {self.name} 已清空")
    
    def update_stocks(self, stocks: List[str]) -> None:
        """
        批量更新股票列表
        
        Args:
            stocks: 新的股票列表
        """
        self.stocks = stocks
        self.updated_at = datetime.now().isoformat()
        logger.info(f"股票池 {self.name} 已更新，共 {len(stocks)} 只股票")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            股票池字典
        """
        return {
            'name': self.name,
            'stocks': self.stocks,
            'strategy_id': self.strategy_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'description': self.description,
            'tags': self.tags,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StockPool':
        """
        从字典创建实例
        
        Args:
            data: 股票池字典
        
        Returns:
            StockPool 实例
        """
        return cls(**data)
    
    def __repr__(self) -> str:
        return f"StockPool(name='{self.name}', count={len(self.stocks)})"


class PoolManager:
    """
    股票池管理器
    
    管理多个股票池的创建、更新、删除和持久化
    
    Attributes:
        storage_path: 存储路径
        pools: 股票池字典
    
    Example:
        ```python
        # 初始化管理器
        manager = PoolManager(storage_path='./data/pools')
        
        # 创建股票池
        pool = manager.create_pool(
            name='优质成长股',
            stocks=['000001.SZ', '000002.SZ'],
            strategy_id='strategy_001'
        )
        
        # 获取股票池
        pool = manager.get_pool('优质成长股')
        
        # 删除股票池
        manager.delete_pool('优质成长股')
        ```
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        初始化股票池管理器
        
        Args:
            storage_path: 存储路径 (默认：~/.tradeflow/pools)
        """
        if storage_path is None:
            home_dir = Path.home()
            storage_path = str(home_dir / '.tradeflow' / 'pools')
        
        self.storage_path = storage_path
        self.pools: Dict[str, StockPool] = {}
        
        # 确保存储目录存在
        self._ensure_storage_dir()
        
        # 加载已保存的股票池
        self._load_pools()
        
        logger.info(f"股票池管理器初始化完成，存储路径：{self.storage_path}")
    
    def _ensure_storage_dir(self) -> None:
        """确保存储目录存在"""
        path = Path(self.storage_path)
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"存储目录已确保存在：{self.storage_path}")
    
    def _get_pool_file(self, pool_name: str) -> str:
        """
        获取股票池文件路径
        
        Args:
            pool_name: 股票池名称
        
        Returns:
            文件路径
        """
        # 使用安全的文件名 (替换特殊字符)
        safe_name = pool_name.replace('/', '_').replace('\\', '_')
        return os.path.join(self.storage_path, f"{safe_name}.json")
    
    def _load_pools(self) -> None:
        """从磁盘加载所有股票池"""
        if not os.path.exists(self.storage_path):
            logger.debug("存储目录不存在，跳过加载")
            return
        
        count = 0
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(self.storage_path, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        pool = StockPool.from_dict(data)
                        self.pools[pool.name] = pool
                        count += 1
                except Exception as e:
                    logger.warning(f"加载股票池文件 {filename} 失败：{e}")
        
        logger.info(f"已加载 {count} 个股票池")
    
    def create_pool(
        self,
        name: str,
        stocks: List[str],
        strategy_id: str = "",
        description: str = "",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> StockPool:
        """
        创建股票池
        
        Args:
            name: 股票池名称
            stocks: 股票代码列表
            strategy_id: 关联的策略 ID
            description: 描述信息
            tags: 标签列表
            metadata: 元数据
        
        Returns:
            创建的 StockPool 实例
        
        Raises:
            ValueError: 当股票池已存在时
        """
        if name in self.pools:
            raise ValueError(f"股票池 '{name}' 已存在")
        
        pool = StockPool(
            name=name,
            stocks=stocks,
            strategy_id=strategy_id,
            description=description,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        self.pools[name] = pool
        self._save_pool(pool)
        
        logger.info(f"创建股票池：{name}, 包含 {len(stocks)} 只股票")
        return pool
    
    def get_pool(self, name: str) -> Optional[StockPool]:
        """
        获取股票池
        
        Args:
            name: 股票池名称
        
        Returns:
            StockPool 实例，不存在返回 None
        """
        return self.pools.get(name)
    
    def update_pool(
        self,
        name: str,
        stocks: Optional[List[str]] = None,
        strategy_id: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        更新股票池
        
        Args:
            name: 股票池名称
            stocks: 新的股票列表 (不提供则保持不变)
            strategy_id: 新的策略 ID
            description: 新的描述
            tags: 新的标签
            metadata: 新的元数据
        
        Returns:
            是否更新成功
        
        Raises:
            ValueError: 当股票池不存在时
        """
        if name not in self.pools:
            raise ValueError(f"股票池 '{name}' 不存在")
        
        pool = self.pools[name]
        
        if stocks is not None:
            pool.stocks = stocks
        if strategy_id is not None:
            pool.strategy_id = strategy_id
        if description is not None:
            pool.description = description
        if tags is not None:
            pool.tags = tags
        if metadata is not None:
            pool.metadata = metadata
        
        pool.updated_at = datetime.now().isoformat()
        self._save_pool(pool)
        
        logger.info(f"更新股票池：{name}")
        return True
    
    def delete_pool(self, name: str) -> bool:
        """
        删除股票池
        
        Args:
            name: 股票池名称
        
        Returns:
            是否删除成功
        """
        if name not in self.pools:
            logger.warning(f"股票池 '{name}' 不存在，无法删除")
            return False
        
        # 删除文件
        filepath = self._get_pool_file(name)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.debug(f"已删除文件：{filepath}")
        except Exception as e:
            logger.warning(f"删除文件 {filepath} 失败：{e}")
        
        # 从内存中移除
        del self.pools[name]
        logger.info(f"股票池 '{name}' 已删除")
        return True
    
    def list_pools(self) -> List[str]:
        """
        列出所有股票池名称
        
        Returns:
            股票池名称列表
        """
        return list(self.pools.keys())
    
    def get_all_pools(self) -> Dict[str, StockPool]:
        """
        获取所有股票池
        
        Returns:
            股票池字典
        """
        return self.pools.copy()
    
    def pool_exists(self, name: str) -> bool:
        """检查股票池是否存在"""
        return name in self.pools
    
    def count_pools(self) -> int:
        """返回股票池数量"""
        return len(self.pools)
    
    def _save_pool(self, pool: StockPool) -> None:
        """
        保存股票池到磁盘
        
        Args:
            pool: StockPool 实例
        """
        filepath = self._get_pool_file(pool.name)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(pool.to_dict(), f, ensure_ascii=False, indent=2)
            logger.debug(f"股票池已保存：{filepath}")
        except Exception as e:
            logger.error(f"保存股票池 {pool.name} 失败：{e}")
            raise
    
    def export_pool(self, name: str, filepath: str) -> bool:
        """
        导出股票池到指定文件
        
        Args:
            name: 股票池名称
            filepath: 导出文件路径
        
        Returns:
            是否导出成功
        """
        if name not in self.pools:
            logger.warning(f"股票池 '{name}' 不存在")
            return False
        
        pool = self.pools[name]
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(pool.to_dict(), f, ensure_ascii=False, indent=2)
            logger.info(f"股票池 '{name}' 已导出到：{filepath}")
            return True
        except Exception as e:
            logger.error(f"导出股票池失败：{e}")
            return False
    
    def import_pool(self, filepath: str, overwrite: bool = False) -> Optional[StockPool]:
        """
        从文件导入股票池
        
        Args:
            filepath: 导入文件路径
            overwrite: 是否覆盖已存在的同名股票池
        
        Returns:
            导入的 StockPool 实例，失败返回 None
        
        Raises:
            ValueError: 当股票池已存在且 overwrite=False 时
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            pool = StockPool.from_dict(data)
            
            if pool.name in self.pools and not overwrite:
                raise ValueError(
                    f"股票池 '{pool.name}' 已存在，设置 overwrite=True 覆盖"
                )
            
            self.pools[pool.name] = pool
            self._save_pool(pool)
            
            logger.info(f"从 {filepath} 导入股票池：{pool.name}")
            return pool
            
        except Exception as e:
            logger.error(f"导入股票池失败：{e}")
            return None
    
    def merge_pools(
        self,
        pool_names: List[str],
        new_pool_name: str,
        remove_duplicates: bool = True
    ) -> Optional[StockPool]:
        """
        合并多个股票池
        
        Args:
            pool_names: 要合并的股票池名称列表
            new_pool_name: 新股票池名称
            remove_duplicates: 是否去重
        
        Returns:
            合并后的 StockPool 实例，失败返回 None
        """
        all_stocks: List[str] = []
        
        for name in pool_names:
            if name not in self.pools:
                logger.warning(f"股票池 '{name}' 不存在，跳过")
                continue
            
            pool = self.pools[name]
            all_stocks.extend(pool.stocks)
        
        if not all_stocks:
            logger.warning("没有股票池可合并")
            return None
        
        # 去重
        if remove_duplicates:
            seen: Set[str] = set()
            unique_stocks = []
            for stock in all_stocks:
                if stock not in seen:
                    seen.add(stock)
                    unique_stocks.append(stock)
            all_stocks = unique_stocks
        
        # 创建新股票池
        try:
            new_pool = self.create_pool(
                name=new_pool_name,
                stocks=all_stocks,
                description=f"合并自：{', '.join(pool_names)}"
            )
            logger.info(
                f"合并 {len(pool_names)} 个股票池，"
                f"新池 '{new_pool_name}' 包含 {len(all_stocks)} 只股票"
            )
            return new_pool
        except ValueError as e:
            logger.error(f"合并股票池失败：{e}")
            return None
    
    def get_pool_stats(self, name: str) -> Dict[str, Any]:
        """
        获取股票池统计信息
        
        Args:
            name: 股票池名称
        
        Returns:
            统计信息字典
        """
        if name not in self.pools:
            return {}
        
        pool = self.pools[name]
        
        return {
            'name': pool.name,
            'stock_count': len(pool.stocks),
            'strategy_id': pool.strategy_id,
            'created_at': pool.created_at,
            'updated_at': pool.updated_at,
            'tags': pool.tags,
            'description': pool.description
        }
    
    def clear_all_pools(self) -> int:
        """
        清空所有股票池
        
        Returns:
            删除的股票池数量
        """
        count = len(self.pools)
        
        # 删除所有文件
        for pool_name in list(self.pools.keys()):
            filepath = self._get_pool_file(pool_name)
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception as e:
                logger.warning(f"删除文件 {filepath} 失败：{e}")
        
        # 清空内存
        self.pools.clear()
        
        logger.info(f"已清空所有 {count} 个股票池")
        return count


# 便捷函数
def create_pool_manager(storage_path: Optional[str] = None) -> PoolManager:
    """
    创建股票池管理器
    
    Args:
        storage_path: 存储路径
    
    Returns:
        PoolManager 实例
    """
    return PoolManager(storage_path)
