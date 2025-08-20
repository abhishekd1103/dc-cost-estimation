import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
from datetime import datetime, timedelta
import base64
from io import BytesIO
import xlsxwriter
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import tempfile
import os

# Page configuration
st.set_page_config(
    page_title="DC Power Studies Cost Estimator | Abhishek Diwanji",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2e8b57 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    .developer-credit {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
        font-weight: bold;
        margin: 20px 0;
    }
    .disclaimer-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 15px;
        margin: 20px 0;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 4px solid #1f4e79;
    }
    .stMetric {
        background: white;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Header with branding
st.markdown("""
<div class="main-header">
    <h1>⚡ Data Center Power System Studies</h1>
    <h2>Professional Cost Estimation Dashboard</h2>
    <p>Advanced Engineering Tool for Load Flow, Short Circuit, PDC & Arc Flash Studies</p>
</div>
""", unsafe_allow_html=True)

# Developer credit
st.markdown("""
<div class="developer-credit">
    🚀 Developed by <strong>Abhishek Diwanji</strong> | Power Systems Engineering Expert 
    <br>📧 Contact for Custom Solutions & Professional Consulting
</div>
""", unsafe_allow_html=True)

# Disclaimer
st.markdown("""
<div class="disclaimer-box">
    <h4>⚠️ Important Disclaimer</h4>
    <p><strong>Bus Count Estimation:</strong> This tool focuses on cost estimation for power system studies. 
    Bus count calculations are handled by a separate specialized tool which will be integrated in future versions. 
    Current bus estimates are for costing purposes only.</p>
    <p><strong>Professional Use:</strong> Results are estimates based on industry standards. 
    Always validate with qualified electrical engineers for actual project implementation.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar inputs
st.sidebar.header("📊 Project Configuration")

# Project Information
st.sidebar.subheader("🏢 Project Details")
project_name = st.sidebar.text_input("Project Name", value="Data Center Power Studies", help="Enter project identifier")
client_name = st.sidebar.text_input("Client Name", value="", help="Client organization name")

# Timeline inputs
start_date = st.sidebar.date_input(
    "Project Start Date", 
    value=datetime.now().date(),
    help="When will the project begin?"
)

# Load inputs
st.sidebar.subheader("⚡ Electrical Load Parameters")
it_capacity = st.sidebar.number_input("IT Capacity (MW)", min_value=0.1, max_value=100.0, value=5.0, step=0.1)
mechanical_load = st.sidebar.number_input("Mechanical Load (MW)", min_value=0.1, max_value=50.0, value=2.0, step=0.1)
house_load = st.sidebar.number_input("House/Auxiliary Load (MW)", min_value=0.1, max_value=20.0, value=0.5, step=0.1)

# Tier and delivery
tier_level = st.sidebar.selectbox("Tier Level", ["Tier I", "Tier II", "Tier III", "Tier IV"], index=2)
delivery_type = st.sidebar.selectbox("Delivery Type", ["Standard", "Urgent"])
report_format = st.sidebar.selectbox(
    "Report Format", 
    ["Basic PDF", "Detailed Report with Appendices", "Client-Branded Report"],
    index=1
)

# Studies selection
st.sidebar.subheader("📋 Studies Required")
studies_selected = {}
studies_selected['load_flow'] = st.sidebar.checkbox("Load Flow Study", value=True)
studies_selected['short_circuit'] = st.sidebar.checkbox("Short Circuit Study", value=True)
studies_selected['pdc'] = st.sidebar.checkbox("Protective Device Coordination", value=True)
studies_selected['arc_flash'] = st.sidebar.checkbox("Arc Flash Study", value=True)

# Additional parameters
client_meetings = st.sidebar.slider("Expected Client Meetings", 0, 10, 2, 1)
custom_margin = st.sidebar.slider("Custom Margin (%)", 0, 30, 15, 1)

# Calibration factors
st.sidebar.subheader("🔧 Calibration Factors")
bus_calibration = st.sidebar.slider("Bus Count Calibration Factor", 0.5, 2.0, 1.0, 0.1)
urgency_multiplier = st.sidebar.slider("Urgent Delivery Multiplier", 1.0, 2.0, 1.3, 0.1)

# Study complexity and rates data
TIER_FACTORS = {"Tier I": 1.0, "Tier II": 1.2, "Tier III": 1.5, "Tier IV": 2.0}
BUS_PER_MW = {"Tier I": 1.5, "Tier II": 1.7, "Tier III": 2.0, "Tier IV": 2.3}

STUDIES_DATA = {
    'load_flow': {'name': 'Load Flow Study', 'base_hours_per_bus': 0.8, 'complexity': 'Medium'},
    'short_circuit': {'name': 'Short Circuit Study', 'base_hours_per_bus': 1.0, 'complexity': 'Medium-High'},
    'pdc': {'name': 'Protective Device Coordination', 'base_hours_per_bus': 1.5, 'complexity': 'High'},
    'arc_flash': {'name': 'Arc Flash Study', 'base_hours_per_bus': 1.2, 'complexity': 'High'}
}

RATES = {
    'senior': {'hourly': 1200, 'allocation': 0.20, 'title': 'Senior Engineer/Manager'},
    'mid': {'hourly': 650, 'allocation': 0.30, 'title': 'Mid-level Engineer'},
    'junior': {'hourly': 350, 'allocation': 0.50, 'title': 'Junior Engineer'}
}

REPORT_MULTIPLIERS = {
    "Basic PDF": 1.0,
    "Detailed Report with Appendices": 1.8,
    "Client-Branded Report": 2.2
}

# Calculation function
def calculate_project_cost():
    # Basic calculations
    total_load = it_capacity + mechanical_load + house_load
    estimated_buses = math.ceil(total_load * BUS_PER_MW[tier_level] * bus_calibration)
    
    # Initialize results
    results = {
        'project_info': {
            'name': project_name,
            'client': client_name,
            'start_date': start_date,
            'total_load': total_load,
            'estimated_buses': estimated_buses,
            'tier': tier_level,
            'delivery': delivery_type,
            'report_format': report_format
        },
        'studies': {},
        'timeline': {},
        'costs': {},
        'summary': {}
    }
    
    # Calculate study-wise costs
    total_study_hours = 0
    total_study_cost = 0
    tier_complexity = TIER_FACTORS[tier_level]
    
    for study_key, study_data in STUDIES_DATA.items():
        if studies_selected.get(study_key, False):
            # Calculate hours
            study_hours = estimated_buses * study_data['base_hours_per_bus'] * tier_complexity
            total_study_hours += study_hours
            
            # Calculate costs by level
            senior_hours = study_hours * RATES['senior']['allocation']
            mid_hours = study_hours * RATES['mid']['allocation']
            junior_hours = study_hours * RATES['junior']['allocation']
            
            # Apply urgency multiplier if needed
            rate_multiplier = urgency_multiplier if delivery_type == "Urgent" else 1.0
            
            senior_cost = senior_hours * RATES['senior']['hourly'] * rate_multiplier
            mid_cost = mid_hours * RATES['mid']['hourly'] * rate_multiplier
            junior_cost = junior_hours * RATES['junior']['hourly'] * rate_multiplier
            
            study_total_cost = senior_cost + mid_cost + junior_cost
            total_study_cost += study_total_cost
            
            # Store study results
            results['studies'][study_key] = {
                'name': study_data['name'],
                'hours': study_hours,
                'senior_hours': senior_hours,
                'mid_hours': mid_hours,
                'junior_hours': junior_hours,
                'senior_cost': senior_cost,
                'mid_cost': mid_cost,
                'junior_cost': junior_cost,
                'total_cost': study_total_cost,
                'complexity': study_data['complexity']
            }
    
    # Additional costs
    meeting_cost = client_meetings * 8000
    report_cost = 15000 * REPORT_MULTIPLIERS[report_format]
    
    # Total project cost
    subtotal = total_study_cost + meeting_cost + report_cost
    total_cost = subtotal * (1 + custom_margin/100)
    
    # Timeline calculation
    base_duration = max(4, total_study_hours / 8)  # Assuming 8 hours per day
    timeline_days = math.ceil(base_duration * (0.8 if delivery_type == "Standard" else 0.6))
    end_date = start_date + timedelta(days=timeline_days)
    
    results['costs'] = {
        'total_study_cost': total_study_cost,
        'meeting_cost': meeting_cost,
        'report_cost': report_cost,
        'subtotal': subtotal,
        'margin_amount': subtotal * (custom_margin/100),
        'total_cost': total_cost,
        'total_hours': total_study_hours
    }
    
    results['timeline'] = {
        'start_date': start_date,
        'end_date': end_date,
        'duration_days': timeline_days,
        'phases': [
            {'name': 'Project Initiation', 'duration': max(1, timeline_days * 0.1)},
            {'name': 'Data Collection', 'duration': max(2, timeline_days * 0.15)},
            {'name': 'ETAP Modeling', 'duration': max(3, timeline_days * 0.25)},
            {'name': 'Studies Execution', 'duration': max(5, timeline_days * 0.35)},
            {'name': 'Analysis & Review', 'duration': max(2, timeline_days * 0.10)},
            {'name': 'Reporting', 'duration': max(1, timeline_days * 0.05)}
        ]
    }
    
    return results

# Generate export functions
def create_excel_report(results):
    """Create Excel report with watermark"""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'bg_color': '#1f4e79',
            'font_color': 'white',
            'align': 'center'
        })
        
        subheader_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#E6F3FF',
            'align': 'center'
        })
        
        currency_format = workbook.add_format({'num_format': '₹#,##0'})
        percent_format = workbook.add_format({'num_format': '0%'})
        
        # Project Summary Sheet
        summary_data = [
            ['Project Name', results['project_info']['name']],
            ['Client', results['project_info']['client'] or 'Not Specified'],
            ['Total Load (MW)', results['project_info']['total_load']],
            ['Tier Level', results['project_info']['tier']],
            ['Delivery Type', results['project_info']['delivery']],
            ['Estimated Buses', results['project_info']['estimated_buses']],
            ['Total Project Cost', f"₹{results['costs']['total_cost']:,.0f}"],
            ['Project Duration', f"{results['timeline']['duration_days']} days"],
            ['Generated By', 'Abhishek Diwanji - Power Systems Expert'],
            ['Generated On', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        summary_df = pd.DataFrame(summary_data, columns=['Parameter', 'Value'])
        summary_df.to_excel(writer, sheet_name='Project Summary', index=False)
        
        # Studies Breakdown Sheet
        studies_data = []
        for study_key, study in results['studies'].items():
            studies_data.append([
                study['name'],
                f"{study['hours']:.1f}",
                f"₹{study['total_cost']:,.0f}",
                study['complexity'],
                f"₹{study['senior_cost']:,.0f}",
                f"₹{study['mid_cost']:,.0f}",
                f"₹{study['junior_cost']:,.0f}"
            ])
        
        studies_df = pd.DataFrame(studies_data, columns=[
            'Study Type', 'Hours', 'Total Cost', 'Complexity',
            'Senior Cost', 'Mid Cost', 'Junior Cost'
        ])
        studies_df.to_excel(writer, sheet_name='Studies Breakdown', index=False)
        
        # Timeline Sheet
        timeline_data = []
        current_date = results['timeline']['start_date']
        for phase in results['timeline']['phases']:
            phase_days = math.ceil(phase['duration'])
            timeline_data.append([
                phase['name'],
                current_date.strftime('%Y-%m-%d'),
                (current_date + timedelta(days=phase_days)).strftime('%Y-%m-%d'),
                phase_days
            ])
            current_date += timedelta(days=phase_days)
        
        timeline_df = pd.DataFrame(timeline_data, columns=[
            'Phase', 'Start Date', 'End Date', 'Duration (Days)'
        ])
        timeline_df.to_excel(writer, sheet_name='Project Timeline', index=False)
        
        # Add watermark to each sheet
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            worksheet.set_header('&C&"Arial,Bold"Data Center Cost Estimator - Abhishek Diwanji')
            worksheet.set_footer('&C&"Arial,Italic"Confidential - For Professional Use Only')
    
    return output.getvalue()

def create_pdf_report(results):
    """Create PDF report with watermark"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1f4e79'),
        alignment=1,
        spaceAfter=30
    )
    
    # Header
    title = Paragraph("Data Center Power System Studies<br/>Cost Estimation Report", title_style)
    story.append(title)
    
    # Developer credit
    credit = Paragraph(
        f"<b>Developed by: Abhishek Diwanji</b><br/>Power Systems Engineering Expert<br/>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
        styles['Normal']
    )
    story.append(credit)
    story.append(Spacer(1, 20))
    
    # Project information table
    proj_data = [
        ['Parameter', 'Value'],
        ['Project Name', results['project_info']['name']],
        ['Client', results['project_info']['client'] or 'Not Specified'],
        ['Total Load (MW)', f"{results['project_info']['total_load']:.1f}"],
        ['Tier Level', results['project_info']['tier']],
        ['Total Cost', f"₹{results['costs']['total_cost']:,.0f}"]
    ]
    
    proj_table = Table(proj_data)
    proj_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e79')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(proj_table)
    story.append(Spacer(1, 20))
    
    # Studies breakdown
    story.append(Paragraph("Studies Breakdown", styles['Heading2']))
    
    studies_data = [['Study Type', 'Hours', 'Cost (₹)', 'Complexity']]
    for study_key, study in results['studies'].items():
        studies_data.append([
            study['name'],
            f"{study['hours']:.1f}",
            f"{study['total_cost']:,.0f}",
            study['complexity']
        ])
    
    studies_table = Table(studies_data)
    studies_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e8b57')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(studies_table)
    
    # Footer
    story.append(Spacer(1, 40))
    footer = Paragraph(
        "<b>Disclaimer:</b> This is a cost estimation tool. Bus count calculations handled separately. "
        "Validate with qualified electrical engineers for actual implementation.",
        styles['Italic']
    )
    story.append(footer)
    
    doc.build(story)
    return buffer.getvalue()

# Calculate results
results = calculate_project_cost()

# Main dashboard layout
col1, col2 = st.columns([3, 2])

with col1:
    st.header("📊 Cost Analysis Results")
    
    # Key metrics
    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.metric("Total Project Cost", f"₹{results['costs']['total_cost']:,.0f}", 
                 delta=f"+{custom_margin}% margin")
    with metric_cols[1]:
        st.metric("Total Hours", f"{results['costs']['total_hours']:.0f}", 
                 delta=f"{len(results['studies'])} studies")
    with metric_cols[2]:
        st.metric("Project Duration", f"{results['timeline']['duration_days']} days")
    with metric_cols[3]:
        st.metric("Estimated Buses", f"{results['project_info']['estimated_buses']}")
    
    # Cost breakdown chart
    if results['studies']:
        st.subheader("💰 Cost Breakdown by Study Type")
        
        study_names = [study['name'] for study in results['studies'].values()]
        study_costs = [study['total_cost'] for study in results['studies'].values()]
        
        fig_pie = px.pie(
            values=study_costs,
            names=study_names,
            title="Study-wise Cost Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Cost components bar chart
        cost_components = ['Study Costs', 'Meeting Costs', 'Report Costs', 'Margin']
        cost_values = [
            results['costs']['total_study_cost'],
            results['costs']['meeting_cost'],
            results['costs']['report_cost'],
            results['costs']['margin_amount']
        ]
        
        fig_bar = px.bar(
            x=cost_components,
            y=cost_values,
            title="Cost Components Breakdown",
            labels={'x': 'Components', 'y': 'Cost (₹)'},
            color=cost_components,
            color_discrete_sequence=['#1f4e79', '#2e8b57', '#ff6b6b', '#ffa500']
        )
        fig_bar.update_traces(text=[f"₹{v:,.0f}" for v in cost_values], textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.header("📅 Project Timeline")
    
    # Timeline visualization
    timeline_data = []
    current_date = results['timeline']['start_date']
    colors_list = ['#1f4e79', '#2e8b57', '#ff6b6b', '#ffa500', '#9d4edd', '#06ffa5']
    
    for i, phase in enumerate(results['timeline']['phases']):
        phase_days = math.ceil(phase['duration'])
        end_date = current_date + timedelta(days=phase_days)
        
        timeline_data.append({
            'Phase': phase['name'],
            'Start': current_date,
            'End': end_date,
            'Duration': phase_days
        })
        current_date = end_date
    
    # Gantt chart
    fig_timeline = go.Figure()
    
    for i, phase in enumerate(timeline_data):
        fig_timeline.add_trace(go.Scatter(
            x=[phase['Start'], phase['End']],
            y=[i, i],
            mode='lines',
            line=dict(color=colors_list[i % len(colors_list)], width=20),
            name=phase['Phase'],
            hovertemplate=f"<b>{phase['Phase']}</b><br>" +
                         f"Duration: {phase['Duration']} days<br>" +
                         f"Start: {phase['Start']}<br>" +
                         f"End: {phase['End']}<extra></extra>"
        ))
    
    fig_timeline.update_layout(
        title="Project Timeline (Gantt Chart)",
        xaxis_title="Date",
        yaxis_title="Project Phases",
        yaxis=dict(
            tickvals=list(range(len(timeline_data))),
            ticktext=[phase['Phase'] for phase in timeline_data]
        ),
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Resource allocation pie chart
    st.subheader("👥 Resource Allocation")
    
    total_senior_cost = sum(study['senior_cost'] for study in results['studies'].values())
    total_mid_cost = sum(study['mid_cost'] for study in results['studies'].values())
    total_junior_cost = sum(study['junior_cost'] for study in results['studies'].values())
    
    if total_senior_cost + total_mid_cost + total_junior_cost > 0:
        fig_resource = px.pie(
            values=[total_senior_cost, total_mid_cost, total_junior_cost],
            names=['Senior Level', 'Mid Level', 'Junior Level'],
            title="Resource Cost Distribution",
            color_discrete_sequence=['#ff6b6b', '#ffa500', '#4ecdc4']
        )
        fig_resource.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_resource, use_container_width=True)

# Detailed breakdown table
st.header("📋 Detailed Study Breakdown")

if results['studies']:
    breakdown_data = []
    for study_key, study in results['studies'].items():
        breakdown_data.append({
            'Study Type': study['name'],
            'Complexity': study['complexity'],
            'Total Hours': f"{study['hours']:.1f}",
            'Senior Hours': f"{study['senior_hours']:.1f}",
            'Mid Hours': f"{study['mid_hours']:.1f}",
            'Junior Hours': f"{study['junior_hours']:.1f}",
            'Senior Cost': f"₹{study['senior_cost']:,.0f}",
            'Mid Cost': f"₹{study['mid_cost']:,.0f}",
            'Junior Cost': f"₹{study['junior_cost']:,.0f}",
            'Total Cost': f"₹{study['total_cost']:,.0f}"
        })
    
    breakdown_df = pd.DataFrame(breakdown_data)
    st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
else:
    st.warning("⚠️ No studies selected. Please select at least one study type from the sidebar.")

# Export section
st.header("💾 Export Options")

export_col1, export_col2, export_col3 = st.columns(3)

with export_col1:
    if st.button("📊 Download Excel Report", type="primary"):
        excel_data = create_excel_report(results)
        st.download_button(
            label="📥 Download Excel File",
            data=excel_data,
            file_name=f"DC_Cost_Estimate_{project_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

with export_col2:
    if st.button("📄 Download PDF Report", type="primary"):
        pdf_data = create_pdf_report(results)
        st.download_button(
            label="📥 Download PDF File",
            data=pdf_data,
            file_name=f"DC_Cost_Report_{project_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )

with export_col3:
    # CSV export for quick sharing
    summary_data = {
        'Parameter': ['Total Cost', 'Total Hours', 'Duration', 'Studies Count', 'Margin %'],
        'Value': [
            f"₹{results['costs']['total_cost']:,.0f}",
            f"{results['costs']['total_hours']:.0f}",
            f"{results['timeline']['duration_days']} days",
            len(results['studies']),
            f"{custom_margin}%"
        ]
    }
    
    csv_data = pd.DataFrame(summary_data).to_csv(index=False)
    st.download_button(
        label="📋 Download CSV Summary",
        data=csv_data,
        file_name=f"DC_Summary_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )

# Technical specifications
with st.expander("🔧 Technical Specifications & Methodology"):
    st.markdown("""
    ### Calculation Methodology
    
    **Cost Calculation Formula:**
    ```
    Study_Cost = Bus_Count × Base_Hours_per_Bus × Tier_Complexity_Factor × Rate_Structure
    Total_Project_Cost = (Study_Costs + Additional_Costs) × (1 + Margin%)
    ```
    
    **Rate Structure (Indian Market 2025):**
    - Senior Engineer: ₹1,200/hour (20% allocation)
    - Mid-level Engineer: ₹650/hour (30% allocation)  
    - Junior Engineer: ₹350/hour (50% allocation)
    
    **Study Complexity Factors:**
    - Load Flow: 0.8 hours/bus (Medium complexity)
    - Short Circuit: 1.0 hours/bus (Medium-High complexity)
    - PDC: 1.5 hours/bus (High complexity)
    - Arc Flash: 1.2 hours/bus (High complexity)
    
    **Tier Multipliers:**
    - Tier I: 1.0x, Tier II: 1.2x, Tier III: 1.5x, Tier IV: 2.0x
    
    **Additional Costs:**
    - Client Meetings: ₹8,000 per meeting
    - Report Preparation: ₹15,000 (base) × format multiplier
    
    **References:**
    - IEEE 1584-2018: Arc Flash Standards
    - IEC 60909: Short Circuit Calculations  
    - Industry salary surveys and consultation rates
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p><b>⚡ Data Center Power System Studies Cost Estimator</b></p>
    <p>🚀 Developed by <b>Abhishek Diwanji</b> | Power Systems Engineering Expert</p>
    <p>📧 For professional consulting, custom tools, and technical support</p>
    <p><i>Version 2.0 | Advanced Analytics & Export Features</i></p>
</div>
""", unsafe_allow_html=True)
