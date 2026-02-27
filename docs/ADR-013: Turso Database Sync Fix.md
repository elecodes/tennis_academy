# ADR-013: Turso Cloud Database Synchronization and Role Management

**Date:** 2026-02-27

## Context
During local testing and development, several authentication and testing scripts (such as `reset_admin.py` and `add_real_coaches.py`) were executing against the local fallback SQLite database (`academy.db`). However, the main backend Flask application was configured to connect to the live Turso cloud database using credentials stored in `.env`.
This resulted in a desync where test passwords and accounts updated locally were not reflected on the running application, preventing the admin and family roles from successfully logging in.

## Decision
1. **Script Refactoring for Cloud Context**: We updated the standalone Python utility scripts (e.g., `reset_admin.py` and `add_real_coaches.py`) to properly import and use the `get_db()` connection manager from `backend/database.py`. 
2. **Turso Environment variables**: By importing from `database.py`, the scripts now automatically read the `.env` variables (`TURSO_URL` and `TURSO_TOKEN`) and connect to the live cloud database just like the main application.
3. **Admin Credential Consolidation**: We identified that the real Turso database used `gelenmp@gmail.com` as the primary live admin account rather than the local dummy `admin@tennis.com`. We replaced the sandbox login details and `test_credentials.md` to reflect this accurate state.
4. **Password Reset**: All `admin` and `family` test passwords were systematically reset to `tennis2026` on the live database to restore smooth QA and testing workflows.

## Consequences
- **Positive**: Tests and local development utility scripts are now fully synchronized with the live environment when `.env` is populated, ensuring "what you test is what you get".
- **Positive**: Test credentials documentation directly maps to actual live accounts in Turso.
- **Negative**: Executing utility scripts locally can modify live cloud data. We must exercise caution when running these scripts in production environments.
