"""
选股条件定义

定义选股策略的各种筛选条件和评分标准

@module: stock_selector.criteria
@author: OpenFinAgent Team
@version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class SelectionMethod(Enum):
    """选股方法枚举"""
    SCORE_BASED = "score_based"  # 基于评分
    SHARPE_BASED = "sharpe_based"  # 基于夏普比率
    RETURN_BASED = "return_based"  # 基于收益率
    CUSTOM = "custom"  # 自定义


@dataclass
class StockCriteria:
    """
    选股条件类
    
    定义选股的各种筛选标准和阈值
    
    Attributes:
        top_n: 选前 N 只股票 (默认 10)
        min_score: 最低评分 (默认 60)
        min_sharpe: 最低夏普比率 (默认 1.0)
        max_drawdown: 最大回撤阈值 (默认 0.20, 即 20%)
        min_return: 最低收益率 (默认 0.10, 即 10%)
        selection_method: 选股方法
        custom_filters: 自定义过滤条件
        exclude_st: 是否排除 ST 股票 (默认 True)
        exclude_new: 是否排除次新股 (默认 False)
        min_market_cap: 最小市值 (亿元)
        max_market_cap: 最大市值 (亿元)
        sectors: 行业筛选列表 (None=不限制)
    
    Example:
        ```python
        # 保守型选股条件
        criteria = StockCriteria(
            top_n=20,
            min_score=70,
            min_sharpe=1.5,
            max_drawdown=0.15,
            min_return=0.15
        )
        
        # 激进型选股条件
        criteria = StockCriteria(
            top_n=10,
            min_score=60,
            min_sharpe=0.8,
            max_drawdown=0.30,
            min_return=0.30
        )
        ```
    """
    
    # 核心筛选条件
    top_n: int = 10
    min_score: float = 60.0
    min_sharpe: float = 1.0
    max_drawdown: float = 0.20
    min_return: float = 0.10
    
    # 选股方法
    selection_method: SelectionMethod = SelectionMethod.SCORE_BASED
    
    # 自定义过滤条件
    custom_filters: Dict[str, Any] = field(default_factory=dict)
    
    # 特殊筛选
    exclude_st: bool = True
    exclude_new: bool = False
    new_stock_days: int = 60  # 定义次新股的天数阈值
    
    # 市值筛选 (亿元)
    min_market_cap: Optional[float] = None
    max_market_cap: Optional[float] = None
    
    # 行业筛选
    sectors: Optional[List[str]] = None
    
    # 技术面筛选
    min_volume: Optional[float] = None  # 最小日均成交量 (手)
    min_price: Optional[float] = None  # 最低股价
    max_price: Optional[float] = None  # 最高股价
    
    def validate(self) -> bool:
        """
        验证条件的合法性
        
        Returns:
            是否合法
            
        Raises:
            ValueError: 当条件不合法时
        """
        if self.top_n <= 0:
            raise ValueError(f"top_n 必须大于 0，当前值：{self.top_n}")
        
        if not 0 <= self.min_score <= 100:
            raise ValueError(f"min_score 必须在 0-100 之间，当前值：{self.min_score}")
        
        if not 0 <= self.max_drawdown <= 1:
            raise ValueError(f"max_drawdown 必须在 0-1 之间，当前值：{self.max_drawdown}")
        
        if self.min_market_cap and self.max_market_cap:
            if self.min_market_cap > self.max_market_cap:
                raise ValueError(
                    f"min_market_cap 不能大于 max_market_cap: "
                    f"{self.min_market_cap} > {self.max_market_cap}"
                )
        
        if self.min_price and self.max_price:
            if self.min_price > self.max_price:
                raise ValueError(
                    f"min_price 不能大于 max_price: "
                    f"{self.min_price} > {self.max_price}"
                )
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            条件字典
        """
        return {
            'top_n': self.top_n,
            'min_score': self.min_score,
            'min_sharpe': self.min_sharpe,
            'max_drawdown': self.max_drawdown,
            'min_return': self.min_return,
            'selection_method': self.selection_method.value,
            'exclude_st': self.exclude_st,
            'exclude_new': self.exclude_new,
            'new_stock_days': self.new_stock_days,
            'min_market_cap': self.min_market_cap,
            'max_market_cap': self.max_market_cap,
            'sectors': self.sectors,
            'min_volume': self.min_volume,
            'min_price': self.min_price,
            'max_price': self.max_price,
            'custom_filters': self.custom_filters
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StockCriteria':
        """
        从字典创建实例
        
        Args:
            data: 条件字典
        
        Returns:
            StockCriteria 实例
        """
        # 转换 selection_method
        if 'selection_method' in data and isinstance(data['selection_method'], str):
            data['selection_method'] = SelectionMethod(data['selection_method'])
        
        return cls(**data)
    
    def __repr__(self) -> str:
        return (
            f"StockCriteria(top_n={self.top_n}, min_score={self.min_score}, "
            f"min_sharpe={self.min_sharpe}, max_drawdown={self.max_drawdown})"
        )


@dataclass
class StockScore:
    """
    个股评分数据类
    
    存储单只股票的各项评分指标
    
    Attributes:
        symbol: 股票代码
        name: 股票名称
        total_score: 综合评分 (0-100)
        sharpe_ratio: 夏普比率
        max_drawdown: 最大回撤
        total_return: 总收益率
        annual_return: 年化收益率
        volatility: 波动率
        win_rate: 胜率
        profit_factor: 盈亏比
        market_cap: 市值 (亿元)
        sector: 所属行业
        pe_ratio: 市盈率
        pb_ratio: 市净率
        details: 详细评分明细
    
    Example:
        ```python
        score = StockScore(
            symbol='000001.SZ',
            name='平安银行',
            total_score=85.5,
            sharpe_ratio=1.8,
            max_drawdown=0.15,
            total_return=0.35
        )
        ```
    """
    
    symbol: str
    name: str = ""
    total_score: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    total_return: float = 0.0
    annual_return: float = 0.0
    volatility: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    market_cap: float = 0.0
    sector: str = ""
    pe_ratio: float = 0.0
    pb_ratio: float = 0.0
    details: Dict[str, float] = field(default_factory=dict)
    
    def meets_criteria(self, criteria: StockCriteria) -> bool:
        """
        检查是否满足选股条件
        
        Args:
            criteria: 选股条件
        
        Returns:
            是否满足
        """
        # 检查评分
        if self.total_score < criteria.min_score:
            return False
        
        # 检查夏普比率
        if self.sharpe_ratio < criteria.min_sharpe:
            return False
        
        # 检查最大回撤
        if self.max_drawdown > criteria.max_drawdown:
            return False
        
        # 检查收益率
        if self.total_return < criteria.min_return:
            return False
        
        # 检查市值
        if criteria.min_market_cap and self.market_cap < criteria.min_market_cap:
            return False
        
        if criteria.max_market_cap and self.market_cap > criteria.max_market_cap:
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            评分字典
        """
        return {
            'symbol': self.symbol,
            'name': self.name,
            'total_score': self.total_score,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'total_return': self.total_return,
            'annual_return': self.annual_return,
            'volatility': self.volatility,
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'market_cap': self.market_cap,
            'sector': self.sector,
            'pe_ratio': self.pe_ratio,
            'pb_ratio': self.pb_ratio,
            'details': self.details
        }
    
    def __repr__(self) -> str:
        return f"StockScore(symbol='{self.symbol}', score={self.total_score:.2f})"


@dataclass
class FilterResult:
    """
    筛选结果数据类
    
    存储筛选过程中的中间结果
    
    Attributes:
        symbol: 股票代码
        passed: 是否通过筛选
        failed_reasons: 失败原因列表
        score: 评分对象
    
    Example:
        ```python
        result = FilterResult(
            symbol='000001.SZ',
            passed=True,
            failed_reasons=[],
            score=stock_score
        )
        ```
    """
    
    symbol: str
    passed: bool
    failed_reasons: List[str] = field(default_factory=list)
    score: Optional[StockScore] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'symbol': self.symbol,
            'passed': self.passed,
            'failed_reasons': self.failed_reasons,
            'score': self.score.to_dict() if self.score else None
        }
