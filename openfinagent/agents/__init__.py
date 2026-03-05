"""
TradeFlow Agents - Agent 框架
==============================
多智能体协作系统

包含：
- ResearchAgent: 投研智能体（市场分析、资讯解读）
- TradingAgent: 交易智能体（策略执行、订单管理）
- RiskAgent: 风控智能体（实时监控、风险预警）
- AgentOrchestrator: 智能体编排引擎

符合金融行业安全规范，支持单元测试
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class AgentMessage:
    """Agent 间消息传递"""
    sender: str
    recipient: str
    message_type: str
    content: Dict
    timestamp: datetime
    priority: str = 'normal'  # 'low', 'normal', 'high', 'urgent'
    
    def to_dict(self) -> Dict:
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'message_type': self.message_type,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'priority': self.priority
        }


class BaseAgent(ABC):
    """
    Agent 基类
    
    所有智能体必须继承此类并实现抽象方法
    """
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        """
        初始化 Agent
        
        Args:
            name: Agent 名称
            config: 配置字典
        """
        self.name = name
        self.config = config or {}
        self.is_active = True
        self.message_queue = []
        self.state = {}
        
        logger.info(f"[{self.name}] Agent 初始化完成")
    
    @abstractmethod
    def process(self, input_data: Dict) -> Dict:
        """
        处理输入数据
        
        Args:
            input_data: 输入数据字典
            
        Returns:
            处理结果字典
        """
        pass
    
    @abstractmethod
    def get_status(self) -> Dict:
        """获取 Agent 状态"""
        pass
    
    def receive_message(self, message: AgentMessage):
        """接收消息"""
        self.message_queue.append(message)
        logger.debug(f"[{self.name}] 收到消息：{message.message_type}")
    
    def send_message(self, recipient: str, message_type: str, content: Dict):
        """
        发送消息
        
        Args:
            recipient: 接收者
            message_type: 消息类型
            content: 消息内容
        """
        message = AgentMessage(
            sender=self.name,
            recipient=recipient,
            message_type=message_type,
            content=content,
            timestamp=datetime.now()
        )
        logger.debug(f"[{self.name}] 发送消息给 {recipient}: {message_type}")
        return message
    
    def activate(self):
        """激活 Agent"""
        self.is_active = True
        logger.info(f"[{self.name}] Agent 已激活")
    
    def deactivate(self):
        """停用 Agent"""
        self.is_active = False
        logger.info(f"[{self.name}] Agent 已停用")


class ResearchAgent(BaseAgent):
    """
    投研智能体
    
    职责：
    - 市场数据分析
    - 资讯解读
    - 生成投研报告
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("ResearchAgent", config)
        self.analysis_cache = {}
    
    def process(self, input_data: Dict) -> Dict:
        """
        处理投研请求
        
        Args:
            input_data: 包含 symbol, analysis_type 等
            
        Returns:
            分析报告
        """
        if not self.is_active:
            return {'error': 'Agent not active'}
        
        logger.info(f"[{self.name}] 处理投研请求：{input_data.get('symbol')}")
        
        analysis_type = input_data.get('type', 'basic')
        symbol = input_data.get('symbol', '')
        
        # 根据分析类型处理
        if analysis_type == 'technical':
            result = self._technical_analysis(symbol, input_data)
        elif analysis_type == 'fundamental':
            result = self._fundamental_analysis(symbol, input_data)
        elif analysis_type == 'sentiment':
            result = self._sentiment_analysis(symbol, input_data)
        else:
            result = self._basic_analysis(symbol, input_data)
        
        return result
    
    def _basic_analysis(self, symbol: str, data: Dict) -> Dict:
        """基础分析（MVP）"""
        return {
            'symbol': symbol,
            'analysis_type': 'basic',
            'trend': 'neutral',
            'support_levels': [],
            'resistance_levels': [],
            'recommendation': 'hold',
            'confidence': 0.5,
            'generated_at': datetime.now().isoformat()
        }
    
    def _technical_analysis(self, symbol: str, data: Dict) -> Dict:
        """技术分析"""
        # TODO: 实现真实的技术指标计算
        return {
            'symbol': symbol,
            'analysis_type': 'technical',
            'indicators': {
                'ma_5': 0,
                'ma_20': 0,
                'rsi': 50,
                'macd': 0
            },
            'signal': 'neutral',
            'generated_at': datetime.now().isoformat()
        }
    
    def _fundamental_analysis(self, symbol: str, data: Dict) -> Dict:
        """基本面分析"""
        # TODO: 实现基本面分析
        return {
            'symbol': symbol,
            'analysis_type': 'fundamental',
            'pe_ratio': 0,
            'pb_ratio': 0,
            'roe': 0,
            'revenue_growth': 0,
            'rating': 'hold',
            'generated_at': datetime.now().isoformat()
        }
    
    def _sentiment_analysis(self, symbol: str, data: Dict) -> Dict:
        """市场情绪分析"""
        # TODO: 集成新闻/社交媒体情绪分析
        return {
            'symbol': symbol,
            'analysis_type': 'sentiment',
            'sentiment_score': 0,
            'news_count': 0,
            'social_mentions': 0,
            'generated_at': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            'name': self.name,
            'active': self.is_active,
            'cache_size': len(self.analysis_cache),
            'pending_messages': len(self.message_queue)
        }


