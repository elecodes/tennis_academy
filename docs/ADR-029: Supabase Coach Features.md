# ADR-029: Supabase Coach Features

## Status
Accepted

## Context
The app has data in two places:
1. **Turso (primary)**: Authentication, RBAC, `groups`, `group_members`, `messages`, `group_schedules`.
2. **Supabase (secondary)**: `lessons`, `students`, `student_lessons`, `coaches`, `seasons` — synced from Google Sheets via GAS v7.

Coaches needed to see their assigned lessons and communicate with enrolled families using Supabase data, which has richer lesson metadata (titles, types, structured day/time) compared to Turso's generic group names.

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

## Consequences

### Positive
- Coaches see rich lesson titles and types from Supabase instead of generic "Group"
- Clean separation: no cross-database joins or message sync
- Existing Turso routes remain untouched and fully operational
- Template reuse minimizes duplication

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
