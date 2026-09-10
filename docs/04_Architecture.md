\# System Architecture



BODH follows a layered monolithic architecture during its initial development.



Presentation Layer

↓



Application Layer



↓



Business Logic



↓



Machine Learning Layer



↓



Database Layer



↓



Infrastructure



The architecture is intentionally modular to allow future migration toward microservices if required.

### Database Layer

The backend uses SQLAlchemy 2.x as the ORM with PostgreSQL as the primary relational database.

The database layer is divided into:

- `core/` – application configuration and environment settings.
- `db/` – SQLAlchemy engine, session management, and declarative base.
- `models/` – ORM entities.
- `repositories/` – database access layer.
- `services/` – business logic.

This separation follows the Repository Pattern and keeps the business logic independent from persistence details.


### Retail Business Hierarchy

BODH currently models the core retail organization around the Retailer entity.

Retailer
├── Stores
└── Employees
    └── Optional Store Assignment

The Retailer acts as the primary ownership boundary for business data.

Stores belong to a Retailer, while Employees belong directly to the Retailer and may optionally be assigned to a Store.

This design supports both store-level personnel and business-level roles such as owners, administrators, and regional managers without forcing every employee into a physical store.

### Product Catalog Architecture

BODH models the product catalog at the Retailer level rather than directly at the Store level.

The core catalog entities are:

Retailer
├── Category
├── Product
└── Supplier

Products may optionally belong to Categories.

Products and Suppliers have a many-to-many relationship implemented through the ProductSupplier association model.

ProductSupplier also stores supplier-specific metadata such as purchase price, supplier product code, and preferred supplier status.

The catalog is intentionally separated from inventory.

A Product defines what an item is, while the Inventory domain will define how much of that Product exists at a particular Store.

This separation allows BODH to support multi-store retailers without duplicating product definitions for every location.

### Inventory Management Architecture

BODH separates product definitions from physical stock.

Products belong to the Retailer-level catalog, while Inventory represents the quantity of a Product available at a particular Store.

The relationship is:

Store
└── Inventory
    └── Product

The Store-Product combination is unique within Inventory.

This architecture allows a single Product definition to be shared across multiple Store locations while maintaining independent stock levels for each Store.

Inventory represents current state.

StockMovement represents historical state changes.

The relationship is:

Store
   │
   └── Inventory
          │
          ├── Product
          │
          └── StockMovement
                  │
                  └── Employee (optional)

StockMovement uses signed quantity changes so incoming and outgoing inventory operations can be represented consistently.

Stock movements may also contain generic references to future business operations such as sales, purchases, returns, and transfers.

Inventory modification business logic will be implemented in the service layer.

This ensures that updating current inventory and recording the corresponding StockMovement can eventually occur within the same database transaction, preventing inconsistencies between stock state and stock history.

Client
   │
FastAPI
   │
API Router
   │
Services
   │
Repositories
   │
SQLAlchemy ORM
   │
PostgreSQL