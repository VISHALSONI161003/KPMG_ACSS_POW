import pandas as pd
import numpy as np

class SignalExtractor:
    """
    Transforms raw transaction data into interpretable financial signals.
    These signals serve as the features (X) for the ML model.
    """
    
    def _categorize_transaction(self, description):
        description = description.lower()
        if any(x in description for x in ['swiggy', 'zomato', 'restaurant', 'cafe', 'food', 'mcdonalds', 'dominos', 'dining']):
            return 'Dining & Food'
        elif any(x in description for x in ['uber', 'ola', 'fuel', 'petrol', 'parking', 'toll', 'irctc', 'flight', 'airline', 'travel', 'cab']):
            return 'Travel & Commute'
        elif any(x in description for x in ['netflix', 'spotify', 'movie', 'cinema', 'bookmyshow', 'hotstar', 'prime', 'game', 'entertainment']):
            return 'Entertainment'
        elif any(x in description for x in ['amazon', 'flipkart', 'myntra', 'shopping', 'retail', 'store', 'zara', 'h&m']):
            return 'Shopping'
        elif any(x in description for x in ['grocery', 'supermarket', 'mart', 'bigbasket', 'blinkit', 'zepto']):
            return 'Groceries'
        elif any(x in description for x in ['bill', 'electricity', 'water', 'gas', 'broadband', 'jio', 'airtel', 'vi ', 'bsnl', 'utilities']):
            return 'Utilities'
        elif any(x in description for x in ['emi', 'loan', 'finance', 'insurance', 'premium', 'sip', 'mutual fund', 'zerodha']):
            return 'Financial Services'
        elif any(x in description for x in ['atm', 'withdrawal', 'cash']):
            return 'Cash Withdrawal'
        elif any(x in description for x in ['rent', 'maintenance']):
            return 'Housing'
        elif any(x in description for x in ['medical', 'pharmacy', 'doctor', 'hospital', 'medicine', 'drug']):
            return 'Health & Medical'
        else:
            return 'Others'

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
            
        # Prepare Trend Data for Visualizations (Last 6 Months)
        # Re-index to ensure all months are present (fill missing with 0)
        full_period = pd.period_range(start=transactions_df['month'].min(), end=transactions_df['month'].max(), freq='M')
        
        inflow_series = monthly_inflows.reindex(full_period, fill_value=0)
        outflow_series = monthly_outflows.reindex(full_period, fill_value=0)
        
        # Convert to list and ensure JSON serializable (float, not numpy type)
        inflow_trend = [float(x) for x in inflow_series.values]
        outflow_trend = [float(x) for x in outflow_series.values]

        # --- Payment Analysis & Lifestyle Scoring ---
        spending_breakdown = {}
        lifestyle_scores = {
            'stability_affinity': 0, 
            'digital_savviness': 0,
            'luxury_index': 0
        }
        
        if not debits.empty:
            # 1. Categorization
            debits = debits.copy()
            debits['category'] = debits['description'].apply(self._categorize_transaction)
            spending_breakdown = debits.groupby('category')['transaction_amount'].sum().astype(float).to_dict()
            
            # 2. Lifestyle Logic
            total_spend = debits['transaction_amount'].sum()
            if total_spend > 0:
                # Essential vs Discretionary
                essentials = ['Groceries', 'Utilities', 'Housing', 'Financial Services', 'Health & Medical']
                discretionary = ['Dining & Food', 'Entertainment', 'Shopping', 'Travel & Commute']
                
                essential_spend = debits[debits['category'].isin(essentials)]['transaction_amount'].sum()
                discretionary_spend = debits[debits['category'].isin(discretionary)]['transaction_amount'].sum()
                
                lifestyle_scores['essential_ratio'] = round(essential_spend / total_spend, 2)
                lifestyle_scores['discretionary_ratio'] = round(discretionary_spend / total_spend, 2)
                
                # Digital Savviness (UPI usage)
                upi_txns = debits[debits['description'].str.contains('UPI', case=False, na=False)].shape[0]
                total_txns = debits.shape[0]
                lifestyle_scores['digital_savviness'] = round((upi_txns / total_txns) * 100, 1) if total_txns > 0 else 0
                
        import json
        return {
            "customer_id": profile.get('customer_id'),
            "avg_monthly_inflow": avg_inflow,
            "income_volatility": income_volatility,
            "avg_monthly_outflow": avg_outflow,
            "net_cash_retention_ratio": net_cash_retention_ratio,
            "cash_surplus_stability": cash_surplus_stability,
            "bill_miss_count": bill_miss_count,
            "risky_spend_ratio": risky_spend_ratio,
            "inflow_trend": str(inflow_trend),   
            "outflow_trend": str(outflow_trend),
            "spending_breakdown": json.dumps(spending_breakdown), # JSON String for CSV
            "lifestyle_scores": json.dumps(lifestyle_scores)      # JSON String for CSV
        }

    def _get_empty_signals(self):
        return {
            "avg_monthly_inflow": 0, "income_volatility": 1.0, 
            "avg_monthly_outflow": 0, "net_cash_retention_ratio": 0,
            "cash_surplus_stability": 0, "bill_miss_count": 0,
            "risky_spend_ratio": 0
        }
