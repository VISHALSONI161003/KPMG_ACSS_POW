import shap
import pandas as pd
import numpy as np
import xgboost as xgb

class Explainer:
    def __init__(self, data_path: str):
        try:
            self.df = pd.read_csv(data_path)
            # Ensure basic numeric conversions
            cols_to_numeric = ['credit_score', 'income_volatility', 'discipline_score']
            for c in cols_to_numeric:
                if c in self.df.columns:
                    self.df[c] = pd.to_numeric(self.df[c], errors='coerce')
        except:
            self.df = pd.DataFrame()
            
        self.model = None
        self.explainer = None
        self.shap_values = None
        
    def train_surrogate_model(self):
        """
        Trains a surrogate XGBoost model to interpret the rule-based scores.
        """
        if self.df.empty:
            return None, None
            
        # Features used in scoring (union of 3-pillar inputs)
        features = [
            'affordability_ratio', 'income_volatility', 'declared_monthly_income', 
            'txn_count_6m', 'missed_utility_bill_count', 'flag_salary_detected',
            'average_monthly_account_credit', 'average_monthly_account_debit'
        ]
        
        # Filter to available features
        available_feats = [f for f in features if f in self.df.columns]
        
        if not available_feats or 'credit_score' not in self.df.columns:
            return None, None
            
        X = self.df[available_feats].copy().fillna(0)
        y = self.df['credit_score'].fillna(300)
        
        # Train
        self.model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=50)
        self.model.fit(X, y)
        
        self.explainer = shap.Explainer(self.model)
        self.shap_values = self.explainer(X)
        self.feature_names = available_feats
        
        return self.explainer, self.shap_values

    def get_explanation_for_customer(self, customer_id):
        """
        Returns explanation for a specific customer.
        """
        if self.explainer is None:
            self.train_surrogate_model()
            
        if self.explainer is None:
            return None
            
        try:
            # Find index
            # Support both mock IDs and real IDs by string matching
            mask = self.df['customer_id'].astype(str) == str(customer_id)
            if not mask.any():
                return None
                
            idx = mask.idxmax() # Get first match
            
            shap_vals = self.shap_values[idx]
            
            contributions = []
            for name, value, data_val in zip(self.feature_names, shap_vals.values, shap_vals.data):
                contributions.append({
                    "feature": name,
                    "impact": float(value),
                    "value": float(data_val)
                })
                
            contributions.sort(key=lambda x: abs(x['impact']), reverse=True)
            
            return {
                "base_value": float(shap_vals.base_values),
                "contributions": contributions
            }
        except Exception as e:
            return None

if __name__ == "__main__":
    pass
