# Automatic Agent Deployment

This project includes full automation for keeping Claude Code and Codex agents in sync.

## How It Works

**Three layers of automation:**

1. **Git pre-commit hook** - When you stage a change to `specs/agents.yaml`, the hook automatically regenerates, validates, and stages generated agent files.
2. **Claude Code file-modified hook** - When you edit `specs/agents.yaml` in Claude Code, the hook automatically regenerates, validates, and deploys to Claude Code and Codex.
3. **Deploy script** - Manual fallback. Run once to sync everything.

## Setup

### Enable Git Hook (one-time)

```powershell
powershell -File scripts/setup-git-hooks.ps1
```

This configures Git to use `.git/hooks` and writes the current `pre-commit` hook.

**Verify the hook is installed:**

```bash
ls -la .git/hooks/pre-commit
```

On Windows, Git uses the `.git/hooks/pre-commit` file as-is.

### Enable Claude Code Hook (one-time)

The `.claude/settings.json` includes a `file-modified` hook that triggers on `specs/agents.yaml`. This is pre-configured and requires no additional setup. Edit the YAML and Claude Code will run the deploy sequence automatically.

## Usage

### Option 1: Edit Spec, Let Automation Run (Recommended)

1. Edit `specs/agents.yaml`, such as updating an agent description or section.
2. Save the file.

**What happens automatically:**

- **In Claude Code:** The file-modified hook detects the change and runs `deploy-agents.ps1`.
- **At git commit time:** The pre-commit hook regenerates, validates, and stages everything.
- **Result:** Claude Code and Codex agents stay in sync.

### Option 2: Manual Deploy

If automation did not trigger, or you prefer explicit control:

```powershell
powershell -File scripts/deploy-agents.ps1
```

This script:

1. Regenerates agents from `specs/agents.yaml`.
2. Validates both platforms.
3. Deploys to `.claude/agents/` for Claude Code.
4. Deploys to `$HOME\.codex\skills/` and `$HOME\.codex\agents/` for Codex.
5. Shows a summary.

### Option 3: Manual Regenerate Only (Dev/Testing)

If you just want to regenerate without deploying:

```powershell
python scripts/generate-agent-kit.py
powershell -File scripts/validate-agent-kit.ps1
```

Then manually copy agents as needed.

## Workflow Example

**Scenario:** You want to add a new section to the `code-reviewer` agent.

1. Edit `specs/agents.yaml` -> find `code-reviewer` -> add a new `heading`/`body` pair.
2. Save the file.
3. **Claude Code hook triggers:**
   - `python scripts/generate-agent-kit.py` OK
   - `powershell -File scripts/validate-agent-kit.ps1` OK
   - `powershell -File scripts/deploy-agents.ps1` OK
4. Both platforms are now in sync.
5. Restart Claude Code session so agents are discovered.
6. Start a new Codex session so agents and skills are discovered.

## What Gets Automated

| Step | Git Hook | Claude Hook | Deploy Script |
|------|----------|-------------|---------------|
| Regenerate | Yes | Yes | Yes |
| Validate | Yes | Yes | Yes |
| Deploy to Claude Code | No | Yes | Yes |
| Deploy to Codex | No | Yes | Yes |
| Stage for commit | Yes | No | No |

## Troubleshooting

### Hook did not run after editing `specs/agents.yaml`

**Git pre-commit hook (at commit time):**

- Ensure `.git/hooks/pre-commit` exists.
- Ensure `git config core.hooksPath` returns `.git/hooks`.
- Re-run `powershell -File scripts/setup-git-hooks.ps1`.

**Claude Code file-modified hook:**

- Make sure `.claude/settings.json` exists in the repo root.
- Restart Claude Code if the file was just created.
- Check that the pattern `specs/agents.yaml` matches exactly.

### Agent changes did not deploy to Codex

The Claude Code hook runs the deploy script, which:

- Copies Codex skills to `$HOME\.codex\skills/`.
- Copies Codex agents to `$HOME\.codex\agents/`.
- Does not restart Codex automatically.

**Action:** Start a new Codex session so it discovers the updated agents and skills.

### Git hook is blocking my commit

If the hook fails:

1. Run `powershell -File scripts/validate-agent-kit.ps1` manually to see the error.
2. Fix the YAML or re-run `python scripts/generate-agent-kit.py`.
3. Try committing again.

## Files Involved

- **Generator:** `scripts/generate-agent-kit.py` reads YAML and writes all generated outputs.
- **Validator:** `scripts/validate-agent-kit.ps1` checks generated sync, frontmatter, TOML shape, and parity.
- **Deployer:** `scripts/deploy-agents.ps1` copies to `.claude/agents/` and Codex user directories.
- **Git hook installer:** `scripts/setup-git-hooks.ps1` writes `.git/hooks/pre-commit`.
- **Git hook:** `.git/hooks/pre-commit`.
- **Claude hook:** `.claude/settings.json` file-modified trigger.

## Notes

- **Do not edit** `claude-agents/*.md`, `codex-skills/*/SKILL.md`, or `.codex/agents/*.toml` by hand; they are generated.
- **Always edit** `specs/agents.yaml` as the source of truth.
- **One spec, two platforms:** Same description and body, platform-specific wrapper.
- Automation is optional; you can always run scripts manually if needed.
