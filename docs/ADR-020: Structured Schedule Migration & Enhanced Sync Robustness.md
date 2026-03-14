# ADR-020: Structured Schedule Migration & Enhanced Sync Robustness

## Status
Proposed (2026-03-14)

## Context
The project is transitioning from purely text-based schedules stored in the `groups` table to structured, queryable session records in the `group_schedules` table. This is necessary for the weekly timetable grid and advanced RBAC filtering.

Additionally, the Google Apps Script synchronization mechanism needed to be more selective to avoid syncing non-core data sheets and more robust against empty sheets or malformed data.

## Decision
1. **Introduction of `backend/migrate_schedules.py`**:
    - A Python utility script to parse existing `schedule` text (e.g., "Mon 4pm, Wed 5pm") into structured records in the `group_schedules` table.
    - Implements regex-based parsing with 24-hour time conversion and meridiem detection.
    - Provides a "Repair Timetable" path for admins to manually trigger this migration from the dashboard.

2. **Google Apps Script (GAS) Enhancements**:
    - Implemented explicit sheet filtering: only sheets matching day names (e.g., "Monday", "Mon") or "data" are scanned.
    - Added safety checks for `lastRow < 2` to prevent processing empty sheets.
    - Improved sync feedback: the `sync_all` action now returns a `version` string (e.g., "v1.3 [DayFilter]") allowing the Admin Dashboard to report which script version responded.

3. **Dashboard Reporting**:
    - Updated `/admin/sync-spreadsheet` to capture and display the GAS version in the flash message, improving observability for system maintainers.

## Consequences
- **Positive**: More reliable synchronization, better visibility into the sync process, automated path for structured data transition.
- **Improved Maintainability**: Admins can self-repair timetable inconsistencies without developer intervention.
- **Migration Path**: All future schedule updates via spreadsheet or dashboard will feed into the structured table, eventually allowing the retirement of the legacy text field.
