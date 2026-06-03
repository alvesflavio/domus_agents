# Automatic Agent Deployment

This project includes full automation for keeping Claude Code and Codex agents in sync.

## How It Works

**Three layers of automation:**

1. **Git pre-commit hook** — When you stage a change to `specs/agents.yaml`, the hook automatically regenerates and stages the agent files. This ensures consistency in every commit.

2. **Claude Code file-modified hook** — When you edit `specs/agents.yaml` in Claude Code, the hook automatically:
   - Regenerates agents
   - Validates
   - Deploys to Claude Code + Codex

3. **Deploy script** — Manual fallback. Run once to sync everything.

## Setup

### Enable Git Hook (one-time)

Make the pre-commit hook executable (on macOS/Linux):
```bash
chmod +x .git/hooks/pre-commit
```

On Windows, Git uses the `.git/hooks/pre-commit` file as-is (or `pre-commit.ps1` if configured for PowerShell).

**Verify the hook is installed:**
```bash
ls -la .git/hooks/pre-commit
```

### Enable Claude Code Hook (one-time)

The `.claude/settings.json` includes a `file-modified` hook that triggers on `specs/agents.yaml`. This is pre-configured and requires no additional setup. Just edit the YAML and Claude Code will run the deploy sequence automatically.

## Usage

### Option 1: Edit Spec, Let Automation Run (Recommended)

1. Edit `specs/agents.yaml` (e.g., update an agent's description or sections)
2. Save the file

**What happens automatically:**

- **In Claude Code:** The file-modified hook detects the change and runs `deploy-agents.ps1`
- **At git commit time:** The pre-commit hook regenerates + validates + stages everything
- **Result:** Claude Code and Codex agents stay in sync, no manual steps

### Option 2: Manual Deploy

If automation didn't trigger (or you prefer explicit control):

```powershell
powershell -File scripts/deploy-agents.ps1
```

This script:
1. Regenerates agents from `specs/agents.yaml`
2. Validates both platforms
3. Deploys to `.claude/agents/` (Claude Code)
4. Deploys to `$HOME\.codex\skills/` (Codex)
5. Shows a summary

### Option 3: Manual Regenerate Only (Dev/Testing)

If you just want to regenerate without deploying:

```powershell
python scripts/generate-agent-kit.py
powershell -File scripts/validate-agent-kit.ps1
```

Then manually copy agents as needed.

## Workflow Example

**Scenario:** You want to add a new section to the `code-reviewer` agent.

1. Edit `specs/agents.yaml` → find `code-reviewer` → add a new `heading`/`body` pair
2. Save the file
3. **Claude Code hook triggers:**
   - `python scripts/generate-agent-kit.py` ✓
   - `powershell -File scripts/validate-agent-kit.ps1` ✓
   - `powershell -File scripts/deploy-agents.ps1` ✓
4. Both platforms are now in sync
5. Restart Claude Code session (agents auto-discovered)
6. Start a new Codex session (skills auto-discovered)

## What Gets Automated

| Step | Git Hook | Claude Hook | Deploy Script |
|------|----------|-------------|---------------|
| Regenerate | ✓ | ✓ | ✓ |
| Validate | ✓ | ✓ | ✓ |
| Deploy to Claude Code | ✗ | ✓ | ✓ |
| Deploy to Codex | ✗ | ✓ | ✓ |
| Stage for commit | ✓ | ✗ | ✗ |

## Troubleshooting

### Hook didn't run after editing `specs/agents.yaml`

**Git pre-commit hook (at commit time):**
- Ensure `.git/hooks/pre-commit` exists and is executable
- On Windows, git may need to be configured to use hooks (usually auto-detected)

**Claude Code file-modified hook:**
- Make sure `.claude/settings.json` exists in the repo root
- Restart Claude Code if the file was just created
- Check that the pattern `specs/agents.yaml` matches exactly

### Agent changes didn't deploy to Codex

The Claude Code hook runs the deploy script, which:
- Copies agents to `$HOME\.codex\skills/` (user scope)
- Does NOT restart Codex automatically

**Action:** Start a new Codex session so it discovers the updated skills.

### Git hook is blocking my commit

If the hook fails:
1. Run `powershell -File scripts/validate-agent-kit.ps1` manually to see the error
2. Fix the YAML or re-run `python scripts/generate-agent-kit.py`
3. Try committing again

## Files Involved

- **Generator:** `scripts/generate-agent-kit.py` (reads YAML, writes both platforms)
- **Validator:** `scripts/validate-agent-kit.ps1` (checks frontmatter + parity)
- **Deployer:** `scripts/deploy-agents.ps1` (copies to `.claude/agents/` and Codex)
- **Git hook:** `.git/hooks/pre-commit` (bash) or `.git/hooks/pre-commit.ps1` (PowerShell)
- **Claude hook:** `.claude/settings.json` (file-modified trigger)

## Notes

- **Do not edit** `claude-agents/*.md` or `codex-skills/*/SKILL.md` by hand; they are generated.
- **Always edit** `specs/agents.yaml` as the source of truth.
- **One spec, two platforms:** Same description and body, only frontmatter differs.
- Automation is optional — you can always run scripts manually if needed.
