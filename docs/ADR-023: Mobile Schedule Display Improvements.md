# ADR-023: Mobile Schedule Display Improvements

## Status
Accepted - 2026-03-20

## Context
The application is primarily used on mobile devices, but schedules were displayed as long text strings (e.g., "Monday & Wednesday 4:00-5:30 PM") which were difficult to read and took up too much space.

Additionally, the weekly timetable page had a bug where schedules weren't displaying correctly due to an undefined `day_num` variable.

## Decision
Implement compact, mobile-friendly schedule display using:

1. **New Jinja2 Filters**:
   - `schedule_compact`: Parses schedule text into array of compact pills
   - `format_time`: Converts 24h time (HH:MM) to 12h format (4pm, 9am)

2. **Template Updates**:
   - Update all views that display schedules to use compact pills
   - Fix timetable day column indexing

## Technical Details

### schedule_compact Filter
```python
def format_schedule_compact(schedule_text):
    """
    Converts schedule text to compact mobile-friendly format.
    Examples:
    - "Monday & Wednesday 4:00-5:30 PM" -> ["Mon 4pm", "Wed 4pm"]
    - "Sun 1:30pm" -> ["Sun 1:30pm"]
    - "Mon 16:00" -> ["Mon 4pm"]  # 24h format support
    """
```

### format_time Filter
```python
def format_time(time_str):
    """Convert 24h time (HH:MM) to 12h format (4pm, 9am)"""
```

### Supported Schedule Formats
| Input | Output |
|-------|--------|
| `Monday & Wednesday 4:00-5:30 PM` | `Mon 4pm`, `Wed 4pm` |
| `Sat 9:00-11:00 AM` | `Sat 9am` |
| `Sun 1:30pm` | `Sun 1:30pm` |
| `Mon 16:00` | `Mon 4pm` |
| `Tue Thu 3pm` | `Tue 3pm`, `Thu 3pm` |

## Templates Updated
1. `frontend/templates/family_dashboard.html`
2. `frontend/templates/admin/groups.html`
3. `frontend/templates/coach/my_groups.html`
4. `frontend/templates/coach_dashboard.html`
5. `frontend/templates/family/enrollments.html`
6. `frontend/templates/timetable.html`

## Consequences

### Positive
- Better mobile UX with readable schedule pills
- Consistent time format across all views
- Timetable now correctly displays all scheduled sessions

### Negative
- None identified

## Implementation Notes
- Filters handle both 12h and 24h time formats
- Graceful fallback to original text if parsing fails
- All existing tests continue to pass (18/18)
