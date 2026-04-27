"""
Project 3 — Operations Analysis
=================================
Loads datasets/operations_data.csv, performs task completion rate,
duration, cost, bottleneck, and priority analysis, saves 4 charts
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
DATA_PATH = os.path.join(BASE, "..", "datasets", "operations_data.csv")
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
    p = 400
    departments = ["Warehouse", "Logistics", "Customer Service", "Production", "Quality"]
    statuses    = ["Completed", "In Progress", "Delayed"]
    priorities  = ["High", "Medium", "Low"]
    employees   = [f"EMP{str(i).zfill(3)}" for i in range(1, 51)]
    task_names  = ["Inventory Check", "Shipment Processing", "Quality Audit",
                   "Order Fulfillment", "Staff Training", "Equipment Maintenance",
                   "Report Generation", "Customer Follow-up"]
    starts = pd.date_range("2023-01-01", "2023-11-30", periods=p)
    dur    = np.random.randint(1, 30, p)
    cost   = np.round(np.random.uniform(100, 5000, p), 2)
    df = pd.DataFrame({
        "OrderID":    [f"OPS{str(i).zfill(4)}" for i in range(1, p + 1)],
        "Department": np.random.choice(departments, p),
        "TaskName":   np.random.choice(task_names, p),
        "StartDate":  starts.strftime("%Y-%m-%d"),
        "EndDate":    [(starts[i] + pd.Timedelta(days=int(dur[i]))).strftime("%Y-%m-%d") for i in range(p)],
        "Duration":   dur,
        "Cost":       cost,
        "Status":     np.random.choice(statuses, p, p=[0.60, 0.25, 0.15]),
        "Employee":   np.random.choice(employees, p),
        "Priority":   np.random.choice(priorities, p, p=[0.30, 0.45, 0.25]),
    })
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)


# ── Analysis helpers ──────────────────────────────────────────────────────────
def completion_rates(df):
    rates = (
        df.groupby("Department")["Status"]
        .value_counts(normalize=True)
        .mul(100)
        .rename("Percentage")
        .reset_index()
    )
    return rates


def avg_duration_by_dept(df):
    return (
        df.groupby("Department")["Duration"]
        .mean()
        .reset_index()
        .rename(columns={"Duration": "AvgDuration"})
        .sort_values("AvgDuration", ascending=False)
    )


def cost_by_dept(df):
    return (
        df.groupby("Department")
        .agg(TotalCost=("Cost", "sum"), AvgCost=("Cost", "mean"), Tasks=("OrderID", "count"))
        .reset_index()
        .sort_values("TotalCost", ascending=False)
    )


def priority_status(df):
    return (
        df.groupby(["Priority", "Status"])["OrderID"]
        .count()
        .reset_index()
        .rename(columns={"OrderID": "Count"})
    )


# ── Visualisations ────────────────────────────────────────────────────────────
def plot_completion_rates(df, out_dir):
    completed = df[df["Status"] == "Completed"].groupby("Department").size()
    total     = df.groupby("Department").size()
    rate_df   = (completed / total * 100).reset_index()
    rate_df.columns = ["Department", "CompletionRate"]

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=rate_df, x="Department", y="CompletionRate", hue="Department",
                ax=ax, palette="Greens_d", legend=False)
    ax.axhline(rate_df["CompletionRate"].mean(), color="red", linestyle="--", linewidth=1,
               label=f"Average ({rate_df['CompletionRate'].mean():.1f}%)")
    ax.set_title("Task Completion Rate by Department", fontsize=14, fontweight="bold")
    ax.set_xlabel("Department")
    ax.set_ylabel("Completion Rate (%)")
    ax.legend()
    ax.tick_params(axis="x", rotation=15)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "completion_rates.png"), dpi=150)
    plt.close()


def plot_dept_duration(dur_df, out_dir):
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=dur_df, x="Department", y="AvgDuration", hue="Department",
                ax=ax, palette="Blues_d", legend=False)
    ax.set_title("Average Task Duration by Department (days)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Department")
    ax.set_ylabel("Average Duration (days)")
    ax.tick_params(axis="x", rotation=15)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "dept_duration.png"), dpi=150)
    plt.close()


def plot_cost_by_dept(cost_df, out_dir):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    sns.barplot(data=cost_df, x="Department", y="TotalCost", hue="Department",
                ax=axes[0], palette="Oranges_d", legend=False)
    axes[0].set_title("Total Cost by Department")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Total Cost ($)")
    axes[0].tick_params(axis="x", rotation=15)
    sns.barplot(data=cost_df, x="Department", y="AvgCost", hue="Department",
                ax=axes[1], palette="Reds_d", legend=False)
    axes[1].set_title("Average Task Cost by Department")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Average Cost ($)")
    axes[1].tick_params(axis="x", rotation=15)
    plt.suptitle("Cost Analysis by Department", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "cost_by_dept.png"), dpi=150)
    plt.close()


def plot_priority_analysis(df, out_dir):
    pivot = (
        df.groupby(["Priority", "Status"])["OrderID"]
        .count()
        .unstack(fill_value=0)
    )
    # Ensure consistent column order
    for col in ["Completed", "In Progress", "Delayed"]:
        if col not in pivot.columns:
            pivot[col] = 0
    pivot = pivot[["Completed", "In Progress", "Delayed"]]
    priority_order = ["High", "Medium", "Low"]
    pivot = pivot.reindex([p for p in priority_order if p in pivot.index])

    ax = pivot.plot(kind="bar", figsize=(9, 5), colormap="Set2", edgecolor="grey")
    ax.set_title("Task Count by Priority and Status", fontsize=14, fontweight="bold")
    ax.set_xlabel("Priority")
    ax.set_ylabel("Number of Tasks")
    ax.legend(title="Status")
    ax.tick_params(axis="x", rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "priority_analysis.png"), dpi=150)
    plt.close()


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    df       = load_data(DATA_PATH)
    dur_df   = avg_duration_by_dept(df)
    cost_df  = cost_by_dept(df)

    plot_completion_rates(df, VIZ_DIR)
    plot_dept_duration(dur_df, VIZ_DIR)
    plot_cost_by_dept(cost_df, VIZ_DIR)
    plot_priority_analysis(df, VIZ_DIR)

    total_tasks     = len(df)
    completed_pct   = (df["Status"] == "Completed").mean() * 100
    delayed_pct     = (df["Status"] == "Delayed").mean() * 100
    total_cost      = df["Cost"].sum()
    avg_duration    = df["Duration"].mean()
    most_delayed    = (
        df[df["Status"] == "Delayed"]
        .groupby("Department")["OrderID"]
        .count()
        .idxmax()
    )

    print("=" * 60)
    print("  PROJECT 3 — OPERATIONS ANALYSIS: SUMMARY")
    print("=" * 60)
    print(f"  Total Tasks           : {total_tasks:>10,}")
    print(f"  Completion Rate       : {completed_pct:>10.1f}%")
    print(f"  Delayed Rate          : {delayed_pct:>10.1f}%")
    print(f"  Total Operational Cost: ${total_cost:>10,.2f}")
    print(f"  Average Task Duration : {avg_duration:>10.1f} days")
    print(f"  Dept with Most Delays : {most_delayed}")
    print("-" * 60)
    print("  Duration by department:")
    for _, row in dur_df.iterrows():
        print(f"    {row['Department']:<20} avg={row['AvgDuration']:.1f} days")
    print("-" * 60)
    print("  Charts saved to:", os.path.abspath(VIZ_DIR))
    print("  Files: completion_rates.png | dept_duration.png |")
    print("         cost_by_dept.png | priority_analysis.png")
    print("=" * 60)


if __name__ == "__main__":
    main()
