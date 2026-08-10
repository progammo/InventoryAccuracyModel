import pandas as pd
import numpy as np

def prepare_data():
    df = pd.read_csv("Data\\sales_inventory.csv")
    df["date"] = pd.to_datetime(df["date"])
    df.drop_duplicates(subset=["sku_id", "date","brand"], keep="last", inplace=True)
    df.to_csv("Data\\sales_inventory_cleaned.csv", index=False)
    df = df.sort_values(["sku_id", "date"]).reset_index(drop=True)
    
    df = (
        df.groupby(["sku_id", "date"], as_index=False)
          .agg({
              "brand": "first",
              "units_sold": "sum",
              "restocked_units": "sum",
              "recorded_stock": "last",
              "price": "mean"
          })
    )

    df["promotional_flag_discount"] = 0
    mask = (df["date"] >= "2026-02-09") & (df["date"] <= "2026-02-15")
    mask2 = (df["date"] >= "2026-04-13") & (df["date"] <= "2026-04-20")
    mask3 = (df["date"] >= "2026-06-15") & (df["date"] <= "2026-06-22")
    df.loc[mask, "promotional_flag_discount"] = 5000
    df.loc[mask2, "promotional_flag_discount"] = 3000
    df.loc[mask3, "promotional_flag_discount"] = 4000
    df["net_price"] = df["price"] - df["promotional_flag_discount"]

    weekly_df = (
        df.groupby(["sku_id", pd.Grouper(key="date", freq="W-MON")])
        .agg({'units_sold': 'sum', 'recorded_stock': 'last', 'net_price': 'mean'})
    )

    weekly_df['lag_1_week'] = weekly_df.groupby('sku_id')['units_sold'].shift(1)
    weekly_df['lag_2_week'] = weekly_df.groupby('sku_id')['units_sold'].shift(2)
    weekly_df['lag_4_week'] = weekly_df.groupby('sku_id')['units_sold'].shift(4)

    for window in [4, 8]:
        weekly_df[f"rolling_{window}w_mean"] = weekly_df.groupby("sku_id")["units_sold"].transform(
            lambda x: x.shift(1).rolling(window=window, min_periods=1).mean())
        weekly_df[f"rolling_{window}w_std"] = weekly_df.groupby("sku_id")["units_sold"].transform(
            lambda x: x.shift(1).rolling(window=window, min_periods=1).std())
    weekly_df["rolling_4w_median"] = weekly_df.groupby("sku_id")["units_sold"].transform(
        lambda x: x.shift(1).rolling(window=4, min_periods=1).median())

    weekly_df.dropna(inplace=True)

    # Save outputs for the next stage
    df.to_csv("Data\\processed_daily.csv", index=False)
    weekly_df.reset_index().to_csv("Data\\processed_weekly.csv", index=False)
    print("Saved Data\\processed_daily.csv and Data\\processed_weekly.csv")

if __name__ == "__main__":
    prepare_data()
    