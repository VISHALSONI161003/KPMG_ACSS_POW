
import sys
import os
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.getcwd())

from src.synthetic_generator import SyntheticGenerator
from src.signal_extractor import SignalExtractor
from src.scoring_engine import MLScorer, LabelGenerator

def regenerate_population(n=50):
    print(f"Regenerating data for {n} users (Scenario-Based)...")
    
    gen = SyntheticGenerator()
    extractor = SignalExtractor()
    scorer = MLScorer()
    lg = LabelGenerator()
    
    all_scored_records = []
    
    # Pools for random generation
    first_names = ["Aarav", "Vihaan", "Aditya", "Sai", "Arjun", "Reyansh", "Vivaan", "Krishna", "Ishaan", 
                   "Diya", "Ananya", "Pari", "Myra", "Saanvi", "Aadhya", "Kiara", "Riya", "Sneha", "Pooja", "Neha"]
    
    # Scenario Definitions (Weighted)
    # 0 = Verma (Approved/Stable) - 35%
    # 1 = Khan (Rejected/High Risk) - 25%
    # 2 = Devi (NTC/Proprietor) - 25%
    # 3 = Singh (Fraud) - 15%
    
    for i in range(n):
        scenario_idx = np.random.choice([0, 1, 2, 3], p=[0.35, 0.25, 0.25, 0.15])
        first_name = np.random.choice(first_names)
        
        if scenario_idx == 0:
            # Scenario 1: Mr. Verma (Software Developer - Safe)
            surname = "Verma"
            emp_type = "Salaried"
            income = np.random.randint(60000, 150000)
            
        elif scenario_idx == 1:
            # Scenario 2: Mr. Khan (Sales Executive - Risky/Gambling)
            surname = "Khan"
            emp_type = "Gig" if np.random.random() > 0.5 else "Salaried" # Mixed
            income = np.random.randint(35000, 55000)
            
        elif scenario_idx == 2:
            # Scenario 3: Mrs. Devi (Proprietor - NTC but Good)
            surname = "Devi"
            emp_type = "Self_Employed"
            income = np.random.randint(20000, 45000)
            
        elif scenario_idx == 3:
            # Scenario 4: Mr. Singh (Fraud - New SIM/Emulator)
            surname = "Singh"
            emp_type = "Gig"
            income = np.random.randint(40000, 80000)
            
        name = f"{first_name} {surname}"
        print(f"[{i+1}/{n}] Processing {name} ({emp_type})...")
        
        # 1. Profile
        profile = gen.generate_profile(name, emp_type, income)
        
        # 2. Transactions
        txns_df = gen.generate_transactions(profile['customer_id'], emp_type, income, name=name)
        silent_data = gen.generate_silent_data(profile['customer_id'], name=name)
        
        # 3. Signals
        signals = extractor.extract_signals(txns_df, profile)
        
        # 4. Score
        prediction = scorer.predict_score(signals)
        _, subscores = lg.generate_label(signals)
        
        # 5. Record
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
        
        record['stability_score'] = subscores['stability_label']
        record['discipline_score'] = subscores['discipline_label']
        record['volatility_score'] = subscores['volatility_label']
        
        # Add to list
        all_scored_records.append(record)
        
    # Save to CSV
    df = pd.DataFrame(all_scored_records)
    df.to_csv("scored_data.csv", index=False)
    print(f"Successfully saved {len(df)} records to scored_data.csv")

if __name__ == "__main__":
    regenerate_population(50)
