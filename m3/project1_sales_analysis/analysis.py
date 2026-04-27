"""
Project 1 — Retail Sales Analysis
==================================
Loads datasets/sales_data.csv, performs comprehensive sales analysis,
saves 5 charts to visualizations/, and prints an executive summary.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler

# ── Paths ────────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE, "..", "datasets", "sales_data.csv")
VIZ_DIR   = os.path.join(BASE, "..", "visualizations")
os.makedirs(VIZ_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted")

# ── Load Data ─────────────────────────────────────────────────────────────────
def load_data(path):
    if not os.path.exists(path):
        print(f"[WARN] {path} not found — regenerating …")
        _generate_fallback(path)
    df = pd.read_csv(path, parse_dates=["OrderDate"])
    return df


def _generate_fallback(path):
    """Fallback: regenerate sales_data.csv if missing."""
    np.random.seed(42)
    n = 500
    categories = ["Electronics", "Clothing", "Food", "Books", "Sports"]
    regions    = ["North", "South", "East", "West"]
    salespeople = ["Alice", "Bob", "Carol", "David", "Eve", "Frank"]
    products = {
        "Electronics": ["Laptop", "Phone", "Tablet", "Headphones", "Camera"],
        "Clothing":    ["T-Shirt", "Jeans", "Jacket", "Dress", "Shoes"],
        "Food":        ["Coffee", "Tea", "Snacks", "Organic Basket", "Spices"],
        "Books":       ["Fiction", "Non-Fiction", "Textbook", "Comic", "Cookbook"],
        "Sports":      ["Yoga Mat", "Dumbbell", "Running Shoes", "Cycle", "Racket"],
    }
    dates   = pd.date_range("2023-01-01", "2023-12-31", periods=n)
    cat_arr = np.random.choice(categories, n)
    prod_arr = [np.random.choice(products[c]) for c in cat_arr]
    qty      = np.random.randint(1, 20, n)
    unit_price = np.round(np.random.uniform(5, 500, n), 2)
    df = pd.DataFrame({
        "OrderID":     [f"ORD{str(i).zfill(4)}" for i in range(1, n + 1)],
        "OrderDate":   dates,
        "CustomerID":  [f"CUST{np.random.randint(100, 999)}" for _ in range(n)],
        "Product":     prod_arr,
        "Category":    cat_arr,
        "Quantity":    qty,
        "UnitPrice":   unit_price,
        "Sales":       np.round(qty * unit_price, 2),
        "Region":      np.random.choice(regions, n),
        "Salesperson": np.random.choice(salespeople, n),
    })
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)


# ── Analysis helpers ──────────────────────────────────────────────────────────
def monthly_sales_trend(df):
    monthly = df.resample("ME", on="OrderDate")["Sales"].sum().reset_index()
    monthly["Month"] = monthly["OrderDate"].dt.strftime("%b")
    return monthly


def category_performance(df):
    return (
        df.groupby("Category")["Sales"]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending=False)
    )


def regional_analysis(df):
    return (
        df.groupby("Region")
        .agg(TotalSales=("Sales", "sum"), Orders=("OrderID", "count"))
        .reset_index()
        .sort_values("TotalSales", ascending=False)
    )


def top_products(df, n=10):
    return (
        df.groupby("Product")["Sales"]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending=False)
        .head(n)
    )


def customer_segmentation(df):
    cust = (
        df.groupby("CustomerID")
        .agg(TotalSpend=("Sales", "sum"), Orders=("OrderID", "count"))
        .reset_index()
    )
    cust["Segment"] = pd.qcut(
        cust["TotalSpend"],
        q=3,
        labels=["Low Value", "Mid Value", "High Value"],
    )
    return cust


def rfm_analysis(df):
    snapshot = df["OrderDate"].max() + pd.Timedelta(days=1)
    rfm = df.groupby("CustomerID").agg(
        Recency=("OrderDate", lambda x: (snapshot - x.max()).days),
        Frequency=("OrderID", "count"),
        Monetary=("Sales", "sum"),
    ).reset_index()
    scaler = MinMaxScaler()
    rfm[["R_score", "F_score", "M_score"]] = scaler.fit_transform(
        rfm[["Recency", "Frequency", "Monetary"]]
    )
    rfm["R_score"] = 1 - rfm["R_score"]          # lower recency = better
    rfm["RFM_score"] = rfm[["R_score", "F_score", "M_score"]].mean(axis=1)
    rfm["Segment"] = pd.cut(
        rfm["RFM_score"],
        bins=[0, 0.33, 0.66, 1.0],
        labels=["At Risk", "Potential", "Champion"],
        include_lowest=True,
    )
    return rfm


# ── Visualisations ────────────────────────────────────────────────────────────
def plot_monthly_sales(monthly, out_dir):
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(monthly["Month"], monthly["Sales"] / 1_000, color=sns.color_palette("Blues_d", len(monthly)))
    ax.plot(monthly["Month"], monthly["Sales"] / 1_000, "o-", color="#e74c3c", linewidth=2)
    ax.set_title("Monthly Sales Trend — 2023", fontsize=15, fontweight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("Sales ($ thousands)")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "monthly_sales.png"), dpi=150)
    plt.close()


def plot_category_performance(cat_df, out_dir):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    # Bar chart
    sns.barplot(data=cat_df, x="Category", y="Sales", hue="Category", ax=axes[0],
                palette="viridis", legend=False)
    axes[0].set_title("Revenue by Category")
    axes[0].set_ylabel("Total Sales ($)")
    axes[0].tick_params(axis="x", rotation=15)
    # Pie chart
    axes[1].pie(
        cat_df["Sales"],
        labels=cat_df["Category"],
        autopct="%1.1f%%",
        colors=sns.color_palette("viridis", len(cat_df)),
        startangle=140,
    )
    axes[1].set_title("Category Share of Revenue")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "category_performance.png"), dpi=150)
    plt.close()


def plot_regional_sales(reg_df, out_dir):
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(reg_df["Region"], reg_df["TotalSales"] / 1_000,
                  color=sns.color_palette("Set2", len(reg_df)))
    ax.bar_label(bars, labels=[f"${v/1:.0f}K" for v in reg_df["TotalSales"] / 1_000], padding=3)
    ax.set_title("Regional Sales Performance", fontsize=14, fontweight="bold")
    ax.set_xlabel("Region")
    ax.set_ylabel("Total Sales ($ thousands)")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "regional_sales.png"), dpi=150)
    plt.close()


def plot_customer_segments(seg_df, out_dir):
    counts = seg_df["Segment"].value_counts()
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.pie(
        counts,
        labels=counts.index,
        autopct="%1.1f%%",
        colors=["#2ecc71", "#f39c12", "#e74c3c"],
        explode=[0.05] * len(counts),
        startangle=90,
    )
    ax.set_title("Customer Value Segments", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "customer_segments.png"), dpi=150)
    plt.close()


def plot_top_products(prod_df, out_dir):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=prod_df, y="Product", x="Sales", hue="Product", ax=ax,
                palette="rocket", legend=False)
    ax.set_title("Top 10 Products by Revenue", fontsize=14, fontweight="bold")
    ax.set_xlabel("Total Sales ($)")
    ax.set_ylabel("")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "top_products.png"), dpi=150)
    plt.close()


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    df = load_data(DATA_PATH)

    # Analyses
    monthly  = monthly_sales_trend(df)
    cat_perf = category_performance(df)
    reg_anal = regional_analysis(df)
    top_prod = top_products(df)
    cust_seg = customer_segmentation(df)
    rfm      = rfm_analysis(df)

    # Charts
    plot_monthly_sales(monthly, VIZ_DIR)
    plot_category_performance(cat_perf, VIZ_DIR)
    plot_regional_sales(reg_anal, VIZ_DIR)
    plot_customer_segments(cust_seg, VIZ_DIR)
    plot_top_products(top_prod, VIZ_DIR)

    # Executive summary
    total_revenue  = df["Sales"].sum()
    avg_order      = df["Sales"].mean()
    top_cat        = cat_perf.iloc[0]["Category"]
    top_cat_pct    = cat_perf.iloc[0]["Sales"] / total_revenue * 100
    top_region     = reg_anal.iloc[0]["Region"]
    champions_pct  = (rfm["Segment"] == "Champion").mean() * 100
    peak_month     = monthly.loc[monthly["Sales"].idxmax(), "Month"]

    print("=" * 60)
    print("  PROJECT 1 — RETAIL SALES ANALYSIS: EXECUTIVE SUMMARY")
    print("=" * 60)
    print(f"  Total Revenue (2023)  : ${total_revenue:>12,.2f}")
    print(f"  Total Orders          : {len(df):>12,}")
    print(f"  Average Order Value   : ${avg_order:>12,.2f}")
    print(f"  Top Category          : {top_cat} ({top_cat_pct:.1f}% of revenue)")
    print(f"  Top Region            : {top_region}")
    print(f"  Peak Month            : {peak_month}")
    print(f"  Champion Customers    : {champions_pct:.1f}% of customer base")
    print("-" * 60)
    print("  Charts saved to:", os.path.abspath(VIZ_DIR))
    print("  Files: monthly_sales.png | category_performance.png |")
    print("         regional_sales.png | customer_segments.png | top_products.png")
    print("=" * 60)


if __name__ == "__main__":
    main()
