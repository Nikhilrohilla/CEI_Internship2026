import pytest
import duckdb
from src.config.settings import DATABASE_PATH
from src.quality.quality_checker import QualityChecker

@pytest.fixture
def quality_setup():
    checker = QualityChecker(db_path=DATABASE_PATH)
    results = checker.run_all_checks()
    checker.close()
    return results

def test_data_quality_framework_results(quality_setup):
    """Verifies that all automated data quality checks pass successfully."""
    conn = duckdb.connect(str(DATABASE_PATH))
    failed_checks = conn.execute("SELECT check_name, table_name, column_name, failed_records FROM data_quality_results WHERE status = 'FAILED'").fetchall()
    assert len(failed_checks) == 0, f"Data Quality Framework failed on checks: {failed_checks}"
    conn.close()
