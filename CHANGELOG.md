# Changelog

## [1.24.0] - 2026-07-06

### Added
- **Message Acknowledgments**: `ack_type` (TEXT) and `ack_at` (TIMESTAMP) columns on `message_recipients` via ALTER TABLE migration. Family can click "OK" or "Received" on each message via `POST /family/acknowledge/<message_id>`. Coach dashboard "Messages Sent" table shows per-message ack summary (e.g., "3 ok | 1 received") in a new Acknowledgments column, or "Awaiting response" if no acks yet.
- **Family Quick Messages**: New `family_quick_messages` table (Turso-only). 4 presets with no free text: Running Late, Will Miss Class, On My Way, Early Pickup. Rate-limited to 1 per 15 minutes per family. "Notify Your Coach" widget on family dashboard shows only when family has enrollments with a known `coach_name`. `POST /family/quick-message` validates preset against whitelist. Enrollment lookup checks Turso `group_members` first, then falls back to Supabase `fetch_family_enrollments()` by `parent_email` + `kid_name`.
- **Coach Reply to Family Alerts**: "Messages from Families" widget on coach dashboard — last 5 `family_quick_messages` filtered to coach's groups. Reply button opens modal with free text (coach is trusted role). `POST /coach/reply-family/<quick_msg_id>` creates `messages` + `message_recipients` row for the family, marks original quick message as `is_read = 1`. Red pulse dot for unread family alerts.
- **Admin Message Auditor**: `GET /admin/messages` — merged table of up to 100 broadcasts + 100 family notes (where `deleted_at IS NULL`), sorted by `sent_at` DESC. Source badges ("Family" purple / "Broadcast" navy). Edit modal with subject/content fields — POST to `/admin/messages/<id>/edit`. Soft delete: family notes set `deleted_at`, broadcasts clear subject/content to `[deleted]`. Nav link "Message Auditor" in admin sidebar.
- **Admin Supabase broadcast route**: `GET/POST /admin/send-message-supabase` — admin selects a Supabase lesson, sends email to enrolled families, stores message + `message_recipients` in Turso so families see it in inbox
- **Unread message tracking**: `is_read` column on `message_recipients` (ALTER TABLE migration). Family dashboard counts only unread messages via `LEFT JOIN + mr.is_read = 0`. "Mark All Read" button on messages page (`POST /family/mark-all-read`).
- **Read/unread visual styling**: Unread messages show accent left border, red pulse dot, bold subject. Read messages show muted opacity/color.
- **Unread Alerts card**: Clickable link to `/family/messages` when `stats.messages|length > 0`; static card showing "0" otherwise.
- **Family timetable from Supabase**: `fetch_timetable()` now accepts `user_email` parameter. For `role="family"`, filters lessons by `students.parent_email`. Family dashboard "Weekly Timetable" link now points to `/timetable-supabase`.
- **Family enrollments from Supabase**: New `fetch_family_enrollments(parent_email)` in `supabase_db.py` — returns enrollment dicts (kid_name, lesson title, coach, schedule) for students matching `parent_email`. Appended to Turso enrollments on family dashboard.
- **Nav bar "Broadcast (Supabase)" link**: Admin dropdown shows new route alongside existing Broadcast Alert.
- **Family enrollments page**: Replaced `sports_tennis` icon with SF TENNIS KIDS Club text badge.

### Changed
- **Coach dashboard**: "Send Message" link now points to `/coach/send-message-supabase` instead of Turso route.
- **Coach message type labels**: Aligned with admin form — `"Weather"` → `"Rain Cancellation"`, `"Delay"` → `"Coach Delay"`, `"Schedule"` → `"Schedule Change"`.
- **Coach Supabase messaging**: Now stores sent messages in Turso (`messages` + `message_recipients`) so families see them in their inbox (previously email-only).
- **Timetable week navigation**: Conditional URL (`timetable_supabase` vs Turso `get_timetable_page`) based on `supabase` template flag.
- **Family dashboard messages query**: Now joins `message_recipients` with `is_read = 0` filter for accurate unread count.
- **Family dashboard**: Now passes `turso_enrollments` and `quick_enrollments` to template — Turso-only enrollments kept for quick message group_id lookup, quick_enrollments filtered to those with a `coach_name`.
- **Coach dashboard recent_messages**: Now includes `ack_display` field per message (computed from `message_recipients` GROUP BY ack_type).

### Fixed
- **Family timetable**: Now correctly filters to only enrolled lessons (previous behavior was always showing "no sessions" — `role="family"` was skipped in `fetch_timetable` with a TODO comment).
- **Family unread count**: Previous query didn't account for `message_recipients`, showing all messages as unread even after viewing.
- **UnboundLocalError for non-admin users**: `sb_lessons_list` and `turso_enrollments`/`quick_enrollments` now initialized at function top before the role branching.
- **Family quick messages for Supabase-only enrollments**: Quick message enrollment lookup now falls back to Supabase `fetch_family_enrollments()` when Turso `group_members` has no match for the given `kid_name`.

## [1.23.0] - 2026-06-20

### Added
- **Admin dashboard Supabase lessons grid**: 9 cards showing title, type badge, coach, and time from Supabase `lessons` table (filters to current season)
- **Coach dashboard Supabase-first logic**: Coaches with Supabase lessons see ONLY Supabase groups (replaces Turso groups). Coaches without Supabase data fall back to Turso.
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

**Last Updated**: 2026-07-06
**Version**: 1.24.0
