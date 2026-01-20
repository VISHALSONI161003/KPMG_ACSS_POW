
import sys
import os
import pandas as pd
import json

# Add project root to path
sys.path.append(os.getcwd())

from src.synthetic_generator import SyntheticGenerator
from src.signal_extractor import SignalExtractor
from src.scoring_engine import MLScorer, LabelGenerator

def generate_demo_user():
    print("Generating POW Demo User (Generic)...")
    
    gen = SyntheticGenerator()
    extractor = SignalExtractor()
    scorer = MLScorer()
    lg = LabelGenerator()
    
    # 1. Profile - Priya (Generic User, no persona triggers)
    name = "Priya Gupta"
    emp_type = "Salaried"
    income = 125000
    
    profile = gen.generate_profile(name, emp_type, income)
    profile['customer_id'] = "POW-GENERIC-001" 
    
    # 2. Transactions (Generic loop in synthetic_generator will run)
    txns_df = gen.generate_transactions(profile['customer_id'], emp_type, income, name=name)
    silent_data = gen.generate_silent_data(profile['customer_id'], name=name)
    
    # 3. Extracts Signals (Triggering the NEW Logic)
    signals = extractor.extract_signals(txns_df, profile)
    
    # 4. Scoring
    prediction = scorer.predict_score(signals)
    _, subscores = lg.generate_label(signals)
    
    # 5. Assemble Record
    record = signals.copy()
    record.update(silent_data)
    
    record['customer_id'] = profile['customer_id']
    record['customer_name'] = profile['customer_name']
    record['employment_type'] = profile['employment_type']
    record['declared_monthly_income'] = profile['declared_monthly_income']
    record['city_tier'] = profile['city_tier']
    record['credit_score'] = prediction['credit_score']
    record['risk_band'] = prediction['risk_band']
    record['docs_verified_flag'] = True
    
    # UI Compat
    record['stability_score'] = subscores['stability_label']
    record['discipline_score'] = subscores['discipline_label']
    record['volatility_score'] = subscores['volatility_label']
    
    # Save
    df = pd.DataFrame([record])
    
    csv_path = "scored_data.csv"
    if os.path.exists(csv_path):
        existing = pd.read_csv(csv_path)
        # Remove old POW user if exists
        existing = existing[existing['customer_id'] != "POW-GENERIC-001"]
        updated = pd.concat([existing, df], ignore_index=True)
    else:
        updated = df
        
    updated.to_csv(csv_path, index=False)
    print(f"Success! Generated user {name} (ID: POW-GENERIC-001)")
    print("Signals keys:", signals.keys())
    
    # Check if 'Dining & Food' is in the breakdown
    import json
    bd = json.loads(signals['spending_breakdown'])
    print("Breakdown Keys found:", list(bd.keys()))

if __name__ == "__main__":
    generate_demo_user()
