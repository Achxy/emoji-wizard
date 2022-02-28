SELECT TABLE_NAME
-- This was from previous implementation
-- This can be used to fetch all the tables
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE',