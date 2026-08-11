import duckdb
from src.config.settings import DATABASE_PATH, SQL_DIR
from src.utils.logger import logger

class GoldTransformer:
    """Transforms Silver tables into Gold Star Schema (dim_customer, dim_product, dim_date, dim_geography, fact_sales)."""

    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = str(db_path)
        self.conn = duckdb.connect(self.db_path)

    def execute_transformations(self) -> dict:
        """Executes 03_create_gold.sql Star Schema transformation scripts."""
        sql_file = SQL_DIR / "gold" / "03_create_gold.sql"
        logger.info(f"Executing Gold Star Schema Transformations from {sql_file.name}")
        
        gold_tables = ["dim_geography", "dim_date", "dim_product", "dim_customer", "fact_sales"]
        for tbl in gold_tables:
            self.conn.execute(f"DROP TABLE IF EXISTS {tbl}")

        with open(sql_file, "r") as f:
            self.conn.execute(f.read())

        counts = {}
        for tbl in gold_tables:
            cnt = self.conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
            counts[tbl] = cnt
            logger.info(f"Created Gold Table '{tbl}': {cnt} rows")

        return counts

    def close(self):
        self.conn.close()
