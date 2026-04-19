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

### Changed
- **Color Palette V2**: Royal Blue (#163E85) + Golden Yellow (#E6C200)
- **UI Readability**: Larger day headers and time text
- **Template Caching**: Disabled auto-reload in production

### Fixed
- **Vercel Deployment**: Fixed 500 Internal Server Error in production by wrapping decorator responses with `make_response`.
- **Vercel Deployment**: Fixed 404 error by adding explicit route to api/app.py in vercel.json
- **Day Filter**: Server-side rendering (JS had CSS/grid issues)
- **Time AM/PM**: Fixed format_time for 12h DB format
- **Quick-Login Passwords**: coach/family now use admin123
- **JavaScript Errors**: Syntax fixes in timetable

## [1.15.0] - 2026-03-23
- Coach dashboard roster by schedule
- Spreadsheet sync continuation rows
- Time normalization

## [1.14.0] - 2026-03-20
- Mobile schedule display
- Simplified coach dashboard

---

**Last Updated**: 2026-04-13
**Version**: 1.16.0