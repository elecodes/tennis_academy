# Changelog

## [Unreleased]

## [1.20.0] - 2026-06-09

### Added
- **Auto-Sync Infrastructure**: Google Sheets edits sync to Turso within seconds via installable GAS triggers (`onSheetEdit`, `syncAll` hourly)
- **Webhook Endpoint**: `POST /api/webhook/sheets-sync` with `X-Sync-Key` auth for cache invalidation
- **Adaptive API Caching**: `@cache_response` decorator with 10s TTL when sync <60s ago, 60s otherwise
- **Service Worker v10**: Cache bypass via `{cache: 'no-cache'}` for fresh data after sync
- **Debug Endpoint**: `/api/debug/sync-status` for verifying Turso data integrity
- **App Config Table**: `app_config` key-value store for sync metadata (`last_sync_at`, `sync_version`)
- **GAS v7 Script**: Installable onEdit trigger + hourly timer, Turso pipeline writes, cleanTime with Date object handling
- **getValues() + instanceof Date**: Robust time parsing that handles Google Sheets Date objects correctly

### Fixed
- **GAS simple onEdit → installable trigger**: Simple triggers can't do `UrlFetchApp.fetch()`
- **Browser stale cache**: SW cache bypass + adaptive TTL prevents serving stale data after sync
- **SW install failure**: Removed auth-protected routes from SW pre-cache (caused install to fail)
- **Date.toString() corruption**: GAS `cleanTime()` checks `instanceof Date` and formats via `getHours()`/`getMinutes()` (v6 proven pattern)
- **CleanTime regex**: Parses "4:00:00 PM" format correctly (handles seconds in displayed values)
- **Group schedule update**: `syncAllData()` now updates existing group's `schedule` and `coach_id` fields when reusing
- **Orphan cleanup**: Groups with no schedules are deleted after each sync
- **Day name display**: Schedule field uses "Mon", "Tue" etc. instead of numeric dayIndex (0–6)

### Changed
- **Admin CRUD read-only**: Group and user create/edit/delete disabled (banner + disabled buttons). Manage via Google Sheets.
- **Sync Sheets / Repair Timetable buttons removed**: Auto-sync handles data; manual buttons were redundant.
- **Sync-spreadsheet route simplified**: Only updates `last_sync_at` for cache refresh (no more `GOOGLE_SHEETS_WEBHOOK_URL` dependency).
- **Removed `requests` dependency**: No longer needed after sync-spreadsheet simplification.

## [1.19.0] - 2026-04-28
- Coach dashboard roster by schedule
- Spreadsheet sync continuation rows
- Time normalization

## [1.14.0] - 2026-03-20
- Mobile schedule display
- Simplified coach dashboard

---

**Last Updated**: 2026-06-09
**Version**: 1.20.0