"""Validate the generated Northstar CSV files and report quality checks."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

required = {
    "products.csv": {"SKU_ID", "Category", "Product_Cost", "Current_Retail_Price"},
    "stores.csv": {"Store_ID", "City", "Region"},
    "vendors.csv": {"Vendor_ID", "Vendor_Name", "On_Time_Delivery_Percentage"},
    "sales.csv": {"Transaction_ID", "Date", "Store_ID", "SKU_ID", "Net_Sales"},
    "inventory.csv": {"Date", "Store_ID", "SKU_ID", "Ending_Inventory", "Inventory_Value"},
    "purchase_orders.csv": {"PO_Number", "Vendor_ID", "SKU_ID", "Delivery_Status"},
    "markdowns.csv": {"Markdown_ID", "SKU_ID", "Store_ID", "Markdown_Percentage"},
}

results = {}
for filename, fields in required.items():
    with (DATA / filename).open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = sorted(fields - set(reader.fieldnames or []))
        rows = 0
        blank_keys = 0
        first_field = next(iter(fields))
        for row in reader:
            rows += 1
            blank_keys += int(not row.get(first_field))
    results[filename] = {"rows": rows, "missing_fields": missing, "blank_keys": blank_keys, "status": "PASS" if not missing and not blank_keys else "FAIL"}

overall = "PASS" if all(item["status"] == "PASS" for item in results.values()) else "FAIL"
print(json.dumps({"model_status": overall, "files": results}, indent=2))
raise SystemExit(0 if overall == "PASS" else 1)
