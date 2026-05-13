/*
===============================================================================
Stored Procedure: Load Silver Layer (Bronze -> Silver)
===============================================================================
Script Purpose:
    This stored procedure performs the ETL (Extract, Transform, Load) process to 
    populate the 'silver' schema tables from the 'bronze' schema.
	Actions Performed:
		- Truncates Silver tables.
		- Inserts transformed and cleansed data from Bronze into Silver tables.
		
Parameters:
    None. 
	  This stored procedure does not accept any parameters or return any values.

Usage Example:
    CALL Silver.load_silver;
===============================================================================
*/

CREATE OR REPLACE PROCEDURE silver.load_silver()
	LANGUAGE plpgsql
	AS $$
	DECLARE 
		start_time TIMESTAMP;
		end_time TIMESTAMP;
		table_start TIMESTAMP;
		table_end TIMESTAMP;
	BEGIN
		start_time := clock_timestamp();
		RAISE NOTICE '=============================================================';
		RAISE NOTICE 'Loading Silver Layer Started at: %', start_time;
		RAISE NOTICE '=============================================================';

		BEGIN	
			RAISE NOTICE '---------------------------------------------------------';
			RAISE NOTICE 'Loading CRM Tables';
			RAISE NOTICE '---------------------------------------------------------';
			
			table_start := clock_timestamp();
			RAISE NOTICE '>> Truncating table silver.crm_cust_info', to_char(table_start, 'HH24:MI:SS'); 
			TRUNCATE TABLE silver.crm_cust_info;
			RAISE NOTICE '>> Inserting Data Into: silver.crm_cust_info';
			INSERT INTO silver.crm_cust_info(
			cst_id,
			cst_key,
			cst_firstname,
			cst_lastname,
			cst_marital_status,
			cst_gndr,
			cst_create_date
			)
			
			SELECT 
			cst_id,
			cst_key,
			TRIM(cst_firstname) cst_firstname,
			TRIM(cst_lastname) cst_lastname,
			CASE WHEN UPPER(TRIM(cst_marital_status)) ='S' THEN 'Single'
			     WHEN UPPER(TRIM(cst_marital_status)) ='M' THEN 'Married' -- Normalize for readable format
				 ELSE 'n/a' 
			END cst_marital_status,
			CASE WHEN UPPER(TRIM(cst_gndr)) ='F' THEN 'Female'
				 WHEN UPPER(TRIM(cst_gndr)) ='M' THEN 'Male'
				 ELSE 'n/a'
			END cst_gndr,
			cst_create_date
			FROM --remove duplicates and filtering
			(
			SELECT *
			FROM(
			SELECT 
			*,
			ROW_NUMBER() OVER(PARTITION BY cst_key ORDER BY  cst_create_date DESC) flag_last
			FROM bronze.crm_cust_info
			WHERE cst_id IS NOT NULL)
			WHERE flag_last = 1); 
			table_end := clock_timestamp();
			RAISE NOTICE '   ✓ Completed bronze.crm_cust_info in % seconds', EXTRACT(EPOCH FROM (table_end - table_start));
			
			table_start := clock_timestamp();
			RAISE NOTICE '>> Truncating table silver.crm_prd_info', to_char(table_start, 'HH24:MI:SS'); 
			TRUNCATE TABLE silver.crm_prd_info;
			RAISE NOTICE '>> Inserting Data Into: silver.crm_prd_info'; 
			INSERT INTO silver.crm_prd_info(
				prd_id,   
				cat_id,
			    prd_key,
			    prd_nm,
			    prd_cost,
			    prd_line,
			    prd_start_dt,
			    prd_end_dt
			)
			
			SELECT
			prd_id,
			REPLACE(LEFT(prd_key, 5), '-', '_') cat_id, -- Extract categoriy ID
			SUBSTRING(prd_key from 7) prd_key,          -- Extract product key
			prd_nm,
			COALESCE(prd_cost,0) prd_cost,
			CASE WHEN UPPER(TRIM(prd_line)) = 'M' THEN 'Mountain'
				 WHEN UPPER(TRIM(prd_line)) = 'R' THEN 'Road'
				 WHEN UPPER(TRIM(prd_line)) = 'S' THEN 'Other Sales'
				 WHEN UPPER(TRIM(prd_line)) = 'T' THEN 'Touring'
				 ELSE 'n/a'
			END prd_line, -- Map product line codes to descriptive values
			prd_start_dt,
			LEAD(prd_start_dt) OVER(PARTITION BY prd_key ORDER BY prd_start_dt)-1 prd_end_dt -- Calculate the end date as one day before the next start date
			FROM bronze.crm_prd_info;
			table_end := clock_timestamp();
			RAISE NOTICE '   ✓ Completed bronze.crm_cust_info in % seconds', EXTRACT(EPOCH FROM (table_end - table_start));
			
			table_start := clock_timestamp();
			RAISE NOTICE '>> Truncating table silver.crm_sales_details', to_char(table_start, 'HH24:MI:SS'); 
			TRUNCATE TABLE silver.crm_sales_details;
			RAISE NOTICE '>> Inserting Data Into: silver.crm_sales_details'; 
			INSERT INTO silver.crm_sales_details(
			sls_ord_num ,
			    sls_prd_key ,
			    sls_cust_id  ,
			    sls_order_dt ,
			    sls_ship_dt  ,
			    sls_due_dt   ,
			    sls_sales    ,
			    sls_quantity ,
			    sls_price
			)
			
			SELECT
			sls_ord_num,
			sls_prd_key,
			sls_cust_id,
			CASE WHEN sls_order_dt <= 0 OR LENGTH(sls_order_dt :: TEXT) != 8 THEN NULL
				 ELSE TO_DATE(sls_order_dt::TEXT, 'YYYYMMDD')
				 END sls_order_dt,
			CASE WHEN sls_ship_dt <= 0 OR LENGTH(sls_ship_dt :: TEXT) != 8 THEN NULL
				 ELSE TO_DATE(sls_ship_dt::TEXT, 'YYYYMMDD')
				 END sls_ship_dt,
			CASE WHEN sls_due_dt <= 0 OR LENGTH(sls_due_dt :: TEXT) != 8 THEN NULL
				 ELSE TO_DATE(sls_due_dt::TEXT, 'YYYYMMDD')
				 END sls_due_dt,
			CASE WHEN sls_sales IS NULL OR sls_sales<=0 OR sls_sales != sls_quantity * ABS(sls_price) THEN sls_quantity * ABS(sls_price)
				 ELSE sls_sales
			END sls_sales,
			sls_quantity,
			CASE WHEN  sls_price IS NULL OR sls_price <=0 THEN sls_sales / NULLIF(sls_quantity, 0)
				 ELSE sls_price
			END sls_price	
			FROM bronze.crm_sales_details;
			table_end := clock_timestamp();
			RAISE NOTICE '   ✓ Completed bronze.crm_cust_info in % seconds', EXTRACT(EPOCH FROM (table_end - table_start));

			RAISE NOTICE '---------------------------------------------------------';
			RAISE NOTICE 'Loading ERP Tables';
			RAISE NOTICE '---------------------------------------------------------';
			
			table_start := clock_timestamp();
			RAISE NOTICE '>> Truncating table silver.erp_cust_az12', to_char(table_start, 'HH24:MI:SS'); 
			TRUNCATE TABLE silver.erp_cust_az12;
			RAISE NOTICE '>> Inserting Data Into: silver.erp_cust_az12'; 
			INSERT INTO silver.erp_cust_az12 (
			cid,
			bdate,
			gen
			)
			SELECT
			CASE WHEN cid LIKE 'NAS%' THEN SUBSTRING(cid FROM 4) -- Remove 'NAS' prefix if present
				ELSE cid
			END AS cid, 
			CASE WHEN bdate > clock_timestamp() THEN NULL
				 ELSE bdate
			END AS bdate, -- Set future birthdates to NULL
			CASE WHEN UPPER(TRIM(gen)) IN ('F', 'FEMALE') THEN 'Female'
				 WHEN UPPER(TRIM(gen)) IN ('M', 'MALE') THEN 'Male'
				 ELSE 'n/a'
			END AS gen -- Normalize gender values and handle unknown cases
			FROM bronze.erp_cust_az12;
			table_end := clock_timestamp();
			RAISE NOTICE '   ✓ Completed bronze.crm_cust_info in % seconds', EXTRACT(EPOCH FROM (table_end - table_start));
			
			table_start := clock_timestamp();
			RAISE NOTICE '>> Truncating table silver.erp_loc_a101', to_char(table_start, 'HH24:MI:SS'); 
			TRUNCATE TABLE silver.erp_loc_a101;
			RAISE NOTICE '>> Inserting Data Into: silver.erp_loc_a101'; 
			INSERT INTO silver.erp_loc_a101(
			cid,
			cntry
			)
			
			SELECT
			REPLACE(cid, '-', '') cid,
			CASE WHEN TRIM(cntry) = 'DE' THEN 'Germany'
			     WHEN TRIM(cntry) IN ('US', 'USA') THEN 'United States'
				 WHEN TRIM(cntry) ='' OR cntry IS NULL THEN 'n/a'
			ELSE TRIM(cntry)
			END cntry
			FROM bronze.erp_loc_a101;
			table_end := clock_timestamp();
			RAISE NOTICE '   ✓ Completed bronze.crm_cust_info in % seconds', EXTRACT(EPOCH FROM (table_end - table_start));
		
			table_start := clock_timestamp();
			RAISE NOTICE '>> Truncating table silver.erp_px_cat_g1v2', to_char(table_start, 'HH24:MI:SS'); 
			TRUNCATE TABLE silver.erp_px_cat_g1v2;
			RAISE NOTICE '>> Inserting Data Into: silver.erp_px_cat_g1v2'; 
			INSERT INTO silver.erp_px_cat_g1v2(
			id,
			cat,
			subcat,
			maintenance
			)
			
			SELECT 
			id,
			cat,
			subcat,
			maintenance
			FROM bronze.erp_px_cat_g1v2;
			table_end := clock_timestamp();
			RAISE NOTICE '   ✓ Completed bronze.crm_cust_info in % seconds', EXTRACT(EPOCH FROM (table_end - table_start));
		
		EXCEPTION
			WHEN OTHERS THEN
				RAISE NOTICE '===================================================';
				RAISE NOTICE '⚠️ ERROR OCCURED DURING LOADING SILVER LAYER';
				RAISE NOTICE 'Error Message: %', SQLERRM;
				RAISE NOTICE 'Error State: %', SQLSTATE;
				RAISE NOTICE '===================================================';
		END;

		end_time := clock_timestamp();
		RAISE NOTICE '===================================================';
		RAISE NOTICE 'Silver layer load finished at: %', end_time;
		RAISE NOTICE 'Total_duration: % seconds', EXTRACT(EPOCH FROM (end_time - start_time));
		RAISE NOTICE '===================================================';
	END; 
	$$
