/*
===============================================================================
Stored Procedure: Load Bronze Layer (Source -> Bronze)
===============================================================================
Script Purpose:
    This stored procedure loads data into the 'bronze' schema from external CSV files. 
    It performs the following actions:
    - Truncates the bronze tables before loading data.
    - Uses the `COPY` command to load data from csv Files to bronze tables.

Parameters:
    None. 
	  This stored procedure does not accept any parameters or return any values.

Usage Example:
    CALL bronze.load_bronze();
===============================================================================
*/
CREATE OR REPLACE PROCEDURE bronze.load_bronze()
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
		RAISE NOTICE 'Loading Bronze Layer Started at: %', start_time;
		RAISE NOTICE '=============================================================';
		
		BEGIN	
			RAISE NOTICE '---------------------------------------------------------';
			RAISE NOTICE 'Loading CRM Tables';
			RAISE NOTICE '---------------------------------------------------------';
		
			table_start := clock_timestamp();
			RAISE NOTICE '>> [%] Truncating Table: bronze.crm_cust_info', to_char(table_start, 'HH24:MI:SS');
			TRUNCATE TABLE bronze.crm_cust_info;
			EXECUTE $sql$
				COPY bronze.crm_cust_info
				FROM 'C:\adventureworks\datasets\source_crm\cust_info.csv'
				DELIMITER ','             -- fields separated by commas
				CSV HEADER;               -- skip header row in CSV
			$sql$;
			table_end := clock_timestamp();
			RAISE NOTICE '   ✓ Completed bronze.crm_cust_info in % seconds', EXTRACT(EPOCH FROM (table_end - table_start));
		
			table_start := clock_timestamp();
			RAISE NOTICE '>> [%] Truncating Table: bronze.crm_prd_info', to_char(table_start, 'HH24:MI:SS');
			TRUNCATE TABLE bronze.crm_prd_info;
			EXECUTE $sql$
				COPY bronze.crm_prd_info
				FROM 'C:\adventureworks\datasets\source_crm\prd_info.csv'
				DELIMITER ','             -- fields separated by commas
				CSV HEADER;               -- skip header row in CSV
			$sql$;
			table_end := clock_timestamp();
			RAISE NOTICE '   ✓ Completed bronze.crm_cust_info in % seconds', EXTRACT(EPOCH FROM (table_end - table_start));

			table_start := clock_timestamp();
			RAISE NOTICE '>> [%] Truncating Table: bronze.crm_sales_details', to_char(table_start, 'HH24:MI:SS');
			TRUNCATE TABLE bronze.crm_sales_details;
			EXECUTE $sql$
				COPY bronze.crm_sales_details
				FROM 'C:\adventureworks\datasets\source_crm\sales_details.csv'
				DELIMITER ','             -- fields separated by commas
				CSV HEADER;               -- skip header row in CSV
			$sql$;
			table_end := clock_timestamp();
			RAISE NOTICE '   ✓ Completed bronze.crm_cust_info in % seconds', EXTRACT(EPOCH FROM (table_end - table_start));
			
			RAISE NOTICE '---------------------------------------------------------';
			RAISE NOTICE 'Loading ERP Tables';
			RAISE NOTICE '---------------------------------------------------------';
			
			table_start := clock_timestamp();
			RAISE NOTICE '>> [%] Truncating Table: bronze.erp_cust_az12', to_char(table_start, 'HH24:MI:SS');
			TRUNCATE TABLE bronze.erp_cust_az12;
			EXECUTE $sql$
			    COPY bronze.erp_cust_az12
				FROM 'C:\adventureworks\datasets\source_erp\cust_az12.csv'
				DELIMITER ','             -- fields separated by commas
				CSV HEADER;               -- skip header row in CSV
			$sql$;
			table_end := clock_timestamp();
			RAISE NOTICE '   ✓ Completed bronze.crm_cust_info in % seconds', EXTRACT(EPOCH FROM (table_end - table_start));

			table_start := clock_timestamp();
			RAISE NOTICE '>> [%] Truncating Table: bronze.erp_loc_a101', to_char(table_start, 'HH24:MI:SS');
			TRUNCATE TABLE bronze.erp_loc_a101;

			EXECUTE $sql$
				COPY bronze.erp_loc_a101
				FROM 'C:\adventureworks\datasets\source_erp\loc_a101.csv'
				DELIMITER ','             -- fields separated by commas
				CSV HEADER;               -- skip header row in CSV
			$sql$;
			table_end := clock_timestamp();
			RAISE NOTICE '   ✓ Completed bronze.crm_cust_info in % seconds', EXTRACT(EPOCH FROM (table_end - table_start));
			
			table_start := clock_timestamp();
			RAISE NOTICE '>> [%] Truncating Table: bronze.erp_px_cat_g1v2', to_char(table_start, 'HH24:MI:SS');
			TRUNCATE TABLE bronze.erp_px_cat_g1v2;
			EXECUTE $sql$
				COPY bronze.erp_px_cat_g1v2
				FROM 'C:\adventureworks\datasets\source_erp\px_cat_g1v2.csv'
				DELIMITER ','             -- fields separated by commas
				CSV HEADER;               -- skip header row in CSV
			$sql$;
			table_end := clock_timestamp();
			RAISE NOTICE '   ✓ Completed bronze.crm_cust_info in % seconds', EXTRACT(EPOCH FROM (table_end - table_start));
			
		EXCEPTION
		WHEN OTHERS THEN
		RAISE NOTICE '===================================================';
		RAISE NOTICE '⚠️ ERROR OCCURED DURING LOADING BRONZE LAYER';
		RAISE NOTICE 'Error Message: %', SQLERRM;
		RAISE NOTICE 'Error State: %', SQLSTATE;
		RAISE NOTICE '===================================================';
		END;

		end_time := clock_timestamp();
		RAISE NOTICE '===================================================';
		RAISE NOTICE 'Bronze layer load finished at: %', end_time;
		RAISE NOTICE 'Total_duration: % seconds', EXTRACT(EPOCH FROM (end_time - start_time));
		RAISE NOTICE '===================================================';
END;
$$
