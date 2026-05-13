# DAX Measures Reference

This document catalogues every DAX measure in the Power BI report. Measures are organized by analytical category and stored in the dedicated ``_Measures`` table for navigability.

## Categories at a Glance

| Category | Measures | Purpose |
|---|---|---|
| Sales & Margin | 5 | Revenue, cost, margin in absolute and percentage forms |
| Customer Intelligence | 6 | Customer counts, LTV, retention |
| Operations & Fulfillment | 4 | Ship lag, on-time performance |
| Time Intelligence | 4 | Year-over-year comparisons |
| Visual Formatting | 2 | Conditional formatting helpers |
| Forward-Looking | 2 | Maintenance outreach prioritization |

---

## Sales & Margin

### Revenue
```daxExcellent — I have all 23 of your measures. This is the kind of substantive material that turns a portfolio doc into a reference. Let me write DAX_MEASURES.md now, organized properly and grouped by category.
Step 1 — Write DAX_MEASURES.md
Copy this entire block and paste into PowerShell:
powershellcd C:\Users\anacl\Documents\adventureworks-cycles-analytics-scaffold\adventureworks-cycles-analytics

$content = @'
# DAX Measures Reference

This document catalogues every DAX measure in the Power BI report. Measures are organized by analytical category and stored in the dedicated ``_Measures`` table for navigability.

## Categories at a Glance

| Category | Measures | Purpose |
|---|---|---|
| Sales & Margin | 5 | Revenue, cost, margin in absolute and percentage forms |
| Customer Intelligence | 6 | Customer counts, LTV, retention |
| Operations & Fulfillment | 4 | Ship lag, on-time performance |
| Time Intelligence | 4 | Year-over-year comparisons |
| Visual Formatting | 2 | Conditional formatting helpers |
| Forward-Looking | 2 | Maintenance outreach prioritization |

---

## Sales & Margin

### Revenue
```dax
Revenue = SUM ( fact_sales[sales_amount] )
```
**Purpose:** Total sales revenue across the filtered period.
**Used in:** every revenue-related visual; the base for margin calculations.

---

### Cost of Goods Sold
```dax
Cost of Goods Sold =
SUMX (
    fact_sales,
    fact_sales[Quantity] * RELATED ( dim_products[cost] )
)
```
**Purpose:** Total cost basis using the per-row product cost from ``dim_products``.
**Why ``SUMX`` with ``RELATED``:** ``cost`` lives in ``dim_products``, so we use ``RELATED`` inside ``SUMX`` to pull each row's product cost.
**Note:** Returns 0 for product rows where cost is null (handled at the silver layer).

---

### Gross Margin $
```dax
Gross Margin $ = [Revenue] - [Cost of Goods Sold]
```
**Purpose:** Absolute gross margin in dollars.

---

### Gross Margin %
```dax
Gross Margin % = DIVIDE ( [Gross Margin $], [Revenue], 0 )
```
**Purpose:** Margin as percentage of revenue.
**Why ``DIVIDE``:** safer than ``/`` because it returns 0 (third argument) when revenue is 0, avoiding ``DIV/0`` errors.

---

### Quantity Sold
```dax
Quantity Sold = SUM ( fact_sales[quantity] )
```
**Purpose:** Total units sold.

---

## Customer Intelligence

### Active Customers
```dax
Active Customers = DISTINCTCOUNT ( fact_sales[customer_key] )
```
**Purpose:** Distinct customer count from sales transactions.
**Note:** Uses the fact table's customer_key, not ``dim_customers``, to ensure only customers who actually transacted are counted.

---

### Order Count
```dax
Order Count = DISTINCTCOUNT ( fact_sales[order_number] )
```
**Purpose:** Number of distinct orders (not order lines).

---

### Average Order Value
```dax
Average Order Value = DIVIDE ( [Revenue], DISTINCTCOUNT ( fact_sales[order_number] ), 0 )
```
**Purpose:** Revenue per order.

---

### Customer LTV
```dax
Customer LTV = DIVIDE ( [Revenue], [Active Customers], 0 )
```
**Purpose:** Average lifetime value per customer in the period.
**Caveat:** This is a simple average, not a cohorted LTV. True LTV would require longitudinal cohort analysis, which would benefit from a Python implementation in Phase 3.

---

### New Customers
```dax
New Customers =
COUNTROWS (
    FILTER (
        'dim_customers',
        'dim_customers'[First Purchase Date] IN VALUES ( 'Date'[Date] )
    )
)
```
**Purpose:** Count customers whose first purchase falls in the current date filter context.
**Why this approach:** ``dim_customers[create_date]`` is contaminated with warehouse-load timestamps (all 2025-2026) and cannot be used for cohort analysis. ``First Purchase Date`` is a calculated column on ``dim_customers`` derived from the earliest ``fact_sales[order_date]`` per customer. See [data quality findings](../../docs/03_data_quality_findings.md).

---

### Repeat Customers
```dax
Repeat Customers = [Active Customers] - [New Customers]
```
**Purpose:** Customers who transacted in the period but whose first purchase was earlier.
**Implication:** ``Active Customers = New Customers + Repeat Customers``, a clean decomposition that maps directly to the CMO's retention narrative.

---

### Repeat Customer Rate
```dax
Repeat Customer Rate = DIVIDE ( [Repeat Customers], [Active Customers], 0 )
```
**Purpose:** Fraction of active customers who are returning rather than new.

---

### Acquisition Revenue
```dax
Acquisition Revenue =
CALCULATE (
    [Revenue],
    FILTER (
        fact_sales,
        fact_sales[order_date] = RELATED ( dim_customers[First Purchase Date] )
    )
)
```
**Purpose:** Revenue specifically from each customer's first order — i.e., the revenue contribution of newly acquired customers.

---

## Operations & Fulfillment

### Ship Lag (days)
```dax
Ship Lag (days) = AVERAGE ( fact_sales[Ship_Lag_Days] )
```
**Purpose:** Average days between order and ship.
**Note:** ``Ship_Lag_Days`` is a calculated column on ``fact_sales`` computed as ``DATEDIFF(order_date, ship_date, DAY)``.

---

### Orders Shipped
```dax
Orders Shipped =
CALCULATE (
    [Order Count],
    NOT ISBLANK ( fact_sales[ship_date] )
)
```
**Purpose:** Distinct order count restricted to orders that have a ship date (i.e., excluding open/pending orders).

---

### % Shipped On Time
```dax
% Shipped On Time =
VAR OnTime =
    CALCULATE (
        [Order Count],
        FILTER (
            fact_sales,
            NOT ISBLANK ( fact_sales[ship_date] )
                && DATEDIFF ( fact_sales[order_date], fact_sales[ship_date], DAY ) <= 7
        )
    )
