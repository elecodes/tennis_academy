# 🎾 SF TENNIS KIDS Club Communication System — Project Constitution

> Non-negotiable principles governing all development, specification, and implementation decisions.

---

## 🔐 Core Domain Rules (RBAC)

### Roles & Permissions Matrix
| Role | Read Access | Write Access | Cannot Access |
|------|-------------|--------------|---------------|
| **Admin** | All messages, announcements, users, coaches, families | Full CRUD on all entities | — |
| **Coach** | • Messages in their assigned family groups<br>• General announcements | • Send messages to families in their groups<br>• Reply to family messages | • Family personal emails<br>• Other coaches' groups<br>• Admin-only data |
| **Family** | • Messages in their own group<br>• Personal messages<br>• General announcements | • Send messages to their assigned coach<br>• Reply to coach messages | • Other families' names/emails<br>• Other coaches' data<br>• Admin panels |

### Data Isolation Requirements
- Families are **completely isolated**: no visibility into other families' identities or contact details
- Coaches see **only metadata** (e.g., "Family A") without PII unless explicitly shared by admin
- All queries must enforce row-level security based on authenticated user role + group assignment

---

## 🏗️ Architecture & Code Quality

- **Clean Architecture** (or closest pragmatic fit for small monolith): clear separation of domains, use-cases, interfaces, and infrastructure [[3]]
- **SOLID Principles**: Single Responsibility, Open/Closed for extensibility, Dependency Inversion for testability
- **KISS & YAGNI**: No over-engineering; implement only what's specified; defer "nice-to-haves" until validated
- **No spaghetti code**: Modular functions, explicit dependencies, avoid deep nesting (>3 levels)
- **Type safety**: Use TypeScript/Python type hints consistently; validate all external inputs

---

## 🧪 Testing Strategy (TDD First)

- **Test-Driven Development**: Write failing test → implement minimal code → refactor (Red-Green-Refactor)
- **AAA Pattern** for all tests: Arrange → Act → Assert for clarity and maintainability [[5]]
- **Test Pyramid**:
  - Unit tests: 70% (business logic, use-cases)
  - Integration tests: 20% (API endpoints, DB interactions)
  - E2E tests: 10% (critical user journeys via **Playwright**) [[4]]
- **Coverage**: ≥90% on core domain logic; 100% on auth/RBAC modules
- **Test data**: Use factories/fixtures; never hardcode credentials

---

## 🛡️ Security (OWASP Top 10 Compliance)

- **Authentication**: Secure session/JWT management; enforce MFA for admin accounts
- **Authorization**: Role + resource-based checks on **every** endpoint/query (never trust client)
- **Input Validation**: Sanitize & validate all user inputs server-side; use allowlists
- **Data Protection**:
  - Emails/PII encrypted at rest; never logged in plaintext
  - Secrets managed via environment variables; **store in Bitwarden**, never in code [[13]]
- **Security Headers**: CSP, HSTS, X-Frame-Options, etc.
- **Audit Logs**: Log auth attempts, permission changes, and sensitive actions (admin-only view)

---

## ♿ Accessibility & UX

- **WCAG 2.1 AA** compliance: semantic HTML, ARIA labels, keyboard navigation, color contrast ≥ 4.5:1
- **Responsive design**: Mobile-first; test on iOS/Android viewports
- **Performance**: 
  - LCP < 2.5s, FID < 100ms, CLS < 0.1 (Core Web Vitals)
  - Lazy-load non-critical assets; cache announcements
- **User Feedback**: Clear success/error states; loading indicators; undo for destructive actions
- **Minimal assets**: Avoid large screenshots; use optimized SVGs/icons when needed [[0]]

---

## 🔄 Development Workflow

- **Git**: Feature branches, descriptive commits (`feat:`, `fix:`, `chore:`), PR reviews required
- **CI/CD**: Run tests, lint, security scan on push; block merge if checks fail
- **Documentation**: 
  - Inline comments for complex logic
  - README with setup, env vars, and role diagrams
  - Keep `.gitignore` updated: `node_modules/`, `.env`, `.DS_Store`, `.specify/cache/`
- **Local Dev**: Use `uv` or `pip` for Python deps; document setup steps clearly

---

## 🚫 Anti-Patterns (Explicitly Forbidden)

- Hardcoded credentials, API keys, or tokens
- Direct DB queries in controllers (use repository pattern)
- Skipping auth checks for "internal" endpoints
- Over-fetching data (return only what the role needs)
- Ignoring accessibility for "simple" components
- Merging untested code

---

## 🎯 Decision Governance

When in doubt, ask:
1. Does this uphold RBAC isolation?
2. Is this the simplest solution that meets the spec (YAGNI)?
3. Can we test this reliably (TDD)?
4. Does this introduce OWASP risks?
5. Is this accessible to all users?

→ If any answer is "no", reconsider before implementing.