# Install Domus Agents globally for all Claude Code projects

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$claudeDir = Join-Path $repoRoot "claude-agents"
$globalAgentsDir = Join-Path $HOME ".claude\agents"

Write-Output "Installing Domus Agents globally..."
Write-Output ""

# Create global agents directory
Write-Output "Creating $globalAgentsDir..."
New-Item -ItemType Directory -Force -Path $globalAgentsDir > $null

# Copy all agents
Write-Output "Copying agents..."
Get-ChildItem -Path $claudeDir -Filter "*.md" -File | ForEach-Object {
  Copy-Item $_.FullName (Join-Path $globalAgentsDir $_.Name) -Force
  Write-Output "  OK: $($_.Name)"
}

Write-Output ""
Write-Output "Done! Agents installed globally."
Write-Output "Location: $globalAgentsDir"
Write-Output ""
Write-Output "Restart Claude Code to discover agents in all projects."
