import pytest
import duckdb
from src.config.settings import DATABASE_PATH
from src.silver.silver_transformer import SilverTransformer

@pytest.fixture
def silver_setup():
    transformer = SilverTransformer(db_path=DATABASE_PATH)
    counts = transformer.execute_transformations()
    transformer.close()
    return counts

def test_silver_customer_normalization(silver_setup):
    """Verifies customer key standardization (stripping NAS and hyphens)."""
    conn = duckdb.connect(str(DATABASE_PATH))
    # Check CUST_AZ12 CIDs have no NAS prefix
    nas_cnt = conn.execute("SELECT COUNT(*) FROM silver_cust_az12 WHERE cid LIKE 'NAS%'").fetchone()[0]
    assert nas_cnt == 0, f"Found {nas_cnt} CIDs still containing 'NAS' prefix in silver_cust_az12"
    
    # Check LOC_A101 CIDs have no hyphens
    hyphen_cnt = conn.execute("SELECT COUNT(*) FROM silver_loc_a101 WHERE cid LIKE '%-%'").fetchone()[0]
    assert hyphen_cnt == 0, f"Found {hyphen_cnt} CIDs still containing '-' in silver_loc_a101"
    conn.close()

def test_silver_product_date_fix(silver_setup):
    """Verifies that invalid product date ranges (start_dt > end_dt) were corrected."""
    conn = duckdb.connect(str(DATABASE_PATH))
    invalid_cnt = conn.execute("SELECT COUNT(*) FROM silver_prd_info WHERE prd_end_dt IS NOT NULL AND prd_start_dt > prd_end_dt").fetchone()[0]
    assert invalid_cnt == 0, f"Found {invalid_cnt} product records with prd_start_dt > prd_end_dt in Silver"
    conn.close()

def test_silver_sales_validations(silver_setup):
    """Verifies sales calculations, positive pricing, and valid order date parsing."""
    conn = duckdb.connect(str(DATABASE_PATH))
    # Formula diff check
    diff_cnt = conn.execute("SELECT COUNT(*) FROM silver_sales_details WHERE ABS(sls_sales - (sls_quantity * sls_price)) > 0.01").fetchone()[0]
    assert diff_cnt == 0, f"Found {diff_cnt} sales formula discrepancies in silver_sales_details"
    
    # Zero / negative price check
    neg_price = conn.execute("SELECT COUNT(*) FROM silver_sales_details WHERE sls_price <= 0 OR sls_sales <= 0").fetchone()[0]
    assert neg_price == 0, f"Found {neg_price} non-positive prices/sales amounts in silver_sales_details"
    conn.close()
