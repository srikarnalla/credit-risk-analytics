/*
Credit Risk Analytics
Creates the database if it does not exist.
Creates dbo.Borrowers only if the table does not exist.
Existing tables and data are preserved.
*/

IF DB_ID(N'CreditRiskAnalytics') IS NULL
BEGIN
    CREATE DATABASE CreditRiskAnalytics;
END;
GO

USE CreditRiskAnalytics;
GO

IF OBJECT_ID(N'dbo.Borrowers', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Borrowers (
        borrower_id BIGINT NOT NULL PRIMARY KEY,
        age TINYINT NOT NULL,
        annual_income DECIMAL(12,2) NOT NULL,
        employment_years DECIMAL(5,1) NOT NULL,
        credit_score SMALLINT NOT NULL,
        loan_amount DECIMAL(12,2) NOT NULL,
        loan_term_months SMALLINT NOT NULL,
        interest_rate DECIMAL(5,2) NOT NULL,
        existing_debt DECIMAL(12,2) NOT NULL,
        debt_to_income_ratio DECIMAL(6,4) NOT NULL,
        home_ownership VARCHAR(20) NOT NULL,
        loan_purpose VARCHAR(30) NOT NULL,
        default_flag BIT NOT NULL
    );
END;
GO

PRINT 'Database setup completed. Existing borrower data was preserved.';
GO