import os
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

# Paths
DATA_DIR = os.environ.get("DATA_DIR", "./data")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "./output")

# Input CSV paths
ORDERS_CSV = os.path.join(DATA_DIR, "orders.csv")
ORDER_ITEMS_CSV = os.path.join(DATA_DIR, "order_items.csv")
CUSTOMERS_CSV = os.path.join(DATA_DIR, "customers.csv")
RETURNS_CSV = os.path.join(DATA_DIR, "returns.csv")

# Output paths
ENRICHED_PARQUET = os.path.join(OUTPUT_DIR, "enriched")
ORPHANED_ITEMS_PARQUET = os.path.join(OUTPUT_DIR, "orphaned_items")
REJECTED_PARQUET = os.path.join(OUTPUT_DIR, "rejected")
SUMMARY_DIR = os.path.join(OUTPUT_DIR, "summary")

# Schemas
ORDERS_SCHEMA = StructType(
    [
        StructField("order_id", StringType(), nullable=True),
        StructField("customer_id", StringType(), nullable=True),
        StructField("order_date", StringType(), nullable=True),   
        StructField("status", StringType(), nullable=True),
        StructField("total_amount", DoubleType(), nullable=True),
        StructField("discount_pct", DoubleType(), nullable=True),
        StructField("_corrupt_record", StringType(), nullable=True),
    ]
)

ORDER_ITEMS_SCHEMA = StructType(
    [
        StructField("item_id", StringType(), nullable=True),
        StructField("order_id", StringType(), nullable=True),
        StructField("product_id", StringType(), nullable=True),
        StructField("category", StringType(), nullable=True),
        StructField("quantity", IntegerType(), nullable=True),
        StructField("unit_price", DoubleType(), nullable=True),
        StructField("_corrupt_record", StringType(), nullable=True),
    ]
)

CUSTOMERS_SCHEMA = StructType(
    [
        StructField("customer_id", StringType(), nullable=True),
        StructField("name", StringType(), nullable=True),
        StructField("email", StringType(), nullable=True),
        StructField("country", StringType(), nullable=True),
        StructField("customer_tier", StringType(), nullable=True),
        StructField("signup_date", StringType(), nullable=True), 
        StructField("_corrupt_record", StringType(), nullable=True),
    ]
)

RETURNS_SCHEMA = StructType(
    [
        StructField("return_id", StringType(), nullable=True),
        StructField("order_id", StringType(), nullable=True),
        StructField("return_date", StringType(), nullable=True), 
        StructField("reason", StringType(), nullable=True),
        StructField("refund_amount", DoubleType(), nullable=True),
        StructField("_corrupt_record", StringType(), nullable=True),
    ]
)
