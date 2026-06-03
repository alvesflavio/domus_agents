# Codex Integration Guide

The Domus Agents team is available in **both Claude Code and Codex**, fully synchronized.

## Installation

### One-Time Setup

```powershell
powershell -File scripts/install-codex-global.ps1
```

This installs all 11 agent skills globally for Codex. They become available in **all Codex sessions**.

## Using the Skills in Codex

### Start a New Codex Session

After installation, start a new Codex session. The 11 skills will be discoverable:

```
@workstyle-standards-coordinator
@product-strategist
@software-architect
@ux-ui-designer
@copy-strategist
@security-reviewer
@devops-release-manager
@task-ops-manager
@implementation-planner
@code-reviewer
@test-debugger
```

### Example: Use in Codex

```
You: "Help me write a product spec"
→ @product-strategist
→ [Product Strategist analyzes and delivers spec]

---

You: "Review this code for security risks"
→ @security-reviewer
→ [Security Reviewer audits and reports findings]

---

You: "I'm not sure how to structure this. Route me to the right expert."
→ @workstyle-standards-coordinator
→ [Coordinator classifies task and delegates to specialist]
```

## Key Differences: Claude Code vs Codex

| Aspect | Claude Code | Codex |
|--------|------------|-------|
| **Invocation** | `@agent-name` | `/skill-name` or `/s` |
| **Model selection** | Per-agent configuration | Uses Codex default |
| **Installation** | `scripts/install-global.ps1` | `scripts/install-codex-global.ps1` |
| **Location** | `$HOME/.claude/agents/` | `$HOME/.codex/skills/` |
| **Auto-sync** | Via git pre-commit hook | Via deploy script |

## Keeping Codex in Sync

The git pre-commit hook **automatically regenerates** the Codex skills when you commit changes to `specs/agents.yaml`. Just run the deploy script to copy to Codex:

```powershell
# After git commit
powershell -File scripts/install-codex-global.ps1
```

Or combine both in one command:

```powershell
python scripts/generate-agent-kit.py
powershell -File scripts/validate-agent-kit.ps1
powershell -File scripts/deploy-agents.ps1
powershell -File scripts/install-codex-global.ps1
```

## Model Selection in Codex

Each skill inherits Codex's default model settings. If you want per-skill models in Codex, configure Codex's skill routing (varies by Codex version).

For Claude Code, model selection is built-in per agent.

## Troubleshooting

**Skills not appearing in Codex?**

1. Ensure installation completed: `powershell -File scripts/install-codex-global.ps1`
2. Check location: `$HOME/.codex/skills/` (should contain 11 subdirectories)
3. Restart Codex session (skills are discovered on session start)

**Skills are outdated?**

The git pre-commit hook regenerates Codex skills automatically. After commit:

```powershell
powershell -File scripts/install-codex-global.ps1
```

Then start a new Codex session.

## Unified Workflow

You now have **one team of 11 specialists** available across:

- **Claude Code** — Full per-agent model control
- **Codex** — Consistent skill interface

Both platforms stay synchronized automatically via git hooks and deploy scripts.

Edit `specs/agents.yaml` once, and both Claude Code and Codex pick up the changes.