RETURN
    DIVIDE ( OnTime, [Orders Shipped], 0 )
```
**Purpose:** Fraction of shipped orders that meet the 7-day SLA.
**Definition of "on time":** ship_date is within 7 days of order_date.

---

### SLA Breach Rate %
```dax
SLA Breach Rate % =
VAR TotalShipped = [Orders Shipped]
VAR LateOrders =
    CALCULATE (
        [Order Count],
        FILTER ( fact_sales, DATEDIFF ( fact_sales[order_date], fact_sales[ship_date], DAY ) > 7 )
    )
RETURN
    DIVIDE ( LateOrders, TotalShipped, 0 )
```
**Purpose:** The inverse of % Shipped On Time — the fraction that miss the 7-day SLA. Both measures are reported for clarity on the dashboard.

---

## Time Intelligence

### Revenue LY
```dax
Revenue LY = CALCULATE ( [Revenue], SAMEPERIODLASTYEAR ( 'Date'[Date] ) )
```
**Purpose:** Revenue in the same period one year prior.

---

### Revenue YoY %
```dax
Revenue YoY % = DIVIDE ( [Revenue] - [Revenue LY], [Revenue LY], 0 )
```
**Purpose:** Year-over-year revenue growth as a percentage.

---

### Gross Margin % LY
```dax
Gross Margin % LY = CALCULATE ( [Gross Margin %], SAMEPERIODLASTYEAR ( 'Date'[Date] ) )
```
**Purpose:** Margin percentage in the same period one year prior.

---

### Gross Margin % YoY pts
```dax
Gross Margin % YoY pts = [Gross Margin %] - [Gross Margin % LY]
```
**Purpose:** Margin movement in percentage points (NOT as a ratio).
**Why percentage points:** A 2-point margin improvement is more meaningful to a CFO than a 5% relative change.

---

## Visual Formatting

These measures support conditional formatting in card visuals (color-coding arrows and percentages).

### #Customers YoY %
```dax
#Customers YoY % =
VAR NewCustLY = CALCULATE ( [New Customers CARD], SAMEPERIODLASTYEAR ( 'Date'[Date] ) )
VAR _perc = DIVIDE ( [New Customers CARD] - NewCustLY, NewCustLY, 0 )
VAR _format =
    SWITCH (
        TRUE (),
        _perc > 0, UNICHAR ( 11165 ) & " " & FORMAT ( _perc, "0.00%" ),
        _perc < 0, UNICHAR ( 11167 ) & " " & FORMAT ( _perc, "0.00%" ),
        FORMAT ( _perc, "0.00%" )
    )
