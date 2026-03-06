"""
辅助工具函数
"""

from datetime import datetime, timedelta
from typing import Union


def format_currency(value: Union[float, int], currency: str = '¥') -> str:
    """
    格式化货币显示

    Args:
        value: 数值
        currency: 货币符号

    Returns:
        格式化字符串
    """
    return f"{currency}{value:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    格式化百分比显示

    Args:
        value: 数值 (0-1 或 0-100)
        decimals: 小数位数

    Returns:
        格式化字符串
    """
    if value > 1:
        return f"{value:.{decimals}f}%"
    else:
        return f"{value * 100:.{decimals}f}%"


def calculate_days(start_date: str, end_date: str) -> int:
    """
    计算两个日期之间的天数

    Args:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)

    Returns:
        天数
    """
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    return (end - start).days


def parse_date(date_str: str) -> datetime:
    """
    解析日期字符串

    Args:
        date_str: 日期字符串

    Returns:
        datetime 对象
    """
    formats = [
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%Y%m%d',
        '%Y-%m-%d %H:%M:%S',
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    raise ValueError(f"无法解析日期：{date_str}")


def truncate_float(value: float, decimals: int = 4) -> float:
    """
    截断浮点数 (不四舍五入)

    Args:
        value: 数值
        decimals: 小数位数

    Returns:
        截断后的数值
    """
    multiplier = 10 ** decimals
    return int(value * multiplier) / multiplier


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    安全除法

    Args:
        numerator: 分子
        denominator: 分母
        default: 分母为 0 时的默认值

    Returns:
        除法结果
    """
    if denominator == 0:
        return default
    return numerator / denominator
