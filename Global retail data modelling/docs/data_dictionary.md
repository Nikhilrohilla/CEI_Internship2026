# Gold Layer Data Dictionary

## Overview

This document provides a comprehensive data dictionary for all Gold tables in the Star Schema.

---

## 1. Table: `dim_customer`

| Column Name | Data Type | Nullable | Primary Key | Foreign Key | Source Column | Transformation Logic | Description |
|---|---|---|---|---|---|---|---|
| `customer_sk` | INT | No | Yes | No | Internal Sequence | `ROW_NUMBER()` | Integer surrogate primary key |
| `customer_business_key` | VARCHAR | No | No | No | `cust_info.cst_key` | `TRIM(cst_key)` | Standardized customer code (e.g. `AW00011000`) |
| `customer_id` | INT | No | No | No | `cust_info.cst_id` | `CAST(cst_id AS INT)` | CRM numeric customer identifier |
| `first_name` | VARCHAR | Yes | No | No | `cust_info.cst_firstname` | `TRIM()` | Customer first name |
| `last_name` | VARCHAR | Yes | No | No | `cust_info.cst_lastname` | `TRIM()` | Customer last name |
| `gender` | VARCHAR | No | No | No | `cust_info.cst_gndr` & `CUST_AZ12.gen` | Coalesced & mapped to `Male`/`Female`/`N/A` | Standardized gender |
| `marital_status` | VARCHAR | No | No | No | `cust_info.cst_marital_status` | Mapped `M`→`Married`, `S`→`Single` | Standardized marital status |
| `birth_date` | DATE | Yes | No | No | `CUST_AZ12.bdate` | Parsed to ANSI `DATE` | Birth date from ERP |
| `country` | VARCHAR | No | No | No | `LOC_A101.cntry` | Mapped country names | Primary residence country |
| `customer_create_date` | DATE | No | No | No | `cust_info.cst_create_date` | Parsed to ANSI `DATE` | Account creation date |
| `effective_start_date` | DATE | No | No | No | System / Create Date | SCD Type 2 start date | Version start date |
| `effective_end_date` | DATE | No | No | No | System | Default `9999-12-31` | Version expiration date |
| `is_current` | INT | No | No | No | System | `1` = Active, `0` = Historical | Current record flag |

---

## 2. Table: `dim_product`

| Column Name | Data Type | Nullable | Primary Key | Foreign Key | Source Column | Transformation Logic | Description |
|---|---|---|---|---|---|---|---|
| `product_sk` | INT | No | Yes | No | Internal Sequence | `ROW_NUMBER()` | Integer surrogate primary key |
| `product_business_key` | VARCHAR | No | No | No | `prd_info.prd_key` | `TRIM(prd_key)` | Full business key (`CO-RF-FR-R92B-58`) |
| `sales_prd_key` | VARCHAR | No | No | No | `prd_info.prd_key` | Suffix extraction | Sales lookup key (`FR-R92B-58`) |
| `product_name` | VARCHAR | No | No | No | `prd_info.prd_nm` | `TRIM()` | Product name |
| `product_cost` | NUMERIC(10,2) | No | No | No | `prd_info.prd_cost` | `COALESCE(cost, 0.00)` | Manufacturing cost ($) |
| `product_line` | VARCHAR | No | No | No | `prd_info.prd_line` | Mapped `R`→`Road`, `M`→`Mountain` | Product line category |
| `category` | VARCHAR | No | No | No | `PX_CAT_G1V2.cat` | Joined via `cat_id` | Master product category |
| `subcategory` | VARCHAR | No | No | No | `PX_CAT_G1V2.subcat` | Joined via `cat_id` | Master subcategory |
| `maintenance` | VARCHAR | No | No | No | `PX_CAT_G1V2.maintenance` | `Yes`/`No` | Maintenance requirement |
| `effective_start_date` | DATE | No | No | No | `prd_info.prd_start_dt` | Fixed swapped dates | Effective start date |
| `effective_end_date` | DATE | No | No | No | `prd_info.prd_end_dt` | Fixed swapped dates | Effective end date |
| `is_current` | INT | No | No | No | Calculated | `1` if end date is null/9999 | Current record flag |

---

## 3. Table: `fact_sales`

| Column Name | Data Type | Nullable | Primary Key | Foreign Key | Source Column | Transformation Logic | Description |
|---|---|---|---|---|---|---|---|
| `sales_sk` | BIGINT | No | Yes | No | Internal Sequence | `ROW_NUMBER()` | Surrogate primary key |
| `order_number` | VARCHAR | No | No | No | `sales_details.sls_ord_num` | `TRIM()` | Sales order number |
| `date_sk` | INT | No | No | Yes (`dim_date`) | `sales_details.sls_order_dt` | Format `YYYYMMDD` | Foreign key to date dimension |
| `customer_sk` | INT | No | No | Yes (`dim_customer`) | `sales_details.sls_cust_id` | Join `sls_cust_id = cst_id` | Foreign key to customer dimension |
| `product_sk` | INT | No | No | Yes (`dim_product`) | `sales_details.sls_prd_key` | Join `sls_prd_key = sales_prd_key` | Foreign key to product dimension |
| `geography_sk` | INT | No | No | Yes (`dim_geography`) | `LOC_A101.cntry` | Join via customer location | Foreign key to geography dimension |
| `order_date` | DATE | No | No | No | `sales_details.sls_order_dt` | Parsed to ANSI `DATE` | Order transaction date |
| `ship_date` | DATE | Yes | No | No | `sales_details.sls_ship_dt` | Parsed to ANSI `DATE` | Order shipment date |
| `due_date` | DATE | Yes | No | No | `sales_details.sls_due_dt` | Parsed to ANSI `DATE` | Payment due date |
| `sales_amount` | NUMERIC(12,2) | No | No | No | `sales_details.sls_sales` | Formula `quantity * price` | Net sales revenue ($) |
| `quantity` | INT | No | No | No | `sales_details.sls_quantity` | `ABS(quantity)` | Quantity ordered |
| `unit_price` | NUMERIC(10,2) | No | No | No | `sales_details.sls_price` | `ABS(price)` | Price per unit ($) |
