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

## Product Catalog Domain

The Product Catalog domain provides the foundation for managing products, categories, and suppliers within each retail business.

### Category

Categories allow retailers to organize their product catalog.

Key characteristics:

- Each Category belongs to one Retailer.
- Category names are unique within a Retailer.
- Categories may contain multiple Products.
- Products are allowed to exist without a Category.

### Product

Products represent the items managed and eventually sold by a Retailer.

Each Product belongs directly to a Retailer.

A Product may optionally belong to a Category.

Important product attributes include:

- Name
- SKU
- Barcode
- Description
- Cost price
- Selling price
- Unit
- Tax rate
- Active status

SKU values are unique within each Retailer.

Financial values such as cost price and selling price use fixed-precision decimal database types rather than floating-point values.

### Supplier

Suppliers represent organizations or individuals from whom a Retailer can obtain products.

Each Supplier belongs to one Retailer.

Supplier information may include:

- Name
- Contact person
- Email
- Phone
- Address

Supplier names are unique within each Retailer.

### ProductSupplier

Products and Suppliers use a many-to-many relationship through the ProductSupplier association model.

This allows:

- One Product to be available from multiple Suppliers.
- One Supplier to provide multiple Products.

The association also stores supplier-specific information:

- Supplier product code
- Purchase price
- Preferred supplier status

Each Product-Supplier pair is unique.

### Product Catalog Relationships

Retailer
├── Categories
│   └── Products
├── Products
│   └── ProductSupplier
│       └── Supplier
└── Suppliers

The Product Catalog intentionally separates product definition from store-level inventory.

Products belong to the Retailer, while inventory quantities will later be maintained independently for each Store.

This allows the same Product to exist across multiple Stores while maintaining different stock levels at each location.