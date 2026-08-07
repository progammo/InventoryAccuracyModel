import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Inventory Forecast Dashboard", layout="wide")

@st.cache_data
def load_data():
    test_df = pd.read_csv("Data\\test_predictions.csv", parse_dates=["date"])
    safety_stock = pd.read_csv("Data\\safety_stock.csv")
    return test_df, safety_stock

test_df, safety_stock = load_data()

results_df = test_df.merge(safety_stock, on="sku_id", how="left").rename(
    columns={"q90_daily_demand": "safety_stock"})

results_df["expected_stock"] = results_df["recorded_stock"] - results_df["lgbm_pred"]
results_df["recommended_order"] = np.maximum(
    0, results_df["lgbm_pred"] + results_df["safety_stock"] - results_df["recorded_stock"])

conditions = [
    results_df["expected_stock"] < 0,
    results_df["expected_stock"] < results_df["safety_stock"]
]
choices = ["Stockout", "Low Stock"]
results_df["status"] = np.select(conditions, choices, default="Safe")
results_df["overstock_limit"] = results_df["lgbm_pred"] * 2 + results_df["safety_stock"]
results_df.loc[results_df["recorded_stock"] > results_df["overstock_limit"], "status"] = "Overstock"

df = results_df

st.title("📦 Inventory Forecast Dashboard")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total SKUs", df["sku_id"].nunique())
c2.metric("Stockout", (df["status"] == "Stockout").sum())
c3.metric("Low Stock", (df["status"] == "Low Stock").sum())
c4.metric("Overstock", (df["status"] == "Overstock").sum())
st.divider()

sku = st.sidebar.selectbox("Select SKU", sorted(df["sku_id"].unique()))
sku_df = df[df["sku_id"] == sku].sort_values("date")
latest = sku_df.iloc[-1]

left, right = st.columns(2)
with left:
    st.subheader("Forecast")
    st.metric("Forecast Demand", f"{latest['lgbm_pred']:.0f}")
    st.metric("Current Stock", latest["recorded_stock"])
    st.metric("Expected Stock", f"{latest['expected_stock']:.0f}")
with right:
    st.subheader("Inventory")
    st.metric("Safety Stock", latest["safety_stock"])
    st.metric("Order Quantity", f"{latest['recommended_order']:.0f}")
    st.metric("Status", latest["status"])

st.divider()
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(sku_df["date"], sku_df["units_sold"], label="Actual")
ax.plot(sku_df["date"], sku_df["lgbm_pred"], label="Forecast")
ax.plot(sku_df["date"], sku_df["rolling_8w_mean"], label="Rolling Mean")
ax.legend()
st.pyplot(fig)

st.divider()
st.subheader("SKU Details")
st.dataframe(sku_df)

st.divider()
st.subheader("Complete Inventory Table")
st.dataframe(df.sort_values("recommended_order", ascending=False))