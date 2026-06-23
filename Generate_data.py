import argparse
import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker

fake = Faker()


def random_date(start: datetime, end: datetime, fmt: str) -> str:
    delta = end - start
    random_days = random.randint(0, delta.days)
    dt = start + timedelta(days=random_days)
    return dt.strftime(fmt)


def mixed_date(start: datetime, end: datetime) -> str:
    """Return a date string in either ISO or DD/MM/YYYY format at random."""
    fmt = "%Y-%m-%d" if random.random() > 0.4 else "%d/%m/%Y"
    return random_date(start, end, fmt)


def generate_customers(n: int) -> pd.DataFrame:
    tiers_raw = ["bronze", "Bronze", "BRONZE", "silver", "Silver", "SILVER", "gold", "Gold", "GOLD"]
    countries = ["Kenya", "Nigeria", "Ghana", "South Africa", "Egypt", "Ethiopia"]
    start = datetime(2018, 1, 1)
    end = datetime(2023, 12, 31)

    records = []
    for i in range(n):
        records.append({
            "customer_id": f"C{i+1:05d}",
            "name": fake.name(),
            "email": fake.email(),
            "country": random.choice(countries),
            "customer_tier": random.choice(tiers_raw),
            "signup_date": mixed_date(start, end),
        })
    df = pd.DataFrame(records)
    # Introduce ~8% duplicates
    dupes = df.sample(frac=0.08, random_state=42)
    return pd.concat([df, dupes], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)


def generate_orders(n: int, customer_ids: list) -> pd.DataFrame:
    statuses = ["completed", "pending", "cancelled", "shipped"]
    start = datetime(2022, 1, 1)
    end = datetime(2023, 12, 31)

    records = []
    for i in range(n):
        cid = random.choice(customer_ids)
        amount = round(random.uniform(10, 5000), 2)
        discount = round(random.uniform(0, 30), 2)

        # ~4% NULL customer_id
        if random.random() < 0.04:
            cid = None
        # ~2% NULL total_amount
        if random.random() < 0.02:
            amount = None
        # ~3% negative total_amount
        elif random.random() < 0.03:
            amount = -abs(amount)

        records.append({
            "order_id": f"O{i+1:06d}",
            "customer_id": cid,
            "order_date": mixed_date(start, end),
            "status": random.choice(statuses),
            "total_amount": amount,
            "discount_pct": discount,
        })
    df = pd.DataFrame(records)
    dupes = df.sample(frac=0.08, random_state=42)
    return pd.concat([df, dupes], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)


def generate_order_items(orders_df: pd.DataFrame, orphan_rate: float = 0.04) -> pd.DataFrame:
    valid_order_ids = orders_df["order_id"].dropna().tolist()
    categories = ["Electronics", "Clothing", "Home & Garden", "Books", "Sports", "Beauty"]
    products = [f"P{i:04d}" for i in range(1, 201)]

    records = []
    item_id = 1
    for oid in valid_order_ids:
        for _ in range(random.randint(1, 4)):
            records.append({
                "item_id": f"I{item_id:07d}",
                "order_id": oid,
                "product_id": random.choice(products),
                "category": random.choice(categories),
                "quantity": random.randint(1, 10),
                "unit_price": round(random.uniform(5, 500), 2),
            })
            item_id += 1

    # Introduce ~4% orphaned items (fake order IDs)
    n_orphans = int(len(records) * orphan_rate)
    for _ in range(n_orphans):
        records.append({
            "item_id": f"I{item_id:07d}",
            "order_id": f"O{random.randint(900000, 999999):06d}",  # non-existent
            "product_id": random.choice(products),
            "category": random.choice(categories),
            "quantity": random.randint(1, 10),
            "unit_price": round(random.uniform(5, 500), 2),
        })
        item_id += 1

    df = pd.DataFrame(records)
    dupes = df.sample(frac=0.08, random_state=42)
    return pd.concat([df, dupes], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)


def generate_returns(orders_df: pd.DataFrame) -> pd.DataFrame:
    valid_orders = orders_df[orders_df["total_amount"].notna()].copy()
    # ~20% of orders get a return
    return_orders = valid_orders.sample(frac=0.20, random_state=42)
    reasons = ["Defective", "Wrong item", "Changed mind", "Too large", "Too small", "Not as described"]
    start = datetime(2022, 2, 1)
    end = datetime(2024, 1, 31)

    records = []
    for i, row in enumerate(return_orders.itertuples(), 1):
        refund = round(abs(row.total_amount) * random.uniform(0.5, 1.0), 2)
        # ~5% of refunds exceed the order total
        if random.random() < 0.05:
            refund = round(abs(row.total_amount) * random.uniform(1.05, 1.5), 2)

        records.append({
            "return_id": f"R{i:05d}",
            "order_id": row.order_id,
            "return_date": mixed_date(start, end),
            "reason": random.choice(reasons),
            "refund_amount": refund,
        })

    df = pd.DataFrame(records)
    dupes = df.sample(frac=0.08, random_state=42)
    return pd.concat([df, dupes], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic e-commerce CSVs.")
    parser.add_argument("--rows", type=int, default=2000, help="Number of base orders to generate")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=str, default="./data")
    args = parser.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)
    Faker.seed(args.seed)

    os.makedirs(args.out, exist_ok=True)

    print("Generating customers...")
    customers_df = generate_customers(n=int(args.rows * 0.4))

    print("Generating orders...")
    orders_df = generate_orders(n=args.rows, customer_ids=customers_df["customer_id"].tolist())

    print("Generating order_items...")
    items_df = generate_order_items(orders_df)

    print("Generating returns...")
    returns_df = generate_returns(orders_df)

    for name, df in [
        ("customers", customers_df),
        ("orders", orders_df),
        ("order_items", items_df),
        ("returns", returns_df),
    ]:
        path = os.path.join(args.out, f"{name}.csv")
        df.to_csv(path, index=False)
        print(f"  Wrote {len(df):,} rows → {path}")

    print("Done.")


if __name__ == "__main__":
    main()
