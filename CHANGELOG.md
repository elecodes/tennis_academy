# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.9.0] - 2026-02-27

### Added
- **GitHub Actions CI/CD**: Automated linting (`flake8`), formatting (`black`), testing (`pytest`), and build validation (`esbuild`) on push and pull requests.
- **ADR-012**: Documented the decision and implementation of GitHub Actions.
- **Improvement**: Added detailed error reporting for failed email deliveries in admin and coach messaging routes.

### Changed
- **Documentation Update**: Updated README and PLAYBOOK to reflect new CI/CD workflows and automated testing.
- **Code Refined**: Reformatted migration scripts to comply with `black` standards.

### Fixed
- **Messaging**: Resolved issue where selecting "All Club Families" resulted in zero recipients for admin broadcasts.
- **User Management**: Removed `UNIQUE` constraints on user emails to support family accounts sharing emails; updated login logic accordingly.
- **Database Integrity**: Fixed an `IntegrityError` preventing group creations and enrollments by repairing stale foreign key references from old migrations (affecting `groups`, `group_members`, `messages`, `group_schedules`).
- **Validation Sync**: Aligned client-side Zod validation (`groupSchema.ts`) with HTML forms and database schema, unblocking group creation silently failing in UI.
- **Google Sheet Sync**: Refactored `google_apps_script.js` and `add_real_coaches.py` to use `SELECT ... WHERE NOT EXISTS` instead of `ON CONFLICT` following the email uniqueness change, restoring coach and schedule synchronizations.

## [1.8.0] - 2026-02-27

## [1.7.0] - 2026-02-26

### Added
- **Turso Cloud Migration**: Moved from local SQLite to Turso Cloud (libSQL) for better reliability and distributed access.
- **Custom HTTP Connector**: Implemented a resilient HTTP-based connector for Turso to bypass SSL and WebSocket handshake issues on macOS.
- **Google Spreadsheet Sync**: Added automated synchronization of groups and schedules from Google Sheets via Google Apps Script.
- **Aggregated Schedules**: Group schedules are now aggregated and displayed as combined strings (e.g., "Mon 4:00 PM, Wed 3:30 PM").
- **Real Coach Accounts**: Provisioned official accounts for Coach Vlad, Michael, and RC.

### Fixed
- **Template Compatibility**: Resolved `KeyError: slice` errors in Jinja2 templates by implementing a custom `TursoRow` class.
- **SSL Certificate Verification**: Fixed connectivity issues with Turso by patching SSL context and managing CA bundles.
- **Sync Reliability**: Improved Google Apps Script to handle multi-sheet workbooks and precise day-of-week formatting.

## [1.6.0] - 2026-02-25

### Added
- **Timetable RBAC Enforcement**: Strict data isolation at the repository layer. Coaches and families are now restricted from seeing unauthorized data (coach emails, other children).
- **100% Core Coverage**: Achieved 100% test coverage for the `TimetableRepository` core logic.

### Changed
- **Repository Refactoring**: Extracted group enrichment logic into dedicated helper methods for better maintainability.
- **Enhanced Data Isolation**: Implemented filtering for coach emails and group member visibility based on user roles.

## [1.5.0] - 2026-02-25

### Changed
- **Comprehensive Branding Overhaul**: Renamed "SF TENNIS KIDS Club" to "SF TENNIS KIDS Club" across all templates, dashboards, and documentation.
- **Portal Terminology**: Standardized "Active Portal" and "Academy Portal" to "SF TENNIS KIDS Portal".

### Added
- Comprehensive system documentation ([ARCHITECTURE.md](file:///Users/elena/Developer/tennis_academy/ARCHITECTURE.md), [SECURITY.md](file:///Users/elena/Developer/tennis_academy/SECURITY.md)).

## [0.1.0] - 2026-02-21

### Changed
- Refactored `app.py` towards modular Blueprints and Repositories.
- Updated all frontend templates to a responsive, premium aesthetic.
- Enhanced database schema for better timetable management.

### Fixed
- Resolved 500 errors in coach messaging routes.
- Fixed icon rendering issues across dashboards.
- Corrected group membership visibility (Role-Based filtering).

## [0.0.1] - 2026-02-18

### Added
- Initial project structure and base Flask application.
- Basic user, group, and message tables in SQLite.
- Core landing page and login functionality.
