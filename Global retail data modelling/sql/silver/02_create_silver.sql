
-- SILVER LAYER DDL & TRANSFORMATION LOGIC
-- Data Cleaning, Standardization, Normalization, Validation, and Deduplication

-- 1. Silver CRM Customer Info
CREATE TABLE IF NOT EXISTS silver_cust_info AS
WITH cleaned AS (
    SELECT 
        CAST(cst_id AS INT) AS cst_id,
        TRIM(cst_key) AS cst_key,
        TRIM(cst_firstname) AS cst_firstname,
        TRIM(cst_lastname) AS cst_lastname,
        CASE 
            WHEN UPPER(TRIM(cst_marital_status)) = 'M' THEN 'Married'
            WHEN UPPER(TRIM(cst_marital_status)) = 'S' THEN 'Single'
            ELSE 'N/A'
        END AS cst_marital_status,
        CASE 
            WHEN UPPER(TRIM(cst_gndr)) = 'M' THEN 'Male'
            WHEN UPPER(TRIM(cst_gndr)) = 'F' THEN 'Female'
            ELSE 'N/A'
        END AS cst_gndr,
        TRY_CAST(cst_create_date AS DATE) AS cst_create_date,
        ROW_NUMBER() OVER (
            PARTITION BY TRIM(cst_key) 
            ORDER BY TRY_CAST(cst_create_date AS DATE) DESC, cst_id DESC
        ) AS dedup_rank
    FROM bronze_cust_info
    WHERE cst_id IS NOT NULL 
      AND TRY_CAST(cst_id AS INT) IS NOT NULL
      AND cst_key IS NOT NULL
      AND TRIM(cst_key) != ''
)
SELECT 
    cst_id,
    cst_key,
    cst_firstname,
    cst_lastname,
    cst_marital_status,
    cst_gndr,
    cst_create_date
FROM cleaned
WHERE dedup_rank = 1;

-- 2. Silver ERP Customer Demographics
CREATE TABLE IF NOT EXISTS silver_cust_az12 AS
SELECT 
    TRIM(REPLACE(cid, 'NAS', '')) AS cid,
    TRY_CAST(bdate AS DATE) AS bdate,
    CASE 
        WHEN UPPER(TRIM(gen)) IN ('MALE', 'M') THEN 'Male'
        WHEN UPPER(TRIM(gen)) IN ('FEMALE', 'F') THEN 'Female'
        ELSE 'N/A'
    END AS gen
FROM bronze_cust_az12
WHERE cid IS NOT NULL AND TRIM(cid) != '';

-- 3. Silver ERP Customer Location
CREATE TABLE IF NOT EXISTS silver_loc_a101 AS
SELECT 
    TRIM(REPLACE(cid, '-', '')) AS cid,
    CASE 
        WHEN UPPER(TRIM(cntry)) IN ('US', 'USA', 'UNITED STATES') THEN 'United States'
        WHEN UPPER(TRIM(cntry)) IN ('DE', 'GERMANY') THEN 'Germany'
        WHEN UPPER(TRIM(cntry)) = 'AUSTRALIA' THEN 'Australia'
        WHEN UPPER(TRIM(cntry)) = 'UNITED KINGDOM' THEN 'United Kingdom'
        WHEN UPPER(TRIM(cntry)) = 'FRANCE' THEN 'France'
        WHEN UPPER(TRIM(cntry)) = 'CANADA' THEN 'Canada'
        ELSE 'N/A'
    END AS cntry
FROM bronze_loc_a101
WHERE cid IS NOT NULL AND TRIM(cid) != '';

