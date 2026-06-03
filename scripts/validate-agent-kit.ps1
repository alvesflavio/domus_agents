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

function Get-Frontmatter([string]$text, [string]$field) {
  $m = [regex]::Match($text, "(?m)^$field`:\s+(.+?)\s*$")
  if ($m.Success) { return $m.Groups[1].Value } else { return $null }
}

# Cross-platform parity: every Claude agent must have a Codex skill with the
# same name and an identical description, so routing triggers the same agent on
# both platforms.
foreach ($file in $claudeAgents) {
  $name = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
  $skill = Join-Path $codexDir (Join-Path $name "SKILL.md")
  if (-not (Test-Path $skill)) {
    throw "Claude agent '$name' has no matching Codex skill at codex-skills\$name\SKILL.md"
  }
  $claudeDesc = Get-Frontmatter (Get-Content -Raw -Path $file.FullName) "description"
  $codexDesc = Get-Frontmatter (Get-Content -Raw -Path $skill) "description"
  if ($claudeDesc -ne $codexDesc) {
    throw "Description mismatch for '$name' between Claude agent and Codex skill. Regenerate with scripts/generate-agent-kit.py."
  }
}

if ($claudeAgents.Count -ne $codexSkills.Count) {
  throw "Agent count mismatch: $($claudeAgents.Count) Claude agents vs $($codexSkills.Count) Codex skills."
}

Write-Output "OK: $($claudeAgents.Count) Claude agents and $($codexSkills.Count) Codex skills validated (descriptions in parity)."
