# ADR-027: Auto-Sync Webhook and Cache Invalidation

## Status
Accepted

## Context
The Tennis Academy app displays schedules sourced from a Google Sheet. Previously, sync was manual (admin clicking "Sync Sheets") or timer-based (GAS hourly trigger). This created a gap where:

1. Coaches updating the sheet had to wait up to an hour for families to see changes.
2. Browser and CDN caching compounded the delay — even after Turso data was updated, stale HTML/API responses persisted for 2-5 minutes.
3. The old GAS script used simple `onEdit()` which can't make HTTP requests, making webhook notification impossible.

We needed a solution where:
- Sheet edits propagate to the app within seconds (not hours).
- Cache is invalidated automatically after a sync.
- The architecture remains simple (no WebSockets, no polling, no extra infra).

## Decision

### 1. GAS Installable Triggers
We switched from simple `onEdit()` to an **installable `onSheetEdit` trigger** (created via `ScriptApp.newTrigger().onEdit().create()`). This is required because simple triggers cannot use `UrlFetchApp.fetch()`.

- `onSheetEdit()` — Fires on every cell edit, debounced at 30s.
- `syncAll()` — Hourly safety-net timer via `installHourlyTrigger()`.

### 2. GAS v7 → Turso Pipeline
The GAS v7 script (`scripts/google_apps_script_v7.js`) writes directly to the Turso database via the HTTP pipeline API:

```
DELETE FROM group_schedules → DELETE FROM group_members
→ For each sheet row: UPSERT group, UPSERT schedule, UPSERT member
→ DELETE orphan groups
```

This is a **full rebuild** approach (clear + re-insert) rather than incremental diffing. The full rebuild is fast enough (<5s for current data volume) and eliminates edge cases with partial updates.

Used `getValues()` (returns Date objects for time cells) + `instanceof Date` check in `cleanTime()` — the same proven pattern from v6 enrollments script.

### 3. Webhook Endpoint (`POST /api/webhook/sheets-sync`)
After writing to Turso, the GAS script calls `notifyFlask()` which POSTs to `/api/webhook/sheets-sync` with a shared `X-Sync-Key` secret for auth.

The Flask endpoint:
- Validates `X-Sync-Key` against `SYNC_API_KEY` env var.
- Records `last_sync_at` timestamp in the `app_config` table.
- Returns `200 OK` — the endpoint does NOT accept data; it only records the sync event for cache invalidation.

### 4. Adaptive Cache Invalidation
A custom `@cache_response` Flask decorator checks `last_sync_at` on each request:

| Sync recency | Cache TTL |
|-------------|-----------|
| <60 seconds ago | 10 seconds |
| ≥60 seconds ago | 60 seconds |

This means: after a Sheets edit, all API responses switch to 10-second TTL for 60 seconds, so user refreshes pick up changes quickly. After 60 seconds of no syncs, it relaxes back to 60-second TTL.

### 5. Service Worker Cache Bypass
The Service Worker (v10+) uses `{cache: 'no-cache'}` when fetching timetable data from the API, bypassing the browser's HTTP cache entirely. Combined with the Flask response TTL, this ensures fresh data on every navigation.

### 6. Debug Endpoint
`GET /api/debug/sync-status` returns a JSON blob with:
- Groups count, members count, last sync timestamp
- Sample of groups and schedules for verification

This is unauthenticated (read-only, no sensitive data) for quick debugging.

## Consequences
- **Positive**: Edits propagate to the app in 10-60 seconds (vs 1 hour).
- **Positive**: Cache adaptivity is automatic — no manual cache-busting.
- **Positive**: No additional infrastructure (no Redis, no message queue, no WebSockets).
- **Positive**: Debug endpoint makes it easy to verify data integrity.
- **Negative**: Full rebuild approach is inefficient for very large sheets (hundreds of rows). Acceptable for current scale (<100 rows).
- **Negative**: `SYNC_API_KEY` must match between Vercel env and GAS CONFIG.
- **Negative**: Installable triggers must be re-created if the GAS project is reset.
