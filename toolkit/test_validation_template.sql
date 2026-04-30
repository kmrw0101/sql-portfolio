Use dbName

DECLARE @Date1 DATE;
SET @Date1 = '2026-02-25';

SELECT s.TEST_NUM, s.ACCT_NO, t.ACCOUNT_NUMBER, t.DATE_FIELD,
    CASE
        WHEN s.TEST_NUM = '1'
         AND s.ACCT_NO = '1000001'
         AND t.ACCOUNT_NUMBER = '1000001'
         AND t.DATE_FIELD = @Date1
         AND t.COLUMN_4 = 'Col4'
         AND t.COLUMN_5 = 'Col5'
            THEN 'PASS'
        ELSE 'FAIL'
    END AS 'TEST_RESULT'
FROM (VALUES
      ('1', '1000001', @Date1)
  ) s(TEST_NUM, ACCT_NO, DATE_FIELD)
JOIN [dbName].[dbo].[TargetTable] t
    ON s.ACCT_NO = t.ACCOUNT_NUMBER
   AND s.DATE_FIELD = t.DATE_FIELD

SELECT '[dbName].[dbo].[TargetTable]'
SELECT ID, DATE_FIELD, ACCOUNT_NUMBER, COLUMN_4, COLUMN_5
FROM [dbName].[dbo].[TargetTable]
WHERE ACCOUNT_NUMBER IN ('1000001')
