# Tennis Academy Skill Bundle

**Usage:** Invoke by name, e.g. "Review this code using `RBACGuardian` and `EmailSafety` skills."

**Priority:** Project skills override Universal Engineering skills when there is conflict.

## 🏆 Project‑Specific Skills

### 🎾 RBACGuardian
**Purpose:** Enforce role‑based access control (admin/coach/family) at all layers.

**Mandatory Checks:**
- Admin: full access (users, groups, schedules, messages to all).
- Coach: only assigned groups + their schedules.
- Family: only enrolled kids' groups + their messages.
- **Never** add routes or logic that bypasses these rules.

**Test Requirements:**
- Integration test for every role/endpoint combination.
- Unit test for RBAC helpers.

**Examples:**
```python
# GOOD: coach can only see own groups
def test_coach_sees_only_assigned_groups(client, tmp_db):
    ...

# BAD: coach accesses admin panel (must fail)
def test_coach_cannot_access_admin_panel(client, tmp_db):
    ...
📧 EmailSafety
Purpose: Ensure email sending is secure, testable, and production‑ready.

Mandatory:

Use SENDER_EMAIL and SENDER_PASSWORD from env vars only.

Never hard‑code credentials or log real passwords.

In tests: mock SMTP, never send real emails.

Test Requirements:

Unit test email templates/formatting.

Integration test: message sent → SMTP called correct number of times.

🗓️ TimetableExpert
Purpose: Preserve weekly timetable behaviour and RBAC filtering.

Core Rules:

Admin: all groups.

Coach: assigned groups only.

Family: enrolled kids' groups only.

7×1 grid layout preserved.

Test Requirements:

Integration test: each role sees correct data.

Unit test: filtering logic.

🧪 PytestFlaskExpert
Purpose: Generate pytest tests that work with Flask test client + temporary SQLite.

Conventions:

tests/unit/test_<module>.py

tests/integration/test_<flow>.py

Use tmp_db fixture for SQLite.

Flask test_client() for HTTP.

Example Structure:

python
def test_admin_view_timetables(client, tmp_db):
    # Arrange
    create_test_data(client)
    
    # Act
    response = client.get('/timetables')
    
    # Assert
    assert response.status_code == 200
    assert 'all groups shown' in response.text
🔗 Universal Skills (imported)
Include all Universal Engineering skills by reference:

AdaptiveProjectAnalysis → Status: GREEN (healthy Flask monolith).

ArchitectureDesign → Follow repository pattern (as in your ADRs).

SecurityDevSecOps → Strict env var validation + session security.

QualityTesting → 100% domain (RBAC/timetables), 80% Flask routes.

ResilientLogic → Email retries + idempotent message sending.

UniversalUX → Bootstrap modals + clear feedback.

DDDImplementation → Domain entities like Group, Enrollment as Value Objects.

⚙️ Invocation Priority
Project skills (RBACGuardian, EmailSafety, etc.)

Universal skills (imported from skills/UNIVERSAL.md)

Testing skill (skills/testing/TESTING_SKILL.md)

Security skill (skills/security/SECURITY_SKILL.md)

📋 Example Usage
text
Review this PR using:
1. RBACGuardian (check role permissions)
2. EmailSafety (no real SMTP in tests)
3. TimetableExpert (schedule filtering)
4. QualityTesting (pytest coverage)
Output format:

text
✅ PASS: [skill name]
- What works well
- Evidence (code snippet)

❌ FAIL: [skill name]  
- What needs fixing
- Concrete fix (code snippet)
- Test to prevent regression