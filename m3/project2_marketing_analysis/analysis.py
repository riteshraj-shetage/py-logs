"""
Project 2 — Marketing Campaign Analysis
=========================================
Loads datasets/marketing_data.csv, performs ROI, conversion rate,
budget efficiency, and campaign performance analysis, saves 4 charts
to visualizations/, and prints a summary.
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# ── Paths ────────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE, "..", "datasets", "marketing_data.csv")
VIZ_DIR   = os.path.join(BASE, "..", "visualizations")
os.makedirs(VIZ_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted")


# ── Load Data ─────────────────────────────────────────────────────────────────
def load_data(path):
    if not os.path.exists(path):
        print(f"[WARN] {path} not found — regenerating …")
        _generate_fallback(path)
    return pd.read_csv(path, parse_dates=["StartDate", "EndDate"])


def _generate_fallback(path):
    np.random.seed(42)
    m = 300
    channels  = ["Email", "Social Media", "SEO", "PPC", "Content"]
    starts    = pd.date_range("2023-01-01", "2023-10-31", periods=m)
    dur       = np.random.randint(7, 60, m)
    impressions = np.random.randint(1000, 100000, m)
    clicks    = np.round(impressions * np.random.uniform(0.01, 0.15, m)).astype(int)
    conversions = np.round(clicks * np.random.uniform(0.02, 0.20, m)).astype(int)
    budget    = np.round(np.random.uniform(500, 20000, m), 2)
    revenue   = np.round(conversions * np.random.uniform(20, 200, m), 2)
    df = pd.DataFrame({
        "CampaignID":   [f"CAMP{str(i).zfill(4)}" for i in range(1, m + 1)],
        "CampaignName": [f"Campaign_{i}" for i in range(1, m + 1)],
        "Channel":      np.random.choice(channels, m),
        "Budget":       budget,
        "Clicks":       clicks,
        "Impressions":  impressions,
        "Conversions":  conversions,
        "Revenue":      revenue,
        "StartDate":    starts.strftime("%Y-%m-%d"),
        "EndDate":      [(starts[i] + pd.Timedelta(days=int(dur[i]))).strftime("%Y-%m-%d") for i in range(m)],
    })
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)


# ── Analysis helpers ──────────────────────────────────────────────────────────
def compute_metrics(df):
    df = df.copy()
    df["ROI"]             = ((df["Revenue"] - df["Budget"]) / df["Budget"]) * 100
    df["CTR"]             = (df["Clicks"] / df["Impressions"]) * 100
    df["ConversionRate"]  = (df["Conversions"] / df["Clicks"].replace(0, np.nan)) * 100
    df["CostPerConv"]     = df["Budget"] / df["Conversions"].replace(0, np.nan)
    return df


def channel_summary(df):
    return (
        df.groupby("Channel")
        .agg(
            AvgROI=("ROI", "mean"),
            TotalRevenue=("Revenue", "sum"),
            TotalBudget=("Budget", "sum"),
            AvgConvRate=("ConversionRate", "mean"),
            AvgCostPerConv=("CostPerConv", "mean"),
            Campaigns=("CampaignID", "count"),
        )
        .reset_index()
        .sort_values("AvgROI", ascending=False)
    )


def top_campaigns(df, n=10):
    return df.nlargest(n, "ROI")[["CampaignName", "Channel", "Budget", "Revenue", "ROI"]]


# ── Visualisations ────────────────────────────────────────────────────────────
def plot_channel_roi(ch_df, out_dir):
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = sns.barplot(data=ch_df, x="Channel", y="AvgROI", hue="Channel", ax=ax,
                       palette="coolwarm", legend=False)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_title("Average ROI by Marketing Channel", fontsize=14, fontweight="bold")
    ax.set_xlabel("Channel")
    ax.set_ylabel("Average ROI (%)")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "channel_roi.png"), dpi=150)
    plt.close()


def plot_conversion_rates(ch_df, out_dir):
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=ch_df, x="Channel", y="AvgConvRate", hue="Channel", ax=ax,
                palette="viridis", legend=False)
    ax.set_title("Average Conversion Rate by Channel", fontsize=14, fontweight="bold")
    ax.set_xlabel("Channel")
    ax.set_ylabel("Conversion Rate (%)")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "conversion_rates.png"), dpi=150)
    plt.close()


def plot_budget_vs_revenue(df, out_dir):
    fig, ax = plt.subplots(figsize=(9, 6))
    scatter = ax.scatter(
        df["Budget"], df["Revenue"],
        c=df["ROI"], cmap="RdYlGn", alpha=0.7, edgecolors="grey", linewidths=0.3, s=40,
    )
    plt.colorbar(scatter, ax=ax, label="ROI (%)")
    ax.set_title("Budget vs. Revenue (coloured by ROI)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Campaign Budget ($)")
    ax.set_ylabel("Campaign Revenue ($)")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "budget_vs_revenue.png"), dpi=150)
    plt.close()


def plot_campaign_performance(df, out_dir):
    top = df.nlargest(15, "Revenue")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=top, y="CampaignName", x="Revenue", hue="Channel", ax=ax, dodge=False,
                palette="tab10")
    ax.set_title("Top 15 Campaigns by Revenue", fontsize=14, fontweight="bold")
    ax.set_xlabel("Revenue ($)")
    ax.set_ylabel("")
    ax.legend(title="Channel", bbox_to_anchor=(1.01, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "campaign_performance.png"), dpi=150)
    plt.close()


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    df  = load_data(DATA_PATH)
    df  = compute_metrics(df)
    ch  = channel_summary(df)
    top = top_campaigns(df)

    plot_channel_roi(ch, VIZ_DIR)
    plot_conversion_rates(ch, VIZ_DIR)
    plot_budget_vs_revenue(df, VIZ_DIR)
    plot_campaign_performance(df, VIZ_DIR)

    total_rev   = df["Revenue"].sum()
    total_bud   = df["Budget"].sum()
    overall_roi = (total_rev - total_bud) / total_bud * 100
    best_chan    = ch.iloc[0]["Channel"]
    best_roi    = ch.iloc[0]["AvgROI"]

    print("=" * 60)
    print("  PROJECT 2 — MARKETING CAMPAIGN ANALYSIS: SUMMARY")
    print("=" * 60)
    print(f"  Total Campaigns       : {len(df):>10,}")
    print(f"  Total Budget Spent    : ${total_bud:>10,.2f}")
    print(f"  Total Revenue         : ${total_rev:>10,.2f}")
    print(f"  Overall ROI           : {overall_roi:>10.1f}%")
    print(f"  Best Channel (ROI)    : {best_chan} ({best_roi:.1f}%)")
    print("-" * 60)
    print("  Channel ROI breakdown:")
    for _, row in ch.iterrows():
        print(f"    {row['Channel']:<16} avg ROI={row['AvgROI']:6.1f}%  "
              f"conv_rate={row['AvgConvRate']:5.1f}%")
    print("-" * 60)
    print("  Charts saved to:", os.path.abspath(VIZ_DIR))
    print("  Files: channel_roi.png | conversion_rates.png |")
    print("         budget_vs_revenue.png | campaign_performance.png")
    print("=" * 60)


if __name__ == "__main__":
    main()
