# Domus Shared Agent Instructions

This project uses Domus shared memory so Claude Code and Codex agents can continue each other's work.

## Shared Memory Protocol

Before delegated, cross-agent, continuation, coordination, planning, review, or debugging work, read:

- `.domus/memory/handoffs.md` for the latest agent actions, current task state, blockers, and requested next agent.
- `.domus/memory/shared.md` for durable project facts, decisions, conventions, and user preferences.
- `.domus/memory/agents/<agent-name>.md` when it exists for specialist-specific context.

If a user says an agent assigned, handed off, continued, remembered, or queued work, inspect shared memory before acting.

After meaningful work, append a concise entry to `.domus/memory/handoffs.md` with:

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

Do not store secrets, credentials, tokens, private personal data, or noisy transient logs.
