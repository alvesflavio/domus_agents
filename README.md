# Domus Agents

Domus Agents is a portable specialist-agent kit for Claude Code and Codex.

It includes a lean startup-style agent team with:

- A default coordinator/router for complex work
- Product, architecture, UX/UI, copy, security, DevOps, planning, task ops, code review, and debugging specialists
- Equivalent Claude subagents and Codex skills
- A shared token-efficiency protocol
- A `specialist_name: TODO` field in every agent so each specialist can receive a character/person name without changing its technical routing name

## Structure

- `specs/agents.yaml`: canonical source of truth.
- `specs/token-efficiency.md`: shared context and token budget protocol.
- `claude-agents/*.md`: Claude Code subagents.
- `codex-skills/*/SKILL.md`: Codex skills.
- `scripts/validate-agent-kit.ps1`: basic local validation.
- `INSTALL.md`: installation instructions.

## Core Team

- `workstyle-standards-coordinator`: default coordinator and router
- `product-strategist`: product strategy and MVP scope
- `software-architect`: architecture and technical decisions
- `ux-ui-designer`: flows, screens, UI, accessibility
- `copy-strategist`: product copy and messaging
- `security-reviewer`: security review and remediation
- `devops-release-manager`: Git, CI/CD, deployments, releases
- `task-ops-manager`: Notion and GitHub Projects task operations
- `implementation-planner`: implementation planning
- `code-reviewer`: code quality review
- `test-debugger`: failing tests and runtime debugging

## Naming Characters

Each agent includes:

```yaml
specialist_name: TODO
```

Replace `TODO` with the character name you want. Keep the technical `name` unchanged because Claude and Codex use it for routing.
