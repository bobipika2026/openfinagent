"""
风险控制模块

提供交易风险管理功能，包括：
- 仓位控制
- 止损止盈
- 最大回撤控制
- 交易频率限制
- 风险预算管理

@module: risk.control
@author: TradeFlow AI Team
@version: 1.0.0
"""

from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


@dataclass
class RiskLimits:
    """风险限制配置"""
    # 仓位控制
    max_position_ratio: float = 0.3  # 单只股票最大仓位比例
    max_total_position_ratio: float = 0.95  # 总仓位上限

    # 止损止盈
    stop_loss_pct: float = 0.08  # 止损阈值 (8%)
    take_profit_pct: float = 0.20  # 止盈阈值 (20%)
    trailing_stop_pct: float = 0.05  # 移动止损阈值 (5%)

    # 回撤控制
    max_drawdown_pct: float = 0.15  # 最大回撤阈值 (15%)
    daily_loss_limit_pct: float = 0.05  # 单日亏损限制 (5%)

    # 交易频率
    max_trades_per_day: int = 10  # 单日最大交易次数
    min_hold_days: int = 1  # 最小持仓天数

    # 风险预算
    max_risk_per_trade_pct: float = 0.02  # 单笔交易最大风险 (2%)


class RiskController:
    """
    风险控制管理器

    在交易执行前进行风险检查，确保交易符合风险限制。
    """

    def __init__(self, limits: Optional[RiskLimits] = None):
        """
        初始化风险控制器

        Args:
            limits: 风险限制配置，使用默认值如果为 None
        """
        self.limits = limits or RiskLimits()

        # 状态跟踪
        self.peak_equity: float = 0.0  # 峰值权益
        self.daily_trades: int = 0  # 当日交易次数
        self.last_trade_date: Optional[datetime] = None
        self.entry_prices: Dict[str, float] = {}  # 入场价格
        self.entry_dates: Dict[str, datetime] = {}  # 入场日期
        self.trade_history: List[Dict[str, Any]] = []

        logger.info("风险控制器初始化完成")

    def reset(self, initial_equity: float = 0.0):
        """重置风险控制状态"""
        self.peak_equity = initial_equity
        self.daily_trades = 0
        self.last_trade_date = None
        self.entry_prices = {}
        self.entry_dates = {}
        self.trade_history = []
        logger.info("风险控制器状态已重置")

    def check_trade_permission(
        self,
        action: str,
        price: float,
        shares: int,
        current_cash: float,
        current_positions: Dict[str, int],
        current_equity: float
    ) -> Dict[str, Any]:
        """
        检查交易是否被允许

        Args:
            action: 交易动作 ('buy' 或 'sell')
            price: 交易价格
            shares: 交易数量
            current_cash: 当前现金
            current_positions: 当前持仓
            current_equity: 当前总权益

        Returns:
            检查结果字典 {allowed: bool, reason: str}
        """
        # 更新峰值权益
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity

        # 检查最大回撤
        if self.peak_equity > 0:
            current_drawdown = (self.peak_equity - current_equity) / self.peak_equity
            if current_drawdown > self.limits.max_drawdown_pct:
                return {
                    'allowed': False,
                    'reason': f'触发最大回撤限制：{current_drawdown:.2%} > {self.limits.max_drawdown_pct:.2%}'
                }

        # 重置每日交易计数
        today = datetime.now().date()
        if self.last_trade_date is None or self.last_trade_date.date() != today:
            self.daily_trades = 0
            self.last_trade_date = datetime.now()

        # 检查交易频率
        if action == 'buy' and self.daily_trades >= self.limits.max_trades_per_day:
            return {
                'allowed': False,
                'reason': f'达到单日最大交易次数：{self.daily_trades}'
            }

        # 买入特定检查
        if action == 'buy':
            # 检查仓位限制
            trade_value = price * shares
            position_ratio = trade_value / current_equity if current_equity > 0 else 0

            if position_ratio > self.limits.max_position_ratio:
                return {
                    'allowed': False,
                    'reason': f'单笔仓位超限：{position_ratio:.2%} > {self.limits.max_position_ratio:.2%}'
                }

            # 检查总仓位
            total_position_value = sum(
                current_positions.get('shares', 0) * price
                for _ in range(1)
            )
            total_position_ratio = total_position_value / current_equity if current_equity > 0 else 0

            if total_position_ratio + position_ratio > self.limits.max_total_position_ratio:
                return {
                    'allowed': False,
                    'reason': f'总仓位超限：{(total_position_ratio + position_ratio):.2%}'
                }

            # 检查现金是否足够
            if trade_value > current_cash:
                return {
                    'allowed': False,
                    'reason': f'现金不足：需要{trade_value:.2f}, 可用{current_cash:.2f}'
                }

        # 卖出特定检查
        elif action == 'sell':
            current_shares = current_positions.get('shares', 0)
            if shares > current_shares:
                return {
                    'allowed': False,
                    'reason': f'持仓不足：需要{shares}股，可用{current_shares}股'
                }

            # 检查最小持仓天数
            symbol = 'default'  # 单股票策略使用默认符号
            if symbol in self.entry_dates:
                hold_days = (datetime.now() - self.entry_dates[symbol]).days
                if hold_days < self.limits.min_hold_days:
                    return {
                        'allowed': False,
                        'reason': f'未达最小持仓天数：{hold_days} < {self.limits.min_hold_days}'
                    }

        return {'allowed': True, 'reason': '通过风险检查'}

    def check_stop_loss_take_profit(
        self,
        current_price: float,
        symbol: str = 'default'
    ) -> Optional[str]:
        """
        检查是否触发止损止盈

        Args:
            current_price: 当前价格
            symbol: 股票符号

        Returns:
            触发类型 ('stop_loss', 'take_profit', 'trailing_stop') 或 None
        """
        if symbol not in self.entry_prices:
            return None

        entry_price = self.entry_prices[symbol]

        # 计算收益率
        if entry_price > 0:
            return_pct = (current_price - entry_price) / entry_price
        else:
            return None

        # 检查止损
        if return_pct <= -self.limits.stop_loss_pct:
            logger.warning(f"触发止损：{symbol}, 收益率={return_pct:.2%}")
            return 'stop_loss'

        # 检查止盈
        if return_pct >= self.limits.take_profit_pct:
            logger.info(f"触发止盈：{symbol}, 收益率={return_pct:.2%}")
            return 'take_profit'

        # 检查移动止损 (仅在有浮盈时)
        if return_pct > 0:
            peak_price = max(
                self.entry_prices.get(f'{symbol}_peak', entry_price),
                current_price
            )
            self.entry_prices[f'{symbol}_peak'] = peak_price

            drawdown_from_peak = (peak_price - current_price) / peak_price
            if drawdown_from_peak >= self.limits.trailing_stop_pct:
                logger.info(f"触发移动止损：{symbol}, 回撤={drawdown_from_peak:.2%}")
                return 'trailing_stop'

        return None

    def record_trade(
        self,
        action: str,
        price: float,
        shares: int,
        symbol: str = 'default'
    ):
        """
        记录交易

        Args:
            action: 交易动作
            price: 成交价格
            shares: 成交数量
            symbol: 股票符号
        """
        # 更新交易计数
        self.daily_trades += 1

        # 记录入场信息
        if action == 'buy':
            self.entry_prices[symbol] = price
            self.entry_dates[symbol] = datetime.now()
            self.entry_prices[f'{symbol}_peak'] = price

        # 记录交易历史
        self.trade_history.append({
            'timestamp': datetime.now(),
            'action': action,
            'price': price,
            'shares': shares,
            'symbol': symbol
        })

        logger.debug(f"交易记录：{action} {shares}股 @ {price:.2f}")

    def get_risk_metrics(self, current_equity: float) -> Dict[str, Any]:
        """
        获取风险指标

        Args:
            current_equity: 当前权益

        Returns:
            风险指标字典
        """
        # 计算回撤
        if self.peak_equity > 0:
            current_drawdown = (self.peak_equity - current_equity) / self.peak_equity
        else:
            current_drawdown = 0.0

        return {
            'peak_equity': self.peak_equity,
            'current_equity': current_equity,
            'current_drawdown': current_drawdown,
            'max_drawdown_limit': self.limits.max_drawdown_pct,
            'daily_trades': self.daily_trades,
            'daily_trades_limit': self.limits.max_trades_per_day,
            'total_trades': len(self.trade_history)
        }

    def adjust_position_size(
        self,
        proposed_shares: int,
        price: float,
        current_equity: float,
        current_positions: Dict[str, int]
    ) -> int:
        """
        根据风险限制调整仓位大小

        Args:
            proposed_shares: 提议的交易数量
            price: 交易价格
            current_equity: 当前权益
            current_positions: 当前持仓

        Returns:
            调整后的交易数量
        """
        if proposed_shares <= 0 or price <= 0:
            return 0

        trade_value = price * proposed_shares

        # 限制单笔仓位
        max_position_value = current_equity * self.limits.max_position_ratio
        if trade_value > max_position_value:
            adjusted_shares = int(max_position_value / price / 100) * 100
            logger.debug(
                f"仓位调整：{proposed_shares} → {adjusted_shares} (单笔限制)"
            )
            return adjusted_shares

        # 限制总仓位
        current_position_value = current_positions.get('shares', 0) * price
        total_after_trade = current_position_value + trade_value
        max_total_value = current_equity * self.limits.max_total_position_ratio

        if total_after_trade > max_total_value:
            adjusted_value = max_total_value - current_position_value
            adjusted_shares = int(adjusted_value / price / 100) * 100
            logger.debug(
                f"仓位调整：{proposed_shares} → {adjusted_shares} (总仓位限制)"
            )
            return max(0, adjusted_shares)

        return proposed_shares
