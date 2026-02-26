# ADR-008: Sentry Error Tracking Integration

## Status
Accepted
Date: 2026-02-25

## Context
As the "SF TENNIS KIDS CLUB" platform grows, we need visibility into application errors and performance bottlenecks in both the Flask backend and the Vanilla JS frontend. Manual log checking is insufficient for proactive error resolution.

## Decision
We decided to integrate **Sentry** (sentry.io) for real-time error tracking and performance monitoring.

1.  **Backend**: Use `sentry-sdk[flask]` and initialize it in `app.py`. It automatically captures unhandled exceptions and integrates with Flask's request lifecycle.
2.  **Frontend**: Use `@sentry/browser` within our bundled validation logic (`validations.js`). It is initialized with a `SENTRY_DSN` that can be provided globally via the `window` object.
3.  **Configuration**: DSNs are managed via environment variables (`SENTRY_DSN`) to keep credentials out of the codebase.

## Consequences
- **Proactive Bug Fixing**: Developers receive immediate alerts when errors occur, including stack traces and context.
- **Performance Insights**: Capture transaction data to identify slow database queries or slow frontend interactions.
- **Improved User Experience**: Replay functionality (frontend) can help reproduce complex client-side bugs.
- **New Dependency**: Added `sentry-sdk` (Python) and `@sentry/browser` (NPM).
