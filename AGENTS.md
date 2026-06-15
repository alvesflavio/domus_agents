# Domus Shared Agent Instructions

This project uses Domus shared memory so Claude Code and Codex agents can continue each other's work.

## Shared Memory Protocol

## Domus Low-Token Memory Stack

Before delegated, cross-agent, continuation, coordination, planning, review, or debugging work, read:

- `.domus/memory/state.md` for the current compact project snapshot.
- `.domus/memory/inbox.md` for active delegated tasks, owners, blockers, and next actions.
- `.domus/memory/shared.md` for durable project facts, decisions, conventions, and user preferences.
- `.domus/memory/agents/<agent-name>.md` when it exists for specialist-specific context.
- `.domus/memory/handoffs.md` only when state/inbox are insufficient or when the user asks for history.

If a user says an agent assigned, handed off, continued, remembered, or queued work, inspect shared memory before acting.

When `workstyle-standards-coordinator` is invoked for delegation, cross-agent continuation, or memory setup, ensure this stack exists:

- `.domus/memory/state.md`
- `.domus/memory/inbox.md`
- `.domus/memory/shared.md`
- `.domus/memory/handoffs.md`
- `.domus/memory/archive/`
- `.domus/memory/agents/`

When delegating, update `.domus/memory/inbox.md` with owner, status, context, expected output, blocker, and next action before the specialist starts. Update `.domus/memory/state.md` with the current focus, open tasks, blockers, and agent status.

After meaningful work, update `state.md` and `inbox.md` first, then append a concise entry to `.domus/memory/handoffs.md` with:

- Timestamp
- Platform if known
- Agent name
- Task
- Actions taken
- Files touched
- Status
- Blocker
- Next agent/action

Update `.domus/memory/shared.md` only for durable facts, decisions, conventions, and explicit user preferences.

Do not store secrets, credentials, tokens, private personal data, or noisy transient logs. Keep `state.md` and `inbox.md` compact; use `handoffs.md` as append-only history and `.domus/memory/archive/` for old log chunks.
