
-- DATA QUALITY FRAMEWORK DDL & CHECK SUITE
-- Monitors Completeness, Uniqueness, Validity, Consistency, Referential Integrity
CREATE TABLE IF NOT EXISTS data_quality_results (
    check_id VARCHAR,
    check_name VARCHAR,
    table_name VARCHAR,
    column_name VARCHAR,
    total_records BIGINT,
    failed_records BIGINT,
    failure_percentage NUMERIC(5,2),
    status VARCHAR,
    execution_timestamp TIMESTAMP
);

-- Procedure queries are executed via Python QualityChecker module
