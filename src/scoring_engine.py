import pandas as pd
import numpy as np
import joblib
import os

class LabelGenerator:
    """
    Generates Ground Truth Labels (Logic-Based).
    Used ONLY for training the ML model.
    Never used for inference in production (unless model is missing).
    """
    def generate_label(self, signals):
        """
        Calculates a rule-based training target (y).
        """
        # 1. Stability (Income Regularity) - 40%
        # Low volatility is good.
        volatility = signals.get('income_volatility', 1.0)
        if volatility < 0.1: stability = 100
        elif volatility < 0.3: stability = 80
        elif volatility < 0.6: stability = 50
        else: stability = 20
        
        # 2. Discipline (Savings & Bills) - 30%
        # Use new signal name: net_cash_retention_ratio
        retention = signals.get('net_cash_retention_ratio', 0)
        missed_bills = signals.get('bill_miss_count', 0)
        
        discipline = 50 # Base
        if retention > 0.2: discipline += 30
        elif retention > 0.1: discipline += 10
        elif retention < 0: discipline -= 30 # PENALTY for Overspending
        
        if missed_bills > 0: discipline -= 20 * missed_bills
        discipline = max(0, min(100, discipline))
        
        # 3. Volatility (Cash Flow Stability) - 30%
        # We use the new signal 'cash_surplus_stability'
        surplus_stab = signals.get('cash_surplus_stability', 0)
        # Higher is better
        if surplus_stab > 2.0: vol_score = 90
        elif surplus_stab > 1.0: vol_score = 70
        elif surplus_stab > 0.5: vol_score = 50
        else: vol_score = 30
        
        # Final Rule-Based Score (300-900 Scale for target)
        weighted_score = (stability * 0.4) + (discipline * 0.3) + (vol_score * 0.3)
        final_score = 300 + (weighted_score / 100) * 600
        
        # Penalize for Risky Spend heavily (Override)
        risky_spend = signals.get('risky_spend_ratio', 0)
        if risky_spend > 0.1:
            final_score -= 100
        if risky_spend > 0.3:
            final_score -= 200
            
        return int(final_score), {
            "stability_label": stability,
            "discipline_label": discipline,
            "volatility_label": vol_score
        }

class MLScorer:
    """
    Predicts Credit Score using a trained ML Model.
    Input: Feature Vector (X)
    Output: Predicted Score (y_pred)
    """
    def __init__(self, model_path="model_v1.pkl"):
        self.model = None
        current_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(current_dir, model_path)
        
        if os.path.exists(full_path):
            try:
                self.model = joblib.load(full_path)
            except:
                print("Warning: Could not load ML model.")
        
    def predict_score(self, signals):
        """
        Args:
            signals (dict): Output from SignalExtractor
            
        Returns:
            dict: {
                'predicted_score': int,
                'risk_band': str,
                'model_used': bool
            }
        """
        # Prepare Feature Vector (Must match training order in model_trainer.py)
        # 1. Avg Inflow
        # 2. Income Volatility
        # 3. Avg Outflow
        # 4. Net Cash Retention (formerly Savings)
        # 5. Cash Surplus Stability
        # 6. Bill Miss Count
        # 7. Risky Spend Ratio
        
        features = [
            signals.get('avg_monthly_inflow', 0),
            signals.get('income_volatility', 1.0),
            signals.get('avg_monthly_outflow', 0),
            signals.get('net_cash_retention_ratio', 0),
            signals.get('cash_surplus_stability', 0),
            signals.get('bill_miss_count', 0),
            signals.get('risky_spend_ratio', 0)
        ]
        
        score = 600 # Fallback
        model_used = False
        
        if self.model:
            # Predict
            try:
                score = self.model.predict([features])[0]
                model_used = True
            except Exception as e:
                print(f"Prediction Error: {e}")
                
        else:
            # Fallback to LabelGenerator (Simulate logic if no model)
            lg = LabelGenerator()
            score, _ = lg.generate_label(signals)
            model_used = False
            
        # Clip to valid range
        score = max(300, min(900, score))
            
        return {
            'credit_score': int(score),
            'risk_band': self._get_risk_band(score),
            'model_used': model_used
        }

    def _get_risk_band(self, score):
        if score >= 750: return "Low Risk"
        elif score >= 650: return "Medium Risk"
        else: return "High Risk"
