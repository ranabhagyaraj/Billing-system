# SubLedger - Low Level Design (LLD)

## Architecture Overview
SubLedger is built using a clean layered architecture with clear separation of concerns:
- **Routes (`app/routes/`)**: Handle HTTP requests and responses, dependency injection of DB sessions.
- **Services (`app/services/`)**: Enforces core business logic and transactional workflows (Invoice generation, Payment reconciliation).
- **Repositories (`app/repositories/`)**: Abstracts database operations and queries away from business logic.
- **Models (`app/models/`)**: SQLAlchemy ORM models representing the database schema.
- **Schemas (`app/schemas/`)**: Pydantic models for request validation and serialization.

## Domain Relationships
- **Customer** has many Subscriptions and LedgerEntries.
- **Plan** has many Subscriptions.
- **Subscription** has many Invoices.
- **Invoice** has many PaymentAttempts and LedgerEntries.

## Key Business Rules Implemented
1. Plan prices must be strictly greater than 0.
2. Customer email addresses are unique.
3. Subscriptions cannot be created against inactive plans.
4. Duplicate active subscriptions for the same customer and plan are prevented.
5. Invoices capture the plan price snapshot at time of generation.
6. Payments cannot exceed the remaining unpaid invoice balance.
7. Ledger entries are append-only and traceable via reference identifiers.
