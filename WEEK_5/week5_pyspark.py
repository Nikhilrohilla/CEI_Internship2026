#!/usr/bin/env python3
"""
Week 5 - Apache Spark Data Processing using PySpark
Celebal Excellence Internship (CEI) 2026 - Data Engineering Domain
Student: Nikhil

Standalone script version of the accompanying Jupyter/Colab notebook.
Run with: python week5_pyspark.py  (requires pyspark installed locally)
"""

# Apache Spark Data Processing using PySpark
# Data Engineering Practical — Superstore Dataset

# Student Details
# | Field | Value |
# |---|---|
# | **Name** | Nikhil |
# | **Program** | Celebal Excellence Internship (CEI) 2026 |
# | **Domain** | Data Engineering |
# | **Week** | 5 |
# | **Topic** | Apache Spark / PySpark — DataFrame Cleaning, Transformation & Aggregation |

# Assignment Objective
# Solve 15 questions covering Spark fundamentals, DataFrame cleaning, filtering,
# grouping, aggregation, and a final end-to-end revenue processing pipeline —
# using a single realistic Superstore-style dataset and the PySpark DataFrame API.

# Apache Spark Overview
# - In-memory distributed processing engine — avoids repeated disk I/O between stages, unlike classic MapReduce
# - Core abstraction is the **RDD**; DataFrames add a schema + Catalyst optimizer on top
# - **Lazy evaluation** — transformations build a DAG; nothing executes until an action (`show`, `count`, `collect`) is called
# - **Catalyst optimizer** rewrites the logical plan (predicate pushdown, projection pruning) before execution
# - **Tungsten engine** manages off-heap binary memory layout for faster serialization
# - Unified engine — batch, streaming, SQL, ML, and graph processing on one runtime
# - Transformations are either **narrow** (map, filter — no shuffle) or **wide** (groupBy, join — shuffle required)

# Environment Setup
# Install PySpark

# Import Libraries

# Core PySpark imports used throughout this notebook
from pyspark.sql import SparkSession, Row
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType,
    DoubleType, TimestampType
)
import random
from datetime import datetime, timedelta

# Initialize Spark Session

# Single SparkSession reused across the entire notebook
spark = (
    SparkSession.builder
    .appName("Week5_Superstore_PySpark")
    .master("local[*]")
    .config("spark.sql.shuffle.partitions", "8")   # small cluster -> fewer shuffle partitions
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")   # suppress verbose Spark logs in Colab output
spark

# Load Dataset
# Using a Superstore-style retail dataset (region / category / sales pattern).
# Generated in-notebook with a fixed seed so the notebook is fully reproducible in Colab
# without external file downloads.

# Reproducible synthetic Superstore-style base data
random.seed(42)

regions = ["West", "East", "Central", "South"]
categories = ["Furniture", "Office Supplies", "Technology"]
sub_categories = {
    "Furniture": ["Chairs", "Tables", "Bookcases"],
    "Office Supplies": ["Binders", "Paper", "Storage"],
    "Technology": ["Phones", "Accessories", "Machines"],
}
cities = ["New York", "Chicago", "Los Angeles", "Seattle", "Austin", "Boston"]
first_names = ["Aarav", "Priya", "John", "Emma", "Liam", "Sofia", "Noah", "Maya", "Ethan", "Ava"]
last_names = ["Sharma", "Khan", "Smith", "Brown", "Garcia", "Lee", "Patel", "Clark"]

base_rows = []
for i in range(1, 301):
    region = random.choice(regions)
    category = random.choice(categories)
    sub_category = random.choice(sub_categories[category])
    city = random.choice(cities)
    fname = random.choice(first_names)
    lname = random.choice(last_names)
    order_date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 700))
    sale_amount = round(random.uniform(15, 2500), 2)

    base_rows.append(Row(
        order_id=f"ORD-{1000 + i}",
        customer_name=f"{fname} {lname}",
        region=region,
        product_category=category,
        sub_category=sub_category,
        city=city,
        order_date=order_date.strftime("%Y-%m-%d"),
        sale_amount=sale_amount,
        quantity=random.randint(1, 12),
        discount=float(random.choice([0, 0.1, 0.15, 0.2, 0.3])),
    ))

