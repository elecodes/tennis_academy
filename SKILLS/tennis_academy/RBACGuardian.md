# 🛡️ RBACGuardian - Role-Based Access Control Enforcer

**Purpose:** Ensure **Admin/Coach/Family** permissions work correctly across all layers.  
**Source of Truth:** `SECURITY.md` + README workflows + `TESTING.md`.

## 🎾 tennis_academy RBAC Rules (MANDATORY)

| Role | Can | Cannot |
|------|-----|--------|
| **Admin** | Users, Groups, **All Timetables**, Messages to **ALL** | None |
| **Coach** | **Own Groups** only, Messages to **own groups** | Admin panel, other coaches' groups |
| **Family** | **Enrolled kids' groups** only, View messages | Send messages, manage users/groups |

## 🔍 Enforcement Checklist

### 1. **Route Decorators (ALL protected routes REQUIRED)**
```python
# ✅ REQUIRED for admin routes
@app.route('/admin/users')
@login_required
@admin_required        # ← MUST HAVE
def manage_users(): ...

# ✅ REQUIRED for coach routes  
@app.route('/coach/groups')
@login_required
@coach_required        # ← MUST HAVE
def coach_groups(): ...

# ✅ REQUIRED for family routes
@app.route('/family/timetables')
@login_required
def family_timetables():  # Family can view own data
    pass
2. RBAC Integration Tests (MANDATORY for EVERY endpoint)
# tests/integration/test_rbac.py

class TestAdminAccess:
    """Admin can access admin routes"""
    def test_admin_can_access_admin_panel(self, client, tmp_db):
        client.post('/login', data={'email': 'admin@test.com', 'password': 'admin123'})
        response = client.get('/admin/users')
        assert response.status_code == 200  # ✅ Success

class TestCoachAccess:
    """Coach can access coach routes only"""  
    def test_coach_can_access_own_groups(self, client, tmp_db):
        client.post('/login', data={'email': 'coach@test.com', 'password': 'pass123'})
        response = client.get('/coach/groups')
        assert response.status_code == 200  # ✅ Own routes OK
        
    def test_coach_cannot_access_admin_panel(self, client, tmp_db):
        client.post('/login', data={'email': 'coach@test.com', 'password': 'pass123'})
        response = client.get('/admin/users')
        assert response.status_code in   # ❌ Blocked!

class TestFamilyAccess:
    """Family can access family routes only"""
    def test_family_can_view_own_timetables(self, client, tmp_db):
        client.post('/login', data={'email': 'family@test.com', 'password': 'pass123'})
        response = client.get('/family/timetables')
        assert response.status_code == 200  # ✅ Own data OK
        
    def test_family_cannot_send_messages(self, client, tmp_db):
        client.post('/login', data={'email': 'family@test.com', 'password': 'pass123'})
        response = client.post('/coach/send_message')
        assert response.status_code in   # ❌ Blocked!
3. Critical RBAC Tests (MUST EXIST)
✅ test_admin_sees_all_groups
✅ test_coach_sees_only_assigned_groups  
✅ test_family_sees_only_enrolled_groups
✅ test_coach_cannot_access_admin_panel
✅ test_family_cannot_access_coach_panel
✅ test_unauthenticated_redirects_to_login
4. Timetable RBAC Tests (WEEKLY GRID)
def test_admin_sees_all_groups_timetables(self, client, tmp_db):
    # Arrange: 2 coaches, 3 groups, 5 timetable entries
    create_test_data(client)  # All groups exist
    
    # Act: admin login → view timetables
    client.post('/login', data={'email': 'admin@test.com', 'password': 'admin123'})
    response = client.get('/timetables')
    
    # Assert: sees ALL groups (7x1 grid complete)
    assert response.status_code == 200
    assert 'Group A' in response.get_data(as_text=True)
    assert 'Group B' in response.get_data(as_text=True)
    assert len(re.findall('group-row', response.text)) >= 3

def test_coach_sees_only_assigned_groups(self, client, tmp_db):
    # Arrange: Coach1 assigned Group A only
    create_coach_group_assignment(client, coach_id=1, group_id=1)
    
    # Act
    client.post('/login', data={'email': 'coach1@test.com', 'password': 'pass123'})
    response = client.get('/timetables')
    
    # Assert: ONLY own group visible
    assert 'Group A' in response.get_data(as_text=True)
    assert 'Group B' not in response.get_data(as_text=True)
🚫 AUTOMATIC REJECTIONS (No merge without fixes)
| Violation         | ❌ Example                   | Fix Required                         |
| ----------------- | --------------------------- | ------------------------------------ |
| Missing decorator | @app.route('/admin/groups') | Add @admin_required                  |
| Wrong permission  | Coach sees admin panel      | test_coach_cannot_access_admin_panel |
| Incomplete tests  | Only admin test exists      | Add coach + family tests             |
| Coverage <100%    | repositories/rbac.py: 75%   | pytest --cov-fail-under=100          |
✅ PASS CRITERIA
✅ Every protected route has correct decorator (@admin_required, @coach_required)
✅ 3 tests per endpoint: [role_success, coach_fail, family_fail] 
✅ Timetables filter correctly by role
✅ pytest --cov=repositories --cov-fail-under=100 PASSES
✅ README workflows preserved (Admin→All, Coach→Own, Family→Kids)
💬 Usage Examples
"New /admin/add_coach route → RBACGuardian + PytestFlaskExpert"
"Fix coach seeing all groups → RBACGuardian + Coverage100_80_0" 
"Review PR #23 → RBACGuardian + TimetableExpert + SecurityGuardian"
"Full standards → RBACGuardian + Coverage100_80_0 + DDDTactical + UXMicrocopy"
🔗 Integration
AGENTS.md → invokes RBACGuardian
TESTING.md → defines pytest structure  
SECURITY.md → defines RBAC policy
README.md → defines business workflows

***

## 🎯 **DONE** ✅

**2 SINGLE FILES ready to copy-paste:**

1. **`skills/tennis_academy/INDEX.md`** → Complete registry (15+ skills)
2. **`skills/tennis_academy/RBACGuardian.md`** → Full RBAC enforcement 

**Your agents can now say:**
"Review using RBACGuardian + Coverage100_80_0"

text

**Everything works together perfectly.** 🚀🎾🔒