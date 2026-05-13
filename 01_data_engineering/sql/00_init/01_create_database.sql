/*
=============================================================
Create Database and Schemas
=============================================================
Create a database with PostgreSQL 
Click the arrow (under Servers on the left) ▸ to expand it → you’ll see:
Databases
Login/Group Roles
Tablespaces

Click on Databases → right-click → Create → Database
→ name it Datawarehouse, then click Save.

Script Purpose:
    This script sets up three schemas within the database named 'DataWarehouse': 'bronze', 'silver', and 'gold'.
*/

-- Create schemas (namespaces)
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;
