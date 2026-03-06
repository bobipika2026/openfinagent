"""
实时监控页面 - 实时数据展示和监控
"""

import streamlit as st
from pathlib import Path
import sys
from datetime import datetime, timedelta
import random

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入自定义组件
from components import render_header, create_equity_chart, create_kline_chart


def show():
    """显示实时监控页面"""
    
    # 页面头部
    render_header("📊 实时监控", "实时市场数据和策略表现监控")
    
    st.divider()
    
    # 自动刷新控制
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 🔄 刷新设置")
        auto_refresh = st.checkbox("自动刷新 (每 30 秒)", value=False, key="auto_refresh")
    
    with col2:
        if st.button("🔄 立即刷新", use_container_width=True, key="manual_refresh"):
            st.rerun()
    
    # 显示最后更新时间
    last_update = datetime.now()
    st.markdown(f"*最后更新：{last_update.strftime('%Y-%m-%d %H:%M:%S')}*")
    
    st.divider()
    
    # 实时市场数据
    st.markdown("### 🌍 全球市场概览")
    
    # 模拟实时数据
    market_data = get_mock_market_data()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        delta = market_data["上证指数"]["change"]
        color = "🟢" if delta >= 0 else "🔴"
        st.metric(
            label=f"{color} 上证指数",
            value=market_data["上证指数"]["price"],
            delta=f"{market_data['上证指数']['change']:+.2f}%"
        )
    
    with col2:
        delta = market_data["深证成指"]["change"]
        color = "🟢" if delta >= 0 else "🔴"
        st.metric(
            label=f"{color} 深证成指",
            value=market_data["深证成指"]["price"],
            delta=f"{market_data['深证成指']['change']:+.2f}%"
        )
    
    with col3:
        delta = market_data["创业板指"]["change"]
        color = "🟢" if delta >= 0 else "🔴"
        st.metric(
            label=f"{color} 创业板指",
            value=market_data["创业板指"]["price"],
            delta=f"{market_data['创业板指']['change']:+.2f}%"
        )
    
    with col4:
        st.metric(
            label="💰 涨跌家数比",
            value="1823 / 2156",
            delta="-333"
        )
    
    with col5:
        st.metric(
            label="📊 成交量 (亿)",
            value="8,234",
            delta="+5.2%"
        )
    
    st.divider()
    
    # 实时 K 线图
    st.markdown("### 📈 实时 K 线")
    
    stock_symbol = st.text_input("股票代码", value="000001", placeholder="输入 6 位股票代码")
    
    if st.button("加载 K 线", key="load_kline"):
        kline_data = get_mock_kline_data(stock_symbol)
        fig = create_kline_chart(kline_data, title=f"{stock_symbol} K 线图", height=500)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # 策略实时监控
    st.markdown("### 🤖 策略运行监控")
    
    # 模拟策略状态
    strategies_status = [
        {"name": "均线交叉 -000001", "status": "running", "position": "持仓", "pnl": "+2.34%", "signal": "持有"},
        {"name": "RSI 策略 -600519", "status": "running", "position": "空仓", "pnl": "+1.12%", "signal": "观望"},
        {"name": "MACD 策略 -000858", "status": "paused", "position": "持仓", "pnl": "-0.56%", "signal": "持有"},
        {"name": "动量策略 -300750", "status": "running", "position": "持仓", "pnl": "+5.67%", "signal": "加仓"},
    ]
    
    # 策略状态表格
    for strategy in strategies_status:
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])
        
        with col1:
            status_icon = "🟢" if strategy["status"] == "running" else "🟡"
            st.markdown(f"{status_icon} **{strategy['name']}**")
        
        with col2:
            position_icon = "📈" if strategy["position"] == "持仓" else "💰"
            st.markdown(f"{position_icon} {strategy['position']}")
        
        with col3:
            pnl_color = "🟢" if float(strategy["pnl"].replace("%", "")) >= 0 else "🔴"
            st.markdown(f"{pnl_color} {strategy['pnl']}")
        
        with col4:
            st.markdown(f"📊 {strategy['signal']}")
        
        with col5:
            if st.button("管理", key=f"manage_{strategy['name']}"):
                st.info("策略管理功能开发中...")
        
        st.divider()
    
    st.divider()
    
    # 实时信号
    st.markdown("### 📡 实时交易信号")
    
    signals = [
        {"time": "14:32:15", "stock": "000001", "strategy": "均线交叉", "signal": "买入", "price": "12.34", "volume": "1000"},
        {"time": "14:28:43", "stock": "600519", "strategy": "RSI 策略", "signal": "卖出", "price": "1856.00", "volume": "500"},
        {"time": "14:15:22", "stock": "000858", "strategy": "MACD 策略", "signal": "买入", "price": "15.67", "volume": "800"},
        {"time": "13:58:09", "stock": "300750", "strategy": "动量策略", "signal": "加仓", "price": "234.56", "volume": "300"},
    ]
    
    # 信号表格
    for signal in signals:
        signal_icon = "🟢" if signal["signal"] in ["买入", "加仓"] else "🔴"
        
        col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 3, 2, 2, 2])
        
        with col1:
            st.markdown(f"⏰ {signal['time']}")
        
        with col2:
            st.markdown(f"📈 {signal['stock']}")
        
        with col3:
            st.markdown(f"🤖 {signal['strategy']}")
        
        with col4:
            st.markdown(f"{signal_icon} {signal['signal']}")
        
        with col5:
            st.markdown(f"💰 ¥{signal['price']}")
        
        with col6:
            st.markdown(f"📊 {signal['volume']}股")
        
        st.divider()
    
    st.divider()
    
    # 系统状态
    st.markdown("### 🖥️ 系统状态")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("数据源状态", "🟢 正常")
    
    with col2:
        st.metric("回测引擎", "🟢 正常")
    
    with col3:
        st.metric("API 响应", "45ms")
    
    with col4:
        st.metric("运行策略", "4")
    
    # 自动刷新逻辑
    if auto_refresh:
        import time
        time.sleep(30)
        st.rerun()


def get_mock_market_data():
    """获取模拟市场数据"""
    
    return {
        "上证指数": {
            "price": f"{3200 + random.uniform(-50, 50):.2f}",
            "change": random.uniform(-2, 2)
        },
        "深证成指": {
            "price": f"{10000 + random.uniform(-500, 500):.2f}",
            "change": random.uniform(-2, 2)
        },
        "创业板指": {
            "price": f"{2100 + random.uniform(-100, 100):.2f}",
            "change": random.uniform(-3, 3)
        }
    }


def get_mock_kline_data(symbol, days=60):
    """获取模拟 K 线数据"""
    
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # 生成模拟 OHLC 数据
    base_price = 100 + random.uniform(-20, 20)
    
    data = []
    for i in range(days):
        open_price = base_price * (1 + random.uniform(-0.02, 0.02))
        close_price = open_price * (1 + random.uniform(-0.03, 0.03))
        high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.02))
        low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.02))
        
        data.append({
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': int(random.uniform(1000000, 10000000))
        })
        
        base_price = close_price
    
    df = pd.DataFrame(data, index=dates)
    return df


def get_mock_strategy_performance():
    """获取模拟策略表现数据"""
    
    import pandas as pd
    
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    
    # 生成模拟权益曲线
    equity = [100000]
    for i in range(29):
        change = random.uniform(-0.03, 0.04)
        equity.append(equity[-1] * (1 + change))
    
    df = pd.DataFrame({
        'timestamp': dates,
        'equity': equity
    })
    df.set_index('timestamp', inplace=True)
    
    return df
