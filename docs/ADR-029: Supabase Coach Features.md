# ADR-029: Supabase Coach Features

## Status
Accepted (Updated 2026-07-06)

## Context
The app has data in two places:
1. **Turso (primary)**: Authentication, RBAC, `groups`, `group_members`, `messages`, `group_schedules`.
2. **Supabase (secondary)**: `lessons`, `students`, `student_lessons`, `coaches`, `seasons` — synced from Google Sheets via GAS v7.

Coaches needed to see their assigned lessons and communicate with enrolled families using Supabase data, which has richer lesson metadata (titles, types, structured day/time) compared to Turso's generic group names.

Later, it was decided that **coaches with Supabase data should see ONLY their Supabase lessons** (replacing Turso groups entirely) and the **admin dashboard should display Supabase lessons directly** rather than just a count.

## Decision

### 1. Supabase-Only Coach Routes
Create parallel routes prefixed with `-supabase` for coach features:

| Route | Purpose | Data Source |
|-------|---------|-------------|
| `/coach/my-groups-supabase` | Coach's lesson roster | Supabase `lessons` + `student_lessons` |
| `/timetable-supabase` | Weekly schedule with RBAC | Supabase `lessons` (all for admin, filtered for coach) |
| `/coach/send-message-supabase` | Send emails to enrolled families | Supabase `students.parent_email` |

### 2. Deduplication by (Day, Time)
Supabase stores lessons per season, creating duplicates (same lesson appears for each season). All three routes deduplicate by `(day, time)` key, and `fetch_timetable` also includes `coach_name` in the dedup key to handle different coaches at the same time.

### 3. Coach Matching by Name
Turso auth users and Supabase coaches share names but not IDs. Coach routes match by `full_name` (from Flask session) against Supabase `coaches.name` (case-insensitive). This works because GAS sync uses the same coach names in both systems.

### 4. Reuse Existing Templates
- `timetable-supabase` renders the existing `timetable.html` with `supabase=True` context flag
- The flag hides admin edit/delete buttons and the "Add Session" modal
- `send-message-supabase` has its own template with Magic Draft support

### 5. Email-Only Messaging (No Storage)
The Supabase messaging route sends emails directly to `students.parent_email` addresses without storing messages in Turso's `messages` table. This simplifies the flow and avoids cross-database message tracking. Future iterations can add logging if needed.

### 6. Coach Dashboard: Supabase-First Replacement
The coach dashboard (`/dashboard`) now replaces Turso groups with Supabase groups when the coach has Supabase data:
- **Has Supabase lessons?** → Show ONLY Supabase groups (filter out Turso `my_groups` from DB)
- **No Supabase lessons?** → Fall back to Turso groups as before
- This avoids duplicate cards and keeps the coach focused on the Supabase view which has richer data
- Implemented with a single `if sb_groups: my_groups = sb_groups` assignment in the dashboard route

### 7. Admin Dashboard: Supabase Lessons Grid
The admin dashboard now displays all Supabase lessons as a visual card grid:
- 3-column responsive grid (cards) showing title, lesson type badge, coach name, and time
- Placed between the stats snapshot and the Club Command Center
- Also shows a "9 total" badge in the section header
- `sb_lessons` is fetched in the same `fetch_lessons()` call already used for the Supabase Sync stat card, then passed to the template

## Consequences

### Positive
- Coaches see rich lesson titles and types from Supabase instead of generic "Group"
- Clean separation: no cross-database joins or message sync
- Existing Turso routes remain untouched and fully operational
- Template reuse minimizes duplication
- Coaches with Supabase data see a clean, deduplicated view (no Turso/Supabase mixup)
- Admin can inspect all Supabase lessons directly from the dashboard without navigating to a separate page

### Negative
- Supabase-only: features don't appear in Turso until GAS sync populates them
- Coach matching by name is fragile — if names diverge between Turso and Supabase, coaches lose visibility
- Messaging not stored in Turso means families can't see message history in their dashboard

### Neutral
- Dedup by (day, time) assumes no two distinct lessons share the same slot — true for current data
- End-time estimated as start + 1 hour (Supabase has no end_time field)

## Technical Details

### Key Functions in `supabase_db.py`

| Function | Returns |
|----------|---------|
| `fetch_coach_groups(coach_name)` | List of deduped lessons with student rosters |
| `fetch_timetable(role, user_name)` | Dict `{groups: [...]}` compatible with `timetable.html` |
| `fetch_coach_lessons(coach_name)` | Flat list of coach's lessons for message form |
| `fetch_lesson_parents(lesson_id)` | Parent contacts from `student_lessons` → `students` |

### Dashboard Integration Points

