# Portable Agent Kit

This kit keeps one canonical agent spec and provides platform-specific files for Claude Code and Codex.

## Files

- `specs/agents.yaml`: shared source of truth.
- `specs/token-efficiency.md`: shared token/context budget protocol.
- `claude-agents/*.md`: Claude Code subagents.
- `codex-skills/*/SKILL.md`: Codex skills with equivalent behavior.

## Included Agents

- `software-architect`: architecture, boundaries, tradeoffs, migrations.
- `product-strategist`: product strategy, MVP scope, prioritization, requirements, experiments.
- `copy-strategist`: product copy, microcopy, messaging.
- `ux-ui-designer`: flows, screens, accessibility, UI ergonomics.
- `security-reviewer`: practical security review and remediation.
- `task-ops-manager`: Notion and GitHub Projects task operations.
- `devops-release-manager`: Git, CI/CD, deployments, releases, rollback, environment problems.
- `workstyle-standards-coordinator`: default coordinator for routing tasks to specialists, reusable project standards, and workflow coordination.
- `code-reviewer`: implementation review.
- `test-debugger`: failing tests and runtime errors.
- `implementation-planner`: scoped implementation planning.

## Install For Claude Code

Project scope:

```powershell
New-Item -ItemType Directory -Force -Path .claude\agents
Copy-Item outputs\portable-agent-kit\claude-agents\*.md .claude\agents\
```

User scope:

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\agents"
Copy-Item outputs\portable-agent-kit\claude-agents\*.md "$HOME\.claude\agents\"
```

Restart Claude Code after manual file changes if the agents were not created through `/agents`.

## Install For Codex

User scope:

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.codex\skills"
Copy-Item -Recurse outputs\portable-agent-kit\codex-skills\* "$HOME\.codex\skills\"
```

Then start a new Codex session so the skills are discoverable.

## Add A New Agent

1. Add it to `specs/agents.yaml`.
2. Create one `claude-agents/<name>.md` file with the same `name`, `description`, tool list, and prompt body.
3. Create one `codex-skills/<name>/SKILL.md` with the same behavior as Codex skill instructions.
4. Keep the `description` explicit because both systems use it to decide when to invoke the agent or skill.

## Name The Characters

Each agent file includes:

```yaml
specialist_name: TODO
```

Replace `TODO` with the character/person name you want to use. Keep the technical `name` unchanged because Claude and Codex use it for routing.
