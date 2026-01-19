import pandas as pd
import numpy as np
import joblib
import os
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from synthetic_generator import SyntheticGenerator
from signal_extractor import SignalExtractor
from scoring_engine import LabelGenerator

def train_model():
    print("🚀 Starting Model Training Pipeline...")
    
    # 1. Generate Synthetic Training Data
    print("generating synthetic applicants...")
    gen = SyntheticGenerator()
    extractor = SignalExtractor()
    labeler = LabelGenerator()
    
    X = []
    y = []
    
    # Mix of profiles
    profiles = [
        ("Salaried", 80000), 
        ("Salaried", 30000), 
        ("Gig", 60000),
        ("Gig", 20000),
        ("Self_Employed", 150000)
    ]
    
    for _ in range(200): # 200 * 5 = 1000 samples
        for emp_type, base_income in profiles:
            # Add some variance
            income = base_income * np.random.uniform(0.8, 1.2)
            
            # Generate Raw Data
            profile = gen.generate_profile("Train User", emp_type, income)
            txns = gen.generate_transactions(profile['customer_id'], emp_type, income)
            
            # Extract Signals (Features)
            signals = extractor.extract_signals(txns, profile)
            
            # Generate Label (Ground Truth)
            score, _ = labeler.generate_label(signals)
            
            # Feature Vector (Must match MLScorer in scoring_engine.py)
            feat_vec = [
                signals.get('avg_monthly_inflow', 0),
                signals.get('income_volatility', 1.0),
                signals.get('avg_monthly_outflow', 0),
                signals.get('net_cash_retention_ratio', 0),
                signals.get('cash_surplus_stability', 0),
                signals.get('bill_miss_count', 0),
                signals.get('risky_spend_ratio', 0)
            ]
            
            X.append(feat_vec)
            y.append(score)
            
    # 2. Train Model
    print(f"Training on {len(X)} samples...")
    # Using Linear Regression for transparency in this POC, or RF for better fit
    model = LinearRegression() 
    model.fit(X, y)
    
    score_r2 = model.score(X, y)
    print(f"✅ Model Trained. R2 Score: {score_r2:.4f}")
    
    # 3. Save Artifact
    model_path = os.path.join(os.path.dirname(__file__), "model_v1.pkl")
    joblib.dump(model, model_path)
    print(f"💾 Model saved to: {model_path}")

if __name__ == "__main__":
    train_model()
