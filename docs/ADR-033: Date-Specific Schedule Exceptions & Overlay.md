# ADR-033: Date-Specific Schedule Exceptions & Overlay Architecture

## Context
The club needed a mechanism to communicate date-specific schedule changes (e.g., "Sat 10/3 at 12pm no lesson", "Alex absent Oct 10", "Time change to 1pm") without modifying or deleting recurring schedules in the database and without breaking the one-way schedule synchronization from `https://sfschedule.onrender.com/`.

## Decision
1. **Additive Local Table (`schedule_exceptions`)**:
   - Created `schedule_exceptions` table with columns: `id`, `group_id`, `schedule_id`, `kid_name`, `exception_date`, `status`, `note_text`, `created_at`.
   - Supported status types: `no_lesson` (🚫), `kid_absent` (🤒), `time_change` (⏰), `note` (ℹ️).
   - Schema defined in both SQLite (`init_db`) and PostgreSQL (`pg_migrate.py`).

2. **Admin Management & API Endpoints**:
   - Added `POST /admin/schedule-exceptions/add` for creating exceptions.
   - Added `POST /admin/schedule-exceptions/delete/<id>` for deleting exceptions.
   - Admin Dashboard UI overlay with interactive alert creation modal (`#addExceptionModal`) and exception status cards with instant deletion control.

3. **Dashboard & Timetable Overlay Layer**:
   - Coach Dashboard: Displays relevant alerts for assigned groups or club-wide exceptions.
   - Timetable View: Passes active `schedule_exceptions` for the target week (`week_start` to `week_end`) and renders a non-destructive Alert Overlay banner above cohort grids.
   - Preserves read-only status of `sfschedule.onrender.com` without modifying recurring master schedules.

## Status
Accepted and Implemented.

## Consequences
- Operational changes (cancellations, sickness, time shifts) can be broadcast to coaches and families cleanly.
- Master recurring schedules remain pristine and fully compatible with external sync sources.
