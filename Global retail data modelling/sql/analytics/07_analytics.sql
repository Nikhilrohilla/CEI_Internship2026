
-- BUSINESS ANALYTICAL SQL QUERIES & WINDOW FUNCTIONS

-- Query 1: Executive Sales KPI Summary
SELECT 
    COUNT(DISTINCT order_number) AS total_orders,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(sales_amount), 2) AS total_revenue,
    ROUND(AVG(sales_amount), 2) AS avg_line_item_value,
    ROUND(SUM(sales_amount) / COUNT(DISTINCT order_number), 2) AS average_order_value
FROM fact_sales;

-- Query 2: Monthly Sales Performance & Month-over-Month (MoM) Growth Rate
WITH monthly_sales AS (
    SELECT 
        d.year,
        d.month,
        d.month_name,
        SUM(f.sales_amount) AS total_sales,
        SUM(f.quantity) AS total_quantity
    FROM fact_sales f
    JOIN dim_date d ON f.date_sk = d.date_sk
    GROUP BY d.year, d.month, d.month_name
)
SELECT 
    year,
    month,
    month_name,
    ROUND(total_sales, 2) AS monthly_revenue,
    ROUND(LAG(total_sales) OVER (ORDER BY year, month), 2) AS prev_month_revenue,
    ROUND(
        (total_sales - LAG(total_sales) OVER (ORDER BY year, month)) 
        / NULLIF(LAG(total_sales) OVER (ORDER BY year, month), 0) * 100, 2
    ) AS mom_growth_pct,
    ROUND(SUM(total_sales) OVER (ORDER BY year, month), 2) AS cumulative_revenue
FROM monthly_sales
ORDER BY year, month;

-- Query 3: Top 10 Customers by Total Spend & Revenue Contribution
SELECT 
    c.customer_business_key,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.country,
    COUNT(DISTINCT f.order_number) AS total_orders,
    ROUND(SUM(f.sales_amount), 2) AS total_spend,
    DENSE_RANK() OVER (ORDER BY SUM(f.sales_amount) DESC) AS customer_rank
FROM fact_sales f
JOIN dim_customer c ON f.customer_sk = c.customer_sk
GROUP BY c.customer_business_key, c.first_name, c.last_name, c.country
ORDER BY total_spend DESC
LIMIT 10;

-- Query 4: Category & Subcategory Revenue Ranking
SELECT 
    p.category,
    p.subcategory,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.sales_amount), 2) AS category_revenue,
    DENSE_RANK() OVER (PARTITION BY p.category ORDER BY SUM(f.sales_amount) DESC) AS subcat_rank_in_cat
FROM fact_sales f
JOIN dim_product p ON f.product_sk = p.product_sk
GROUP BY p.category, p.subcategory
ORDER BY p.category, category_revenue DESC;

-- Query 5: Country Sales & Regional Performance
SELECT 
    g.region,
    g.country_name,
    COUNT(DISTINCT f.order_number) AS total_orders,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.sales_amount), 2) AS country_revenue,
    ROUND(SUM(f.sales_amount) / SUM(SUM(f.sales_amount)) OVER () * 100, 2) AS global_revenue_share_pct
FROM fact_sales f
JOIN dim_geography g ON f.geography_sk = g.geography_sk
GROUP BY g.region, g.country_name
ORDER BY country_revenue DESC;
