# Data dictionary

All values are synthetic. `data/raw/borrowers.csv` has 2,500 rows and 13 columns, with no missing values.

| Column | Type | Description |
|---|---|---|
| `borrower_id` | integer | Synthetic unique identifier (not used as a model feature) |
| `age` | integer | Borrower age in years (21-70) |
| `annual_income` | integer | Annual income, in simulated currency units (no specific currency claimed) |
| `employment_years` | float | Years employed |
| `credit_score` | integer | Credit-score-like value (451-850) |
| `loan_amount` | integer | Requested loan amount, simulated currency units |
| `loan_term_months` | integer | Loan duration: 12, 24, 36, 48 or 60 months |
| `interest_rate` | float | Simulated annual interest rate, percent |
| `existing_debt` | integer | Existing debt, simulated currency units |
| `debt_to_income_ratio` | float | Simulated risk feature. **It is not calculated as `existing_debt / annual_income`** (the two only correlate at about 0.84) |
| `home_ownership` | text | `RENT`, `MORTGAGE`, `OWN` or `OTHER` |
| `loan_purpose` | text | `DEBT_CONSOLIDATION`, `HOME_IMPROVEMENT`, `OTHER`, `MEDICAL`, `EDUCATION` or `BUSINESS` |
| `default_flag` | 0/1 | Synthetic target: 1 = simulated default, 0 = no simulated default |
