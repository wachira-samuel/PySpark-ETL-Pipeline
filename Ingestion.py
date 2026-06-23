import logging
from typing import Tuple

from pyspark.sql import DataFrame, SparkSession
import pyspark.sql.functions as F

from config import (
    CUSTOMERS_CSV,
    CUSTOMERS_SCHEMA,
    ORDER_ITEMS_CSV,
    ORDER_ITEMS_SCHEMA,
    ORDERS_CSV,
    ORDERS_SCHEMA,
    REJECTED_PARQUET,
    RETURNS_CSV,
    RETURNS_SCHEMA,
)

logger = logging.getLogger(__name__)

def load_csv(
    spark: SparkSession,
    path: str,
    schema,
    table_name: str,
) -> Tuple[DataFrame, DataFrame]:
  
    raw = (
        spark.read.format("csv")
        .option("header", "true")
        .option("mode", "PERMISSIVE")
        .option("columnNameOfCorruptRecord", "_corrupt_record")
        .schema(schema)
        .load(path)
    )

    rejected = (
        raw.filter(F.col("_corrupt_record").isNotNull())
        .withColumn("source_table", F.lit(table_name))
        .withColumn("rejection_reason", F.lit("corrupt_record / type cast failure"))
    )

    clean = raw.filter(F.col("_corrupt_record").isNull()).drop("_corrupt_record")

    rejected_count = rejected.count()
    clean_count = clean.count()
    logger.info(
        "[%s] loaded %d clean rows, %d rejected rows",
        table_name,
        clean_count,
        rejected_count,
    )

    return clean, rejected


def ingest_all(spark: SparkSession) -> Tuple[DataFrame, DataFrame, DataFrame, DataFrame, DataFrame]:
    
    orders_clean, orders_rejected = _load_csv(spark, ORDERS_CSV, ORDERS_SCHEMA, "orders")
    items_clean, items_rejected = _load_csv(spark, ORDER_ITEMS_CSV, ORDER_ITEMS_SCHEMA, "order_items")
    customers_clean, customers_rejected = _load_csv(spark, CUSTOMERS_CSV, CUSTOMERS_SCHEMA, "customers")
    returns_clean, returns_rejected = _load_csv(spark, RETURNS_CSV, RETURNS_SCHEMA, "returns")

    rejected_dfs = [orders_rejected, items_rejected, customers_rejected, returns_rejected]
    combined_rejected = rejected_dfs[0]
    for rdf in rejected_dfs[1:]:
        combined_rejected = combined_rejected.unionByName(rdf, allowMissingColumns=True)

    total_rejected = combined_rejected.count()
    if total_rejected > 0:
        logger.warning("Total rejected rows across all tables: %d", total_rejected)
        combined_rejected.write.mode("overwrite").parquet(REJECTED_PARQUET)
        logger.info("Rejected rows written to %s", REJECTED_PARQUET)
    else:
        logger.info("No rejected rows found — all records parsed successfully.")

    return orders_clean, items_clean, customers_clean, returns_clean, combined_rejected
