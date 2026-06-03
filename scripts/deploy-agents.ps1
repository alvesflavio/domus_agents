<#
Deploy Domus Agents to Claude Code and Codex
#>

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$claudeDir = Join-Path $root "claude-agents"
$codexDir = Join-Path $root "codex-skills"
$projectAgentsDir = Join-Path (Join-Path $root ".claude") "agents"
$userCodexDir = Join-Path $HOME ".codex\skills"

Write-Output "Domus Agents Deploy`n"

# Regenerate
Write-Output "Regenerating..."
python (Join-Path $root "scripts\generate-agent-kit.py")

# Validate
Write-Output "`nValidating..."
powershell -File (Join-Path $root "scripts\validate-agent-kit.ps1")

# Deploy to Claude Code
Write-Output "`nDeploying to Claude Code..."
New-Item -ItemType Directory -Force -Path $projectAgentsDir > $null
Get-ChildItem -Path $claudeDir -Filter "*.md" -File | ForEach-Object {
  Copy-Item $_.FullName (Join-Path $projectAgentsDir $_.Name) -Force
  Write-Output "  OK: $($_.Name)"
}

# Deploy to Codex
Write-Output "`nDeploying to Codex..."
New-Item -ItemType Directory -Force -Path $userCodexDir > $null
Get-ChildItem -Path $codexDir -Directory | ForEach-Object {
  $skillDir = Join-Path $userCodexDir $_.Name
  New-Item -ItemType Directory -Force -Path $skillDir > $null
  $skillMd = Join-Path $_.FullName "SKILL.md"
  if (Test-Path $skillMd) {
    Copy-Item $skillMd (Join-Path $skillDir "SKILL.md") -Force
    Write-Output "  OK: $($_.Name)"
  }
}

Write-Output "`nComplete! Restart Claude Code and Codex sessions."