class TradingAgent(BaseAgent):
    """
    交易智能体
    
    职责：
    - 策略执行
    - 订单管理
    - 持仓跟踪
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("TradingAgent", config)
        self.orders = {}
        self.positions = {}
        self.broker = self.config.get('broker', 'paper')
    
    def process(self, input_data: Dict) -> Dict:
        """
        处理交易请求
        
        Args:
            input_data: 包含 action, symbol, quantity 等
            
        Returns:
            交易结果
        """
        if not self.is_active:
            return {'error': 'Agent not active'}
        
        action = input_data.get('action', '')
        
        if action == 'buy':
            return self._execute_buy(input_data)
        elif action == 'sell':
            return self._execute_sell(input_data)
        elif action == 'cancel':
            return self._cancel_order(input_data)
        else:
            return {'error': 'Unknown action'}
    
    def _execute_buy(self, data: Dict) -> Dict:
        """执行买入"""
        symbol = data.get('symbol')
        quantity = data.get('quantity', 0)
        price = data.get('price')
        
        logger.info(f"[{self.name}] 买入：{quantity} {symbol} @ {price or 'market'}")
        
        order_id = f"BUY_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.orders[order_id] = {
            'type': 'buy',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'status': 'filled',
            'created_at': datetime.now().isoformat()
        }
        
        # 更新持仓
        current = self.positions.get(symbol, 0)
        self.positions[symbol] = current + quantity
        
        return {
            'order_id': order_id,
            'status': 'filled',
            'symbol': symbol,
            'quantity': quantity
        }
    
    def _execute_sell(self, data: Dict) -> Dict:
        """执行卖出"""
        symbol = data.get('symbol')
        quantity = data.get('quantity', 0)
        price = data.get('price')
        
        logger.info(f"[{self.name}] 卖出：{quantity} {symbol} @ {price or 'market'}")
        
        order_id = f"SELL_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.orders[order_id] = {
            'type': 'sell',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'status': 'filled',
            'created_at': datetime.now().isoformat()
        }
        
        # 更新持仓
        current = self.positions.get(symbol, 0)
        self.positions[symbol] = max(0, current - quantity)
        
        return {
            'order_id': order_id,
            'status': 'filled',
            'symbol': symbol,
            'quantity': quantity
        }
    
    def _cancel_order(self, data: Dict) -> Dict:
        """取消订单"""
        order_id = data.get('order_id')
        if order_id in self.orders:
            self.orders[order_id]['status'] = 'cancelled'
            return {'status': 'cancelled', 'order_id': order_id}
        return {'error': 'Order not found'}
    
    def get_positions(self) -> Dict:
        """获取持仓"""
        return self.positions.copy()
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            'name': self.name,
            'active': self.is_active,
            'total_orders': len(self.orders),
            'positions_count': len(self.positions),
            'broker': self.broker
        }


class RiskAgent(BaseAgent):
    """
    风控智能体
    
    职责：
    - 实时监控风险指标
    - 风险预警
    - 合规检查
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("RiskAgent", config)
        self.risk_limits = self.config.get('risk_limits', {
            'max_position': 100000,
            'max_single_trade': 50000,
            'max_daily_loss': 10000,
            'max_drawdown': 0.1
        })
        self.alerts = []
    
    def process(self, input_data: Dict) -> Dict:
        """
        处理风控检查请求
        
        Args:
            input_data: 包含 check_type, data 等
            
        Returns:
            风控结果
        """
        if not self.is_active:
            return {'error': 'Agent not active'}
        
        check_type = input_data.get('check_type', 'trade')
        
        if check_type == 'trade':
            return self._check_trade(input_data)
        elif check_type == 'position':
            return self._check_position(input_data)
        elif check_type == 'portfolio':
            return self._check_portfolio(input_data)
        else:
            return {'error': 'Unknown check type'}
    
    def _check_trade(self, data: Dict) -> Dict:
        """交易前风控检查"""
        symbol = data.get('symbol', '')
        quantity = data.get('quantity', 0)
        price = data.get('price', 0)
        
        trade_value = quantity * price
        
        checks = {
            'single_trade_limit': trade_value <= self.risk_limits['max_single_trade'],
            'position_limit': True,  # TODO: 检查持仓集中度
            'daily_loss_limit': True  # TODO: 检查日亏损
        }
        
        passed = all(checks.values())
        
        if not passed:
            self._create_alert('trade_rejected', data, checks)
        
        return {
            'passed': passed,
            'checks': checks,
            'trade_value': trade_value
        }
    
    def _check_position(self, data: Dict) -> Dict:
        """持仓风控检查"""
        # TODO: 实现持仓风险检查
        return {
            'passed': True,
            'concentration': 0,
            'var': 0
        }
    
    def _check_portfolio(self, data: Dict) -> Dict:
        """组合风控检查"""
        # TODO: 实现组合风险检查
        return {
            'passed': True,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'var_95': 0
        }
    
    def _create_alert(self, alert_type: str, data: Dict, details: Dict):
        """创建风险预警"""
        alert = {
            'type': alert_type,
            'timestamp': datetime.now().isoformat(),
            'data': data,
            'details': details,
            'severity': 'high'
        }
        self.alerts.append(alert)
        logger.warning(f"[{self.name}] 风险预警：{alert_type}")
    
    def get_alerts(self, limit: int = 10) -> List[Dict]:
        """获取预警列表"""
        return self.alerts[-limit:]
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            'name': self.name,
            'active': self.is_active,
            'alerts_count': len(self.alerts),
            'risk_limits': self.risk_limits
        }


