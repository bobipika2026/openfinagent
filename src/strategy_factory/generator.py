"""
策略代码生成器 - 根据解析的参数生成可执行的策略代码

支持策略类型:
- 均线交叉 (ma_cross)
- 动量策略 (momentum)
- 布林带策略 (bollinger)
- RSI 策略 (rsi)

生成的代码符合现有策略接口规范，继承自 BaseStrategy 类。

作者：OpenFinAgent Team
版本：1.0.0
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class StrategyCodeGenerator:
    """
    策略代码生成器
    
    根据 NLP 解析后的参数生成可执行的策略代码。
    生成的代码继承自 BaseStrategy，实现 generate_signals 和 on_bar 方法。
    
    Attributes:
        strategy_templates: 策略模板字典
    """
    
    def __init__(self):
        """初始化策略代码生成器"""
        self.strategy_templates = {
            'ma_cross': self._get_ma_cross_template,
            'momentum': self._get_momentum_template,
            'bollinger': self._get_bollinger_template,
            'rsi': self._get_rsi_template,
        }
    
    def generate(
        self,
        strategy_type: str,
        params: Dict[str, Any],
        name: str,
        initial_capital: float = 100000.0
    ) -> str:
        """
        生成策略代码
        
        Args:
            strategy_type: 策略类型 (ma_cross/momentum/bollinger/rsi)
            params: 策略参数字典
            name: 策略名称
            initial_capital: 初始资金
        
        Returns:
            生成的策略代码字符串
        
        Raises:
            ValueError: 当策略类型不支持时
        """
        if strategy_type not in self.strategy_templates:
            supported = ', '.join(self.strategy_templates.keys())
            raise ValueError(
                f"不支持的策略类型：{strategy_type}，支持的类型：{supported}"
            )
        
        template_func = self.strategy_templates[strategy_type]
        code = template_func(params, name, initial_capital)
        
        logger.info(f"生成策略代码：{name}, 类型：{strategy_type}")
        
        return code
    
    def _get_ma_cross_template(
        self,
        params: Dict[str, Any],
        name: str,
        initial_capital: float
    ) -> str:
        """
        获取均线交叉策略模板
        
        Args:
            params: 策略参数
            name: 策略名称
            initial_capital: 初始资金
        
        Returns:
            策略代码
        """
        short_window = params.get('short_window', 5)
        long_window = params.get('long_window', 20)
        
        code = f'''"""
{name} - 均线交叉策略

策略逻辑:
- 当短期均线 ({short_window}日) 上穿长期均线 ({long_window}日) 时买入
- 当短期均线下穿长期均线时卖出

作者：OpenFinAgent Strategy Factory
创建时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime

from strategy.base import BaseStrategy


