# 🎾 tennis_academy Complete Skill Index

**Official skill registry** for Tennis Academy Communication System (Flask + RBAC + pytest).  
**Priority:** Project → High Standards → Universal → Testing → Security

**Usage:** `"Review using RBACGuardian + Coverage100_80_0 + DDDTactical"`

---

## 🏆 PRIORITY 1: Project-Specific (Highest)

| Skill | Purpose | Triggers | pytest Location | Source |
|-------|---------|----------|-----------------|--------|
| **`RBACGuardian`** | **Admin/Coach/Family permissions** | **New routes, auth changes** | `tests/integration/test_rbac.py` | `SECURITY.md` + README |
| **`EmailSafety`** | Secure SMTP + test mocking | Email logic, message sending | `tests/integration/test_email.py` | README + `TESTING.md` |
| **`TimetableExpert`** | Weekly grid + role filtering | Timetable routes/templates | `tests/integration/test_timetables.py` | README features |
| **`PytestFlaskExpert`** | Flask `test_client()` + `tmp_db` | **All testing tasks** | All `tests/` | `TESTING.md` |

## 🎯 PRIORITY 2: High Standards Suite 

| Skill | Source File | Flask Adaptation | Coverage Target |
|-------|-------------|------------------|-----------------|
| **`ManifestoGuardian`** | `ENGINEERING_MANIFESTO.md` | Repository Pattern (your ADRs) | All refactors |
| **`DDDTactical`** | `TACTICAL_DDD_STANDARDS.md` | `Group.enroll_family()`, Value Objects | Domain models |
| **`Coverage100_80_0`** | `QUALITY_AND_TESTING_POLICY.md` | **100% repositories/RBAC, 80% routes** | `pytest-cov` |
| **`UXMicrocopy`** | `UX_AND_MICROCOPY_STANDARDS.md` | Bootstrap flash messages + modals | Templates/UI |
| **`DevSecOpsFlask`** | `DEVSECOPS_AND_SECURITY.md` | Flask-WTF forms + session security | Security reviews |

## 🌐 PRIORITY 3: Universal Engineering Bundle

| Skill | Purpose | Status |
|-------|---------|--------|
| **`AdaptiveProjectAnalysis`** | Architecture health check | **🟢 GREEN** (healthy Flask monolith) |
| **`ArchitectureDesign`** | Modular monolith + SOLID | Repository pattern validated |
| **`SecurityDevSecOps`** | OWASP + input validation | Flask-WTF + session security |
| **`ResilientLogic`** | Email retries + idempotency | Gmail SMTP specifics |
| **`UniversalUX`** | Accessibility + status visibility | Bootstrap WCAG compliant |

## 🧪 PRIORITY 4: Testing Framework

| Skill | pytest Files | Enforcement |
|-------|--------------|-------------|
| **`TestingGuardian`** | All `tests/` | **Blocks PRs <80% coverage** |
| **`TestingAdvisor`** | Test generation | AAA + `tmp_db` fixture |

## 🔒 PRIORITY 5: Security

| Skill | OWASP Coverage | Enforcement |
|-------|----------------|-------------|
| **`SecurityGuardian`** | Session/CSRF/XSS | `SECURITY_SKILL.md` |

---

## 💬 Invocation Matrix

| Task Type | Recommended Skills |
|-----------|-------------------|
| **New Route** | `RBACGuardian + PytestFlaskExpert + DevSecOpsFlask` |
| **RBAC Change** | `RBACGuardian + Coverage100_80_0 + TestingGuardian` |
| **Email Logic** | `EmailSafety + DevSecOpsFlask + PytestFlaskExpert` |
| **Timetable UI** | `TimetableExpert + UXMicrocopy + DDDTactical` |
| **Refactor** | `ManifestoGuardian + ArchitectureDesign + DDDTactical` |
| **Full PR Review** | `RBACGuardian + Coverage100_80_0 + SecurityGuardian + UXMicrocopy` |

## 📋 Standards Compliance Status

| Standard | Status | Enforcement |
|----------|--------|-------------|
| **100/80/0 Coverage** | 🟡 13/13 unit tests, needs integration | `Coverage100_80_0` |
| **DDD Value Objects** | 🔴 Missing (`GroupId`, `Email`) | `DDDTactical` |
| **RBAC Tests** | 🟡 Partial (needs all roles/endpoints) | `RBACGuardian` |
| **UX Microcopy** | 🟢 Bootstrap flash messages | `UXMicrocopy` |
| **Security Headers** | 🔴 Missing Flask-Talisman | `DevSecOpsFlask` |

---

## 🚀 Quick Start Commands

Single skill
"Review /admin/users using RBACGuardian"

Multiple skills
"New feature: family dashboard. Use RBACGuardian + UXMicrocopy + PytestFlaskExpert"

Full standards suite
"Apply high standards: ManifestoGuardian + Coverage100_80_0 + DevSecOpsFlask"

Standards + project
"Refactor timetables with TimetableExpert + DDDTactical + Coverage100_80_0"

## ⚙️ Priority Resolution Rules

Project skills OVERRIDE standards (RBACGuardian > SecurityDevSecOps)

TESTING.md is SOURCE OF TRUTH (Coverage100_80_0 aligns with pytest)

README workflows are SACRED (EmailSafety > ResilientLogic)

Human says → Human wins (all skills defer to user)
## 📊 Agent Output Format

🎾 SKILL REVIEW [PR #5 - Add Family Dashboard]

✅ PASS: RBACGuardian

All routes have @family_required decorator

test_family_cannot_access_coach_panel ✅

✅ PASS: UXMicrocopy

Flash messages use active voice

Bootstrap modals have ARIA labels

❌ FAIL: Coverage100_80_0

routes/family.py: 62% coverage (needs 80%)

FIX: tests/integration/test_family_dashboard.py

🔧 RECOMMENDED: DDDTactical

Extract FamilyId Value Object from family.family_id: int