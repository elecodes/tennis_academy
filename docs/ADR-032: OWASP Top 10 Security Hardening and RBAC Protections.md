# ADR-032: OWASP Top 10 Security Hardening and RBAC Protections

## Status
Accepted

## Context
The SF TENNIS KIDS Club platform handles sensitive family PII, including children's names, email addresses, phone numbers, and weekly group schedules. Ensuring defense-in-depth protection against the OWASP Top 10 security vulnerabilities is essential to protect user data and maintain system integrity.

## Decisions

### 1. Access Control Hardening (OWASP A01)
- **Protected Debug Endpoints**: Restricted `/api/debug/sync-status` and `/api/debug/pg-check` behind `@login_required` and `@admin_required` decorators to eliminate unauthenticated data leakage.
- **Eliminated IDOR in Coach Replies**: Enforced strict authorization checks on `/coach/reply-family/<int:quick_msg_id>` to ensure coaches can only reply to messages associated with groups they explicitly manage (or if acting as administrator).

### 2. Cryptographic Failures & Secrets Protection (OWASP A04)
- **Removed Hardcoded Credentials in Source**: Removed fallback app passwords (`SENDER_PASSWORD`), Turso JWT tokens, and PostgreSQL connection string passwords from source files (`app.py`, `database.py`, `pg_db.py`).
- **Configured Session Cookie Flags**: Enforced `SESSION_COOKIE_HTTPONLY = True` and `SESSION_COOKIE_SAMESITE = "Lax"` in Flask configuration to guard against XSS-based session hijacking and CSRF attacks.

### 3. Injection Prevention (OWASP A05)
- **Database Query Parameterization**: Verified 100% parameterization across all SQLite, PostgreSQL, and Turso database operations (`?` and `%s` placeholders).
- **Template XSS Protection**: Confirmed Jinja2 autoescaping across all dynamic variables and attributes in templates (`|e`).

### 4. Fail-Closed Error Handling & Security Headers (OWASP A02/A07)
- **Custom Error Handlers**: Added `@app.errorhandler(404)` and `@app.errorhandler(500)` handlers to render clean error pages without exposing stack traces or environment details.
- **Talisman Security Headers**: Maintained `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, and Content Security Policy (CSP).

## Consequences
- PII and system secrets are protected against exposure via source code, logs, and public endpoints.
- Role-based authorization is strictly enforced at every route level.
- Automated testing covers all 4 core security areas with 19 passing tests (`tests/test_rbac_access_control.py`, `tests/test_sensitive_data_protection.py`, `tests/test_input_validation_injection.py`, `tests/test_security_configuration.py`, `tests/test_app_smoke.py`).
