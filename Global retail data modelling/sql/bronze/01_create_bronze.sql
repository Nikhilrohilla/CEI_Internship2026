
-- BRONZE LAYER DDL - RAW INGESTION & AUDIT METADATA
-- Preserves original source schema without business transformations.

-- CRM Customer Info
CREATE TABLE IF NOT EXISTS bronze_cust_info (
    cst_id VARCHAR,
    cst_key VARCHAR,
    cst_firstname VARCHAR,
    cst_lastname VARCHAR,
    cst_marital_status VARCHAR,
    cst_gndr VARCHAR,
    cst_create_date VARCHAR,
    -- Audit Metadata
    source_file VARCHAR,
    ingestion_timestamp VARCHAR,
    batch_id VARCHAR,
    record_hash VARCHAR
);

-- ERP Customer Demographics
CREATE TABLE IF NOT EXISTS bronze_cust_az12 (
    cid VARCHAR,
    bdate VARCHAR,
    gen VARCHAR,
    -- Audit Metadata
    source_file VARCHAR,
    ingestion_timestamp VARCHAR,
    batch_id VARCHAR,
    record_hash VARCHAR
);

-- ERP Customer Location
CREATE TABLE IF NOT EXISTS bronze_loc_a101 (
    cid VARCHAR,
    cntry VARCHAR,
    -- Audit Metadata
    source_file VARCHAR,
    ingestion_timestamp VARCHAR,
    batch_id VARCHAR,
    record_hash VARCHAR
);

-- CRM Product Info
CREATE TABLE IF NOT EXISTS bronze_prd_info (
    prd_id VARCHAR,
    prd_key VARCHAR,
    prd_nm VARCHAR,
    prd_cost VARCHAR,
    prd_line VARCHAR,
    prd_start_dt VARCHAR,
    prd_end_dt VARCHAR,
    -- Audit Metadata
    source_file VARCHAR,
    ingestion_timestamp VARCHAR,
    batch_id VARCHAR,
    record_hash VARCHAR
);

-- ERP Product Category Lookup
CREATE TABLE IF NOT EXISTS bronze_px_cat_g1v2 (
    id VARCHAR,
    cat VARCHAR,
    subcat VARCHAR,
    maintenance VARCHAR,
    -- Audit Metadata
    source_file VARCHAR,
    ingestion_timestamp VARCHAR,
    batch_id VARCHAR,
    record_hash VARCHAR
);

-- CRM Sales Details
CREATE TABLE IF NOT EXISTS bronze_sales_details (
    sls_ord_num VARCHAR,
    sls_prd_key VARCHAR,
    sls_cust_id VARCHAR,
    sls_order_dt VARCHAR,
    sls_ship_dt VARCHAR,
    sls_due_dt VARCHAR,
    sls_sales VARCHAR,
    sls_quantity VARCHAR,
    sls_price VARCHAR,
    -- Audit Metadata
    source_file VARCHAR,
    ingestion_timestamp TIMESTAMP,
    batch_id VARCHAR,
    record_hash VARCHAR
);
