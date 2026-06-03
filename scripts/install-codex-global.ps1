# Install Domus Agents skills globally for Codex

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$codexDir = Join-Path $repoRoot "codex-skills"
$globalCodexDir = Join-Path $HOME ".codex\skills"

Write-Output "Installing Domus Agents for Codex..."
Write-Output ""

# Create global codex skills directory
Write-Output "Creating $globalCodexDir..."
New-Item -ItemType Directory -Force -Path $globalCodexDir > $null

# Copy all skills
Write-Output "Copying skills..."
Get-ChildItem -Path $codexDir -Directory | ForEach-Object {
  $skillName = $_.Name
  $skillDir = Join-Path $globalCodexDir $skillName
  New-Item -ItemType Directory -Force -Path $skillDir > $null

  $skillMd = Join-Path $_.FullName "SKILL.md"
  if (Test-Path $skillMd) {
    Copy-Item $skillMd (Join-Path $skillDir "SKILL.md") -Force
    Write-Output "  OK: $skillName"
  }
}

Write-Output ""
Write-Output "Done! Codex skills installed globally."
Write-Output "Location: $globalCodexDir"
Write-Output ""
Write-Output "Start a new Codex session to discover the skills."
