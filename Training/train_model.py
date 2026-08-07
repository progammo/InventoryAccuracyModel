import pandas as pd
import numpy as np
import pickle
import lightgbm as lgb
from sklearn.metrics import mean_absolute_error

def train():
    weeklytraintest = pd.read_csv("Data\\processed_weekly.csv", parse_dates=["date"])
    weeklytraintest = weeklytraintest.sort_values(["sku_id", "date"]).reset_index(drop=True)

    row_position = weeklytraintest.groupby("sku_id").cumcount()
    group_size = weeklytraintest.groupby("sku_id")["sku_id"].transform("count")
    train_cutoff = (group_size * 0.8).astype(int)

    weeklytraintest["split"] = "train"
    weeklytraintest.loc[row_position >= train_cutoff, "split"] = "test"

    train_df = weeklytraintest[weeklytraintest['split'] == 'train'].drop(columns=['split']).copy()
    test_df = weeklytraintest[weeklytraintest['split'] == 'test'].drop(columns=['split']).copy()

    for d in [train_df, test_df]:
        d["sku_id"] = d["sku_id"].astype("category")
        d["day"] = d["date"].dt.day
        d["month"] = d["date"].dt.month
        d["year"] = d["date"].dt.year

    X_train = train_df.drop(columns=["units_sold", "date"])
    X_test = test_df.drop(columns=["units_sold", "date"])
    y_train = train_df["units_sold"]
    y_test = test_df["units_sold"]

    lgbm = lgb.LGBMRegressor(learning_rate=0.05, n_estimators=300, num_leaves=31, random_state=42)
    lgbm.fit(X_train, y_train, categorical_feature=["sku_id"])
    pred = lgbm.predict(X_test)

    mae = mean_absolute_error(y_test, pred)
    print(f"MAE: {mae:.2f}")

    test_df["lgbm_pred"] = pred

    # Safety stock
    safety_stock = (
        train_df.groupby('sku_id')['units_sold'].quantile(0.90).reset_index()
        .rename(columns={'units_sold': 'q90_daily_demand'})
    )
    safety_stock["q90_daily_demand"] = safety_stock["q90_daily_demand"].apply(lambda x: int(np.ceil(x)))

    # Save everything the dashboard needs
    with open("Training\\model.pkl", "wb") as f:
        pickle.dump(lgbm, f)
    test_df.to_csv("Data\\test_predictions.csv", index=False)
    safety_stock.to_csv("Data\\safety_stock.csv", index=False)
    print("Saved Training\\model.pkl, Data\\test_predictions.csv, Data\\safety_stock.csv")

if __name__ == "__main__":
    train()