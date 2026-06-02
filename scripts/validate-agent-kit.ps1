$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$spec = Join-Path $root "specs\agents.yaml"
$claudeDir = Join-Path $root "claude-agents"
$codexDir = Join-Path $root "codex-skills"

if (-not (Test-Path $spec)) {
  throw "Missing specs\agents.yaml"
}

$claudeAgents = Get-ChildItem -Path $claudeDir -Filter "*.md" -File
if ($claudeAgents.Count -eq 0) {
  throw "No Claude agent files found"
}

foreach ($file in $claudeAgents) {
  $text = Get-Content -Raw -Path $file.FullName
  if (-not $text.StartsWith("---`n") -and -not $text.StartsWith("---`r`n")) {
    throw "Claude agent missing YAML frontmatter: $($file.Name)"
  }
  if ($text -notmatch "(?m)^name:\s+[a-z0-9-]+$") {
    throw "Claude agent missing valid name: $($file.Name)"
  }
  if ($text -notmatch "(?m)^description:\s+.+$") {
    throw "Claude agent missing description: $($file.Name)"
  }
}

$codexSkills = Get-ChildItem -Path $codexDir -Filter "SKILL.md" -File -Recurse
if ($codexSkills.Count -eq 0) {
  throw "No Codex SKILL.md files found"
}

foreach ($file in $codexSkills) {
  $text = Get-Content -Raw -Path $file.FullName
  if (-not $text.StartsWith("---`n") -and -not $text.StartsWith("---`r`n")) {
    throw "Codex skill missing YAML frontmatter: $($file.FullName)"
  }
  if ($text -notmatch "(?m)^name:\s+[a-z0-9-]+$") {
    throw "Codex skill missing valid name: $($file.FullName)"
  }
  if ($text -notmatch "(?m)^description:\s+.+$") {
    throw "Codex skill missing description: $($file.FullName)"
  }
}

Write-Output "OK: $($claudeAgents.Count) Claude agents and $($codexSkills.Count) Codex skills validated."
