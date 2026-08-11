from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CRM_DATA_DIR = RAW_DATA_DIR / "source_crm"
ERP_DATA_DIR = RAW_DATA_DIR / "source_erp"
DATABASE_DIR = DATA_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "retail_medallion.db"
SQL_DIR = BASE_DIR / "sql"
DOCS_DIR = BASE_DIR / "docs"

# Source File Mappings
SOURCE_FILES = {
    "cust_info": CRM_DATA_DIR / "cust_info.csv",
    "prd_info": CRM_DATA_DIR / "prd_info.csv",
    "sales_details": CRM_DATA_DIR / "sales_details.csv",
    "cust_az12": ERP_DATA_DIR / "CUST_AZ12.csv",
    "loc_a101": ERP_DATA_DIR / "LOC_A101.csv",
    "px_cat_g1v2": ERP_DATA_DIR / "PX_CAT_G1V2.csv",
}

# Ensure directories exist
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
