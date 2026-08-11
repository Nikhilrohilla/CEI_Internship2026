import duckdb
from src.config.settings import DATABASE_PATH, SQL_DIR
from src.utils.logger import logger

class SCDHandler:
    """Manages SCD Type 2 tracking and controlled update demonstrations."""

    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = str(db_path)
        self.conn = duckdb.connect(self.db_path)

    def run_scd_demonstration(self) -> list:
        """Executes 04_scd.sql and returns historical version records for target customer."""
        sql_file = SQL_DIR / "scd" / "04_scd.sql"
        logger.info(f"Running SCD Type 2 demonstration from {sql_file.name}")
        
        with open(sql_file, "r") as f:
            self.conn.execute(f.read())

        # Retrieve history for AW00011000
        records = self.conn.execute("""
            SELECT customer_sk, customer_business_key, country, marital_status,
                   effective_start_date, effective_end_date, is_current
            FROM dim_customer
            WHERE customer_business_key = 'AW00011000'
            ORDER BY customer_sk ASC
        """).fetchall()

        logger.info(f"SCD Type 2 History for AW00011000: {len(records)} version(s)")
        for rec in records:
            logger.info(f"  SK: {rec[0]} | Key: {rec[1]} | Country: {rec[2]} | Start: {rec[4]} | End: {rec[5]} | Current: {rec[6]}")

        return records

    def close(self):
        self.conn.close()
