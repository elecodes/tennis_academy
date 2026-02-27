# ADR-011: Implementing Security Headers with Talisman

## Status
Accepted

**Date: 2026-02-27**

## Context
As the application handles family and child data, ensuring a high security baseline is critical. Common web vulnerabilities such as Cross-Site Scripting (XSS) and Clickjacking need to be mitigated through standardized security headers. While Express.js applications typically use `helmet`, Flask applications lack this out-of-the-box, requiring a dedicated middleware.

## Decision
We decided to:
1.  **Implement `flask-talisman`**: Selected as the Flask-native equivalent to `helmet`.
2.  **Strict Security-by-Default**:
    -   Set `frame_options='DENY'` to completely prevent the application from being embedded in iframes (anti-clickjacking).
    -   Enabled `X-Content-Type-Options: nosniff`.
3.  **Tailored Content Security Policy (CSP)**:
    -   Allowed `self` for scripts and styles.
    -   Whitelisted Google Fonts (`fonts.googleapis.com`, `fonts.gstatic.com`).
    -   Whitelisted Tailwind CDN (`cdn.tailwindcss.com`) for utility-first styling.
    -   Whitelisted Sentry domains for transaction and error monitoring.
    -   Allowed `'unsafe-inline'` for scripts and styles to support the current template system and Tailwind's runtime injection.

## Consequences
-   **Pros**:
    -   Significant reduction in XSS and Clickjacking risks.
    -   Improved compliance with modern security standards.
    -   Non-intrusive integration that doesn't break existing monitoring or design systems.
-   **Cons**:
    -   `'unsafe-inline'` in CSP is a security tradeoff required for Tailwind CDN and current inline script usage; this should be reviewed if moving to a compiled CSS/JS architecture.
    -   Minor maintenance overhead to update the CSP whitelist for new external dependencies.
