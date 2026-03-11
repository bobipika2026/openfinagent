"""
信号检测器 - 交易信号检测

根据策略和市场数据检测买入、卖出、持有信号。

@module: monitor.signal_detector
@author: OpenFinAgent Team
@version: 1.0.0
"""

import logging
from datetime import datetime
from typing import Optional, Any, Dict
from dataclasses import dataclass, field
from enum import Enum
import uuid

import pandas as pd
import numpy as np

try:
    from ..strategy.base import BaseStrategy
except ImportError:
    from strategy.base import BaseStrategy

logger = logging.getLogger(__name__)


class SignalType(Enum):
    """信号类型"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class Signal:
    """
    交易信号数据模型
    
    Attributes:
        id: 信号 ID
        symbol: 股票代码
        signal_type: 信号类型
        strategy_id: 策略 ID
        price: 信号触发价格
        timestamp: 信号时间
        confidence: 置信度 (0-1)
        metadata: 附加信息
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = ""
    signal_type: SignalType = SignalType.HOLD
    strategy_id: str = ""
    price: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'signal_type': self.signal_type.value,
            'strategy_id': self.strategy_id,
            'price': self.price,
            'timestamp': self.timestamp.isoformat(),
            'confidence': self.confidence,
            'metadata': self.metadata
        }
    
    def __repr__(self) -> str:
        return (
            f"Signal(id={self.id}, symbol={self.symbol}, "
            f"type={self.signal_type.value}, price={self.price:.2f})"
        )


