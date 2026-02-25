# ADR-009: Timetable RBAC and Data Isolation

## Status
Accepted

## Context
While the platform had basic RBAC decorators (`@admin_required`, etc.), the data retrieval layer in `TimetableRepository` was returning full objects regardless of the requester's role. This led to potential data leakage, specifically:
1. Coach emails being visible to all roles.
2. Families being able to see names of other children in shared groups.

## Decision
We decided to enforce strict Role-Based Access Control (RBAC) at the **Repository Layer** (`CORE` layer) to ensure data isolation.

1.  **Repository Method Signature**: Updated `get_weekly_timetable` to require `role` and `user_id`.
2.  **Coach Email Isolation**: Filter out `coach_email` if the role is not `admin`.
3.  **Kid Visibility Isolation**: For `family` role, filter group members to only include children belonging to that specific `family_id`.
4.  **Refactored Enrichment**: Extracted `_get_group_kids` and `_get_group_schedules` to handle specialized RBAC queries cleanly.
5.  **TDD Requirement**: Mandatory 100% test coverage for all RBAC-related logic in the repository layer.

## Consequences
- **Improved Security**: Zero leakage of PII (emails, child names) across unauthorized roles.
- **Maintainability**: Clear separation of concern between "fetching groups" and "enriching data for roles".
- **Performance**: Targeted SQL queries for families (filtering by `family_id`) ensure we only fetch necessary rows.
- **Verification**: Strict 100% coverage target ensures no regressions can be introduced without test failures.
