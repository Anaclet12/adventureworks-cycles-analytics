/*
===============================================================================
DDL Script: Create Gold Views
===============================================================================
Script Purpose:
    This script creates views for the Gold layer in the data warehouse. 
    The Gold layer represents the final dimension and fact tables (Star Schema)

    Each view performs transformations and combines data from the Silver layer 
    to produce a clean, enriched, and business-ready dataset.

Usage:
    - These views can be queried directly for analytics and reporting.
===============================================================================
*/

-- =============================================================================
-- Create Dimension: gold.dim_customers
-- =============================================================================
DROP IF EXISTS VIEW gold.dim_customers;
CREATE VIEW gold.dim_customers AS
SELECT 
ROW_NUMBER() OVER(ORDER BY cst_key) customer_key,
a.cst_id customer_id,
a.cst_key customer_number,
a.cst_firstname first_name,
a.cst_lastname last_name,
c.cntry country,
a.cst_marital_status marital_status,
CASE WHEN a.cst_gndr != 'n/a' THEN a.cst_gndr
	 ELSE COALESCE(b.gen, 'n/a')
END gender, 
b.bdate birthdate,
a.cst_create_date create_date
FROM silver.crm_cust_info a
LEFT JOIN silver.erp_cust_az12 b
ON        a.cst_key = b.cid
LEFT JOIN silver.erp_loc_a101 c
ON        a.cst_key = C.cid
-- =============================================================================
-- Create Dimension: gold.dim_products
-- =============================================================================
DROP IF EXISTS VIEW gold.dim_products;
CREATE VIEW gold.dim_products AS
SELECT
ROW_NUMBER() OVER(ORDER BY a.prd_start_dt, a.prd_id) product_key,
a.prd_id product_id,
a.prd_key product_number,
a.prd_nm product_name,
a.cat_id category_id,
b.cat category,
b.subcat subcategory,
b.maintenance,
a.prd_cost cost,
a.prd_line product_line,
a.prd_start_dt start_date
FROM silver.crm_prd_info a
JOIN silver.erp_px_cat_g1v2 b
ON        a.cat_id = b.id
WHERE prd_end_dt IS NULL --Filter out all historical data  
-- =============================================================================
-- Create Fact: gold.fact_sales
-- =============================================================================
DROP IF EXISTS VIEW gold.fact_sales;
CREATE VIEW gold.fact_sales AS
SELECT
a.sls_ord_num order_number,
b.product_key,
c.customer_key,
a.sls_order_dt order_date,
a.sls_ship_dt ship_date,
a.sls_due_dt due_date,
a.sls_sales sales_amount,
a.sls_quantity quantity,
a.sls_price price
FROM silver.crm_sales_details a
LEFT JOIN gold.dim_products b
ON        a.sls_prd_key = b.product_number
LEFT JOIN gold.dim_customers c
ON        a.sls_cust_id = c.customer_id