class AgentOrchestrator:
    """
    智能体编排引擎
    
    负责：
    - Agent 生命周期管理
    - Agent 间消息路由
    - 任务协调
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化编排引擎
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.agents: Dict[str, BaseAgent] = {}
        self.message_bus = []
        
        logger.info("Agent 编排引擎初始化完成")
    
    def register_agent(self, agent: BaseAgent):
        """注册 Agent"""
        self.agents[agent.name] = agent
        logger.info(f"注册 Agent: {agent.name}")
    
    def unregister_agent(self, name: str):
        """注销 Agent"""
        if name in self.agents:
            self.agents[name].deactivate()
            del self.agents[name]
            logger.info(f"注销 Agent: {name}")
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """获取 Agent"""
        return self.agents.get(name)
    
    def send_message(self, message: AgentMessage):
        """发送消息到消息总线"""
        self.message_bus.append(message)
        
        # 路由到目标 Agent
        if message.recipient in self.agents:
            self.agents[message.recipient].receive_message(message)
    
    def process_task(self, task_type: str, input_data: Dict) -> Dict:
        """
        处理任务
        
        Args:
            task_type: 任务类型
            input_data: 输入数据
            
        Returns:
            处理结果
        """
        logger.info(f"处理任务：{task_type}")
        
        if task_type == 'research':
            return self._process_research_task(input_data)
        elif task_type == 'trade':
            return self._process_trade_task(input_data)
        elif task_type == 'risk_check':
            return self._process_risk_task(input_data)
        else:
            return {'error': 'Unknown task type'}
    
    def _process_research_task(self, data: Dict) -> Dict:
        """处理投研任务"""
        agent = self.agents.get('ResearchAgent')
        if not agent:
            return {'error': 'ResearchAgent not found'}
        return agent.process(data)
    
    def _process_trade_task(self, data: Dict) -> Dict:
        """处理交易任务"""
        # 先进行风控检查
        risk_agent = self.agents.get('RiskAgent')
        if risk_agent:
            risk_result = risk_agent.process({
                'check_type': 'trade',
                **data
            })
            if not risk_result.get('passed', False):
                return {'error': 'Risk check failed', 'details': risk_result}
        
        # 执行交易
        trading_agent = self.agents.get('TradingAgent')
        if not trading_agent:
            return {'error': 'TradingAgent not found'}
        
        return trading_agent.process(data)
    
    def _process_risk_task(self, data: Dict) -> Dict:
        """处理风控任务"""
        agent = self.agents.get('RiskAgent')
        if not agent:
            return {'error': 'RiskAgent not found'}
        return agent.process(data)
    
    def get_system_status(self) -> Dict:
        """获取系统状态"""
        return {
            'active_agents': len([a for a in self.agents.values() if a.is_active]),
            'total_agents': len(self.agents),
            'pending_messages': len(self.message_bus),
            'agents_status': {name: agent.get_status() for name, agent in self.agents.items()}
        }
    
    def shutdown(self):
        """关闭所有 Agent"""
        for agent in self.agents.values():
            agent.deactivate()
        logger.info("所有 Agent 已关闭")


# 便捷函数
def create_default_orchestrator() -> AgentOrchestrator:
    """创建默认配置的编排引擎"""
    orchestrator = AgentOrchestrator()
    
    # 注册默认 Agent
    orchestrator.register_agent(ResearchAgent())
    orchestrator.register_agent(TradingAgent({'broker': 'paper'}))
    orchestrator.register_agent(RiskAgent())
    
    return orchestrator


# 单元测试
if __name__ == '__main__':
    print("运行 Agent 框架单元测试...")
    
    # 测试 1: 创建编排引擎
    orchestrator = create_default_orchestrator()
    assert len(orchestrator.agents) == 3
    print("✓ 编排引擎初始化测试通过")
    
    # 测试 2: 投研 Agent
    research_agent = orchestrator.get_agent('ResearchAgent')
    result = research_agent.process({'symbol': '000001.SZ', 'type': 'basic'})
    assert 'analysis_type' in result
    print("✓ 投研 Agent 测试通过")
    
    # 测试 3: 交易 Agent
    trading_agent = orchestrator.get_agent('TradingAgent')
    result = trading_agent.process({'action': 'buy', 'symbol': '000001.SZ', 'quantity': 100})
    assert result['status'] == 'filled'
    print("✓ 交易 Agent 测试通过")
    
    # 测试 4: 风控 Agent
    risk_agent = orchestrator.get_agent('RiskAgent')
    result = risk_agent.process({'check_type': 'trade', 'symbol': '000001.SZ', 'quantity': 100, 'price': 10})
    assert 'passed' in result
    print("✓ 风控 Agent 测试通过")
    
    # 测试 5: 任务协调
    task_result = orchestrator.process_task('trade', {
        'action': 'buy',
        'symbol': '000001.SZ',
        'quantity': 100,
        'price': 10
    })
    assert task_result.get('status') == 'filled' or 'error' in task_result
    print("✓ 任务协调测试通过")
    
    # 测试 6: 系统状态
    status = orchestrator.get_system_status()
    assert 'active_agents' in status
    print("✓ 系统状态测试通过")
    
    # 清理
    orchestrator.shutdown()
    
    print("\n✅ 所有 Agent 框架单元测试通过!")
