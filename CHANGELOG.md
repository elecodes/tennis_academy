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
- **PWA Icon (Android)**: Fixed home screen icon showing generic letter instead of app logo — converted corrupt JPEG-as-PNG icons to valid PNG, split manifest `"any maskable"` into separate entries, and removed erroneous `/static/` Vercel route.
- **PWA Maskable Icons**: Added solid navy blue background to maskable icons to prevent Android from defaulting to grey/white background.
- **Login Security**: Removed plaintext sandbox credentials from the login page and moved them to a gitignored `test_credentials.md` file.
- **Service Worker Caching**: Bumped cache-busting `?v=8` parameter and SW `CACHE_NAME` to ensure PWA icon updates are fetched by devices.
- **Day Filter**: Server-side rendering (JS had CSS/grid issues)
- **Time AM/PM**: Fixed format_time for 12h DB format
- **Quick-Login Passwords**: coach/family now use admin123
- **JavaScript Errors**: Syntax fixes in timetable

## [1.16.0] - 2026-04-15
- Coach dashboard roster by schedule
- Spreadsheet sync continuation rows
- Time normalization

## [1.14.0] - 2026-03-20
- Mobile schedule display
- Simplified coach dashboard

---

**Last Updated**: 2026-04-28
**Version**: 1.18.0