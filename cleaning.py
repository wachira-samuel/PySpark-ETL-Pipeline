import logging
from pyspark.sql import DataFrame
import pyspark.sql.functions as F

logger = logging.getLogger(__name__)

# Step 1 - Drop duplicates
def remove_duplicates(df: DataFrame, table_name: str = "") -> DataFrame:
    before = df.count()
    deduped = df.dropDuplicates()
    after = deduped.count()
    logger.info("[%s] deduplication: %d → %d rows (%d removed)", table_name, before, after, before - after)
    return deduped

# Step 2 - Date normalisation
def normalise_column_date(df: DataFrame, col_name: str) -> DataFrame:
    return df.withColumn(
        col_name,
        F.coalesce(
            F.to_date(F.col(col_name), "yyyy-MM-dd")           
        ),
    )


def normalise_dates(df: DataFrame, date_columns: list) -> DataFrame:
  
    for col_name in date_columns:
        df = _normalise_column_date(df, col_name)
    return df

# Step 3 - customer casing
def standardise_tier(df: DataFrame) -> DataFrame:
    return df.withColumn(
        "customer_tier",
        F.lower(F.trim(F.col("customer_tier"))),
    )

# Step 4 - Drop NULL key fields
def drop_null_keys(df: DataFrame, key_cols: list, table_name: str = "") -> DataFrame:  
    null_filter = F.lit(False)
    for col_name in key_cols:
        null_filter = null_filter | F.col(col_name).isNull()

    null_count = df.filter(null_filter).count()
    if null_count > 0:
        logger.warning(
            "[%s] dropping %d rows with NULL in key column(s): %s",
            table_name,
            null_count,
            key_cols,
        )
    result = df.filter(null_filter)
    return result

# Step 5 — negative amounts
def flag_negative_amounts(df: DataFrame) -> DataFrame:
    return df.withColumn(
        "is_negative_amount",
        F.when(F.col("total_amount") < 0, True).otherwise(False),
    )

# Orchestrator
def clean_orders(df: DataFrame) -> DataFrame:
    df = remove_duplicates(df, "orders")
    df = normalise_dates(df, ["order_date"])
    df = drop_null_keys(df, ["order_id", "customer_id"], "orders")
    df = flag_negative_amounts(df)
    return df

def clean_customers(df: DataFrame) -> DataFrame:
    df = remove_duplicates(df, "customers")
    df = normalise_dates(df, ["signup_date"])
    df = standardise_tier(df)
    return df

def clean_order_items(df: DataFrame) -> DataFrame:
    df = remove_duplicates(df, "order_items")
    return df

def clean_returns(df: DataFrame) -> DataFrame:
    df = remove_duplicates(df, "returns")
    df = normalise_dates(df, ["return_date"])
    return df
