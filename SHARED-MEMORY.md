# Domus Shared Memory

Domus shared memory is a project-local handoff layer for Claude Code and Codex agents.

It is designed for this workflow:

1. A Claude agent records what it did and which agent should continue.
2. A Codex agent starts in the same project, reads the latest handoff, and understands why the task was assigned.
3. Codex records its result, blocker, or next delegation.
4. Claude can later read the same memory and continue without relying on chat history.

This is not raw chat history. It is a compact, auditable project memory that lives with the repository.

## Project Layout

Run this inside each project where you want Claude and Codex to share state:

```powershell
powershell -File scripts\init-shared-memory.ps1 -ProjectRoot C:\path\to\project
```

The script creates or updates:

- `AGENTS.md`: shared instructions loaded by Codex and imported by Claude.
- `CLAUDE.md`: imports `AGENTS.md` for Claude Code.
- `.domus/memory/shared.md`: durable facts, decisions, conventions, and explicit user preferences.
- `.domus/memory/handoffs.md`: chronological agent action and delegation log.
- `.domus/memory/agents/`: optional specialist-specific memory files.

## Handoff Contract

Every meaningful handoff entry should include:

- Timestamp
- Platform if known
- Agent name
- Task
- Actions taken
- Files touched
- Status
- Blocker
- Next agent/action

Example:

```md
### 2026-06-08T14:40:00Z | platform: Claude Code | agent: workstyle-standards-coordinator

- Task: Prepare Codex to review the shared-memory implementation.
- Actions: Added shared memory protocol to `specs/agents.yaml` and regenerated agents.
- Files touched: `specs/agents.yaml`, `scripts/generate-agent-kit.py`.
- Status: in-progress.
- Blocker: None.
- Next agent/action: `code-reviewer` in Codex should review generated output and validation coverage.
```

## Agent Behavior

All generated Domus agents include the same shared-memory instruction:

- Read `.domus/memory/handoffs.md` before delegated, cross-agent, continuation, coordination, planning, review, or debugging work.
- Read `.domus/memory/shared.md` for durable project context.
- Read `.domus/memory/agents/<agent-name>.md` when agent-specific context exists.
- Append to `handoffs.md` after meaningful work, blockers, decisions, or delegation.
- Update `shared.md` only for durable information.

Only `workstyle-standards-coordinator` owns initialization. When the user asks to prepare or enable shared memory for a project, the coordinator should run `scripts\init-shared-memory.ps1` for the target project, or create the same minimal structure manually if the script is unavailable. Other specialists should use the memory when it exists, but should not initialize it for unrelated one-off tasks.

## Safety Rules

Do not write these into shared memory:

- Secrets, API keys, tokens, passwords, private keys, or credentials.
- Private personal data.
- Large logs or raw command output.
- Temporary speculation that will confuse future agents.

Keep entries concise. The goal is continuity, not transcript storage.
