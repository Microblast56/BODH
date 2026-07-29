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