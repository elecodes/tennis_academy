# Changelog

## [Unreleased]

### Added
- **PWA Support**: manifest.json, service worker, PWA meta tags for "Add to Home Screen"
- **Mobile Bottom Navigation**: Fixed bottom nav bar for mobile
- **Google Sheets Sync**: Schedules sync from Sheets to Turso
- **Day Filter Buttons**: Filter schedule by day (Mon-Sun)
- **V1/V2 Theme Toggle**: Palette button to switch color themes
- **Docker Support**: Dockerfile, docker-compose.yml
- **Vercel Deployment**: Full Vercel deployment with caching
- **API Response Caching**: Cache-Control headers for GET routes (private for RBAC)
- **Magic Draft Vercel Runtime Requirements**: Added `api/requirements.txt` for serverless dependency installation.

### Changed
- **Color Palette V2**: Royal Blue (#163E85) + Golden Yellow (#E6C200)
- **UI Readability**: Larger day headers and time text
- **Template Caching**: Disabled auto-reload in production
- **Vercel Python Install Source**: Switched install command to `pip install -r api/requirements.txt` for `api/app.py` runtime alignment.

### Fixed
- **Vercel Deployment**: Fixed 404 error by adding explicit route to api/app.py in vercel.json
- **PWA Icons**: Now displaying correctly on Vercel
- **Day Filter**: Server-side rendering (JS had CSS/grid issues)
- **Time AM/PM**: Fixed format_time for 12h DB format
- **Quick-Login Passwords**: coach/family now use admin123
- **JavaScript Errors**: Syntax fixes in timetable
- **Magic Draft Endpoint Reliability**: Added compatibility route for `/admin/api/draft-message` and improved status mapping for AI failures (`502` provider, `503` unavailable).
- **Magic Draft Error Handling**: Hardened malformed AI response parsing to avoid generic 500 fallthrough.

## [1.16.0] - 2026-04-15
- Coach dashboard roster by schedule
- Spreadsheet sync continuation rows
- Time normalization

## [1.14.0] - 2026-03-20
- Mobile schedule display
- Simplified coach dashboard

---

**Last Updated**: 2026-04-28
**Version**: 1.19.0