# Deliberately duplicate a handful of rows to make Q3/Q6 realistic
base_rows += random.sample(base_rows, 15)

superstore_schema = StructType([
    StructField("order_id", StringType(), True),
    StructField("customer_name", StringType(), True),
    StructField("region", StringType(), True),
    StructField("product_category", StringType(), True),
    StructField("sub_category", StringType(), True),
    StructField("city", StringType(), True),
    StructField("order_date", StringType(), True),
    StructField("sale_amount", DoubleType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("discount", DoubleType(), True),
])

df_sales = spark.createDataFrame(base_rows, schema=superstore_schema)
print(f"Base rows loaded: {df_sales.count()}")
df_sales.show(5)

# Extend Dataset
# The assignment references columns that don't exist in a plain Superstore export
# (`user_id`, `transaction_date`, `status`, `subscription`, `age`, `username`,
# `email`, `price`, `raw_timestamp`, `store_id`). These are derived once, in a
# single chained transformation, so the **same DataFrame** is used for every
# question below.

# Derive every extra column the assignment needs, in one chained transformation
df_sales = (
    df_sales
    .withColumn("user_id", (F.monotonically_increasing_id() + 1))
    .withColumn("transaction_date", F.to_date("order_date"))
    .withColumn(
        "status",
        F.when(F.rand(seed=1) < 0.08, None)                       # ~8% nulls -> for na.drop/na.fill demo
         .otherwise(F.element_at(F.array(F.lit("Active"), F.lit("Inactive"), F.lit("Pending")),
                                  (F.floor(F.rand(seed=2) * 3) + 1).cast("int")))
    )
    .withColumn(
        "subscription",
        F.when(F.rand(seed=3) < 0.5, F.lit("Premium")).otherwise(F.lit("Basic"))
    )
    .withColumn(
        "age",
        F.when(F.rand(seed=4) < 0.05, None)                        # small % missing ages
         .otherwise((F.rand(seed=5) * 45 + 16).cast("int"))         # ~16-61
    )
    .withColumn(
        "username",
        F.when(F.rand(seed=6) < 0.05, F.lit(""))                   # a few empty usernames -> Q12
         .otherwise(F.lower(F.regexp_replace("customer_name", " ", ".")))
    )
    .withColumn(
        "email",
        F.when(F.rand(seed=7) < 0.07, None)                        # a few missing emails -> Q12
         .otherwise(F.concat(F.lower(F.regexp_replace("customer_name", " ", ".")), F.lit("@example.com")))
    )
    .withColumn(
        "price",
        F.when(F.rand(seed=8) < 0.06, None).otherwise(F.col("sale_amount"))   # nulls for Q5 / Q15
    )
    .withColumn(
        "raw_timestamp",
        F.concat(F.col("order_date"), F.lit(" "),
                  F.lpad((F.rand(seed=9) * 24).cast("int").cast("string"), 2, "0"), F.lit(":00:00"))
    )
    .withColumn("store_id", F.concat(F.lit("STORE_"), (F.abs(F.hash("city")) % 10).cast("string")))
)

df_sales.printSchema()

# Data Inspection

# Basic shape, schema and summary checks before cleaning
print(f"Row count: {df_sales.count()}")
print(f"Column count: {len(df_sales.columns)}")
df_sales.select("sale_amount", "price", "age").describe().show()

# Null audit per column -- guides the cleaning decisions below
null_counts = df_sales.select(
    [F.count(F.when(F.col(c).isNull(), c)).alias(c) for c in df_sales.columns]
)
null_counts.show(truncate=False)

# Data Cleaning
# General-purpose cleaning applied once, upfront:
# - Drop exact full-row duplicates
# - Standardize the `city` / `region` text casing
# Column-specific null handling (status, price, email, username) is deliberately
# left for the relevant question below, since each needs a different strategy.

# Remove exact duplicate rows and normalize text casing
df_sales = (
    df_sales
    .dropDuplicates()
    .withColumn("city", F.initcap("city"))
    .withColumn("region", F.initcap("region"))
)
print(f"Row count after removing exact duplicates: {df_sales.count()}")

# Questions 1–15

# Q1 — Limitations of MapReduce vs. Spark
# **Problem Statement:** Key limitations of traditional MapReduce that make Spark preferable for modern big data processing.
# **Key Observation (theory):**
# - MapReduce writes intermediate results to **HDFS** after every Map/Reduce stage — Spark keeps data **in-memory (RDD/DataFrame)** across stages
# - Iterative workloads (ML, graph algorithms) re-read the full dataset from disk each pass in MapReduce; Spark caches once and reuses it
# - MapReduce only exposes two primitives (`map`, `reduce`); Spark offers a rich set (`filter`, `join`, `groupBy`, windowing) reducing job count
# - Spark's **DAG scheduler** optimizes multi-stage pipelines as one job; MapReduce treats each stage as a separate job with new JVM startup overhead
# - No unified engine in the MapReduce world — separate tools were needed for SQL (Hive), streaming (Storm), ML (Mahout); Spark unifies all of these
# - Fault tolerance in Spark is via **RDD lineage** (recompute lost partitions) rather than replicated intermediate disk writes
# - Latency: MapReduce jobs typically run in minutes even for small data due to disk I/O; Spark local jobs run in seconds

# Q2 — In-Memory Computing for iterative ML
# **Problem Statement:** How Spark's in-memory computing speeds up iterative ML algorithms vs. disk-based systems.
# **Key Observation (theory):**
# - Iterative ML (e.g. gradient descent, k-means) reuses the **same dataset** across many iterations
# - `.cache()` / `.persist()` keep a DataFrame's partitions in executor memory after the first pass, avoiding re-reading from disk on every iteration
# - Disk-based MapReduce re-reads and re-writes the dataset to HDFS every iteration — I/O cost dominates over compute
# - Spark's DAG lets the optimizer skip recomputation of already-cached stages when only downstream logic changes
# - Memory tiers (`MEMORY_ONLY`, `MEMORY_AND_DISK`) let Spark spill gracefully instead of failing when data doesn't fully fit in RAM
# - Broadcast variables let small lookup tables (e.g. model weights) be shared across executors without repeated shuffles
# - Net effect: iterative jobs that take MapReduce many minutes can complete in seconds to low minutes in Spark for the same iteration count

# Q3 — Remove duplicates on (user_id, transaction_date)
# **Problem Statement:** Remove duplicate rows based on `user_id` and `transaction_date`.
# **Solution Approach:** `dropDuplicates()` with a column subset keeps the first occurrence per key combination.

# Deduplicate on the composite business key (user_id, transaction_date)
df_dedup = df_sales.dropDuplicates(subset=["user_id", "transaction_date"])

print(f"Rows before: {df_sales.count()} | Rows after: {df_dedup.count()}")
df_dedup.select("user_id", "transaction_date", "order_id").show(5)

# **Key Observation:** `dropDuplicates(subset=...)` is a wide transformation (it shuffles to compare keys across partitions); since `user_id` is unique per row here, this mainly demonstrates the pattern for datasets where the same user could transact identically twice.

# Q4 — Filter West region, average sale by category
# **Problem Statement:** Filter `df_sales` for `region == 'West'`, group by `product_category`, find average `sale_amount`.
# **Solution Approach:** `.filter()` then `.groupBy().agg()`, chained.

# Filter -> group -> aggregate, chained in one expression
west_avg_by_category = (
    df_sales
    .filter(F.col("region") == "West")
    .groupBy("product_category")
    .agg(F.round(F.avg("sale_amount"), 2).alias("avg_sale_amount"))
    .orderBy(F.desc("avg_sale_amount"))
)

west_avg_by_category.show()

# **Key Observation:** Filtering before grouping (predicate pushdown-friendly) reduces the volume shuffled during the subsequent `groupBy`.

# Q5 — na.drop() vs na.fill()
# **Problem Statement:** Difference between `.na.drop()` and `.na.fill()`; fill nulls in `status` with `'Unknown'`.
# **Key Observation (theory):**
# - `.na.drop()` **removes rows** containing nulls (in any/specified columns) — reduces row count, used when incomplete records are unusable
# - `.na.fill()` **substitutes** a default value for nulls **in place** — preserves row count, used when a sensible default exists
# - `.na.drop(how="any")` drops if *any* column is null; `how="all"` drops only if *every* column is null
# - `.na.fill()` can take a dict to apply different fill values per column in a single call
# - Choosing drop vs. fill depends on whether the missing value is *recoverable* (fill) or the row is unusable without it (drop)
# - Both are lazy transformations — no computation happens until an action is triggered

# Fill null 'status' values with a placeholder instead of dropping the rows
df_status_filled = df_sales.na.fill({"status": "Unknown"})

df_status_filled.groupBy("status").count().orderBy(F.desc("count")).show()

# Q6 — City counts above 100
# **Problem Statement:** Total record count per city, only where count > 100.
# **Solution Approach:** `groupBy().count()` then `filter()` on the aggregated column (HAVING-equivalent).

# Aggregate first, then filter on the aggregated result (HAVING-style)
city_counts = (
    df_sales
    .groupBy("city")
    .count()
    .filter(F.col("count") > 100)
    .orderBy(F.desc("count"))
)

city_counts.show()

# **Key Observation:** With only 300 base rows spread across 6 cities, no city crosses 100 here at full scale — the query pattern is correct and would return matching cities on a larger dataset; the DataFrame API expresses HAVING as a plain post-aggregation `.filter()`, unlike SQL's separate clause.

# Q7 — Immutability and data cleaning
# **Problem Statement:** How DataFrame immutability affects cleaning steps like dropping/renaming columns.
# **Key Observation (theory):**
# - DataFrames are **immutable** — `.drop()`, `.withColumnRenamed()`, `.withColumn()` all return a **new** DataFrame; the original is untouched
# - Cleaning pipelines are therefore written as **chains** (`df.drop(...).withColumnRenamed(...)`) or reassigned to the same variable name
# - Immutability enables safe **lineage-based fault tolerance** — Spark can recompute any DataFrame from its transformation history
# - No accidental in-place mutation across parallel tasks — each executor works on its own partition without shared mutable state
# - Every intermediate cleaning step exists only in the DAG until an action forces evaluation, so "renaming" doesn't cost anything until execution
# - Practical implication: forgetting to reassign (`df.drop("x")` without `df = df.drop("x")`) is a common bug — the drop simply has no effect on `df`

# Q8 — Filter age 18–30 and Premium subscription
# **Problem Statement:** Filter rows where `age` is between 18 and 30 inclusive and `subscription == 'Premium'`.

# Range filter combined with an equality filter
young_premium_users = df_sales.filter(
    (F.col("age").between(18, 30)) & (F.col("subscription") == "Premium")
)

print(f"Matching rows: {young_premium_users.count()}")
young_premium_users.select("user_id", "age", "subscription", "city").show(5)

# Q9 — Handle nulls before aggregation
# **Problem Statement:** Why handle nulls before `sum()` / `avg()`.
# **Key Observation (theory):**
# - Spark's `sum()`/`avg()` **silently skip nulls** rather than erroring — this can quietly bias results if nulls aren't intentional
# - `avg()` divides by the **count of non-null values**, not total row count — a column with many nulls looks artificially "healthy"
# - Unhandled nulls can propagate into downstream joins/calculations as `NULL`, silently dropping rows in later `inner` joins
# - Deciding fill-vs-drop *before* aggregating keeps the denominator (row count) meaningful and the result reproducible
# - Aggregating first and patching nulls after is **too late** — the aggregate value itself may already be wrong or misleading
# - Best practice: run a null audit (as done in Data Inspection above) before writing any aggregation logic

# Q10 — Cast raw_timestamp to TimestampType, rename to event_time
# **Problem Statement:** Cast `raw_timestamp` to `TimestampType` and rename to `event_time`.

# Cast string timestamp to TimestampType and rename in one chained call
df_sales = (
    df_sales
    .withColumn("event_time", F.col("raw_timestamp").cast(TimestampType()))
    .drop("raw_timestamp")
)

df_sales.select("event_time").printSchema()
df_sales.select("event_time").show(5, truncate=False)

# Q11 — The Shuffle process in grouping
# **Problem Statement:** Explain the Shuffle process during grouping; why it's a wide transformation.
# **Key Observation (theory):**
# - `groupBy()` needs all rows sharing a key on the **same partition** to aggregate correctly — this requires redistributing data across the cluster
# - The **shuffle** writes intermediate data to disk on each executor, then transfers it over the network to the executor owning that key's partition
# - It's a **wide transformation** because each output partition can depend on data from *every* input partition — unlike `map`/`filter` (narrow, one-to-one partition dependency)
# - Shuffles are the most expensive operation in Spark: disk I/O + network I/O + serialization overhead
# - `spark.sql.shuffle.partitions` controls the number of post-shuffle partitions — too high causes overhead from tiny tasks, too low causes skew/OOM
# - Techniques like `reduceByKey`-style partial aggregation (map-side combine) reduce shuffle volume by pre-aggregating within a partition before the shuffle
# - Repeated wide transformations in a pipeline compound shuffle cost — minimizing groupBy/join count matters for performance

# Q12 — Remove null emails OR empty usernames
# **Problem Statement:** Remove rows where `email` is null OR `username` is an empty string.

# Combine an isNull check with an empty-string check using OR
df_valid_contacts = df_sales.filter(
    ~(F.col("email").isNull() | (F.col("username") == ""))
)

print(f"Rows before: {df_sales.count()} | Rows after: {df_valid_contacts.count()}")
df_valid_contacts.select("user_id", "username", "email").show(5)

# **Key Observation:** Null-checks need `.isNull()` (not `== None`, which Spark evaluates to `NULL` rather than `True`/`False`); combining with an empty-string check needs an explicit `==` "" since blank strings are not null.

# Q13 — Multiple statistics with .agg()
# **Problem Statement:** Use `.agg()` to calculate min, max, and mean of `price` at once.

# Multiple aggregate functions on the same column in a single .agg() call
price_stats = df_sales.agg(
    F.min("price").alias("min_price"),
    F.max("price").alias("max_price"),
    F.round(F.avg("price"), 2).alias("mean_price"),
)

price_stats.show()

# **Key Observation:** All three aggregate functions scan the DataFrame in a single pass/job — cheaper than three separate `.agg()` calls, since Spark computes them together in one execution plan.

# Q14 — Risk of inferSchema=true with messy dates
# **Problem Statement:** Risk of using `inferSchema=true` when source data has messy/inconsistent date formats.
# **Key Observation (theory):**
# - `inferSchema=true` samples rows and guesses types — inconsistent date formats often cause Spark to fall back to **StringType** for the whole column instead of `DateType`/`TimestampType`
# - Once mis-typed as string, no automatic date arithmetic or comparisons work until an explicit `to_date`/`to_timestamp` cast is applied later
# - Schema inference requires an **extra full (or sampled) pass over the data** before the real job starts — added latency at scale
# - Mixed formats within the same column (e.g. `MM/dd/yyyy` and `yyyy-MM-dd`) mean any single inferred pattern will silently produce `null` for the non-matching rows
# - Silent `null`s from failed parsing are easy to miss — they look identical to legitimate missing data in a schema/count check
# - Best practice: define an **explicit schema** with the date column as `StringType`, then parse deliberately with `to_date(col, "fmt")`, handling multiple formats via `coalesce()` if needed

# Q15 — Final processing pipeline: duplicates → null prices → revenue by store
# **Problem Statement:** Build a complete pipeline that removes duplicates, fills null prices with 0, groups by `store_id`, and calculates total revenue.
# **Solution Approach:** One chained pipeline — `dropDuplicates → na.fill → groupBy → agg` — followed by `.show()` of the final result.

# End-to-end revenue processing pipeline in a single chain
final_revenue_df = (
    df_sales
    .dropDuplicates(subset=["order_id"])          # 1. remove duplicate orders
    .na.fill({"price": 0})                         # 2. null prices -> 0
    .groupBy("store_id")                           # 3. group by store
    .agg(
        F.round(F.sum("price"), 2).alias("total_revenue"),
        F.count("order_id").alias("order_count"),
    )
    .orderBy(F.desc("total_revenue"))              # readability
)

print("Final processed revenue DataFrame:")
final_revenue_df.show(20, truncate=False)

# **Key Observation:** Order matters — filling nulls with 0 *before* summing ensures missing prices contribute 0 revenue rather than being silently excluded from the row count; deduplicating on `order_id` first prevents double-counting revenue from the intentionally duplicated rows introduced earlier.

# Performance Considerations
# - Cache (`.cache()`) any DataFrame reused across multiple questions/actions to avoid recomputing the DAG from scratch each time
# - Filter before grouping/joining wherever possible — reduces the volume moved during a shuffle
# - Tune `spark.sql.shuffle.partitions` to the actual data size — default (200) is oversized for small/local datasets
# - Prefer `.select()` early to project only needed columns before wide transformations
# - Use `explain()` to inspect the physical plan when a job runs slower than expected
# Best Practices Learned
# - Chain transformations instead of reassigning many intermediate DataFrames — improves readability and lets Catalyst optimize the whole chain
# - Audit nulls (`isNull` counts) before deciding between `.na.drop()` and `.na.fill()`
# - Use explicit schemas instead of `inferSchema=true` for anything beyond a quick exploration
# - Deduplicate on a meaningful business key, not just full-row equality, when the use case calls for it
# - Aggregate with `.agg()` using multiple functions in one call rather than one call per statistic
# Common Mistakes to Avoid
# - Comparing to null with `== None` instead of `.isNull()` (always evaluates to null/false, silently skips rows)
# - Forgetting DataFrames are immutable — calling `.drop()`/`.withColumn()` without reassigning the result
# - Aggregating before cleaning nulls, producing misleading averages/sums
# - Leaving `spark.sql.shuffle.partitions` at its default for small local/Colab datasets
# - Relying on `inferSchema=true` on messy real-world date columns
# Key Takeaways
# - Spark's DataFrame API expresses full ETL pipelines (clean → filter → group → aggregate) as one lazy, optimized chain
# - Wide transformations (`groupBy`, `join`) trigger shuffles and are the primary cost center in a Spark job
# - Correct null handling — not just presence of code — determines whether aggregates are trustworthy
# - Immutability + lineage is what gives Spark both safety (no shared mutable state) and fault tolerance (recompute from DAG)
# Conclusion
# This notebook implements a complete Spark DataFrame workflow — from environment setup through cleaning, filtering, grouping, and a final revenue pipeline — on a single reproducible Superstore-style dataset, covering the DataFrame-API patterns most commonly used in production Data Engineering pipelines.
