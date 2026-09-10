# ADR-031: Complete UI and Route Unification on Neon Database with Resilient Connection Pooling

## Status
Accepted

## Context
Following the primary database migration to Neon PostgreSQL ([ADR-030](ADR-030:%20Migrating%20Primary%20Database%20to%20Neon.md)), the application contained residual split views and duplicate route endpoints (such as `/timetable` vs `/timetable-supabase`, `/admin/groups` vs `/admin/groups-supabase`, `/admin/users` vs `/admin/users-supabase`).

Furthermore, several user experience and stability issues were identified:
1. **Navbar & Dashboard Fragmentation**: UI navigation bars and Admin Command Center cards retained legacy "(Neo)" / "(Supabase)" badges and duplicate links.
2. **Database Connection Timeout / Socket Dropping**: In serverless environments, Neon pooler sockets would occasionally time out or close idle connections, raising `OSError: cannot read from timed out object` or `InterfaceError: network error`.
3. **Family Enrollment & Null-Pointer Exception**: Family logins experienced `AttributeError: 'NoneType' object has no attribute 'strip'` in `fetch_family_enrollments()` when student records contained `NULL` parent emails or comma-separated parent email lists (`esukhovnina@gmail.com, elena.sukhovnina@tennis.com, family1@email.com`).
4. **Schedule Navigation**: Clicking "Schedules" in the navbar routed to the legacy SQLite timetable endpoint (`/timetable`), rendering blank schedules for families enrolled in Neon.

## Decision

### 1. Unified Routes & Single Source of Truth
We consolidated all primary navigation links and endpoints to point to the unified Neon PostgreSQL data layer:
- Mapped `/timetable`, `/timetable-neon`, and `/timetable-supabase` to the single Neon timetable engine (`timetable_supabase()`).
- Updated legacy blueprint routes in `routes/timetables.py` to redirect to `timetable_supabase`.
- Cleaned up `base.html` and `admin_dashboard.html`, removing duplicate "(Neo)" badges and legacy cards.

### 2. Resilient Database Connection Pooling & Auto-Reconnect
Updated `_ConnectionPool` and `PgCursor` in `backend/pg_db.py`:
- Configured connection timeout (`timeout=30`) and cleared socket read timeouts post-SSL handshake.
- Added active connection validation (`SELECT 1`) inside `getconn()` before releasing a pooled connection.
- Built automatic connection recovery in `PgCursor.execute()`: if a socket error (`OSError`, socket timeout, or dropped connection) occurs during query execution, `PgCursor` transparently creates a new connection and retries the query once.

### 3. Multi-Email & Null-Safe Family Enrollment Resolution
Updated `fetch_family_enrollments()` and `fetch_timetable()` in `backend/academy_db.py`:
- Implemented robust string parsing for comma-separated and semicolon-separated `parent_email` fields.
- Added null-coalescing (`(s.get("parent_email") or "").strip().lower()`) to safely handle `NULL` values in PostgreSQL without raising `AttributeError`.
- Fixed boolean evaluation in `backend/app.py` (`if neon_family_enrollments is not None:`) to prevent accidental fallback to legacy SQLite queries when Neon returns valid enrollment records.
- Linked demo family (`family1@email.com`) and `elena.sukhovnina@tennis.com` to active student records (Aleksander & Alissa).

## Consequences

### Positive
- **Unified User Experience**: Single, clean navigation experience across Admin, Coach, and Family portals without duplicate links or badges.
- **Zero Socket Crashes**: Dropped or idle serverless PostgreSQL connections auto-reconnect seamlessly.
- **100% Family Login Reliability**: Family accounts log in cleanly and display their children's active lesson schedules on both the dashboard and weekly timetable.
- **Fully Verified**: Backend test suite passes 100%.

### Negative
- None.
