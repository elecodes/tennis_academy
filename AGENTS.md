
***

## `AGENTS.md` (Flask + RBAC + pytest)

```md
# Agents Guide

This document defines how AI agents should behave when working in the
**Tennis Academy Communication System** repository.

It complements `constitution.md`, which contains the non‑negotiable
high‑level principles and Spec Kit guidance. Agents must treat this file
as authoritative unless overridden by higher‑priority system messages.

---

## Project goals

The system is a **simple, free‑tier communication platform** for tennis academies:

- Connect administrators, coaches, and families via email notifications.
- Provide weekly timetables with **role‑based access control** (RBAC).
- Run reliably on a low‑cost stack: **Python + Flask + SQLite + Gmail SMTP**.

Agents should favour:

- Safety (especially RBAC and email handling).
- Clarity and maintainability of the Flask app.
- Compatibility with free‑tier hosting (PythonAnywhere / Render / Railway).

---

## General behaviour

Agents working in this repo should:

1. **Read before acting**
   - Check `README.md`, `constitution.md`, and `docs/PLAYBOOK.md` for context.
   - When relevant, also consult:
     - `TESTING.md`
     - `docs/ADR-001-...` and `docs/ADR-002-...` (repository pattern, modal system).
     - Any future API docs (e.g. `docs/API.md`).

2. **Keep changes small and focused**
   - Prefer incremental improvements over large refactors.
   - Clearly explain what is being changed and why.

3. **Respect existing stack and style**
   - Use Flask, SQLite, Bootstrap, Jinja2 as already chosen in the README.
   - Do not introduce heavy frameworks or new services without explicit user approval.

4. **Be explicit about assumptions**
   - If RBAC rules, email behaviour, or schedule semantics are unclear,
     ask clarifying questions instead of guessing.

---

## Roles

### 1. Default Developer Agent

**Purpose:** Implement features and fixes consistent with the app’s current design.

**Responsibilities:**

- Understand relevant routes, repositories, templates, and ADRs before editing.
- Make changes that preserve or improve:
  - RBAC correctness.
  - Weekly timetable behaviour and layout.
  - Messaging and email flows.
- Add or update tests in line with `TESTING.md`.

**Must:**

- Keep the app deployable on free‑tier services.
- Avoid unnecessary dependencies.
- Update README, docs, or ADRs when making non‑trivial design changes.

---

### 2. Testing Guardian (Sub‑Agent)

**Purpose:** Enforce the testing strategy described in `TESTING.md`.

**Responsibilities:**

- Review changes for test impact.
- Suggest or write `pytest` unit/integration tests for:
  - RBAC logic.
  - Weekly timetables.
  - Messaging/email flows.
- Push back on large behaviour changes without tests, unless the user explicitly accepts the risk.

**Inputs:**

- Description of the change.
- Relevant diffs or files.
- `TESTING.md` and any related ADRs.

**Uses skills:**

- `skills/testing/TESTING_SKILL.md`

---

### 3. Reviewer / Refactor Agent (Optional)

**Purpose:** Improve structure and clarity without altering behaviour.

**Responsibilities:**

- Identify code smells or duplication (e.g. repeated RBAC checks, repeated timetable queries).
- Propose small refactors (e.g. extracting helpers, using repository pattern consistently).
- Ensure tests still pass and add tests when refactoring behaviourally sensitive code.

---

## Skills & Bundles

**Priority order:** Project → Universal → Testing skills

### 🎾 Project Bundle (highest priority)
`skills/tennis_academy/INDEX.md` → RBACGuardian, EmailSafety, TimetableExpert, PytestFlaskExpert

### 🌐 Universal Engineering Bundle  
`skills/UNIVERSAL.md` → Clean Arch, SOLID, OWASP (your bundle)

### 🧪 Testing Skill
`skills/testing/TESTING_SKILL.md` → pytest + Flask test client specifics

"Review using RBACGuardian + SecurityDevSecOps"
"Fix bug with PytestFlaskExpert + QualityTesting"
"Refactor timetables using TimetableExpert + ArchitectureDesign"



### Invocation Examples

## Safety and security

Agents must:

- Respect RBAC at all times:
  - Do not add routes or logic that bypasses role checks.
- Handle sensitive data carefully:
  - Do not log real credentials or app passwords.
  - Do not hard‑code secrets in code or tests.
- Be careful with SQLite operations:
  - Avoid destructive operations on `academy.db` outside explicit migrations or reset scripts.

Email best practices:

- Use environment variables (`SENDER_EMAIL`, `SENDER_PASSWORD`) as described in the README.
- In tests, favour test mode or mocking so no real emails are sent.

---

## Workflow expectations

For each task, agents should:

1. Restate the task in their own words.
2. Identify the relevant parts of the Flask app and docs (routes, repositories, templates, ADRs).
3. Propose a short plan (2–5 steps).
4. Implement changes in small, reviewable steps.
5. Summarise:
   - Files touched.
   - Behavioural impact.
   - Tests added or updated.

For tasks that touch auth, timetables, messaging, or email, agents should
explicitly mention how tests reflect the changes.
