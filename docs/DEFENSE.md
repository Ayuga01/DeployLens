# DEFENSE: DeployLens event persistence

## What it does

DeployLens accepts normalized operational events and stores them durably so later incident-correlation features can query them. It treats repeated identical event submissions as safe retries and refuses conflicting reuse of an event ID.

## How it works

FastAPI validates the request, opens a SQLAlchemy session, and calls the repository. The repository maps the Pydantic event to the `events` table. PostgreSQL is the deployment target; SQLite is an offline development fallback. Alembic owns the schema.

## Key decisions

We chose PostgreSQL over a document store because the first access patterns are exact ID lookup and service/time filtering. We chose SQLAlchemy plus Alembic over direct SQL so the mapping and schema history are explicit and testable. We keep SQLite as the default only so the offline test command remains usable without Docker.

## Data structures

The main structure is the `events` table: `event_id` is the primary key, `service` and `timestamp` are indexed, and source-specific fields live in JSON `metadata`. This supports idempotent writes and future time-window grouping without prematurely indexing unknown metadata.

## Abuse and failure

The current API has validation and conflict protection but no authentication, rate limiting, tenant isolation, or request-size limit. A database outage prevents event reads/writes; a missing migration prevents event routes from working. These are known pre-production gaps.

## What changes next

Before a customer-facing deployment, add authentication, authorization, request limits, readiness checks, structured observability, PostgreSQL integration tests, and a tested backup/rollback procedure.
