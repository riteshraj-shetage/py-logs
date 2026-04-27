import numpy as np
import pandas as pd
import os

np.random.seed(42)

# ── Sales Data ──────────────────────────────────────────────────────────────
n = 500
dates = pd.date_range("2023-01-01", "2023-12-31", periods=n)
categories = ["Electronics", "Clothing", "Food", "Books", "Sports"]
regions = ["North", "South", "East", "West"]
salespeople = ["Alice", "Bob", "Carol", "David", "Eve", "Frank"]
products = {
    "Electronics": ["Laptop", "Phone", "Tablet", "Headphones", "Camera"],
    "Clothing":    ["T-Shirt", "Jeans", "Jacket", "Dress", "Shoes"],
    "Food":        ["Coffee", "Tea", "Snacks", "Organic Basket", "Spices"],
    "Books":       ["Fiction", "Non-Fiction", "Textbook", "Comic", "Cookbook"],
    "Sports":      ["Yoga Mat", "Dumbbell", "Running Shoes", "Cycle", "Racket"],
}
cat_arr = np.random.choice(categories, n)
prod_arr = [np.random.choice(products[c]) for c in cat_arr]
qty = np.random.randint(1, 20, n)
unit_price = np.round(np.random.uniform(5, 500, n), 2)
sales_df = pd.DataFrame({
    "OrderID":     [f"ORD{str(i).zfill(4)}" for i in range(1, n+1)],
    "OrderDate":   dates.strftime("%Y-%m-%d"),
    "CustomerID":  [f"CUST{np.random.randint(100, 999)}" for _ in range(n)],
    "Product":     prod_arr,
    "Category":    cat_arr,
    "Quantity":    qty,
    "UnitPrice":   unit_price,
    "Sales":       np.round(qty * unit_price, 2),
    "Region":      np.random.choice(regions, n),
    "Salesperson": np.random.choice(salespeople, n),
})
sales_df.to_csv(os.path.join(os.path.dirname(__file__), "sales_data.csv"), index=False)
print("sales_data.csv written")

# ── Marketing Data ───────────────────────────────────────────────────────────
m = 300
channels = ["Email", "Social Media", "SEO", "PPC", "Content"]
m_starts = pd.date_range("2023-01-01", "2023-10-31", periods=m)
dur = np.random.randint(7, 60, m)
impressions = np.random.randint(1000, 100000, m)
clicks = np.round(impressions * np.random.uniform(0.01, 0.15, m)).astype(int)
conversions = np.round(clicks * np.random.uniform(0.02, 0.20, m)).astype(int)
budget = np.round(np.random.uniform(500, 20000, m), 2)
revenue = np.round(conversions * np.random.uniform(20, 200, m), 2)
mkt_df = pd.DataFrame({
    "CampaignID":   [f"CAMP{str(i).zfill(4)}" for i in range(1, m+1)],
    "CampaignName": [f"Campaign_{i}" for i in range(1, m+1)],
    "Channel":      np.random.choice(channels, m),
    "Budget":       budget,
    "Clicks":       clicks,
    "Impressions":  impressions,
    "Conversions":  conversions,
    "Revenue":      revenue,
    "StartDate":    m_starts.strftime("%Y-%m-%d"),
    "EndDate":      [(m_starts[i] + pd.Timedelta(days=int(dur[i]))).strftime("%Y-%m-%d") for i in range(m)],
})
mkt_df.to_csv(os.path.join(os.path.dirname(__file__), "marketing_data.csv"), index=False)
print("marketing_data.csv written")

# ── Operations Data ──────────────────────────────────────────────────────────
p = 400
departments = ["Warehouse", "Logistics", "Customer Service", "Production", "Quality"]
statuses = ["Completed", "In Progress", "Delayed"]
priorities = ["High", "Medium", "Low"]
employees = [f"EMP{str(i).zfill(3)}" for i in range(1, 51)]
task_names = ["Inventory Check", "Shipment Processing", "Quality Audit", "Order Fulfillment",
              "Staff Training", "Equipment Maintenance", "Report Generation", "Customer Follow-up"]
op_starts = pd.date_range("2023-01-01", "2023-11-30", periods=p)
op_dur = np.random.randint(1, 30, p)
op_cost = np.round(np.random.uniform(100, 5000, p), 2)
op_df = pd.DataFrame({
    "OrderID":    [f"OPS{str(i).zfill(4)}" for i in range(1, p+1)],
    "Department": np.random.choice(departments, p),
    "TaskName":   np.random.choice(task_names, p),
    "StartDate":  op_starts.strftime("%Y-%m-%d"),
    "EndDate":    [(op_starts[i] + pd.Timedelta(days=int(op_dur[i]))).strftime("%Y-%m-%d") for i in range(p)],
    "Duration":   op_dur,
    "Cost":       op_cost,
    "Status":     np.random.choice(statuses, p, p=[0.60, 0.25, 0.15]),
    "Employee":   np.random.choice(employees, p),
    "Priority":   np.random.choice(priorities, p, p=[0.30, 0.45, 0.25]),
})
op_df.to_csv(os.path.join(os.path.dirname(__file__), "operations_data.csv"), index=False)
print("operations_data.csv written")
