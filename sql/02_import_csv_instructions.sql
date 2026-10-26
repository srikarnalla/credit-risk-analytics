/*
Load data/raw/borrowers.csv into dbo.Borrowers. Pick ONE option.

OPTION A - SSMS wizard (works everywhere)
  Right-click the CreditRiskAnalytics database > Tasks > Import Flat File
  (or Import Data). Source: data\raw\borrowers.csv. Destination table:
  dbo.Borrowers. First row contains column names: Yes.
  Check the column mappings before finishing (numeric columns numeric,
  default_flag as bit). If the wizard creates its own staging table, verify
  row counts and column names before inserting into dbo.Borrowers.

OPTION B - BULK INSERT (SQL Server 2017+)
  The file path is read by the SQL SERVER SERVICE, so it must be a path that
  the server can access. Edit the path below, then uncomment and run.

  BULK INSERT dbo.Borrowers
  FROM 'C:\path\to\credit-risk-analytics\data\raw\borrowers.csv'
  WITH (FORMAT = 'CSV', FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '0x0a', TABLOCK);

After loading, the checks below should show 2500 rows.
*/
USE CreditRiskAnalytics;
GO
SELECT COUNT(*) AS borrower_rows FROM dbo.Borrowers;
SELECT TOP (10) * FROM dbo.Borrowers ORDER BY borrower_id;
GO
