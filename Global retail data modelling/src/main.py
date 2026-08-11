import sys
from pathlib import Path

# Add project root to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
from datetime import datetime
import duckdb
from tabulate import tabulate

from src.config.settings import DATABASE_PATH, SQL_DIR
from src.utils.logger import logger
from src.ingestion.bronze_loader import BronzeLoader
from src.silver.silver_transformer import SilverTransformer
from src.quality.quality_checker import QualityChecker
from src.gold.gold_transformer import GoldTransformer
from src.gold.scd_handler import SCDHandler

def run_pipeline():
    """Master orchestrator for the Retail Medallion Data Pipeline."""
    start_time = time.time()
    logger.info("================================================================================")
    logger.info("STARTING RETAIL MEDALLION DATA PIPELINE EXECUTION")
    logger.info("================================================================================")

    try:
        # Phase 1: Bronze Ingestion
        logger.info("\n--- PHASE 1: BRONZE LAYER INGESTION ---")
        bronze_loader = BronzeLoader()
        bronze_results = bronze_loader.run_all()
        bronze_loader.close()

        # Phase 2: Silver Transformations
        logger.info("\n--- PHASE 2: SILVER LAYER CLEANING & STANDARDIZATION ---")
        silver_transformer = SilverTransformer()
        silver_counts = silver_transformer.execute_transformations()
        silver_transformer.close()

        # Phase 3: Data Quality Framework Checks
        logger.info("\n--- PHASE 3: DATA QUALITY FRAMEWORK VALIDATION ---")
        quality_checker = QualityChecker()
        quality_results = quality_checker.run_all_checks()
        quality_checker.close()

        # Phase 4: Gold Star Schema Transformations
        logger.info("\n--- PHASE 4: GOLD LAYER STAR SCHEMA CREATION ---")
        gold_transformer = GoldTransformer()
        gold_counts = gold_transformer.execute_transformations()
        gold_transformer.close()

        # Phase 5: SCD Type 2 Demonstration
        logger.info("\n--- PHASE 5: SLOWLY CHANGING DIMENSIONS (SCD TYPE 2) ---")
        scd_handler = SCDHandler()
        scd_history = scd_handler.run_scd_demonstration()
        scd_handler.close()

        # Phase 6: Index Optimization
        logger.info("\n--- PHASE 6: PERFORMANCE INDEX CREATION ---")
        conn = duckdb.connect(str(DATABASE_PATH))
        index_sql_file = SQL_DIR / "indexes" / "05_indexes.sql"
        with open(index_sql_file, "r") as f:
            conn.execute(f.read())
        logger.info("Indexes successfully created on Gold dimensions and fact tables.")

        # Phase 7: Executive Analytics Execution
        logger.info("\n--- PHASE 7: EXECUTIVE ANALYTICAL REPORTING ---")
        analytics_file = SQL_DIR / "analytics" / "07_analytics.sql"
        with open(analytics_file, "r") as f:
            sql_statements = f.read().split(";")
            
        kpi_res = conn.execute(sql_statements[0]).fetchall()
        headers = ["Total Orders", "Units Sold", "Total Revenue ($)", "Avg Line Price ($)", "Avg Order Value ($)"]
        logger.info("\nExecutive Sales KPIs:\n" + tabulate(kpi_res, headers=headers, tablefmt="grid"))

        cat_res = conn.execute(sql_statements[3]).fetchall()
        cat_headers = ["Category", "Subcategory", "Units Sold", "Revenue ($)", "Subcat Rank"]
        logger.info("\nTop Categories & Subcategories:\n" + tabulate(cat_res[:10], headers=cat_headers, tablefmt="grid"))
        
        conn.close()

        elapsed = round(time.time() - start_time, 2)
        logger.info("\n================================================================================")
        logger.info(f"PIPELINE COMPLETED SUCCESSFULLY IN {elapsed} SECONDS")
        logger.info("================================================================================")

    except Exception as e:
        logger.error(f"PIPELINE EXECUTION FAILED: {str(e)}", exc_info=True)
        raise e

if __name__ == "__main__":
    run_pipeline()
