#!/usr/bin/env python3
"""
Web UI 模块导入测试脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试模块导入"""
    
    print("=" * 60)
    print("OpenFinAgent Web UI - 模块导入测试")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # 测试 1: 导入策略构建器
    print("\n[测试 1] 导入策略构建器...")
    try:
        from src.strategy.builder import StrategyBuilder
        print("✅ 策略构建器导入成功")
        tests_passed += 1
        
        # 测试创建策略
        print("  - 创建均线交叉策略...")
        strategy = StrategyBuilder.create('ma_cross', short_window=5, long_window=20)
        print(f"    ✅ 策略名称：{strategy.name}")
        
        # 测试自然语言创建
        print("  - 从自然语言创建策略...")
        nl_strategy = StrategyBuilder.from_natural_language('当 5 日均线上穿 20 日均线时买入')
        print(f"    ✅ 策略名称：{nl_strategy.name}")
        
    except Exception as e:
        print(f"❌ 失败：{e}")
        tests_failed += 1
    
    # 测试 2: 导入回测引擎
    print("\n[测试 2] 导入回测引擎...")
    try:
        from src.backtest.engine import BacktestEngine, load_data
        print("✅ 回测引擎导入成功")
        tests_passed += 1
        
        # 测试加载模拟数据
        print("  - 测试加载模拟数据...")
        data = load_data('MOCK', '2023-01-01', '2023-12-31', source='mock')
        print(f"    ✅ 加载 {len(data)} 条数据")
        
    except Exception as e:
        print(f"❌ 失败：{e}")
        tests_failed += 1
    
    # 测试 3: 导入可视化工具
    print("\n[测试 3] 导入可视化工具...")
    try:
        from src.visualization.plotter import StrategyPlotter
        print("✅ 可视化工具导入成功")
        tests_passed += 1
        
    except Exception as e:
        print(f"❌ 失败：{e}")
        tests_failed += 1
    
    # 测试 4: 导入所有策略类型
    print("\n[测试 4] 测试所有策略类型...")
    try:
        strategies_config = [
            ('ma_cross', {'short_window': 5, 'long_window': 20}),
            ('momentum', {'lookback_period': 20, 'threshold': 0.05}),
            ('rsi', {'rsi_period': 14, 'oversold_threshold': 30, 'overbought_threshold': 70}),
            ('macd', {'fast_period': 12, 'slow_period': 26, 'signal_period': 9}),
            ('bollinger', {'window': 20, 'num_std': 2.0}),
            ('dual_ma_volume', {'short_window': 5, 'long_window': 20, 'volume_window': 20, 'volume_multiplier': 1.5})
        ]
        
        for strategy_type, params in strategies_config:
            strategy = StrategyBuilder.create(strategy_type, **params)
            print(f"  ✅ {strategy_type}: {strategy.name}")
        
        tests_passed += 1
        
    except Exception as e:
        print(f"❌ 失败：{e}")
        tests_failed += 1
    
    # 测试 5: 简单回测
    print("\n[测试 5] 运行简单回测...")
    try:
        strategy = StrategyBuilder.create('ma_cross', short_window=5, long_window=20, initial_capital=100000)
        engine = BacktestEngine(commission_rate=0.0003, slippage=0.001)
        data = load_data('MOCK', '2023-01-01', '2023-06-30', source='mock')
        results = engine.run(strategy, data, show_progress=False)
        
        print(f"  ✅ 回测完成")
        print(f"    - 初始资金：¥{results.initial_capital:,.2f}")
        print(f"    - 最终权益：¥{results.equity_curve[-1]['equity']:,.2f}")
        print(f"    - 交易次数：{len(results.trades)}")
        
        if results.metrics:
            print(f"    - 总收益：{results.metrics.get('总收益 (%)', 0):.2f}%")
            print(f"    - 夏普比率：{results.metrics.get('夏普比率', 0):.2f}")
        
        tests_passed += 1
        
    except Exception as e:
        print(f"❌ 失败：{e}")
        tests_failed += 1
    
    # 总结
    print("\n" + "=" * 60)
    print(f"测试结果：{tests_passed} 通过，{tests_failed} 失败")
    print("=" * 60)
    
    if tests_failed == 0:
        print("\n🎉 所有测试通过！Web UI 已准备就绪。")
        print("\n下一步：")
        print("1. 安装依赖：pip install -r requirements.txt")
        print("2. 运行应用：streamlit run app.py")
        print("3. 访问界面：http://localhost:8501")
        return True
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息。")
        return False


if __name__ == '__main__':
    success = test_imports()
    sys.exit(0 if success else 1)
