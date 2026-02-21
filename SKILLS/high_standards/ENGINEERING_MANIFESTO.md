# 🎯 ManifestoGuardian

**Source:** ENGINEERING_MANIFESTO.md

## Enforcement for tennis_academy

**Domain-First:** Before DB changes, define:
- `Group.enroll_family(family_id)`
- `Timetable.filter_by_role(user_role)`

**Hexagonal Adaptation:** 
Core: repositories/timetable_repository.py (pure logic)
Adapters: app.py (Flask routes)

**Copilot Rule:** Every suggestion links to:
- `TESTING.md` rule violated
- `SECURITY.md` section
- README workflow impacted

**No Big Bangs:** Extract `GroupMembershipError` Value Object from existing code first.