# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **PWA Support**: Added manifest.json, service worker (sw.js), and PWA meta tags for mobile "Add to Home Screen" functionality
- **Mobile Bottom Navigation**: Fixed bottom navigation bar for mobile with active state highlighting
- **Google Sheets Sync**: Schedules now sync directly from Google Sheets to Turso database
- **Day Filter Buttons**: Added day filter buttons on schedule page to show only groups with lessons on selected day
- **V1/V2 Theme Toggle**: Palette button in header toggles between V1 (original navy/orange) and V2 (royal blue/golden yellow) themes, persisted in localStorage
- **Docker Support**: Added Dockerfile, docker-compose.yml, and .dockerignore for containerized deployment
- **Vercel Static Asset Caching**: 1-year immutable cache for CSS/JS/icons via Vercel edge CDN, service worker always revalidated
- **Template Caching**: Disabled auto-reload in production for faster Vercel cold starts

### Changed
- **Tailwind CDN**: Changed from link to script tag for proper loading
- **Mobile Layout**: Improved send message pages (coach & admin) for mobile with smaller padding, larger touch targets
- **Schedule Display**: Empty days now hidden for coach/family, shown with "+ Add" button for admin
- **Dashboard Header**: Reduced size on mobile for less scrolling
- **Coach Schedule**: Now shows only groups that have lessons on the selected day via day filter
- **Color Palette V2**: Deep Royal Blue (#163E85) + Golden Yellow (#E6C200) + medium-light gray background (#EEF0F5)
- **Timetable Readability**: Enlarged day headers (text-lg) and time text (text-base) with bolder styling and thicker borders
- **Coach Schedule UI**: Bold uppercase day names with larger time display for better readability

### Fixed
- **CDN Blocking**: Added fallback styles and local Tailwind as workaround for blocked CDN
- **Duplicate Groups**: Removed duplicate "Group" entry that was cluttering coach schedules
- **Admin Manage Groups Table**: Adjusted column widths - smaller Group column, wider Schedule column for better readability
- **Admin Dashboard**: Removed "System Health: Optimal" card from statistics snapshot
- **Timetable Provision**: Added separate page (/admin/timetable/new) for creating new sessions instead of modal
- **Local Tailwind**: Added local tailwind.js fallback when CDN is blocked
- **Day Filter JavaScript**: Fixed `filterGroupsByDay` not defined error - wrapped event listeners in DOMContentLoaded
- **Day Filter Type Mismatch**: Fixed string/number comparison bug in day filter - dayIndex now converted to string before comparison
- **Day Filter Server-Side**: Switched from JS filtering to server-side rendering with `?day=X` URL parameter for reliable filtering
- **Day Filter Grid Layout**: Fixed hidden day columns still taking grid space - now uses single-column layout when filtered
- **Day Filter Day Headers**: Fixed day headers showing when content was hidden - now hides entire day wrapper
- **Time Display AM/PM Bug**: Fixed `format_time` treating DB 12h times (e.g., "2:40:00pm") as 24h format, causing PM times to show as AM
- **Quick-Login Passwords**: Fixed coach and family quick-login buttons using wrong password (`password123` → `admin123`)
- **Duplicate Enrollments**: Removed duplicate student entries from database after sync

### Added
- **Coach My Groups Day Filter**: Added day filter buttons to coach my groups page to filter groups and schedule slots by day

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
