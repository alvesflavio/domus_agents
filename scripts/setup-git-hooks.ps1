# Setup git hooks for Windows
$ErrorActionPreference = "Stop"

$repoRoot = git rev-parse --show-toplevel
$hooksDir = "$repoRoot\.git\hooks"

Write-Output "Setting up git hooks for automatic agent deployment..."

# Configure git
git config core.hooksPath .git/hooks

Write-Output "Git hooks configured"
Write-Output ""
Write-Output "Next commit with specs/agents.yaml changes:"
Write-Output "  1. Hook regenerates agents"
Write-Output "  2. Validates both platforms"
Write-Output "  3. Auto-stages everything"
Write-Output "  4. Commit proceeds"
