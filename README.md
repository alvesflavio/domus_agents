# Domus Agents

Domus Agents is a portable specialist-agent kit for Claude Code and Codex.

It includes a lean startup-style agent team with:

- A default coordinator/router for complex work
- Product, architecture, UX/UI, copy, security, DevOps, planning, task ops, code review, and debugging specialists
- **Claude Code subagents, Codex skills, Codex agents, and Antigravity agents**, fully synchronized
- Per-agent model selection (Opus for complex, Sonnet for general, Haiku for simple)
- A shared token-efficiency protocol
- Project-local shared memory for Claude/Codex handoffs
- Automatic deployment via git hooks
- A configurable `specialist_name` field so each specialist can receive a character/person name without changing its technical routing name

## Structure

- `specs/agents.yaml`: canonical source of truth.
- `specs/token-efficiency.md`: shared context and token budget protocol.
- `claude-agents/*.md`: Claude Code subagents (generated).
- `codex-skills/*/SKILL.md`: Codex skills (generated).
- `.codex/agents/*.toml`: Codex agents (generated).
- `antigravity-agents/*.md`: Antigravity agents (generated).
- `scripts/generate-agent-kit.py`: generates all platform outputs from `specs/agents.yaml`.
- `scripts/validate-agent-kit.ps1`: local validation, including cross-platform description parity.
- `scripts/init-shared-memory.ps1`: initializes project-local Claude/Codex shared memory.
- `SHARED-MEMORY.md`: shared memory protocol and handoff format.
- `INSTALL.md`: installation instructions.

## Uniform Across Platforms

All platforms are generated from one spec so each specialist behaves identically:

- Same `description` (so routing triggers the same agent on every platform).
- Same body: identity, role, and structured sections.
- Only the frontmatter differs per platform: Claude declares `tools`/`model`; Codex adds an H1 title; Antigravity adds `platform: antigravity`.

Do not edit the generated files by hand. Edit `specs/agents.yaml` and automation takes care of the rest:

- **Git pre-commit hook**: Auto-regenerates agents when you commit `specs/agents.yaml` changes
- **Claude Code file-modified hook**: Auto-deploys when you save `specs/agents.yaml`
- **Deploy script**: Manual fallback: `powershell -File scripts/deploy-agents.ps1`

For full details, see `AUTOMATION.md`.

## Core Team

- `workstyle-standards-coordinator`: default coordinator and router (Opus)
- `product-strategist`: product strategy and MVP scope
- `software-architect`: architecture and technical decisions (Opus)
- `ux-ui-designer`: flows, screens, UI, accessibility
- `copy-strategist`: product copy and messaging (Haiku)
- `security-reviewer`: security review and remediation
- `devops-release-manager`: Git, CI/CD, deployments, releases
- `task-ops-manager`: Notion and GitHub Projects task operations
- `implementation-planner`: implementation planning (Opus)
- `code-reviewer`: code quality review
- `test-debugger`: failing tests and runtime debugging (Haiku)

## Three Platforms

- **Claude Code**: Agents available via `@agent-name` (globally installed)
- **Codex**: Agents available globally plus skills available via `/skill-name` (fully synchronized)
- **Antigravity**: Agents installed from `antigravity-agents/*.md` (fully synchronized)

All three platforms stay in sync automatically — same `description`, same body, only the frontmatter differs. See `CODEX-INTEGRATION.md` for Codex setup and `INSTALL.md` for Antigravity setup.

## Shared Memory

To let Claude Code, Codex, and Antigravity agents see each other's last action inside a project, initialize Domus shared memory in that project:

```powershell
powershell -File scripts\init-shared-memory.ps1 -ProjectRoot C:\path\to\project
```

This creates `AGENTS.md`, `CLAUDE.md`, and `.domus/memory/`. Agents use `.domus/memory/handoffs.md` as the cross-platform action log and `.domus/memory/shared.md` for durable project facts. See `SHARED-MEMORY.md`.

For token efficiency, shared memory is initialized on demand by `workstyle-standards-coordinator` or by the script above. Other specialists consume existing memory instead of checking and creating the structure on every task.

