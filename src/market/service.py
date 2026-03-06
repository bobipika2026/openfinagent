"""
策略市场服务

提供策略上传、浏览、搜索、下载、收藏、评论等功能

@module: market.service
@author: OpenFinAgent Team
@version: 0.4.0
"""

from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
import json
import logging
from datetime import datetime

from .models import (
    Strategy, StrategyCategory, StrategyStatus,
    Comment, Star, StrategyPackage
)

logger = logging.getLogger(__name__)


class MarketService:
    """
    策略市场服务
    
    提供策略的完整生命周期管理：
    - 上传/发布策略
    - 浏览/搜索策略
    - 下载策略
    - 收藏/取消收藏
    - 评论/回复
    
    Attributes:
        db_path: 数据文件路径
        strategies: 策略字典
        comments: 评论字典
        stars: 收藏列表
    """
    
    def __init__(self, db_path: str = "~/.openfinagent/market.json"):
        """
        初始化策略市场服务
        
        Args:
            db_path: 数据文件路径
        """
        from pathlib import Path
        
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 数据存储
        self.strategies: Dict[str, Strategy] = {}
        self.comments: Dict[str, List[Comment]] = {}  # strategy_id -> comments
        self.stars: List[Star] = []
        
        # 加载数据
        self._load_data()
        
        logger.info(f"策略市场服务初始化完成，已加载 {len(self.strategies)} 个策略")
    
    def _load_data(self) -> None:
        """从文件加载数据"""
        if not self.db_path.exists():
            logger.info("市场数据文件不存在，将创建新文件")
            self._save_data()
            return
        
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 加载策略
            for strategy_data in data.get('strategies', []):
                strategy = Strategy.from_dict(strategy_data)
                self.strategies[strategy.id] = strategy
            
            # 加载评论
            for strategy_id, comments_data in data.get('comments', {}).items():
                self.comments[strategy_id] = [
                    Comment.from_dict(c) for c in comments_data
                ]
            
            # 加载收藏
            self.stars = [Star.from_dict(s) for s in data.get('stars', [])]
            
            logger.info(f"成功加载 {len(self.strategies)} 个策略，{len(self.stars)} 个收藏")
            
        except Exception as e:
            logger.error(f"加载市场数据失败：{e}")
            # 初始化空数据
            self.strategies = {}
            self.comments = {}
            self.stars = []
    
    def _save_data(self) -> None:
        """保存数据到文件"""
        try:
            data = {
                'strategies': [s.to_dict() for s in self.strategies.values()],
                'comments': {
                    strategy_id: [c.to_dict() for c in comments]
                    for strategy_id, comments in self.comments.items()
                },
                'stars': [s.to_dict() for s in self.stars]
            }
            
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"已保存市场数据到 {self.db_path}")
            
        except Exception as e:
            logger.error(f"保存市场数据失败：{e}")
            raise
    
    def upload_strategy(
        self,
        name: str,
        code: str,
        author_id: str,
        author_name: str,
        description: str = "",
        config: Optional[Dict[str, Any]] = None,
        backtest_report: Optional[Dict[str, Any]] = None,
        category: str = "other",
        tags: Optional[List[str]] = None,
        status: str = "draft"
    ) -> Strategy:
        """
        上传策略
        
        Args:
            name: 策略名称
            code: 策略代码
            author_id: 作者 ID
            author_name: 作者名称
            description: 策略描述
            config: 策略配置
            backtest_report: 回测报告
            category: 策略分类
            tags: 标签列表
            status: 策略状态
        
        Returns:
            策略对象
        
        Raises:
            ValueError: 当参数不合法时
        """
        # 参数验证
        if not name or not name.strip():
            raise ValueError("策略名称不能为空")
        
        if not code or not code.strip():
            raise ValueError("策略代码不能为空")
        
        # 验证策略代码 (基本检查)
        if not self._validate_strategy_code(code):
            raise ValueError("策略代码格式不正确")
        
        # 创建策略
        strategy = Strategy(
            name=name.strip(),
            description=description,
            author_id=author_id,
            author_name=author_name,
            code=code,
            config=config or {},
            backtest_report=backtest_report or {},
            category=StrategyCategory(category),
            tags=tags or [],
            status=StrategyStatus(status)
        )
        
        # 保存策略
        self.strategies[strategy.id] = strategy
        self._save_data()
        
        logger.info(f"策略上传成功：{strategy.name} ({strategy.id})")
        
        return strategy
    
    def update_strategy(
        self,
        strategy_id: str,
        author_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        code: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> Strategy:
        """
        更新策略
        
        Args:
            strategy_id: 策略 ID
            author_id: 作者 ID (用于权限验证)
            name: 新名称
            description: 新描述
            code: 新代码
            config: 新配置
            tags: 新标签
        
        Returns:
            更新后的策略对象
        
        Raises:
            ValueError: 当策略不存在或无权限时
        """
        strategy = self.strategies.get(strategy_id)
        
        if not strategy:
            raise ValueError("策略不存在")
        
        # 权限检查
        if strategy.author_id != author_id:
            raise ValueError("无权限修改他人策略")
        
        # 更新字段
        if name:
            strategy.name = name.strip()
        
        if description is not None:
            strategy.description = description
        
        if code:
            if not self._validate_strategy_code(code):
                raise ValueError("策略代码格式不正确")
            strategy.code = code
        
        if config is not None:
            strategy.config = config
        
        if tags is not None:
            strategy.tags = tags
        
        strategy.updated_at = datetime.now()
        strategy.version = self._increment_version(strategy.version)
        
        # 保存
        self._save_data()
        
        logger.info(f"策略更新成功：{strategy.name}")
        
        return strategy
    
    def publish_strategy(self, strategy_id: str, author_id: str) -> Strategy:
        """
        发布策略
        
        Args:
            strategy_id: 策略 ID
            author_id: 作者 ID
        
        Returns:
            策略对象
        
        Raises:
            ValueError: 当策略不存在或无权限时
        """
        strategy = self.strategies.get(strategy_id)
        
        if not strategy:
            raise ValueError("策略不存在")
        
        if strategy.author_id != author_id:
            raise ValueError("无权限发布他人策略")
        
        strategy.status = StrategyStatus.PUBLISHED
        strategy.updated_at = datetime.now()
        
        self._save_data()
        
        logger.info(f"策略发布成功：{strategy.name}")
        
        return strategy
    
    def delete_strategy(self, strategy_id: str, author_id: str) -> bool:
        """
        删除策略
        
        Args:
            strategy_id: 策略 ID
            author_id: 作者 ID
        
        Returns:
            是否删除成功
        
        Raises:
            ValueError: 当策略不存在或无权限时
        """
        strategy = self.strategies.get(strategy_id)
        
        if not strategy:
            raise ValueError("策略不存在")
        
        if strategy.author_id != author_id:
            raise ValueError("无权限删除他人策略")
        
        # 删除策略
        del self.strategies[strategy_id]
        
        # 删除相关评论
        if strategy_id in self.comments:
            del self.comments[strategy_id]
        
        # 删除相关收藏
        self.stars = [s for s in self.stars if s.strategy_id != strategy_id]
        
        self._save_data()
        
        logger.info(f"策略删除成功：{strategy_id}")
        
        return True
    
    def get_strategy(self, strategy_id: str) -> Optional[Strategy]:
        """
        获取策略详情
        
        Args:
            strategy_id: 策略 ID
        
        Returns:
            策略对象或 None
        """
        strategy = self.strategies.get(strategy_id)
        
        if strategy:
            # 增加浏览量
            strategy.views += 1
            self._save_data()
        
        return strategy
    
    def list_strategies(
        self,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        author_id: Optional[str] = None,
        search: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Strategy], int]:
        """
        浏览策略列表
        
        Args:
            category: 分类筛选
            tag: 标签筛选
            author_id: 作者筛选
            search: 搜索关键词
            status: 状态筛选
            page: 页码
            page_size: 每页数量
        
        Returns:
            (策略列表，总数)
        """
        strategies = list(self.strategies.values())
        
        # 筛选
        if category:
            strategies = [s for s in strategies if s.category.value == category]
        
        if tag:
            strategies = [s for s in strategies if tag in s.tags]
        
        if author_id:
            strategies = [s for s in strategies if s.author_id == author_id]
        
        if status:
            strategies = [s for s in strategies if s.status.value == status]
        
        if search:
            search_lower = search.lower()
            strategies = [
                s for s in strategies
                if search_lower in s.name.lower() or
                   search_lower in s.description.lower() or
                   search_lower in ' '.join(s.tags).lower()
            ]
        
        # 排序 (按更新时间倒序)
        strategies.sort(key=lambda s: s.updated_at, reverse=True)
        
        # 分页
        total = len(strategies)
        start = (page - 1) * page_size
        end = start + page_size
        
        return strategies[start:end], total
    
    def download_strategy(self, strategy_id: str, user_id: str) -> StrategyPackage:
        """
        下载策略
        
        Args:
            strategy_id: 策略 ID
            user_id: 用户 ID
        
        Returns:
            策略包对象
        
        Raises:
            ValueError: 当策略不存在时
        """
        strategy = self.strategies.get(strategy_id)
        
        if not strategy:
            raise ValueError("策略不存在")
        
        # 增加下载量
        strategy.downloads += 1
        self._save_data()
        
        # 创建策略包
        package = StrategyPackage(
            strategy=strategy,
            code_files={
                'strategy.py': strategy.code
            },
            config=strategy.config,
            backtest_data=strategy.backtest_report,
            readme=f"# {strategy.name}\n\n{strategy.description}"
        )
        
        logger.info(f"策略下载：{strategy.name} by user {user_id}")
        
        return package
    
    def star_strategy(self, strategy_id: str, user_id: str) -> bool:
        """
        收藏策略
        
        Args:
            strategy_id: 策略 ID
            user_id: 用户 ID
        
        Returns:
            是否收藏成功
        
        Raises:
            ValueError: 当策略不存在或已收藏时
        """
        strategy = self.strategies.get(strategy_id)
        
        if not strategy:
            raise ValueError("策略不存在")
        
        # 检查是否已收藏
        for star in self.stars:
            if star.strategy_id == strategy_id and star.user_id == user_id:
                raise ValueError("已收藏该策略")
        
        # 添加收藏
        star = Star(strategy_id=strategy_id, user_id=user_id)
        self.stars.append(star)
        
        # 更新策略收藏数
        strategy.stars += 1
        self._save_data()
        
        logger.info(f"策略收藏：{strategy.name} by user {user_id}")
        
        return True
    
    def unstar_strategy(self, strategy_id: str, user_id: str) -> bool:
        """
        取消收藏策略
        
        Args:
            strategy_id: 策略 ID
            user_id: 用户 ID
        
        Returns:
            是否取消成功
        """
        # 查找收藏
        star_to_remove = None
        
        for star in self.stars:
            if star.strategy_id == strategy_id and star.user_id == user_id:
                star_to_remove = star
                break
        
        if not star_to_remove:
            logger.warning(f"未找到收藏：{strategy_id} by user {user_id}")
            return False
        
        # 移除收藏
        self.stars.remove(star_to_remove)
        
        # 更新策略收藏数
        strategy = self.strategies.get(strategy_id)
        if strategy and strategy.stars > 0:
            strategy.stars -= 1
        
        self._save_data()
        
        logger.info(f"取消收藏：{strategy_id} by user {user_id}")
        
        return True
    
    def add_comment(
        self,
        strategy_id: str,
        user_id: str,
        user_name: str,
        content: str,
        parent_id: Optional[str] = None
    ) -> Comment:
        """
        添加评论
        
        Args:
            strategy_id: 策略 ID
            user_id: 用户 ID
            user_name: 用户名称
            content: 评论内容
            parent_id: 父评论 ID (回复)
        
        Returns:
            评论对象
        
        Raises:
            ValueError: 当策略不存在或内容为空时
        """
        strategy = self.strategies.get(strategy_id)
        
        if not strategy:
            raise ValueError("策略不存在")
        
        if not content or not content.strip():
            raise ValueError("评论内容不能为空")
        
        # 如果是回复，检查父评论是否存在
        if parent_id:
            parent_comment = self._get_comment(strategy_id, parent_id)
            if not parent_comment:
                raise ValueError("父评论不存在")
        
        # 创建评论
        comment = Comment(
            strategy_id=strategy_id,
            user_id=user_id,
            user_name=user_name,
            content=content.strip(),
            parent_id=parent_id
        )
        
        # 添加到评论列表
        if strategy_id not in self.comments:
            self.comments[strategy_id] = []
        
        self.comments[strategy_id].append(comment)
        self._save_data()
        
        logger.info(f"评论添加：{strategy_id} by {user_name}")
        
        return comment
    
    def get_comments(self, strategy_id: str) -> List[Comment]:
        """
        获取策略评论
        
        Args:
            strategy_id: 策略 ID
        
        Returns:
            评论列表
        """
        return self.comments.get(strategy_id, [])
    
    def is_starred(self, strategy_id: str, user_id: str) -> bool:
        """
        检查用户是否已收藏策略
        
        Args:
            strategy_id: 策略 ID
            user_id: 用户 ID
        
        Returns:
            是否已收藏
        """
        for star in self.stars:
            if star.strategy_id == strategy_id and star.user_id == user_id:
                return True
        return False
    
    def get_user_stars(self, user_id: str) -> List[Strategy]:
        """
        获取用户收藏的策略列表
        
        Args:
            user_id: 用户 ID
        
        Returns:
            策略列表
        """
        starred_ids = [s.strategy_id for s in self.stars if s.user_id == user_id]
        return [
            self.strategies[sid] for sid in starred_ids
            if sid in self.strategies
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取市场统计信息
        
        Returns:
            统计信息字典
        """
        total_strategies = len(self.strategies)
        published_strategies = len([s for s in self.strategies.values() if s.status == StrategyStatus.PUBLISHED])
        total_downloads = sum(s.downloads for s in self.strategies.values())
        total_stars = sum(s.stars for s in self.strategies.values())
        total_views = sum(s.views for s in self.strategies.values())
        
        # 分类统计
        category_stats = {}
        for strategy in self.strategies.values():
            cat = strategy.category.value
            category_stats[cat] = category_stats.get(cat, 0) + 1
        
        return {
            'total_strategies': total_strategies,
            'published_strategies': published_strategies,
            'total_downloads': total_downloads,
            'total_stars': total_stars,
            'total_views': total_views,
            'category_stats': category_stats
        }
    
    def _validate_strategy_code(self, code: str) -> bool:
        """
        验证策略代码 (基本检查)
        
        Args:
            code: 策略代码
        
        Returns:
            是否有效
        """
        # 基本检查：非空、包含类定义或函数定义
        if not code or not code.strip():
            return False
        
        # 检查是否包含 Python 代码特征
        has_class = 'class ' in code
        has_def = 'def ' in code
        has_import = 'import ' in code or 'from ' in code
        
        return has_class or has_def or has_import
    
    def _increment_version(self, version: str) -> str:
        """
        递增版本号
        
        Args:
            version: 当前版本号
        
        Returns:
            新版本号
        """
        try:
            parts = version.split('.')
            if len(parts) >= 3:
                parts[2] = str(int(parts[2]) + 1)
                return '.'.join(parts)
        except Exception:
            pass
        
        # 默认递增
        return "1.0.1"
    
    def _get_comment(self, strategy_id: str, comment_id: str) -> Optional[Comment]:
        """根据 ID 获取评论"""
        comments = self.comments.get(strategy_id, [])
        
        for comment in comments:
            if comment.id == comment_id:
                return comment
        
        return None
