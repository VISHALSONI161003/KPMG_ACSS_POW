
import sys
import os
import pandas as pd
import json

sys.path.append(os.getcwd())

from src.synthetic_generator import SyntheticGenerator
from src.signal_extractor import SignalExtractor

def test_new_app_integration():
    print("Testing New Application Integration...")
    
    # 1. Simulate what valid inputs look like
    name = "Test User NewApp"
    emp_type = "Salaried"
    income = 60000
    
    # 2. Run the pipeline (copied from 3_New_Application.py logic)
    gen = SyntheticGenerator()
    profile = gen.generate_profile(name, emp_type, income)
    txns_df = gen.generate_transactions(profile['customer_id'], emp_type, income, name=name)
    
    extractor = SignalExtractor()
    signals = extractor.extract_signals(txns_df, profile)
    
    # 3. Verify Keys present
    keys = signals.keys()
    print("Generated Keys:", keys)
    
    if 'spending_breakdown' in keys and 'lifestyle_scores' in keys:
        print("✅ SUCCESS: New Application flow correctly generates Payment & Lifestyle data.")
        
        # Check content
        bd = json.loads(signals['spending_breakdown'])
        ls = json.loads(signals['lifestyle_scores'])
        
        print("Breakdown Sample:", list(bd.keys()))
        print("Lifestyle Sample:", ls)
        
        if len(bd) > 0 and 'essential_ratio' in ls:
             print("✅ Data content is valid.")
        else:
             print("❌ Data content empty or invalid.")
    else:
        print("❌ FAILURE: Missing new keys in output.")

if __name__ == "__main__":
    test_new_app_integration()
