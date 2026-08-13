"""Generate Northstar Home & Living's deterministic synthetic retail dataset.

The generator creates a portfolio-sized merchandising dataset with deliberate
commercial patterns: strong lighting productivity, excess premium decor,
seasonal allocation imbalances, and varied vendor service performance.
"""

from __future__ import annotations

import csv
import json
import math
import random
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path


SEED = 260812
random.seed(SEED)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PUBLIC_DIR = ROOT / "public"
APP_DIR = ROOT / "app"
DATA_DIR.mkdir(parents=True, exist_ok=True)
PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
APP_DIR.mkdir(parents=True, exist_ok=True)

AS_OF = date(2026, 8, 12)
START_DATE = date(2025, 2, 1)
FY_START = date(2026, 1, 1)
RECENT_START = AS_OF - timedelta(days=90)


STORES = [
    ("S001", "Charlottetown Flagship", "Charlottetown", "PE", "Atlantic", "B", 0.72, 0.92),
    ("S002", "Halifax Harbour", "Halifax", "NS", "Atlantic", "A", 1.18, 1.03),
    ("S003", "Moncton Market", "Moncton", "NB", "Atlantic", "B", 0.84, 1.08),
    ("S004", "Fredericton House", "Fredericton", "NB", "Atlantic", "C", 0.66, 0.96),
    ("S005", "Dartmouth Crossing", "Dartmouth", "NS", "Atlantic", "B", 0.91, 1.00),
    ("S006", "Toronto Atelier", "Toronto", "ON", "Central", "A", 1.48, 1.06),
    ("S007", "Ottawa Collection", "Ottawa", "ON", "Central", "A", 1.14, 1.01),
    ("S008", "Mississauga Studio", "Mississauga", "ON", "Central", "A", 1.28, 1.04),
    ("S009", "London Gallery", "London", "ON", "Central", "B", 0.88, 0.98),
    ("S010", "Kingston Edit", "Kingston", "ON", "Central", "B", 0.80, 0.95),
]

CATEGORY_CONFIG = [
    ("Home Decor", "Decorative Objects", 190, 0.90, 1.36, (18, 120), "DEC"),
    ("Home Decor", "Wall Decor", 160, 0.84, 1.33, (24, 180), "WAL"),
    ("Home Decor", "Mirrors", 80, 0.70, 1.30, (55, 260), "MIR"),
    ("Home Decor", "Textiles", 120, 0.96, 1.20, (20, 110), "TEX"),
    ("Furniture", "Accent Furniture", 125, 0.62, 1.18, (90, 520), "FUR"),
    ("Furniture", "Seating", 85, 0.58, 1.12, (140, 780), "SEA"),
    ("Furniture", "Tables", 90, 0.64, 1.15, (120, 690), "TAB"),
    ("Kitchen", "Cookware", 120, 1.06, 1.02, (30, 220), "KIT"),
    ("Kitchen", "Serveware", 110, 1.02, 1.03, (18, 140), "SRV"),
    ("Kitchen", "Utensils", 70, 1.18, 0.94, (8, 65), "UTL"),
    ("Bedding", "Duvets", 80, 0.82, 1.10, (80, 280), "DUV"),
    ("Bedding", "Sheets", 100, 1.00, 1.02, (45, 190), "SHT"),
    ("Bedding", "Pillows", 80, 1.10, 0.96, (20, 120), "PIL"),
    ("Bath", "Towels", 90, 1.15, 0.92, (12, 75), "TOW"),
    ("Bath", "Bath Accessories", 70, 1.00, 1.00, (10, 90), "BTH"),
    ("Storage", "Baskets", 80, 0.82, 1.26, (16, 95), "BSK"),
    ("Storage", "Shelving", 50, 0.72, 1.28, (50, 240), "SHL"),
    ("Storage", "Organizers", 70, 0.90, 1.18, (12, 110), "ORG"),
    ("Lighting", "Table Lamps", 65, 1.72, 0.76, (45, 260), "LGT"),
    ("Lighting", "Floor Lamps", 45, 1.54, 0.80, (95, 420), "FLR"),
    ("Lighting", "Pendants", 40, 1.43, 0.84, (120, 560), "PEN"),
    ("Seasonal", "Christmas Decor", 65, 1.45, 0.92, (14, 180), "CHR"),
    ("Seasonal", "Halloween", 35, 1.05, 1.08, (10, 95), "HAL"),
    ("Seasonal", "Summer Living", 45, 1.18, 0.96, (18, 160), "SUM"),
    ("Seasonal", "Winter Comfort", 35, 1.12, 1.00, (24, 150), "WIN"),
    ("Giftware", "Candles", 70, 1.34, 0.92, (10, 85), "CND"),
    ("Giftware", "Frames", 45, 0.86, 1.14, (15, 95), "FRM"),
    ("Giftware", "Curated Gifts", 40, 1.08, 1.00, (18, 175), "GFT"),
]

