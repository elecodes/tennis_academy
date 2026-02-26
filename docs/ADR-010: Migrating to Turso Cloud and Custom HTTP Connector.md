# ADR-010: Migrating to Turso Cloud and Custom HTTP Connector

## Status
Accepted

## Context
The application originally used a local SQLite database (`academy.db`). To enable real-time synchronization from external sources like Google Spreadsheets and to support distributed access, a cloud-hosted database was required. Turso Cloud (libSQL) was selected for its SQLite compatibility and performance.

However, during implementation, several critical blockers were encountered with the standard `libsql-client` Python library and its WebSocket implementation:
1. **SSL Certificate Verification**: Severe issues on macOS where `libsql-client` failed to find local CA bundles, even with `certifi` installed.
2. **Protocol/Server Errors**: Encountered repeated `505 Invalid response status` and `WSServerHandshakeError` when using the default WebSocket protocol.
3. **Template Compatibility**: The default `Row` objects from `libsql-client` were not fully compatible with Jinja2's slicing and attribute access (leading to `KeyError: slice`).

## Decision
We decided to:
1. **Migrate to Turso Cloud**: Move all production data to a Turso database.
2. **Implement a Custom Turso Connector**: Replace `libsql-client` with a custom implementation in `backend/database.py` that uses the `requests` library to communicate directly with the Turso HTTP API.
3. **Aggressive SSL Patching**: Centralize SSL context patching (using `SSL_CERT_FILE` and `REQUESTS_CA_BUNDLE`) to ensure connectivity on macOS environments.
4. **Custom Row Class**: Implement `TursoRow` to mimic `sqlite3.Row` behavior, ensuring full compatibility with existing frontend templates and slicing logic.
5. **Direct Spreadsheet Sync**: Use Google Apps Script to push data directly to Turso via their HTTP Pipeline API, bypassing the need for a backend intermediary for routine data updates.

## Consequences
- **Pros**:
    - High reliability and stability by bypassing problematic WebSocket libraries.
    - Improved developer experience with centralized database configuration.
    - Direct, fast synchronization from Google Sheets.
    - Full template compatibility without refactoring hundreds of lines of UI.
- **Cons**:
    - Slightly higher latency for individual queries compared to WebSockets (mitigated by batching).
    - Maintenance of a custom connector (though it is minimal and uses standard `requests` and `json` libraries).
