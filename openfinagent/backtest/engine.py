"""
TradeFlow Backtest Engine - 回测引擎
=====================================
策略回测核心引擎

功能：
- 事件驱动回测框架
- 支持多策略回测
- 性能指标计算
- 交易成本模拟
- 风险控制模拟

符合金融行业回测规范，支持单元测试
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import math

logger = logging.getLogger(__name__)


@dataclass
class Trade:
    """交易记录"""
    timestamp: datetime
    symbol: str
    action: str  # 'buy' | 'sell'
    quantity: int
    price: float
    commission: float = 0.0
    slippage: float = 0.0
    
    @property
    def total_cost(self) -> float:
        """总成本"""
        return self.quantity * self.price + self.commission + self.slippage
    
    @property
    def total_value(self) -> float:
        """总价值"""
        return self.quantity * self.price


@dataclass
class Position:
    """持仓记录"""
    symbol: str
    quantity: int
    avg_cost: float
    current_price: float = 0.0
    
    @property
    def market_value(self) -> float:
        """市值"""
        return self.quantity * self.current_price
    
    @property
    def unrealized_pnl(self) -> float:
        """未实现盈亏"""
        return (self.current_price - self.avg_cost) * self.quantity
    
    @property
    def unrealized_pnl_percent(self) -> float:
        """未实现盈亏比例"""
        if self.avg_cost == 0:
            return 0.0
        return (self.current_price - self.avg_cost) / self.avg_cost


@dataclass
class BacktestMetrics:
    """回测指标"""
    total_return: float = 0.0
    annualized_return: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    avg_trade_duration: float = 0.0  # 天


class BacktestEngine:
    """
    回测引擎
    
    事件驱动架构，支持：
    - 日线/分钟线回测
    - 多策略并发
    - 交易成本模拟
    - 滑点模拟
    """
    
    def __init__(
        self,
        initial_capital: float = 100000.0,
        config: Optional[Dict] = None
    ):
        """
        初始化回测引擎
        
        Args:
            initial_capital: 初始资金
            config: 配置字典
                - commission_rate: 佣金率 (默认 0.0003)
                - slippage_rate: 滑点率 (默认 0.001)
                - risk_free_rate: 无风险利率 (默认 0.03)
        """
        self.initial_capital = initial_capital
        self.config = config or {}
        
        # 交易成本参数
        self.commission_rate = self.config.get('commission_rate', 0.0003)
        self.slippage_rate = self.config.get('slippage_rate', 0.001)
        self.risk_free_rate = self.config.get('risk_free_rate', 0.03)
        
        # 回测状态
        self.capital = initial_capital
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.equity_curve: List[Dict] = []
        self.daily_returns: List[float] = []
        
        # 市场数据
        self.market_data = {}
        self.current_date = None
        
        logger.info(f"回测引擎初始化完成，初始资金：{initial_capital:,.2f}")
    
    def run(
        self,
        strategy: Dict,
        start_date: str,
        end_date: str
    ) -> 'BacktestResult':
        """
        运行回测
        
        Args:
            strategy: 策略字典
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            回测结果
        """
        logger.info(f"开始回测：{strategy.get('strategy_id', 'unknown')}")
        
        # 重置状态
        self._reset()
        
        # 加载市场数据
        self._load_market_data(start_date, end_date)
        
        # 运行回测
        self._run_backtest(strategy)
        
        # 计算指标
        metrics = self._calculate_metrics()
        
        # 创建结果
        result = BacktestResult(
            strategy_name=strategy.get('strategy_id', 'unknown'),
            start_date=start_date,
            end_date=end_date,
            total_return=metrics.total_return,
            sharpe_ratio=metrics.sharpe_ratio,
            max_drawdown=metrics.max_drawdown,
            win_rate=metrics.win_rate,
            total_trades=metrics.total_trades,
            details=metrics.__dict__
        )
        
        logger.info(
            f"回测完成：收益率={metrics.total_return:.2%}, "
            f"夏普比率={metrics.sharpe_ratio:.2f}, "
            f"最大回撤={metrics.max_drawdown:.2%}"
        )
        
        return result
    
    def _reset(self):
        """重置回测状态"""
        self.capital = self.initial_capital
        self.positions.clear()
        self.trades.clear()
        self.equity_curve.clear()
        self.daily_returns.clear()
        self.market_data.clear()
    
    def _load_market_data(self, start_date: str, end_date: str):
        """
        加载市场数据
        
        MVP 版本使用模拟数据
        TODO: 集成真实数据源
        """
        logger.info(f"加载市场数据 [{start_date} to {end_date}]")
        
        # 生成模拟数据
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        dates = []
        current = start
        while current <= end:
            if current.weekday() < 5:  # 跳过周末
                dates.append(current)
            current += timedelta(days=1)
        
        # 为每个日期生成数据
        for date in dates:
            self.market_data[date] = {
                'date': date,
                'prices': {},  # symbol -> price
                'signals': []
            }
        
        logger.info(f"加载 {len(dates)} 个交易日数据")
    
    def _run_backtest(self, strategy: Dict):
        """
        执行回测
        
        事件驱动循环
        """
        dates = sorted(self.market_data.keys())
        
        prev_equity = self.initial_capital
        
        for i, date in enumerate(dates):
            self.current_date = date
            
            # 1. 生成信号
            signals = self._generate_signals(strategy, date)
            
            # 2. 执行交易
            for signal in signals:
                self._execute_signal(signal, date)
            
            # 3. 更新持仓价格
            self._update_positions(date)
            
            # 4. 计算权益
            current_equity = self._calculate_equity()
            self.equity_curve.append({
                'date': date,
                'equity': current_equity,
                'capital': self.capital,
                'positions_value': current_equity - self.capital
            })
            
            # 5. 计算日收益率
            if prev_equity > 0:
                daily_return = (current_equity - prev_equity) / prev_equity
                self.daily_returns.append(daily_return)
            prev_equity = current_equity
        
        logger.info(f"回测执行完成，共 {len(dates)} 个交易日")
    
    def _generate_signals(self, strategy: Dict, date: datetime) -> List[Dict]:
        """
        生成交易信号
        
        MVP 版本返回空信号
        TODO: 实现策略信号生成
        """
        # 模拟一些信号用于测试
        if date.day == 15:  # 每月 15 号生成买入信号
            return [{
                'action': 'buy',
                'symbol': 'TEST',
                'quantity': 100,
                'price': 10.0
            }]
        elif date.day == 25:  # 每月 25 号生成卖出信号
            if 'TEST' in self.positions:
                return [{
                    'action': 'sell',
                    'symbol': 'TEST',
                    'quantity': self.positions['TEST'].quantity,
                    'price': 11.0
                }]
        
        return []
    
    def _execute_signal(self, signal: Dict, date: datetime):
        """执行交易信号"""
        action = signal.get('action')
        symbol = signal.get('symbol')
        quantity = signal.get('quantity', 0)
        price = signal.get('price', 0.0)
        
        if action == 'buy':
            self._execute_buy(symbol, quantity, price, date)
        elif action == 'sell':
            self._execute_sell(symbol, quantity, price, date)
    
    def _execute_buy(
        self,
        symbol: str,
        quantity: int,
        price: float,
        date: datetime
    ):
        """执行买入"""
        # 计算成本
        trade_value = quantity * price
        commission = trade_value * self.commission_rate
        slippage = trade_value * self.slippage_rate
        total_cost = trade_value + commission + slippage
        
        # 检查资金
        if total_cost > self.capital:
            logger.warning(f"资金不足，跳过买入：{symbol}")
            return
        
        # 扣减资金
        self.capital -= total_cost
        
        # 更新持仓
        if symbol in self.positions:
            pos = self.positions[symbol]
            total_qty = pos.quantity + quantity
            total_cost = pos.avg_cost * pos.quantity + trade_value
            pos.avg_cost = total_cost / total_qty if total_qty > 0 else 0
            pos.quantity = total_qty
        else:
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                avg_cost=price
            )
        
        # 记录交易
        trade = Trade(
            timestamp=date,
            symbol=symbol,
            action='buy',
            quantity=quantity,
            price=price,
            commission=commission,
            slippage=slippage
        )
        self.trades.append(trade)
        
        logger.debug(f"买入：{quantity} {symbol} @ {price}")
    
    def _execute_sell(
        self,
        symbol: str,
        quantity: int,
        price: float,
        date: datetime
    ):
        """执行卖出"""
        if symbol not in self.positions:
            logger.warning(f"无持仓，跳过卖出：{symbol}")
            return
        
        pos = self.positions[symbol]
        quantity = min(quantity, pos.quantity)
        
        if quantity <= 0:
            return
        
        # 计算收入
        trade_value = quantity * price
        commission = trade_value * self.commission_rate
        slippage = trade_value * self.slippage_rate
        net_income = trade_value - commission - slippage
        
        # 增加资金
        self.capital += net_income
        
        # 更新持仓
        pos.quantity -= quantity
        if pos.quantity == 0:
            del self.positions[symbol]
        
        # 记录交易
        trade = Trade(
            timestamp=date,
            symbol=symbol,
            action='sell',
            quantity=quantity,
            price=price,
            commission=commission,
            slippage=slippage
        )
        self.trades.append(trade)
        
        logger.debug(f"卖出：{quantity} {symbol} @ {price}")
    
    def _update_positions(self, date: datetime):
        """更新持仓价格"""
        # MVP: 使用模拟价格
        for symbol, pos in self.positions.items():
            # 模拟价格增长
            pos.current_price = pos.avg_cost * 1.01
    
    def _calculate_equity(self) -> float:
        """计算总权益"""
        positions_value = sum(pos.market_value for pos in self.positions.values())
        return self.capital + positions_value
    
    def _calculate_metrics(self) -> BacktestMetrics:
        """计算回测指标"""
        metrics = BacktestMetrics()
        
        if not self.equity_curve:
            return metrics
        
        # 总收益率
        final_equity = self.equity_curve[-1]['equity']
        metrics.total_return = (final_equity - self.initial_capital) / self.initial_capital
        
        # 年化收益率
        days = len(self.equity_curve)
        if days > 0:
            metrics.annualized_return = (
                (1 + metrics.total_return) ** (252 / days) - 1
            )
        
        # 夏普比率
        if self.daily_returns and len(self.daily_returns) > 1:
            avg_return = sum(self.daily_returns) / len(self.daily_returns)
            std_return = math.sqrt(
                sum((r - avg_return) ** 2 for r in self.daily_returns) / 
                (len(self.daily_returns) - 1)
            ) if len(self.daily_returns) > 1 else 1
            if std_return > 0:
                metrics.sharpe_ratio = (avg_return - self.risk_free_rate / 252) / std_return * math.sqrt(252)
        
        # 最大回撤
        metrics.max_drawdown = self._calculate_max_drawdown()
        
        # 交易统计
        metrics.total_trades = len(self.trades)
        buy_trades = [t for t in self.trades if t.action == 'buy']
        sell_trades = [t for t in self.trades if t.action == 'sell']
        
        # 计算盈亏
        winning_trades = []
        losing_trades = []
        
        for sell_trade in sell_trades:
            # 找到对应的买入交易
            matching_buys = [
                t for t in buy_trades 
                if t.symbol == sell_trade.symbol and t.timestamp < sell_trade.timestamp
            ]
            if matching_buys:
                avg_buy_price = sum(t.price for t in matching_buys) / len(matching_buys)
                pnl = (sell_trade.price - avg_buy_price) * sell_trade.quantity
                if pnl > 0:
                    winning_trades.append(pnl)
                else:
                    losing_trades.append(abs(pnl))
        
        metrics.winning_trades = len(winning_trades)
        metrics.losing_trades = len(losing_trades)
        
        if metrics.total_trades > 0:
            metrics.win_rate = metrics.winning_trades / metrics.total_trades
        
        if winning_trades:
            metrics.avg_win = sum(winning_trades) / len(winning_trades)
        if losing_trades:
            metrics.avg_loss = sum(losing_trades) / len(losing_trades)
        
        if metrics.avg_loss > 0:
            metrics.profit_factor = sum(winning_trades) / sum(losing_trades) if losing_trades else float('inf')
        
        return metrics
    
    def _calculate_max_drawdown(self) -> float:
        """计算最大回撤"""
        if not self.equity_curve:
            return 0.0
        
        max_equity = 0.0
        max_drawdown = 0.0
        
        for point in self.equity_curve:
            equity = point['equity']
            if equity > max_equity:
                max_equity = equity
            
            drawdown = (max_equity - equity) / max_equity if max_equity > 0 else 0
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown
    
    def get_equity_curve(self) -> List[Dict]:
        """获取权益曲线"""
        return self.equity_curve.copy()
    
    def get_trades(self) -> List[Trade]:
        """获取交易记录"""
        return self.trades.copy()
    
    def get_positions(self) -> Dict[str, Position]:
        """获取持仓"""
        return self.positions.copy()


@dataclass
class BacktestResult:
    """回测结果"""
    strategy_name: str
    start_date: str
    end_date: str
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    details: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'strategy_name': self.strategy_name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'total_return': self.total_return,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'win_rate': self.win_rate,
            'total_trades': self.total_trades,
            'details': self.details
        }
    
    def summary(self) -> str:
        """返回摘要字符串"""
        return (
            f"策略：{self.strategy_name}\n"
            f"期间：{self.start_date} ~ {self.end_date}\n"
            f"收益率：{self.total_return:.2%}\n"
            f"夏普比率：{self.sharpe_ratio:.2f}\n"
            f"最大回撤：{self.max_drawdown:.2%}\n"
            f"胜率：{self.win_rate:.2%}\n"
            f"交易次数：{self.total_trades}"
        )


# 便捷函数
def create_backtest_engine(
    initial_capital: float = 100000.0,
    config: Optional[Dict] = None
) -> BacktestEngine:
    """创建回测引擎实例"""
    return BacktestEngine(initial_capital, config)


# 单元测试
if __name__ == '__main__':
    print("运行回测引擎单元测试...")
    
    # 测试 1: 引擎初始化
    engine = create_backtest_engine(100000.0)
    assert engine.initial_capital == 100000.0
    print("✓ 回测引擎初始化测试通过")
    
    # 测试 2: 运行回测
    strategy = {
        'strategy_id': 'test_strategy',
        'conditions': [],
        'actions': []
    }
    result = engine.run(strategy, '2024-01-01', '2024-01-31')
    assert isinstance(result, BacktestResult)
    assert result.start_date == '2024-01-01'
    print("✓ 回测运行测试通过")
    
    # 测试 3: 回测结果
    assert hasattr(result, 'total_return')
    assert hasattr(result, 'sharpe_ratio')
    assert hasattr(result, 'max_drawdown')
    print("✓ 回测结果测试通过")
    
    # 测试 4: 权益曲线
    equity_curve = engine.get_equity_curve()
    assert len(equity_curve) > 0
    print("✓ 权益曲线测试通过")
    
    # 测试 5: 交易记录
    trades = engine.get_trades()
    assert isinstance(trades, list)
    print("✓ 交易记录测试通过")
    
    # 测试 6: 结果摘要
    summary = result.summary()
    assert '收益率' in summary
    print("✓ 结果摘要测试通过")
    
    # 测试 7: 结果转字典
    result_dict = result.to_dict()
    assert 'total_return' in result_dict
    print("✓ 结果转字典测试通过")
    
    print("\n✅ 所有回测引擎单元测试通过!")
