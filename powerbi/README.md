# Power BI implementation pack

The hosted dashboard is the fully implemented interactive portfolio experience. This folder contains the assets required to reproduce the same six-page report in Power BI Desktop:

- `Northstar_Noir_Champagne.json` - report theme.
- `measures.dax` - core merchandising measures and action logic.
- CSV source tables are in `../data/`.
- The relationship design is documented in `../documentation/Data_Dictionary.pdf` and `../sql/database_schema.sql`.

Recommended report pages:

1. Merchandising Executive Overview
2. Category & Assortment Performance
3. SKU Performance
4. Inventory & Allocation
5. Markdown & Seasonal Performance
6. Vendor Performance

No `.pbix` binary is committed because it is a proprietary desktop artifact that cannot be generated or audited in this environment. The theme, measures, model documentation, source tables, and completed web implementation make the report reproducible in Power BI Desktop.
