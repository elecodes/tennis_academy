# TDD SKILL — SF TENNIS KIDS Club

## When to use this skill
Read this file before writing ANY new feature or fixing any bug in this project.
Follow Red → Green → Refactor strictly. No exceptions.

---

## Stack & Test Setup
- Language: Python 3.8+, Flask, SQLite
- Test framework: pytest
- Key modules:
  - `backend/app.py` — main Flask app
  - `backend/repositories/timetable_repository.py` — RBAC logic
  - `backend/routes/timetables.py` — timetable endpoints
- Test folders: `tests/unit/` and `tests/integration/`

## Run Tests
```bash
export PYTHONPATH=$PYTHONPATH:.
pytest tests/ -v --cov=backend --cov-report=term-missing
```

---

## TDD Cycle — strictly Red → Green → Refactor

1. **RED**: Write ONE failing pytest test. Show it failing before any implementation.
2. **GREEN**: Write the minimum production code to pass it. Nothing more.
3. **REFACTOR**: Clean up. Then repeat from RED.

---

## Mandatory Rules (never skip)
- Always use `tmp_db` fixture — never touch `academy.db`
- Always mock SMTP: `@patch('backend.app.smtplib.SMTP')`
- Test naming: `test_should_[behavior]_when_[condition]`
- One assertion focus per test
- Use `pytest.mark.parametrize` for edge cases and boundaries

---

## RBAC Coverage Requirements

| Role   | Coverage Target | Permissions |
|--------|----------------|-------------|
| Admin  | 100%           | Full access: users, groups, schedules, all messages |
| Coach  | 100%           | Their groups only, message their families only |
| Family | 100%           | Read-only: enrolled groups, schedules, own messages |

> ⚠️ Families have NO message sending capability at this stage.
> Any route that allows family to POST a message must return 403.

---

## Domain Priority Order (tackle lowest coverage first)

1. **RBAC on timetable queries** — what each role sees
2. **Admin → Coach messaging** — admin sends to all or specific groups
3. **Coach → Family messaging** — coach sends to their groups only
4. **User authentication and session enforcement** — login, logout, role on session
5. **Group management** — create group, assign coach, enroll family
6. **Weekly schedule filtering** — by role and by week

---

## Current Role Messaging Matrix (enforce via tests)

| Sender | Can message       | Cannot message         |
|--------|-------------------|------------------------|
| Admin  | Any group, all families, coaches | — |
| Coach  | Families in their groups only | Other coaches' groups |
| Family | ❌ Cannot send (future feature) | Everyone |

### Tests to write for messaging boundaries
```
test_should_allow_admin_to_send_message_to_any_group
test_should_allow_admin_to_send_general_announcement_to_all_families
test_should_allow_coach_to_send_message_to_their_group
test_should_reject_coach_sending_message_to_another_coaches_group
test_should_return_403_when_family_attempts_to_send_any_message
```

---

## SMTP Mock Pattern
```python
@patch('backend.app.smtplib.SMTP')
def test_should_send_message_when_coach_messages_their_group(mock_smtp, tmp_db, client):
    # login as coach
    # POST to /messages/send with valid group_id (assigned to this coach)
    # assert 200 or redirect
    # assert mock_smtp called — real emails never sent in tests
```

---

## Definition of Done for any feature
- [ ] All happy path tests pass
- [ ] All edge cases covered (invalid input, empty state, boundary values)
- [ ] RBAC enforced: unauthorized roles get 403, not 200
- [ ] SMTP mocked in every test that touches messaging
- [ ] `tmp_db` used in every test that touches the database
- [ ] Coverage targets met before merging

---

## 🔮 FUTURE FEATURES — Do Not Implement Yet

### Family Absence Notice (planned, not active)

> ⛔ DO NOT build this until coach/admin communication is fully tested and stable.
> This section is for planning only. No tests, no routes, no UI for this yet.

**Planned business rules (for reference):**
- Families will only be able to send one message type: `absence_notice`
- Recipients will be auto-resolved to: assigned coach + admin (family cannot choose)
- Fixed format — family fills in:
  - `kid_name` (must match an enrolled kid for that family)
  - `session_date` (future date only, format: YYYY-MM-DD)
  - `reason` (optional, max 280 chars)
- Subject auto-generated: `"Absence Notice – {kid_name} – {session_date}"`
- No duplicates: one absence notice per kid per session date
- Family cannot modify recipient list, message type, or subject

**When ready to build**, start with these tests in order:
```
test_should_send_absence_notice_when_family_submits_valid_form
test_should_reject_absence_notice_when_kid_not_enrolled_in_family
test_should_reject_absence_notice_when_session_date_is_in_the_past
test_should_reject_absence_notice_when_duplicate_for_same_kid_and_date
test_should_auto_resolve_recipients_to_coach_and_admin
test_should_not_allow_family_to_choose_message_type
test_should_not_allow_family_to_modify_subject
test_should_reject_reason_exceeding_280_chars
test_should_not_allow_family_to_send_other_message_types
  # parametrize: rain_cancellation, coach_delay, general_announcement, schedule_change
```