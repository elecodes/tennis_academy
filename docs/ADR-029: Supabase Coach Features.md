# ADR-029: Supabase Coach Features

## Status
Accepted (Updated 2026-07-03)

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
