import streamlit as st
import pandas as pd
import math
from datetime import datetime, timedelta

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
    .cost-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #1f4e79;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .study-item {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 3px solid #2e8b57;
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
    'load_flow': {'name': 'Load Flow Study', 'base_hours_per_bus': 0.8, 'complexity': 'Medium', 'emoji': '⚡'},
    'short_circuit': {'name': 'Short Circuit Study', 'base_hours_per_bus': 1.0, 'complexity': 'Medium-High', 'emoji': '⚡'},
    'pdc': {'name': 'Protective Device Coordination', 'base_hours_per_bus': 1.5, 'complexity': 'High', 'emoji': '🔧'},
    'arc_flash': {'name': 'Arc Flash Study', 'base_hours_per_bus': 1.2, 'complexity': 'High', 'emoji': '🔥'}
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
        'costs': {},
        'timeline': {}
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
                'emoji': study_data['emoji'],
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
    subtotal = total_study_cost + meeting_cost + report_cost
    total_cost = subtotal * (1 + custom_margin/100)
    
    # Timeline calculation
    base_duration = max(4, total_study_hours / 8)
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
        'duration_days': timeline_days
    }
    
    return results

# Calculate results
results = calculate_project_cost()

# Display results
st.header("📊 Cost Analysis Results")

