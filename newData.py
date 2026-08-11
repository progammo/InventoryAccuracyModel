"""
Synthetic product catalog generator.

Generates a realistic-looking (but fully fake) product catalog with
categories, brands, SKUs, and prices — useful as dummy data for
building/testing an inventory forecasting pipeline before real data
is available.
"""

import pandas as pd
import numpy as np
import random

# ---- Configuration: categories, brands, price ranges ----

CATEGORIES = {
    "Mobiles": {
        "brands": ["Samsung", "Xiaomi", "Infinix", "Tecno", "Vivo", "Oppo", "Apple", "Realme",
                   "Honor", "Nothing", "Itel", "Nokia", "OnePlus"],
        "price_range": (15000, 250000),
    },
    "Earless Buds": {
        "brands": ["JBL", "Sony", "Anker", "Xiaomi", "QCY", "Soundcore", "Oraimo",
                   "Faster", "Hoco", "Baseus", "Space"],
        "price_range": (1200, 35000),
    },
    "Smart Watches": {
        "brands": ["Xiaomi", "Samsung", "Apple", "Amazfit", "Faster", "Vizo",
                   "Ronin", "Sigma", "Zero"],
        "price_range": (2000, 90000),
    },
    "Trimmers Shaver": {
        "brands": ["Faster", "Sonic", "Riversong", "Vgo-Tel", "Sigma", "Login"],
        "price_range": (1500, 25000),
    },
    "Power Banks": {
        "brands": ["Anker", "Xiaomi", "Faster", "Oraimo", "Ldnio", "Baseus",
                   "Space", "Vizo", "Sovo"],
        "price_range": (1200, 20000),
    },
    "Wall Chargers": {
        "brands": ["Anker", "Xiaomi", "Samsung", "Apple", "Ldnio", "Baseus",
                   "Hoco", "Faster", "XO"],
        "price_range": (500, 12000),
    },
    "Bluetooth Speakers": {
        "brands": ["JBL", "Sony", "Anker", "Tronsmart", "Audionic", "Sound-Crush",
                   "Xiaomi", "W-King", "Soundcore"],
        "price_range": (1500, 70000),
    },
    "Tablets": {
        "brands": ["Samsung", "Apple", "Xiaomi", "Lenovo", "Huawei", "Infinix"],
        "price_range": (25000, 300000),
    },
    "Laptops": {
        "brands": ["HP", "Dell", "Lenovo", "Asus", "Acer", "Apple", "MSI"],
        "price_range": (60000, 400000),
    },
}

def generate_catalog(n_products=200, seed=42):
    rng = np.random.default_rng(seed)
    random.seed(seed)

    rows = []
    sku_counter = 1

    categories_list = list(CATEGORIES.keys())

    for _ in range(n_products):
        category = random.choice(categories_list)
        cat_info = CATEGORIES[category]
        brand = random.choice(cat_info["brands"])
        low, high = cat_info["price_range"]

        # Skewed price distribution (more budget items than premium ones)
        price = round(float(rng.lognormal(mean=np.log((low + high) / 4), sigma=0.5)), -1)
        price = max(low, min(price, high))

        sku_id = f"SKU_{brand.upper().replace(' ', '_').replace('&','AND')}_{sku_counter:04d}"
        sku_counter += 1

        rows.append({
            "sku_id": sku_id,
            "category": category,
            "brand": brand,
            "price": price,
        })

    catalog_df = pd.DataFrame(rows).drop_duplicates(subset=["sku_id"]).reset_index(drop=True)
    return catalog_df


if __name__ == "__main__":
    catalog_df = generate_catalog(n_products=200)
    catalog_df.to_csv("Data/product_catalog.csv", index=False)
    print(f"Generated {len(catalog_df)} products")
    print(catalog_df.head(10))
    print("\nCategory breakdown:")
    print(catalog_df["category"].value_counts())