# Data Quality Findings

A working analyst doesn't just build dashboards on top of the data they're given — they interrogate the data first. This document records the data quality issues discovered during this project, the business impact of each, and the mitigation applied.

## Finding #1 — Customer Create Date Contamination

### Observation

All values in `dim_customers.create_date` fall in 2025–2026, while sales transactions in `fact_sales` span 2010 through mid-2014. This is logically impossible: a customer cannot place an order in 2013 against an account that didn't exist until 2025.

### Discovery Path

The issue surfaced while building the `New Customers` measure in Power BI. Filtering customers by `create_date` against a `Date[Year] = 2013` filter returned zero customers — the inactive relationship was correctly configured, but no customer record had a create_date falling in 2013.

A quick range check confirmed:

```dax
MIN Create Date = MIN ( dim_customers[create_date] )    -- returned 2025-10-06
MAX Create Date = MAX ( dim_customers[create_date] )    -- returned 2026-01-15
```

While the latest order date in `fact_sales` was June 28, 2014.

### Root Cause Hypothesis

The most likely explanation is **refresh-date contamination**: the source ETL captured `create_date` as the timestamp at which the record was loaded into the warehouse, not the timestamp at which the customer actually signed up. This is a common bug in legacy CRM exports — the field gets overwritten on every refresh.

Other possible causes:
- Migration from a prior CRM system, where the new system stamped `create_date` with the migration date for every imported customer.
- A data refresh script that updates `create_date` nightly by accident, turning it into "last seen" rather than "first seen."

### Business Impact

Any "customer acquisition" or "cohort" analysis based on this field would be misleading. Specifically:
- A naive "new customers per year" report would show zero before 2025 and all customers in 2025–2026, suggesting the business only acquired customers in those two years.
- Cohort retention curves anchored on `create_date` would all start in 2025, making any retention measurement nonsensical.

### Mitigation Applied

Redefined "New Customer" as **a customer whose first purchase falls in the period**, computed from `fact_sales` rather than `dim_customers.create_date`. The DAX:

```dax
First Purchase Date =
CALCULATE (
    MIN ( fact_sales[order_date] ),
    ALLEXCEPT ( fact_sales, fact_sales[customer_key] )
)

New Customers =
COUNTROWS (
    FILTER (
        VALUES ( fact_sales[customer_key] ),
        VAR fp =
            CALCULATE (
                MIN ( fact_sales[order_date] ),
                ALL ( 'Date' )
            )
        RETURN fp >= MIN ( 'Date'[Date] ) && fp <= MAX ( 'Date'[Date] )
    )
)
```

This is also a **more business-meaningful** definition: it measures customers who started buying in a period, not customers whose record was created. For most analyses, that's what stakeholders actually want anyway.

### Recommended Source Fix

Investigate the source ETL to determine whether actual signup dates exist upstream in the operational CRM. If they do, capture them properly into the warehouse. If they don't, the field should be renamed (`record_loaded_at` or similar) to prevent future analysts from making the same mistake.

---

## Finding #2 — Sales Amount Inconsistencies

### Observation

Some rows in `bronze.crm_sales_details` had `sales_amount` values that did not equal `quantity × price`. A few rows had negative or null prices.

### Mitigation Applied

In the silver layer transformation, recompute `sales_amount` from `quantity × price` whenever the stored value disagrees or is non-positive. For rows where price is missing or non-positive but sales and quantity are valid, derive price as `sales / quantity`.

This is a one-line silver-layer fix and a common pattern in any retail data pipeline.

---

## Finding #3 — Inconsistent Country Codes

### Observation

The `cntry` field in `bronze.erp_loc_a101` contained a mix of full country names, two-letter codes (`US`, `DE`, `UK`), and three-letter codes (`USA`), plus blank values.

### Mitigation Applied

Silver-layer normalization to full country names, with blanks mapped to `n/a`. Tableau / Power BI dashboards filter out the `n/a` country row by default.

---

## Finding #4 — Discontinued Products in Active Catalogue

### Observation

The product table contains both currently-sold products and historical versions of products that have been replaced or discontinued. The `prd_end_dt` column marks discontinued products, but the column was not consistently filtered in upstream reports.

### Mitigation Applied

The gold-layer `dim_products` view filters to `prd_end_dt IS NULL` (active products only). Historical products are still available in silver for trend analysis. Every BI visual reading from `dim_products` therefore reflects the active catalogue by default.

---

## Finding #5 — Integer Date Format in Sales Table

### Observation

The `sls_order_dt`, `sls_ship_dt`, and `sls_due_dt` fields in `bronze.crm_sales_details` are stored as `INT` in `YYYYMMDD` format (e.g., `20130415` for April 15, 2013). This is a legacy ERP convention. Some rows had `0` where dates were missing.

### Mitigation Applied

Silver-layer conversion to proper `DATE` type, with `0` and invalid values mapped to `NULL`. The gold-layer fact table exposes proper date types, enabling all downstream date arithmetic (ship lag, seasonality analysis) to work cleanly.

---

## How This Document Is Used

This document is part of the project deliverable. It demonstrates:

1. That the analyst interrogated the data rather than accepting it at face value.
2. That data quality issues were identified, root-caused, and mitigated rather than ignored.
3. That mitigations were documented so future maintainers understand why the warehouse logic looks the way it does.

For an analyst's portfolio, this is the most valuable single document in the project. Every interviewer asks some version of *"tell me about a time you found a data quality issue."* This file is the answer.
