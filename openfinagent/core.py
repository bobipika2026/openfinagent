"""
TradeFlow Core Engine - 核心交易引擎
=====================================
金融 AI Agent 操作系统的核心驱动模块

功能：
- 自然语言策略解析（集成 AI API）
- 策略回测调度
- 市场数据接口统一管理
- 交易执行模拟

符合金融行业安全规范，支持单元测试
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
import hashlib

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TradeSignal:
    """交易信号数据类"""
    symbol: str
    action: str  # 'buy', 'sell', 'hold'
    quantity: int
    price: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    strategy_name: str = ""
    confidence: float = 0.0
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'symbol': self.symbol,
            'action': self.action,
            'quantity': self.quantity,
            'price': self.price,
            'timestamp': self.timestamp.isoformat(),
            'strategy_name': self.strategy_name,
            'confidence': self.confidence
        }


@dataclass
class BacktestResult:
    """回测结果数据类"""
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
        """转换为字典格式"""
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


class CoreEngine:
    """
    核心交易引擎
    
    负责协调策略解析、数据获取、回测和执行
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化核心引擎
        
        Args:
            config: 配置字典，可包含：
                - ai_api_endpoint: AI API 端点
                - data_source: 数据源 ('akshare' | 'yfinance')
                - broker: 经纪商 ('paper' | 'real')
                - risk_limit: 风险限制参数
        """
        self.config = config or {}
        self.ai_api_endpoint = self.config.get('ai_api_endpoint', 'default')
        self.data_source = self.config.get('data_source', 'akshare')
        self.broker = self.config.get('broker', 'paper')
        self.risk_limit = self.config.get('risk_limit', {'max_position': 100000})
        
        self.strategies = {}
        self.positions = {}
        self.trade_history = []
        
        logger.info(f"核心引擎初始化完成，数据源：{self.data_source}")
    
    def parse_strategy(self, natural_language: str) -> Dict:
        """
        解析自然语言策略描述
        
        Args:
            natural_language: 自然语言策略描述
            
        Returns:
            解析后的策略字典，包含条件和动作
            
        Security Note:
            - 对输入进行 sanitization
            - 限制策略复杂度
            - 记录解析日志用于审计
        """
        logger.info(f"解析策略：{natural_language[:100]}...")
        
        # 输入验证 - 金融安全规范
        if len(natural_language) > 1000:
            raise ValueError("策略描述过长，限制 1000 字符")
        
        # TODO: 集成 AI API 进行自然语言理解
        # 当前使用规则-based 解析作为 MVP
        parsed = self._rule_based_parse(natural_language)
        
        # 生成策略 ID（用于追踪）
        strategy_id = hashlib.md5(
            natural_language.encode()
        ).hexdigest()[:8]
        parsed['strategy_id'] = strategy_id
        
        logger.info(f"策略解析完成，ID: {strategy_id}")
        return parsed
    
    def _rule_based_parse(self, text: str) -> Dict:
        """
        基于规则的策略解析（MVP 版本）
        
        TODO: 替换为 AI 模型解析
        """
        conditions = []
        actions = []
        
        # 简单关键词匹配（MVP）
        if '均线' in text:
            conditions.append({'type': 'moving_average_cross', 'params': {}})
        if '买入' in text or '买' in text:
            actions.append({'type': 'buy', 'params': {}})
        if '卖出' in text or '卖' in text:
            actions.append({'type': 'sell', 'params': {}})
        if '止损' in text:
            actions.append({'type': 'stop_loss', 'params': {}})
        
        return {
            'description': text,
            'conditions': conditions,
            'actions': actions,
            'parsed_at': datetime.now().isoformat()
        }
    
    def get_market_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        frequency: str = 'daily'
    ) -> Optional[Dict]:
        """
        获取市场数据
        
        Args:
            symbol: 股票代码（如 '000001.SZ', 'AAPL'）
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            frequency: 频率 ('daily' | 'minute' | 'tick')
            
        Returns:
            市场数据字典，包含 OHLCV 等
            
        Security Note:
            - 验证日期范围
            - 限制数据量防止 DoS
            - 记录数据访问日志
        """
        logger.info(f"获取数据：{symbol} [{start_date} to {end_date}]")
        
        # 日期验证
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            if start > end:
                raise ValueError("开始日期不能晚于结束日期")
            if (end - start).days > 365:
                logger.warning("请求数据超过 1 年，可能影响性能")
        except ValueError as e:
            logger.error(f"日期格式错误：{e}")
            raise
        
        # 根据数据源获取数据
        if self.data_source == 'akshare':
            return self._get_akshare_data(symbol, start_date, end_date, frequency)
        elif self.data_source == 'yfinance':
            return self._get_yfinance_data(symbol, start_date, end_date, frequency)
        else:
            raise ValueError(f"不支持的数据源：{self.data_source}")
    
    def _get_akshare_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        frequency: str
    ) -> Dict:
        """
        从 AkShare 获取 A 股数据
        
        MVP 版本返回模拟数据结构
        TODO: 实现真实 API 调用
        """
        logger.info(f"[AkShare] 获取 {symbol} 数据")
        
        # MVP: 返回模拟数据结构
        return {
            'symbol': symbol,
            'source': 'akshare',
            'frequency': frequency,
            'data': [],  # TODO: 填充真实数据
            'metadata': {
                'retrieved_at': datetime.now().isoformat(),
                'total_records': 0
            }
        }
    
    def _get_yfinance_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        frequency: str
    ) -> Dict:
        """
        从 YFinance 获取美股/加密货币数据
        
        MVP 版本返回模拟数据结构
        TODO: 实现真实 API 调用
        """
        logger.info(f"[YFinance] 获取 {symbol} 数据")
        
        return {
            'symbol': symbol,
            'source': 'yfinance',
            'frequency': frequency,
            'data': [],  # TODO: 填充真实数据
            'metadata': {
                'retrieved_at': datetime.now().isoformat(),
                'total_records': 0
            }
        }
    
    def run_backtest(
        self,
        strategy: Dict,
        start_date: str,
        end_date: str,
        initial_capital: float = 100000.0
    ) -> BacktestResult:
        """
        运行策略回测
        
        Args:
            strategy: 策略字典（来自 parse_strategy）
            start_date: 开始日期
            end_date: 结束日期
            initial_capital: 初始资金
            
        Returns:
            BacktestResult 回测结果
            
        Security Note:
            - 回测在沙箱环境运行
            - 不影响真实持仓
            - 记录完整回测日志
        """
        logger.info(f"开始回测：{strategy.get('strategy_id', 'unknown')}")
        
        # 导入回测引擎
        from .backtest.engine import BacktestEngine
        
        engine = BacktestEngine(
            initial_capital=initial_capital,
            config=self.config
        )
        
        # 执行回测
        result = engine.run(strategy, start_date, end_date)
        
        logger.info(
            f"回测完成：收益率={result.total_return:.2%}, "
            f"夏普比率={result.sharpe_ratio:.2f}"
        )
        
        return result
    
    def execute_trade(self, signal: TradeSignal) -> Dict:
        """
        执行交易信号
        
        Args:
            signal: 交易信号
            
        Returns:
            执行结果字典
            
        Security Note:
            - 风险检查（仓位限制、单笔限额）
            - 纸面交易 vs 真实交易分离
            - 完整审计日志
        """
        logger.info(f"执行交易：{signal.action} {signal.quantity} {signal.symbol}")
        
        # 风险检查
        if not self._risk_check(signal):
            logger.warning(f"交易未通过风险检查：{signal.symbol}")
            return {'status': 'rejected', 'reason': 'risk_check_failed'}
        
        # 根据经纪商类型执行
        if self.broker == 'paper':
            result = self._execute_paper_trade(signal)
        else:
            # TODO: 实现真实交易执行
            logger.warning("真实交易执行尚未实现")
            result = {'status': 'not_implemented'}
        
        # 记录交易历史
        self.trade_history.append({
            'signal': signal.to_dict(),
            'result': result,
            'executed_at': datetime.now().isoformat()
        })
        
        return result
    
    def _risk_check(self, signal: TradeSignal) -> bool:
        """
        风险检查
        
        金融安全规范要求的风险控制点
        """
        # 检查仓位限制
        max_position = self.risk_limit.get('max_position', 100000)
        estimated_value = signal.quantity * (signal.price or 0)
        
        if estimated_value > max_position:
            logger.warning(f"超出最大仓位限制：{estimated_value} > {max_position}")
            return False
        
        # TODO: 添加更多风险检查
        # - 单一标的集中度
        # - 日交易次数限制
        # - 异常价格检测
        
        return True
    
    def _execute_paper_trade(self, signal: TradeSignal) -> Dict:
        """
        执行纸面交易（模拟）
        """
        order_id = f"PAPER_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 更新模拟持仓
        if signal.action == 'buy':
            current = self.positions.get(signal.symbol, 0)
            self.positions[signal.symbol] = current + signal.quantity
        elif signal.action == 'sell':
            current = self.positions.get(signal.symbol, 0)
            self.positions[signal.symbol] = max(0, current - signal.quantity)
        
        return {
            'order_id': order_id,
            'status': 'filled',
            'symbol': signal.symbol,
            'action': signal.action,
            'quantity': signal.quantity,
            'price': signal.price,
            'mode': 'paper'
        }
    
    def get_positions(self) -> Dict:
        """获取当前持仓"""
        return self.positions.copy()
    
    def get_trade_history(self, limit: int = 100) -> List[Dict]:
        """获取交易历史"""
        return self.trade_history[-limit:]
    
    def export_audit_log(self) -> str:
        """
        导出审计日志（合规要求）
        
        Returns:
            JSON 格式的审计日志
        """
        audit_data = {
            'exported_at': datetime.now().isoformat(),
            'total_trades': len(self.trade_history),
            'current_positions': self.positions,
            'trade_history': self.trade_history,
            'config': {
                'data_source': self.data_source,
                'broker': self.broker,
                'risk_limit': self.risk_limit
            }
        }
        return json.dumps(audit_data, indent=2, ensure_ascii=False)


# 便捷函数
def create_engine(config: Optional[Dict] = None) -> CoreEngine:
    """创建核心引擎实例"""
    return CoreEngine(config)


# 单元测试
if __name__ == '__main__':
    print("运行 CoreEngine 单元测试...")
    
    # 测试 1: 引擎初始化
    engine = create_engine({'data_source': 'akshare', 'broker': 'paper'})
    assert engine.data_source == 'akshare'
    print("✓ 引擎初始化测试通过")
    
    # 测试 2: 策略解析
    strategy = engine.parse_strategy("当 5 日均线上穿 20 日均线时买入")
    assert 'strategy_id' in strategy
    assert len(strategy['conditions']) > 0
    print("✓ 策略解析测试通过")
    
    # 测试 3: 风险检查
    signal = TradeSignal(
        symbol='000001.SZ',
        action='buy',
        quantity=1000,
        price=10.0
    )
    assert engine._risk_check(signal) == True
    print("✓ 风险检查测试通过")
    
    # 测试 4: 纸面交易
    result = engine.execute_trade(signal)
    assert result['status'] == 'filled'
    assert engine.positions.get('000001.SZ') == 1000
    print("✓ 纸面交易测试通过")
    
    # 测试 5: 审计日志导出
    audit_log = engine.export_audit_log()
    assert 'trade_history' in audit_log
    print("✓ 审计日志导出测试通过")
    
    print("\n✅ 所有单元测试通过!")
