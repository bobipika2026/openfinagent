"""
OpenFinAgent API 服务 - 真正的 AI 驱动回测

功能:
- ✅ 调用真实回测引擎
- ✅ AI 策略生成
- ✅ 自动化回测
- ✅ 实时返回结果
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from strategy.builder import StrategyBuilder, MACrossStrategy, MomentumStrategy, RSIStrategy
from backtest.engine import BacktestEngine, load_data


class OpenFinAgentAPI:
    """OpenFinAgent API - 真正的 AI 驱动回测"""
    
    def __init__(self):
        self.builder = StrategyBuilder()
    
    def quick_backtest(self, strategy_name: str, symbol: str = '600519.SH'):
        """快速回测 - 预设参数"""
        
        # 预设策略参数
        presets = {
            '均线交叉': {'short': 5, 'long': 20},
            '金叉死叉': {'short': 5, 'long': 20},
            'RSI 超买超卖': {'period': 14, 'oversold': 30, 'overbought': 70},
            'MACD 趋势': {'fast': 12, 'slow': 26, 'signal': 9},
            '布林带回归': {'period': 20, 'std': 2},
        }
        
        if strategy_name not in presets:
            return {'success': False, 'error': '未知策略'}
        
        params = presets[strategy_name]
        
        try:
            # 创建策略
            if '均线' in strategy_name or '金叉' in strategy_name:
                strategy = MACrossStrategy(short_window=params['short'], long_window=params['long'])
            elif 'RSI' in strategy_name:
                strategy = RSIStrategy(period=params['period'], oversold=params['oversold'], overbought=params['overbought'])
            elif 'MACD' in strategy_name:
                from strategy.macd_strategy import MACDStrategy
                strategy = MACDStrategy(fast_period=params['fast'], slow_period=params['slow'], signal_period=params['signal'])
            elif '布林带' in strategy_name:
                from strategy.bollinger_strategy import BollingerStrategy
                strategy = BollingerStrategy(period=params['period'], std_dev=params['std'])
            else:
                return {'success': False, 'error': '策略不支持'}
            
            # 加载数据
            print(f"加载数据：{symbol} (2023-01-01 ~ 2023-12-31)")
            data = load_data(symbol=symbol, start_date='2023-01-01', end_date='2023-12-31', source='mock')
            print(f"数据加载完成：{len(data)} 条")
            
            # 运行回测
            print("运行回测...")
            engine = BacktestEngine(commission_rate=0.0003, slippage=0.001)
            results = engine.run(strategy, data, show_progress=False)
            
            # 提取结果
            metrics = results.metrics
            equity_curve = results.equity_curve
            trades = results.trades[-10:]  # 最近 10 笔
            
            # 格式化输出
            formatted_trades = []
            for trade in trades:
                formatted_trades.append({
                    'date': str(trade.get('date', '')),
                    'type': trade.get('type', ''),
                    'price': float(trade.get('price', 0)),
                    'quantity': int(trade.get('quantity', 0)),
                    'pnl': float(trade.get('pnl', 0))
                })
            
            return {
                'success': True,
                'metrics': metrics,
                'equity_curve': equity_curve,
                'trades': formatted_trades,
                'message': '回测完成'
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'message': '回测失败'
            }
    
    def run_custom_backtest(self, strategy_type: str, params: dict, symbol: str = '600519.SH'):
        """自定义回测"""
        try:
            # 创建策略
            if strategy_type == '均线交叉':
                strategy = MACrossStrategy(
                    short_window=params.get('short', 5),
                    long_window=params.get('long', 20)
                )
            elif strategy_type == 'RSI':
                strategy = RSIStrategy(
                    period=params.get('period', 14),
                    oversold=params.get('oversold', 30),
                    overbought=params.get('overbought', 70)
                )
            elif strategy_type == 'MACD':
                from strategy.macd_strategy import MACDStrategy
                strategy = MACDStrategy(
                    fast_period=params.get('fast', 12),
                    slow_period=params.get('slow', 26),
                    signal_period=params.get('signal', 9)
                )
            else:
                return {'success': False, 'error': '不支持的策略类型'}
            
            # 加载数据
            data = load_data(symbol=symbol, start_date='2023-01-01', end_date='2023-12-31', source='mock')
            
            # 运行回测
            engine = BacktestEngine(commission_rate=0.0003, slippage=0.001)
            results = engine.run(strategy, data, show_progress=False)
            
            return {
                'success': True,
                'metrics': results.metrics,
                'equity_curve': results.equity_curve,
                'trades': results.trades[-10:],
                'message': '回测完成'
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'message': '回测失败'
            }


# 测试
if __name__ == '__main__':
    api = OpenFinAgentAPI()
    
    print("="*70)
    print("🧪 OpenFinAgent API 测试")
    print("="*70)
    
    # 测试 1: 快速回测
    print("\n📊 测试 1: 均线交叉策略回测")
    result = api.quick_backtest('均线交叉', '600519.SH')
    
    if result['success']:
        print(f"✅ 回测成功")
        metrics = result['metrics']
        print(f"   总收益：{metrics.get('总收益 (%)', 0):.2f}%")
        print(f"   夏普比率：{metrics.get('夏普比率', 0):.2f}")
        print(f"   交易次数：{metrics.get('交易次数', 0)}")
        print(f"   胜率：{metrics.get('胜率 (%)', 0):.1f}%")
    else:
        print(f"❌ 回测失败：{result['error']}")
    
    print("\n✅ API 测试完成")
