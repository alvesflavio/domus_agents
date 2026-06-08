# Domus Agent Handoffs

Append newest entries at the top of the log. Keep entries compact and factual.

## Log

### 2026-06-08T01:44:37Z | platform: Codex | agent: workstyle-standards-coordinator

- Task: Make shared-memory initialization token-efficient and coordinator-owned.
- Actions: Added a coordinator-only initialization rule, documented that other specialists consume existing memory instead of auto-initializing it, regenerated agent outputs, and validated generated parity.
- Files touched: `specs/agents.yaml`, `SHARED-MEMORY.md`, `README.md`, `QUICK-START.md`, generated coordinator outputs, generated shared-memory sections.
- Status: done.
- Blocker: None.
- Next agent/action: Commit the shared-memory integration changes.

### 2026-06-08T01:32:38Z | platform: Codex | agent: workstyle-standards-coordinator

- Task: Add project-local shared memory so Claude Code and Codex agents can hand off work.
- Actions: Added shared memory protocol to generated agents, created `scripts/init-shared-memory.ps1`, documented the workflow, regenerated all agent outputs, and initialized memory in this repository.
- Files touched: `specs/agents.yaml`, `scripts/generate-agent-kit.py`, `scripts/init-shared-memory.ps1`, `SHARED-MEMORY.md`, `README.md`, `INSTALL.md`, `QUICK-START.md`, `AGENTS.md`, `CLAUDE.md`, `.domus/memory/*`, generated agent outputs.
- Status: done.
- Blocker: None.
- Next agent/action: `code-reviewer` can review the shared-memory protocol and generated output before commit.

### 0000-00-00T00:00:00Z | platform: unknown | agent: example-agent

- Task: Example task title.
- Actions: Example action summary.
- Files touched: `path/to/file`.
- Status: pending | in-progress | blocked | done.
- Blocker: None.
- Next agent/action: `agent-name` should do the next concrete action.
