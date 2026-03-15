# ADR-019: Fix Admin Setup and Sandbox Credentials

## Status
Accepted (2026-03-15)

## Context
The application's initial setup flow (`/setup`) was failing because the route lacks the `POST` method in its Flask decorator. This prevented users from creating the initial administrator account. Additionally, demo credentials on the login page ("Sandbox Access") were outdated and did not match the actual seeded data in the Turso production database.

## Decision
1.  **Fix /setup route**: Add `methods=["GET", "POST"]` to the `/setup` route in `backend/app.py`.
2.  **Manual Admin Seeding**: Manually insert the `admin@tennis.com` user into the Turso database with the password `admin123` to restore access immediately.
3.  **Update Sandbox Credentials**: Synchronize the login page's "Sandbox Access" card with the actual database state:
    *   Administrator: `admin@tennis.com` / `admin123`
    *   Coach/Family: Updated to use `password123` (matching the demo data in `002_insert_sample_data.sql`).

## Consequences
- The initial setup process is now functional.
- Developers and testers can quickly log in using the "Sandbox Access" card with working credentials.
- Documentation (README, Playbook, etc.) must be updated to reflect the new default administrator email and passwords.
