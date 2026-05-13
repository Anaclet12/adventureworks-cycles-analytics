\# Installation Guide — Phase 1 Data Warehouse



This guide walks you through setting up the PostgreSQL data warehouse from scratch. Estimated time: 30-45 minutes.



\## Prerequisites



You need three things installed:



1\. \*\*PostgreSQL 14 or later\*\*

2\. \*\*pgAdmin 4\*\* (or `psql` from the command line, if you prefer)

3\. \*\*The 6 source CSV files\*\* (you'll place these in a specific folder — see Step 3)



\---



\## Step 1 — Install PostgreSQL



\### Windows



1\. Download the installer from \[postgresql.org/download/windows](https://www.postgresql.org/download/windows/).

2\. Run the installer. Accept defaults except:

&#x20;  - \*\*Password for `postgres` superuser:\*\* choose something you'll remember. Write it down.

&#x20;  - \*\*Port:\*\* keep the default `5432`.

3\. The installer also installs \*\*pgAdmin 4\*\* — a graphical client we'll use to run the scripts.



\### macOS / Linux



```bash

\\# macOS (Homebrew)

brew install postgresql@16

brew services start postgresql@16



\\# Ubuntu / Debian

sudo apt update

sudo apt install postgresql postgresql-contrib

sudo systemctl start postgresql

```



\### Verify



```bash

psql --version

\\# Expected: psql (PostgreSQL) 14.x or higher

```



\---



\## Step 2 — Create the Database



Open \*\*pgAdmin 4\*\* and connect to your local PostgreSQL server (it should appear automatically on first launch).



1\. In the left sidebar, expand \*\*Servers → PostgreSQL → Databases\*\*.

2\. Right-click \*\*Databases → Create → Database…\*\*

3\. Name it `adventureworks\\\_dwh` and click \*\*Save\*\*.



Alternative via `psql`:



```bash

psql -U postgres -c "CREATE DATABASE adventureworks\\\_dwh;"

```



\---



\## Step 3 — Place the Source CSV Files



The bronze load procedure expects CSV files at specific absolute paths on the machine running PostgreSQL.



\### Create the Folder Structure



```powershell

\\# Windows

mkdir C:\\\\adventureworks\\\\datasets\\\\source\\\_crm

mkdir C:\\\\adventureworks\\\\datasets\\\\source\\\_erp

```



```bash

\\# macOS / Linux

sudo mkdir -p /adventureworks/datasets/source\\\_crm

sudo mkdir -p /adventureworks/datasets/source\\\_erp

```



> \\\*\\\*Note for non-Windows users:\\\*\\\* the SQL scripts use Windows-style paths (`C:\\\\adventureworks\\\\datasets\\\\...`). On macOS/Linux, you'll need to edit `03\\\_bronze\\\_load\\\_procedure.sql` and replace `C:\\\\adventureworks\\\\datasets` with `/adventureworks/datasets` (or wherever you put the data). PostgreSQL's `COPY` command requires the OS path of the server.



\### Place the 6 CSV Files



Put them in their respective folders:



C:\\adventureworks\\datasets\\source\_crm

├── cust\_info.csv

├── prd\_info.csv

└── sales\_details.csv

C:\\adventureworks\\datasets\\source\_erp

├── cust\_az12.csv

├── loc\_a101.csv

└── px\_cat\_g1v2.csv



\### Grant PostgreSQL Read Access



PostgreSQL runs as a service account (`postgres` on Windows, `postgres` user on Linux). The service account must be able to read these CSV files.



\*\*Windows:\*\* right-click `C:\\adventureworks` folder → \*\*Properties → Security → Edit\*\* → add user `NETWORK SERVICE` with \*\*Read \& execute\*\* permissions. Then \*\*OK\*\* through.



\*\*macOS / Linux:\*\* make the files world-readable:

```bash

sudo chmod -R o+r /adventureworks/

```



\---



\## Step 4 — Run the SQL Scripts In Order



In pgAdmin, \*\*connect to the `adventureworks\_dwh` database\*\* (right-click it → Query Tool).



Open and execute each script in this exact order:



| # | File | What it does |

|---|---|---|

| 01 | `sql/00\_init/01\_create\_database.sql` | Creates the 3 schemas |

| 02 | `sql/01\_bronze/02\_bronze\_ddl.sql` | Defines bronze tables |

| 03 | `sql/01\_bronze/03\_bronze\_load\_procedure.sql` | Creates the `load\_bronze()` procedure |

| 04 | `sql/02\_silver/04\_silver\_ddl.sql` | Defines silver tables |

| 05 | `sql/02\_silver/05\_silver\_load\_procedure.sql` | Creates the `load\_silver()` procedure |

| 06 | `sql/03\_gold/06\_gold\_views.sql` | Creates the star schema views |



For each script in pgAdmin's Query Tool: \*\*File → Open\*\*, navigate to the file, then press \*\*F5\*\* (execute).



If a script runs successfully, you'll see output like `CREATE SCHEMA` or `CREATE PROCEDURE` in the Messages tab below.



\---



\## Step 5 — Load the Data Into Bronze



Once all DDL scripts are run, invoke the bronze loader:



```sql

CALL bronze.load\_bronze();

```



You should see messages like:



NOTICE:  Loading Bronze Layer Started at: 2026-05-12 14:30:45.123

NOTICE:  --- Loading CRM Tables ---

NOTICE:  >> Truncating Table: bronze.crm\_cust\_info

NOTICE:  >> Completed bronze.crm\_cust\_info in 0.34 seconds



If you see `ERROR: could not open file "..."`, the CSV files aren't where the procedure expects, or PostgreSQL can't read them. Check Step 3.



\---



\## Step 6 — Load Silver and Run Quality Checks



```sql

\-- Silver layer

CALL silver.load\_silver();

```



Then run the quality checks:



```sql

\-- In Query Tool: File → Open

\-- 99\_utils/07\_quality\_checks\_silver.sql → F5

\-- 99\_utils/08\_quality\_checks\_gold.sql   → F5

```



These should return zero rows (meaning all checks passed) or flag specific issues for investigation.



\---



\## Step 7 — Verify the Gold Layer



```sql

SELECT 'dim\_customers' AS table\_name, COUNT(\*) AS row\_count FROM gold.dim\_customers

UNION ALL

SELECT 'dim\_products',     COUNT(\*) FROM gold.dim\_products

UNION ALL

SELECT 'fact\_sales',       COUNT(\*) FROM gold.fact\_sales;

```



Expected approximate counts:



| Table | Rows |

|---|---|

| `dim\_customers` | \~18,484 |

| `dim\_products` | \~295 |

| `fact\_sales` | \~60,000 |



If your numbers match, the pipeline is complete.



\---



\## Troubleshooting



\### `ERROR: could not open file "..." for reading: Permission denied`

PostgreSQL doesn't have read access to the CSV. See Step 3 — Grant PostgreSQL Read Access.



\### `ERROR: could not open file "..." No such file or directory`

The path inside `03\_bronze\_load\_procedure.sql` doesn't match where you placed the data. Either move the data or edit the procedure.



\### `ERROR: relation "bronze.xxx" does not exist`

You skipped a DDL script. Run them in order 01 → 06.



\### `ERROR: schema "bronze" does not exist`

You're connected to the wrong database. In pgAdmin, double-click the `adventureworks\_dwh` database to connect to it before opening the Query Tool.



\### macOS / Linux: `permission denied` on COPY

The PostgreSQL service runs as the `postgres` user, not your user. Make the data folder accessible:

```bash

sudo chown -R postgres:postgres /adventureworks/

```



\---



\## Next Steps



Once Phase 1 is running, the gold-layer views (`gold.dim\_customers`, `gold.dim\_products`, `gold.fact\_sales`) become the input for:



\- \*\*Phase 2\*\* — Power BI dashboards (see \[`../02\_business\_intelligence/`](../../02\_business\_intelligence/))

\- \*\*Phase 3\*\* — Python machine learning (see \[`../03\_machine\_learning/`](../../03\_machine\_learning/))

...

