\# Phase 1 — Data Engineering



> Production-grade PostgreSQL data warehouse using the medallion architecture (bronze → silver → gold). Implements stored procedures, transactions, error handling via `RAISE NOTICE`, and data quality checks.



\## What's In This Folder

01\_data\_engineering/

├── README.md                           ← This file

├── sql/                                Numbered SQL scripts (run in order)

│   ├── 00\_init/

│   │   └── 01\_create\_database.sql     Creates bronze, silver, gold schemas

│   ├── 01\_bronze/

│   │   ├── 02\_bronze\_ddl.sql          Bronze table definitions

│   │   └── 03\_bronze\_load\_procedure.sql   Loads CSV files into bronze

│   ├── 02\_silver/

│   │   ├── 04\_silver\_ddl.sql          Silver table definitions

│   │   └── 05\_silver\_load\_procedure.sql   Cleanses bronze → silver

│   ├── 03\_gold/

│   │   └── 06\_gold\_views.sql          Star schema views (dim + fact)

│   └── 99\_utils/

│       ├── 07\_quality\_checks\_silver.sql   Silver-layer data quality

│       └── 08\_quality\_checks\_gold.sql     Gold-layer data quality

├── docs/

│   ├── INSTALL.md                      One-time setup instructions

│   ├── data\_catalog.md                 Field-level dictionary of every table

│   ├── naming\_conventions.md           Naming standards used across the warehouse

│   ├── data\_layers.pdf                 Medallion layer explanation

│   ├── Project\_Notes\_Sketches.pdf      Original design notes and sketches

│   └── images/                         Architecture and data model diagrams

└── data/raw/                           Source CSV files (gitignored — see INSTALL.md)



\## Architecture

Sources               Bronze              Silver              Gold

─────────             ─────────           ─────────           ─────────

CRM CSVs   ─────►   raw landing  ─►   cleansed     ─►   star schema

ERP CSVs   ─────►   (as-is)            standardized      (dim + fact)

full reload        deduplicated         views

type-fixed

See \[`docs/images/data\_architecture.png`](docs/images/data\_architecture.png) for the full architecture diagram.



\## What This Phase Delivers



\### Three Schemas

\- \*\*`bronze`\*\* — raw ingestion, no transformations, preserves source artifacts

\- \*\*`silver`\*\* — cleansed, deduplicated, standardized

\- \*\*`gold`\*\* — business-ready star schema (`dim\_customers`, `dim\_products`, `fact\_sales`)



\### Two Stored Procedures

\- \*\*`bronze.load\_bronze()`\*\* — truncates and reloads all 6 bronze tables from CSV via `COPY` commands inside dynamic SQL

\- \*\*`silver.load\_silver()`\*\* — applies the silver-layer transformations (date conversion, gender/marital status normalization, deduplication, key parsing)



\### Quality Checks

\- \*\*`07\_quality\_checks\_silver.sql`\*\* — validates silver-layer integrity (no NULL keys, sales = quantity × price, valid date ranges)

\- \*\*`08\_quality\_checks\_gold.sql`\*\* — validates gold-layer integrity (surrogate-key uniqueness, referential integrity, model relationships)



\### Gold Layer Outputs

Three business-ready views:

\- `gold.dim\_customers` — unified customer master (CRM identity + ERP demographics)

\- `gold.dim\_products` — active product catalogue with category hierarchy and maintenance flag

\- `gold.fact\_sales` — sales transactions joined to both dimensions



\## Quick Start



See \[`docs/INSTALL.md`](docs/INSTALL.md) for detailed setup. Summary:



```bash

\# 1. Create C:\\adventureworks\\datasets\\source\_crm and source\_erp folders

\# 2. Place the 6 source CSV files there

\# 3. Create a PostgreSQL database (e.g., adventureworks\_dwh)

\# 4. Run the scripts in order 01 → 08

```



\## Tech Stack



PostgreSQL 14+ · plpgsql · pgAdmin (or psql)



\## What's Next



The gold layer outputs (`dim\_customers`, `dim\_products`, `fact\_sales`) feed:



\- \*\*Phase 2 (Power BI)\*\* — connected via CSV extracts of the gold views or live connection.

\- \*\*Phase 3 (Python ML)\*\* — loaded as pandas DataFrames for segmentation and forecasting.



See the \[top-level README](../README.md) for the overall project context.

