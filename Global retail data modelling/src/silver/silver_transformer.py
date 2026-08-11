# pyrefly: ignore [missing-import]
import duckdb
from src.config.settings import DATABASE_PATH, SQL_DIR
from src.utils.logger import logger

class SilverTransformer:
    """Transforms raw Bronze tables into clean, standardized Silver tables."""

    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = str(db_path)
        self.conn = duckdb.connect(self.db_path)

    def execute_transformations(self) -> dict:
        """Executes 02_create_silver.sql transformation queries."""
        sql_file = SQL_DIR / "silver" / "02_create_silver.sql"
        logger.info(f"Executing Silver Transformations from {sql_file.name}")
        

        silver_tables = [
            "silver_cust_info", "silver_cust_az12", "silver_loc_a101",
            "silver_prd_info", "silver_px_cat_g1v2", "silver_sales_details"
        ]
        for tbl in silver_tables:
            self.conn.execute(f"DROP TABLE IF EXISTS {tbl}")

        with open(sql_file, "r") as f:
            transformation_sql = f.read()

    
        self.conn.execute(transformation_sql)

        
        counts = {}
        for tbl in silver_tables:
            cnt = self.conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
            counts[tbl] = cnt
            logger.info(f"Created Silver Table '{tbl}': {cnt} rows")

        return counts

    def close(self):
        self.conn.close()