class {name.replace(' ', '').replace('-', '_')}Strategy(BaseStrategy):
    """
    {name} - 均线交叉策略实现
    
    Attributes:
        short_window: 短期均线周期 ({short_window}日)
        long_window: 长期均线周期 ({long_window}日)
    """
    
    def __init__(
        self,
        name: str = "{name}",
        initial_capital: float = {initial_capital},
        commission_rate: float = 0.0003,
        slippage: float = 0.001,
        short_window: int = {short_window},
        long_window: int = {long_window}
    ):
        """
        初始化策略
        
        Args:
            name: 策略名称
            initial_capital: 初始资金
            commission_rate: 手续费率
            slippage: 滑点
            short_window: 短期均线周期
            long_window: 长期均线周期
        """
        super().__init__(name, initial_capital, commission_rate, slippage)
        
        self.short_window = short_window
        self.long_window = long_window
        
        self.prev_short_ma = None
        self.prev_long_ma = None
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成交易信号
        
        Args:
            data: 市场数据 DataFrame，包含 'close' 列
        
        Returns:
            信号 Series (1=买入，-1=卖出，0=持有)
        """
        if 'close' not in data.columns:
            raise ValueError("数据必须包含 'close' 列")
        
        # 计算均线
        short_ma = data['close'].rolling(window=self.short_window).mean()
        long_ma = data['close'].rolling(window=self.long_window).mean()
        
        # 生成信号
        signals = pd.Series(0, index=data.index)
        
        # 金叉买入：短期均线上穿长期均线
        signals[(short_ma > long_ma) & (short_ma.shift(1) <= long_ma.shift(1))] = 1
        
        # 死叉卖出：短期均线下穿长期均线
        signals[(short_ma < long_ma) & (short_ma.shift(1) >= long_ma.shift(1))] = -1
        
        return signals
    
    def on_bar(self, data: pd.DataFrame, index: int) -> Optional[Dict[str, Any]]:
        """
        每根 K 线回调 - 策略核心逻辑
        
        Args:
            data: 市场数据 DataFrame
            index: 当前 K 线索引
        
        Returns:
            交易指令字典，包含 action/price/shares/timestamp
        """
        if index < self.long_window:
            return None
        
        # 获取当前和历史均线值
        close_prices = data['close'].iloc[:index + 1]
        short_ma = close_prices.rolling(window=self.short_window).mean().iloc[-1]
        long_ma = close_prices.rolling(window=self.long_window).mean().iloc[-1]
        
        prev_short_ma = close_prices.rolling(window=self.short_window).mean().iloc[-2]
        prev_long_ma = close_prices.rolling(window=self.long_window).mean().iloc[-2]
        
        current_price = data['close'].iloc[index]
        timestamp = data.index[index]
        
        # 检测金叉
        if short_ma > long_ma and prev_short_ma <= prev_long_ma:
            shares = self.calculate_position_size(current_price, 1)
            if shares > 0:
                return {{
                    'action': 'buy',
                    'price': current_price,
                    'shares': shares,
                    'timestamp': timestamp
                }}
        
        # 检测死叉
        elif short_ma < long_ma and prev_short_ma >= prev_long_ma:
            current_shares = self.positions.get('shares', 0)
            if current_shares > 0:
                return {{
                    'action': 'sell',
                    'price': current_price,
                    'shares': current_shares,
                    'timestamp': timestamp
                }}
        
        return None
    
    def get_params(self) -> Dict[str, Any]:
        """获取策略参数"""
        return {{
            'strategy_type': 'ma_cross',
            'short_window': self.short_window,
            'long_window': self.long_window
        }}
'''
        return code
    
    def _get_momentum_template(
        self,
        params: Dict[str, Any],
        name: str,
        initial_capital: float
    ) -> str:
        """
        获取动量策略模板
        
        Args:
            params: 策略参数
            name: 策略名称
            initial_capital: 初始资金
        
        Returns:
            策略代码
        """
        lookback_period = params.get('lookback_period', 20)
        threshold = params.get('threshold', 0.05)
        
        code = f'''"""
{name} - 动量策略

策略逻辑:
- 当价格超过过去{lookback_period}日收益率阈值 ({threshold*100}%) 时买入
- 当价格低于过去{lookback_period}日收益率阈值时卖出

作者：OpenFinAgent Strategy Factory
创建时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime

from strategy.base import BaseStrategy


class {name.replace(' ', '').replace('-', '_')}Strategy(BaseStrategy):
    """
    {name} - 动量策略实现
    
    Attributes:
        lookback_period: 回看周期 ({lookback_period}日)
        threshold: 收益率阈值 ({threshold*100}%)
    """
    
    def __init__(
        self,
        name: str = "{name}",
        initial_capital: float = {initial_capital},
        commission_rate: float = 0.0003,
        slippage: float = 0.001,
        lookback_period: int = {lookback_period},
        threshold: float = {threshold}
    ):
        """
        初始化策略
        
        Args:
            name: 策略名称
            initial_capital: 初始资金
            commission_rate: 手续费率
            slippage: 滑点
            lookback_period: 回看周期
            threshold: 收益率阈值
        """
        super().__init__(name, initial_capital, commission_rate, slippage)
        
        self.lookback_period = lookback_period
        self.threshold = threshold
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成交易信号
        
        Args:
            data: 市场数据 DataFrame，包含 'close' 列
        
        Returns:
            信号 Series (1=买入，-1=卖出，0=持有)
        """
        if 'close' not in data.columns:
            raise ValueError("数据必须包含 'close' 列")
        
        # 计算动量 (收益率)
        momentum = data['close'].pct_change(periods=self.lookback_period)
        
        # 生成信号
        signals = pd.Series(0, index=data.index)
        signals[momentum > self.threshold] = 1
        signals[momentum < -self.threshold] = -1
        
        return signals
    
    def on_bar(self, data: pd.DataFrame, index: int) -> Optional[Dict[str, Any]]:
        """
        每根 K 线回调 - 策略核心逻辑
        
        Args:
            data: 市场数据 DataFrame
            index: 当前 K 线索引
        
        Returns:
            交易指令字典
        """
        if index < self.lookback_period:
            return None
        
        current_price = data['close'].iloc[index]
        past_price = data['close'].iloc[index - self.lookback_period]
        momentum = (current_price - past_price) / past_price
        
        timestamp = data.index[index]
        
        # 强动量买入
        if momentum > self.threshold:
            shares = self.calculate_position_size(current_price, 1)
            if shares > 0:
                return {{
                    'action': 'buy',
                    'price': current_price,
                    'shares': shares,
                    'timestamp': timestamp
                }}
        
        # 强负动量卖出
        elif momentum < -self.threshold:
            current_shares = self.positions.get('shares', 0)
            if current_shares > 0:
                return {{
                    'action': 'sell',
                    'price': current_price,
                    'shares': current_shares,
                    'timestamp': timestamp
                }}
        
        return None
    
    def get_params(self) -> Dict[str, Any]:
        """获取策略参数"""
        return {{
            'strategy_type': 'momentum',
            'lookback_period': self.lookback_period,
            'threshold': self.threshold
        }}
'''
        return code
    
    def _get_bollinger_template(
        self,
        params: Dict[str, Any],
        name: str,
        initial_capital: float
    ) -> str:
        """
        获取布林带策略模板
        
        Args:
            params: 策略参数
            name: 策略名称
            initial_capital: 初始资金
        
        Returns:
            策略代码
        """
        window = params.get('window', 20)
        num_std = params.get('num_std', 2.0)
        
        code = f'''"""
{name} - 布林带策略