-- 4. Silver CRM Product Info
CREATE TABLE IF NOT EXISTS silver_prd_info AS
WITH cleaned_prd AS (
    SELECT 
        CAST(prd_id AS INT) AS prd_id,
        TRIM(prd_key) AS prd_key,
        TRIM(prd_nm) AS prd_nm,
        TRY_CAST(prd_cost AS NUMERIC(10,2)) AS prd_cost,
        CASE 
            WHEN UPPER(TRIM(prd_line)) = 'R' THEN 'Road'
            WHEN UPPER(TRIM(prd_line)) = 'M' THEN 'Mountain'
            WHEN UPPER(TRIM(prd_line)) = 'T' THEN 'Touring'
            WHEN UPPER(TRIM(prd_line)) = 'S' THEN 'Standard'
            ELSE 'N/A'
        END AS prd_line,
        -- Correct date anomalies where start > end date by swapping
        CASE 
            WHEN TRY_CAST(prd_start_dt AS DATE) > TRY_CAST(prd_end_dt AS DATE) 
            THEN TRY_CAST(prd_end_dt AS DATE)
            ELSE TRY_CAST(prd_start_dt AS DATE)
        END AS prd_start_dt,
        CASE 
            WHEN TRY_CAST(prd_start_dt AS DATE) > TRY_CAST(prd_end_dt AS DATE) 
            THEN TRY_CAST(prd_start_dt AS DATE)
            ELSE TRY_CAST(prd_end_dt AS DATE)
        END AS prd_end_dt,
        -- Derive Category Lookup Key 
        REGEXP_EXTRACT(TRIM(prd_key), '^([^-]+-[^-]+)', 1) AS raw_cat_prefix,
        -- Derive Sales Product Key Suffix
        SUBSTR(TRIM(prd_key), POSITION('-' IN SUBSTR(TRIM(prd_key), POSITION('-' IN TRIM(prd_key)) + 1)) + POSITION('-' IN TRIM(prd_key)) + 1) AS sales_prd_key
    FROM bronze_prd_info
    WHERE prd_id IS NOT NULL AND TRY_CAST(prd_id AS INT) IS NOT NULL
)
SELECT 
    prd_id,
    prd_key,
    prd_nm,
    prd_cost,
    prd_line,
    prd_start_dt,
    prd_end_dt,
    REPLACE(raw_cat_prefix, '-', '_') AS cat_id,
    sales_prd_key
FROM cleaned_prd;

-- 5. Silver ERP Product Category Lookup
CREATE TABLE IF NOT EXISTS silver_px_cat_g1v2 AS
SELECT 
    TRIM(id) AS id,
    TRIM(cat) AS cat,
    TRIM(subcat) AS subcat,
    TRIM(maintenance) AS maintenance
FROM bronze_px_cat_g1v2
WHERE id IS NOT NULL AND TRIM(id) != '';

-- 6. Silver CRM Sales Details
CREATE TABLE IF NOT EXISTS silver_sales_details AS
WITH parsed_sales AS (
    SELECT 
        TRIM(sls_ord_num) AS sls_ord_num,
        TRIM(sls_prd_key) AS sls_prd_key,
        CAST(sls_cust_id AS INT) AS sls_cust_id,
        TRY_CAST(STRPTIME(sls_order_dt, '%Y%m%d') AS DATE) AS sls_order_dt,
        TRY_CAST(STRPTIME(sls_ship_dt, '%Y%m%d') AS DATE) AS sls_ship_dt,
        TRY_CAST(STRPTIME(sls_due_dt, '%Y%m%d') AS DATE) AS sls_due_dt,
        ABS(TRY_CAST(sls_quantity AS INT)) AS raw_quantity,
        ABS(TRY_CAST(sls_price AS NUMERIC(10,2))) AS raw_price,
        TRY_CAST(sls_sales AS NUMERIC(12,2)) AS raw_sales
    FROM bronze_sales_details
    WHERE sls_ord_num IS NOT NULL 
      AND TRIM(sls_ord_num) != ''
      AND sls_order_dt IS NOT NULL
      AND sls_order_dt != '0'
      AND LENGTH(TRIM(sls_order_dt)) = 8
)
SELECT 
    sls_ord_num,
    sls_prd_key,
    sls_cust_id,
    sls_order_dt,
    sls_ship_dt,
    sls_due_dt,
    COALESCE(raw_quantity, 1) AS sls_quantity,
    CASE 
        WHEN raw_price IS NOT NULL AND raw_price > 0 THEN raw_price
        WHEN raw_sales IS NOT NULL AND raw_quantity > 0 THEN ROUND(raw_sales / raw_quantity, 2)
        ELSE 0.00
    END AS sls_price,
    CASE 
        WHEN raw_quantity > 0 AND raw_price > 0 THEN ROUND(raw_quantity * raw_price, 2)
        WHEN raw_sales IS NOT NULL AND raw_sales > 0 THEN raw_sales
        ELSE 0.00
    END AS sls_sales
FROM parsed_sales;