VENDOR_NAMES = [
    "Maison Source Co.", "Atelier North", "Luma House", "Stone & Stem", "Cedarline Goods",
    "Aster Living", "Morrow Textiles", "Calder & Finch", "Hearthwell", "Forma Studio",
    "Meridian Craft", "Juniper Supply", "Vale & Loom", "Cove Trading", "Orchard Lane",
    "Marais Collection", "Arbor Works", "Vela Home", "Arc & Ash", "Foundry Objects",
]

ADJECTIVES = ["Arc", "Luna", "Marlow", "Avery", "Noir", "Cove", "Sable", "Vale", "Aster", "Ridge", "Mira", "Harbour"]
NOUNS = ["Collection", "Vessel", "Studio", "Edit", "Form", "Series", "House", "Line", "Object", "Atelier"]
MATERIALS = ["Ceramic", "Oak", "Linen", "Stone", "Glass", "Brass", "Cotton", "Rattan", "Wool", "Marble"]
COLOURS = ["Ivory", "Charcoal", "Sand", "Sage", "Natural", "Espresso", "Champagne", "Oat", "Slate", "Terracotta"]


def write_csv(name: str, fieldnames: list[str], rows: list[dict]) -> None:
    with (DATA_DIR / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def price_band(price: float) -> str:
    if price < 20:
        return "Entry"
    if price < 40:
        return "Good"
    if price < 70:
        return "Better"
    return "Best"


def season_for(category: str) -> str:
    if category == "Christmas Decor":
        return "Christmas"
    if category == "Halloween":
        return "Halloween"
    if category == "Summer Living":
        return "Summer"
    if category == "Winter Comfort":
        return "Winter"
    return "Core"


def seasonal_factor(category: str, dt: date) -> float:
    month = dt.month
    if category == "Christmas Decor":
        return 4.2 if month in (10, 11, 12) else 0.12
    if category == "Halloween":
        return 4.0 if month in (9, 10) else 0.10
    if category == "Summer Living":
        return 2.4 if month in (5, 6, 7, 8) else 0.38
    if category == "Winter Comfort":
        return 2.1 if month in (11, 12, 1, 2) else 0.52
    return 1.0


vendors = []
for index, name in enumerate(VENDOR_NAMES, 1):
    on_time = round(max(0.70, min(0.98, random.gauss(0.89, 0.07))), 3)
    if index in (7, 16):
        on_time = round(random.uniform(0.70, 0.78), 3)
    defect = round(max(0.004, min(0.06, random.gauss(0.022, 0.011))), 3)
    vendors.append({
        "Vendor_ID": f"V{index:03d}",
        "Vendor_Name": name,
        "Country": random.choice(["Canada", "United States", "Portugal", "India", "Vietnam", "China"]),
        "Primary_Category": CATEGORY_CONFIG[(index * 3) % len(CATEGORY_CONFIG)][1],
        "Average_Lead_Time": random.randint(14, 62),
        "Minimum_Order_Quantity": random.choice([12, 24, 36, 48, 72]),
        "Payment_Terms": random.choice(["Net 30", "Net 45", "Net 60"]),
        "On_Time_Delivery_Percentage": on_time,
        "Defect_Rate": defect,
        "Average_Cost": round(random.uniform(12, 96), 2),
        "Vendor_Status": "Review" if on_time < 0.78 or defect > 0.045 else "Active",
    })

products = []
product_lookup = {}
product_weights = []
product_index = 1
for department, category, count, demand, inventory_bias, retail_range, prefix in CATEGORY_CONFIG:
    for _ in range(count):
        retail = round(random.uniform(*retail_range) * random.choice([0.95, 0.99, 1.0, 1.05]), 2)
        margin_rate = max(0.42, min(0.68, random.gauss(0.54, 0.045)))
        cost = round(retail * (1 - margin_rate), 2)
        launch = START_DATE - timedelta(days=random.randint(20, 620))
        vendor = vendors[(product_index * 7 + random.randint(0, 4)) % len(vendors)]
        sku = f"{prefix}{product_index:04d}"
        product_name = f"{random.choice(ADJECTIVES)} {random.choice(MATERIALS)} {random.choice(NOUNS)}"
        status = random.choices(["Active", "Seasonal", "Exit"], [0.88, 0.09, 0.03])[0]
        row = {
            "SKU_ID": sku,
            "Product_Name": product_name,
            "Department": department,
            "Category": category,
            "Subcategory": category,
            "Brand": random.choice(["Northstar Collection", "Atelier Edit", "Maison Reserve", "Foundry Home"]),
            "Vendor_ID": vendor["Vendor_ID"],
            "Product_Cost": cost,
            "Original_Retail_Price": retail,
            "Current_Retail_Price": retail if status != "Exit" else round(retail * 0.7, 2),
            "Margin_Percentage": round(margin_rate, 4),
            "Launch_Date": launch.isoformat(),
            "Season": season_for(category),
            "Product_Status": status,
            "Style": random.choice(["Modern", "Organic", "Classic", "Minimal", "Artisan"]),
            "Colour": random.choice(COLOURS),
            "Size": random.choice(["Small", "Medium", "Large", "One Size"]),
            "Material": random.choice(MATERIALS),
            "Price_Band": price_band(retail),
            "Demand_Index": round(demand * random.lognormvariate(0, 0.42), 4),
            "Inventory_Bias": inventory_bias,
        }
        products.append(row)
        product_lookup[sku] = row
        product_weights.append(row["Demand_Index"])
        product_index += 1

store_rows = []
for store_id, store_name, city, province, region, tier, sales_mult, inventory_mult in STORES:
    store_rows.append({
        "Store_ID": store_id,
        "Store_Name": store_name,
        "City": city,
        "Province": province,
        "Region": region,
        "Store_Size": round(9000 + sales_mult * 10000),
        "Opening_Date": date(random.randint(2008, 2023), random.randint(1, 12), 1).isoformat(),
        "Store_Format": "Flagship" if sales_mult > 1.35 else "Gallery" if sales_mult > 1 else "Standard",
        "Sales_Tier": tier,
        "Inventory_Capacity": round(175000 + inventory_mult * 240000),
        "Sales_Multiplier": sales_mult,
        "Inventory_Multiplier": inventory_mult,
    })

sales = []
sales_by_product_store = defaultdict(lambda: {"units": 0, "sales": 0.0, "margin": 0.0, "gross": 0.0, "markdown_sales": 0.0})
sales_ytd = []
date_span = (AS_OF - START_DATE).days
for tx in range(1, 120001):
    dt = START_DATE + timedelta(days=random.randint(0, date_span))
    product = random.choices(products, weights=product_weights, k=1)[0]
    season_factor = seasonal_factor(product["Category"], dt)
    if random.random() > min(1, season_factor):
        product = random.choices(products, weights=product_weights, k=1)[0]
    store = random.choices(STORES, weights=[s[6] for s in STORES], k=1)[0]
    units = random.choices([1, 2, 3, 4, 5], weights=[58, 25, 10, 5, 2], k=1)[0]
    promo = random.random() < 0.18
    markdown = product["Product_Status"] == "Exit" or random.random() < (0.10 if product["Inventory_Bias"] > 1.2 else 0.055)
    discount_rate = random.choice([0.10, 0.15, 0.20, 0.25, 0.30, 0.40]) if markdown else (0.10 if promo else 0)
    unit_price = round(product["Current_Retail_Price"] * (1 - discount_rate), 2)
    gross_sales = round(product["Original_Retail_Price"] * units, 2)
    discount = round(gross_sales - unit_price * units, 2)
    net_sales = round(unit_price * units, 2)
    cogs = round(product["Product_Cost"] * units, 2)
    margin = round(net_sales - cogs, 2)
    row = {
        "Transaction_ID": f"TX{tx:07d}", "Date": dt.isoformat(), "Store_ID": store[0], "SKU_ID": product["SKU_ID"],
        "Units_Sold": units, "Unit_Price": unit_price, "Gross_Sales": gross_sales, "Discount": discount,
        "Net_Sales": net_sales, "Product_Cost": cogs, "Gross_Margin": margin,
        "Markdown_Flag": int(markdown), "Promotion_Flag": int(promo),
    }
    sales.append(row)
    key = (product["SKU_ID"], store[0])
    agg = sales_by_product_store[key]
    agg["units"] += units
    agg["sales"] += net_sales
    agg["margin"] += margin
    agg["gross"] += gross_sales
    if markdown:
        agg["markdown_sales"] += net_sales
    if dt >= FY_START:
        sales_ytd.append(row)

recent_units = Counter()
for row in sales:
    if row["Date"] >= RECENT_START.isoformat():
        recent_units[(row["SKU_ID"], row["Store_ID"])] += int(row["Units_Sold"])

inventory = []
inventory_map = {}
for product in products:
    for store in STORES:
        key = (product["SKU_ID"], store[0])
        weekly = recent_units[key] / 13
        if weekly == 0:
            weekly = product["Demand_Index"] * store[6] * 0.08
        target_wos = random.uniform(3.2, 6.8) * product["Inventory_Bias"] * store[7]
        if product["Category"] == "Christmas Decor" and store[2] in ("Halifax", "Toronto"):
            target_wos *= 0.50
        if product["Category"] == "Christmas Decor" and store[2] in ("Charlottetown", "Moncton"):
            target_wos *= 1.65
        ending = max(0, round(weekly * target_wos + random.gauss(0.0, 0.7)))
        units_sold = recent_units[key]
        received = max(0, ending + units_sold - random.randint(0, max(1, ending // 2 + 1)))
        beginning = max(0, ending + units_sold - received)
        row = {
            "Date": AS_OF.isoformat(), "Store_ID": store[0], "SKU_ID": product["SKU_ID"],
            "Beginning_Inventory": beginning, "Units_Received": received, "Units_Sold": units_sold,
            "Units_Transferred_In": random.randint(0, 3), "Units_Transferred_Out": random.randint(0, 3),
            "Damaged_Units": 1 if random.random() < 0.025 else 0, "Ending_Inventory": ending,
            "Inventory_Value": round(ending * product["Product_Cost"], 2),
        }
        inventory.append(row)
        inventory_map[key] = row

purchase_orders = []
for po in range(1, 6001):
    product = random.choice(products)
    vendor = next(v for v in vendors if v["Vendor_ID"] == product["Vendor_ID"])
    order_date = START_DATE + timedelta(days=random.randint(0, date_span - 35))
    expected = order_date + timedelta(days=int(vendor["Average_Lead_Time"]))
    delay = round(random.gauss(1 if vendor["On_Time_Delivery_Percentage"] > 0.86 else 7, 5))
    actual = expected + timedelta(days=delay)
    units_ordered = random.choice([24, 36, 48, 72, 96, 120])
    short = random.random() > vendor["On_Time_Delivery_Percentage"]
    units_received = max(0, units_ordered - (random.choice([6, 12, 18]) if short else 0))
    purchase_orders.append({
        "PO_Number": f"PO{po:06d}", "Vendor_ID": vendor["Vendor_ID"], "SKU_ID": product["SKU_ID"],
        "Order_Date": order_date.isoformat(), "Expected_Delivery_Date": expected.isoformat(),
        "Actual_Delivery_Date": actual.isoformat(), "Units_Ordered": units_ordered,
        "Units_Received": units_received, "Unit_Cost": product["Product_Cost"],
        "Total_Cost": round(units_ordered * product["Product_Cost"], 2),
        "Delivery_Status": "Late" if actual > expected + timedelta(days=2) else "On Time",
    })

markdowns = []
candidate_keys = sorted(inventory_map, key=lambda key: inventory_map[key]["Ending_Inventory"], reverse=True)[:3000]
for md, key in enumerate(random.sample(candidate_keys, 1200), 1):
    product = product_lookup[key[0]]
    inv = inventory_map[key]
    rate = random.choice([0.20, 0.25, 0.30, 0.40])
    before_velocity = round(max(0.4, recent_units[key] / 13 * random.uniform(0.45, 0.80)), 1)
    after_velocity = round(before_velocity * random.uniform(1.45, 2.45), 1)
    markdowns.append({
        "Markdown_ID": f"MD{md:05d}", "SKU_ID": key[0], "Store_ID": key[1],
        "Markdown_Date": (AS_OF - timedelta(days=random.randint(7, 75))).isoformat(),
        "Original_Price": product["Original_Retail_Price"],
        "Markdown_Price": round(product["Original_Retail_Price"] * (1 - rate), 2),
        "Markdown_Percentage": rate, "Inventory_Before_Markdown": inv["Ending_Inventory"] + round(after_velocity * 4),
        "Units_Sold_After_Markdown": round(after_velocity * 4),
        "Revenue_After_Markdown": round(after_velocity * 4 * product["Original_Retail_Price"] * (1 - rate), 2),
        "Velocity_Before": before_velocity, "Velocity_After": after_velocity,
    })

write_csv("products.csv", list(products[0].keys()), products)
write_csv("stores.csv", list(store_rows[0].keys()), store_rows)
write_csv("vendors.csv", list(vendors[0].keys()), vendors)
write_csv("sales.csv", list(sales[0].keys()), sales)
write_csv("inventory.csv", list(inventory[0].keys()), inventory)
write_csv("purchase_orders.csv", list(purchase_orders[0].keys()), purchase_orders)
write_csv("markdowns.csv", list(markdowns[0].keys()), markdowns)


def money(value: float) -> float:
    return round(value, 2)


category_stats = defaultdict(lambda: defaultdict(float))
store_stats = defaultdict(lambda: defaultdict(float))
sku_stats = defaultdict(lambda: defaultdict(float))
vendor_stats = defaultdict(lambda: defaultdict(float))
monthly_stats = defaultdict(float)
for row in sales_ytd:
    product = product_lookup[row["SKU_ID"]]
    cat = category_stats[product["Category"]]
    cat["sales"] += row["Net_Sales"]
    cat["gross"] += row["Gross_Sales"]
    cat["margin"] += row["Gross_Margin"]
    cat["units"] += row["Units_Sold"]
    store_stats[row["Store_ID"]]["sales"] += row["Net_Sales"]
    store_stats[row["Store_ID"]]["units"] += row["Units_Sold"]
    sku = sku_stats[row["SKU_ID"]]
    sku["sales"] += row["Net_Sales"]
    sku["gross"] += row["Gross_Sales"]
    sku["margin"] += row["Gross_Margin"]
    sku["units"] += row["Units_Sold"]
    vendor = vendor_stats[product["Vendor_ID"]]
    vendor["sales"] += row["Net_Sales"]
    vendor["margin"] += row["Gross_Margin"]
    vendor["units"] += row["Units_Sold"]
    monthly_stats[row["Date"][:7]] += row["Net_Sales"]

for row in inventory:
    product = product_lookup[row["SKU_ID"]]
    category_stats[product["Category"]]["inventory"] += row["Inventory_Value"]
    category_stats[product["Category"]]["inventory_units"] += row["Ending_Inventory"]
    store_stats[row["Store_ID"]]["inventory"] += row["Inventory_Value"]
    store_stats[row["Store_ID"]]["inventory_units"] += row["Ending_Inventory"]
    sku_stats[row["SKU_ID"]]["inventory"] += row["Inventory_Value"]
    sku_stats[row["SKU_ID"]]["inventory_units"] += row["Ending_Inventory"]
    vendor_stats[product["Vendor_ID"]]["inventory"] += row["Inventory_Value"]
    vendor_stats[product["Vendor_ID"]]["inventory_units"] += row["Ending_Inventory"]

total_sales = sum(row["Net_Sales"] for row in sales_ytd)
total_gross = sum(row["Gross_Sales"] for row in sales_ytd)
total_margin = sum(row["Gross_Margin"] for row in sales_ytd)
total_units = sum(row["Units_Sold"] for row in sales_ytd)
total_inventory = sum(row["Inventory_Value"] for row in inventory)
total_inventory_units = sum(row["Ending_Inventory"] for row in inventory)
recent_total_units = sum(recent_units.values())
weeks_elapsed = max(1, (AS_OF - FY_START).days / 7)

category_sku_counts = Counter(p["Category"] for p in products)
category_data = []
for category, stats in category_stats.items():
    available = stats["units"] + stats["inventory_units"]
    category_data.append({
        "name": category, "sales": money(stats["sales"]), "margin": round(stats["margin"] / stats["sales"], 4),
        "sellThrough": round(stats["units"] / available, 4) if available else 0,
        "inventory": money(stats["inventory"]), "salesShare": round(stats["sales"] / total_sales, 4),
        "inventoryShare": round(stats["inventory"] / total_inventory, 4),
        "salesPerSku": money(stats["sales"] / category_sku_counts[category]), "skuCount": category_sku_counts[category],
    })
category_data.sort(key=lambda item: item["sales"], reverse=True)

store_lookup = {s[0]: s for s in STORES}
store_data = []
for store_id, stats in store_stats.items():
    weekly = stats["units"] / weeks_elapsed
    store = store_lookup[store_id]
    store_data.append({
        "id": store_id, "name": store[2], "fullName": store[1], "region": store[4], "tier": store[5],
        "sales": money(stats["sales"]), "inventory": money(stats["inventory"]),
        "wos": round(stats["inventory_units"] / weekly, 1) if weekly else 0,
    })
store_data.sort(key=lambda item: item["sales"], reverse=True)


def sku_action(stats: dict) -> tuple[str, float, float]:
    weekly = stats["units"] / weeks_elapsed
    wos = stats["inventory_units"] / weekly if weekly else 99
    sell_through = stats["units"] / (stats["units"] + stats["inventory_units"]) if stats["units"] + stats["inventory_units"] else 0
    if sell_through < 0.22:
        action = "EXIT"
    elif sell_through > 0.72 and wos < 3.0:
        action = "REORDER"
    elif sell_through < 0.34 and wos > 8.0:
        action = "MARKDOWN"
    elif sell_through < 0.46 and wos > 6.5:
        action = "TRANSFER"
    else:
        action = "MAINTAIN"
    return action, sell_through, wos

sku_data_all = []
action_counts = Counter()
for sku_id, stats in sku_stats.items():
    product = product_lookup[sku_id]
    action, sell_through, wos = sku_action(stats)
    action_counts[action] += 1
    sku_data_all.append({
        "sku": sku_id, "product": product["Product_Name"], "category": product["Category"],
        "sales": money(stats["sales"]), "margin": round(stats["margin"] / stats["sales"], 4) if stats["sales"] else 0,
        "sellThrough": round(sell_through, 4), "wos": round(wos, 1), "inventory": money(stats["inventory"]),
        "action": action, "priceBand": product["Price_Band"],
    })

action_priority = {"REORDER": 5, "MARKDOWN": 4, "TRANSFER": 3, "EXIT": 2, "MAINTAIN": 1}
sku_data = sorted(sku_data_all, key=lambda item: (action_priority[item["action"]], item["sales"]), reverse=True)[:100]

vendor_lookup = {v["Vendor_ID"]: v for v in vendors}
vendor_data = []
for vendor_id, stats in vendor_stats.items():
    vendor = vendor_lookup[vendor_id]
    sell_through = stats["units"] / (stats["units"] + stats["inventory_units"]) if stats["units"] + stats["inventory_units"] else 0
    margin_rate = stats["margin"] / stats["sales"] if stats["sales"] else 0
    score = round(100 * (0.30 * min(1, margin_rate / 0.56) + 0.30 * min(1, sell_through / 0.66) + 0.30 * vendor["On_Time_Delivery_Percentage"] + 0.10 * (1 - vendor["Defect_Rate"] / 0.08)))
    vendor_data.append({
        "id": vendor_id, "name": vendor["Vendor_Name"], "sales": money(stats["sales"]),
        "margin": round(margin_rate, 4), "sellThrough": round(sell_through, 4),
        "onTime": vendor["On_Time_Delivery_Percentage"], "leadTime": vendor["Average_Lead_Time"],
        "defectRate": vendor["Defect_Rate"], "score": max(0, min(100, score)),
    })
vendor_data.sort(key=lambda item: item["score"], reverse=True)

monthly = []
for month_key in sorted(monthly_stats):
    actual = monthly_stats[month_key]
    phase = int(month_key[-2:])
    plan_bias = 0.96 if phase in (4, 5, 6) else 1.02
    monthly.append({"month": month_key, "actual": money(actual), "plan": money(actual / plan_bias)})

price_band_stats = defaultdict(lambda: defaultdict(float))
for item in sku_data_all:
    band = price_band_stats[item["priceBand"]]
    band["sales"] += item["sales"]
    band["inventory"] += item["inventory"]
    band["units"] += sku_stats[item["sku"]]["units"]
    band["inventory_units"] += sku_stats[item["sku"]]["inventory_units"]
price_bands = []
for band in ["Entry", "Good", "Better", "Best"]:
    stats = price_band_stats[band]
    available = stats["units"] + stats["inventory_units"]
    price_bands.append({
        "name": band, "sales": money(stats["sales"]), "inventory": money(stats["inventory"]),
        "sellThrough": round(stats["units"] / available, 4) if available else 0,
    })

transfer_candidates = []
by_sku_store = defaultdict(list)
for key, inv in inventory_map.items():
    weekly = recent_units[key] / 13
    wos = inv["Ending_Inventory"] / weekly if weekly else 99
    by_sku_store[key[0]].append((key[1], wos, inv["Ending_Inventory"], weekly))
for sku_id, positions in by_sku_store.items():
    donor = max(positions, key=lambda x: x[1])
    receiver = min(positions, key=lambda x: x[1])
    if donor[1] > 6.0 and receiver[1] < max(5.0, donor[1] * 0.55) and donor[2] > 4 and receiver[3] > 0:
        qty = min(max(6, round(receiver[3] * 4 - receiver[2])), max(6, round(donor[2] * 0.4)))
        if qty > 0:
            transfer_candidates.append({
                "sku": sku_id, "product": product_lookup[sku_id]["Product_Name"],
                "from": store_lookup[donor[0]][2], "to": store_lookup[receiver[0]][2],
                "units": qty, "fromWos": round(donor[1], 1), "toWos": round(receiver[1], 1),
            })
transfer_candidates = sorted(transfer_candidates, key=lambda x: x["units"], reverse=True)[:12]
if len(transfer_candidates) < 8:
    used = {item["sku"] for item in transfer_candidates}
    modeled = [item for item in sku_data_all if item["action"] == "TRANSFER" and item["sku"] not in used]
    donor_cities = ["Charlottetown", "Moncton", "London", "Kingston"]
    receiver_cities = ["Halifax", "Toronto", "Ottawa", "Mississauga"]
    for index, item in enumerate(modeled[: 8 - len(transfer_candidates)]):
        transfer_candidates.append({
            "sku": item["sku"], "product": item["product"],
            "from": donor_cities[index % len(donor_cities)], "to": receiver_cities[index % len(receiver_cities)],
            "units": 8 + (index % 4) * 4, "fromWos": round(8.8 + index * 0.6, 1), "toWos": round(0.9 + index * 0.2, 1),
        })

seasonal = []
for label, category in [("Christmas Decor", "Christmas Decor"), ("Giftware", "Curated Gifts"), ("Summer Living", "Summer Living"), ("Halloween", "Halloween"), ("Winter Comfort", "Winter Comfort")]:
    actual = category_stats[category]["sales"]
    variance = {"Christmas Decor": 0.183, "Giftware": 0.092, "Summer Living": 0.071, "Halloween": -0.058, "Winter Comfort": -0.137}[label]
    seasonal.append({"name": label, "actual": money(actual), "plan": money(actual / (1 + variance)), "variance": variance})

markdown_velocity_before = sum(m["Velocity_Before"] for m in markdowns) / len(markdowns)
markdown_velocity_after = sum(m["Velocity_After"] for m in markdowns) / len(markdowns)

summary = {
    "meta": {"brand": "Northstar Home & Living", "asOf": AS_OF.isoformat(), "fiscalPeriod": "FY2026 · Week 32", "stores": 10, "skus": len(products), "transactions": len(sales)},
    "kpis": {
        "netSales": money(total_sales), "salesVsPlan": 0.042, "grossMargin": round(total_margin / total_sales, 4),
        "sellThrough": round(recent_total_units / (recent_total_units + total_inventory_units), 4), "inventoryValue": money(total_inventory),
        "weeksOfSupply": round(total_inventory_units / (recent_total_units / 13), 1),
        "markdownPenetration": round((total_gross - total_sales) / total_gross, 4),
        "stockTurn": round((total_units / weeks_elapsed * 52 * (sum(p["Product_Cost"] for p in products) / len(products))) / total_inventory, 1),
    },
    "monthlyTrend": monthly,
    "categories": category_data,
    "stores": store_data,
    "skus": sku_data,
    "actionCounts": dict(action_counts),
    "vendors": vendor_data,
    "priceBands": price_bands,
    "transfers": transfer_candidates,
    "seasonal": seasonal,
    "markdown": {
        "beforeVelocity": round(markdown_velocity_before, 1), "afterVelocity": round(markdown_velocity_after, 1),
        "velocityLift": round(markdown_velocity_after / markdown_velocity_before - 1, 4),
        "inventoryCleared": sum(m["Units_Sold_After_Markdown"] for m in markdowns),
    },
}

with (PUBLIC_DIR / "dashboard-data.json").open("w", encoding="utf-8") as handle:
    json.dump(summary, handle, indent=2)

with (APP_DIR / "dashboard-data.json").open("w", encoding="utf-8") as handle:
    json.dump(summary, handle, indent=2)

with (DATA_DIR / "dataset_manifest.json").open("w", encoding="utf-8") as handle:
    json.dump({
        "seed": SEED, "as_of": AS_OF.isoformat(),
        "tables": {"products": len(products), "stores": len(store_rows), "vendors": len(vendors), "sales": len(sales), "inventory": len(inventory), "purchase_orders": len(purchase_orders), "markdowns": len(markdowns)},
    }, handle, indent=2)

print(json.dumps({"status": "generated", "sales_records": len(sales), "products": len(products), "net_sales_ytd": round(total_sales, 2), "inventory_value": round(total_inventory, 2)}, indent=2))
