
-- GOLD LAYER DDL & STAR SCHEMA TRANSFORMATIONS
-- Dimensions (dim_customer, dim_product, dim_date, dim_geography) & Fact (fact_sales)

-- 1. Dimension: Geography
CREATE TABLE IF NOT EXISTS dim_geography AS
WITH distinct_countries AS (
    SELECT DISTINCT cntry AS country_name
    FROM silver_loc_a101
    WHERE cntry IS NOT NULL AND cntry != ''
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY country_name) AS geography_sk,
    CASE 
        WHEN country_name = 'United States' THEN 'US'
        WHEN country_name = 'Australia' THEN 'AU'
        WHEN country_name = 'Germany' THEN 'DE'
        WHEN country_name = 'United Kingdom' THEN 'UK'
        WHEN country_name = 'France' THEN 'FR'
        WHEN country_name = 'Canada' THEN 'CA'
        ELSE 'XX'
    END AS country_code,
    country_name,
    CASE 
        WHEN country_name IN ('United States', 'Canada') THEN 'North America'
        WHEN country_name IN ('Germany', 'United Kingdom', 'France') THEN 'Europe'
        WHEN country_name = 'Australia' THEN 'Pacific'
        ELSE 'Other'
    END AS region
FROM distinct_countries;

-- Add N/A record for missing geography joins
INSERT INTO dim_geography VALUES (0, 'NA', 'N/A', 'Unknown');

-- 2. Dimension: Date (Generates 2010 to 2015 range)
CREATE TABLE IF NOT EXISTS dim_date AS
WITH RECURSIVE date_range AS (
    SELECT DATE '2010-01-01' AS full_date
    UNION ALL
    SELECT full_date + INTERVAL 1 DAY
    FROM date_range
    WHERE full_date < DATE '2015-12-31'
)
SELECT 
    CAST(STRFTIME(full_date, '%Y%m%d') AS INT) AS date_sk,
    full_date,
    EXTRACT(DAY FROM full_date) AS day,
    DAYNAME(full_date) AS day_name,
    EXTRACT(MONTH FROM full_date) AS month,
    MONTHNAME(full_date) AS month_name,
    EXTRACT(QUARTER FROM full_date) AS quarter,
    EXTRACT(YEAR FROM full_date) AS year,
    EXTRACT(WEEK FROM full_date) AS week_of_year,
    EXTRACT(DAYOFWEEK FROM full_date) AS day_of_week,
    CASE WHEN EXTRACT(DAYOFWEEK FROM full_date) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend
FROM date_range;

-- 3. Dimension: Product (SCD Type 2 Structure)
CREATE TABLE IF NOT EXISTS dim_product AS
SELECT 
    ROW_NUMBER() OVER (ORDER BY p.prd_id) AS product_sk,
    p.prd_key AS product_business_key,
    p.sales_prd_key,
    p.prd_nm AS product_name,
    COALESCE(p.prd_cost, 0.00) AS product_cost,
    p.prd_line AS product_line,
    COALESCE(c.cat, 'N/A') AS category,
    COALESCE(c.subcat, 'N/A') AS subcategory,
    COALESCE(c.maintenance, 'No') AS maintenance,
    COALESCE(p.prd_start_dt, DATE '2003-01-01') AS effective_start_date,
    COALESCE(p.prd_end_dt, DATE '9999-12-31') AS effective_end_date,
    CASE WHEN p.prd_end_dt IS NULL OR p.prd_end_dt = DATE '9999-12-31' THEN 1 ELSE 0 END AS is_current
FROM silver_prd_info p
LEFT JOIN silver_px_cat_g1v2 c ON p.cat_id = c.id;

-- 4. Dimension: Customer (SCD Type 2 Structure)
CREATE TABLE IF NOT EXISTS dim_customer AS
WITH integrated AS (
    SELECT 
        c.cst_key AS customer_business_key,
        c.cst_id AS customer_id,
        c.cst_firstname AS first_name,
        c.cst_lastname AS last_name,
        c.cst_marital_status AS marital_status,
        -- Priority: Use ERP gender if CRM gender is missing/NA
        CASE 
            WHEN c.cst_gndr != 'N/A' THEN c.cst_gndr
            WHEN a.gen IS NOT NULL AND a.gen != 'N/A' THEN a.gen
            ELSE 'N/A'
        END AS gender,
        a.bdate AS birth_date,
        COALESCE(l.cntry, 'N/A') AS country,
        COALESCE(c.cst_create_date, DATE '2025-01-01') AS customer_create_date
    FROM silver_cust_info c
    LEFT JOIN silver_cust_az12 a ON c.cst_key = a.cid
    LEFT JOIN silver_loc_a101 l ON c.cst_key = l.cid
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY customer_id) AS customer_sk,
    customer_business_key,
    customer_id,
    first_name,
    last_name,
    gender,
    marital_status,
    birth_date,
    country,
    customer_create_date,
    customer_create_date AS effective_start_date,
    DATE '9999-12-31' AS effective_end_date,
    1 AS is_current
FROM integrated;

-- 5. Fact Table: Sales
CREATE TABLE IF NOT EXISTS fact_sales AS
WITH prd_map AS (
    SELECT 
        product_sk,
        sales_prd_key,
        effective_start_date,
        effective_end_date,
        is_current,
        ROW_NUMBER() OVER (
            PARTITION BY sales_prd_key 
            ORDER BY is_current DESC, effective_start_date DESC
        ) AS rank_fallback
    FROM dim_product
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY s.sls_ord_num, s.sls_order_dt) AS sales_sk,
    s.sls_ord_num AS order_number,
    CAST(STRFTIME(s.sls_order_dt, '%Y%m%d') AS INT) AS date_sk,
    COALESCE(c.customer_sk, 0) AS customer_sk,
    COALESCE(p_exact.product_sk, p_fallback.product_sk, 0) AS product_sk,
    COALESCE(g.geography_sk, 0) AS geography_sk,
    s.sls_order_dt AS order_date,
    s.sls_ship_dt AS ship_date,
    s.sls_due_dt AS due_date,
    s.sls_sales AS sales_amount,
    s.sls_quantity AS quantity,
    s.sls_price AS unit_price
FROM silver_sales_details s
LEFT JOIN dim_customer c ON s.sls_cust_id = c.customer_id AND c.is_current = 1
LEFT JOIN dim_product p_exact 
    ON s.sls_prd_key = p_exact.sales_prd_key 
   AND s.sls_order_dt BETWEEN p_exact.effective_start_date AND p_exact.effective_end_date
LEFT JOIN prd_map p_fallback 
    ON s.sls_prd_key = p_fallback.sales_prd_key 
   AND p_fallback.rank_fallback = 1
LEFT JOIN silver_loc_a101 l ON c.customer_business_key = l.cid
LEFT JOIN dim_geography g ON COALESCE(l.cntry, 'N/A') = g.country_name;
