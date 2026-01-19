import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide", page_title="Helix: Customers", page_icon="👥")

# Removed hardcoded Light Theme CSS to respect global config.toml

# --- Logic ---

# @st.cache_data  <-- Removing cache to ensure real-time updates
def load_data():
    try:
        # Load from the scored data artifact
        # construct path dynamically to be safe
        import os
        project_root = os.getcwd()
        data_path = os.path.join(project_root, "scored_data.csv")
        
        if not os.path.exists(data_path):
             raise ValueError("File not found")
             
        df = pd.read_csv(data_path)
        if df.empty:
            raise ValueError("Empty CSV")
        sorted_df = df.sort_values(by='credit_score', ascending=False)
        return sorted_df
    except Exception:
        # Generate MOCK DATA for Demo
        mock_data = [
            {'customer_id': 'CUST-001', 'customer_name': 'Rajesh Kumar', 'employment_type': 'Salaried', 'declared_monthly_income': 85000, 'risk_band': 'Low Risk', 'credit_score': 780},
            {'customer_id': 'CUST-002', 'customer_name': 'Sneha Gupta', 'employment_type': 'Self_Employed', 'declared_monthly_income': 120000, 'risk_band': 'Low Risk', 'credit_score': 765},
        ]
        return pd.DataFrame(mock_data)

df = load_data()

# --- Header ---
c1, c2 = st.columns([3, 1])
with c1:
    st.title("Customers")
    st.caption("Manage scoring candidates and applications.")
with c2:
    if st.button("+ New Application", type="primary"):
        st.switch_page("pages/3_New_Application.py")

st.divider()

# --- Customer Filter ---
search = st.text_input("Search by Name or ID", placeholder="Search...")

if not df.empty:
    # 1. Backfill Names if missing
    if 'customer_name' not in df.columns:
        df['customer_name'] = np.nan
        
    demo_names = [
        "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", 
        "Ishaan", "Diya", "Saanvi", "Anya", "Aadhya", "Pari", "Ananya", "Myra", "Rohan", 
        "Vikram", "Suresh", "Priya", "Rahul", "Neha", "Amit", "Sneha", "Rajesh", "Pooja", 
        "Ankit", "Meera", "Varun", "Karan", "Simran", "Deepak", "Kavita"
    ]
    def assign_demo_name(row):
        val = row['customer_name']
        if pd.isna(val) or str(val).lower() in ['nan', 'n/a', 'none']:
            idx = hash(str(row['customer_id'])) % len(demo_names)
            return demo_names[idx]
        return val

    df['customer_name'] = df.apply(assign_demo_name, axis=1)

    # 2. Filter
    if search:
        mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
        filtered_df = df[mask].copy()
    else:
        filtered_df = df.copy()
        
    # Styling the dataframe (Native Streamlit Table handles Dark Mode well)
    st.dataframe(
        filtered_df[['customer_id', 'customer_name', 'employment_type', 'declared_monthly_income', 'risk_band', 'credit_score']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "customer_id": "ID",
            "customer_name": "Applicant Name",
            "employment_type": "Employment",
            "declared_monthly_income": st.column_config.NumberColumn("Income", format="₹%d"),
            "risk_band": "Risk Band",
            "credit_score": "Score"
        }
    )
    
    st.write("### Actions")
    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        # Display Name in dropdown for easier selection
        # FIX: Ensure everything is string before adding
        filtered_df['display_label'] = filtered_df['customer_name'].astype(str) + " (" + filtered_df['customer_id'].astype(str) + ")"
        
        # We need to map back to ID
        label_to_id = dict(zip(filtered_df['display_label'], filtered_df['customer_id']))
        
        selected_label = st.selectbox("Select Customer to View Scorecard", filtered_df['display_label'].unique())
        selected_id = label_to_id.get(selected_label)
    with col_btn:
        st.write("") # Spacer
        st.write("") # Spacer
        if st.button("View Scorecard →"):
            st.session_state['selected_customer_id'] = selected_id
            st.switch_page("pages/4_Scorecard.py")

else:
    st.info("No customer data found. Start a new application!")
