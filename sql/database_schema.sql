-- Northstar Home & Living - retail merchandising star schema (SQLite)
PRAGMA foreign_keys = ON;

CREATE TABLE dim_store (
  store_id TEXT PRIMARY KEY,
  store_name TEXT NOT NULL,
  city TEXT NOT NULL,
  province TEXT NOT NULL,
  region TEXT NOT NULL,
  store_size INTEGER,
  opening_date DATE,
  store_format TEXT,
  sales_tier TEXT,
  inventory_capacity NUMERIC
);

CREATE TABLE dim_vendor (
  vendor_id TEXT PRIMARY KEY,
  vendor_name TEXT NOT NULL,
  country TEXT,
  primary_category TEXT,
  average_lead_time INTEGER,
  minimum_order_quantity INTEGER,
  payment_terms TEXT,
  on_time_delivery_percentage NUMERIC,
  defect_rate NUMERIC,
  average_cost NUMERIC,
  vendor_status TEXT
);

CREATE TABLE dim_product (
  sku_id TEXT PRIMARY KEY,
  product_name TEXT NOT NULL,
  department TEXT NOT NULL,
  category TEXT NOT NULL,
  subcategory TEXT,
  brand TEXT,
  vendor_id TEXT NOT NULL REFERENCES dim_vendor(vendor_id),
  product_cost NUMERIC NOT NULL,
  original_retail_price NUMERIC NOT NULL,
  current_retail_price NUMERIC NOT NULL,
  margin_percentage NUMERIC,
  launch_date DATE,
  season TEXT,
  product_status TEXT,
  style TEXT,
  colour TEXT,
  size TEXT,
  material TEXT,
  price_band TEXT
);

CREATE TABLE fact_sales (
  transaction_id TEXT PRIMARY KEY,
  sale_date DATE NOT NULL,
  store_id TEXT NOT NULL REFERENCES dim_store(store_id),
  sku_id TEXT NOT NULL REFERENCES dim_product(sku_id),
  units_sold INTEGER NOT NULL,
  unit_price NUMERIC NOT NULL,
  gross_sales NUMERIC NOT NULL,
  discount NUMERIC NOT NULL,
  net_sales NUMERIC NOT NULL,
  product_cost NUMERIC NOT NULL,
  gross_margin NUMERIC NOT NULL,
  markdown_flag INTEGER NOT NULL,
  promotion_flag INTEGER NOT NULL
);

CREATE TABLE fact_inventory (
  inventory_date DATE NOT NULL,
  store_id TEXT NOT NULL REFERENCES dim_store(store_id),
  sku_id TEXT NOT NULL REFERENCES dim_product(sku_id),
  beginning_inventory INTEGER,
  units_received INTEGER,
  units_sold INTEGER,
  units_transferred_in INTEGER,
  units_transferred_out INTEGER,
  damaged_units INTEGER,
  ending_inventory INTEGER,
  inventory_value NUMERIC,
  PRIMARY KEY (inventory_date, store_id, sku_id)
);

CREATE TABLE fact_purchase_orders (
  po_number TEXT PRIMARY KEY,
  vendor_id TEXT NOT NULL REFERENCES dim_vendor(vendor_id),
  sku_id TEXT NOT NULL REFERENCES dim_product(sku_id),
  order_date DATE,
  expected_delivery_date DATE,
  actual_delivery_date DATE,
  units_ordered INTEGER,
  units_received INTEGER,
  unit_cost NUMERIC,
  total_cost NUMERIC,
  delivery_status TEXT
);

CREATE TABLE fact_markdowns (
  markdown_id TEXT PRIMARY KEY,
  sku_id TEXT NOT NULL REFERENCES dim_product(sku_id),
  store_id TEXT NOT NULL REFERENCES dim_store(store_id),
  markdown_date DATE,
  original_price NUMERIC,
  markdown_price NUMERIC,
  markdown_percentage NUMERIC,
  inventory_before_markdown INTEGER,
  units_sold_after_markdown INTEGER,
  revenue_after_markdown NUMERIC,
  velocity_before NUMERIC,
  velocity_after NUMERIC
);

CREATE INDEX idx_sales_date ON fact_sales(sale_date);
CREATE INDEX idx_sales_store_sku ON fact_sales(store_id, sku_id);
CREATE INDEX idx_inventory_store_sku ON fact_inventory(store_id, sku_id);
CREATE INDEX idx_product_category ON dim_product(department, category);
