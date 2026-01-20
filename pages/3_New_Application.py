import streamlit as st
import sys
import os
import pandas as pd
import time

# --- Robust Import Setup ---
def find_project_root(current_path, marker='src'):
    """Recursively find the directory containing the marker folder."""
    root = current_path
    for _ in range(5): # Limit depth
        if os.path.exists(os.path.join(root, marker)):
            return root
        parent = os.path.dirname(root)
        if parent == root: # Filesystem root
            break
        root = parent
    return None

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = find_project_root(current_dir)

if project_root:
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
else:
    # Fallback: assume CWD is root (common in Streamlit)
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())

import importlib
try:
    import src.synthetic_generator
    import src.scoring_engine
    import src.signal_extractor # Pre-load to avoid partial init
    
    # Force Reload to pick up latest code changes (Fix for AttributeError on new methods)
    importlib.reload(src.synthetic_generator)
    importlib.reload(src.scoring_engine)
    
    from src.synthetic_generator import SyntheticGenerator
    from src.scoring_engine import MLScorer
except ImportError as e:
    st.error(f"System Error: Could not load backend modules.")
    st.code(f"Error: {e}\nCWD: {os.getcwd()}\nSys Path: {sys.path[:3]}\nProject Root: {project_root}")
    st.stop()

st.set_page_config(layout="wide", page_title="Helix: New App", page_icon="📝")

st.title("New Customer Application")
st.markdown("Enter customer details to generate a synthetic profile and score.", help="This generates a realistic 6-month transaction history.")

# --- Form (Native Streamlit Theme) ---
# --- Form (Native Streamlit Theme) ---
st.subheader("Personal Details")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Full Name", "Alex Rivera")
    email = st.text_input("Email", "alex.rivera@example.com")
    age = st.number_input("Age", 18, 100, 30)

with col2:
    phone = st.text_input("Phone", "+91 98765 43210")
    emp_type = st.selectbox("Employment Status", ["Salaried", "Self_Employed", "Gig"])
    income = st.number_input("Declared Monthly Income (₹)", 10000, 1000000, 45000, step=5000)

address = st.text_area("Address", "123, Tech Park, Bangalore")

st.markdown("---")
st.subheader("📄 Document Verification")
st.caption("Upload required documents to process your application.")

uploaded_files = {}
missing_docs = []

if emp_type == "Salaried":
    req_docs = ["PAN Card", "Aadhaar Card", "Salary Slips (Last 3 Months)", "Bank Statement (Last 6 Months)"]
else:
    req_docs = ["PAN Card", "Aadhaar Card", "ITR (Last 2 Years)", "Bank Statement (Last 12 Months)", "GST/Udyam Reg"]
    
for doc in req_docs:
    f = st.file_uploader(f"Upload {doc}", type=['pdf', 'jpg', 'png'], key=doc)
    if f is not None:
        uploaded_files[doc] = f
    else:
        missing_docs.append(doc)
        
st.markdown("---")
submitted = st.button("🚀 Submit Application", type="primary", use_container_width=True)

if submitted:
    if missing_docs:
        st.error(f"⚠️ Please upload all required documents: {', '.join(missing_docs)}")
        st.stop()
        
    status_text = st.empty()
    bar = st.progress(0)
    
    try:
        # 1. Generate Profile
        status_text.text("Generating digital footprint...")
        bar.progress(10)
        gen = SyntheticGenerator()
        profile = gen.generate_profile(name, emp_type, income)
        
        # 2. Generate Transactions & Silent Data
        status_text.text("Simulating banking & device history...")
        bar.progress(30)
        txns_df = gen.generate_transactions(profile['customer_id'], emp_type, income, name=name)
        silent_data = gen.generate_silent_data(profile['customer_id'], name=name)
        
        # 3. Hybrid ML Pipeline
        status_text.text("Extracting behavioral signals...")
        bar.progress(50)
        
        # A. Signal Extraction
        from src.signal_extractor import SignalExtractor
        extractor = SignalExtractor()
        signals = extractor.extract_signals(txns_df, profile)
        
        # B. ML Scoring
        status_text.text("Running ML prediction model...")
        bar.progress(70)
        
        from src.scoring_engine import MLScorer
        scorer = MLScorer() # Loads model_v1.pkl
        prediction = scorer.predict_score(signals)
        
        final_score = prediction['credit_score']
        risk_band = prediction['risk_band']
        
        # 4. Save/Append
        status_text.text("Finalizing profile...")
        bar.progress(90)
        
        # Create Flattened Record for CSV (Signals + Score)
        record = signals.copy()
        
        # Map Signals to Schema expected by Scorecard/UI
        record['average_monthly_account_credit'] = signals.get('avg_monthly_inflow', 0)
        record['average_monthly_account_debit'] = signals.get('avg_monthly_outflow', 0)
        record['txn_count_6m'] = signals.get('total_txn_count', 0)
        
        record['customer_id'] = profile['customer_id']
        record['customer_name'] = profile['customer_name'] # Added Name Persistence
        record['employment_type'] = profile['employment_type']
        record['declared_monthly_income'] = profile['declared_monthly_income']
        record['city_tier'] = profile['city_tier']
        record['credit_score'] = final_score
        record['risk_band'] = risk_band
        record['model_version'] = "v1_hybrid"
        
        # Merge Silent Data
        record.update(silent_data)
        # Save Verified Docs for Scorecard Logic Display
        record['verified_documents'] = str(list(uploaded_files.keys()))
        record['docs_verified_flag'] = True
        
        # Add labels for UI backward compatibility if needed (Stability/Vol/Disc)
        # We can map back from signals or the LabelGenerator for "display" purposes if UI needs them
        # For now, let's generate them using LabelGenerator just for the Gauge Visualization
        from src.scoring_engine import LabelGenerator
        lg = LabelGenerator()
        _, subscores = lg.generate_label(signals)
        
        record['stability_score'] = subscores['stability_label']
        record['discipline_score'] = subscores['discipline_label']
        record['volatility_score'] = subscores['volatility_label']
        
        scored_row = pd.DataFrame([record])
        
        data_path = os.path.join(project_root if project_root else os.getcwd(), "scored_data.csv")
        if os.path.exists(data_path):
            existing_df = pd.read_csv(data_path)
            # Ensure columns match (concat handles this by adding NaNs if needed)
            updated_df = pd.concat([existing_df, scored_row], ignore_index=True)
        else:
            updated_df = scored_row
            
        updated_df.to_csv(data_path, index=False)
        
        bar.progress(100)
        status_text.text("Complete!")
        st.success(f"Application Approved! Customer ID: {profile['customer_id']}")
        
        # Set session state for the scorecard to pick up
        st.session_state['selected_customer_id'] = profile['customer_id']
        
        # Auto-redirect after short delay
        time.sleep(1)
        st.switch_page("pages/4_Scorecard.py")
            
    except Exception as e:
        status_text.text("Error occurred.")
        st.error(f"An error occurred: {e}")
        # Debug info
        import traceback
        st.code(traceback.format_exc())
