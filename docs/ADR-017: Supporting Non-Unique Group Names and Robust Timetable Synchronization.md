# ADR-017: Supporting Non-Unique Group Names and Robust Timetable Synchronization

## Status
Accepted

## Context
The tennis academy often has multiple groups with the same name (e.g., "Private", "Afternoon Squad") operating at the same time but managed by different coaches. 
Previously, the `groups` table had a `UNIQUE` constraint on the `name` column, which caused synchronization issues:
1. Overlapping sessions in Google Sheets would result in groups being merged or overwritten.
2. The UI would only show one instance of the group, effectively hiding other coaches' schedules.
3. Synchronizing a group with the same name but a different coach would either fail or inadvertently update the wrong record.

Furthermore, a bug was identified where processing multiple sessions for the same group on the same day would cause subsequent sessions to overwrite previous ones during the synchronization process.

## Decision
1. **Coach-Based Identity**: Removed the `UNIQUE` constraint from the `name` column in the `groups` table and introduced a composite `UNIQUE(name, coach_id)` constraint. Each group is now uniquely identified by its name paired with its coach.
2. **Robust Synchronization**: 
    - Modified `google_apps_script.js` to lookup groups by `(name, coach_id)`.
    - Updated `syncAllData` to clear the `group_schedules` table once at the start of a full sync, preventing "session wiping" while still allowing for complete schedule refreshes.
3. **Admin Webhook Updates**: Updated the `admin_edit_group` route to track and transmit the `original_coach_name` to the spreadsheet sync webhook, ensuring that changing a group's coach correctly updates the corresponding row in Google Sheets without losing the original identity reference.

## Consequences
### Positive
- **Support for Overlaps**: Different coaches can now lead distinct groups with identical names at the same time and on the same court (or different courts).
- **All Sessions Visible**: The weekly timetable correctly renders separate cards for all concurrent sessions.
- **Improved Sync Reliability**: Multiple sessions per day/group are now correctly preserved and accumulated during synchronization.

### Negative
- **Naming Ambiguity**: Administrators must be careful when viewing lists of groups with identical names; the system now displays the coach name to provide necessary context.

## Verification
- **Automated Verification**: Created `tmp/verify_robust.py` which confirmed that:
    - Two "Private" groups with different coaches at the same time are correctly synchronized and stored as separate entities.
    - Multiple sessions for the same group on the same day (e.g., 4:00 PM and 5:00 PM) are both correctly recorded in the database.
- **Manual Verification**: Inspected the database after a simulated sync and confirmed distinct group entries and full schedule preservation.
