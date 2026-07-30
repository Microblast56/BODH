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