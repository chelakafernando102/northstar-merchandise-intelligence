-- Northstar Home & Living - decision-oriented merchandising analysis portfolio

-- 01. Top 20 products by net sales
SELECT p.sku_id, p.product_name, p.category, ROUND(SUM(s.net_sales), 2) AS net_sales
FROM fact_sales s JOIN dim_product p ON p.sku_id = s.sku_id
GROUP BY p.sku_id, p.product_name, p.category ORDER BY net_sales DESC LIMIT 20;

-- 02. Highest gross-margin SKUs with a minimum sales threshold
SELECT p.sku_id, p.product_name, ROUND(SUM(s.gross_margin), 2) AS margin_dollars,
       ROUND(SUM(s.gross_margin) / NULLIF(SUM(s.net_sales), 0), 4) AS margin_rate
FROM fact_sales s JOIN dim_product p ON p.sku_id = s.sku_id
GROUP BY p.sku_id, p.product_name HAVING SUM(s.net_sales) >= 5000
ORDER BY margin_dollars DESC LIMIT 20;

-- 03. Lowest sell-through products
WITH sold AS (SELECT sku_id, SUM(units_sold) units FROM fact_sales GROUP BY sku_id),
stock AS (SELECT sku_id, SUM(ending_inventory) inventory FROM fact_inventory GROUP BY sku_id)
SELECT p.sku_id, p.product_name, p.category, sold.units, stock.inventory,
       ROUND(1.0 * sold.units / NULLIF(sold.units + stock.inventory, 0), 4) AS sell_through
FROM dim_product p JOIN sold USING (sku_id) JOIN stock USING (sku_id)
ORDER BY sell_through ASC LIMIT 30;

-- 04. Products with more than eight weeks of supply
WITH velocity AS (
  SELECT sku_id, SUM(units_sold) / 13.0 AS avg_weekly_units
  FROM fact_sales WHERE sale_date >= DATE((SELECT MAX(sale_date) FROM fact_sales), '-90 day') GROUP BY sku_id
), stock AS (SELECT sku_id, SUM(ending_inventory) inventory FROM fact_inventory GROUP BY sku_id)
SELECT p.sku_id, p.product_name, p.category, stock.inventory,
       ROUND(stock.inventory / NULLIF(velocity.avg_weekly_units, 0), 1) AS weeks_of_supply
FROM dim_product p JOIN velocity USING (sku_id) JOIN stock USING (sku_id)
WHERE stock.inventory / NULLIF(velocity.avg_weekly_units, 0) > 8
ORDER BY weeks_of_supply DESC;

-- 05. Category sales contribution
SELECT p.department, p.category, ROUND(SUM(s.net_sales), 2) net_sales,
       ROUND(SUM(s.net_sales) / SUM(SUM(s.net_sales)) OVER (), 4) sales_share
FROM fact_sales s JOIN dim_product p USING (sku_id)
GROUP BY p.department, p.category ORDER BY net_sales DESC;

-- 06. Store inventory imbalance by category
SELECT p.category, st.city, ROUND(SUM(i.inventory_value), 2) inventory_value,
       ROUND(SUM(i.inventory_value) / SUM(SUM(i.inventory_value)) OVER (PARTITION BY p.category), 4) category_inventory_share
FROM fact_inventory i JOIN dim_product p USING (sku_id) JOIN dim_store st USING (store_id)
GROUP BY p.category, st.city ORDER BY p.category, inventory_value DESC;

-- 07. Products approaching stock-out before replenishment
WITH velocity AS (
  SELECT store_id, sku_id, SUM(units_sold) / 13.0 weekly_units
  FROM fact_sales WHERE sale_date >= DATE((SELECT MAX(sale_date) FROM fact_sales), '-90 day')
  GROUP BY store_id, sku_id
)
SELECT st.city, p.sku_id, p.product_name, i.ending_inventory, v.weekly_units,
       ROUND(i.ending_inventory / NULLIF(v.weekly_units, 0), 1) weeks_of_supply,
       ven.average_lead_time
FROM fact_inventory i JOIN velocity v USING (store_id, sku_id)
JOIN dim_product p USING (sku_id) JOIN dim_store st USING (store_id)
JOIN dim_vendor ven ON ven.vendor_id = p.vendor_id
WHERE i.ending_inventory / NULLIF(v.weekly_units, 0) < ven.average_lead_time / 7.0
ORDER BY weeks_of_supply;

