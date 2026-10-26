USE CreditRiskAnalytics;
GO

-- 1. Portfolio size and simulated default rate
SELECT
    COUNT(*) AS total_borrowers,
    SUM(CAST(default_flag AS INT)) AS simulated_defaults,
    CAST(100.0 * AVG(CAST(default_flag AS FLOAT)) AS DECIMAL(6,2)) AS default_rate_pct,
    AVG(CAST(annual_income AS FLOAT)) AS avg_annual_income,
    AVG(CAST(loan_amount AS FLOAT)) AS avg_loan_amount
FROM dbo.Borrowers;

-- 2. Default rate by credit-score band
SELECT
    CASE
        WHEN credit_score < 580 THEN 'Below 580'
        WHEN credit_score < 670 THEN '580-669'
        WHEN credit_score < 740 THEN '670-739'
        ELSE '740+'
    END AS credit_score_band,
    COUNT(*) AS borrowers,
    CAST(100.0 * AVG(CAST(default_flag AS FLOAT)) AS DECIMAL(6,2)) AS default_rate_pct
FROM dbo.Borrowers
GROUP BY CASE
        WHEN credit_score < 580 THEN 'Below 580'
        WHEN credit_score < 670 THEN '580-669'
        WHEN credit_score < 740 THEN '670-739'
        ELSE '740+'
    END
ORDER BY MIN(credit_score);

-- 3. Default rate by debt-to-income band
SELECT
    CASE
        WHEN debt_to_income_ratio < 0.20 THEN '< 20%'
        WHEN debt_to_income_ratio < 0.40 THEN '20-39%'
        WHEN debt_to_income_ratio < 0.60 THEN '40-59%'
        ELSE '60%+'
    END AS dti_band,
    COUNT(*) AS borrowers,
    CAST(100.0 * AVG(CAST(default_flag AS FLOAT)) AS DECIMAL(6,2)) AS default_rate_pct
FROM dbo.Borrowers
GROUP BY CASE
        WHEN debt_to_income_ratio < 0.20 THEN '< 20%'
        WHEN debt_to_income_ratio < 0.40 THEN '20-39%'
        WHEN debt_to_income_ratio < 0.60 THEN '40-59%'
        ELSE '60%+'
    END
ORDER BY MIN(debt_to_income_ratio);

-- 4. Portfolio by loan purpose
SELECT loan_purpose, COUNT(*) AS borrowers,
       AVG(CAST(loan_amount AS FLOAT)) AS avg_loan_amount,
       CAST(100.0 * AVG(CAST(default_flag AS FLOAT)) AS DECIMAL(6,2)) AS default_rate_pct
FROM dbo.Borrowers
GROUP BY loan_purpose
ORDER BY borrowers DESC;

-- 5. Home ownership profile
SELECT home_ownership, COUNT(*) AS borrowers,
       CAST(100.0 * AVG(CAST(default_flag AS FLOAT)) AS DECIMAL(6,2)) AS default_rate_pct
FROM dbo.Borrowers
GROUP BY home_ownership
ORDER BY borrowers DESC;

-- 6. Loan term summary
SELECT loan_term_months, COUNT(*) AS borrowers,
       AVG(CAST(loan_amount AS FLOAT)) AS avg_loan_amount,
       CAST(100.0 * AVG(CAST(default_flag AS FLOAT)) AS DECIMAL(6,2)) AS default_rate_pct
FROM dbo.Borrowers
GROUP BY loan_term_months
ORDER BY loan_term_months;

-- 7. High DTI / low score segment for investigation, not automatic rejection
SELECT TOP (25) borrower_id, credit_score, debt_to_income_ratio,
       annual_income, loan_amount, default_flag
FROM dbo.Borrowers
WHERE debt_to_income_ratio >= 0.45 AND credit_score < 640
ORDER BY debt_to_income_ratio DESC, credit_score ASC;

-- 8. Range / sanity checks (every count should be 0)
SELECT
    SUM(CASE WHEN credit_score < 300 OR credit_score > 850 THEN 1 ELSE 0 END) AS unusual_credit_scores,
    SUM(CASE WHEN loan_amount <= 0 THEN 1 ELSE 0 END) AS nonpositive_loan_amount,
    SUM(CASE WHEN annual_income <= 0 THEN 1 ELSE 0 END) AS nonpositive_income,
    SUM(CASE WHEN age < 18 THEN 1 ELSE 0 END) AS under_18,
    SUM(CASE WHEN debt_to_income_ratio < 0 THEN 1 ELSE 0 END) AS negative_dti
FROM dbo.Borrowers;
GO
