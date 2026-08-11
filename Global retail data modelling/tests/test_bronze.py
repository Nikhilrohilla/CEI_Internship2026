import pytest
import duckdb
from src.config.settings import DATABASE_PATH
from src.ingestion.bronze_loader import BronzeLoader

@pytest.fixture
def bronze_setup():
    loader = BronzeLoader(db_path=DATABASE_PATH)
    results = loader.run_all()
    loader.close()
    return results

def test_bronze_table_counts(bronze_setup):
    """Verifies all 6 Bronze tables are populated with correct row counts."""
    conn = duckdb.connect(str(DATABASE_PATH))
    expected_counts = {
        "bronze_cust_info": 18494,
        "bronze_cust_az12": 18484,
        "bronze_loc_a101": 18484,
        "bronze_prd_info": 397,
        "bronze_px_cat_g1v2": 37,
        "bronze_sales_details": 60398,
    }
    for tbl, expected in expected_counts.items():
        cnt = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        assert cnt == expected, f"Table {tbl} row count {cnt} does not match expected {expected}"
    conn.close()

def test_bronze_metadata_columns(bronze_setup):
    """Verifies audit lineage metadata columns exist and are non-null in Bronze tables."""
    conn = duckdb.connect(str(DATABASE_PATH))
    meta_cols = ["source_file", "ingestion_timestamp", "batch_id", "record_hash"]
    for col in meta_cols:
        null_cnt = conn.execute(f"SELECT COUNT(*) FROM bronze_cust_info WHERE {col} IS NULL").fetchone()[0]
        assert null_cnt == 0, f"Column {col} has {null_cnt} null values in bronze_cust_info"
    conn.close()
