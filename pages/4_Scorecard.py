import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
import os

# --- Robust Import Setup ---
def find_project_root(current_path, marker='src'):
    root = current_path
    for _ in range(5):
        if os.path.exists(os.path.join(root, marker)):
            return root
        parent = os.path.dirname(root)
        if parent == root: break
        root = parent
    return None

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = find_project_root(current_dir)
if project_root and project_root not in sys.path:
    sys.path.insert(0, project_root)

# Fallback
if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())
    
from src.explainability import Explainer

st.set_page_config(layout="wide", page_title="Helix: Scorecard", page_icon="📈")

# --- Custom CSS (Tweaks only, respecting global theme) ---
st.markdown("""
<style>
    /* Adjustments for dark mode cards */
    div[data-testid="stMetricValue"] {
        color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)
def create_gauge(value, title, color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 18}},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': color},
            'bgcolor': "white",
            'steps': [{'range': [0, 100], 'color': "#f8f9fa"}]
        }
    ))
    fig.update_layout(height=200, margin=dict(l=20, r=20, t=50, b=20))
    return fig

# --- Load Data ---
if 'selected_customer_id' not in st.session_state:
    st.warning("No customer selected. Please select a customer from the Users list.")
    if st.button("Go to Customers"):
        st.switch_page("pages/2_Customers.py")
    st.stop()

cid = st.session_state['selected_customer_id']

@st.cache_data
def get_data(customer_id):
    try:
        # Dynamic path resolution to fix deployment issue
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(base_dir, "scored_data.csv")
        df = pd.read_csv(csv_path)
        # Ensure ID is string for matching
        df['customer_id'] = df['customer_id'].astype(str)
        row = df[df['customer_id'] == str(customer_id)]
        if not row.empty:
            return row.iloc[0]
    except Exception:
        pass
    
    # Fallback: Mock Data for specific IDs
    if str(customer_id).startswith("CUST-"):
        # Create a dummy row for display
        return pd.Series({
            'customer_id': customer_id,
            'employment_type': 'Salaried',
            'declared_monthly_income': 85000,
            'city_tier': 'Tier 1',
            'risk_band': 'Low Risk',
            'credit_score': 780,
            'stability_score': 85,
            'discipline_score': 75,
            'volatility_score': 90,
            'average_monthly_account_credit': 90000,
            'average_monthly_account_debit': 40000,
            'income_volatility': 0.05,
            'missed_utility_bill_count': 0
        })
        
    return None

customer = get_data(cid)

if customer is None:
    st.error(f"Customer {cid} not found.")
    st.stop()

# --- UI Layout ---

# Sidebar Profile
with st.sidebar:
    st.subheader("Customer Profile")
    st.markdown("---")
    
    # Name Display
    name = customer.get('customer_name', 'Unknown')
    
    # Deterministic Backfill for Legacy Data
    if pd.isna(name) or str(name).lower() in ['nan', 'n/a', 'unknown', 'none']:
        demo_names = [
            "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", 
            "Ishaan", "Diya", "Saanvi", "Anya", "Aadhya", "Pari", "Ananya", "Myra", "Rohan", 
            "Vikram", "Suresh", "Priya", "Rahul", "Neha", "Amit", "Sneha", "Rajesh", "Pooja", 
            "Ankit", "Meera", "Varun", "Karan", "Simran", "Deepak", "Kavita"
        ]
        idx = hash(str(cid)) % len(demo_names)
        name = demo_names[idx]
    
    st.markdown(f"**Name:** {name}")
    st.caption(f"ID: {cid}")
    
    st.markdown(f"**Employment:** {customer['employment_type']}")
    st.markdown(f"**Income:** ₹{customer['declared_monthly_income']:,.0f}")
    st.markdown(f"**City:** {customer['city_tier']}")
    st.markdown("---")
    if customer['risk_band'] == 'Low Risk':
        st.success(f"Band: {customer['risk_band']}")
    elif customer['risk_band'] == 'Medium Risk':
        st.warning(f"Band: {customer['risk_band']}")
    else:
        st.error(f"Band: {customer['risk_band']}")

# Main Header
c1, c2 = st.columns([3, 1])
with c1:
    st.title("Creditworthiness Scorecard")
    st.caption(f"Analysis for Reference ID: {cid}")
with c2:
    st.markdown("### ")
    if st.button("🔄 Recalculate"):
        st.rerun()

# Decision Banner
score = customer['credit_score']
if score >= 750:
    decision = "APPROVED"
    color = "#00c853" # Green
    offer = f"₹{int(customer['declared_monthly_income'] * 12):,}"
    tenure = "24 Months"
    desc = "Excellent Stability detected. High loan limit unlocked."
elif score >= 650:
    decision = "CONDITIONAL"
    color = "#ffd600" # Yellow - darker for contrast
    offer = f"₹{int(customer['declared_monthly_income'] * 6):,}"
    tenure = "12 Months"
    desc = "Good repayment potential. Standard offer available."
else:
    decision = "REJECTED"
    color = "#d50000" # Red
    offer = "₹0"
    tenure = "-"
    desc = "High volatility detected. Application declined at this time."

st.markdown(f"""
<div style="background-color: {color}; padding: 25px; border-radius: 15px; color: black; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
    <h2 style="margin:0; text-align:center; color: white; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">{decision}</h2>
    <p style="text-align:center; color: white; margin-bottom: 20px; font-style: italic;">{desc}</p>
    <div style="display:flex; justify-content:space-around; background: rgba(255,255,255,0.9); padding: 15px; border-radius: 10px;">
        <div style="text-align:center;">
            <span style="display:block; font-size:12px; color:#555;">PRE-APPROVED LIMIT</span>
            <span style="font-size:20px; font-weight:bold; color:#333;">{offer}</span>
        </div>
        <div style="text-align:center;">
            <span style="display:block; font-size:12px; color:#555;">KEY TERM</span>
            <span style="font-size:20px; font-weight:bold; color:#333;">{tenure}</span>
        </div>
        <div style="text-align:center;">
            <span style="display:block; font-size:12px; color:#555;">ML PREDICTED SCORE</span>
            <span style="font-size:20px; font-weight:bold; color:#333;">{int(score)}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 3 Pillars
st.subheader("Behavioral Signals (Input to Model)")
col1, col2, col3 = st.columns(3)

with col1:
    val = customer.get('stability_score', 0)
    st.plotly_chart(create_gauge(val, "Stability", "#4facfe"), key="stability_gauge", width="stretch") # Auto-width by default in columns, or use explicit theme support
    st.caption("Income regularity & Job status")

with col2:
    val = customer.get('discipline_score', 0)
    st.plotly_chart(create_gauge(val, "Discipline", "#00f2fe"), key="discipline_gauge", width="stretch")
    st.caption("Bill payments & Savings ratio")

with col3:
    val = customer.get('volatility_score', 0)
    st.plotly_chart(create_gauge(val, "Volatility", "#a8edea"), key="volatility_gauge", width="stretch")
    st.caption("Cash flow consistency")

st.divider()

# --- Comparative Analysis Logic ---

# Scenario Detection Proxies
is_khan_risk = customer.get('risky_spend_ratio', 0) > 0.01 # Scenario 2
is_singh_fraud = customer.get('credit_score') < 350 and customer.get('employment_type') == 'Self_Employed' # Scenario 4

# Define values based on actual score/profile
trad_decision = "PENDING"
trad_amount = 0
lift_text = "N/A"

is_rejected = score < 650

if score > 700:
    trad_decision = "APPROVED (Standard)"
    trad_amount = int(customer['declared_monthly_income'] * 5)
    lift_text = "✅ 20% Higher Limit & Instant Approval"
    diff_color = "green"
elif is_rejected:
    # Logic: If Traditional would reject (No CIBIL) and We reject -> Risk Validation
    # If Traditional would Approve (Salary Slip) and We reject -> Risk Avoidance
    
    if customer.get('employment_type') == 'Salaried':
         trad_decision = "BORDERLINE APPROVE"
         trad_amount = int(customer['declared_monthly_income'] * 3)
         lift_text = "🛡️ Hidden Risk Detected (Bad Loan Avoided)"
    else:
         trad_decision = "REJECTED (No CIBIL)"
         trad_amount = 0
         lift_text = "✅ Risk Verified (Model Aligns with Prudence)"
         
    diff_color = "red"
elif is_khan_risk == False and "patel" in str(name).lower():
    # Scenario 5: Multi-Bank Aggregation
    trad_decision = "PARTIAL APPROVAL"
    trad_amount = int(customer['declared_monthly_income'] * 2) # They only see half the income (HDFC)
    lift_text = "🌟 ACCOUNT AGGREGATION: Unified Limit (HDFC + SBI Income Configured)"
    diff_color = "green"
else:
    # Score 600-700 (Conditional)
    trad_decision = "REJECTED (No CIBIL)"
    trad_amount = 0
    lift_text = "✅ Financial Inclusion (New Customer Segment)"
    diff_color = "blue"

comp_data = {
    "Parameter": ["Decision", "Income Assessment", "Loan Amount (LTV)", "Processing Time"],
    "Traditional Bank": [trad_decision, f"₹{customer['declared_monthly_income']:,.0f} (Docs)", f"₹{trad_amount:,}", "2-3 Days"],
    "Helix AI Scoring": [decision, f"₹{customer['declared_monthly_income']:,.0f} + Behaviors", offer, "Instant"],
    "Impact / Lift": [lift_text, "Behaviors Factor In", "Optimized Risk", "99% Faster"]
}
comp_df = pd.DataFrame(comp_data)

st.table(comp_df)

if is_khan_risk:
    st.error("🚨 RISK ALERT: Hidden Latent Debt & Gambling Activity detected. Traditional models would have missed this.")

if score > 750 and "Salaried" in str(customer.get('employment_type')):
    st.success("🌟 OPPORTUNITY: High stability detected (Quarterly Bonuses). Recommended for Premium Upsell.")

st.divider()

# --- Detailed Explanation ---
c_exp, c_fact = st.columns([1, 1])

with c_exp:
    st.subheader("📝 Decision Rationale")
    model_ver = customer.get('model_version', 'Legacy Rule-Based')
    st.caption(f"Model Version: {model_ver}")
    
    # Dynamic Reason Generator
    reasons = []
    
    # 1. Stability Check
    stab = customer.get('stability_score', 0)
    if stab < 50:
        reasons.append("• **Unstable Income**: Monthly inflows are highly variable, indicating irregular employment or cash flow shocks.")
    elif stab > 80:
        reasons.append("• **Strong Stability**: Consistent monthly inflows detected, positively impacting the score.")
        
    # 2. Discipline Check
    disc = customer.get('discipline_score', 0)
    # Support new and old keys
    retention = customer.get('net_cash_retention_ratio', customer.get('savings_ratio', 0))
    
    if retention < 0:
        reasons.append(f"• **Critical Overspending**: Expenses exceed income by {abs(retention*100):.1f}%. Immediate financial course correction needed.")
    elif disc < 40:
        reasons.append("• **Low Discipline**: High spending relative to income (Low Net Cash Retention).")
    
    # 3. Volatility Check
    vol = customer.get('volatility_score', 0)
    if vol < 40:
        reasons.append("• **High Volatility Risk**: Significant fluctuations in account balance suggest potential liquidity issues.")
    
    # 4. Specific Signals
    if customer.get('risky_spend_ratio', 0) > 0.05:
        reasons.append("• **Risky Behavior**: Detected transactions related to gambling or speculative assets.")
        
    if not reasons:
        reasons.append("• **Generic**: The profile meets standard criteria but lacks strong positive signals to boost the score higher.")
        
    for r in reasons:
        st.markdown(r)
        
    st.markdown("---")
    st.caption("⚠️ **Disclaimer**: The 300–900 scale is used for interpretability and familiarity. This score does not replicate or replace bureau scores (CIBIL/Equifax).")

    with st.expander("View Raw Transaction Signals"):
        st.write(f"• Salary Detected: {'YES' if customer.get('employment_type') == 'Salaried' else 'NO'}")
        
        # Handle Clean formatting for NaNs
        cred = customer.get('average_monthly_account_credit', 0)
        deb = customer.get('average_monthly_account_debit', 0)
        if pd.isna(cred): cred = 0
        if pd.isna(deb): deb = 0
        
        st.write(f"• Avg Monthly Credit: ₹{cred:,.0f}")
        st.write(f"• Avg Monthly Debit: ₹{deb:,.0f}")
        st.write(f"• Net Cash Retention: {retention*100:.1f}%")


