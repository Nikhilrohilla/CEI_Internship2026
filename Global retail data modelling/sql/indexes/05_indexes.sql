
-- PERFORMANCE OPTIMIZATION INDEXES
-- Creates indexes on Surrogate Keys, Business Keys, and Foreign Keys

-- Customer Dimension Indexes
CREATE INDEX IF NOT EXISTS idx_dim_customer_sk ON dim_customer (customer_sk);
CREATE INDEX IF NOT EXISTS idx_dim_customer_bkey ON dim_customer (customer_business_key);
CREATE INDEX IF NOT EXISTS idx_dim_customer_id ON dim_customer (customer_id);

-- Product Dimension Indexes
CREATE INDEX IF NOT EXISTS idx_dim_product_sk ON dim_product (product_sk);
CREATE INDEX IF NOT EXISTS idx_dim_product_bkey ON dim_product (product_business_key);
CREATE INDEX IF NOT EXISTS idx_dim_product_skey ON dim_product (sales_prd_key);

-- Date Dimension Indexes
CREATE INDEX IF NOT EXISTS idx_dim_date_sk ON dim_date (date_sk);

-- Geography Dimension Indexes
CREATE INDEX IF NOT EXISTS idx_dim_geography_sk ON dim_geography (geography_sk);

-- Sales Fact Table Foreign Key Indexes
CREATE INDEX IF NOT EXISTS idx_fact_sales_date ON fact_sales (date_sk);
CREATE INDEX IF NOT EXISTS idx_fact_sales_cust ON fact_sales (customer_sk);
CREATE INDEX IF NOT EXISTS idx_fact_sales_prd ON fact_sales (product_sk);
CREATE INDEX IF NOT EXISTS idx_fact_sales_geo ON fact_sales (geography_sk);