-- 08. Vendor commercial and operational scorecard
SELECT v.vendor_id, v.vendor_name, ROUND(SUM(s.net_sales), 2) sales,
       ROUND(SUM(s.gross_margin) / NULLIF(SUM(s.net_sales), 0), 4) margin_rate,
       v.on_time_delivery_percentage, v.average_lead_time, v.defect_rate
FROM dim_vendor v JOIN dim_product p USING (vendor_id) JOIN fact_sales s USING (sku_id)
GROUP BY v.vendor_id, v.vendor_name, v.on_time_delivery_percentage, v.average_lead_time, v.defect_rate
ORDER BY sales DESC;

-- 09. Monthly sales trend with month-over-month variance
WITH monthly AS (
  SELECT SUBSTR(sale_date, 1, 7) month, SUM(net_sales) net_sales FROM fact_sales GROUP BY month
)
SELECT month, ROUND(net_sales, 2) net_sales,
       ROUND(net_sales - LAG(net_sales) OVER (ORDER BY month), 2) variance_dollars,
       ROUND(net_sales / NULLIF(LAG(net_sales) OVER (ORDER BY month), 0) - 1, 4) variance_rate
FROM monthly ORDER BY month;

-- 10. Markdown effectiveness
SELECT ROUND(markdown_percentage, 2) markdown_depth,
       ROUND(AVG(velocity_before), 1) velocity_before,
       ROUND(AVG(velocity_after), 1) velocity_after,
       ROUND(AVG(velocity_after / NULLIF(velocity_before, 0) - 1), 4) velocity_lift,
       ROUND(SUM(revenue_after_markdown), 2) post_markdown_revenue
FROM fact_markdowns GROUP BY ROUND(markdown_percentage, 2) ORDER BY markdown_depth;

-- 11. ABC revenue classification
WITH revenue AS (
  SELECT sku_id, SUM(net_sales) sales FROM fact_sales GROUP BY sku_id
), ranked AS (
  SELECT *, SUM(sales) OVER (ORDER BY sales DESC) / SUM(sales) OVER () cumulative_share FROM revenue
)
SELECT p.sku_id, p.product_name, ROUND(r.sales, 2) sales,
       CASE WHEN cumulative_share <= 0.80 THEN 'A' WHEN cumulative_share <= 0.95 THEN 'B' ELSE 'C' END abc_class
FROM ranked r JOIN dim_product p USING (sku_id) ORDER BY sales DESC;

-- 12. Price-band performance
SELECT p.price_band, ROUND(SUM(s.net_sales), 2) sales, SUM(s.units_sold) units,
       ROUND(SUM(s.gross_margin) / NULLIF(SUM(s.net_sales), 0), 4) margin_rate
FROM fact_sales s JOIN dim_product p USING (sku_id)
GROUP BY p.price_band ORDER BY CASE p.price_band WHEN 'Entry' THEN 1 WHEN 'Good' THEN 2 WHEN 'Better' THEN 3 ELSE 4 END;

-- 13. Seasonal sales performance by category
SELECT p.season, p.category, ROUND(SUM(s.net_sales), 2) sales,
       ROUND(SUM(s.gross_margin) / NULLIF(SUM(s.net_sales), 0), 4) margin_rate
FROM fact_sales s JOIN dim_product p USING (sku_id)
WHERE p.season <> 'Core' GROUP BY p.season, p.category ORDER BY sales DESC;

-- 14. Slow-moving inventory exposure
WITH recent AS (
  SELECT sku_id, SUM(units_sold) / 13.0 weekly_units
  FROM fact_sales WHERE sale_date >= DATE((SELECT MAX(sale_date) FROM fact_sales), '-90 day') GROUP BY sku_id
), stock AS (
  SELECT sku_id, SUM(ending_inventory) units, SUM(inventory_value) value FROM fact_inventory GROUP BY sku_id
)
SELECT p.sku_id, p.product_name, p.category, ROUND(stock.value, 2) inventory_value,
       ROUND(stock.units / NULLIF(recent.weekly_units, 0), 1) weeks_of_supply
