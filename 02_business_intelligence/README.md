# Phase 2 — Business Intelligence

> Three Power BI dashboards built on the gold-layer star schema, serving the CFO, CMO, COO, and VP Merchandising.

## What's In This Folder

```
02_business_intelligence/
├── README.md                       ← This file
├── pbix/
│   └── AdventureWorks_Analytics.pbix    The Power BI report (open in Power BI Desktop)
├── extracts/                       Gold-layer CSV files the .pbix consumes (gitignored)
├── screenshots/                    PNG snapshots of each dashboard
├── theme/
│   └── aw_theme.json              Custom Power BI theme matching project palette
└── docs/
    ├── BLUEPRINT.md                Dashboard blueprint (audience → questions → fields)
    ├── DAX_MEASURES.md             Every DAX measure, documented
    ├── DATA_MODEL.md               Star schema explanation + screenshot
    └── mockups/                    Pre-build wireframes for each dashboard
```

## What This Phase Delivers

### Three Dashboards

| Dashboard | Primary stakeholder | Business questions answered |
|---|---|---|
| **Sales & Margin** | CFO, VP Merchandising | Margin by product line × region; top products; revenue vs margin scatter |
| **Customer Intelligence** | CMO | RFM segments; demographics; premium-bike buyer profile; new customer acquisition |
| **Operations & Fulfillment** | COO, Customer Service | Ship lag by region; seasonality; maintenance-eligible base |

### Data Model

Classic star schema with:
- 1 fact table (`fact_sales`)
- 2 dimension tables (`dim_customers`, `dim_products`)
- 1 calendar table (`Date`, marked as Date Table)
- 1 dedicated measures container (`_Measures`)
- 1 derived table for RFM analysis (`Customer_RFM`)

See [`docs/DATA_MODEL.md`](docs/DATA_MODEL.md).

### DAX Measures

20+ measures organized into:
- **Sales metrics:** Revenue, COGS, Gross Margin $, Gross Margin %, AOV, Quantity Sold
- **Customer metrics:** Active Customers, New Customers (by first-purchase date), Customer LTV, Repeat Customer Rate
- **Operations metrics:** Ship Lag (days), % Shipped On Time, Maintenance-Eligible Customers
- **Time intelligence:** Revenue LY, Revenue YoY %, Gross Margin % YoY

See [`docs/DAX_MEASURES.md`](docs/DAX_MEASURES.md) for every measure with explanation.

## Quick Start

1. Open Power BI Desktop.
2. **File → Open** → navigate to `pbix/AdventureWorks_Analytics.pbix`.
3. If the report shows "Refresh failed" or "Data source error":
   - Generate the three CSV extracts (`fact_sales.csv`, `dim_customers.csv`, `dim_products.csv`) from the Phase 1 gold layer.
   - Place them in `extracts/`.
   - **Home → Transform data → Data source settings** → update the file paths to point to your `extracts/` folder.
   - **Home → Refresh**.

## Key Design Decisions

### Star Schema, Not Snowflake
We chose a star schema (denormalized dimensions) over a snowflake (normalized dimensions) because:
- Power BI is optimized for star schemas — query performance is better.
- Calculated columns and measures are simpler to write.
- The trade-off (some redundancy in dimension tables) is acceptable at this data volume.

### Inactive Relationships for Multiple Dates
`fact_sales` has three date fields: `order_date`, `ship_date`, `due_date`. The first is the **active** relationship to the calendar; the other two are **inactive**, activated when needed via DAX `USERELATIONSHIP`. This allows time-intelligence measures to default to order date but switch contexts cleanly.

### Custom Theme File
A custom theme (`theme/aw_theme.json`) enforces the project palette across all visuals:
- Primary: deep teal `#1F4E5F`
- Categorical: green `#5B8C5A`, orange `#E07B39`, gray `#9B9B9B`
- Diverging: red `#E24B4A` ↔ green `#1D9E75`

This means a new visual added to the report automatically inherits the palette.

## Dashboard Screenshots

See [`screenshots/`](screenshots/) for current renderings of each dashboard.

## Tech Stack

Power BI Desktop · DAX · M (Power Query)

## What's Next

The dashboards establish the descriptive baseline. Phase 3 (Python ML) extends with predictive and prescriptive analytics, with model outputs (segments, forecasts) written back as CSV for Tableau / Power BI consumption.

See [`../README.md`](../README.md) for the overall project context.
