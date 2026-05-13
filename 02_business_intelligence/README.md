\# Phase 2 — Business Intelligence



> Three Power BI dashboards built on the gold-layer star schema, serving the CFO, CMO, COO, and VP Merchandising. Built with DAX measures, a custom theme, and a derived RFM segmentation table.



\## At a Glance



The `.pbix` file in \[`pbix/`](pbix/) contains three executive-ready dashboards plus supporting model tables. Each dashboard targets a specific stakeholder and answers one or two of the project's five business questions.



| Dashboard | Primary stakeholder | Business questions answered |

|---|---|---|

| \*\*Sales \& Margin\*\* | CFO, VP Merchandising | Margin by product line × region; top products; revenue vs margin scatter |

| \*\*Customer Intelligence\*\* | CMO | RFM segments; demographics; premium-bike buyer profile; new customer acquisition |

| \*\*Operations \& Fulfillment\*\* | COO, Customer Service | Ship lag by region; seasonality; maintenance-eligible base |



\## Dashboards



\### Dashboard 1 — Sales \& Margin

\*Audience: CFO, VP Merchandising\*



!\[Sales \& Margin](screenshots/d1\_sales\_margin.png)



Shows revenue, gross margin, and average order value across product lines and regions. The margin heatmap pinpoints where the company is underpriced relative to cost.



\### Dashboard 2 — Customer Intelligence

\*Audience: CMO\*



!\[Customer Intelligence](screenshots/d2\_customer\_intelligence.png)



Surfaces the customer base: new vs. active customers (using first-purchase date — see \[data quality findings](../docs/03\_data\_quality\_findings.md)), behavioral segments via RFM (Whales, Everyday, At Risk, New Passions), and LTV / AOV by age band.



\### Dashboard 3 — Operations \& Fulfillment

\*Audience: COO, Customer Service Director\*



!\[Operations \& Fulfillment](screenshots/d3\_operations\_fulfillment.png)



Tracks order-to-ship lag by region and product line, seasonal volume patterns, and the maintenance-eligible customer base for service team outreach.



\## What's In This Folder





\# Phase 2 — Business Intelligence



> Three Power BI dashboards built on the gold-layer star schema, serving the CFO, CMO, COO, and VP Merchandising. Built with DAX measures, a custom theme, and a derived RFM segmentation table.



\## At a Glance



The `.pbix` file in \[`pbix/`](pbix/) contains three executive-ready dashboards plus supporting model tables. Each dashboard targets a specific stakeholder and answers one or two of the project's five business questions.



| Dashboard | Primary stakeholder | Business questions answered |

|---|---|---|

| \*\*Sales \& Margin\*\* | CFO, VP Merchandising | Margin by product line × region; top products; revenue vs margin scatter |

| \*\*Customer Intelligence\*\* | CMO | RFM segments; demographics; premium-bike buyer profile; new customer acquisition |

| \*\*Operations \& Fulfillment\*\* | COO, Customer Service | Ship lag by region; seasonality; maintenance-eligible base |



\## Dashboards



\### Dashboard 1 — Sales \& Margin

\*Audience: CFO, VP Merchandising\*



!\[Sales \& Margin](screenshots/d1\_sales\_margin.png)



Shows revenue, gross margin, and average order value across product lines and regions. The margin heatmap pinpoints where the company is underpriced relative to cost.



\### Dashboard 2 — Customer Intelligence

\*Audience: CMO\*



!\[Customer Intelligence](screenshots/d2\_customer\_intelligence.png)



Surfaces the customer base: new vs. active customers (using first-purchase date — see \[data quality findings](../docs/03\_data\_quality\_findings.md)), behavioral segments via RFM (Whales, Everyday, At Risk, New Passions), and LTV / AOV by age band.



\### Dashboard 3 — Operations \& Fulfillment

\*Audience: COO, Customer Service Director\*



!\[Operations \& Fulfillment](screenshots/d3\_operations\_fulfillment.png)



Tracks order-to-ship lag by region and product line, seasonal volume patterns, and the maintenance-eligible customer base for service team outreach.



\## What's In This Folder



02\_business\_intelligence/

├── README.md                         ← This file

├── pbix/

│   └── AdventureWorks\_Analytics.pbix Open in Power BI Desktop

