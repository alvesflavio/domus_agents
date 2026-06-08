# Domus Agent Handoffs

Append newest entries at the top of the log. Keep entries compact and factual.

## Log

### 2026-06-08T03:30:00Z | platform: Claude Code | agent: workstyle-standards-coordinator

- Task: Divide agents between Claude and Codex only (no Antigravity assignments yet).
- Actions: Added `platforms` field support to `generate-agent-kit.py`; assigned `platforms: [claude]` to 5 deep-reasoning agents and `platforms: [codex]` to 6 execution/product agents in `specs/agents.yaml`; regenerated all outputs; removed orphaned files; updated `shared.md` with the durable decision.
- Files touched: `scripts/generate-agent-kit.py`, `specs/agents.yaml`, `claude-agents/` (5 kept, 6 removed), `codex-skills/` (6 kept, 5 removed), `.codex/agents/` (6 kept, 5 removed), `antigravity-agents/` (removed entirely), `.domus/memory/shared.md`, `.domus/memory/handoffs.md`.
- Status: done.
- Blocker: None.
- Next agent/action: If Antigravity gets agents assigned, add `platforms: [antigravity]` entries in `specs/agents.yaml` and re-run the generator.

### 2026-06-08T03:00:00Z | platform: Claude Code | agent: workstyle-standards-coordinator

- Task: Add Antigravity platform support so agents stay uniform across Claude Code, Codex, and Antigravity.
- Actions: Added `render_antigravity()` to `generate-agent-kit.py` (YAML frontmatter with `platform: antigravity`); updated `expected_outputs()` to write `antigravity-agents/<name>.md`; regenerated all 11 agents; updated `specs/agents.yaml` header and `shared_memory_note`; updated README, INSTALL, AUTOMATION, and `shared.md`.
- Files touched: `scripts/generate-agent-kit.py`, `specs/agents.yaml`, `antigravity-agents/*.md` (11 new), `README.md`, `INSTALL.md`, `AUTOMATION.md`, `.domus/memory/shared.md`, `.domus/memory/handoffs.md`.
- Status: done.
- Blocker: None.
- Next agent/action: If Antigravity uses a different install path than `$HOME\.antigravity\agents`, update `INSTALL.md` accordingly.

### 2026-06-08T02:31:26Z | platform: Codex | agent: Codex

- Task: Apply apostle-inspired persona names to all agents.
- Actions: Added per-agent `specialist_name` values for all 11 agents, expanded README rationale for each apostolic persona, updated quick-start customization docs, regenerated generated outputs, deployed to Claude/Codex locations, and validated generated parity.
- Files touched: `specs/agents.yaml`, `README.md`, `QUICK-START.md`, `claude-agents/*`, `codex-skills/*/SKILL.md`, `.codex/agents/*.toml`, `.claude/agents/*`, `.domus/memory/shared.md`, `.domus/memory/handoffs.md`.
- Status: done.
- Blocker: None.
- Next agent/action: Continue calling agents by technical names; personas are in `specialist_name`.

### 2026-06-08T01:55:50Z | platform: Codex | agent: Codex

- Task: Make coordinator persona name configurable without changing behavior.
- Actions: Set `workstyle-standards-coordinator` `specialist_name` to `wojtyla_CTO`, documented per-agent naming configuration, regenerated generated outputs, and validated parity.
- Files touched: `specs/agents.yaml`, `claude-agents/workstyle-standards-coordinator.md`, `codex-skills/workstyle-standards-coordinator/SKILL.md`, `.codex/agents/workstyle-standards-coordinator.toml`, `README.md`, `QUICK-START.md`, `.domus/memory/shared.md`, `.domus/memory/handoffs.md`.
- Status: done.
- Blocker: None.
- Next agent/action: Use `specialist_name` for persona names; keep technical `name` fields stable for routing.

### 2026-06-08T01:53:19Z | platform: Codex | agent: Codex

- Task: Record user-defined agent name.
- Actions: Added durable naming convention that `workstyle-standards-coordinator` is named `wojtyla_CTO`.
- Files touched: `.domus/memory/shared.md`, `.domus/memory/handoffs.md`.
- Status: done.
- Blocker: None.
- Next agent/action: Use `wojtyla_CTO` when referring to `workstyle-standards-coordinator`.

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
