# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Comprehensive Branding Overhaul**: Renamed "Tennis Kids Academy" to "SF TENNIS KIDS Club" across all templates, dashboards, and documentation.
- **Portal Terminology**: Standardized "Active Portal" and "Academy Portal" to "SF TENNIS KIDS Portal".

### Added
- Comprehensive system documentation ([ARCHITECTURE.md](file:///Users/elena/Developer/tennis_academy/ARCHITECTURE.md), [SECURITY.md](file:///Users/elena/Developer/tennis_academy/SECURITY.md)).

## [0.1.0] - 2026-02-21

### Added
- **Weekly Timetable**: Structured weekly group schedules with Admin CRUD management.
- **Premium UI**: Centered, high-contrast "SF TENNIS KIDS" design system for all dashboards.
- **Modal System**: Custom vanilla JS modal system for non-intrusive CRUD operations and alerts.
- **RBAC**: Role-Based Access Control using Python decorators (`@admin_required`, `@coach_required`).
- **Messaging Engine**: Multi-channel (Dashboard + Email) notification system with SMTP integration.
- **Enrollment Tracking**: Improved kid-to-group enrollment logic and reporting.

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