策略逻辑:
- 当价格触及下轨时买入 (超卖)
- 当价格触及上轨时卖出 (超买)
- 使用{window}日移动平均线和{num_std}倍标准差

作者：OpenFinAgent Strategy Factory
创建时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime

from strategy.base import BaseStrategy


class {name.replace(' ', '').replace('-', '_')}Strategy(BaseStrategy):
    """
    {name} - 布林带策略实现
    
    Attributes:
        window: 均线周期 ({window}日)
        num_std: 标准差倍数 ({num_std}倍)
    """
    
    def __init__(
        self,
        name: str = "{name}",
        initial_capital: float = {initial_capital},
        commission_rate: float = 0.0003,
        slippage: float = 0.001,
        window: int = {window},
        num_std: float = {num_std}
    ):
        """
        初始化策略
        
        Args:
            name: 策略名称
            initial_capital: 初始资金
            commission_rate: 手续费率
            slippage: 滑点
            window: 均线周期
            num_std: 标准差倍数
        """
        super().__init__(name, initial_capital, commission_rate, slippage)
        
        self.window = window
        self.num_std = num_std
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成交易信号
        
        Args:
            data: 市场数据 DataFrame，包含 'close' 列
        
        Returns:
            信号 Series (1=买入，-1=卖出，0=持有)
        """
        if 'close' not in data.columns:
            raise ValueError("数据必须包含 'close' 列")
        
        # 计算布林带
        middle = data['close'].rolling(window=self.window).mean()
        std = data['close'].rolling(window=self.window).std()
        upper = middle + self.num_std * std
        lower = middle - self.num_std * std
        
        # 生成信号
        signals = pd.Series(0, index=data.index)
        signals[data['close'] < lower] = 1  # 触及下轨买入
        signals[data['close'] > upper] = -1  # 触及上轨卖出
        
        return signals
    
    def on_bar(self, data: pd.DataFrame, index: int) -> Optional[Dict[str, Any]]:
        """
        每根 K 线回调 - 策略核心逻辑
        
        Args:
            data: 市场数据 DataFrame
            index: 当前 K 线索引
        
        Returns:
            交易指令字典
        """
        if index < self.window:
            return None
        
        current_price = data['close'].iloc[index]
        timestamp = data.index[index]
        
        # 计算布林带
        close_prices = data['close'].iloc[:index + 1]
        middle = close_prices.rolling(window=self.window).mean().iloc[-1]
        std = close_prices.rolling(window=self.window).std().iloc[-1]
        upper = middle + self.num_std * std
        lower = middle - self.num_std * std
        
        # 触及下轨买入
        if current_price < lower:
            shares = self.calculate_position_size(current_price, 1)
            if shares > 0:
                return {{
                    'action': 'buy',
                    'price': current_price,
                    'shares': shares,
                    'timestamp': timestamp
                }}
        
        # 触及上轨卖出
        elif current_price > upper:
            current_shares = self.positions.get('shares', 0)
            if current_shares > 0:
                return {{
                    'action': 'sell',
                    'price': current_price,
                    'shares': current_shares,
                    'timestamp': timestamp
                }}
        
        return None
    
    def get_params(self) -> Dict[str, Any]:
        """获取策略参数"""
        return {{
            'strategy_type': 'bollinger',
            'window': self.window,
            'num_std': self.num_std
        }}
'''
        return code
    
    def _get_rsi_template(
        self,
        params: Dict[str, Any],
        name: str,
        initial_capital: float
    ) -> str:
        """
        获取 RSI 策略模板
        
        Args:
            params: 策略参数
            name: 策略名称
            initial_capital: 初始资金
        
        Returns:
            策略代码
        """
        period = params.get('period', 14)
        oversold = params.get('oversold', 30)
        overbought = params.get('overbought', 70)
        
        code = f'''"""
{name} - RSI 策略

