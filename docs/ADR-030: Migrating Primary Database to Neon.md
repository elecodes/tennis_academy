# ADR-030: Migrating Primary Database to Neon

## Status
Accepted

## Context
Previously, the primary PostgreSQL database used for Render/Vercel environments (specified by `DATABASE_URL`) was hosted on Supabase. However, Supabase's free-tier has a tendency to pause projects after 7 days of inactivity, and the project required a more reliable PostgreSQL database provider for hosting the direct SQL read/write layer.

Neon provides a modern, serverless PostgreSQL database with automated scaling and instant cold starts, which fits the platform's requirements better.

## Decision

### 1. Migrated PostgreSQL Provider to Neon
We migrated the direct database layer from Supabase PostgreSQL to Neon. The primary connection string (`DATABASE_URL`) has been updated to point to the new Neon connection pooler:
`postgresql://neondb_owner:npg_aSRPgxD35LBv@ep-purple-moon-aygn9vcl-pooler.c-5.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require`

### 2. URL Parsing Optimization
We updated `_parse_url()` in `backend/pg_db.py` to robustly strip any incoming query parameters (such as `?sslmode=require&channel_binding=require`) from the database name string. This prevents the driver (`pg8000`) from erroneously attempting to connect to a database named `database_name?parameters...`.

### 3. Data Migration & Schema Creation
We successfully initialized the tables on the new Neon database using the existing schema script (`backend/pg_migrate.py create`) and executed a custom migration script to copy all users, groups, schedules, members, messages, and configurations from the old Supabase instance to Neon in correct dependency order.

## Consequences

### Positive
- Modern, serverless database architecture on Neon with faster connection pooling and robust availability.
- Fixed the `ModuleNotFoundError` caused by incorrect python import path references (`from backend.pg_db ...` changed to `from pg_db ...`) when running on Render.
- Clean separation of database query parameters from driver parameter configuration.

### Negative
- None.
