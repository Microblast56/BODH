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

## Inventory Management Domain

The Inventory Management domain tracks the quantity of each Product available at individual Store locations and maintains an audit history of stock changes.

The domain is intentionally separated into two concepts:

- Inventory represents the current stock state.
- StockMovement represents the historical record of changes to that stock.

This separation allows BODH to efficiently determine current stock levels while preserving the information required for auditing, analytics, and future forecasting.

### Inventory

Inventory connects a Product with a specific Store.

A Product is defined once at the Retailer level but may have different inventory quantities at different Store locations.

For example:

Product
├── Store A → 50 units
├── Store B → 18 units
└── Store C → 0 units

Each Inventory record contains:

- Store
- Product
- Quantity on hand
- Reorder level
- Reorder quantity
- Last restocked timestamp
- Created timestamp
- Updated timestamp

The combination of `store_id` and `product_id` is unique.

This guarantees that a Store has only one current Inventory record for a particular Product.

### Reorder Information

`reorder_level` represents the quantity at which stock should be considered low.

`reorder_quantity` represents the suggested amount to replenish when stock reaches the reorder level.

These fields provide the foundation for future features such as:

- Low-stock alerts
- Reorder recommendations
- Automated replenishment workflows
- Inventory forecasting

### StockMovement

StockMovement provides an audit trail of changes made to Inventory.

Inventory answers:

> How much stock exists now?

StockMovement answers:

> Why did the stock quantity change?

Each StockMovement contains:

- Inventory reference
- Optional Employee reference
- Movement type
- Quantity change
- Optional reference type
- Optional reference ID
- Notes
- Created timestamp
- Updated timestamp

### Movement Quantity

`quantity_change` is stored as a signed integer.

Positive values represent stock entering inventory.

Examples:

- Purchase: +50
- Customer return: +2
- Transfer in: +10

Negative values represent stock leaving inventory.

Examples:

- Sale: -5
- Damage: -2
- Transfer out: -8

This representation simplifies inventory calculations and historical analysis.

### Movement Types

The initial StockMovement architecture supports movement categories such as:

- PURCHASE
- SALE
- RETURN
- DAMAGE
- ADJUSTMENT
- TRANSFER_IN
- TRANSFER_OUT

Movement types are currently represented as strings so the initial system remains flexible while the business workflow is still being developed.

### Employee Attribution

A StockMovement may optionally reference an Employee.

This allows BODH to record who performed stock operations such as manual adjustments or damage reporting.

The Employee reference is optional because some future stock movements may be generated automatically by the system.

### External References

StockMovement contains optional `reference_type` and `reference_id` fields.

These allow stock movements to be associated with future business entities without tightly coupling the inventory model to those entities.

Examples include:

- Sale
- Purchase order
- Return
- Stock transfer
- Manual adjustment

For example:

`reference_type = "sale"`

`reference_id = 125`

indicates that the stock movement originated from Sale 125.

### Inventory Relationships

Store
└── Inventory
    └── StockMovement

Product
└── Inventory
    └── StockMovement

Employee
└── StockMovement

A Store may contain multiple Inventory records.

A Product may exist in multiple Store inventories.

Each Store-Product pair has exactly one current Inventory record.

Each Inventory record may have multiple StockMovement records.

### Inventory Consistency

Direct modification of inventory quantities should eventually be handled through the service layer rather than scattered throughout the application.

A stock operation should conceptually perform the following transaction:

1. Validate the requested movement.
2. Update the Inventory quantity.
3. Create the corresponding StockMovement record.
4. Commit both operations atomically.

This approach will keep current stock quantities synchronized with their historical audit trail.