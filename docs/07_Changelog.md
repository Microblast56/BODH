\# Changelog



\## v0.1.0



\- Project initialized

\- PostgreSQL installed

\- Documentation created

\- Folder structure established

\- Product renamed to BODH

### Database Configuration Layer
- Implemented centralized application configuration using Pydantic Settings.
- Added SQLAlchemy engine and session management.
- Established a successful connection between BODH and PostgreSQL.
- Verified database connectivity using a dedicated connection test.


### Retail Business Structure
- Added Store ORM model and Retailer-Store relationship.
- Added Employee ORM model.
- Added Retailer-Employee and Store-Employee relationships.
- Added retailer-scoped uniqueness constraints for store codes and employee emails.
- Added indexed foreign keys for retail ownership relationships.
- Created and successfully applied Store and Employee Alembic migrations.
- Established Retailer → Store → Employee as the initial retail business hierarchy.

### Product Catalog Foundation

- Added Category ORM model.
- Added Product ORM model.
- Added Supplier ORM model.
- Added ProductSupplier association model.
- Added Retailer-Category relationship.
- Added Retailer-Product relationship.
- Added Retailer-Supplier relationship.
- Added optional Category-Product relationship.
- Added many-to-many Product-Supplier architecture.
- Added retailer-scoped Category name uniqueness.
- Added retailer-scoped Product SKU uniqueness.
- Added retailer-scoped Supplier name uniqueness.
- Added supplier-specific purchase price and product code support.
- Added preferred supplier support.
- Added fixed-precision decimal storage for product pricing and tax rates.
- Added and successfully applied Category/Product Alembic migration.
- Added and successfully applied Supplier/ProductSupplier Alembic migration.
- Database migration head advanced to fef5ff6db301.