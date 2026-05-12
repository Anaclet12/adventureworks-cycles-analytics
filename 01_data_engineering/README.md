# Phase 1 — Data Engineering

> Production-grade PostgreSQL data warehouse using the medallion architecture (bronze → silver → gold). Built with stored procedures, transactions, error handling, audit triggers, and data quality checks.

## What's In This Folder

```
01_data_engineering/
├── README.md                   ← This file
├── sql/                        SQL scripts numbered 01-XX in execution order
│   ├── 00_init/                Database, schemas, roles, metadata tables
│   ├── 01_bronze/              Bronze layer (raw landing)
│   ├── 02_silver/              Silver layer (cleansed, standardized)
│   ├── 03_gold/                Gold layer (business-ready star schema)
│   └── 99_utils/               Utility scripts (quality checks, monitoring)
├── scripts/                    Bash runners
│   └── run_phase1.sh           Bootstrap entire phase with one command
├── docs/                       Phase-specific documentation
│   ├── INSTALL.md              One-time setup on a fresh machine
│   ├── EXECUTION_ORDER.md      What runs when and why
│   ├── PROJECT_STRUCTURE.md    Folder and file conventions
│   └── PHASE1_GUIDE.md         What was built + verification steps
└── data/raw/                   Source CSV files (gitignored)
```

## What This Phase Delivers

- **5 schemas** with role-based access control (`bronze`, `silver`, `gold`, `meta`, `quality`)
- **3 user roles** with least-privilege grants (`etl_user`, `analyst_user`, `app_user`)
- **6 bronze tables** mirroring source files exactly, with metadata columns for lineage
- **`bronze.load_bronze()` stored procedure** with full error handling, transaction control, and logging
- **`meta.etl_log`** capturing every procedure call with run_id, timing, row counts, status
- **`meta.audit_log`** with JSONB-based row-level change tracking via triggers
- **`quality.violation_log`** with data quality rule violations
- **Indexing strategy** appropriate to each layer

## Quick Start

```bash
cd 01_data_engineering
bash scripts/run_phase1.sh "$(pwd)/data/raw"
```

Expected output: 6 bronze tables loaded with row counts matching source files (116,294 total rows), every step logged.

See [`docs/INSTALL.md`](docs/INSTALL.md) for prerequisites and detailed setup.

## Architecture

```
   Sources               Bronze              Silver              Gold
  ─────────             ─────────           ─────────           ─────────
   CRM CSVs   ─────►   raw landing  ─►   cleansed     ─►   star schema
   ERP CSVs   ─────►   (as-is)            standardized      (dim + fact)
                       full reload        deduplicated      materialized
                                          type-fixed         + indexed
```

## Tech Stack

PostgreSQL 14+ · plpgsql · bash · `psql`

## What's Next

The gold layer produces three business-ready outputs (`dim_customers`, `dim_products`, `fact_sales`) consumed by:

- Phase 2 (Power BI) — connected as CSV extracts or live database connection.
- Phase 3 (Python ML) — loaded as pandas DataFrames for segmentation and forecasting.

See [`../README.md`](../README.md) for the overall project context.
