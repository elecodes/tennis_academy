# Changelog

All notable changes to the SF TENNIS KIDS Club platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.27.0] - 2026-10-03

### Security Hardening (OWASP Top 10)
- **Access Control**: Secured `/api/debug/sync-status` and `/api/debug/pg-check` behind `@login_required` and `@admin_required` decorators.
- **IDOR Prevention**: Enforced coach group ownership checks on `/coach/reply-family/<int:quick_msg_id>`.
- **Secrets Protection**: Removed hardcoded plaintext fallbacks for `SENDER_PASSWORD`, Turso JWT tokens, and PostgreSQL connection passwords across `app.py`, `database.py`, and `pg_db.py`.
- **Session Security**: Enforced `SESSION_COOKIE_HTTPONLY = True` and `SESSION_COOKIE_SAMESITE = "Lax"`.
- **Error Handling**: Added `@app.errorhandler(404)` and `@app.errorhandler(500)` custom error handlers to prevent system stack trace leaks.

### Testing
- Added `tests/test_rbac_access_control.py` (5 tests).
- Added `tests/test_sensitive_data_protection.py` (4 tests).
- Added `tests/test_input_validation_injection.py` (2 tests).
- Added `tests/test_security_configuration.py` (3 tests).
- Added `tests/test_app_smoke.py` (4 end-to-end smoke tests).
- Automated test suite expanded to 19/19 passing tests (`100% passing`).

### Documentation
- Created `docs/ADR-032: OWASP Top 10 Security Hardening and RBAC Protections.md`.