# Key metrics in columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="cost-card">
        <h3 style="color: #1f4e79; margin: 0;">💰 Total Cost</h3>
        <h2 style="color: #2e8b57; margin: 5px 0;">₹{results['costs']['total_cost']:,.0f}</h2>
        <p style="margin: 0; color: #666;">+{custom_margin}% margin</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="cost-card">
        <h3 style="color: #1f4e79; margin: 0;">⏱️ Total Hours</h3>
        <h2 style="color: #2e8b57; margin: 5px 0;">{results['costs']['total_hours']:.0f}</h2>
        <p style="margin: 0; color: #666;">{len(results['studies'])} studies</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="cost-card">
        <h3 style="color: #1f4e79; margin: 0;">📅 Duration</h3>
        <h2 style="color: #2e8b57; margin: 5px 0;">{results['timeline']['duration_days']}</h2>
        <p style="margin: 0; color: #666;">days</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="cost-card">
        <h3 style="color: #1f4e79; margin: 0;">🔌 Buses</h3>
        <h2 style="color: #2e8b57; margin: 5px 0;">{results['project_info']['estimated_buses']}</h2>
        <p style="margin: 0; color: #666;">estimated</p>
    </div>
    """, unsafe_allow_html=True)

# Study breakdown
if results['studies']:
    st.header("📋 Study-wise Breakdown")
    
    for study_key, study in results['studies'].items():
        st.markdown(f"""
        <div class="study-item">
            <h4>{study['emoji']} {study['name']}</h4>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>Complexity:</strong> {study['complexity']}<br>
                    <strong>Hours:</strong> {study['hours']:.1f} 
                    <small>(Sr: {study['senior_hours']:.1f}, Mid: {study['mid_hours']:.1f}, Jr: {study['junior_hours']:.1f})</small>
                </div>
                <div style="text-align: right;">
                    <h3 style="color: #2e8b57; margin: 0;">₹{study['total_cost']:,.0f}</h3>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Cost breakdown table
    st.subheader("💰 Detailed Cost Breakdown")
    
    breakdown_data = []
    for study_key, study in results['studies'].items():
        breakdown_data.append({
            'Study Type': f"{study['emoji']} {study['name']}",
            'Complexity': study['complexity'],
            'Total Hours': f"{study['hours']:.1f}",
            'Senior Cost': f"₹{study['senior_cost']:,.0f}",
            'Mid Cost': f"₹{study['mid_cost']:,.0f}",
            'Junior Cost': f"₹{study['junior_cost']:,.0f}",
            'Total Cost': f"₹{study['total_cost']:,.0f}"
        })
    
    df = pd.DataFrame(breakdown_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.warning("⚠️ No studies selected. Please select at least one study type from the sidebar.")

# Additional costs breakdown
st.subheader("💼 Additional Cost Components")

additional_col1, additional_col2, additional_col3 = st.columns(3)

with additional_col1:
    st.markdown(f"""
    <div class="study-item">
        <h4>🤝 Client Meetings</h4>
        <p><strong>{client_meetings} meetings × ₹8,000</strong></p>
        <h3 style="color: #2e8b57; margin: 0;">₹{results['costs']['meeting_cost']:,.0f}</h3>
    </div>
    """, unsafe_allow_html=True)

with additional_col2:
    st.markdown(f"""
    <div class="study-item">
        <h4>📄 Report Preparation</h4>
        <p><strong>{report_format}</strong></p>
        <h3 style="color: #2e8b57; margin: 0;">₹{results['costs']['report_cost']:,.0f}</h3>
    </div>
    """, unsafe_allow_html=True)

with additional_col3:
    st.markdown(f"""
    <div class="study-item">
        <h4>📈 Profit Margin</h4>
        <p><strong>{custom_margin}% on subtotal</strong></p>
        <h3 style="color: #2e8b57; margin: 0;">₹{results['costs']['margin_amount']:,.0f}</h3>
    </div>
    """, unsafe_allow_html=True)

# Timeline information
st.header("📅 Project Timeline")

timeline_col1, timeline_col2 = st.columns(2)

with timeline_col1:
    st.markdown(f"""
    <div class="cost-card">
        <h4>📅 Project Schedule</h4>
        <p><strong>Start Date:</strong> {results['timeline']['start_date']}</p>
        <p><strong>End Date:</strong> {results['timeline']['end_date']}</p>
        <p><strong>Duration:</strong> {results['timeline']['duration_days']} days</p>
        <p><strong>Delivery Type:</strong> {delivery_type}</p>
    </div>
    """, unsafe_allow_html=True)

with timeline_col2:
    st.markdown(f"""
    <div class="cost-card">
        <h4>👥 Resource Allocation</h4>
        <p><strong>Senior Engineers:</strong> {results['costs']['total_hours'] * 0.20:.1f} hours (20%)</p>
        <p><strong>Mid-level Engineers:</strong> {results['costs']['total_hours'] * 0.30:.1f} hours (30%)</p>
        <p><strong>Junior Engineers:</strong> {results['costs']['total_hours'] * 0.50:.1f} hours (50%)</p>
    </div>
    """, unsafe_allow_html=True)

# Export section
st.header("💾 Export Options")

# Create comprehensive CSV data
if st.button("📊 Generate Complete Report", type="primary"):
    # Project summary
    summary_data = {
        'Parameter': [
            'Project Name', 'Client Name', 'Start Date', 'End Date', 'Duration (Days)',
            'IT Capacity (MW)', 'Mechanical Load (MW)', 'House Load (MW)', 'Total Load (MW)',
            'Tier Level', 'Delivery Type', 'Estimated Buses',
            'Total Study Cost', 'Meeting Cost', 'Report Cost', 'Margin Amount', 'Total Project Cost',
            'Total Hours', 'Studies Selected', 'Generated By', 'Generated On'
        ],
        'Value': [
            project_name, client_name or 'Not Specified', 
            results['timeline']['start_date'], results['timeline']['end_date'], results['timeline']['duration_days'],
            it_capacity, mechanical_load, house_load, results['project_info']['total_load'],
            tier_level, delivery_type, results['project_info']['estimated_buses'],
            f"₹{results['costs']['total_study_cost']:,.0f}",
            f"₹{results['costs']['meeting_cost']:,.0f}",
            f"₹{results['costs']['report_cost']:,.0f}",
            f"₹{results['costs']['margin_amount']:,.0f}",
            f"₹{results['costs']['total_cost']:,.0f}",
            f"{results['costs']['total_hours']:.0f}",
            len(results['studies']),
            'Abhishek Diwanji - Power Systems Expert',
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ]
    }
    
    csv_data = pd.DataFrame(summary_data).to_csv(index=False)
    
    st.download_button(
        label="📥 Download Complete Report (CSV)",
        data=csv_data,
        file_name=f"DC_Complete_Report_{project_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        help="Download comprehensive project report with all calculations"
    )

# Quick summary download
col1, col2 = st.columns(2)

with col1:
    if st.button("📋 Quick Summary"):
        quick_data = {
            'Item': ['Total Cost', 'Total Hours', 'Duration', 'Studies', 'Buses'],
            'Value': [
                f"₹{results['costs']['total_cost']:,.0f}",
                f"{results['costs']['total_hours']:.0f}",
                f"{results['timeline']['duration_days']} days",
                len(results['studies']),
                results['project_info']['estimated_buses']
            ]
        }
        
        quick_csv = pd.DataFrame(quick_data).to_csv(index=False)
        st.download_button(
            label="📥 Download Quick Summary",
            data=quick_csv,
            file_name=f"DC_Quick_Summary_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )

with col2:
    if st.button("📊 Study Breakdown"):
        if results['studies']:
            study_data = []
            for study in results['studies'].values():
                study_data.append({
                    'Study': study['name'],
                    'Complexity': study['complexity'],
                    'Hours': f"{study['hours']:.1f}",
                    'Cost': f"₹{study['total_cost']:,.0f}"
                })
            
            study_csv = pd.DataFrame(study_data).to_csv(index=False)
            st.download_button(
                label="📥 Download Study Breakdown",
                data=study_csv,
                file_name=f"DC_Study_Breakdown_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )

# Technical specifications
with st.expander("🔧 Technical Specifications & Methodology"):
    st.markdown("""
    ### 📊 Calculation Methodology
    
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
    - Industry salary surveys and consultation rates (2025)
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p><b>⚡ Data Center Power System Studies Cost Estimator</b></p>
    <p>🚀 Developed by <b>Abhishek Diwanji</b> | Power Systems Engineering Expert</p>
    <p>📧 For professional consulting, custom tools, and technical support</p>
    <p><i>Reliable Version 1.0 | No External Dependencies</i></p>
</div>
""", unsafe_allow_html=True)
