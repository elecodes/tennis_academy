# ADR-004: Project Structure Reorganization

## Status
Accepted

## Context
As the project grew, having all logic, templates, and static files in the root directory became difficult to maintain. We needed a clearer separation of concerns between backend logic and frontend assets to improve developer experience and prepare for potential scaling.

## Decision
We have reorganized the codebase into two primary top-level directories:
1.  `backend/`: Contains all server-side Python logic, including `app.py`, repositories, routes, and migrations.
2.  `frontend/`: Contains all user-facing assets, specifically `static/` files and `templates/`.

## Consequences
- **Maintainability**: Developers can easily locate relevant files.
- **Flask Configuration**: The Flask app initialization now explicitly defines the `template_folder` and `static_folder` paths relative to the `backend/app.py` location.
- **Database Pathing**: Database connectivity and scripts must now account for being in subdirectories (e.g., using `../academy.db`).
- **Path Consistency**: All documentation and scripts (e.g., `README.md`, `PLAYBOOK.md`, `quickstart.sh`) have been updated to reflect the new structure.
