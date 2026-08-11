import uuid
from datetime import datetime
import duckdb
from tabulate import tabulate
from src.config.settings import DATABASE_PATH, SQL_DIR
from src.utils.logger import logger

class QualityChecker:
    """Executes automated Data Quality checks across completeness, uniqueness, validity, consistency, and referential integrity."""

    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = str(db_path)
        self.conn = duckdb.connect(self.db_path)

    def initialize_table(self):
        """Initializes the data_quality_results table."""
        sql_file = SQL_DIR / "quality" / "06_quality_checks.sql"
        with open(sql_file, "r") as f:
            self.conn.execute(f.read())

    def record_check(self, check_name: str, table_name: str, column_name: str,
                     total_records: int, failed_records: int) -> dict:
        """Calculates failure percentage, logs result, and stores in database."""
        failure_pct = round((failed_records / total_records * 100), 2) if total_records > 0 else 0.0
        status = "PASSED" if failed_records == 0 else ("WARNING" if failure_pct < 5.0 else "FAILED")
        
        check_id = str(uuid.uuid4())[:8]
        ts = datetime.now().isoformat()
        
        self.conn.execute("""
            INSERT INTO data_quality_results (
                check_id, check_name, table_name, column_name,
                total_records, failed_records, failure_percentage, status, execution_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (check_id, check_name, table_name, column_name, total_records, failed_records, failure_pct, status, ts))
        
        return {
            "check_id": check_id,
            "check_name": check_name,
            "table_name": table_name,
            "column_name": column_name,
            "total_records": total_records,
            "failed_records": failed_records,
            "failure_percentage": failure_pct,
            "status": status
        }

    def run_all_checks(self) -> list:
        """Runs complete suite of data quality checks across Silver and Gold layers."""
        self.initialize_table()
        logger.info("Executing Data Quality Framework checks...")
        results = []

        # 1. COMPLETENESS: Null checks on critical business keys
        null_checks = [
            ("silver_cust_info", "cst_key"),
            ("silver_prd_info", "prd_key"),
            ("silver_sales_details", "sls_ord_num"),
            ("silver_sales_details", "sls_cust_id"),
        ]
        for tbl, col in null_checks:
            tot = self.conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
            fail = self.conn.execute(f"SELECT COUNT(*) FROM {tbl} WHERE {col} IS NULL OR TRIM(CAST({col} AS VARCHAR)) = ''").fetchone()[0]
            results.append(self.record_check("Completeness Check (Null Keys)", tbl, col, tot, fail))

        # 2. UNIQUENESS: Duplicate check on primary business keys
        dup_checks = [
            ("silver_cust_info", "cst_key"),
            ("silver_px_cat_g1v2", "id"),
        ]
        for tbl, col in dup_checks:
            tot = self.conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
            fail = self.conn.execute(f"SELECT COUNT(*) FROM (SELECT {col} FROM {tbl} GROUP BY {col} HAVING COUNT(*) > 1)").fetchone()[0]
            results.append(self.record_check("Uniqueness Check (Duplicate Keys)", tbl, col, tot, fail))

        # 3. VALIDITY: Price and quantity non-negative checks
        tot_sales = self.conn.execute("SELECT COUNT(*) FROM silver_sales_details").fetchone()[0]
        invalid_price = self.conn.execute("SELECT COUNT(*) FROM silver_sales_details WHERE sls_price <= 0 OR sls_sales <= 0").fetchone()[0]
        results.append(self.record_check("Validity Check (Positive Financials)", "silver_sales_details", "sls_price/sls_sales", tot_sales, invalid_price))

        # 4. CONSISTENCY: Financial formula check (sales_amount ≈ quantity * unit_price)
        calc_diff = self.conn.execute("SELECT COUNT(*) FROM silver_sales_details WHERE ABS(sls_sales - (sls_quantity * sls_price)) > 0.01").fetchone()[0]
        results.append(self.record_check("Consistency Check (Sales Formula)", "silver_sales_details", "sls_sales", tot_sales, calc_diff))

        # 5. REFERENTIAL INTEGRITY: Sales Customer ID vs Silver Customer ID
        unmatched_cust = self.conn.execute("""
            SELECT COUNT(*) FROM silver_sales_details s
            LEFT JOIN silver_cust_info c ON s.sls_cust_id = c.cst_id
            WHERE c.cst_id IS NULL
        """).fetchone()[0]
        results.append(self.record_check("Referential Integrity (Sales -> Customer)", "silver_sales_details", "sls_cust_id", tot_sales, unmatched_cust))

        # 6. REFERENTIAL INTEGRITY: Sales Product Key vs Silver Product Key
        unmatched_prd = self.conn.execute("""
            SELECT COUNT(*) FROM silver_sales_details s
            LEFT JOIN silver_prd_info p ON s.sls_prd_key = p.sales_prd_key
            WHERE p.sales_prd_key IS NULL
        """).fetchone()[0]
        results.append(self.record_check("Referential Integrity (Sales -> Product)", "silver_sales_details", "sls_prd_key", tot_sales, unmatched_prd))

        # Output Summary Table to Logs
        summary_data = [[r["check_name"], r["table_name"], r["column_name"], r["total_records"], r["failed_records"], f"{r['failure_percentage']}%", r["status"]] for r in results]
        headers = ["Check Name", "Table", "Column", "Total", "Failed", "Fail %", "Status"]
        logger.info("\n" + tabulate(summary_data, headers=headers, tablefmt="grid"))

        return results

    def close(self):
        self.conn.close()
