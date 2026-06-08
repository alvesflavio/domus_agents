# Domus Shared Memory

Durable project context shared by Claude Code and Codex agents.

## Project Facts

- Add stable architecture, domain, workflow, and repository facts here.

## Decisions

- Domus shared memory is project-local under `.domus/memory/`, so Claude Code, Codex, and Antigravity agents working in the same repository can read and update the same handoff state.
- `AGENTS.md` is the shared instruction entry point; `CLAUDE.md` imports it with `@AGENTS.md` so Claude Code, Codex, and Antigravity follow the same project-memory protocol.
- `.domus/memory/handoffs.md` is the cross-platform action log (Claude Code, Codex, Antigravity); `.domus/memory/shared.md` is reserved for durable facts, decisions, conventions, and explicit user preferences.
- Antigravity agents are generated from `specs/agents.yaml` to `antigravity-agents/*.md` using YAML frontmatter (`name`, `description`, `model`, `platform: antigravity`) and the same shared body as Claude and Codex. No hand-editing of generated files.
- Record decisions that future agents should not re-litigate without new evidence.
- Agents are divided by platform strength: Claude gets the 5 deep-reasoning specialists (coordinator, architect, implementation-planner, security-reviewer, code-reviewer); Codex gets the 6 execution/product specialists (devops-release-manager, test-debugger, task-ops-manager, product-strategist, ux-ui-designer, copy-strategist). Antigravity is supported by the generator but not yet assigned agents. The `platforms` field in `specs/agents.yaml` controls this — omitting it defaults to all platforms.

## User Preferences

- Record durable working preferences only when the user explicitly states them or repeatedly corrects the agents.

## Conventions

- Record project-specific commands, naming, review, testing, and deployment conventions.
- Agent persona naming uses apostle-inspired `specialist_name` values; keep technical routing names unchanged. Current map: `workstyle-standards-coordinator` -> `pedro_CTO`, `product-strategist` -> `andre_produto`, `software-architect` -> `joao_arquiteto`, `ux-ui-designer` -> `filipe_UX`, `copy-strategist` -> `judas_tadeu_copy`, `security-reviewer` -> `bartolomeu_security`, `devops-release-manager` -> `tiago_release`, `task-ops-manager` -> `mateus_ops`, `implementation-planner` -> `tiago_planner`, `code-reviewer` -> `tome_reviewer`, `test-debugger` -> `simao_debugger`.
