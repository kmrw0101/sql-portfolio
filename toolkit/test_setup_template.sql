Use dbName

-----------------------------------------
-- Clean up any previous runs of the test
-----------------------------------------

DELETE FROM [dbName].[dbo].[TableName] -- source
WHERE ACCT_NO IN ('1000001')

-----------------------------------------
-- Setup test scenarios
-----------------------------------------

DECLARE @Date1 DATE;
SET @Date1 = '2026-02-25';

DECLARE @ID INT;
SET @ID = COALESCE((SELECT MAX(ID) FROM dbo.TableName), 0) + 1

INSERT INTO [dbName].[dbo].[TableName]
   (ID,
       DATE_FIELD,
       CHANGE_TYPE,
       ACCT_NO,
       Col4,
       Col5)
VALUES
   (@ID,
       @Date1,
       'A', --ADD
    '1000001',
       'Col4',
       'Col5')

/*
 Continue to build out testing for all scenarios:
 record behavior for multi-day tests with ADDS, CHANGES, VOIDS 
 and all transformations for each column. Test happy path 
 and negative edge case testing to ensure data is mapped 
 appropriately based on what is in the source-to-target or 
 metadata documents provided.
 */

-----------------------------------------
-- Review inserted data
-----------------------------------------
SELECT '[dbName].[dbo].[TableName]'
SELECT ID, DATE_FIELD, CHANGE_TYPE, ACCT_NO, Col4, Col5
FROM [dbName].[dbo].[TableName]
WHERE ACCT_NO IN ('1000001')
