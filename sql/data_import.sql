-- SQLite CLI import guide. Run from the repository root after executing database_schema.sql.
.mode csv
.headers on
.import --skip 1 data/stores.csv dim_store
.import --skip 1 data/vendors.csv dim_vendor
-- products.csv includes two generator-only modelling columns at the end; load through
-- a staging table or select the first 20 fields in your preferred SQL client.
.import --skip 1 data/sales.csv fact_sales
.import --skip 1 data/inventory.csv fact_inventory
.import --skip 1 data/purchase_orders.csv fact_purchase_orders
.import --skip 1 data/markdowns.csv fact_markdowns
