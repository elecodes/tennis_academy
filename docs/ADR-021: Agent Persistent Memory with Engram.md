# ADR-021: Agent Persistent Memory with Engram

## Status
Accepted (2026-03-15)

## Context
As the project grows in complexity, maintaining context across multiple agentic coding sessions becomes critical. While standard LLM context carries short-term state, long-term architectural decisions, specific bug "gotchas," and testing standards can be lost between sessions if not explicitly persisted.

## Decision
Integrate the **Engram MCP** (Memory Context Protocol) server to facilitate persistent "learnings" for AI agents.

1.  **Session Registration**: Every major task or feature development will begin with an Engram session (`mem_session_start`).
2.  **Proactive Observations**: Agents are encouraged to save structured observations (`mem_save`) regarding:
    *   Architectural choices (Monolith vs. Microservices).
    *   Security patterns (RBAC enforcement).
    *   Testing requirements (Coverage targets, mocking SMTP).
3.  **Cross-Session Continuity**: Agents must query `mem_context` or `mem_search` at the start of new sessions to recover the project's specific mental model.

## Consequences
- **Positive**: Reduced "amnesia" between sessions; faster onboarding for new agents; centralized repository of non-obvious project knowledge.
- **Workflow**: Adds a small overhead of session management and observation saving for the agent.
- **Storage**: Learnings are stored in the Engram persistent database, independent of the git repository but logically tied to the `tennis_academy` project ID.