策略逻辑:
- 当 RSI 低于{oversold}时买入 (超卖)
- 当 RSI 高于{overbought}时卖出 (超买)
- 使用{period}日 RSI 计算

作者：OpenFinAgent Strategy Factory
创建时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime

from strategy.base import BaseStrategy


class {name.replace(' ', '').replace('-', '_')}Strategy(BaseStrategy):
    """
    {name} - RSI 策略实现
    
    Attributes:
        period: RSI 周期 ({period}日)
        oversold: 超卖阈值 ({oversold})
        overbought: 超买阈值 ({overbought})
    """
    
    def __init__(
        self,
        name: str = "{name}",
        initial_capital: float = {initial_capital},
        commission_rate: float = 0.0003,
        slippage: float = 0.001,
        period: int = {period},
        oversold: int = {oversold},
        overbought: int = {overbought}
    ):
        """
        初始化策略
        
        Args:
            name: 策略名称
            initial_capital: 初始资金
            commission_rate: 手续费率
            slippage: 滑点
            period: RSI 周期
            oversold: 超卖阈值
            overbought: 超买阈值
        """
        super().__init__(name, initial_capital, commission_rate, slippage)
        
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
    
    def _calculate_rsi(self, prices: pd.Series) -> float:
        """
        计算 RSI 指标
        
        Args:
            prices: 价格序列
        
        Returns:
            RSI 值
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        rs = gain / loss if loss != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if len(rsi) > 0 else 50
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成交易信号
        
        Args:
            data: 市场数据 DataFrame，包含 'close' 列
        
        Returns:
            信号 Series (1=买入，-1=卖出，0=持有)
        """
        if 'close' not in data.columns:
            raise ValueError("数据必须包含 'close' 列")
        
        # 计算 RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # 生成信号
        signals = pd.Series(0, index=data.index)
        signals[rsi < self.oversold] = 1  # 超卖买入
        signals[rsi > self.overbought] = -1  # 超买卖出
        
        return signals
    
    def on_bar(self, data: pd.DataFrame, index: int) -> Optional[Dict[str, Any]]:
        """
        每根 K 线回调 - 策略核心逻辑
        
        Args:
            data: 市场数据 DataFrame
            index: 当前 K 线索引
        
        Returns:
            交易指令字典
        """
        if index < self.period:
            return None
        
        current_price = data['close'].iloc[index]
        timestamp = data.index[index]
        
        # 计算 RSI
        close_prices = data['close'].iloc[:index + 1]
        rsi = self._calculate_rsi(close_prices)
        
        # 超卖买入
        if rsi < self.oversold:
            shares = self.calculate_position_size(current_price, 1)
            if shares > 0:
                return {{
                    'action': 'buy',
                    'price': current_price,
                    'shares': shares,
                    'timestamp': timestamp
                }}
        
        # 超买卖出
        elif rsi > self.overbought:
            current_shares = self.positions.get('shares', 0)
            if current_shares > 0:
                return {{
                    'action': 'sell',
                    'price': current_price,
                    'shares': current_shares,
                    'timestamp': timestamp
                }}
        
        return None
    
    def get_params(self) -> Dict[str, Any]:
        """获取策略参数"""
        return {{
            'strategy_type': 'rsi',
            'period': self.period,
            'oversold': self.oversold,
            'overbought': self.overbought
        }}
'''
        return code