RETURN
    _format
```
**Purpose:** Returns a formatted YoY percentage with an upward (▲) or downward (▼) arrow for visual reading.
**Note:** UNICHAR ( 11165 ) is ▲ ; UNICHAR ( 11167 ) is ▼.

---

### CF New Customers YoY %
```dax
CF New Customers YoY % =
VAR NewCustLY = CALCULATE ( [New Customers], SAMEPERIODLASTYEAR ( 'Date'[Date] ) )
VAR _perc = DIVIDE ( [New Customers] - NewCustLY, NewCustLY, 0 )
VAR _format =
    SWITCH (
        TRUE (),
        _perc > 0, "GREEN",
        _perc < 0, "RED",
        "GRAY"
    )
RETURN
    _format
```
**Purpose:** Returns a color name string ("GREEN" / "RED" / "GRAY") used in conditional formatting to color KPI cards by direction of change.

---

### New Customers CARD
```dax
New Customers CARD =
FORMAT (
    COUNTROWS (
        FILTER (
            'dim_customers',
            'dim_customers'[First Purchase Date] IN VALUES ( 'Date'[Date] )
        )
    ),
    "#,##0"
)
```
**Purpose:** Same logic as ``New Customers`` but returns a formatted string for display in card visuals (e.g., "1,234").

---

## Forward-Looking

### Maintenance Outreach Priority
```dax
Maintenance Outreach Priority =
CALCULATE (
    [Active Customers],
    dim_products[maintenance] = "Yes",
    dim_customers[Days Since Last Purchase] > 90
)
```
**Purpose:** Counts customers who:
1. Own a maintenance-eligible product (``dim_products[maintenance] = "Yes"``)
2. Haven't transacted in the last 90 days

This is the input pool for the Customer Service Director's quarterly outreach list. The Phase 3 prescriptive layer will rank these customers by segment value and produce an actionable target list.

---

## Design Principles Across All Measures

### ``DIVIDE`` Everywhere
Every ratio uses ``DIVIDE(numerator, denominator, alternativeResult)`` rather than the ``/`` operator. This:
- Prevents ``DIV/0`` errors when filter context produces zero
- Returns a specific fallback (usually 0) instead of blank

### Distinct Counts on Fact, Not Dimension
``DISTINCTCOUNT ( fact_sales[customer_key] )`` is used for ``Active Customers`` rather than counting rows of ``dim_customers``. This ensures only customers who actually transacted are counted; passive customer records are excluded.

### Variable-Heavy for Readability
Complex measures decompose into named variables (``VAR _perc = ...``) before the ``RETURN``. This makes the logic explicit and helps when debugging.

### Naming Convention
- Plain measure names (no prefixes) for primary business metrics: ``Revenue``, ``Active Customers``.
- ``CARD`` suffix for measures specifically formatted for card visuals.
- ``CF`` prefix for conditional-formatting helper measures.
- ``LY`` suffix for last-year comparisons; ``YoY %`` and ``YoY pts`` for year-over-year deltas.

### Coupling to ``dim_customers[First Purchase Date]``
Several measures depend on a calculated column ``First Purchase Date`` on ``dim_customers`` that derives each customer's earliest order date from ``fact_sales``. This is the workaround for the ``create_date`` data quality issue. The column is computed once at refresh, then referenced by ``New Customers``, ``Repeat Customers``, ``Acquisition Revenue``, and several formatting measures.