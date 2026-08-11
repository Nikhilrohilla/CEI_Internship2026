import hashlib
import uuid
from datetime import datetime
import pandas as pd
# pyrefly: ignore [missing-import]
import duckdb
from src.config.settings import DATABASE_PATH, SQL_DIR, SOURCE_FILES
from src.utils.logger import logger

class BronzeLoader:
    """Ingests raw CSV files into DuckDB Bronze tables with audit metadata."""
    
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = str(db_path)
        self.conn = duckdb.connect(self.db_path)

    def initialize_tables(self):
        """Executes 01_create_bronze.sql DDL script."""
        sql_file = SQL_DIR / "bronze" / "01_create_bronze.sql"
        logger.info(f"Initializing Bronze DDL from {sql_file.name}")
        with open(sql_file, "r") as f:
            ddl_sql = f.read()
        self.conn.execute(ddl_sql)

    @staticmethod
    def _compute_hash(row: pd.Series) -> str:
        """Calculates SHA-256 hash across raw row values for data auditability."""
        concat_str = "|".join([str(val) if pd.notnull(val) else "" for val in row])
        return hashlib.sha256(concat_str.encode("utf-8")).hexdigest()

    def load_file(self, table_name: str, file_path: str, batch_id: str) -> dict:
        """Reads a single CSV file, attaches lineage metadata, and loads into Bronze table."""
        logger.info(f"Ingesting {file_path.name} into {table_name}...")
        df = pd.read_csv(file_path, dtype=str)
        rows_read = len(df)
        
        # Calculate record hash
        df["record_hash"] = df.apply(self._compute_hash, axis=1)
        df["source_file"] = file_path.name
        df["ingestion_timestamp"] = datetime.now().isoformat()
        df["batch_id"] = batch_id
        
        # Truncate and Reload 
        self.conn.execute(f"TRUNCATE TABLE {table_name}")
        self.conn.register("df_temp", df)
        
        # Match columns dynamically
        cols = ", ".join(df.columns)
        self.conn.execute(f"INSERT INTO {table_name} ({cols}) SELECT {cols} FROM df_temp")
        self.conn.unregister("df_temp")
        
        count_res = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        logger.info(f"Loaded {count_res} rows into {table_name} (Rows Read: {rows_read})")
        
        return {
            "table_name": table_name,
            "source_file": file_path.name,
            "rows_read": rows_read,
            "rows_written": count_res,
            "batch_id": batch_id
        }

    def run_all(self) -> list:
        """Runs raw ingestion for all CRM and ERP files."""
        self.initialize_tables()
        batch_id = str(uuid.uuid4())[:8]
        results = []
        
        mappings = [
            ("bronze_cust_info", SOURCE_FILES["cust_info"]),
            ("bronze_cust_az12", SOURCE_FILES["cust_az12"]),
            ("bronze_loc_a101", SOURCE_FILES["loc_a101"]),
            ("bronze_prd_info", SOURCE_FILES["prd_info"]),
            ("bronze_px_cat_g1v2", SOURCE_FILES["px_cat_g1v2"]),
            ("bronze_sales_details", SOURCE_FILES["sales_details"]),
        ]
        
        for table_name, file_path in mappings:
            res = self.load_file(table_name, file_path, batch_id)
            results.append(res)
            
        return results

    def close(self):
        self.conn.close()