| Dashboard | Data Source | Logic |
|-----------|-------------|-------|
| Admin (`/dashboard`) | Turso stats + Supabase `fetch_lessons()`, `fetch_coaches()`, `fetch_students()` | 4 stat cards + Supabase lessons card grid |
| Coach (`/dashboard`) | Turso `my_groups` + Supabase `fetch_coach_lessons()` | Supabase lessons replace Turso groups if present; fallback to Turso otherwise |
| Family (`/dashboard`) | Turso `group_members` + Supabase `fetch_family_enrollments()` | Supabase enrollments appended to Turso enrollments; family timetable link points to Supabase |

---

## Extension: Family Dashboard + Unread Tracking (2026-07-03)

### 8. Admin Supabase Broadcast Route
`GET/POST /admin/send-message-supabase` — admin selects a Supabase lesson, writes a message, emails are sent to enrolled families, and the message is **also stored in Turso** with `message_recipients` entries so families see it in their inbox. This addresses the previous negative consequence where Supabase messages weren't visible in the family dashboard.

### 9. Coach Message Label Alignment
The coach Supabase message form's message type dropdown labels were aligned with the admin form:
- `"Weather"` → `"Rain Cancellation"`
- `"Delay"` → `"Coach Delay"`
- `"Schedule"` → `"Schedule Change"`

### 10. Coach Dashboard Supabase-First Link
The coach dashboard "Send Message" button now points to `/coach/send-message-supabase` instead of the Turso route.

### 11. Family Timetable from Supabase
`fetch_timetable()` now accepts a third `user_email` parameter. For `role="family"`, it filters lessons by `students.parent_email` matching the session email. The family dashboard "Weekly Timetable" link points to `/timetable-supabase`. The timetable week navigation uses conditional URLs (Supabase vs Turso) based on the `supabase` template flag.

### 12. Family Enrollments from Supabase
New `fetch_family_enrollments(parent_email)` function in `supabase_db.py` returns enrollment dicts (kid_name, lesson title, coach, schedule) for students whose `parent_email` matches. The family dashboard appends these to Turso enrollments — if no Turso enrollments exist, Supabase-only content is shown.

### 13. Unread Message Tracking
- **Schema**: `message_recipients.is_read` column (INTEGER DEFAULT 0) with ALTER TABLE migration (try/except for idempotency)
- **Unread count**: Family dashboard query uses `LEFT JOIN message_recipients` + `mr.is_read = 0` to count only unread messages
- **Family messages page**: Shows `is_read` status per message with visual styling:
  - **Unread**: accent left border, shadow, ring, red pulse dot next to type badge, bold subject
  - **Read**: muted left border, 70% opacity, no pulse dot, muted subject
- **Mark All Read**: `POST /family/mark-all-read` updates all `is_read = 1` for the logged-in family user
- **Unread Alerts card**: Clickable link to `/family/messages` when count > 0, static card with "0" otherwise

### Consequences

#### Positive
- Families see Supabase-based messages in their Turso inbox (cross-database bridge)
- Unread tracking gives families clear visual distinction between new and read messages
- Family timetable now works correctly (only shows enrolled lessons)
- One-click "Mark All Read" improves UX for families with many messages

#### Negative
- `fetch_timetable` family filtering requires fetching all students/lessons first (no server-side filtering via Supabase REST — O(n) over full dataset)
- Message storage in Turso from Supabase routes is best-effort (wrapped in try/except — if Turso write fails, email is still sent)

#### Neutral
- `is_read` migration uses ALTER TABLE with try/except — safe for both fresh installs and upgrades
- Message storage pattern (INSERT into `messages` + `message_recipients`) is identical for admin and coach Supabase routes

### Key Functions Added

| Function | Purpose |
|----------|---------|
| `fetch_family_enrollments(parent_email)` | Enrollments from Supabase filtered by `students.parent_email` |
| `fetch_timetable(role, user_name, user_email)` | Now supports `role="family"` with lesson filtering by parent_email |

### Routes Added

| Route | Method | Purpose |
|-------|--------|---------|
| `/admin/send-message-supabase` | GET, POST | Admin broadcasts to Supabase lesson families, stores in Turso |
| `/family/mark-all-read` | POST | Marks all unread messages as read for the logged-in family |

---

## Extension: Message Acknowledgments, Quick Messages, Coach Reply & Admin Auditor (2026-07-06)

### 14. Message Acknowledgments
- **Schema**: `ack_type` (TEXT) and `ack_at` (TIMESTAMP) columns on `message_recipients` via ALTER TABLE migration
- **Family flow**: Each message on `/family/messages` shows two buttons — "OK" and "Received" — below unacknowledged messages
- **POST `/family/acknowledge/<message_id>`**: Accepts `ack=ok` or `ack=received`, updates `ack_type`, `ack_at`, and sets `is_read = 1`
- **Coach ack summary**: Coach dashboard "Messages Sent" table shows per-message acknowledgment status (e.g., "3 ok | 1 received") in a new "Acknowledgments" column, or "Awaiting response" if no acks yet

