# Retail Data Platform Architecture

## Executive Overview

This document outlines the architectural blueprint of the **Retail Data Platform**, built on a modern **Medallion Architecture (Bronze → Silver → Gold)**. The system ingests fragmented, inconsistent transactional and demographic records from CRM and ERP legacy systems, cleanses and standardizes them, and builds an OLAP analytics-ready **Star Schema** optimized for business intelligence, data quality auditing, and historical change tracking (SCD Type 2).

---

## 1. High-Level System Architecture Diagram

```mermaid
flowchart TD
    subgraph SOURCES ["Source Systems"]
        CRM["CRM Platform<br>• cust_info.csv<br>• prd_info.csv<br>• sales_details.csv"]
        ERP["ERP System<br>• CUST_AZ12.csv<br>• LOC_A101.csv<br>• PX_CAT_G1V2.csv"]
    end

    subgraph BRONZE ["Bronze Layer (Raw Ingestion & Lineage)"]
        B_CI["bronze_cust_info"]
        B_AZ["bronze_cust_az12"]
        B_LOC["bronze_loc_a101"]
        B_PI["bronze_prd_info"]
        B_PX["bronze_px_cat_g1v2"]
        B_SD["bronze_sales_details"]
    end

    subgraph SILVER ["Silver Layer (Cleansing, Standardization & Validation)"]
        S_CI["silver_cust_info"]
        S_AZ["silver_cust_az12"]
        S_LOC["silver_loc_a101"]
        S_PI["silver_prd_info"]
        S_PX["silver_px_cat_g1v2"]
        S_SD["silver_sales_details"]
        DQ["Data Quality Framework<br>(Completeness, Uniqueness, Validity, Consistency, Referential Integrity)"]
    end

    subgraph GOLD ["Gold Layer (Star Schema OLAP)"]
        D_CUST["dim_customer (SCD Type 2)"]
        D_PRD["dim_product (SCD Type 2)"]
        D_DATE["dim_date"]
        D_GEO["dim_geography"]
        F_SALES["fact_sales"]
    end

    CRM -->|Raw CSV Load| BRONZE
    ERP -->|Raw CSV Load| BRONZE

    B_CI -->|Deduplicate & Parse| S_CI
    B_AZ -->|Strip NAS & Standardize Gender| S_AZ
    B_LOC -->|Strip Hyphens & Standardize Country| S_LOC
    B_PI -->|Fix Date Swaps & Derive Keys| S_PI
    B_PX -->|Clean Lookup Keys| S_PX
    B_SD -->|Validate Math & Fix Dates| S_SD

    SILVER --> DQ

    S_CI & S_AZ & S_LOC -->|Surrogate Keys & Attributes| D_CUST
    S_PI & S_PX -->|Hierarchy & Attributes| D_PRD
    S_LOC -->|Master Countries| D_GEO
    S_SD & D_CUST & D_PRD & D_DATE & D_GEO -->|Dimensional Joins & Measures| F_SALES
```

---

## 2. Medallion Layer Specifications

### Bronze Layer (Raw Storage)
- **Purpose**: Preserves raw source records in their original state for lineage, auditing, and re-processing.
- **Key Characteristics**:
  - No business transformation applied.
  - Columns stored as raw text (`VARCHAR`).
  - Audit columns appended: `source_file`, `ingestion_timestamp`, `batch_id`, `record_hash` (SHA-256).

### Silver Layer (Cleansed & Standardized)
- **Purpose**: Serves as the single source of truth for clean, standardized, and validated business entities.
- **Key Transformations**:
  - **Whitespace Trimming**: Stripped leading and trailing spaces across strings.
  - **Identifier Normalization**:
    - Removed prefix `'NAS'` from ERP Customer IDs (`NASAW00011000` → `AW00011000`).
    - Removed hyphens from ERP Location CIDs (`AW-00011000` → `AW00011000`).
  - **Categorical Standardization**:
    - Gender normalized to `'Male'`, `'Female'`, `'N/A'`.
    - Country names unified (`'US'`, `'USA'`, `'United States'` → `'United States'`; `'DE'`, `'Germany'` → `'Germany'`).
    - Product lines mapped (`'R'` → `'Road'`, `'M'` → `'Mountain'`, `'T'` → `'Touring'`, `'S'` → `'Standard'`).
  - **Date Anomaly Fixing**:
    - Swapped product date records exhibiting `prd_start_dt > prd_end_dt`.
    - Parsed integer YYYYMMDD sales dates into proper ANSI `DATE` objects.
  - **Financial Validation Rules**:
    - Corrected negative prices to positive values (`ABS(unit_price)`).
    - Enforced formula consistency: `sales_amount = quantity * unit_price`.
    - Inferred missing price when sales amount and quantity were present.

### Gold Layer (Dimensional Star Schema)
- **Purpose**: Optimized for high-speed analytical queries, BI tools (Power BI, Tableau), and executive reporting.
- **Key Characteristics**:
  - **Surrogate Keys**: Integer surrogate primary keys (`customer_sk`, `product_sk`, `date_sk`, `geography_sk`, `sales_sk`).
  - **SCD Type 2**: Supports historical change tracking on `dim_customer` and `dim_product` using `effective_start_date`, `effective_end_date`, and `is_current` flags.
  - **Conformed Dimensions**: Shared date and geography dimensions.

---

## 3. Technology Stack & Rationale

| Component | Technology | Rationale |
|---|---|---|
| **Database Engine** | **DuckDB** | In-process columnar OLAP database providing fast vector execution, ANSI SQL compliance, window functions, and zero-server setup overhead. |
| **ETL Orchestration** | **Python 3.9+** | Modular object-oriented architecture (`BronzeLoader`, `SilverTransformer`, `GoldTransformer`, `QualityChecker`, `SCDHandler`). |
| **SQL Dialect** | **ANSI SQL** | Clean, portable DDL/DML scripts organized into modular `.sql` files. |
| **Testing** | **Pytest** | Automated unit and integration testing covering data transformations, quality metrics, and surrogate key integrity. |
| **Formatting & Logging**| **Tabulate & Logging**| Professional CLI tables and structured file logging. |
