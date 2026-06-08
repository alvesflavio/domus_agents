# Quick Start: Automated Agent Deployment

## One-Time Setup

Run once to enable automation:

```powershell
powershell -File scripts/setup-git-hooks.ps1
```

This configures git to automatically regenerate agents on every commit.

## Your Workflow

### Option 1: Automatic (Recommended)

```bash
# 1. Edit specs/agents.yaml (e.g., update a specialist's description)
nano specs/agents.yaml

# 2. Commit normally
git add specs/agents.yaml
git commit -m "Update code-reviewer agent description"

# 3. Git hook automatically:
#    - Regenerates all 33 generated files
#    - Validates both platforms
#    - Auto-stages the changes
#    - Commit succeeds with synchronized agents
```

**That's it!** Both Claude Code and Codex agents are in sync automatically.

### Option 2: Manual Deploy (Fallback)

If you need to sync without committing:

```powershell
powershell -File scripts/deploy-agents.ps1
```

This regenerates, validates, and deploys to both platforms in one shot.

## What Happens Behind the Scenes

**At commit time, the git pre-commit hook:**

1. Detects changes to `specs/agents.yaml`
2. Runs: `python scripts/generate-agent-kit.py` (regenerate)
3. Runs: `powershell -File scripts/validate-agent-kit.ps1` (validate)
4. Auto-stages the generated `claude-agents/*.md`, `codex-skills/*/SKILL.md`, and `.codex/agents/*.toml`
5. Commit proceeds with everything in sync

**Result:** Every commit ensures Claude Code and Codex agents are identical.

## Files to Know

- **Source of truth:** `specs/agents.yaml` (edit this)
- **Generated Claude agents:** `claude-agents/*.md` (auto-generated, don't edit)
- **Generated Codex skills:** `codex-skills/*/SKILL.md` (auto-generated, don't edit)
- **Generated Codex agents:** `.codex/agents/*.toml` (auto-generated, don't edit)
- **Git hook:** `.git/hooks/pre-commit` (runs on every commit)
- **Deployment script:** `scripts/deploy-agents.ps1` (manual fallback)

## Customization

To customize the character names (e.g., "specialist_name: Claude"):

1. Edit `specs/agents.yaml`
2. Change `specialist_name: TODO` to your preferred name in `defaults:`
3. Commit -> hook regenerates all agents with the new name

## Troubleshooting

**Hook didn't run?**

1. Ensure `core.hooksPath` is set: `git config core.hooksPath`
2. Re-run setup: `powershell -File scripts/setup-git-hooks.ps1`
3. Try committing again

**Manual regenerate needed?**

```powershell
python scripts/generate-agent-kit.py
powershell -File scripts/validate-agent-kit.ps1
powershell -File scripts/deploy-agents.ps1
```

## Next: Use the Agents

After setup, restart Claude Code and start a new Codex session so they discover the agents. The default entry point is `workstyle-standards-coordinator`; it will route you to the right specialist for any task.

## Optional: Shared Memory In A Project

To let Claude and Codex agents continue each other's work inside a project:

```powershell
powershell -File scripts\init-shared-memory.ps1 -ProjectRoot C:\path\to\project
```

Agents will use `.domus/memory/handoffs.md` for the latest actions and `.domus/memory/shared.md` for durable project context.

For the lowest token cost, initialize this once per project, usually through `workstyle-standards-coordinator` when you ask it to prepare shared agent memory.
