# ADR-012: Implementing GitHub Actions for CI/CD

## Status
Accepted - 2026-02-27

## Context
As the `tennis_academy` project grows in complexity with multiple contributors and a rigorous testing strategy, we need to ensure that code quality is maintained automatically. Previously, linting and testing were manual processes, which are prone to being skipped or forgotten.

## Decision
We will implement GitHub Actions as our CI/CD platform to automate the following processes:
1. **Linting and Formatting**: Use `flake8` and `black` to ensure Python code adheres to project standards.
2. **Automated Testing**: Run the `pytest` suite on every push and pull request to the `main` branch.
3. **Build Validation**: Verify that frontend assets (bundled via `esbuild` and `zod`) can be built successfully.

## Consequences
- **Improved Code Quality**: Every PR will be automatically checked for linting and testing errors.
- **Faster Feedback**: Developers will know immediately if their changes break existing functionality or violate style guides.
- **Workflow Overhead**: Developers must ensure their code passes CI before merging.
- **Reformatting Requirements**: Some existing files (like `migrate_schedules.py`) had to be reformatted once to comply with `black` formatting checks.

## Tech Stack
- **GitHub Actions**: Runner environment.
- **Python 3.10**: Backend environment.
- **Node.js 20**: Frontend build environment.