The memory stack is optimized for low token usage: agents read `.domus/memory/state.md` and `.domus/memory/inbox.md` first, use `.domus/memory/shared.md` for durable context, and only open the full `.domus/memory/handoffs.md` history when the compact files are insufficient or history is explicitly requested.

## Naming Characters

Each agent includes:

```yaml
specialist_name: TODO
```

Set `defaults.specialist_name` to apply the same character name to every agent, or set `specialist_name` on one agent to override only that specialist. Keep the technical `name` unchanged because Claude and Codex use it for routing.

For Codex agent TOML files, the generator also writes `display_name = "<specialist_name>"` as an experimental UI hint. Keep `name` stable; whether `display_name` appears in Codex Desktop's Subagents list depends on Codex Desktop support for that field.

## Apostolic Persona Map

The default persona names are inspired by the traditional personalities and narrative roles of Jesus' apostles. These names are intentionally stored in `specialist_name`, not in the technical `name`, so they shape identity without changing routing, tools, model selection, or behavior.

| Technical agent | Persona name | Rationale |
| --- | --- | --- |
| `workstyle-standards-coordinator` | `pedro_CTO` | Peter is the natural coordinator figure: direct, visible, responsible for holding the group together, and often the first to act. That maps well to the default entry point that classifies work, routes specialists, owns standards, and makes practical coordination calls. |
| `product-strategist` | `andre_produto` | Andrew is remembered as someone who brings people and opportunities forward, including introducing others to Jesus. That fits product strategy: noticing needs, connecting the user's problem to the right opportunity, and turning early signals into a focused product direction. |
| `software-architect` | `joao_arquiteto` | John is the most contemplative and theologically deep of the apostolic voices. That fits architecture work because it needs long-range thinking, pattern recognition, conceptual clarity, and the patience to design structure rather than only react to the immediate task. |
| `ux-ui-designer` | `filipe_UX` | Philip often asks for what can be seen and made concrete. That fits UX/UI because the role translates abstract goals into visible screens, flows, states, hierarchy, and interactions users can actually understand and complete. |
| `copy-strategist` | `judas_tadeu_copy` | Jude/Thaddeus is associated with a clarifying question that asks why something is revealed to some and not others. That maps to copy work: audience awareness, clear messaging, removing ambiguity, and making intent understandable in the user's language. |
| `security-reviewer` | `bartolomeu_security` | Bartholomew is traditionally identified with Nathanael, described as a person without deceit. That makes him a strong fit for security review, where integrity, trust boundaries, hidden assumptions, and false confidence matter more than surface polish. |
| `devops-release-manager` | `tiago_release` | James son of Zebedee is forceful, decisive, and associated with bold action. That fits release and incident work, where the agent must inspect operational state, make controlled decisions under pressure, preserve rollback paths, and keep delivery moving. |
| `task-ops-manager` | `mateus_ops` | Matthew's background as a tax collector suggests records, ledgers, traceability, and administrative discipline. That fits task operations across Notion, GitHub Projects, issues, statuses, owners, blockers, and next actions. |
| `implementation-planner` | `tiago_planner` | James son of Alphaeus is quieter and less narratively prominent, which fits a planning role that should be careful, structured, and useful without taking over implementation. The persona reinforces low-drama sequencing, assumptions, risks, and verification steps. |
| `code-reviewer` | `tome_reviewer` | Thomas asks for evidence before accepting a claim. That is exactly the stance of a strong code reviewer: skeptical, concrete, grounded in changed behavior, and unwilling to approve vague reasoning without proof. |
| `test-debugger` | `simao_debugger` | Simon the Zealot suggests persistence, intensity, and commitment to a cause. That fits debugging: staying with failures, isolating root cause, testing hypotheses, and pushing through noisy logs or flaky behavior until the issue is understood. |

`judas_iscariotes` is intentionally not used for a standard operating agent. If the kit later adds an adversarial red-team, abuse-case, or betrayal-mode reviewer, that symbolism could fit there without making it part of the normal delivery team.
