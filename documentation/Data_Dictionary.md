# Northstar Home & Living - Data Dictionary

As of 12 August 2026. All records are synthetic and were generated for portfolio demonstration.

| Table | Grain | Primary key | Purpose |
| --- | --- | --- | --- |
| `dim_product` | One row per SKU | `SKU_ID` | Product hierarchy, cost, price, vendor, season and assortment attributes |
| `dim_store` | One row per location | `Store_ID` | Store geography, tier, format and capacity |
| `dim_vendor` | One row per supplier | `Vendor_ID` | Commercial terms and service performance |
| `fact_sales` | One row per transaction line | `Transaction_ID` | Units, retail, discount, net sales, cost and margin |
| `fact_inventory` | One SKU-store snapshot | `Date + Store_ID + SKU_ID` | Units received/sold/transferred, ending stock and inventory value |
| `fact_purchase_orders` | One PO line | `PO_Number` | Vendor ordering and delivery performance |
| `fact_markdowns` | One SKU-store markdown event | `Markdown_ID` | Markdown depth, inventory clearance and velocity response |

## KPI definitions

- **Net sales:** gross sales less discount.
- **Gross margin dollars:** net sales less product cost.
- **Gross margin percent:** gross margin dollars divided by net sales.
- **Sell-through:** units sold divided by units sold plus ending inventory.
- **Weeks of supply:** ending inventory divided by average weekly units sold.
- **Stock turn:** annualized cost of goods sold divided by inventory value.
- **Markdown penetration:** discount dollars divided by original retail value.
- **Sales per SKU:** category net sales divided by active SKU count.
- **GMROI:** gross margin dollars divided by average inventory investment.