class SignalDetector:
    """
    信号检测器
    
    根据策略生成的信号和市场数据，检测交易机会。
    支持多种信号确认机制，减少假信号。
    
    Attributes:
        min_confidence: 最小置信度阈值
        price_window: 价格窗口大小
    """
    
    def __init__(
        self,
        min_confidence: float = 0.6,
        price_window: int = 5
    ):
        """
        初始化信号检测器
        
        Args:
            min_confidence: 最小置信度阈值 (0-1)
            price_window: 价格窗口大小
        """
        self.min_confidence = min_confidence
        self.price_window = price_window
        self._signal_history: Dict[str, Signal] = {}
        
        logger.info(
            f"信号检测器初始化：min_confidence={min_confidence}, "
            f"price_window={price_window}"
        )
    
    def check_signal(
        self,
        strategy: BaseStrategy,
        symbol: str,
        data: pd.DataFrame
    ) -> Optional[Signal]:
        """
        检测交易信号
        
        Args:
            strategy: 策略实例
            symbol: 股票代码
            data: 市场数据 DataFrame
            
        Returns:
            信号对象，无信号则返回 None
            
        Raises:
            ValueError: 当数据格式不合法时
        """
        try:
            # 验证数据
            if data is None or data.empty:
                logger.debug(f"数据为空：{symbol}")
                return None
            
            required_columns = ['close']
            if not all(col in data.columns for col in required_columns):
                logger.warning(f"数据缺少必要列：{symbol}, 需要 {required_columns}")
                return None
            
            # 获取最新数据
            latest_data = data.tail(self.price_window)
            
            if len(latest_data) < 2:
                logger.debug(f"数据不足：{symbol}, 需要至少 2 条记录")
                return None
            
            # 使用策略生成信号
            current_price = latest_data['close'].iloc[-1]
            previous_price = latest_data['close'].iloc[-2]
            
            # 调用策略的信号生成方法
            if hasattr(strategy, 'generate_signals'):
                try:
                    signals = strategy.generate_signals(latest_data)
                    if signals is not None and len(signals) > 0:
                        raw_signal = signals.iloc[-1]
                        
                        # 解析信号
                        signal_type = self._parse_signal_value(raw_signal)
                        
                        if signal_type != SignalType.HOLD:
                            # 计算置信度
                            confidence = self._calculate_confidence(
                                latest_data,
                                signal_type
                            )
                            
                            # 创建信号对象
                            signal = Signal(
                                symbol=symbol,
                                signal_type=signal_type,
                                strategy_id=strategy.name,
                                price=current_price,
                                timestamp=datetime.now(),
                                confidence=confidence,
                                metadata={
                                    'previous_price': previous_price,
                                    'price_change': (current_price - previous_price) / previous_price,
                                    'volume': latest_data.get('volume', [0]).iloc[-1] if 'volume' in latest_data.columns else 0
                                }
                            )
                            
                            # 检查置信度阈值
                            if confidence >= self.min_confidence:
                                self._signal_history[symbol] = signal
                                logger.info(
                                    f"信号生成：{symbol}, "
                                    f"类型：{signal_type.value}, "
                                    f"置信度：{confidence:.2f}"
                                )
                                return signal
                            else:
                                logger.debug(
                                    f"信号置信度不足：{symbol}, "
                                    f"{confidence:.2f} < {self.min_confidence}"
                                )
                
                except Exception as e:
                    logger.error(f"策略信号生成失败：{symbol}, {e}")
            
            # 备用方案：基于价格变化检测信号
            return self._detect_price_signal(symbol, latest_data, current_price)
            
        except Exception as e:
            logger.error(f"信号检测失败：{symbol}, {e}", exc_info=True)
            return None
    
    def _parse_signal_value(self, signal_value: Any) -> SignalType:
        """
        解析信号值
        
        Args:
            signal_value: 信号值 (1/-1/0 或其他格式)
            
        Returns:
            信号类型
        """
        try:
            if isinstance(signal_value, (int, float)):
                if signal_value > 0:
                    return SignalType.BUY
                elif signal_value < 0:
                    return SignalType.SELL
                else:
                    return SignalType.HOLD
            else:
                # 尝试转换为数字
                value = float(signal_value)
                return self._parse_signal_value(value)
        except (ValueError, TypeError):
            logger.warning(f"无法解析信号值：{signal_value}")
            return SignalType.HOLD
    
    def _detect_price_signal(
        self,
        symbol: str,
        data: pd.DataFrame,
        current_price: float
    ) -> Optional[Signal]:
        """
        基于价格变化检测信号（备用方案）
        
        Args:
            symbol: 股票代码
            data: 市场数据
            current_price: 当前价格
            
        Returns:
            信号对象或 None
        """
        # 计算价格变化率
        price_change = (data['close'].pct_change()).iloc[-1]
        
        if pd.isna(price_change):
            return None
        
        # 简单阈值策略
        if price_change > 0.02:  # 上涨超过 2%
            signal_type = SignalType.BUY
            confidence = min(price_change / 0.05, 1.0)
        elif price_change < -0.02:  # 下跌超过 2%
            signal_type = SignalType.SELL
            confidence = min(abs(price_change) / 0.05, 1.0)
        else:
            return None
        
        if confidence >= self.min_confidence:
            signal = Signal(
                symbol=symbol,
                signal_type=signal_type,
                strategy_id="price_change_detector",
                price=current_price,
                timestamp=datetime.now(),
                confidence=confidence,
                metadata={
                    'price_change': price_change,
                    'method': 'price_change'
                }
            )
            
            logger.info(
                f"价格信号：{symbol}, "
                f"类型：{signal_type.value}, "
                f"变化率：{price_change:.2%}"
            )
            return signal
        
        return None
    
    def _calculate_confidence(
        self,
        data: pd.DataFrame,
        signal_type: SignalType
    ) -> float:
        """
        计算信号置信度
        
        Args:
            data: 市场数据
            signal_type: 信号类型
            
        Returns:
            置信度 (0-1)
        """
        confidence = 0.5  # 基础置信度
        
        # 基于成交量确认
        if 'volume' in data.columns:
            avg_volume = data['volume'].mean()
            latest_volume = data['volume'].iloc[-1]
            
            if latest_volume > avg_volume * 1.5:
                confidence += 0.2  # 放量确认
            elif latest_volume > avg_volume:
                confidence += 0.1
        
        # 基于价格趋势确认
        if len(data) >= 3:
            recent_trend = data['close'].iloc[-3:].pct_change().mean()
            
            if signal_type == SignalType.BUY and recent_trend > 0:
                confidence += 0.15
            elif signal_type == SignalType.SELL and recent_trend < 0:
                confidence += 0.15
        
        # 基于波动率确认
        if len(data) >= 5:
            volatility = data['close'].std()
            avg_price = data['close'].mean()
            volatility_ratio = volatility / avg_price
            
            if volatility_ratio > 0.03:  # 高波动
                confidence += 0.1
        
        return min(confidence, 1.0)
    
    def get_signal_history(self, symbol: Optional[str] = None) -> Dict[str, Signal]:
        """
        获取信号历史
        
        Args:
            symbol: 股票代码，为 None 则返回所有
            
        Returns:
            信号历史字典
        """
        if symbol:
            return {symbol: self._signal_history.get(symbol)}
        return self._signal_history.copy()
    
    def clear_history(self) -> None:
        """清除信号历史"""
        self._signal_history.clear()
        logger.info("信号历史已清除")