├── screenshots/                      PNG snapshots of each dashboard

│   ├── d1\_sales\_margin.png

│   ├── d2\_customer\_intelligence.png

│   └── d3\_operations\_fulfillment.png

├── theme/                            (Reserved for custom Power BI theme JSON)

└── docs/

├── BLUEPRINT.md                  (to be added) Dashboard wireframes + design rationale

├── DAX\_MEASURES.md               (to be added) Every DAX measure documented

├── DATA\_MODEL.md                 (to be added) Star schema + relationships

└── mockups/                      (to be added) Pre-build wireframes



\## Data Model



Classic star schema with one fact and three dimensions:



\[Date]

&#x20;                  │

&#x20;                  │ (Order Date — active)

&#x20;                  │ (Ship Date — inactive)

&#x20;                  │ (Due Date — inactive)

&#x20;                  │



\[dim\_customers] ─── \[fact\_sales] ─── \[dim\_products]

Customer Key       Product Key       Product Key



Plus two supporting tables:

\- \*\*`\_Measures`\*\* — dedicated container for all DAX measures (no associated data, used purely for organization)

\- \*\*`Customer\_RFM`\*\* — calculated table containing each customer's Recency, Frequency, Monetary scores and the assigned `RFM\_Segment` label



\## DAX Measures



The report defines 20+ DAX measures organized into four categories:



\- \*\*Sales metrics:\*\* Revenue, COGS, Gross Margin $, Gross Margin %, AOV, Quantity Sold

\- \*\*Customer metrics:\*\* Active Customers, New Customers (by first-purchase date), Customer LTV, Repeat Customer Rate

\- \*\*Operations metrics:\*\* Ship Lag (days), % Shipped On Time, Maintenance-Eligible Customers

\- \*\*Time intelligence:\*\* Revenue LY, Revenue YoY %, Gross Margin % YoY



Full documentation in `docs/DAX\_MEASURES.md` (to be added).



\## Key Design Decisions



\### Star Schema, Not Snowflake

Star schemas (denormalized dimensions) outperform snowflake schemas in Power BI's VertiPaq engine. DAX measures are also simpler to write against a star schema. The slight redundancy in dimension tables is an acceptable trade-off at this data volume.



\### Inactive Relationships for Multiple Dates

`fact\_sales` has three date columns: `order\_date` (active relationship to `Date`), plus `ship\_date` and `due\_date` (inactive). DAX measures use `USERELATIONSHIP` to switch contexts when measuring fulfillment performance vs. revenue.



\### "New Customer" Defined via First-Purchase Date

The source `dim\_customers.create\_date` is contaminated with warehouse-load timestamps (all 2025-2026), making it unusable for cohort analysis. New customer acquisition is therefore derived from the first transaction in `fact\_sales` per customer. Documented in detail in \[data quality findings](../docs/03\_data\_quality\_findings.md).



\### Custom Theme

A custom theme file (`theme/aw\_theme.json` — to be added) enforces the project palette across all visuals: teal `#1F4E5F`, green `#5B8C5A`, orange `#E07B39`, gray `#9B9B9B`. New visuals inherit the palette automatically.



\## How to Open the Report



1\. Install \*\*Power BI Desktop\*\* (free, Windows only): \[powerbi.microsoft.com/desktop](https://powerbi.microsoft.com/desktop/)

2\. Clone or download this repository

3\. Open `pbix/AdventureWorks\_Analytics.pbix` in Power BI Desktop

4\. If the report shows a "Refresh failed" error, the data source paths need updating — see \[`docs/BLUEPRINT.md`](docs/BLUEPRINT.md) (to be added) for details



\## Tech Stack



Power BI Desktop · DAX · M (Power Query)



\## What's Next



The dashboards establish the descriptive and diagnostic baseline. \[Phase 3 (Machine Learning)](../03\_machine\_learning/) extends with predictive and prescriptive analytics:



\- \*\*Customer segmentation\*\* — validates this dashboard's RFM segments with K-Means clustering

\- \*\*Sales forecasting\*\* — Prophet + LSTM models projecting revenue by product line and region

\- \*\*Prescriptive recommendations\*\* — combines segmentation and forecast into action lists for marketing, operations, and customer service



See the \[top-level README](../README.md) for the overall project context.

