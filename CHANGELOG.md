# Changelog

## [Unreleased]

### Added
- **Supabase REST API read layer**: New `supabase_db.py` client using Supabase REST API (PostgREST) via HTTPS
- **Student list from Supabase**: `GET /admin/students` page with table of students from Supabase
- **Supabase enrollment list**: `GET /admin/enrollments-supabase` joining students + student_lessons + lessons + seasons + coaches, with season name mapping
- **Supabase unified users page**: `GET /admin/users-supabase` showing coaches + students from Supabase with type filter tabs (Coach/Student), source badges, deduplication by email
- **Coach groups from Supabase**: `GET /coach/my-groups-supabase` showing coach's lessons from Supabase with student rosters, deduplicated by (day, time)
- **Supabase weekly timetable**: `GET /timetable-supabase` renders full weekly schedule using Supabase lessons with RBAC (admin sees all, coach sees own), deduplication by (day, time, coach)
- **Supabase coach messaging**: `GET/POST /coach/send-message-supabase` — coach selects a Supabase lesson, writes message, Magic Draft supported, emails sent to parents enrolled via student_lessons
- **JSON endpoints**: `GET /supabase/students`, `/supabase/coaches`, `/supabase/lessons` for raw data access
- **`fetch_seasons`, `fetch_enrollments`, `fetch_supabase_users`, `fetch_coach_groups`, `fetch_timetable`, `fetch_coach_lessons`, `fetch_lesson_parents`**: New functions in `supabase_db.py`
- **Nav integration**: Admin dropdown (Students/Enrollments/Users Supabase) + Coach nav (My Groups/Send Message Supabase) + Schedules Supabase link for all roles
- **`_clean_kid_name()`**: Parses corrupted JS Date strings ("Sat Mar 14 2026...") in kid_name display for coach groups

### Changed
- **Stack**: Removed `sqlalchemy`, `psycopg2-binary`, `pg8000` from requirements — Supabase accessed via `requests` + REST API (no native PostgreSQL driver needed)
- **genkit** removed from root `requirements.txt` — caused Render build hang (google-cloud-bigquery metadata incompatible with pip≥24.1). Magic Draft gracefully falls back.
- **`timetable.html`**: Supports `supabase=True` context flag to hide admin edit/delete/modals in Supabase read-only mode

### Fixed
- **Render build**: Python 3.14 had no wheel for psycopg2-binary → switched to pg8000 → then to REST API entirely
- **Supabase IPv6-only**: Database only had AAAA record, no IPv4. REST API works over HTTPS (IPv4-compatible)
- **`@cache_response` decorator**: `render_template()` returns a string, not a Response object — wrapped with `make_response()` to avoid `AttributeError: 'str' object has no attribute 'headers'`

### Changed
- **Stack**: Removed `sqlalchemy`, `psycopg2-binary`, `pg8000` from requirements — Supabase accessed via `requests` + REST API (no native PostgreSQL driver needed)
- **genkit** removed from root `requirements.txt` — caused Render build hang (google-cloud-bigquery metadata incompatible with pip≥24.1). Magic Draft gracefully falls back.

### Fixed
- **Render build**: Python 3.14 had no wheel for psycopg2-binary → switched to pg8000 → then to REST API entirely
- **Supabase IPv6-only**: Database only had AAAA record, no IPv4. REST API works over HTTPS (IPv4-compatible)

## [1.20.0] - 2026-06-09

### Added
- **Auto-Sync Infrastructure**: Google Sheets edits sync to Turso within seconds via installable GAS triggers (`onSheetEdit`, `syncAll` hourly)
- **Webhook Endpoint**: `POST /api/webhook/sheets-sync` with `X-Sync-Key` auth for cache invalidation
- **Adaptive API Caching**: `@cache_response` decorator with 10s TTL when sync <60s ago, 60s otherwise
- **Service Worker v10**: Cache bypass via `{cache: 'no-cache'}` for fresh data after sync
- **Debug Endpoint**: `/api/debug/sync-status` for verifying Turso data integrity
- **App Config Table**: `app_config` key-value store for sync metadata (`last_sync_at`, `sync_version`)
- **GAS v7 Script**: Installable onEdit trigger + hourly timer, Turso pipeline writes, cleanTime with Date object handling
- **getValues() + instanceof Date**: Robust time parsing that handles Google Sheets Date objects correctly

### Fixed
- **GAS simple onEdit → installable trigger**: Simple triggers can't do `UrlFetchApp.fetch()`
- **Browser stale cache**: SW cache bypass + adaptive TTL prevents serving stale data after sync
- **SW install failure**: Removed auth-protected routes from SW pre-cache (caused install to fail)
- **Date.toString() corruption**: GAS `cleanTime()` checks `instanceof Date` and formats via `getHours()`/`getMinutes()` (v6 proven pattern)
- **CleanTime regex**: Parses "4:00:00 PM" format correctly (handles seconds in displayed values)
- **Group schedule update**: `syncAllData()` now updates existing group's `schedule` and `coach_id` fields when reusing
- **Orphan cleanup**: Groups with no schedules are deleted after each sync
- **Day name display**: Schedule field uses "Mon", "Tue" etc. instead of numeric dayIndex (0–6)

### Changed
- **Admin CRUD read-only**: Group and user create/edit/delete disabled (banner + disabled buttons). Manage via Google Sheets.
- **Sync Sheets / Repair Timetable buttons removed**: Auto-sync handles data; manual buttons were redundant.
- **Sync-spreadsheet route simplified**: Only updates `last_sync_at` for cache refresh (no more `GOOGLE_SHEETS_WEBHOOK_URL` dependency).
- **Removed `requests` dependency**: No longer needed after sync-spreadsheet simplification.

## [1.19.0] - 2026-04-28
- Coach dashboard roster by schedule
- Spreadsheet sync continuation rows
- Time normalization

## [1.14.0] - 2026-03-20
- Mobile schedule display
- Simplified coach dashboard

---

**Last Updated**: 2026-07-02
**Version**: 1.22.0