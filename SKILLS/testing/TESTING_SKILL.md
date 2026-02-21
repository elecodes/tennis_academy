# SKILL: Testing Advisor

## Purpose

Help developers and agents design, write, and enforce tests for the **Tennis Academy Communication System**, following the rules defined in `TESTING.md`.  
If there is any conflict, `TESTING.md` is the source of truth.

## Scope

This skill focuses on:

- Suggesting appropriate tests (unit, integration) for new or changed behaviour.
- Refusing to accept or generate significant changes without corresponding tests, unless explicitly justified.
- Reviewing existing tests for clarity, coverage of happy/edge/error paths, and alignment with project conventions.

It does **not** define the overall testing strategy for the project (that lives in `TESTING.md`).

## When to use this skill

- When implementing a new feature or modifying behaviour.
- When fixing a bug.
- When reviewing a pull request or code diff.
- When the user asks about tests, coverage, or how to test a specific scenario.

If the task only concerns documentation or non‑behavioural changes (e.g. README updates), this skill is usually not needed.

## Inputs

The skill works best when it receives:

- A short description of the change or feature.
- Relevant code snippets (Flask routes, repository methods, templates).
- Existing tests (if any) for the affected area.
- The specific pytest setup and Flask test client usage.

## Expected behaviour

When invoked, the Testing Advisor should:

1. Identify the behaviour being added or changed.
2. Classify the right test types:
   - **Unit**: pure repository logic, RBAC helpers, utilities.
   - **Integration**: Flask routes + test client + temporary SQLite DB.

3. Propose specific test cases:
   - Happy path (normal usage).
   - RBAC enforcement (wrong roles fail).
   - Edge cases (no data, invalid input, empty schedules).
   - Error handling (DB errors, invalid dates).

4. Enforce minimal rules:
   - Significant behaviour changes should come with tests.
   - Critical flows (auth, RBAC, timetables, messaging, email) must always have tests.

5. Point out missing tests and suggest where to place them in the project tree.

## Conventions

- Use **pytest** and follow the project structure:
  - `tests/unit/test_<module>.py`
  - `tests/integration/test_<feature>.py`
- Use Flask’s `test_client()` for integration tests.
- Use **temporary SQLite DB** for tests (not production `academy.db`).
- Mock SMTP/email sending in tests (do not send real emails).

## Examples

### Example 1 – New Flask route

**Input:**  
“Added route `POST /admin/send_message` for admins to send group messages.”

**Expected behaviour:**  

Propose integration tests:

```python
# tests/integration/test_message_sending.py

def test_admin_can_send_to_group(client, tmp_db):
    # Arrange: login as admin, create group
    ...
    
    # Act: POST to send_message
    response = client.post('/admin/send_message', data={...})
    
    # Assert: 200, message created, email queued (mocked)
    assert response.status_code == 200
    assert Message.query.count() == 1
Example 2 – RBAC change
Input:
“Fixed bug: coaches can now send to their groups only.”

Expected behaviour:

Suggest unit + integration tests:

python
# tests/unit/test_rbac.py
def test_coach_can_send_to_own_group():
    coach = User(role='coach', group_id=1)
    assert rbac.can_send_to_group(coach, group_id=1) == True
    assert rbac.can_send_to_group(coach, group_id=2) == False

# tests/integration/test_coach_permissions.py
def test_coach_cannot_access_other_groups_messages(client, tmp_db):
    # Arrange: login as coach1, create message for group2
    ...
    response = client.get('/coach/messages/group2')
    assert response.status_code in   # redirect or forbidden
Example 3 – Weekly timetable update
Input:
“Added ability to filter timetables by coach for admins.”

Expected behaviour:

Suggest integration test:

python
# tests/integration/test_weekly_timetables.py
def test_admin_can_filter_timetables_by_coach(client, tmp_db):
    # Arrange: create 2 coaches, 3 groups, 5 timetable entries
    ...
    
    # Act: GET /timetables?coach_id=coach1
    response = client.get('/timetables?coach_id=coach1')
    
    # Assert: correct template, only coach1 groups shown
    assert response.status_code == 200
    assert 'coach1_group' in response.get_data(as_text=True)
    assert 'coach2_group' not in response.get_data(as_text=True)
Example 4 – Email sending
Input:
“Fixed email template for rain cancellations.”

Expected behaviour:

Suggest unit test for email logic + integration test:

python
# tests/unit/test_email_utils.py
def test_rain_cancellation_template():
    msg = format_rain_cancellation(group_name="Juniors")
    assert "⚠️ RAIN CANCELLATION" in msg.subject
    assert "Juniors" in msg.body

# tests/integration/test_email_flow.py
def test_message_sends_emails_to_group_members(client, tmp_db, mock_smtp):
    # Arrange: group with 3 families
    ...
    
    # Act: admin sends message
    client.post('/admin/send_message', data={...})
    
    # Assert: 3 email calls made
    mock_smtp.send_message.assert_called()
    assert mock_smtp.call_count == 3
Failure modes
The skill should avoid:

Approving changes to auth/RBAC, timetables, or messaging without tests.

Suggesting tests that hit the production academy.db.

Proposing real email sends in tests (always mock SMTP).

Writing tests that rely on implementation details instead of observable behaviour:

Good: assert HTTP status, DB row count, rendered text.

Bad: assert specific internal variable values or private method calls.

Relationship to TESTING.md
TESTING.md defines:

Overall strategy (pytest, test types, coverage targets).

Tools used and how to run tests.

Global rules for what must be tested.

This SKILL defines:

How an agent behaves when reasoning about or proposing tests.

Concrete pytest examples, fixtures, and guardrails for testing‑related tasks.

If in doubt, read TESTING.md first and align all suggestions with it.

