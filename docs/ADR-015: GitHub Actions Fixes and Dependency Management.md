# ADR-015: GitHub Actions Black Formatting and Requests Dependency Fix

**Status:** Accepted  
**Date:** 2026-03-05

## Context

During a routine GitHub Actions workflow run, the CI pipeline failed unexpectedly. 
The investigation revealed two separate but compounding issues:
1. **Formatting Discrepancy**: The `black --check .` step failed. The local developer environment and the CI environment were using different versions or had unformatted files, leading to a discrepancy causing the CI to fail.
2. **Missing Dependency**: After fixing the formatting issue, the subsequent `pytest` step failed with `ModuleNotFoundError: No module named 'requests'`. This was caused by the recent Turso Cloud HTTP connector migration (ADR-010) introducing the `requests` library in `backend/database.py` without it being added to `backend/requirements.txt`.

## Decision

1. **Format Code**: Formatted all Python files locally (`backend/app.py`, `backend/migrate_schedules.py`, `scripts/init_migrations.py`, `tests/test_timetable_repository.py`) using `black` to strictly adhere to the project's formatting code standards check.
2. **Add Dependency**: Explicitly added the `requests` library to `backend/requirements.txt`.

## Consequences

- **Positive**:
  - The CI pipeline (GitHub Actions) now succeeds, restoring confidence in code changes through automated checks.
  - The codebase formatting is unified and verified automatically.
  - The environment dependencies are fully specified, preventing downstream runtime and test deployment issues.
- **Negative**:
  - `requests` adds a minor dependency footprint, though it's standard and lightweight enough for the scope of the project's external HTTP calls.

## Future Considerations

- We should consider pinning the `black` version across developer environments to prevent formatting mismatches in the future, if this continues to be an issue.
- Incorporating an automated dependency checker could help identify missing modules in `requirements.txt` from imported libraries before they reach the testing stage.
