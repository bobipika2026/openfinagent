"""
策略市场测试

测试策略上传、浏览、搜索、下载、收藏、评论等功能

@module: tests.test_market
@author: OpenFinAgent Team
@version: 0.4.0
"""

import pytest
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from market.models import Strategy, StrategyCategory, StrategyStatus, Comment, Star
from market.service import MarketService


class TestStrategyModel:
    """测试策略模型"""
    
    def test_strategy_creation(self):
        """测试策略创建"""
        strategy = Strategy(
            name="双均线策略",
            description="简单的双均线交叉策略",
            author_id="user123",
            author_name="张三",
            code="class MyStrategy: ...",
            category=StrategyCategory.CTA,
            tags=["均线", "趋势跟踪"]
        )
        
        assert strategy.name == "双均线策略"
        assert strategy.author_id == "user123"
        assert strategy.category == StrategyCategory.CTA
        assert strategy.status == StrategyStatus.DRAFT
        assert "均线" in strategy.tags
    
    def test_strategy_to_dict(self):
        """测试策略转字典"""
        strategy = Strategy(name="Test Strategy", author_id="user1", author_name="User")
        
        strategy_dict = strategy.to_dict()
        
        assert strategy_dict['name'] == "Test Strategy"
        assert strategy_dict['author_id'] == "user1"
        assert strategy_dict['category'] == "other"
        assert 'id' in strategy_dict


