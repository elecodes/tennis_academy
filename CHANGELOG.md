# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **PWA Support**: Added manifest.json, service worker (sw.js), and PWA meta tags for mobile "Add to Home Screen" functionality
- **Mobile Bottom Navigation**: Fixed bottom navigation bar for mobile with active state highlighting
- **Google Sheets Sync**: Schedules now sync directly from Google Sheets to Turso database
- **Day Filter Buttons**: Added day filter buttons on schedule page to show only groups with lessons on selected day

### Changed
- **Tailwind CDN**: Changed from link to script tag for proper loading
- **Mobile Layout**: Improved send message pages (coach & admin) for mobile with smaller padding, larger touch targets
- **Schedule Display**: Empty days now hidden for coach/family, shown with "+ Add" button for admin
- **Dashboard Header**: Reduced size on mobile for less scrolling
- **Coach Schedule**: Now shows only groups that have lessons on the selected day via day filter

### Fixed
- **CDN Blocking**: Added fallback styles and local Tailwind as workaround for blocked CDN
- **Duplicate Groups**: Removed duplicate "Group" entry that was cluttering coach schedules
- **Admin Manage Groups Table**: Adjusted column widths - smaller Group column, wider Schedule column for better readability
- **Admin Dashboard**: Removed "System Health: Optimal" card from statistics snapshot
- **Timetable Provision**: Added separate page (/admin/timetable/new) for creating new sessions instead of modal
- **Local Tailwind**: Added local tailwind.js fallback when CDN is blocked

### Fixed
- **Duplicate Enrollments**: Removed duplicate student entries from database after sync

## [1.15.0] - 2026-03-23

### Added
- **Coach Dashboard Roster by Schedule**: Students now appear grouped by their specific schedule slot. Each time slot shows which kids are enrolled at that time.
- **Spreadsheet Sync Continuation Rows**: Sync script now properly handles continuation rows where time/coach/group columns are empty but kid names are listed.
- **Time Normalization**: Fixed time format handling to prevent duplicate schedule entries from different time formats (e.g., "4:00pm" vs "4:00:00pm").

### Changed
- **Coach My Groups Page**: Students are now displayed under their specific schedule slot instead of all together in a flat list.
- **Removed UNIQUE Constraint**: `group_members` table no longer prevents duplicate kid entries in the same group, allowing the same kid to attend multiple slots.

### Technical Details
- Added `schedule_id` column to `group_members` table to track which schedule slot each enrollment belongs to
- Updated sync script to track and maintain the kid → schedule association
- Fixed time normalization to convert all times to 12-hour format consistently

## [1.14.0] - 2026-03-20

### Added
- Mobile schedule display with compact day/time pills
- Simplified coach dashboard (removed families card)
- Google Sheets MCP configuration
- Google Apps Script v6 with enrollment sync

### Changed
- Mobile-friendly schedule display
- Coach dashboard shows only groups and sessions
- Improved duplicate schedule detection and prevention

## [1.13.0] - 2026-03-17

### Added
- Sentry error tracking integration
- Turso cloud database with custom HTTP connector

### Changed
- One-way schedule sync architecture
- GitHub Actions CI/CD pipeline

## Previous Versions
See git history for earlier changelog entries.
