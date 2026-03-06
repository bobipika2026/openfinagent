"""
技术指标计算模块

提供常用技术指标的计算函数，供策略使用。

@module: strategy.indicators
@author: TradeFlow AI Team
@version: 2.0.0
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def calculate_sma(series: pd.Series, window: int) -> pd.Series:
    """
    计算简单移动平均线 (SMA)

    Args:
        series: 价格序列
        window: 计算周期

    Returns:
        SMA 序列
    """
    if window <= 0:
        raise ValueError(f"窗口必须大于 0，当前值：{window}")
    return series.rolling(window=window).mean()


def calculate_ema(series: pd.Series, window: int) -> pd.Series:
    """
    计算指数移动平均线 (EMA)

    Args:
        series: 价格序列
        window: 计算周期

    Returns:
        EMA 序列
    """
    if window <= 0:
        raise ValueError(f"窗口必须大于 0，当前值：{window}")
    return series.ewm(span=window, adjust=False).mean()


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    计算相对强弱指数 (RSI)

    RSI = 100 - 100 / (1 + RS)
    RS = 平均涨幅 / 平均跌幅

    Args:
        series: 价格序列 (通常为收盘价)
        period: 计算周期 (默认 14)

    Returns:
        RSI 序列 (0-100)

    Reference:
        Wilder, J. W. (1978). New Concepts in Technical Trading Systems
    """
    if period <= 1:
        raise ValueError(f"RSI 周期必须大于 1，当前值：{period}")

    # 计算价格变化
    delta = series.diff()

    # 分离涨跌
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    # 计算平均涨跌幅 (使用 EMA 平滑)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()

    # 计算 RS 和 RSI
    rs = avg_gain / avg_loss.replace(0, np.inf)
    rsi = 100 - (100 / (1 + rs))

    # 处理除零情况
    rsi = rsi.replace([np.inf, -np.inf], np.nan).fillna(50)

    logger.debug(f"RSI 计算完成：周期={period}, 有效值={rsi.notna().sum()}")
    return rsi


def calculate_macd(
    series: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    计算 MACD 指标

    MACD 由三部分组成：
    - MACD 线：快线 EMA - 慢线 EMA
    - Signal 线：MACD 线的 EMA
    - Histogram: MACD 线 - Signal 线

    Args:
        series: 价格序列 (通常为收盘价)
        fast_period: 快线周期 (默认 12)
        slow_period: 慢线周期 (默认 26)
        signal_period: 信号线周期 (默认 9)

    Returns:
        (macd_line, signal_line, histogram) 三元组

    Raises:
        ValueError: 当周期参数不合法时

    Reference:
        Appel, G. (1979). Moving Average Convergence Divergence
    """
    if fast_period >= slow_period:
        raise ValueError(f"快线周期 ({fast_period}) 必须小于慢线周期 ({slow_period})")
    if fast_period <= 0 or slow_period <= 0 or signal_period <= 0:
        raise ValueError("所有周期参数必须大于 0")

    # 计算快慢 EMA
    ema_fast = series.ewm(span=fast_period, adjust=False).mean()
    ema_slow = series.ewm(span=slow_period, adjust=False).mean()

    # MACD 线
    macd_line = ema_fast - ema_slow

    # Signal 线
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()

    # Histogram
    histogram = macd_line - signal_line

    logger.debug(
        f"MACD 计算完成：fast={fast_period}, slow={slow_period}, signal={signal_period}"
    )
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(
    series: pd.Series,
    window: int = 20,
    num_std: float = 2.0
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    计算布林带 (Bollinger Bands)

    由三部分组成：
    - 中轨：SMA
    - 上轨：中轨 + N 倍标准差
    - 下轨：中轨 - N 倍标准差

    Args:
        series: 价格序列 (通常为收盘价)
        window: 计算周期 (默认 20)
        num_std: 标准差倍数 (默认 2)

    Returns:
        (upper_band, middle_band, lower_band) 三元组

    Raises:
        ValueError: 当参数不合法时

    Reference:
        Bollinger, J. (2002). Bollinger on Bollinger Bands
    """
    if window <= 1:
        raise ValueError(f"窗口必须大于 1，当前值：{window}")
    if num_std <= 0:
        raise ValueError(f"标准差倍数必须大于 0，当前值：{num_std}")

    # 中轨 (SMA)
    middle_band = series.rolling(window=window).mean()

    # 标准差
    rolling_std = series.rolling(window=window).std()

    # 上下轨
    upper_band = middle_band + (rolling_std * num_std)
    lower_band = middle_band - (rolling_std * num_std)

    logger.debug(f"布林带计算完成：window={window}, std={num_std}")
    return upper_band, middle_band, lower_band


def calculate_atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14
) -> pd.Series:
    """
    计算平均真实波幅 (ATR)

    TR = max(
        high - low,
        abs(high - close_prev),
        abs(low - close_prev)
    )
    ATR = TR 的移动平均

    Args:
        high: 最高价序列
        low: 最低价序列
        close: 收盘价序列
        period: 计算周期 (默认 14)

    Returns:
        ATR 序列

    Raises:
        ValueError: 当参数不合法时

    Reference:
        Wilder, J. W. (1978). New Concepts in Technical Trading Systems
    """
    if period <= 1:
        raise ValueError(f"ATR 周期必须大于 1，当前值：{period}")

    # 计算真实波幅
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # ATR (使用 EMA 平滑)
    atr = tr.ewm(com=period - 1, min_periods=period).mean()

    logger.debug(f"ATR 计算完成：period={period}")
    return atr


def calculate_volume_sma(volume: pd.Series, window: int = 20) -> pd.Series:
    """
    计算成交量移动平均

    Args:
        volume: 成交量序列
        window: 计算周期

    Returns:
        成交量 SMA 序列
    """
    return calculate_sma(volume, window)


def calculate_price_volume_trend(
    close: pd.Series,
    volume: pd.Series
) -> pd.Series:
    """
    计算价量趋势指标 (PVT)

    PVT = 累计 (收益率 * 成交量)

    Args:
        close: 收盘价序列
        volume: 成交量序列

    Returns:
        PVT 序列
    """
    returns = close.pct_change()
    pvt = (returns * volume).cumsum()
    return pvt


def detect_crossover(
    series1: pd.Series,
    series2: pd.Series,
    direction: str = 'cross_above'
) -> pd.Series:
    """
    检测两条线的交叉

    Args:
        series1: 第一条线
        series2: 第二条线
        direction: 交叉方向 ('cross_above' 或 'cross_below')

    Returns:
        交叉信号序列 (1=发生交叉，0=无交叉)
    """
    if direction not in ['cross_above', 'cross_below']:
        raise ValueError(f"无效的交叉方向：{direction}")

    if direction == 'cross_above':
        # series1 从下向上穿越 series2
        crossover = (series1.shift(1) < series2.shift(1)) & (series1 > series2)
    else:
        # series1 从上向下穿越 series2
        crossover = (series1.shift(1) > series2.shift(1)) & (series1 < series2)

    return crossover.astype(int)


def is_overbought(rsi: pd.Series, threshold: float = 70.0) -> pd.Series:
    """
    判断是否超买

    Args:
        rsi: RSI 序列
        threshold: 超买阈值 (默认 70)

    Returns:
        超买信号序列
    """
    return (rsi > threshold).astype(int)


def is_oversold(rsi: pd.Series, threshold: float = 30.0) -> pd.Series:
    """
    判断是否超卖

    Args:
        rsi: RSI 序列
        threshold: 超卖阈值 (默认 30)

    Returns:
        超卖信号序列
    """
    return (rsi < threshold).astype(int)