class TestMarketService:
    """测试市场服务"""
    
    @pytest.fixture
    def market_service(self, tmp_path):
        """创建测试用的市场服务"""
        db_path = tmp_path / "test_market.json"
        return MarketService(db_path=str(db_path))
    
    def test_upload_strategy_success(self, market_service):
        """测试成功上传策略"""
        strategy = market_service.upload_strategy(
            name="测试策略",
            code="class TestStrategy:\n    pass",
            author_id="user123",
            author_name="张三",
            description="这是一个测试策略",
            category="cta",
            tags=["测试", "示例"]
        )
        
        assert strategy.name == "测试策略"
        assert strategy.author_id == "user123"
        assert strategy.status == StrategyStatus.DRAFT
        assert strategy.id is not None
    
    def test_upload_strategy_invalid_code(self, market_service):
        """测试上传无效代码"""
        with pytest.raises(ValueError, match="策略代码格式不正确"):
            market_service.upload_strategy(
                name="无效策略",
                code="这不是有效的 Python 代码",
                author_id="user123",
                author_name="张三"
            )
    
    def test_upload_strategy_empty_name(self, market_service):
        """测试上传空名称策略"""
        with pytest.raises(ValueError, match="策略名称不能为空"):
            market_service.upload_strategy(
                name="",
                code="class Test: pass",
                author_id="user123",
                author_name="张三"
            )
    
    def test_update_strategy(self, market_service):
        """测试更新策略"""
        # 先上传
        strategy = market_service.upload_strategy(
            name="原名称",
            code="class Test: pass",
            author_id="user123",
            author_name="张三"
        )
        
        # 更新
        updated = market_service.update_strategy(
            strategy_id=strategy.id,
            author_id="user123",
            name="新名称",
            description="新描述"
        )
        
        assert updated.name == "新名称"
        assert updated.description == "新描述"
    
    def test_update_strategy_no_permission(self, market_service):
        """测试无权限更新"""
        # 先上传
        strategy = market_service.upload_strategy(
            name="测试策略",
            code="class Test: pass",
            author_id="user123",
            author_name="张三"
        )
        
        # 其他人尝试更新
        with pytest.raises(ValueError, match="无权限修改他人策略"):
            market_service.update_strategy(
                strategy_id=strategy.id,
                author_id="user456",
                name="新名称"
            )
    
    def test_publish_strategy(self, market_service):
        """测试发布策略"""
        strategy = market_service.upload_strategy(
            name="测试策略",
            code="class Test: pass",
            author_id="user123",
            author_name="张三",
            status="draft"
        )
        
        # 发布
        published = market_service.publish_strategy(
            strategy_id=strategy.id,
            author_id="user123"
        )
        
        assert published.status == StrategyStatus.PUBLISHED
    
    def test_delete_strategy(self, market_service):
        """测试删除策略"""
        strategy = market_service.upload_strategy(
            name="测试策略",
            code="class Test: pass",
            author_id="user123",
            author_name="张三"
        )
        
        # 删除
        result = market_service.delete_strategy(
            strategy_id=strategy.id,
            author_id="user123"
        )
        
        assert result is True
        
        # 验证已删除
        deleted_strategy = market_service.get_strategy(strategy.id)
        assert deleted_strategy is None
    
    def test_get_strategy(self, market_service):
        """测试获取策略详情"""
        strategy = market_service.upload_strategy(
            name="测试策略",
            code="class Test: pass",
            author_id="user123",
            author_name="张三"
        )
        
        # 获取
        retrieved = market_service.get_strategy(strategy.id)
        
        assert retrieved is not None
        assert retrieved.id == strategy.id
        
        # 验证浏览量增加
        assert retrieved.views == 1
    
    def test_list_strategies(self, market_service):
        """测试浏览策略列表"""
        # 上传多个策略
        market_service.upload_strategy(name="策略 1", code="class Test1: pass", author_id="user1", author_name="User1")
        market_service.upload_strategy(name="策略 2", code="class Test2: pass", author_id="user1", author_name="User1")
        market_service.upload_strategy(name="策略 3", code="class Test3: pass", author_id="user2", author_name="User2")
        
        # 获取全部
        strategies, total = market_service.list_strategies()
        
        assert total == 3
        assert len(strategies) == 3
        
        # 分页
        strategies_page1, total = market_service.list_strategies(page=1, page_size=2)
        assert len(strategies_page1) == 2
    
    def test_search_strategies(self, market_service):
        """测试搜索策略"""
        market_service.upload_strategy(
            name="双均线策略",
            code="class DualMA: pass",
            author_id="user1",
            author_name="User1",
            tags=["均线", "趋势"]
        )
        
        market_service.upload_strategy(
            name="RSI 策略",
            code="class RSI: pass",
            author_id="user1",
            author_name="User1",
            tags=["震荡", "技术指标"]
        )
        
        # 按名称搜索
        strategies, total = market_service.list_strategies(search="均线")
        assert total == 1
        
        # 按标签搜索
        strategies, total = market_service.list_strategies(tag="趋势")
        assert total == 1
    
    def test_download_strategy(self, market_service):
        """测试下载策略"""
        strategy = market_service.upload_strategy(
            name="测试策略",
            code="class Test: pass",
            author_id="user123",
            author_name="张三"
        )
        
        # 下载
        package = market_service.download_strategy(
            strategy_id=strategy.id,
            user_id="user456"
        )
        
        assert package.strategy.id == strategy.id
        assert 'strategy.py' in package.code_files
        
        # 验证下载量增加
        updated = market_service.get_strategy(strategy.id)
        assert updated.downloads == 1
    
    def test_star_strategy(self, market_service):
        """测试收藏策略"""
        strategy = market_service.upload_strategy(
            name="测试策略",
            code="class Test: pass",
            author_id="user123",
            author_name="张三"
        )
        
        # 收藏
        result = market_service.star_strategy(
            strategy_id=strategy.id,
            user_id="user456"
        )
        
        assert result is True
        
        # 验证收藏数增加
        updated = market_service.get_strategy(strategy.id)
        assert updated.stars == 1
        
        # 验证已收藏
        assert market_service.is_starred(strategy.id, "user456") is True
    
    def test_unstar_strategy(self, market_service):
        """测试取消收藏"""
        strategy = market_service.upload_strategy(
            name="测试策略",
            code="class Test: pass",
            author_id="user123",
            author_name="张三"
        )
        
        # 先收藏
        market_service.star_strategy(strategy_id=strategy.id, user_id="user456")
        
        # 取消收藏
        result = market_service.unstar_strategy(
            strategy_id=strategy.id,
            user_id="user456"
        )
        
        assert result is True
        
        # 验证收藏数减少
        updated = market_service.get_strategy(strategy.id)
        assert updated.stars == 0
    
    def test_add_comment(self, market_service):
        """测试添加评论"""
        strategy = market_service.upload_strategy(
            name="测试策略",
            code="class Test: pass",
            author_id="user123",
            author_name="张三"
        )
        
        # 添加评论
        comment = market_service.add_comment(
            strategy_id=strategy.id,
            user_id="user456",
            user_name="李四",
            content="很好的策略！"
        )
        
        assert comment.content == "很好的策略！"
        assert comment.user_name == "李四"
        
        # 获取评论
        comments = market_service.get_comments(strategy.id)
        assert len(comments) == 1
    
    def test_reply_comment(self, market_service):
        """测试回复评论"""
        strategy = market_service.upload_strategy(
            name="测试策略",
            code="class Test: pass",
            author_id="user123",
            author_name="张三"
        )
        
        # 添加主评论
        parent_comment = market_service.add_comment(
            strategy_id=strategy.id,
            user_id="user456",
            user_name="李四",
            content="很好的策略！"
        )
        
        # 回复
        reply = market_service.add_comment(
            strategy_id=strategy.id,
            user_id="user123",
            user_name="张三",
            content="谢谢支持！",
            parent_id=parent_comment.id
        )
        
        assert reply.parent_id == parent_comment.id
        assert reply.content == "谢谢支持！"
    
    def test_get_user_stars(self, market_service):
        """测试获取用户收藏的策略"""
        strategy1 = market_service.upload_strategy(
            name="策略 1",
            code="class Test1: pass",
            author_id="user1",
            author_name="User1"
        )
        
        strategy2 = market_service.upload_strategy(
            name="策略 2",
            code="class Test2: pass",
            author_id="user1",
            author_name="User1"
        )
        
        # 收藏两个策略
        market_service.star_strategy(strategy1.id, "user_fan")
        market_service.star_strategy(strategy2.id, "user_fan")
        
        # 获取收藏列表
        starred = market_service.get_user_stars("user_fan")
        
        assert len(starred) == 2
    
    def test_get_statistics(self, market_service):
        """测试获取统计信息"""
        # 上传多个策略
        market_service.upload_strategy(name="策略 1", code="class Test1: pass", author_id="user1", author_name="User1", category="cta")
        market_service.upload_strategy(name="策略 2", code="class Test2: pass", author_id="user1", author_name="User1", category="ml")
        
        # 发布一个
        strategies, _ = market_service.list_strategies()
        market_service.publish_strategy(strategies[0].id, "user1")
        
        # 获取统计
        stats = market_service.get_statistics()
        
        assert stats['total_strategies'] == 2
        assert stats['published_strategies'] == 1
        assert 'category_stats' in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
