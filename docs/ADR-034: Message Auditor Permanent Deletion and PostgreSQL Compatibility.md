# ADR-034: Message Auditor Permanent Deletion and PostgreSQL Compatibility

## Context
When deleting test messages from the Message Auditor (`/admin/messages/<message_id>/delete`) on the live production environment (`tennis-academy-six.vercel.app` backed by Neon PostgreSQL):
1. **PostgreSQL Compatibility Crash**: Deleting family notes executed `UPDATE family_quick_messages SET deleted_at = datetime('now') WHERE id = ?`. While `datetime('now')` is valid in SQLite, it is not a valid SQL function in PostgreSQL and caused an unhandled HTTP 500 error (`function datetime(unknown) does not exist`).
2. **Deletions Left Strikethrough Artifacts**: Deleting broadcast messages executed `UPDATE messages SET content = '[deleted by admin]', subject = '[deleted]' WHERE id = ?`, leaving crossed-out `[deleted]` entries on the auditor table rather than erasing them.

## Decision
1. **ANSI Standard SQL Timestamps**:
   - Replaced SQLite-specific `datetime('now')` with standard `CURRENT_TIMESTAMP`, which is universally supported across SQLite and PostgreSQL.
2. **Permanent Record Erasure**:
   - Updated `admin_delete_message` to hard delete messages:
     - For family notes: `DELETE FROM family_quick_messages WHERE id = ?`.
     - For broadcast messages: `DELETE FROM message_recipients WHERE message_id = ?` followed by `DELETE FROM messages WHERE id = ?`.
3. **Legacy Clean-up & Auditor UI**:
   - In `admin_message_auditor`, added automatic purge queries on page load to clean up any historical `[deleted]` records and deleted family notes (`deleted_at IS NOT NULL`).
   - Converted rows to standard Python dictionaries before sorting and mutating `ack_summary` to avoid `sqlite3.Row` attribute and mutation errors.
   - Removed obsolete `[deleted]` strikethrough logic from `frontend/templates/admin/message_auditor.html`.
4. **Automated Test Coverage**:
   - Extended `tests/test_rbac_access_control.py` to assert permanent record deletion from both `messages` and `family_quick_messages` tables, as well as verifying RBAC restrictions against unauthorized role access.

## Status
Accepted and Implemented.

## Consequences
- Administrators can erase broadcast and family quick messages permanently without leaving lingering `[deleted]` items in the auditor.
- Full cross-database compatibility between local SQLite and production Neon PostgreSQL.
