# ADR-005: Messaging System Robustness & Environment Configuration

## Status
Accepted

**Date**: 2026-02-22

## Context
Refactoring and environment changes occasionally led to messaging failures that were difficult to diagnose due to lack of error handling and inconsistent environment variable loading. Specifically, coaches were unable to see group members or send messages if underlying SMTP configurations were not properly loaded.

## Decision
We have implemented several measures to ensure the messaging system is reliable and transparent:
1.  **Environment Sync**: Integrated `python-dotenv` with explicit loading in `backend/app.py` to support both root and logic-adjacent `.env` files.
2.  **Error Handling**: Wrapped all messaging routes (both Admin and Coach) in `try/except` blocks to prevent 500 errors and provide user feedback via flash messages.
3.  **Detailed Logging**: Added prefix-identifiable logic logging (e.g., `CRITICAL ERROR in coach_send_message`) to aid in remote troubleshooting.
4.  **Database Mapping Fixes**: Corrected the `coach_my_groups` route to ensure group member data is consistently fetched and passed to the frontend.

## Consequences
- **User Experience**: Users (Coaches/Admins) receive immediate feedback if a message fails to send.
- **Supportability**: Technical support can identify failures via server logs without deep code investigation.
- **Reliability**: Use of `load_dotenv` reduces "mystery failures" caused by missing credentials.
