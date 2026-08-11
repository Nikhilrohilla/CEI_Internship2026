# End-to-End Data Lineage

## Overview

This document maps data lineage across all three Medallion layers: **Raw Source File → Bronze Table → Silver Transformation → Gold Star Schema Field**.

---

## Lineage Matrix Table

| Source System | Raw Source Column | Bronze Table & Field | Silver Transformation Rules | Gold Table & Target Field |
|---|---|---|---|---|
| **CRM** | `cust_info.cst_id` | `bronze_cust_info.cst_id` | Cast to INTEGER, filter out nulls/garbage (`SF566`) | `dim_customer.customer_id` |
| **CRM** | `cust_info.cst_key` | `bronze_cust_info.cst_key` | `TRIM()`, deduplicate taking latest create date | `dim_customer.customer_business_key` |
| **CRM** | `cust_info.cst_firstname` | `bronze_cust_info.cst_firstname` | `TRIM()` whitespace | `dim_customer.first_name` |
| **CRM** | `cust_info.cst_lastname` | `bronze_cust_info.cst_lastname` | `TRIM()` whitespace | `dim_customer.last_name` |
| **CRM** | `cust_info.cst_marital_status` | `bronze_cust_info.cst_marital_status` | Map `'M'`→`'Married'`, `'S'`→`'Single'`, else `'N/A'` | `dim_customer.marital_status` |
| **CRM/ERP** | `cust_info.cst_gndr` & `CUST_AZ12.gen` | `bronze_cust_info.cst_gndr` / `bronze_cust_az12.gen` | Strip `'NAS'`, coalesce missing CRM gender with ERP gender, map to `'Male'`/`'Female'` | `dim_customer.gender` |
| **ERP** | `CUST_AZ12.bdate` | `bronze_cust_az12.bdate` | Parse string date to ANSI `DATE` | `dim_customer.birth_date` |
| **ERP** | `LOC_A101.cntry` | `bronze_loc_a101.cntry` | Standardize variants (`US`/`USA`/`United States`→`United States`; `DE`/`Germany`→`Germany`) | `dim_customer.country` / `dim_geography.country_name` |
| **CRM** | `prd_info.prd_key` | `bronze_prd_info.prd_key` | `TRIM()`, derive `cat_id` prefix (`CO_RF`) and `sales_prd_key` suffix (`FR-R92B-58`) | `dim_product.product_business_key` / `sales_prd_key` |
| **CRM** | `prd_info.prd_nm` | `bronze_prd_info.prd_nm` | `TRIM()` whitespace | `dim_product.product_name` |
| **CRM** | `prd_info.prd_cost` | `bronze_prd_info.prd_cost` | Cast to NUMERIC(10,2), default `0.00` | `dim_product.product_cost` |
| **CRM** | `prd_info.prd_line` | `bronze_prd_info.prd_line` | Map `'R'`→`'Road'`, `'M'`→`'Mountain'`, `'T'`→`'Touring'`, `'S'`→`'Standard'` | `dim_product.product_line` |
| **CRM** | `prd_info.prd_start_dt` / `prd_end_dt` | `bronze_prd_info.prd_start_dt` / `prd_end_dt` | Swap start and end date if `start > end` | `dim_product.effective_start_date` / `effective_end_date` |
| **ERP** | `PX_CAT_G1V2.cat` / `subcat` | `bronze_px_cat_g1v2.cat` / `subcat` | `TRIM()`, join to product via `cat_id` | `dim_product.category` / `subcategory` |
| **CRM** | `sales_details.sls_ord_num` | `bronze_sales_details.sls_ord_num` | `TRIM()` order number | `fact_sales.order_number` |
| **CRM** | `sales_details.sls_order_dt` | `bronze_sales_details.sls_order_dt` | Parse integer YYYYMMDD string to ANSI `DATE` and `YYYYMMDD` integer `date_sk` | `fact_sales.order_date` / `date_sk` |
| **CRM** | `sales_details.sls_cust_id` | `bronze_sales_details.sls_cust_id` | Cast to INT, join to `dim_customer.customer_id` | `fact_sales.customer_sk` |
| **CRM** | `sales_details.sls_prd_key` | `bronze_sales_details.sls_prd_key` | `TRIM()`, join to `dim_product.sales_prd_key` | `fact_sales.product_sk` |
| **CRM** | `sales_details.sls_sales` | `bronze_sales_details.sls_sales` | Enforce formula `quantity * unit_price` | `fact_sales.sales_amount` |
| **CRM** | `sales_details.sls_quantity` | `bronze_sales_details.sls_quantity` | Cast to INT, take `ABS()` | `fact_sales.quantity` |
| **CRM** | `sales_details.sls_price` | `bronze_sales_details.sls_price` | Take `ABS()`, infer from `sales / quantity` if missing | `fact_sales.unit_price` |
