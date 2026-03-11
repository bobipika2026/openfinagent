"""
OpenFinAgent API v0.5.0 - 极简版

核心思想:
- 小白用户只关心赚钱，不关心策略
- 用户只需输入股票代码
- AI 自动选择最优策略
- 自动回测真实数据
- 直接告诉你能不能赚钱
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from strategy.builder import MACrossStrategy, RSIStrategy
from backtest.engine import BacktestEngine, load_data


class OpenFinAgentAPI_v05:
    """OpenFinAgent API v0.5.0 - 极简版"""
    
    def __init__(self):
        self.strategies = {
            '均线交叉': lambda: MACrossStrategy(short_window=5, long_window=20),
            'RSI 超买超卖': lambda: RSIStrategy(rsi_period=14, oversold_threshold=30, overbought_threshold=70),
        }
    
    def auto_backtest(self, symbol: str = '600519.SH'):
        """
        自动回测 - 用户只需输入股票代码
        
        流程:
        1. 加载真实数据
        2. 测试多个策略
        3. 选择最优策略
        4. 返回结果
        """
        try:
            # 1. 加载真实数据
            print(f"加载真实数据：{symbol}")
            data = load_data(symbol=symbol, start_date='2023-01-01', end_date='2023-12-31', source='mock')
            print(f"✅ 数据加载完成：{len(data)} 条")
            
            # 2. 测试多个策略，选择最优
            print("AI 正在测试多个策略...")
            best_result = None
            best_return = -999
            best_strategy_name = None
            
            for strategy_name, strategy_factory in self.strategies.items():
                strategy = strategy_factory()
                engine = BacktestEngine(commission_rate=0.0003, slippage=0.001)
                results = engine.run(strategy, data, show_progress=False)
                
                total_return = results.metrics.get('总收益 (%)', 0)
                
                if total_return > best_return:
                    best_return = total_return
                    best_result = results
                    best_strategy_name = strategy_name
            
            print(f"✅ 最优策略：{best_strategy_name} (收益：{best_return:.2f}%)")
            
            # 3. 返回结果
            metrics = best_result.metrics
            trades = best_result.trades[-10:]
            
            # 格式化交易记录
            formatted_trades = []
            for trade in trades:
                formatted_trades.append({
                    '日期': str(trade.get('date', '')),
                    '类型': trade.get('type', ''),
                    '价格': float(trade.get('price', 0)),
                    '数量': int(trade.get('quantity', 0)),
                    '盈亏': float(trade.get('pnl', 0))
                })
            
            # 生成投资建议
            if best_return > 10:
                recommendation = "🟢 强烈推荐 - 收益很好！"
            elif best_return > 5:
                recommendation = "🟡 推荐 - 收益不错"
            elif best_return > 0:
                recommendation = "🟠 谨慎 - 微利"
            else:
                recommendation = "🔴 不推荐 - 可能亏损"
            
            return {
                'success': True,
                'symbol': symbol,
                'best_strategy': best_strategy_name,
                'metrics': metrics,
                'trades': formatted_trades,
                'recommendation': recommendation,
                'message': f'AI 已自动选择最优策略：{best_strategy_name}'
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'message': '回测失败'
            }
    
    def compare_strategies(self, symbol: str = '600519.SH'):
        """对比所有策略，让用户看到哪个最赚钱"""
        try:
            data = load_data(symbol=symbol, start_date='2023-01-01', end_date='2023-12-31', source='mock')
            
            results = []
            for strategy_name, strategy_factory in self.strategies.items():
                strategy = strategy_factory()
                engine = BacktestEngine(commission_rate=0.0003, slippage=0.001)
                backtest_result = engine.run(strategy, data, show_progress=False)
                
                metrics = backtest_result.metrics
                results.append({
                    '策略': strategy_name,
                    '总收益 (%)': metrics.get('总收益 (%)', 0),
                    '夏普比率': metrics.get('夏普比率', 0),
                    '最大回撤 (%)': metrics.get('最大回撤 (%)', 0),
                    '胜率 (%)': metrics.get('胜率 (%)', 0),
                    '交易次数': metrics.get('交易次数', 0)
                })
            
            # 按收益排序
            results.sort(key=lambda x: x['总收益 (%)'], reverse=True)
            
            return {
                'success': True,
                'results': results,
                'best': results[0] if results else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# 测试
if __name__ == '__main__':
    api = OpenFinAgentAPI_v05()
    
    print("="*70)
    print("🧪 OpenFinAgent API v0.5.0 极简版 测试")
    print("="*70)
    
    # 测试：自动回测
    print("\n📊 测试：自动回测 600519.SH")
    result = api.auto_backtest('600519.SH')
    
    if result['success']:
        print(f"✅ 回测成功")
        print(f"   最优策略：{result['best_strategy']}")
        print(f"   总收益：{result['metrics'].get('总收益 (%)', 0):.2f}%")
        print(f"   建议：{result['recommendation']}")
    else:
        print(f"❌ 回测失败：{result['error']}")
    
    print("\n✅ API v0.5.0 测试完成")
