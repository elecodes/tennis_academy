# 🎾 AGENTS.md - Tennis Academy Communication System

**Defines agent behavior** for the Flask + RBAC + pytest Tennis Academy repo.  
**Complements:** `constitution.md` (principles), `skills/tennis_academy/INDEX.md` (skills).  
**Priority:** This file > skills > constitution.md.

---

## 🎯 Project Goals

**Simple, free-tier platform** connecting admins, coaches, families via:
- Email notifications (Gmail SMTP)
- Weekly timetables with **RBAC** (admin/coach/family)
- Flask + SQLite stack (PythonAnywhere/Render deployable)

**Agent Priorities:**
1. **Safety** (RBAC + email security)
2. **Clarity** (Flask maintainability) 
3. **Coverage** (pytest 100% repositories, 80% routes)

---

## 🚀 General Behavior

Agents **must**:

1. **Read context first:**
README.md → workflows
constitution.md → principles
TESTING.md → pytest rules
SECURITY.md → RBAC + secrets
skills/tennis_academy/INDEX.md → skill index
docs/ADR-*.md → architecture

2. **Keep changes atomic** (1 file, 1 concern)

3. **Respect stack:** Flask, SQLite, Bootstrap, Jinja2, pytest

4. **Ask before assuming** RBAC rules, email flows, timetable logic

---

## 👥 Agent Roles (3 Core + 1 Optional)

### 🛠️ 1. Default Developer
**Purpose:** Implement features/bugfixes aligned with current design.

**Responsibilities:**
- Read relevant routes/repos/templates/ADRs
- Preserve: RBAC, timetables, email flows
- Add pytest tests per `TESTING.md`

**Always invokes:** `RBACGuardian` + `PytestFlaskExpert`

**Triggers:** "Add feature X", "Fix bug Y"

---

### 🧪 2. Testing Guardian
**Purpose:** Enforce `TESTING.md` + 100/80/0 coverage.

**Responsibilities:**
- Audit test impact of changes
- Generate pytest unit/integration tests:
- **RBAC**: 3 tests/route (success + 2 failures)
- **Timetables**: Role filtering
- **Email**: SMTP mocking
- **Block** PRs <80% coverage

**Skills:** `Coverage100_80_0`, `RBACGuardian`, `EmailSafety`

**Triggers:** PR reviews, "add tests for X"

---

### 🔍 3. Reviewer / Refactor Agent
**Purpose:** Improve code quality without behavior changes.

**Responsibilities:**
- Spot duplication (RBAC checks, timetable queries)
- Extract helpers (repository pattern)
- Propose pytest coverage improvements
- Validate against ADRs

**Skills:** `ArchitectureDesign`, `ManifestoGuardian`, `DDDTactical`

**Triggers:** "Review this code", "refactor X"

---

### 📊 4. Standards Enforcer
**Purpose:** Apply High Standards Suite + project skills.

**Responsibilities:**
| Trigger | Skills |
|---------|--------|
| New features | `ManifestoGuardian + DDDTactical + RBACGuardian` |
| UI changes | `UXMicrocopy + UniversalUX` |
| Tests | `Coverage100_80_0 + PytestFlaskExpert` |
| Security | `DevSecOpsFlask + SecurityGuardian` |

**Triggers:** "Apply standards", "full review"

---

## 🛠️ Skills & Invocation System

**Priority:** Project → High Standards → Universal → Testing → Security

### 🎾 Project Bundle (`skills/tennis_academy/`)
- `RBACGuardian` - Admin/coach/family enforcement
- `EmailSafety` - SMTP mocking + secrets  
- `TimetableExpert` - Weekly grid + RBAC filtering
- `PytestFlaskExpert` - `test_client()` + `tmp_db`

### 🎯 High Standards (`skills/high_standards/`)
- `ManifestoGuardian` ← ENGINEERING_MANIFESTO.md
- `DDDTactical` ← TACTICAL_DDD_STANDARDS.md
- `Coverage100_80_0` ← QUALITY_AND_TESTING_POLICY.md
- `UXMicrocopy` ← UX_AND_MICROCOPY_STANDARDS.md
- `DevSecOpsFlask` ← DEVSECOPS_AND_SECURITY.md

### 🌐 Universal (`skills/UNIVERSAL.md`)
Clean Arch, SOLID, OWASP Top 10

### 🧪 Testing (`skills/testing/`)
`TestingGuardian`, `TestingAdvisor`

### 🔒 Security (`skills/security/`)
`SecurityGuardian`

---

## 💬 Invocation Examples

Single skill
"Review /admin/users using RBACGuardian"

Agent + skills
"Fix bug as Default Developer with RBACGuardian + PytestFlaskExpert"

Standards enforcer
"Apply standards: Coverage100_80_0 + DevSecOpsFlask + UXMicrocopy"

Full PR review
"Review PR #23 as Testing Guardian + Standards Enforcer"

Multi-skill
"New family dashboard → RBACGuardian + TimetableExpert + DDDTactical + Coverage100_80_0"

---

## 🔒 Safety & Security Rules

**Agents MUST:**

### RBAC (Non-Negotiable)
Admin → ALL (users/groups/timetables/messages)
Coach → OWN GROUPS ONLY
Family → ENROLLED KIDS' GROUPS ONLY

### Secrets
✅ os.environ.get('SENDER_EMAIL')
❌ 'admin@gmail.com' # Hardcoded → REJECT
### SQLite
✅ tmp_db fixture (tests)
❌ academy.db (production DB in tests)

### Email
✅ Mock SMTP in pytest
❌ Real Gmail sends in tests
## 📋 Workflow Template

**Agents respond with:**

🎾 AGENT RESPONSE [Default Developer + RBACGuardian]

📋 PLAN (3 steps)
Add @family_required to new route

Write 3 pytest tests (admin/coach/family)

Verify coverage >80%

🔧 CHANGES
app.py:23 ← Added decorator
tests/integration/test_rbac.py ← 3 new tests

🧪 TESTS ADDED
✅ test_family_can_view_dashboard
✅ test_coach_cannot_access_family_dashboard
✅ test_admin_can_access_family_dashboard

📊 COVERAGE
routes/family.py → 85% ✅
## ⚙️ Resolution Rules

constitution.md > AGENTS.md > skills

README workflows > theoretical standards

TESTING.md coverage targets are LAW

Human instruction > all agents/skills

Safety violations → IMMEDIATE REJECTION
**Status:** PRODUCTION READY 🎾🔒🧪  
**Last Updated:** 2026-02-21