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