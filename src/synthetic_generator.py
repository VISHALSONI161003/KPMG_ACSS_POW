import pandas as pd
import numpy as np
import uuid
from datetime import datetime, timedelta

class SyntheticGenerator:
    def __init__(self):
        self.categories = {
            'essential': ['Groceries', 'Utilities', 'Rent', 'Medical', 'Fuel'],
            'discretionary': ['Dining', 'Entertainment', 'Shopping', 'Travel'],
            'income': ['Salary', 'Freelance Payment', 'Transfer In', 'Interest']
        }

    def generate_profile(self, name, emp_type, income):
        """Creates a basic customer profile context"""
        return {
            'customer_id': str(uuid.uuid4())[:8],
            'customer_name': name,
            'employment_type': emp_type,
            'declared_monthly_income': float(income),
            'city_tier': np.random.choice(['Tier 1', 'Tier 2', 'Tier 3']),
            'application_date': datetime.now().strftime('%Y-%m-%d')
        }

        # Scenario-Based Logic
        is_verma = "verma" in customer_id.lower() or "verma" in str(emp_type).lower() # identifying by name passed in ID lookup or handle in caller
        # Actually generate_transactions receives ID. We need to pass name or handle inside based on ID lookups if we stored it? 
        # Simpler: The caller (New App) passes the ID which came from generate_profile. 
        # Let's trust the random generation for generic, but for the DEMO names, we need to know.
        # Hack: attributes like name aren't passed to generate_transactions. 
        # Fix: We will rely on the caller passing a 'scenario_flag' or we just infer from income/type or random. 
        # Better: Update generate_transactions signature or use the ID to store a flag in a global/class dict? No, stateless.
        # Let's check if the caller can pass the name.
        
        # ACTUALLY, I will check the 'customer_id' string. 
        # In 'generate_profile', I'll embed the name into the ID or just rely on the 'New Application' passing the name to 'generate_transactions' which I need to update the signature for.
        
        # Let's update the signature to accept 'name' as well for scenario injection.
    
    def generate_transactions(self, customer_id, emp_type, income, name=""):
        """
        Generates 6 months of raw transaction ledger data.
        Uses predefined behavioral personas for demo simulation only.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)
        
        txns = []
        current_date = start_date
        
        # Predefined behavioral personas for demo simulation
        name_lower = name.lower()
        is_sc1_verma = "verma" in name_lower
        is_sc2_khan = "khan" in name_lower
        is_sc3_devi = "devi" in name_lower
        
        # Scenario 4: Fraud/Ghost (Singh)
        is_sc4_singh = "singh" in name_lower
        
        # Scenario 5: Multi-Bank/Aggregation (Patel)
        is_sc5_patel = "patel" in name_lower
        
        # Monthly fixed patterns
        while current_date <= end_date:
            # 1. Income Generation
            if is_sc3_devi:
                # Scenario 3: Kirana Store (Shadow Income) - Many small UPI credits
                if np.random.random() < 0.9: # Almost everyday
                    credits_count = np.random.randint(5, 12)
                    for _ in range(credits_count):
                        amt = np.random.uniform(100, 2000)
                        txns.append(self._create_txn(customer_id, current_date, amt, 'CREDIT', 'UPI Transfer', 'UPI', 'UPI Credit: Customer Payment'))
            
            elif is_sc4_singh:
                # Scenario 4: Fraud/Ghost - Minimal/No valid income despite claim
                if current_date.day == 15 and np.random.random() < 0.2: # Very rare
                    txns.append(self._create_txn(customer_id, current_date, 5000, 'CREDIT', 'Cash Deposit', 'Branch', 'Cash Deposit Self'))
            
            elif is_sc5_patel:
                # Scenario 5: Multi-Bank Aggregation
                # Split income into two banks
                if current_date.day == 1:
                    txns.append(self._create_txn(customer_id, current_date, income * 0.6, 'CREDIT', 'Salary', 'HDFC Bank', 'Salary Credit: Tech Corp (HDFC)'))
                if current_date.day == 3:
                     txns.append(self._create_txn(customer_id, current_date, income * 0.4, 'CREDIT', 'Salary', 'SBI Bank', 'Salary Credit: Tech Corp (SBI)'))
                     
            elif emp_type == 'Salaried':
                # Scenario 1 & 2
                if current_date.day == 1:
                    base_amt = income
                    if is_sc1_verma:
                        # Add Incentive/Bonus every quarter
                        if current_date.month % 3 == 0:
                            txns.append(self._create_txn(customer_id, current_date, 15000, 'CREDIT', 'Performance Bonus', 'Bank Transfer', 'Salary Bonus Qtrly'))
                    
                    txns.append(self._create_txn(customer_id, current_date, base_amt, 'CREDIT', 'Salary', 'Bank Transfer', 'Salary Credit: Tech Solutions Ltd'))
            
            else:
                # Gig/Self-Employed (Standard)
                if np.random.random() < 0.3: 
                    amt = income * np.random.uniform(0.1, 0.4)
                    txns.append(self._create_txn(customer_id, current_date, amt, 'CREDIT', 'Freelance Payment', 'UPI', 'UPI Credit: Client Payout'))

            # 2. Expenses & Risky Behavior
            if is_sc2_khan:
                # Scenario 2: Hidden Risk (Gambling + BNPL)
                if current_date.day == 10:
                    txns.append(self._create_txn(customer_id, current_date, 4000, 'DEBIT', 'BNPL_EMI_Afterpay', 'Auto-Debit', 'Afterpay EMI Installment'))
                    txns.append(self._create_txn(customer_id, current_date, 4000, 'DEBIT', 'BNPL_EMI_Simpl', 'Auto-Debit', 'Simpl Pay Later Bill'))
                
                if np.random.random() < 0.4:
                     txns.append(self._create_txn(customer_id, current_date, np.random.uniform(500, 2000), 'DEBIT', 'Gaming_Wallet_Dream11', 'UPI', 'Dream11 Add Money'))
            
            # Standard Expense Noise
            if not is_sc4_singh and np.random.random() < 0.6:
                cat = np.random.choice(self.categories['essential'] + self.categories['discretionary'])
                amt = np.random.uniform(50, 5000)
                txns.append(self._create_txn(customer_id, current_date, amt, 'DEBIT', cat, 'UPI', f'UPI Debit: {cat} Merchant'))
            
            # Rent/Bills
            if not is_sc4_singh and current_date.day == 5:
                rent = income * 0.3
                txns.append(self._create_txn(customer_id, current_date, rent, 'DEBIT', 'Rent', 'Bank Transfer', 'Rent Transfer'))
                
            current_date += timedelta(days=1)
            
        return pd.DataFrame(txns)

    def _create_txn(self, cid, date, amount, direction, cat, channel, desc):
        return {
            'customer_id': cid,
            'transaction_date': date.strftime('%Y-%m-%d'),
            'transaction_amount': round(amount, 2),
            'transaction_direction': direction,
            'transaction_category': cat,
            'transaction_channel': channel,
            'description': desc # Added for Signal Extractor compatibility
        }
