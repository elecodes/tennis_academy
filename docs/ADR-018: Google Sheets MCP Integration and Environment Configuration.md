# ADR-018: Google Sheets MCP Integration and Environment Configuration

## Context

To leverage AI agents for automated spreadsheet synchronization and data management within the SF TENNIS KIDS Club platform, we integrated the `mcp-google-sheets` Model Context Protocol (MCP) server. During setup, several environment and connectivity challenges were identified and resolved.

## Decision

1.  **Standardized Environment Variables**: Switched from custom keys to the industry-standard `GOOGLE_APPLICATION_CREDENTIALS` for service account path definition.
2.  **Spreadsheet ID Sanitization**: Configured the MCP server to use clean Spreadsheet IDs (e.g., `1pnJWsdaALpM9NghSXM41O0yM29FMgXDCPgRnbbceQBU`) instead of full URLs to prevent parsing errors.
3.  **Discovery Bypass Strategy**: For scenarios where the MCP server may not be immediately recognized by the host agent environment, a direct Python script execution pattern using `uv run --with google-api-python-client` is established as a reliable fall-back for critical data retrieval.

## Status

**Accepted** (2026-03-12)

## Consequences

-   **Connectivity**: The `google-sheets` server is now correctly configured to point to the `sfcoachesschedule-bf83e4ddaf57.json` service account.
-   **Maintainability**: Centralized configuration in `mcp_config.json` allows for easy updates to credentials or spreadsheet targets.
-   **Robustness**: Using `uv` for on-the-fly dependency management ensures that synchronization scripts remain decoupled from the main Flask `venv` while still being runnable by agents.
