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

## Retail Business Structure

The initial business hierarchy has been implemented using three core entities:

### Retailer
Represents the retail business using BODH and acts as the ownership boundary for retail data.

### Store
Represents a physical retail location belonging to a retailer.

Relationships:
- One Retailer can own multiple Stores.
- Each Store belongs to exactly one Retailer.
- Store codes are unique within each Retailer.

### Employee
Represents personnel belonging to a retail business.

Relationships:
- Each Employee belongs to one Retailer.
- An Employee may optionally be assigned to a Store.
- Business-level employees such as owners or regional managers can exist without a specific Store assignment.

### Current Business Hierarchy

Retailer
├── Stores
└── Employees
    └── Optional Store Assignment

The implemented schema uses:
- Foreign-key constraints for ownership relationships.
- Indexes on frequently referenced foreign keys.
- Retailer-scoped uniqueness constraints.
- Created and updated timestamps.
- Active/inactive status fields.
- SQLAlchemy ORM relationships for application-level navigation.
- Alembic migrations for controlled schema evolution.