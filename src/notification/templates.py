"""
通知模板 - 预定义通知模板

提供买入、卖出、止盈止损、日报周报等通知模板。

@module: notification.templates
@author: OpenFinAgent Team
@version: 1.0.0
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """通知类型（本地定义避免循环导入）"""
    SIGNAL = "signal"
    TRADE = "trade"
    RISK = "risk"
    REPORT = "report"
    SYSTEM = "system"
    CUSTOM = "custom"


class TemplateType(Enum):
    """模板类型"""
    BUY_SIGNAL = "buy_signal"
    SELL_SIGNAL = "sell_signal"
    TAKE_PROFIT = "take_profit"
    STOP_LOSS = "stop_loss"
    DAILY_REPORT = "daily_report"
    WEEKLY_REPORT = "weekly_report"
    CUSTOM = "custom"


@dataclass
class NotificationTemplate:
    """
    通知模板
    
    Attributes:
        id: 模板 ID
        name: 模板名称
        template_type: 模板类型
        subject_template: 标题模板
        content_template: 内容模板
        variables: 可用变量列表
        created_at: 创建时间
    """
    id: str = ""
    name: str = ""
    template_type: TemplateType = TemplateType.CUSTOM
    subject_template: str = ""
    content_template: str = ""
    variables: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def render(self, **kwargs) -> Dict[str, str]:
        """
        渲染模板
        
        Args:
            **kwargs: 模板变量
            
        Returns:
            渲染后的标题和内容
        """
        try:
            # 使用 Python 字符串格式化
            subject = self.subject_template.format(**kwargs)
            content = self.content_template.format(**kwargs)
            
            return {
                'subject': subject,
                'content': content
            }
            
        except KeyError as e:
            logger.warning(f"模板变量缺失：{e}")
            # 部分渲染失败时返回原始模板
            return {
                'subject': self.subject_template,
                'content': self.content_template
            }
        except Exception as e:
            logger.error(f"模板渲染失败：{self.name}, {e}")
            return {
                'subject': self.subject_template,
                'content': self.content_template
            }


class TemplateManager:
    """
    模板管理器
    
    管理通知模板的注册、渲染和使用。
    
    Attributes:
        templates: 模板字典
    """
    
    def __init__(self):
        """初始化模板管理器"""
        self.templates: Dict[str, NotificationTemplate] = {}
        self._init_builtin_templates()
        logger.info("模板管理器初始化完成")
    
    def _init_builtin_templates(self) -> None:
        """初始化内置模板"""
        
        # 买入信号模板
        buy_template = NotificationTemplate(
            id="buy_signal_001",
            name="买入信号通知",
            template_type=TemplateType.BUY_SIGNAL,
            subject_template="📈 买入信号：{symbol}",
            content_template="""
🔔 **买入信号提醒**

📊 股票：{symbol}
💰 价格：{price:.2f}
📈 信号类型：买入
🎯 策略：{strategy}
📊 置信度：{confidence:.2%}
⏰ 时间：{timestamp}

💡 建议操作：
- 关注成交量变化
- 设置止损位：{stop_loss:.2f}
- 目标价位：{target_price:.2f}

---
OpenFinAgent 监控系统
            """.strip(),
            variables=['symbol', 'price', 'strategy', 'confidence', 'timestamp', 'stop_loss', 'target_price'],
            created_at=datetime.now()
        )
        
        # 卖出信号模板
        sell_template = NotificationTemplate(
            id="sell_signal_001",
            name="卖出信号通知",
            template_type=TemplateType.SELL_SIGNAL,
            subject_template="📉 卖出信号：{symbol}",
            content_template="""
🔔 **卖出信号提醒**

📊 股票：{symbol}
💰 价格：{price:.2f}
📉 信号类型：卖出
🎯 策略：{strategy}
📊 置信度：{confidence:.2%}
⏰ 时间：{timestamp}

💡 建议操作：
- 及时止盈/止损
- 关注后续走势
- 调整仓位配置

---
OpenFinAgent 监控系统
            """.strip(),
            variables=['symbol', 'price', 'strategy', 'confidence', 'timestamp'],
            created_at=datetime.now()
        )
        
        # 止盈通知模板
        take_profit_template = NotificationTemplate(
            id="take_profit_001",
            name="止盈通知",
            template_type=TemplateType.TAKE_PROFIT,
            subject_template="✅ 止盈提醒：{symbol}",
            content_template="""
✅ **止盈提醒**

📊 股票：{symbol}
💰 当前价格：{price:.2f}
🎯 目标价格：{target_price:.2f}
💵 收益率：{profit_rate:.2%}
💵 盈利金额：{profit_amount:.2f}
⏰ 时间：{timestamp}

🎉 恭喜达到止盈目标！

---
OpenFinAgent 监控系统
            """.strip(),
            variables=['symbol', 'price', 'target_price', 'profit_rate', 'profit_amount', 'timestamp'],
            created_at=datetime.now()
        )
        
        # 止损通知模板
        stop_loss_template = NotificationTemplate(
            id="stop_loss_001",
            name="止损通知",
            template_type=TemplateType.STOP_LOSS,
            subject_template="⚠️ 止损提醒：{symbol}",
            content_template="""
⚠️ **止损提醒**

