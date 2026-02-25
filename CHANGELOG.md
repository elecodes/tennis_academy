# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
