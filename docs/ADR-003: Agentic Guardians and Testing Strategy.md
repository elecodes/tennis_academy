# ADR-003: Agentic Guardians and Testing Strategy

## Status
Proposed

**Date**: 2026-02-21

## Context
As the project grows in complexity, ensuring consistent Role-Based Access Control (RBAC), security standards, and testing coverage becomes more challenging for both human developers and AI agents. We need a formalized way to enforce these standards automatically during the development process.

The project currently uses a manual testing strategy (13/13 unit tests passing) but lacks a deep integration of security and RBAC checks into the "agentic" workflow.

## Decision
We will implement a "Guardian" system using AI Sub-Agents and custom "Skills". This system will include:

1.  **Mandatory Rules Documents**:
    - `TESTING.md`: The source of truth for all testing rules, coverage targets (100% Core, 80% Global), and pytest conventions.
    - `AGENTS.md`: Defines the behavior and responsibilities of different AI agent roles (Developer, Testing Guardian, Reviewer).
    - `SECURITY.md` (Updated): Formalizes "Agent Enforcement Rules" for secrets, validation, and decorators.

2.  **Agent Skills**: 
    - Specialized instruction sets (e.g., `RBACGuardian`, `EmailSafety`, `PytestFlaskExpert`) that agents must invoke when modifying sensitive code.

3.  **Strict Enforcement**:
    - Agents are prohibited from adding routes without RBAC decorators.
    - Agents must provide corresponding tests for every behavioral change.
    - Real SMTP must never be used in tests.

## Consequences

### Positive
- **Consistency**: All code changes will follow the same security and testing patterns.
- **Safety**: Automated "push-back" from agents when risky changes are proposed without verification.
- **Scalability**: New developers (human or AI) can quickly understand the boundaries of the system.

### Negative
- **Overhead**: Every small change now requires thinking about (and potentially writing) tests and invoking specific skills.
- **Complexity**: The development environment now includes specialized "Guardians" and "Skills" logic that must be maintained.

## References
- [AGENTS.md](file:///Users/elena/Developer/tennis_academy/AGENTS.md)
- [TESTING.md](file:///Users/elena/Developer/tennis_academy/TESTING.md)
- [SECURITY.md](file:///Users/elena/Developer/tennis_academy/SECURITY.md)
- [SKILLS/tennis_academy/INDEX.md](file:///Users/elena/Developer/tennis_academy/SKILLS/tennis_academy/INDEX.md)
