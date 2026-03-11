# ADR-016: Enhancing Spreadsheet Sync Observability and Manual Repair Tools

**Date**: 2026-03-11  
**Status**: Accepted  

## Context
Following the implementation of the one-way schedule sync (ADR-014), several operational issues were identified:
1. **Silent Failures**: The Google Apps Script would occasionally fail to sync specific rows or statements without clear logging back to the system.
2. **Sync Latency**: Administrators had to wait for hourly triggers or manually run the Apps Script to see changes, which was suboptimal for urgent updates.
3. **Data Desync**: Manual edits to group descriptions in the Web Dashboard could lead to the structured `group_schedules` table becoming out of sync with the text-based `schedule` field in the `groups` table.

## Decision
1. **Improved Apps Script Error Reporting**: Modified `google_apps_script.js` to return detailed results of batch executions, including individual SQL errors. This allows for better debugging of malformed sheet data.
2. **Remote Sync Trigger (Webhook)**: Added a `sync_all` action to the Google Apps Script and a corresponding `/admin/sync-spreadsheet` route in the Flask backend. This allows administrators to trigger a full refresh from the dashboard.
3. **Repair Timetable Utility**: Implemented a `/admin/repair-timetable` route that clears and repopulates the `group_schedules` table by parsing the `schedule` text field from the `groups` table.
4. **Admin UI Integration**: Added "Sync Sheets" and "Repair Timetable" buttons to the Groups management page to provide direct access to these tools.

## Consequences
### Positive
- **Better Observability**: Errors in the spreadsheet (like invalid times or missing groups) are now explicitly logged and traceable.
- **On-Demand Updates**: Sync latency is reduced to seconds when manually triggered.
- **Self-Healing Data**: The repair tool provides a safe way to restore the weekly grid if it becomes corrupted or desynchronized from the text descriptions.

### Negative
- **Increased Webhook Surface Area**: The Apps Script now exposes a `sync_all` action, which requires the `GOOGLE_SHEETS_WEBHOOK_URL` to be kept secure (though it is already limited by the `CONFIG` object access).
- **Complexity**: Adds more administrative routes and UI elements, slightly increasing the cognitive load for new admins.
