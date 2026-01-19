# Helix: Alternate Credit Scoring System 🚀

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31%2B-FF4B4B)
![Status](https://img.shields.io/badge/Status-Proof%20of%20Work-green)

A **Hybrid Signal-Based Machine Learning System** designed to assess the creditworthiness of "Thin-File" customers (Gig workers, Freelancers, Shopkeepers) who lack traditional credit history (CIBIL/Equifax).

> **⚠️ Disclaimer**: This system generates an "Alternate Credit Score" (300–900) using behavioral signals from synthetic banking data. It is for **demonstration and simulation purposes only** and does not replicate or replace standard bureau scores.

---

## 🎯 Project Objective
Traditional credit models rely on salary slips and credit history, excluding millions of credit-worthy individuals. **Helix** solves this by analyzing **Cash Flow Behavior** directly from bank transaction ledgers.

**Key Value Proposition:**
*   **Behavioral Underwriting**: Scores based on *how* you spend/save, not just *what* you earn.
*   **Transparent ML**: Uses an interpretable Linear Regression model with clear "Reason Codes".
*   **Financial Inclusion**: Approves reliable Gig workers/Shopkeepers who are rejected by banks.

---

## ⚙️ How It Works (The Hybrid Pipeline)

The system moves beyond simple simulations by strictly separating **Signal Extraction**, **Label Generation**, and **ML Inference**.

1.  **Raw Data Engine**:
    *   Generates realistic 6-month transaction ledgers (PDF/CSV equivalent).
    *   Simulates predefined personas (e.g., "Impulsive Spender", "Stable Saver").
2.  **Signal Extractor (`src/signal_extractor.py`)**:
    *   Converts raw transactions into auditable signals.
    *   *Key Signals*: `net_cash_retention_ratio`, `income_volatility`, `cash_surplus_stability`, `risky_spend_ratio` (Gambling/BNPL detection).
3.  **ML Inference (`src/scoring_engine.py`)**:
    *   An offline-trained **Linear Regression** model predicts the score.
    *   **Formula**: $Score = w_1(Inflow) + w_2(Stability) - w_3(Risk) ...$

---

## 🧪 Proof of Work Scenarios
The system demonstrates "Lift" over traditional methods through 5 key scenarios:

| Scenario | Persona | Behavior Pattern | Result | Lift / Impact |
| :--- | :--- | :--- | :--- | :--- |
| **1. Optimization** | **Mr. Verma** (Salaried) | Consistent Salary + Bonuses | **APPROVED** (High Limit) | **20% Higher Limit** (Bonuses Recognized) |
| **2. Hidden Risk** | **Mr. Khan** (Salaried) | High Income but Gambling/BNPL | **REJECTED** (Risk Alert) | **Bad Loan Avoided** (Risk Detected) |
| **3. Inclusion** | **Mrs. Devi** (Gig/Shop) | No Payslip, High Daily UPI | **APPROVED** (Risk Priced) | **Financial Inclusion** (Shadow Income) |
| **4. Fraud** | **Mr. Singh** (Self-Emp) | High Declared Income, No Txns | **REJECTED** (Fraud Flag) | **Fraud Prevention** (Validation Failed) |
| **5. Aggregation** | **Mr. Patel** (Salaried) | Split Income (Bank A + Bank B) | **APPROVED** (Unified) | **Account Aggregation** (Full Limit Unlocked) |

---

## 🛠️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/helix-credit-score.git
    cd helix-credit-score
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**
    ```bash
    streamlit run app.py
    ```

4.  **Access the Dashboard**
    Open `http://localhost:8501` in your browser.

---

## 📂 Project Structure

```
├── app.py                  # Entry Point (Redirects to Home)
├── pages/
│   ├── 1_Home.py           # Landing Page
│   ├── 2_Customers.py      # Customer List & Management
│   ├── 3_New_Application.py# Application Form (Trigger ML Pipeline)
│   └── 4_Scorecard.py      # The Dashboard (Explanation & Gauges)
├── src/
│   ├── signal_extractor.py # Core Logic: Raw Txns -> Signals
│   ├── scoring_engine.py   # Hybrid Engine: LabelGen + MLScorer
│   ├── model_trainer.py    # Offline Training Script
│   └── synthetic_generator.py # Data Simulation Engine
└── scored_data.csv         # Local Database (Simulated persistence)
```

---

## 🛡️ Key Compliance Claims
*   ✅ **We Claim**: "ML-based alternate credit score", "Behavioral risk modeling", "Explainable AI".
*   ❌ **We Do NOT Claim**: "Predicts probability of default", "Production-ready Model", "Replacement for CIBIL".

---

## 📝 License
This project is created for **Proof of Concept (POC)** demonstration only.