### 15. Family Quick Messages
- **Schema**: New `family_quick_messages` table with `id`, `user_id`, `group_id`, `kid_name`, `coach_name`, `preset`, `subject`, `content`, `sent_at`, `is_read`, `deleted_at`
- **4 presets** (no free text — families are untrusted):
  - `running_late` — "Running Late — {kid}"
  - `will_miss` — "Will Miss Class — {kid}"
  - `on_my_way` — "On My Way — {kid}"
  - `early_pickup` — "Early Pickup — {kid}"
- **Rate-limited**: 15-minute cooldown per family user (checked by last `sent_at` in `family_quick_messages`)
- **Family dashboard "Notify Your Coach" widget**: Shows only when family has enrollments with a known `coach_name`. Dropdown selects child, then 4 preset buttons.
- **Enrollment resolution**: Checks Turso `group_members` first, then falls back to Supabase `fetch_family_enrollments()` by `parent_email` + `kid_name`
- **POST `/family/quick-message`**: Validates preset against whitelist, inserts row, flashes success

### 16. Coach Reply to Family Alerts
- **Coach dashboard "Messages from Families" widget**: Shows last 5 `family_quick_messages` where `deleted_at IS NULL`, filtered to coach's groups (by `group_id` or `coach_name` match)
- **Reply button** on each alert card → opens modal with family name and subject context
- **Coach has free text** (coach is a trusted role — no preset restriction)
- **POST `/coach/reply-family/<quick_msg_id>`**:
  1. Validates original quick message exists and is not deleted
  2. Creates a new `messages` entry with sender = coach, subject = `"Reply re: {original_subject}"`
  3. Creates `message_recipients` row for the family user
  4. Marks the original `family_quick_messages` row as `is_read = 1`
- **Red pulse dot**: Shows on unread family alerts in coach dashboard (from `is_read = 0`)

### 17. Admin Message Auditor
- **Route**: `GET /admin/messages` — new page at `/admin/messages`
- **Data sources**: Merges up to 100 broadcasts from `messages` table + up to 100 family notes from `family_quick_messages` (where `deleted_at IS NULL`), sorted by `sent_at` DESC
- **Table columns**: Sent, From (sender name + source badge: "Family" or "Broadcast"), Type (preset or message_type badge), Subject, Content (truncated), Actions
- **Edit modal**: Opens inline modal with pre-filled subject and content fields. POST to `/admin/messages/<id>/edit` updates the appropriate table based on `source` parameter
- **Soft delete**:
  - **Family notes** (`source=family_note`): Sets `deleted_at` timestamp (row hidden from coach dashboard)
  - **Broadcasts** (`source=broadcast`): Clears content to `[deleted by admin]` and subject to `[deleted]` (keeps the row for audit)
- **Nav link**: "Message Auditor" entry in admin sidebar dropdown (below "Broadcast (Supabase)" with `summarize` icon)

### Consequences

#### Positive
- Families can acknowledge messages, giving coaches visibility into whether families read important notices
- Quick messages give families a simple, safe way to communicate with coaches without exposing free-text abuse vectors
- Coach reply completes the communication loop — families can send quick notices and coaches can respond
- Admin auditor provides full visibility into ALL club communication (broadcasts + family notes) from one page
- Soft delete preserves audit trail while hiding content from regular views

#### Negative
- `family_quick_messages` is Turso-only (no Supabase storage) — families with only Supabase enrollments but no Turso user may get `flash` errors on quick message send
- 15-minute rate limit is app-level, not enforced in DB — concurrent requests could bypass it
- Ack summary queries are O(n) per coach dashboard render — acceptable for <50 messages but won't scale past hundreds

#### Neutral
- Ack pattern (ALTER TABLE + try/except) follows the same idempotent migration pattern as `is_read`
- Quick messages store the full resolved text (subject + content) rather than computing on read — simpler queries at the cost of minor duplication

### Routes Added

| Route | Method | Purpose |
|-------|--------|---------|
| `/admin/messages` | GET | Admin message auditor — all broadcasts + family notes |
| `/admin/messages/<id>/edit` | POST | Edit message subject/content |
| `/admin/messages/<id>/delete` | POST | Soft-delete family note or clear broadcast content |
| `/coach/reply-family/<quick_msg_id>` | POST | Coach replies to a family quick message |
| `/family/acknowledge/<message_id>` | POST | Family acknowledges a message (ok/received) |
| `/family/quick-message` | POST | Family sends a preset quick message to coach |

### Key Schema Additions

| Table/Column | Purpose |
|--------------|---------|
| `message_recipients.ack_type` | TEXT — `"ok"` or `"received"` |
| `message_recipients.ack_at` | TIMESTAMP — when family acknowledged |
| `family_quick_messages` | Family preset messages with `user_id`, `kid_name`, `coach_name`, `preset`, `subject`, `content`, `sent_at`, `is_read`, `deleted_at` |
