"""
OpenFinAgent - 金融 AI Agent 操作系统

让每个人拥有自己的私人投行 AI，让每个开发者都能构建金融智能体
"""

__version__ = "0.1.0"
__author__ = "OpenFinAgent Team"
__email__ = "hi@openfinagent.ai"

from .core import Agent, create_engine
from .agents import ResearchAgent, TradingAgent, RiskAgent, AgentOrchestrator
from .backtest import BacktestEngine

__all__ = [
    "Agent",
    "create_engine",
    "ResearchAgent",
    "TradingAgent",
    "RiskAgent",
    "AgentOrchestrator",
    "BacktestEngine",
]