📊 股票：{symbol}
💰 当前价格：{price:.2f}
🛑 止损价格：{stop_loss:.2f}
📉 亏损率：{loss_rate:.2%}
💸 亏损金额：{loss_amount:.2f}
⏰ 时间：{timestamp}

⚠️ 已达到止损线，请注意风险！

---
OpenFinAgent 监控系统
            """.strip(),
            variables=['symbol', 'price', 'stop_loss', 'loss_rate', 'loss_amount', 'timestamp'],
            created_at=datetime.now()
        )
        
        # 日报模板
        daily_report_template = NotificationTemplate(
            id="daily_report_001",
            name="投资日报",
            template_type=TemplateType.DAILY_REPORT,
            subject_template="📊 投资日报 - {date}",
            content_template="""
📊 **投资日报**

📅 日期：{date}

💼 账户概览：
- 总资产：{total_assets:.2f}
- 现金：{cash:.2f}
- 持仓市值：{position_value:.2f}
- 当日盈亏：{daily_pnl:.2f} ({daily_pnl_rate:.2%})

📈 持仓明细：
{positions}

🔔 今日信号：
- 买入信号：{buy_signals} 次
- 卖出信号：{sell_signals} 次

📊 市场概况：
{market_summary}

---
OpenFinAgent 监控系统
            """.strip(),
            variables=['date', 'total_assets', 'cash', 'position_value', 'daily_pnl', 'daily_pnl_rate', 'positions', 'buy_signals', 'sell_signals', 'market_summary'],
            created_at=datetime.now()
        )
        
        # 周报模板
        weekly_report_template = NotificationTemplate(
            id="weekly_report_001",
            name="投资周报",
            template_type=TemplateType.WEEKLY_REPORT,
            subject_template="📈 投资周报 - {week_start} 至 {week_end}",
            content_template="""
📈 **投资周报**

📅 周期：{week_start} 至 {week_end}

💼 账户表现：
- 期初资产：{start_assets:.2f}
- 期末资产：{end_assets:.2f}
- 周盈亏：{weekly_pnl:.2f} ({weekly_pnl_rate:.2%})
- 周收益率：{weekly_return:.2%}

📊 交易统计：
- 交易次数：{trade_count} 次
- 买入次数：{buy_count} 次
- 卖出次数：{sell_count} 次
- 胜率：{win_rate:.2%}

🏆 最佳表现：
- 最佳股票：{best_stock} ({best_return:.2%})
- 最差股票：{worst_stock} ({worst_return:.2%})

📈 市场概况：
{market_summary}

💡 下周策略：
{next_week_strategy}

---
OpenFinAgent 监控系统
            """.strip(),
            variables=['week_start', 'week_end', 'start_assets', 'end_assets', 'weekly_pnl', 'weekly_pnl_rate', 'weekly_return', 'trade_count', 'buy_count', 'sell_count', 'win_rate', 'best_stock', 'best_return', 'worst_stock', 'worst_return', 'market_summary', 'next_week_strategy'],
            created_at=datetime.now()
        )
        
        # 注册内置模板
        self.register(buy_template)
        self.register(sell_template)
        self.register(take_profit_template)
        self.register(stop_loss_template)
        self.register(daily_report_template)
        self.register(weekly_report_template)
        
        logger.info(f"内置模板初始化完成，共{len(self.templates)}个")
    
    def register(self, template: NotificationTemplate) -> bool:
        """
        注册模板
        
        Args:
            template: 模板对象
            
        Returns:
            是否成功
        """
        if not template.id:
            template.id = f"template_{len(self.templates) + 1}"
        
        self.templates[template.id] = template
        logger.info(f"模板注册：{template.name} ({template.id})")
        return True
    
    def get_template(self, template_id: str) -> Optional[NotificationTemplate]:
        """
        获取模板
        
        Args:
            template_id: 模板 ID
            
        Returns:
            模板对象，不存在则返回 None
        """
        return self.templates.get(template_id)
    
    def get_template_by_type(self, template_type: TemplateType) -> Optional[NotificationTemplate]:
        """
        根据类型获取模板
        
        Args:
            template_type: 模板类型
            
        Returns:
            模板对象，不存在则返回 None
        """
        for template in self.templates.values():
            if template.template_type == template_type:
                return template
        return None
    
    def list_templates(self) -> List[NotificationTemplate]:
        """
        列出所有模板
        
        Returns:
            模板列表
        """
        return list(self.templates.values())
    
    def render(
        self,
        template_id: str,
        **kwargs
    ) -> Optional[Dict[str, str]]:
        """
        渲染模板
        
        Args:
            template_id: 模板 ID
            **kwargs: 模板变量
            
        Returns:
            渲染结果，失败则返回 None
        """
        template = self.get_template(template_id)
        
        if not template:
            logger.error(f"模板不存在：{template_id}")
            return None
        
        return template.render(**kwargs)
    
    def delete_template(self, template_id: str) -> bool:
        """
        删除模板
        
        Args:
            template_id: 模板 ID
            
        Returns:
            是否成功
        """
        if template_id in self.templates:
            del self.templates[template_id]
            logger.info(f"模板删除：{template_id}")
            return True
        
        logger.warning(f"模板不存在：{template_id}")
        return False
