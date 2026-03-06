"""
策略模板库页面 - 提供预设策略模板
"""

import streamlit as st
from pathlib import Path
import sys

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入自定义组件
from components import render_header, render_strategy_card


def show():
    """显示策略模板库页面"""
    
    # 页面头部
    render_header("📚 策略模板库", "精选经典量化策略模板")
    
    st.divider()
    
    # 策略分类筛选
    st.markdown("### 🔍 筛选策略")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category = st.selectbox(
            "策略类型",
            ["全部", "趋势跟踪", "均值回归", "动量策略", "复合策略"],
            key="template_category"
        )
    
    with col2:
        difficulty = st.selectbox(
            "难度等级",
            ["全部", "⭐ 入门", "⭐⭐ 初级", "⭐⭐⭐ 中级", "⭐⭐⭐⭐ 高级"],
            key="template_difficulty"
        )
    
    with col3:
        search = st.text_input(
            "搜索策略",
            placeholder="输入策略名称...",
            key="template_search"
        )
    
    st.divider()
    
    # 策略模板列表
    templates = get_strategy_templates()
    
    # 筛选逻辑
    filtered_templates = filter_templates(templates, category, difficulty, search)
    
    # 显示策略卡片
    st.markdown(f"### 📊 共 {len(filtered_templates)} 个策略模板")
    
    # 分组显示
    for template in filtered_templates:
        render_strategy_card(
            name=template["name"],
            description=template["description"],
            params=template["params"],
            on_select=on_strategy_selected
        )
    
    st.divider()
    
    # 策略对比功能
    st.markdown("### ⚖️ 策略对比")
    
    st.info("""
    💡 **提示**: 选择多个策略模板进行对比，找到最适合你的策略
    
    1. 点击上方策略卡片的「选择此策略」按钮
    2. 至少选择 2 个策略
    3. 切换到「策略对比」页面查看对比结果
    """)
    
    # 已选择的策略
    if 'selected_templates' not in st.session_state:
        st.session_state.selected_templates = []
    
    if st.session_state.selected_templates:
        st.markdown(f"**已选择 {len(st.session_state.selected_templates)} 个策略:**")
        for name in st.session_state.selected_templates:
            st.markdown(f"- ✅ {name}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ 清空选择", use_container_width=True):
                st.session_state.selected_templates = []
                st.rerun()
        with col2:
            if len(st.session_state.selected_templates) >= 2:
                if st.button("⚖️ 开始对比", use_container_width=True, type="primary"):
                    st.query_params["page"] = "compare"
                    st.rerun()
    
    st.divider()
    
    # 策略使用指南
    st.markdown("### 📖 策略使用指南")
    
    tab1, tab2, tab3 = st.tabs(["新手入门", "参数调优", "风险控制"])
    
    with tab1:
        st.markdown("""
        ### 🎯 新手入门
        
        **第一步：选择策略**
        - 从模板库中选择感兴趣的策略
        - 查看策略说明和参数
        - 点击「使用此模板」
        
        **第二步：了解策略**
        - 阅读策略逻辑说明
        - 理解买入/卖出条件
        - 了解适用场景
        
        **第三步：回测验证**
        - 选择股票和时间范围
        - 运行回测查看表现
        - 分析各项指标
        
        **💡 建议**: 新手建议从「均线交叉」或「RSI 策略」开始
        """)
    
    with tab2:
        st.markdown("""
        ### ⚙️ 参数调优
        
        **常见参数优化方法**:
        
        1. **网格搜索**
           - 遍历参数组合
           - 找到最优参数
           - 注意过拟合风险
        
        2. **逐步优化**
           - 每次调整一个参数
           - 观察效果变化
           - 记录最优组合
        
        3. **样本外验证**
           - 用部分数据优化
           - 用剩余数据验证
           - 确保策略稳健性
        
        **⚠️ 注意**: 避免过度优化导致过拟合
        """)
    
    with tab3:
        st.markdown("""
        ### 🛡️ 风险控制
        
        **风险管理要点**:
        
        1. **仓位控制**
           - 单笔交易不超过总资金的 10%
           - 总持仓不超过 80%
           - 设置止损位
        
        2. **分散投资**
           - 不要把所有资金投入单一策略
           - 多策略组合降低风险
           - 跨品种分散
        
        3. **回测验证**
           - 长周期回测 (至少 1 年)
           - 不同市场环境测试
           - 考虑手续费和滑点
        
        4. **实盘监控**
           - 定期回顾策略表现
           - 及时止损
           - 根据市场调整
        
        **⚠️ 重要**: 回测结果不代表未来收益
        """)