FROM stock JOIN recent USING (sku_id) JOIN dim_product p USING (sku_id)
WHERE stock.units / NULLIF(recent.weekly_units, 0) > 10 ORDER BY inventory_value DESC;

-- 15. Store-to-store transfer opportunities
WITH velocity AS (
  SELECT store_id, sku_id, SUM(units_sold) / 13.0 weekly_units
  FROM fact_sales WHERE sale_date >= DATE((SELECT MAX(sale_date) FROM fact_sales), '-90 day') GROUP BY store_id, sku_id
), position AS (
  SELECT i.store_id, i.sku_id, i.ending_inventory, v.weekly_units,
         i.ending_inventory / NULLIF(v.weekly_units, 0) wos
  FROM fact_inventory i JOIN velocity v USING (store_id, sku_id)
), paired AS (
  SELECT d.sku_id, d.store_id donor_store, r.store_id receiver_store, d.wos donor_wos, r.wos receiver_wos,
         CAST(MIN(d.ending_inventory * 0.4, r.weekly_units * 4 - r.ending_inventory) AS INTEGER) transfer_units
  FROM position d JOIN position r ON r.sku_id = d.sku_id AND r.store_id <> d.store_id
  WHERE d.wos > 9 AND r.wos < 2.5
)
SELECT p.sku_id, p.product_name, ds.city donor, rs.city receiver, donor_wos, receiver_wos, transfer_units
FROM paired JOIN dim_product p USING (sku_id)
JOIN dim_store ds ON ds.store_id = donor_store JOIN dim_store rs ON rs.store_id = receiver_store
WHERE transfer_units > 0 ORDER BY transfer_units DESC;

-- 16. Plan-vs-actual proxy using monthly budget phasing
WITH actual AS (
  SELECT SUBSTR(sale_date, 1, 7) month, SUM(net_sales) actual_sales FROM fact_sales GROUP BY month
), plan AS (
  SELECT month, actual_sales / CASE WHEN CAST(SUBSTR(month, 6, 2) AS INTEGER) BETWEEN 4 AND 6 THEN 1.04 ELSE 0.98 END planned_sales
  FROM actual
)
SELECT a.month, ROUND(a.actual_sales, 2) actual_sales, ROUND(p.planned_sales, 2) planned_sales,
       ROUND(a.actual_sales - p.planned_sales, 2) variance_dollars,
       ROUND(a.actual_sales / NULLIF(p.planned_sales, 0) - 1, 4) variance_rate
FROM actual a JOIN plan p USING (month) ORDER BY a.month;

-- 17. Purchase-order delivery reliability
SELECT v.vendor_name, COUNT(*) purchase_orders,
       ROUND(AVG(CASE WHEN po.delivery_status = 'On Time' THEN 1.0 ELSE 0 END), 4) actual_on_time_rate,
       ROUND(AVG(JULIANDAY(po.actual_delivery_date) - JULIANDAY(po.expected_delivery_date)), 1) avg_days_variance
FROM fact_purchase_orders po JOIN dim_vendor v USING (vendor_id)
GROUP BY v.vendor_name ORDER BY actual_on_time_rate DESC;

-- 18. Action intelligence classification
WITH performance AS (
  SELECT p.sku_id, p.product_name, SUM(s.units_sold) units_sold, SUM(s.net_sales) sales,
         SUM(i.ending_inventory) inventory_units,
         1.0 * SUM(s.units_sold) / NULLIF(SUM(s.units_sold) + SUM(i.ending_inventory), 0) sell_through
  FROM dim_product p JOIN fact_sales s USING (sku_id) JOIN fact_inventory i USING (sku_id)
  GROUP BY p.sku_id, p.product_name
)
SELECT *, CASE
  WHEN sell_through > 0.70 AND inventory_units < units_sold * 0.15 THEN 'REORDER'
  WHEN sell_through < 0.30 AND inventory_units > units_sold * 0.45 THEN 'MARKDOWN'
  WHEN sell_through < 0.45 AND inventory_units > units_sold * 0.30 THEN 'TRANSFER'
  WHEN sell_through < 0.25 THEN 'EXIT'
  ELSE 'MAINTAIN' END recommended_action
FROM performance ORDER BY sales DESC;
