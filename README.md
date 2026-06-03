# Domus Agents

Domus Agents is a portable specialist-agent kit for Claude Code and Codex.

It includes a lean startup-style agent team with:

- A default coordinator/router for complex work
- Product, architecture, UX/UI, copy, security, DevOps, planning, task ops, code review, and debugging specialists
- **Both Claude Code subagents AND Codex skills**, fully synchronized
- Per-agent model selection (Opus for complex, Sonnet for general, Haiku for simple)
- A shared token-efficiency protocol
- Automatic deployment via git hooks
- A `specialist_name: TODO` field in every agent so each specialist can receive a character/person name without changing its technical routing name

## Structure

- `specs/agents.yaml`: canonical source of truth.
- `specs/token-efficiency.md`: shared context and token budget protocol.
- `claude-agents/*.md`: Claude Code subagents (generated).
- `codex-skills/*/SKILL.md`: Codex skills (generated).
- `scripts/generate-agent-kit.py`: generates both platform outputs from `specs/agents.yaml`.
- `scripts/validate-agent-kit.ps1`: local validation, including cross-platform description parity.
- `INSTALL.md`: installation instructions.

## Uniform Claude + Codex

Both platforms are generated from one spec so each specialist behaves identically:

- Same `description` (so routing triggers the same agent on both platforms).
- Same body: identity, role, and structured sections.
- Only the frontmatter differs, because each platform requires a different shape (Claude declares `tools`/`model`; Codex adds an H1 title).

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

## Two Platforms

- **Claude Code**: Agents available via `@agent-name` (globally installed)
- **Codex**: Skills available via `/skill-name` (fully synchronized)

Both platforms stay in sync automatically. See `CODEX-INTEGRATION.md` for Codex setup.

## Naming Characters

Each agent includes:

```yaml
specialist_name: TODO
```

Replace `TODO` with the character name you want. Keep the technical `name` unchanged because Claude and Codex use it for routing.
