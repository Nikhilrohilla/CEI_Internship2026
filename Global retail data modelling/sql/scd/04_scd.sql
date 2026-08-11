
-- SLOWLY CHANGING DIMENSIONS (SCD TYPE 2) DEMONSTRATION & UPDATE SCRIPT
-- Demonstrates customer record versioning on attribute updates.

-- Step 1: Expire Existing Version for Target Customer
UPDATE dim_customer
SET 
    effective_end_date = CURRENT_DATE,
    is_current = 0
WHERE customer_business_key = 'AW00011000' 
  AND is_current = 1;

-- Step 2: Insert New Version with New Surrogate Key
INSERT INTO dim_customer (
    customer_sk,
    customer_business_key,
    customer_id,
    first_name,
    last_name,
    gender,
    marital_status,
    birth_date,
    country,
    customer_create_date,
    effective_start_date,
    effective_end_date,
    is_current
)
SELECT 
    (SELECT MAX(customer_sk) + 1 FROM dim_customer) AS customer_sk,
    'AW00011000' AS customer_business_key,
    11000 AS customer_id,
    'Jon' AS first_name,
    'Yang' AS last_name,
    'Male' AS gender,
    'Married' AS marital_status,
    DATE '1971-10-06' AS birth_date,
    'Canada' AS country, -- Updated attribute (Moved from Australia to Canada)
    DATE '2025-10-06' AS customer_create_date,
    CURRENT_DATE AS effective_start_date,
    DATE '9999-12-31' AS effective_end_date,
    1 AS is_current;