def get_strategy_templates():
    """获取策略模板列表"""
    
    return [
        {
            "name": "均线交叉策略",
            "category": "趋势跟踪",
            "difficulty": "⭐⭐",
            "description": "经典的趋势跟踪策略，当短期均线上穿长期均线时买入，下穿时卖出",
            "params": {
                "短期均线": "5 日",
                "长期均线": "20 日",
                "初始资金": "10 万元"
            },
            "returns_avg": "8-15%",
            "max_drawdown": "-15%",
            "suitable_for": "趋势明显的市场环境"
        },
        {
            "name": "RSI 超买超卖策略",
            "category": "均值回归",
            "difficulty": "⭐⭐",
            "description": "基于 RSI 指标的均值回归策略，超卖时买入，超买时卖出",
            "params": {
                "RSI 周期": "14 日",
                "超卖线": "30",
                "超买线": "70"
            },
            "returns_avg": "6-12%",
            "max_drawdown": "-12%",
            "suitable_for": "震荡市、均值回归"
        },
        {
            "name": "MACD 金叉死叉策略",
            "category": "趋势跟踪",
            "difficulty": "⭐⭐⭐",
            "description": "利用 MACD 指标的金叉死叉信号进行交易，捕捉趋势",
            "params": {
                "快线周期": "12",
                "慢线周期": "26",
                "信号线周期": "9"
            },
            "returns_avg": "10-18%",
            "max_drawdown": "-18%",
            "suitable_for": "中长期趋势跟踪"
        },
        {
            "name": "布林带策略",
            "category": "均值回归",
            "difficulty": "⭐⭐⭐",
            "description": "基于布林带上下轨的突破或反转策略",
            "params": {
                "周期": "20 日",
                "标准差倍数": "2.0"
            },
            "returns_avg": "7-14%",
            "max_drawdown": "-14%",
            "suitable_for": "震荡市、突破交易"
        },
        {
            "name": "动量策略",
            "category": "动量策略",
            "difficulty": "⭐⭐",
            "description": "追涨杀跌的动量策略，捕捉强势股的持续上涨",
            "params": {
                "回看周期": "20 日",
                "收益率阈值": "5%"
            },
            "returns_avg": "12-20%",
            "max_drawdown": "-20%",
            "suitable_for": "强势股跟踪"
        },
        {
            "name": "双均线 + 成交量策略",
            "category": "复合策略",
            "difficulty": "⭐⭐⭐⭐",
            "description": "结合均线和成交量的复合策略，提高信号可靠性",
            "params": {
                "短期均线": "5 日",
                "长期均线": "20 日",
                "成交量均线周期": "20 日",
                "成交量倍数": "1.5"
            },
            "returns_avg": "10-16%",
            "max_drawdown": "-13%",
            "suitable_for": "趋势 + 成交量确认"
        }
    ]


def filter_templates(templates, category, difficulty, search):
    """筛选策略模板"""
    
    filtered = templates
    
    # 按类别筛选
    if category != "全部":
        category_map = {
            "趋势跟踪": ["均线交叉策略", "MACD 金叉死叉策略"],
            "均值回归": ["RSI 超买超卖策略", "布林带策略"],
            "动量策略": ["动量策略"],
            "复合策略": ["双均线 + 成交量策略"]
        }
        filtered = [t for t in filtered if t["name"] in category_map.get(category, [])]
    
    # 按难度筛选
    if difficulty != "全部":
        difficulty_map = {
            "⭐ 入门": 1,
            "⭐⭐ 初级": 2,
            "⭐⭐⭐ 中级": 3,
            "⭐⭐⭐⭐ 高级": 4
        }
        target_diff = difficulty_map.get(difficulty, 0)
        filtered = [t for t in filtered if t["difficulty"].count("⭐") == target_diff]
    
    # 按搜索词筛选
    if search:
        filtered = [t for t in filtered if search.lower() in t["name"].lower() or search.lower() in t["description"].lower()]
    
    return filtered


def on_strategy_selected(name, params):
    """策略选择回调"""
    
    if 'selected_templates' not in st.session_state:
        st.session_state.selected_templates = []
    
    if name not in st.session_state.selected_templates:
        st.session_state.selected_templates.append(name)
        st.success(f"✅ 已选择策略：{name}")
    else:
        st.info(f"ℹ️ 策略 {name} 已在选择列表中")
