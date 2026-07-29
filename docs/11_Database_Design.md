Table: users



Column        Type          Constraints

\-----------------------------------------

1. &#x20;      

## Database Platform

Database: PostgreSQL 18

ORM: SQLAlchemy 2.x

Migration Tool: Alembic

Current Status:
- Database connection verified successfully.
- Ready for schema creation and migrations.

## Retail MVP Domain Model

The initial BODH database focuses on retail operations for small and medium businesses.

Core entities:

- Retailer
- Store
- Employee
- Supplier
- Category
- Product
- Inventory
- Customer
- Sale
- SaleItem

Design principles:

- PostgreSQL as the primary database.
- SQLAlchemy ORM.
- Integer auto-increment primary keys.
- Common audit fields (`created_at`, `updated_at`).
- Soft deactivation using `is_active` where appropriate.
- Normalized relationships to reduce data duplication and support future AI analytics.