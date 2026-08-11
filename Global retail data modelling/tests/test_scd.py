import pytest
import duckdb
from src.config.settings import DATABASE_PATH
from src.gold.scd_handler import SCDHandler

def test_scd_type_2_demonstration():
    """Verifies that SCD Type 2 correctly expires previous records and inserts new versions."""
    handler = SCDHandler(db_path=DATABASE_PATH)
    records = handler.run_scd_demonstration()
    handler.close()
    
    # Must have 2 records for AW00011000 after update
    assert len(records) >= 2, f"Expected at least 2 SCD versions for AW00011000, got {len(records)}"
    
    # Old version must be expired (is_current = 0)
    old_version = records[0]
    assert old_version[6] == 0, f"Old SCD record is_current expected 0, got {old_version[6]}"
    
    # New version must be current (is_current = 1, country = Canada)
    new_version = records[-1]
    assert new_version[6] == 1, f"New SCD record is_current expected 1, got {new_version[6]}"
    assert new_version[2] == "Canada", f"New SCD record country expected 'Canada', got {new_version[2]}"
