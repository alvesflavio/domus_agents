# Domus Shared Memory

Durable project context shared by Claude Code and Codex agents.

## Project Facts

- Add stable architecture, domain, workflow, and repository facts here.

## Decisions

- Domus shared memory is project-local under `.domus/memory/`, so Claude Code and Codex agents working in the same repository can read and update the same handoff state.
- `AGENTS.md` is the shared instruction entry point; `CLAUDE.md` imports it with `@AGENTS.md` so Claude Code and Codex follow the same project-memory protocol.
- `.domus/memory/handoffs.md` is the cross-platform action log; `.domus/memory/shared.md` is reserved for durable facts, decisions, conventions, and explicit user preferences.
- Record decisions that future agents should not re-litigate without new evidence.

## User Preferences

- Record durable working preferences only when the user explicitly states them or repeatedly corrects the agents.

## Conventions

- Record project-specific commands, naming, review, testing, and deployment conventions.
