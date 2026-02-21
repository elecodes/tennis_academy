# 🧱 DDDTactical

**Source:** TACTICAL_DDD_STANDARDS.md

## tennis_academy Entities

**Value Objects (create these):**
```python
@dataclass(frozen=True)
class GroupId:
    value: int
    def __post_init__(self):
        if not isinstance(self.value, int) or self.value <= 0:
            raise ValueError("Invalid Group ID")

@dataclass(frozen=True)
class Email:
    value: str
    def __post_init__(self):
        if '@' not in self.value or not self.value.endswith(('@gmail.com', '@tennis.com')):
            raise ValueError("Invalid academy email")
Aggregates:

text
Group (Aggregate Root)
├── name: str
├── coach_id: CoachId
├── enroll_family(family: FamilyId) → GroupMembership
└── invariant: max 20 families per group
Ubiquitous Language:

✅ group.enroll_family(family_id)
❌ group.update_member_count(5)
SOLID Check:

SRP: timetable_repository.py → only filtering

OCP: Add new @role_required('parent') without touching core auth