import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import math
from datetime import datetime, timedelta
import base64
from io import BytesIO

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
project_name = st.sidebar.text_input("Project Name", value="Data Center Power Studies")
client_name = st.sidebar.text_input("Client Name", value="")

# Timeline inputs
start_date = st.sidebar.date_input("Project Start Date", value=datetime.now().date())

# Load inputs
st.sidebar.subheader("⚡ Electrical Load Parameters")
it_capacity = st.sidebar.number_input("IT Capacity (MW)", min_value=0.1, max_value=100.0, value=5.0, step=0.1)
mechanical_load = st.sidebar.number_input("Mechanical Load (MW)", min_value=0.1, max_value=50.0, value=2.0, step=0.1)
house_load = st.sidebar.number_input("House/Auxiliary Load (MW)", min_value=0.1, max_value=20.0, value=0.5, step=0.1)

# Tier and delivery
tier_level = st.sidebar.selectbox("Tier Level", ["Tier I", "Tier II", "Tier III", "Tier IV"], index=2)
delivery_type = st.sidebar.selectbox("Delivery Type", ["Standard", "Urgent"])
report_format = st.sidebar.selectbox("Report Format", ["Basic PDF", "Detailed Report with Appendices", "Client-Branded Report"], index=1)

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

# Study data
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

REPORT_MULTIPLIERS = {"Basic PDF": 1.0, "Detailed Report with Appendices": 1.8, "Client-Branded Report": 2.2}

# Calculation function
def calculate_project_cost():
    total_load = it_capacity + mechanical_load + house_load
    estimated_buses = math.ceil(total_load * BUS_PER_MW[tier_level])
    
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
        'costs': {}
    }
    
    # Calculate study costs
    total_study_hours = 0
    total_study_cost = 0
    tier_complexity = TIER_FACTORS[tier_level]
    urgency_multiplier = 1.3 if delivery_type == "Urgent" else 1.0
    
    for study_key, study_data in STUDIES_DATA.items():
        if studies_selected.get(study_key, False):
            study_hours = estimated_buses * study_data['base_hours_per_bus'] * tier_complexity
            total_study_hours += study_hours
            
            # Calculate costs by level
            senior_hours = study_hours * RATES['senior']['allocation']
            mid_hours = study_hours * RATES['mid']['allocation']
            junior_hours = study_hours * RATES['junior']['allocation']
            
            senior_cost = senior_hours * RATES['senior']['hourly'] * urgency_multiplier
            mid_cost = mid_hours * RATES['mid']['hourly'] * urgency_multiplier
            junior_cost = junior_hours * RATES['junior']['hourly'] * urgency_multiplier
            
            study_total_cost = senior_cost + mid_cost + junior_cost
            total_study_cost += study_total_cost
            
            results['studies'][study_key] = {
                'name': study_data['name'],
                'hours': study_hours,
                'total_cost': study_total_cost,
                'complexity': study_data['complexity']
            }
    
    # Additional costs
    meeting_cost = client_meetings * 8000
    report_cost = 15000 * REPORT_MULTIPLIERS[report_format]
    subtotal = total_study_cost + meeting_cost + report_cost
    total_cost = subtotal * (1 + custom_margin/100)
    
    results['costs'] = {
        'total_study_cost': total_study_cost,
        'meeting_cost': meeting_cost,
        'report_cost': report_cost,
        'subtotal': subtotal,
        'total_cost': total_cost,
        'total_hours': total_study_hours
    }
    
    return results

# Calculate results
results = calculate_project_cost()

# Display results
st.header("📊 Cost Analysis Results")

# Key metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Project Cost", f"₹{results['costs']['total_cost']:,.0f}")
with col2:
    st.metric("Total Hours", f"{results['costs']['total_hours']:.0f}")
with col3:
    st.metric("Estimated Buses", f"{results['project_info']['estimated_buses']}")
with col4:
    st.metric("Studies Selected", f"{len(results['studies'])}")

# Charts
if results['studies']:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Cost Breakdown by Study")
        study_names = [study['name'] for study in results['studies'].values()]
        study_costs = [study['total_cost'] for study in results['studies'].values()]
        
        fig_pie = px.pie(values=study_costs, names=study_names, title="Study-wise Cost Distribution")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("⏱️ Hours by Study Type")
        study_hours = [study['hours'] for study in results['studies'].values()]
        
        fig_bar = px.bar(x=study_names, y=study_hours, title="Hours by Study Type")
        st.plotly_chart(fig_bar, use_container_width=True)

# Detailed breakdown
st.header("📋 Detailed Study Breakdown")
if results['studies']:
    breakdown_data = []
    for study_key, study in results['studies'].items():
        breakdown_data.append({
            'Study Type': study['name'],
            'Complexity': study['complexity'],
            'Hours': f"{study['hours']:.1f}",
            'Cost': f"₹{study['total_cost']:,.0f}"
        })
    
    df = pd.DataFrame(breakdown_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

# Export section
st.header("💾 Export Options")

# Simple CSV export
if st.button("📊 Download Summary Report"):
    summary_data = {
        'Parameter': ['Project Name', 'Client', 'Total Load (MW)', 'Total Cost', 'Total Hours', 'Studies Count'],
        'Value': [
            project_name,
            client_name or 'Not Specified',
            results['project_info']['total_load'],
            f"₹{results['costs']['total_cost']:,.0f}",
            f"{results['costs']['total_hours']:.0f}",
            len(results['studies'])
        ]
    }
    
    csv_data = pd.DataFrame(summary_data).to_csv(index=False)
    st.download_button(
        label="📥 Download CSV File",
        data=csv_data,
        file_name=f"DC_Cost_Summary_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p><b>⚡ Data Center Power System Studies Cost Estimator</b></p>
    <p>🚀 Developed by <b>Abhishek Diwanji</b> | Power Systems Engineering Expert</p>
    <p>📧 For professional consulting, custom tools, and technical support</p>
    <p><i>Simplified Version 1.0 | Core Analytics Features</i></p>
</div>
""", unsafe_allow_html=True)
