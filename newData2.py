"""
Daily sales/stock feed simulator.

Generates sales & stock data using SKUs from the product catalog
(generate_catalog.py), with a running stock simulation per SKU
(stock decreases with units_sold, jumps up on restocks) so the
data behaves like a real inventory feed over time.

Output columns:
date, sku_id, brand, category, units_sold, restocked_units, recorded_stock, price
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta


def load_catalog(path="Data/product_catalog.csv"):
    return pd.read_csv(path)


def _fmt_date(d):
    # M/D/YYYY, no leading zeros — matches the existing sales_inventory.csv format
    return f"{d.month}/{d.day}/{d.year}"


def generate_historical_feed(catalog_df, start_date, end_date, seed=42):
    """
    Generate a full historical range of daily feeds with a running
    stock simulation per SKU (stock carries over day to day).
    """
    rng = np.random.default_rng(seed)

    stock_levels = {
        row["sku_id"]: int(rng.integers(100, 500))
        for _, row in catalog_df.iterrows()
    }

    rows = []
    current = start_date
    while current <= end_date:
        for _, item in catalog_df.iterrows():
            sku_id = item["sku_id"]
            brand = item["brand"]
            category = item["category"]
            price = item["price"]

            lam = max(1, 30000 / max(price, 1000))
            units_sold = int(rng.poisson(lam))
            units_sold = min(units_sold, stock_levels[sku_id])

            restocked_units = int(rng.choice(
                [0, 0, 0, 0, 50, 100, 200],
                p=[0.5, 0.15, 0.1, 0.1, 0.08, 0.05, 0.02]
            ))

            stock_levels[sku_id] = max(0, stock_levels[sku_id] - units_sold + restocked_units)

            rows.append({
                "date": _fmt_date(current),
                "sku_id": sku_id,
                "brand": brand,
                "category": category,
                "units_sold": units_sold,
                "restocked_units": restocked_units,
                "recorded_stock": stock_levels[sku_id],
                "price": price,
            })

        current += timedelta(days=1)

    return pd.DataFrame(rows)


def generate_daily_feed(catalog_df, feed_date=None, previous_stock=None, seed=None):
    """
    Generate a single day's rows, continuing from previous_stock
    (a dict of {sku_id: stock_level}) if provided. This is what your
    daily ingestion job should call each day, passing in yesterday's
    ending stock so levels carry over correctly.

    Returns (daily_df, updated_stock_dict).
    """
    feed_date = feed_date or date.today()
    rng = np.random.default_rng(seed)

    stock_levels = dict(previous_stock) if previous_stock else {
        row["sku_id"]: int(rng.integers(100, 500)) for _, row in catalog_df.iterrows()
    }

    rows = []
    for _, item in catalog_df.iterrows():
        sku_id = item["sku_id"]
        brand = item["brand"]
        category = item["category"]
        price = item["price"]

        lam = max(1, 30000 / max(price, 1000))
        units_sold = int(rng.poisson(lam))
        units_sold = min(units_sold, stock_levels.get(sku_id, 0))

        restocked_units = int(rng.choice(
            [0, 0, 0, 0, 50, 100, 200],
            p=[0.5, 0.15, 0.1, 0.1, 0.08, 0.05, 0.02]
        ))

        stock_levels[sku_id] = max(0, stock_levels.get(sku_id, 0) - units_sold + restocked_units)

        rows.append({
            "date": _fmt_date(feed_date),
            "sku_id": sku_id,
            "brand": brand,
            "category": category,
            "units_sold": units_sold,
            "restocked_units": restocked_units,
            "recorded_stock": stock_levels[sku_id],
            "price": price,
        })

    return pd.DataFrame(rows), stock_levels


if __name__ == "__main__":
    catalog_df = load_catalog()

    start = date.today() - timedelta(days=90)
    end = date.today() - timedelta(days=1)
    history_df = generate_historical_feed(catalog_df, start, end)
    history_df.to_csv("Data/sales_inventory.csv", index=False)
    print(f"Generated {len(history_df)} historical rows from {start} to {end}")
    print(history_df.head(10))