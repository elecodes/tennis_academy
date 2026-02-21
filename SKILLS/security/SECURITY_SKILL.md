# SKILL: Security Guardian

## Purpose
Enforce Flask + OWASP security for **Tennis Academy Communication System** per `SECURITY.md`.  
**Source of truth:** `SECURITY.md` > this skill.

## When to invoke
- New routes/forms/endpoints
- Authentication/RBAC changes  
- Email/SMTP modifications
- Database access changes
- PR/code reviews

## Critical Rules (Flask + tennis_academy)

### 1. Secrets & Environment
```python
# ✅ GOOD
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-only-fallback')

# ❌ NEVER
SENDER_EMAIL = 'admin@tennis.com'  # Hardcoded!
app.secret_key = 'hardcoded-secret' 
2. RBAC Enforcement
Every protected route must have a decorator:

python
# ✅ GOOD  
@app.route('/admin/users')
@login_required
@admin_required  
def manage_users(): ...

# ❌ BAD
@app.route('/admin/users')  # Missing decorators!
def manage_users(): ...
3. Input Validation (ALL forms)
python
# ✅ GOOD - Validate everything
email = request.form.get('email', '').strip().lower()
if not email or '@' not in email:
    flash('Valid email required')
    return redirect(request.url)

name = request.form.get('name', '').strip()
if len(name) < 2 or len(name) > 50:
    flash('Name must be 2-50 characters')
    return redirect(request.url)

# ❌ BAD - No validation
user.email = request.form.get('email')  # Raw!
user.name = request.form.get('name')    # Raw!
4. Jinja2 XSS Safety
xml
<!-- ✅ GOOD - Jinja2 auto-escapes -->
<h2>{{ user.name }}</h2>           <!-- Safe -->
<p>{{ message.content }}</p>       <!-- Safe -->

<!-- ❌ DANGER - Manual escaping needed -->
{{ user_input | e }}               <!-- Explicit -->
{{ user_input | safe }}            <!-- ONLY if sanitized! -->
5. Testing Security
python
# ✅ GOOD - Mock SMTP, tmp_db
def test_send_message(client, tmp_db, monkeypatch):
    def mock_smtp(*args, **kwargs):
        return MockSent()
    monkeypatch.setattr('smtplib.SMTP', mock_smtp)
    
    # Test logic without real email
    response = client.post('/send_message', data={...})
    assert response.status_code == 200

# ❌ BAD - Real SMTP in tests
smtplib.SMTP('smtp.gmail.com')  # Never in tests!
6. Logging Safety
python
# ✅ GOOD
app.logger.info(f"User {session['user_id']} sent message to group {group_id}")
# Log IDs/UUIDs only, never PII

# ❌ BAD  
app.logger.info(f"User {user.email} sent: {message.content}")
# Never log email/content!
Examples
Example 1: New Admin Route
Input: New /admin/add_coach route

text
❌ FAIL: Missing @admin_required decorator
✅ FIX: 
@app.route('/admin/add_coach', methods=['GET', 'POST'])
@login_required
@admin_required
def add_coach():
    # ... validated form logic
Example 2: Message Form
Input: New message sending form

text
❌ FAIL: No email/input validation
✅ FIX:
email = request.form.get('email', '').strip().lower()
if not validate_email(email):
    flash('Invalid email')
    return redirect(url)
    
subject = request.form.get('subject', '').strip()
if len(subject) > 200:
    flash('Subject too long')
    return redirect(url)
Example 3: Test Coverage
Input: New feature without security tests

text
❌ FAIL: Missing security tests
✅ FIX: Add to tests/integration/
def test_coach_cannot_access_admin_panel(client, tmp_db):
    # Login as coach
    client.post('/login', data={'email': 'coach@test.com', 'password': 'pass'})
    
    # Try admin route
    response = client.get('/admin/users')
    assert response.status_code in 
Checklist Format (for PR reviews)
text
🔒 SECURITY REVIEW [PR #X]

✅ Secrets: All use os.environ.get()
✅ RBAC: All protected routes have decorators  
✅ Validation: All forms validate required fields
✅ Logging: No PII/credentials in logs
✅ Tests: SMTP mocked, tmp_db fixture used
✅ Jinja2: No unsafe |safe filters

❌ FIX NEEDED: [specific issue + code fix]