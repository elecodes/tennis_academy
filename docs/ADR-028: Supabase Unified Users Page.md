# ADR-028: Supabase Unified Users Page

## Status
Accepted

## Context
The app has user data in two places:
1. **Turso (primary)**: Users with roles (admin/coach/family), used for authentication and RBAC.
2. **Supabase (secondary)**: Coaches and students from the Google Sheets sync, used for read-only views.

Admins needed a single page to see all people in the system. The challenge was that Turso and Supabase store different user types — Turso has login credentials and roles, Supabase has coach profiles and student records with parent contact info.

Initial implementation merged both sources into one view with "Login" and "Supabase" source badges, deduplicating by email. However, this created confusion because the two datasets represent different concepts (auth users vs. people records), and merging them risked exposing internal login accounts.

## Decision

### 1. Supabase-Only View
Show **only** Supabase data (coaches + students) in the `/admin/users-supabase` page. Turso users remain accessible via the existing `/admin/users` page.

### 2. Type Filter Tabs
Filter buttons toggle between All / Coach / Student views, built with vanilla JS class toggling — no extra dependencies.

### 3. Deduplication by Email
Supabase stores coaches and students per season, creating duplicates (same coach appears for each season). The `fetch_supabase_users()` function deduplicates by email for coaches and parent_email for students, using a shared `seen` set.

### 4. Source Badging
Every user row shows a "Supabase" badge with distinct blue styling, making it clear the data comes from the read layer, not the auth system.

### 5. Python-Side Join (Not SQL)
All data fetching uses Supabase REST API (PostgREST) which doesn't support cross-table queries. Joins between students, coaches, and other tables are done in Python. This is acceptable for the current data volume (<100 records).

## Consequences

### Positive
- Clear separation between auth users and people records
- Admins can see all Supabase people in one place with type filtering
- No risk of exposing login credentials in a read-only view
- Simple, maintainable code — no SQL joins across disparate databases

### Negative
- Duplicate information: admins must visit two pages (Users + Users Supabase) for the full picture
- Python-side joins don't scale to thousands of records (fine for current usage)

### Neutral
- Dedup by email assumes emails are unique across coaches and students — currently true, but may need revisiting if a parent email matches a coach email
