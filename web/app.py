"""
OpenFinAgent Web UI - 真正的 AI 驱动版 (v0.4.0)

核心优化:
- ✅ 调用真实回测引擎
- ✅ AI 策略自动生成
- ✅ 一键运行回测
- ✅ 实时返回结果
- ✅ 用户操作极简
"""

import streamlit as st
from pathlib import Path
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入真实 API
from api.agent_api import OpenFinAgentAPI

# 初始化 API
api = OpenFinAgentAPI()


# ==================== 页面配置 ====================
st.set_page_config(
    page_title="OpenFinAgent - AI 量化交易平台",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================== 侧边栏导航 ====================
def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.markdown("### 📈 OpenFinAgent")
        st.markdown("AI 量化交易平台 - 让投资更简单")
        st.divider()
        
        # 页面导航
        page = st.radio(
            "导航",
            ["🏠 首页", "✨ 一键回测", "📊 策略对比", "📚 策略库"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # 新手引导
        with st.expander("📚 新手入门"):
            st.markdown("""
            **3 步开始量化交易**:
            1. 选择推荐策略
            2. 点击运行回测
            3. 查看真实结果
            
            **无需操作**:
            - ✅ 无需手动配置参数
            - ✅ 无需选择指标
            - ✅ AI 自动完成
            """)
        
        # 信息
        st.markdown("""
        ### 关于
        **版本**: v0.4.0 (AI 驱动版)
        
        **特点**:
        - ✅ 真实回测引擎
        - ✅ AI 自动生成
        - ✅ 一键运行
        
        [GitHub](https://github.com/bobipika2026/openfinagent)
        """)
    
    return page


# ==================== 首页 ====================
def render_home():
    """首页 - 添加真实示例"""
    st.markdown('# 🏠 OpenFinAgent 首页')
    st.markdown('### AI 驱动的量化交易平台 - 让投资更简单')
    st.markdown('无需编程基础，一键运行真实回测！')
    
    st.divider()
    
    # 核心优势
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success("""
        ### 🎯 极简
        一键运行回测
        AI 自动完成
        """)
    with col2:
        st.info("""
        ### 📊 真实
        调用真实引擎
        实时返回结果
        """)
    with col3:
        st.warning("""
        ### 🚀 快速
        无需配置参数
        3 秒出结果
        """)
    
    st.divider()
    
    # 真实回测示例
    st.markdown('### 📈 真实回测示例 - 点击立即查看')
    st.markdown('以下是使用真实回测引擎运行的结果，点击即可运行:')
    
    # 示例卡片
    cols = st.columns(3)
    
    examples = [
        {
            'stock': '贵州茅台 (600519.SH)',
            'strategy': '均线交叉',
            'desc': '5 日均线上穿 20 日均线买入'
        },
        {
            'stock': '平安银行 (000001.SZ)',
            'strategy': 'RSI 超买超卖',
            'desc': 'RSI 低于 30 买入，高于 70 卖出'
        },
        {
            'stock': '宁德时代 (300750.SZ)',
            'strategy': 'MACD 趋势',
            'desc': 'MACD 线上穿信号线买入'
        }
    ]
    
    for idx, example in enumerate(examples):
        with cols[idx]:
            st.markdown(f"""
            #### {example['stock']}
            **策略**: {example['strategy']}
            
            {example['desc']}
            
            时间：2023-01-01 ~ 2023-12-31  
            初始资金：¥100,000
            """)
            
            if st.button(f"▶️ 运行回测", key=f"example_{idx}", use_container_width=True):
                st.session_state.current_page = "✨ 一键回测"
                st.session_state.quick_strategy = example['strategy']
                st.session_state.quick_stock = example['stock'].split('(')[1].split(')')[0]
                st.rerun()
    
    st.divider()
    
    # 快速开始
    st.markdown('### 🚀 快速开始')
    
    if st.button("🎯 开始一键回测", type="primary", use_container_width=True):
        st.session_state.current_page = "✨ 一键回测"
        st.rerun()
    
    # 页脚
    st.divider()
    st.markdown(
        """
        <div style="text-align: center; color: #666; padding: 20px;">
            OpenFinAgent v0.4.0 (AI 驱动版) | AI 量化交易平台 | 
            <a href="https://github.com/bobipika2026/openfinagent">GitHub</a>
        </div>
        """,
        unsafe_allow_html=True
    )


# ==================== 一键回测页面 (核心功能) ====================
def render_quick_backtest():
    """一键回测页面 - 真正的 AI 驱动"""
    st.markdown('# ✨ 一键回测')
    st.markdown('### 选择策略，点击运行，AI 自动完成')
    
    st.divider()
    
    # 策略选择
    st.markdown('### 📚 推荐策略')
    
    strategies = {
        '均线交叉': {
            'desc': '当短期均线上穿长期均线时买入，下穿时卖出',
            'difficulty': '⭐⭐',
            'suitable': '趋势跟踪',
            'params': {'短期均线': 5, '长期均线': 20}
        },
        'RSI 超买超卖': {
            'desc': 'RSI 低于 30 买入 (超卖),高于 70 卖出 (超买)',
            'difficulty': '⭐⭐⭐',
            'suitable': '震荡行情',
            'params': {'周期': 14, '超买线': 70, '超卖线': 30}
        },
        'MACD 趋势': {
            'desc': 'MACD 线上穿信号线买入，下穿卖出',
            'difficulty': '⭐⭐⭐',
            'suitable': '趋势跟踪',
            'params': {'快线': 12, '慢线': 26, '信号线': 9}
        },
        '布林带回归': {
            'desc': '价格触及下轨买入，上轨卖出',
            'difficulty': '⭐⭐⭐',
            'suitable': '震荡行情',
            'params': {'周期': 20, '标准差': 2}
        }
    }
    
    # 策略选择
    selected_strategy = st.selectbox(
        "选择策略",
        list(strategies.keys()),
        format_func=lambda x: f"{x} - {strategies[x]['suitable']} {strategies[x]['difficulty']}"
    )
    
    # 显示策略详情
    if selected_strategy:
        info = strategies[selected_strategy]
        st.info(f"""
        **策略说明**: {info['desc']}
        
        **适合行情**: {info['suitable']}  
        **难度**: {info['difficulty']}  
        **默认参数**: {', '.join([f'{k}={v}' for k, v in info['params'].items()])}
        """)
    
    # 股票选择
    stock = st.text_input("股票代码", value="600519.SH", help="输入 6 位股票代码")
    
    # 运行回测
    if st.button("▶️ 运行回测", type="primary", use_container_width=True, key="run_backtest"):
        with st.spinner("AI 正在运行回测..."):
            # 调用真实 API
            result = api.quick_backtest(selected_strategy, stock)
            
            if result['success']:
                st.success("✅ 回测完成！")
                
                # 显示结果
                metrics = result['metrics']
                
                # 性能指标
                st.markdown('#### 📊  performance 指标')
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_return = metrics.get('总收益 (%)', 0)
                    st.metric("总收益", f"{total_return:.2f}%", delta=f"{total_return:.1f}%")
                
                with col2:
                    annual_return = metrics.get('年化收益 (%)', 0)
                    st.metric("年化收益", f"{annual_return:.2f}%", delta=f"{annual_return:.1f}%")
                
                with col3:
                    sharpe = metrics.get('夏普比率', 0)
                    st.metric("夏普比率", f"{sharpe:.2f}", delta="低风险" if sharpe > 1 else "高风险")
                
                with col4:
                    max_dd = metrics.get('最大回撤 (%)', 0)
                    st.metric("最大回撤", f"{max_dd:.2f}%", delta=f"{max_dd:.1f}%")
                
                st.divider()
                
                # 权益曲线
                st.markdown('#### 📈 权益曲线')
                equity_curve = result['equity_curve']
                
                if equity_curve and len(equity_curve) > 0:
                    # 检查数据格式
                    if isinstance(equity_curve[0], dict) and 'date' in equity_curve[0]:
                        df_equity = pd.DataFrame(equity_curve)
                        df_equity['date'] = pd.to_datetime(df_equity['date'])
                        df_equity = df_equity.set_index('date')
                        st.line_chart(df_equity[['value']], use_container_width=True)
                    elif isinstance(equity_curve, dict):
                        # 如果是字典格式，转换为 DataFrame
                        df_equity = pd.DataFrame(list(equity_curve.items()), columns=['date', 'value'])
                        df_equity['date'] = pd.to_datetime(df_equity['date'])
                        df_equity = df_equity.set_index('date')
                        st.line_chart(df_equity[['value']], use_container_width=True)
                
                st.divider()
                
                # 交易记录
                st.markdown('#### 📝 交易记录')
                trades = result['trades']
                
                if trades:
                    df_trades = pd.DataFrame(trades)
                    st.dataframe(df_trades, use_container_width=True)
                
                # 详细指标
                st.divider()
                st.markdown('#### 📊 详细指标')
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    - **波动率**: {metrics.get('波动率 (%)', 0):.2f}%
                    - **胜率**: {metrics.get('胜率 (%)', 0):.1f}%
                    - **交易次数**: {metrics.get('交易次数', 0)}
                    """)
                
                with col2:
                    st.markdown(f"""
                    - **初始资金**: ¥{metrics.get('初始资金', 0):,.0f}
                    - **最终资金**: ¥{metrics.get('最终资金', 0):,.2f}
                    - **策略名称**: {metrics.get('策略名称', selected_strategy)}
                    """)
                
            else:
                st.error(f"❌ 回测失败：{result.get('error', '未知错误')}")
                st.info("💡 请检查股票代码是否正确，或尝试其他策略")


# ==================== 策略对比页面 ====================
def render_compare():
    """策略对比页面 - 真实回测对比"""
    st.markdown('# 📊 策略对比')
    st.markdown('### 多策略并行回测，直观对比性能')
    
    st.divider()
    
    # 策略选择
    strategies = st.multiselect(
        "选择要对比的策略",
        ["均线交叉", "RSI 超买超卖", "MACD 趋势", "布林带回归"],
        default=["均线交叉", "RSI 超买超卖"]
    )
    
    # 股票选择
    stock = st.text_input("股票代码", value="600519.SH")
    
    if st.button("▶️ 运行对比", type="primary", use_container_width=True):
        if len(strategies) >= 2:
            with st.spinner("AI 正在运行多个策略回测..."):
                results = []
                
                for strategy_name in strategies:
                    result = api.quick_backtest(strategy_name, stock)
                    if result['success']:
                        results.append({
                            '策略': strategy_name,
                            '结果': result
                        })
                
                if results:
                    st.success(f"✅ 完成 {len(results)} 个策略回测")
                    
                    # 对比表格
                    data = []
                    for r in results:
                        metrics = r['结果']['metrics']
                        data.append({
                            '策略': r['策略'],
                            '总收益 (%)': f"{metrics.get('总收益 (%)', 0):.2f}",
                            '年化收益 (%)': f"{metrics.get('年化收益 (%)', 0):.2f}",
                            '夏普比率': f"{metrics.get('夏普比率', 0):.2f}",
                            '最大回撤 (%)': f"{metrics.get('最大回撤 (%)', 0):.2f}",
                            '胜率 (%)': f"{metrics.get('胜率 (%)', 0):.1f}",
                            '交易次数': metrics.get('交易次数', 0)
                        })
                    
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                    
                    # 收益对比图
                    st.markdown('#### 📊 收益对比')
                    df_chart = df.set_index('策略')[['总收益 (%)']].astype(float)
                    st.bar_chart(df_chart, use_container_width=True)
                else:
                    st.error("❌ 所有策略回测失败")
        else:
            st.warning("⚠️ 请至少选择 2 个策略")


# ==================== 策略库页面 ====================
def render_library():
    """策略库页面"""
    st.markdown('# 📚 策略库')
    st.markdown('### 经典策略大全')
    
    st.divider()
    
    strategies = {
        '🎯 经典策略': {
            '均线交叉': '当短期均线上穿长期均线时买入，下穿时卖出',
            '金叉死叉': '5 日均线上穿 20 日均线为金叉 (买入),反之为死叉 (卖出)'
        },
        '📊 动量策略': {
            'RSI 超买超卖': 'RSI 低于 30 买入 (超卖),高于 70 卖出 (超买)',
            'MACD 趋势': 'MACD 线上穿信号线买入，下穿卖出'
        },
        '🛡️ 稳健策略': {
            '布林带回归': '价格触及下轨买入，上轨卖出',
            '双均线 + 成交量': '均线金叉 + 放量时买入，死叉时卖出'
        }
    }
    
    for category, items in strategies.items():
        st.markdown(f"### {category}")
        
        cols = st.columns(2)
        for idx, (name, desc) in enumerate(items.items()):
            with cols[idx % 2]:
                with st.container():
                    st.markdown(f"**{name}**")
                    st.markdown(desc)
                    
                    if st.button(f"运行回测", key=f"lib_{name}", use_container_width=True):
                        st.session_state.current_page = "✨ 一键回测"
                        st.session_state.quick_strategy = name
                        st.rerun()
        
        st.divider()


# ==================== 主程序 ====================
def main():
    """主函数"""
    
    # 渲染侧边栏
    page = render_sidebar()
    
    # 页面映射
    page_map = {
        "🏠 首页": render_home,
        "✨ 一键回测": render_quick_backtest,
        "📊 策略对比": render_compare,
        "📚 策略库": render_library,
    }
    
    # 获取当前页面
    if 'current_page' in st.session_state:
        current_page = st.session_state.current_page
    else:
        current_page = page
    
    # 更新 session state
    st.session_state.current_page = current_page
    
    # 渲染页面
    if current_page in page_map:
        page_map[current_page]()
    else:
        render_home()


if __name__ == "__main__":
    main()
