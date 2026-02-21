# Security: Tennis Kids Academy

This document outlines the security policies, sensitive data handling, and defensive measures implemented in the Tennis Kids Academy system.

## 1. Sensitive Data

### 1.1. Data Classification
The following data is considered sensitive and must be handled with care:
- **PII (Personally Identifiable Information)**: User full names, email addresses, phone numbers, and child names.
- **Credentials**: User passwords.
- **Authentication Tokens**: Flask session cookies and secret keys.
- **SMTP Secrets**: App-specific passwords for Gmail/Email services.

### 1.2. Handling Rules
- **Passwords**: Never stored in plain text. Hashed using `pbkdf2:sha256` via `werkzeug.security`.
- **Logging**: General rule: **never log sensitive data**. No PII, passwords, or tokens should ever appear in server logs or console outputs.
- **Persistence**: Sensitive data is stored in [academy.db](file:///Users/elena/Developer/tennis_academy/academy.db) with appropriate access restrictions.

## 2. Authentication and Authorization

### 2.1. Authentication
- **Mechanism**: Session-based authentication using Flask's `session` object.
- **Session Security**: Secured by a cryptographically strong `app.secret_key`.

### 2.2. Authorization (RBAC)
User permissions are enforced via Role-Based Access Control (RBAC) using custom Python decorators:
- `@login_required`: Restricts access to authenticated users.
- `@admin_required`: Restricts access to users with the `admin` role.
- `@coach_required`: Restricts access to users with either the `admin` or `coach` role.

## 3. Input Validation

### 3.1. Validation Patterns
All external inputs (HTTP POST/GET) are validated before processing:
- **Sanitization**: Inputs are cleaned using `.strip()` and `.lower()` (for emails) where appropriate.
- **Mandatory Fields**: Routes check for the presence of required fields (e.g., `email`, `password`) and flash warnings to the user if missing.
- **Type Casting**: Critical IDs (e.g., `coach_id`, `group_id`) are cast to appropriate types (`int` or `None`) to prevent processing errors.

## 4. Secret Management

### 4.1. Environment Variables
All operational secrets are managed through environment variables to keep them out of source control.
- **Usage**: The application uses `os.environ.get()` to retrieve secrets.
- **Local Dev**: Managed via a `.env` file (see [.env.example](file:///Users/elena/Developer/tennis_academy/.env.example)).
- **Production**: Secrets are injected directly into the hosting environment (e.g., Render).

### 4.2. Repository Safety
Secrets are **never committed** to the repository. The `.gitignore` file includes `.env` to prevent accidental disclosure.

## 5. Minimal OWASP-based Checklist

- [x] **No `eval`**: The system does not use `eval()` or similar unsafe constructs.
- [x] **Safe Subprocesses**: The system avoids `shell=True` and does not build shell commands from user input.
- [x] **Parameterized Queries**: All database interactions use parameterized SQL via `sqlite3` to prevent **SQL Injection**.
- [x] **CSRF Protection**: Flask session cookies are used to maintain user state securely.
- [x] **XSS Mitigation**: Jinja2 auto-escaping is enabled for all templates, preventing reflected and stored XSS.
## 6. Agent Enforcement Rules

AI agents working on this project **must** enforce these security rules:

### Never Do:
- Hard-code `SENDER_EMAIL` or `SENDER_PASSWORD`
- Log `session` contents, user PII, or SMTP credentials
- Use `shell=True` subprocess calls
- Render raw user input in Jinja2 templates without `|e` filter
- Access `academy.db` directly in tests (use tmp_db fixture)

### Always Do:
- Validate all form inputs (email format, required fields, length limits)
- Use `@login_required`, `@admin_required`, `@coach_required` decorators
- Mock SMTP in tests (`monkeypatch.setattr(smtplib, 'SMTP', MockSMTP)`)
- Check `app.config['TEST_MODE']` before sending real emails

### Quick Security Checklist for PRs:
[]  No hardcoded secrets
[ ] All forms validate required fields
[ ] RBAC decorators on protected routes
[ ] No PII in logs/console output
[ ] Tests use tmp_db, not production DB
[ ] SMTP mocked in tests

