import pandas as pd
import numpy as np

class SignalExtractor:
    """
    Transforms raw transaction data into interpretable financial signals.
    These signals serve as the features (X) for the ML model.
    """
    
    def extract_signals(self, transactions_df, profile):
        """
        Args:
            transactions_df (pd.DataFrame): Raw transaction ledger
            profile (dict): Customer profile metadata (income, etc.)
            
        Returns:
            dict: Financial signals (Auditable & Interpretable)
        """
        if transactions_df.empty:
            return self._get_empty_signals()
            
        # Ensure date format
        transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])
        transactions_df['month'] = transactions_df['transaction_date'].dt.to_period('M')
        
        # Split Streams
        credits = transactions_df[transactions_df['transaction_direction'] == 'CREDIT']
        debits = transactions_df[transactions_df['transaction_direction'] == 'DEBIT']
        
        # 1. Income Analysis (Stability)
        if not credits.empty:
            monthly_inflows = credits.groupby('month')['transaction_amount'].sum()
            avg_inflow = monthly_inflows.mean()
            std_inflow = monthly_inflows.std() if len(monthly_inflows) > 1 else 0
            
            # CV (Coefficient of Variation) - Lower is better
            income_volatility = std_inflow / avg_inflow if avg_inflow > 0 else 1.0
        else:
            avg_inflow = 0
            income_volatility = 1.0
            monthly_inflows = pd.Series()
            
        # 2. Spending Hygiene
        monthly_outflows = debits.groupby('month')['transaction_amount'].sum()
        avg_outflow = monthly_outflows.mean() if not monthly_outflows.empty else 0
        
        # 3. Net Cash Retention Ratio (formerly Affordability/Savings)
        # Logic: (Inflow - Outflow) / Inflow
        net_cash_retention_ratio = 0.0
        if avg_inflow > 0:
            net_cash_retention_ratio = (avg_inflow - avg_outflow) / avg_inflow
            
        # 4. Cash Surplus Stability
        # Logic: Statistical stability of end-of-month surplus
        all_months = transactions_df['month'].unique()
        surpluses = []
        for m in all_months:
            inc = monthly_inflows.get(m, 0) if not credits.empty else 0
            out = monthly_outflows.get(m, 0) if not debits.empty else 0
            surpluses.append(inc - out)
            
        surpluses = np.array(surpluses)
        
        if len(surpluses) > 1 and np.mean(surpluses) > 0:
            # We use 1 / CV of Surplus as a proxy for stability, capped for normalization
            surplus_mean = np.mean(surpluses)
            surplus_std = np.std(surpluses)
            if surplus_std > 0:
                # Higher is better
                cash_surplus_stability = max(0, 1 - (surplus_std / surplus_mean)) 
            else:
                cash_surplus_stability = 1.0 # Perfectly stable
        else:
            cash_surplus_stability = 0.0 # Unstable or negative flow

        # 5. Bill Miss Count
        # Keywords: bounce, return, penalty, late, decline
        missed_keywords = ['bounce', 'return', 'penalty', 'late', 'decline']
        bill_miss_count = transactions_df[
            transactions_df['description'].str.contains('|'.join(missed_keywords), case=False, na=False) |
            transactions_df['transaction_category'].str.contains('Penalty', case=False, na=False)
        ].shape[0]

        # 6. Risky Spend Ratio
        # Keywords: Dream11, Bet365, Crypto, BNPL, etc.
        risky_keywords = ['Dream11', 'Gaming_Wallet', 'Crypto', 'Betting', 'Bet365', 'Rummy', 
                          'Poker', 'Binance', 'Coinbase', 'Uni.Cards', 'Slice', 'Lazypay', 'Simpl']
        
        risky_txns = debits[debits['description'].str.contains('|'.join(risky_keywords), case=False, na=False)]
        risky_spend_vol = risky_txns['transaction_amount'].sum()
        
        risky_spend_ratio = 0.0
        if avg_outflow > 0:
            risky_spend_ratio = risky_spend_vol / (avg_outflow * 6) # Ratio against total outflow
            
        # Return strict Feature Vector
        return {
            "customer_id": profile.get('customer_id'),
            "avg_monthly_inflow": avg_inflow,
            "income_volatility": income_volatility,
            "avg_monthly_outflow": avg_outflow,
            "net_cash_retention_ratio": net_cash_retention_ratio,
            "cash_surplus_stability": cash_surplus_stability,
            "bill_miss_count": bill_miss_count,
            "risky_spend_ratio": risky_spend_ratio
        }

    def _get_empty_signals(self):
        return {
            "avg_monthly_inflow": 0, "income_volatility": 1.0, 
            "avg_monthly_outflow": 0, "net_cash_retention_ratio": 0,
            "cash_surplus_stability": 0, "bill_miss_count": 0,
            "risky_spend_ratio": 0
        }
