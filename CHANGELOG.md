# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.12.1] - 2026-03-11

### Fixed
- **Overlapping Sessions**: Resolved issue where same-time lessons with different coaches were hidden.
- **Duplicate Group Names**: Groups with the same name (e.g., "Private") are now correctly distinguished by Coach ID.
- **Spreadsheet Sync**: Fixed session wiping bug where multiple daily sessions for the same group would overwrite each other.

## [1.12.0] - 2026-03-11

### Added
- **Admin Dashboard Tools**: New "Sync Sheets" and "Repair Timetable" buttons in the Manage Groups interface.
- **Manual Sync Webhook**: Backend route `/admin/sync-spreadsheet` to trigger Google Apps Script sync remotely.
- **Timetable Repair Logic**: Backend route `/admin/repair-timetable` to rebuild structured sessions from text schedules.
- **Improved Logging**: Enhanced Google Apps Script error reporting for batch SQL executions.

### Fixed
- **Spreadsheet Sync reliability**: Improved error handling in `executeBatch` to prevent silent failures.
- **Linting**: Resolved multiple linting errors across `app.py`, `magic_draft.py`, and test files.
- **CI Pipeline**: Fixed character limit and line length issues in `app.py` that were breaking pre-commit hooks.

### Changed
- **Group Editing**: Updated Group edit form to include a note about using the Repair Timetable tool after schedule text updates.

## [1.11.1] - 2026-03-05

### Added
- **Sentry Integration**: Added error tracking and monitoring.
- **Security Headers**: Implemented `flask-talisman` for improved security.

### Changed
- **Premium UI**: Migrated to a centered layout for better readability on large screens.
- **Turso Cloud**: Completed migration to Turso Edge database.
