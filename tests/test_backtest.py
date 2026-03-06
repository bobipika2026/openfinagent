#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回测模块测试
"""

import sys
sys.path.insert(0, '../src')

import pandas as pd
import numpy as np
from openfinagent.backtest.results import BacktestResults


def test_backtest_results():
    """测试回测结果类"""
    results = BacktestResults('测试策略', 100000)

    # 添加权益点
    from datetime import datetime
    results.add_equity_point(datetime(2023, 1, 1), 100000)
    results.add_equity_point(datetime(2023, 1, 2), 102000)
    results.add_equity_point(datetime(2023, 1, 3), 98000)

    # 添加交易
    results.add_trade({
        'timestamp': datetime(2023, 1, 2),
        'type': 'buy',
        'price': 100,
        'shares': 100,
        'cost': 10000
    })

    # 生成价格数据
    prices = pd.Series([100, 102, 98])

    # 计算指标
    results.calculate_metrics(prices)

    # 验证指标
    assert '总收益 (%)' in results.metrics
    assert '夏普比率' in results.metrics
    assert '最大回撤 (%)' in results.metrics

    print("✅ 回测结果测试通过")

    # 显示结果
    results.show()

    # 转换为字典
    data = results.to_dict()
    assert 'strategy_name' in data
    assert 'metrics' in data

    print("✅ 所有测试通过")


if __name__ == '__main__':
    test_backtest_results()
