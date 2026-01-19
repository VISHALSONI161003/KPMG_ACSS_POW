import pandas as pd
import sys
import os

# Ensure src is in path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from src.scoring_engine import CreditScorer

def migrate():
    print("Loading merged data...")
    try:
        # Try to load merged data first
        df = pd.read_csv("merged_full_data.csv")
    except FileNotFoundError:
        print("merged_full_data.csv not found. Trying scored_data.csv...")
        try:
            df = pd.read_csv("scored_data.csv")
            # If we load scored_data, we might have old score columns. 
            # CreditScorer.score_population handles dropping them usually, but being explicit is good.
        except FileNotFoundError:
            print("No data found to migrate.")
            return

    print(f"Data loaded: {len(df)} rows.")
    
    print("Applying new 3-Pillar Scoring Logic...")
    scorer = CreditScorer()
    new_scored_df = scorer.score_population(df)
    
    print("Saving to scored_data.csv...")
    new_scored_df.to_csv("scored_data.csv", index=False)
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
