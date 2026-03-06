"""
导出工具 - 回测结果导出功能
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import io


def export_results_to_csv(results: Dict[str, Any], filename: str = None) -> io.BytesIO:
    """导出回测结果为 CSV"""
    
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"backtest_results_{timestamp}.csv"
    
    # 创建 CSV 内容
    output = io.StringIO()
    
    # 写入指标
    output.write("=== 回测指标 ===\n")
    if 'metrics' in results:
        for key, value in results['metrics'].items():
            output.write(f"{key},{value}\n")
    
    output.write("\n=== 交易记录 ===\n")
    if 'trades' in results:
        trades_df = pd.DataFrame(results['trades'])
        trades_df.to_csv(output, index=False, encoding='utf-8-sig')
    
    # 转换为 BytesIO
    csv_buffer = io.BytesIO()
    csv_buffer.write(output.getvalue().encode('utf-8-sig'))
    csv_buffer.seek(0)
    
    return csv_buffer


def export_equity_curve_to_csv(equity_data: pd.DataFrame, filename: str = None) -> io.BytesIO:
    """导出权益曲线为 CSV"""
    
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"equity_curve_{timestamp}.csv"
    
    csv_buffer = io.BytesIO()
    equity_data.to_csv(csv_buffer, index=True, encoding='utf-8-sig')
    csv_buffer.seek(0)
    
    return csv_buffer


def export_results_to_pdf(results: Dict[str, Any], filename: str = None) -> Optional[bytes]:
    """导出回测结果为 PDF"""
    
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"backtest_report_{timestamp}.pdf"
        
        # 创建 PDF 文档
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # 样式
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # 标题
        elements.append(Paragraph("OpenFinAgent 回测报告", title_style))
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # 策略信息
        elements.append(Paragraph("策略信息", heading_style))
        
        if 'strategy_name' in results:
            strategy_data = [
                ['策略名称', results.get('strategy_name', 'N/A')],
                ['初始资金', f"¥{results.get('initial_capital', 0):,.2f}"],
                ['回测期间', results.get('period', 'N/A')],
            ]
            
            strategy_table = Table(strategy_data, colWidths=[2*inch, 4*inch])
            strategy_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            
            elements.append(strategy_table)
            elements.append(Spacer(1, 0.3*inch))
        
        # 回测指标
        elements.append(Paragraph("回测指标", heading_style))
        
        if 'metrics' in results:
            metrics_data = [['指标', '数值']]
            
            for key, value in results['metrics'].items():
                if isinstance(value, float):
                    value = f"{value:.2f}" if '比率' in key or '率' in key else f"{value:,.2f}"
                metrics_data.append([key, str(value)])
            
            metrics_table = Table(metrics_data, colWidths=[3*inch, 3*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f8f8')]),
            ]))
            
            elements.append(metrics_table)
            elements.append(Spacer(1, 0.3*inch))
        
        # 交易统计
        elements.append(Paragraph("交易统计", heading_style))
        
        if 'trades' in results and results['trades']:
            trades_summary = [
                ['总交易次数', len(results['trades'])],
                ['买入次数', len([t for t in results['trades'] if t.get('type') == 'buy'])],
                ['卖出次数', len([t for t in results['trades'] if t.get('type') == 'sell'])],
            ]
            
            trades_table = Table(trades_summary, colWidths=[3*inch, 3*inch])
            trades_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            
            elements.append(trades_table)
        
        # 构建 PDF
        doc.build(elements)
        
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
        
    except ImportError:
        st.error("导出 PDF 需要安装 reportlab: pip install reportlab")
        return None
    except Exception as e:
        st.error(f"导出 PDF 失败：{e}")
        return None


def export_chart_to_image(fig, filename: str = "chart.png") -> Optional[str]:
    """导出图表为图片"""
    
    try:
        # 尝试使用 kaleido
        fig.write_image(filename)
        return filename
    except Exception as e:
        st.error(f"导出图片失败：{e}")
        return None


def create_download_button(
    data: io.BytesIO,
    label: str,
    filename: str,
    mime: str = "text/csv",
    use_container_width: bool = True
):
    """创建下载按钮"""
    
    return st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime=mime,
        use_container_width=use_container_width
    )


def export_all_results(results: Dict[str, Any], equity_data: pd.DataFrame = None):
    """导出所有结果"""
    
    st.markdown("### 📥 导出选项")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # CSV 导出
        csv_data = export_results_to_csv(results)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        st.download_button(
            label="📊 下载 CSV",
            data=csv_data,
            file_name=f"backtest_{timestamp}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # PDF 导出
        pdf_data = export_results_to_pdf(results)
        if pdf_data:
            st.download_button(
                label="📄 下载 PDF",
                data=pdf_data,
                file_name=f"backtest_report_{timestamp}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    
    with col3:
        # 权益曲线 CSV
        if equity_data is not None:
            equity_csv = export_equity_curve_to_csv(equity_data)
            st.download_button(
                label="📈 下载权益曲线",
                data=equity_csv,
                file_name=f"equity_curve_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True
            )
