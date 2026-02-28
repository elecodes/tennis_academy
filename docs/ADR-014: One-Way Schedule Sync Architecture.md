# ADR-014: Disabling Two-Way Schedule Sync & Google Apps Script Execution Context

**Date**: 2026-02-28  
**Status**: Accepted  

## Context
Our application implements a synchronization system between the dashboard (Flask/SQLite) and Google Spreadsheets. Initially, the goal was **two-way synchronization**: edits in the dashboard would push to the Sheet, and edits in the Sheet would push to the dashboard. 

While this worked for standard row data (Kids Names, Parent Emails, Coach Names), it broke down catastrophically for **Group Schedules**. 

Because schedules are stored inside Google Sheets parsed across multiple day-specific tabs (e.g., "Monday", "Tuesday"), updating a schedule from the dashboard directly via the Apps Script Webhook corrupted the spreadsheet layout. Dashboard users could accidentally overwrite days, merge schedules incorrectly, or duplicate rows across tabs because the dashboard treats a schedule as a single unified string (e.g., `Mon 4PM, Wed 4PM`). 

Simultaneously, we encountered a Google Apps Script limitation: `UrlFetchApp` (HTTP Requests to our Turso database) is explicitly blocked from running inside "Simple Triggers" (like the default `onEdit(e)` function).

## Decision
1. **Disable Schedule Syncing from the Dashboard**: We modified the Flask backend (`admin_edit_group`) and Google Apps Script (`handleUpdateGroup`) to completely ignore the `schedule` field coming from dashboard updates. 
2. **Spreadsheet as Source of Truth for Schedules**: The Google Spreadsheet is now strictly the *only* place where Group Schedules can be safely modified. 
3. **Use Installable Triggers**: The Google Apps Script function `onEdit` was renamed to `onSpreadsheetEdit` to force administrators to set up an **Installable Trigger** via the Apps Script UI, which *does* have permission to make external REST API calls to our Turso database.

## Consequences
### Positive
- **Guaranteed Data Integrity**: The Google Sheet tabs remain fully intact and cannot be corrupted by malformed text strings from the UI.
- **Immediate Propagation**: With the Installable Trigger correctly configured, edits in the sheet instantly update the application via Turso.

### Negative
- **Friction for Admins**: Administrators can no longer easily shift a group's schedule by 30 minutes natively inside the Web Dashboard. They must open the Google Sheet, find the right day tab, and execute the change manually. 
- **Setup Complexity**: Deploying the system to a new Google Sheet requires manual intervention to set up the Installable Trigger, rather than just copy-pasting code.
