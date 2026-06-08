# Setup git hooks for Windows
$ErrorActionPreference = "Stop"

$repoRoot = git rev-parse --show-toplevel
$hooksDir = "$repoRoot\.git\hooks"
$preCommitHook = Join-Path $hooksDir "pre-commit"

Write-Output "Setting up git hooks for automatic agent deployment..."

# Configure git
git config core.hooksPath .git/hooks

New-Item -ItemType Directory -Force -Path $hooksDir > $null

$hookContent = @'
#!/bin/bash
# Git pre-commit hook: auto-regenerate generated agents if specs/agents.yaml changed.

set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"
SPEC_FILE="$REPO_ROOT/specs/agents.yaml"
CLAUDE_DIR="$REPO_ROOT/claude-agents"
CODEX_SKILLS_DIR="$REPO_ROOT/codex-skills"
CODEX_AGENTS_DIR="$REPO_ROOT/.codex/agents"

if git diff --name-only --cached | grep -q "^specs/agents.yaml$" || \
   git diff --name-only | grep -q "^specs/agents.yaml$"; then
  echo "specs/agents.yaml changed, regenerating agents..."

  python "$REPO_ROOT/scripts/generate-agent-kit.py" || {
    echo "Generation failed"
    exit 1
  }

  powershell -File "$REPO_ROOT/scripts/validate-agent-kit.ps1" || {
    echo "Validation failed"
    exit 1
  }

  git add "$CLAUDE_DIR"/*.md "$CODEX_SKILLS_DIR"/*/SKILL.md "$CODEX_AGENTS_DIR"/*.toml "$SPEC_FILE"
  echo "Agents regenerated and staged"
fi

exit 0
'@

Set-Content -Path $preCommitHook -Value $hookContent -Encoding ASCII

Write-Output "Git hooks configured"
Write-Output ""
Write-Output "Next commit with specs/agents.yaml changes:"
Write-Output "  1. Hook regenerates agents"
Write-Output "  2. Validates both platforms"
Write-Output "  3. Auto-stages everything"
Write-Output "  4. Commit proceeds"
