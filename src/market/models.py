"""
策略市场数据模型

定义策略、评论、收藏等数据结构

@module: market.models
@author: OpenFinAgent Team
@version: 0.4.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class StrategyCategory(Enum):
    """策略分类"""
    CTA = "cta"  # CTA 策略
    ARBITRAGE = "arbitrage"  # 套利策略
    ML = "ml"  # 机器学习策略
    MEAN_REVERSION = "mean_reversion"  # 均值回归
    MOMENTUM = "momentum"  # 动量策略
    OTHER = "other"  # 其他


class StrategyStatus(Enum):
    """策略状态"""
    DRAFT = "draft"  # 草稿
    PUBLISHED = "published"  # 已发布
    ARCHIVED = "archived"  # 已归档
    SUSPENDED = "suspended"  # 已暂停


@dataclass
class Strategy:
    """
    策略数据模型
    
    Attributes:
        id: 策略 ID
        name: 策略名称
        description: 策略描述
        author_id: 作者 ID
        author_name: 作者名称
        code: 策略代码
        config: 策略配置
        backtest_report: 回测报告
        category: 策略分类
        tags: 标签列表
        downloads: 下载次数
        stars: 收藏数
        views: 浏览量
        version: 版本号
        status: 策略状态
        created_at: 创建时间
        updated_at: 更新时间
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    author_id: str = ""
    author_name: str = ""
    code: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    backtest_report: Dict[str, Any] = field(default_factory=dict)
    category: StrategyCategory = StrategyCategory.OTHER
    tags: List[str] = field(default_factory=list)
    downloads: int = 0
    stars: int = 0
    views: int = 0
    version: str = "1.0.0"
    status: StrategyStatus = StrategyStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'author_id': self.author_id,
            'author_name': self.author_name,
            'code': self.code,
            'config': self.config,
            'backtest_report': self.backtest_report,
            'category': self.category.value,
            'tags': self.tags,
            'downloads': self.downloads,
            'stars': self.stars,
            'views': self.views,
            'version': self.version,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Strategy':
        """从字典创建"""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            name=data.get('name', ''),
            description=data.get('description', ''),
            author_id=data.get('author_id', ''),
            author_name=data.get('author_name', ''),
            code=data.get('code', ''),
            config=data.get('config', {}),
            backtest_report=data.get('backtest_report', {}),
            category=StrategyCategory(data.get('category', 'other')),
            tags=data.get('tags', []),
            downloads=data.get('downloads', 0),
            stars=data.get('stars', 0),
            views=data.get('views', 0),
            version=data.get('version', '1.0.0'),
            status=StrategyStatus(data.get('status', 'draft')),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if 'updated_at' in data else datetime.now()
        )


@dataclass
class Comment:
    """
    评论数据模型
    
    Attributes:
        id: 评论 ID
        strategy_id: 策略 ID
        user_id: 用户 ID
        user_name: 用户名称
        content: 评论内容
        parent_id: 父评论 ID (回复)
        created_at: 创建时间
        updated_at: 更新时间
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    strategy_id: str = ""
    user_id: str = ""
    user_name: str = ""
    content: str = ""
    parent_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'strategy_id': self.strategy_id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'content': self.content,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Comment':
        """从字典创建"""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            strategy_id=data.get('strategy_id', ''),
            user_id=data.get('user_id', ''),
            user_name=data.get('user_name', ''),
            content=data.get('content', ''),
            parent_id=data.get('parent_id'),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if 'updated_at' in data else datetime.now()
        )


@dataclass
class Star:
    """
    收藏数据模型
    
    Attributes:
        strategy_id: 策略 ID
        user_id: 用户 ID
        created_at: 收藏时间
    """
    strategy_id: str = ""
    user_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'strategy_id': self.strategy_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class StrategyPackage:
    """
    策略包数据模型
    
    用于策略的导入导出
    
    Attributes:
        strategy: 策略元数据
        code_files: 代码文件字典 {filename: content}
        config: 配置文件
        backtest_data: 回测数据
        readme: README 文件内容
    """
    strategy: Strategy = field(default_factory=Strategy)
    code_files: Dict[str, str] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    backtest_data: Dict[str, Any] = field(default_factory=dict)
    readme: str = ""
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'strategy': self.strategy.to_dict(),
            'code_files': self.code_files,
            'config': self.config,
            'backtest_data': self.backtest_data,
            'readme': self.readme
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StrategyPackage':
        """从字典创建"""
        return cls(
            strategy=Strategy.from_dict(data.get('strategy', {})),
            code_files=data.get('code_files', {}),
            config=data.get('config', {}),
            backtest_data=data.get('backtest_data', {}),
            readme=data.get('readme', '')
        )
