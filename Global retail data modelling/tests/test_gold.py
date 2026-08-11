import pytest
import duckdb
from src.config.settings import DATABASE_PATH
from src.gold.gold_transformer import GoldTransformer

@pytest.fixture
def gold_setup():
    transformer = GoldTransformer(db_path=DATABASE_PATH)
    counts = transformer.execute_transformations()
    transformer.close()
    return counts

def test_gold_star_schema_relationships(gold_setup):
    """Verifies Star Schema surrogate key relationships between fact_sales and dimension tables."""
    conn = duckdb.connect(str(DATABASE_PATH))
    
    # Check customer surrogate key joins
    unmatched_cust = conn.execute("SELECT COUNT(*) FROM fact_sales WHERE customer_sk = 0").fetchone()[0]
    assert unmatched_cust == 0, f"Found {unmatched_cust} fact_sales rows with unmapped customer_sk = 0"

    # Check product surrogate key joins
    unmatched_prd = conn.execute("SELECT COUNT(*) FROM fact_sales WHERE product_sk = 0").fetchone()[0]
    assert unmatched_prd == 0, f"Found {unmatched_prd} fact_sales rows with unmapped product_sk = 0"

    # Check date surrogate key joins
    unmatched_date = conn.execute("SELECT COUNT(*) FROM fact_sales f LEFT JOIN dim_date d ON f.date_sk = d.date_sk WHERE d.date_sk IS NULL").fetchone()[0]
    assert unmatched_date == 0, f"Found {unmatched_date} fact_sales rows with invalid date_sk"

    conn.close()

def test_gold_surrogate_key_uniqueness(gold_setup):
    """Verifies surrogate primary keys are unique across Gold dimension tables."""
    conn = duckdb.connect(str(DATABASE_PATH))
    dims = [("dim_customer", "customer_sk"), ("dim_product", "product_sk"), ("dim_geography", "geography_sk"), ("dim_date", "date_sk")]
    for tbl, sk in dims:
        dups = conn.execute(f"SELECT COUNT(*) FROM (SELECT {sk} FROM {tbl} GROUP BY {sk} HAVING COUNT(*) > 1)").fetchone()[0]
        assert dups == 0, f"Found {dups} duplicate surrogate keys in {tbl}.{sk}"
    conn.close()
