import streamlit as st

st.set_page_config(layout="wide", page_title="Helix: Home", page_icon="💳")

# --- Keep Session Alive ---
import sys
import os
# Ensure src is in path logic (though usually added by app.py, pages run in new contexts)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.session_utils import keep_alive
keep_alive()

# Custom CSS for Dark Landing Page
st.markdown("""
<style>
    /* Force specific styles for this page if possible, though Streamlit is global. 
       We will use a container with dark background to simulate the hero section. */
    
    .stApp {
        background-color: #0e1117;
        color: white;
    }
    
    .hero-container {
        padding: 50px 20px;
        text-align: center;
        background: linear-gradient(180deg, #1e2532 0%, #0e1117 100%);
        border-radius: 20px;
        margin-bottom: 30px;
    }
    
    .hero-title {
        font-family: 'Inter', sans-serif;
        font-size: 64px;
        font-weight: 700;
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }
    
    .hero-subtitle {
        font-size: 24px;
        color: #b0b8c4;
        max-width: 800px;
        margin: 0 auto 40px auto;
        line-height: 1.5;
    }
    
    .feature-card {
        background-color: #1a1d24;
        padding: 30px;
        border-radius: 15px;
        border: 1px solid #30333d;
        text-align: left;
        height: 100%;
        transition: transform 0.2s;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        border-color: #4facfe;
    }
    
    .cta-button {
        display: inline-block;
        background: linear-gradient(90deg, #2e3192 0%, #1bffff 100%);
        color: white;
        padding: 15px 40px;
        border-radius: 30px;
        font-size: 20px;
        font-weight: 600;
        text-decoration: none;
        margin-top: 20px;
    }

</style>
""", unsafe_allow_html=True)

# --- Hero Section ---
st.markdown('<div class="hero-container">', unsafe_allow_html=True)
st.markdown('<h1 class="hero-title">Thin-File Customer Scoring</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Unlock credit potential for the underserved. Our AI-driven engine analyzes alternative data to score customers with limited bureau history.</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Go to Dashboard →", type="primary", use_container_width=True):
        st.switch_page("pages/2_Customers.py")
st.markdown('</div>', unsafe_allow_html=True)

# --- Features Section ---
st.markdown("### Beyond the Credit Bureau")
st.markdown("Traditional scoring leaves millions behind. Our layered pipeline analyzes verified cash flows, spending behavior, and stability metrics to build a complete financial profile.")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="feature-card">
        <h3>👥 100% Coverage</h3>
        <p>Score anyone with a bank account, regardless of credit history.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="feature-card">
        <h3>🛡️ AI Verified</h3>
        <p>Robust fraud detection and income verification built-in.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="feature-card">
        <h3>⚡ Real-time</h3>
        <p>Get decision-ready scores in milliseconds.</p>
    </div>
    """, unsafe_allow_html=True)

# --- Pipeline Viz ---
st.markdown("### Scoring Pipeline")
st.info("Data Intake -> Feature Engineering -> Model Inference")
