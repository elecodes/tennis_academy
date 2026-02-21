# Testing Strategy (Flask + RBAC)

Defines **mandatory testing rules** for the **Tennis Academy Communication System**.  
**Source of truth** for humans and AI agents. Used by `TestingGuardian`, `RBACGuardian`, and `PytestFlaskExpert` skills.

Current status: **13/13 unit tests passing** (per README). Integration tests needed.

---

## 🎯 Goals

1. **Protect core flows**: RBAC, timetables, messaging, email notifications
2. **Catch regressions**: Every bug fix gets a test that fails without the fix
3. **Enable refactoring**: 80%+ coverage on routes/repositories
4. **Agent enforcement**: Skills reject untested RBAC/timetable changes

**Rule**: If production failure would embarrass you (wrong role sees data, wrong families get emails), it **must** have a test.

---

## 🧪 Test Types & Coverage Targets

| Type | Coverage Target | What to Test | pytest Location | Example |
|------|----------------|--------------|-----------------|---------|
| **Unit** | **100%** | Domain logic, RBAC helpers, repositories | `tests/unit/` | `test_timetable_repository.py` |
| **Integration** | **80%** | Flask routes + DB + RBAC decorators | `tests/integration/` | `test_admin_rbac.py` |
| **E2E** | **Future** | Full browser flows | `tests/e2e/` | `test_coach_workflow.py` |

---

## 🎾 RBAC Testing (MANDATORY)

**Every protected route needs these 3 tests** (admin/coach/family):

### Template: RBAC Integration Test
```python
def test_[role]_can_access_[endpoint](client, tmp_db):
    # Arrange: login as [role]
    client.post('/login', data={'email': f'{role}@test.com', 'password': 'pass123'})
    
    # Act
    response = client.get('/[endpoint]')
    
    # Assert: success
    assert response.status_code == 200

def test_[wrong_role]_cannot_access_[endpoint](client, tmp_db):
    # Arrange: login as wrong role
    client.post('/login', data={'email': 'coach@test.com', 'password': 'pass123'})
    
    # Act  
    response = client.get('/admin/users')  # coach tries admin route
    
    # Assert: blocked
    assert response.status_code in 
Critical RBAC Tests Required:

✅ [ ] Admin sees all groups/timetables
✅ [ ] Coach sees only assigned groups  
✅ [ ] Family sees only enrolled kids' groups
✅ [ ] Coach cannot access admin panel
✅ [ ] Family cannot send messages
✅ [ ] Unauthenticated → login page
📧 Email Testing (MANDATORY)
Never send real emails in tests. Mock SMTP always.


def test_message_triggers_emails(client, tmp_db, monkeypatch):
    # Arrange: group with 3 families
    create_test_group_with_families(client)
    
    # Mock SMTP
    def mock_smtp(*args, **kwargs):
        return MockSMTP()
    monkeypatch.setattr('smtplib.SMTP', mock_smtp)
    
    # Act: send message
    response = client.post('/admin/send_message', data={
        'group_id': 1, 
        'subject': 'Test', 
        'content': 'Test message'
    })
    
    # Assert: 3 emails queued, no real SMTP calls
    assert response.status_code == 200
    mock_smtp.assert_called_once()
🗓️ Timetable Testing (MANDATORY)
Test RBAC filtering + week navigation:

def test_admin_sees_all_groups_timetables(client, tmp_db):
    # Arrange: 2 coaches, 3 groups, 5 timetable entries
    create_test_data(client)
    
    # Act: admin views timetables
    response = client.get('/timetables')
    
    # Assert: all groups visible
    assert response.status_code == 200
    assert 'Group A' in response.get_data(as_text=True)
    assert 'Group B' in response.get_data(as_text=True)

def test_coach_sees_only_assigned_groups(client, tmp_db):
    # Arrange: coach1 assigned to Group A only
    
    # Act
    response = client.get('/timetables')
    
    # Assert: only own group
    assert 'Group A' in response.get_data(as_text=True)
    assert 'Group B' not in response.get_data(as_text=True)
🏗️ Required Test Fixtures
Agents must use these pytest fixtures:

# conftest.py
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

@pytest.fixture  
def tmp_db(tmp_path):
    # Use temporary SQLite, never touch academy.db
    db_path = tmp_path / "test_academy.db"
    app.config['DATABASE'] = str(db_path)
    init_db()
    yield
    # Cleanup
🚫 Agent Enforcement Rules
TestingGuardian + RBACGuardian reject these changes without tests:

Change Type	Must Have Tests
New route	RBAC test (all roles)
RBAC change	Unit + integration tests
New form	Input validation + submission
Email logic	Mocked SMTP test
Timetable logic	Role-filtering test
Bug fix	Regression test
🧪 How to Run Tests (Canonical)

# All tests (current: 13/13 passing)
pytest tests/ -v

# Unit only  
pytest tests/unit/ -v

# Integration + coverage
pytest tests/integration/ --cov=app --cov-report=html

# Specific RBAC test
pytest tests/integration/test_rbac.py::test_coach_cannot_access_admin -v
📋 Agent Checklist Format
Agents must output tests in this format:


🧪 TESTING PLAN [Feature X]

✅ UNIT TESTS [tests/unit/test_X.py]

def test_[specific_case]():
    assert ...
✅ INTEGRATION TESTS [tests/integration/test_X.py]

def test_[role]_can_[action](client, tmp_db):
    # AAA pattern
❌ MISSING: [specific test needed]

## 🔗 Integration with Skills

| Document/Skill | Purpose |
|----------------|---------|
| `TESTING.md` | Human policy + pytest structure |
| `RBACGuardian` | Enforces RBAC test coverage |
| `PytestFlaskExpert` | Generates concrete pytest code |
| `TestingGuardian` | Rejects untested PRs |

**Priority:** `TESTING.md` > all skills. Skills must align with this document.
