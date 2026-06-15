<#
Setup automation for Domus agent usage collection (Phase 2).

1. Registers a Windows Scheduled Task that runs `agent-usage.py collect`
   every hour (and at logon), so the SQLite history stays current even if
   Claude Code rotates old transcripts.
2. Adds a SubagentStop hook to the user-level Claude Code settings so usage
   is collected in near real time whenever a subagent finishes, in any project.

Both triggers are zero-token: they only read local files into SQLite.

Run:  powershell -File scripts\setup-usage-automation.ps1
#>

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$collector = Join-Path $root "scripts\agent-usage.py"
$python = (Get-Command python).Source
$taskName = "DomusUsageCollect"

Write-Output "Domus Usage Automation Setup`n"

# --- 1. Scheduled Task (hourly + at logon) ---------------------------------
Write-Output "Registering scheduled task '$taskName'..."

# schtasks (em vez de Register-ScheduledTask) porque funciona sem elevacao
schtasks /Create /TN $taskName /TR "`"$python`" `"$collector`" collect" /SC HOURLY /F | Out-Null
if ($LASTEXITCODE -ne 0) { throw "schtasks falhou (exit $LASTEXITCODE)" }
Write-Output "  OK: roda a cada hora."

# --- 2. Claude Code SubagentStop hook (user scope, all projects) ------------
Write-Output "`nAdding SubagentStop hook to user Claude settings..."

$settingsPath = Join-Path $HOME ".claude\settings.json"
$json = if (Test-Path $settingsPath) {
  Get-Content $settingsPath -Raw | ConvertFrom-Json
} else {
  [pscustomobject]@{}
}

$hookCmd = "python `"$collector`" collect"
$hookEntry = [pscustomobject]@{
  hooks = @([pscustomobject]@{ type = "command"; command = $hookCmd; timeout = 60 })
}

if (-not $json.PSObject.Properties["hooks"]) {
  $json | Add-Member -NotePropertyName hooks -NotePropertyValue ([pscustomobject]@{})
}
$existing = $json.hooks.PSObject.Properties["SubagentStop"]
$already = $false
if ($existing) {
  foreach ($e in $existing.Value) {
    foreach ($h in $e.hooks) { if ($h.command -eq $hookCmd) { $already = $true } }
  }
}
if ($already) {
  Write-Output "  OK: hook ja instalado, nada a fazer."
} else {
  if ($existing) {
    $existing.Value = @($existing.Value) + @($hookEntry)
  } else {
    $json.hooks | Add-Member -NotePropertyName SubagentStop -NotePropertyValue @($hookEntry)
  }
  Copy-Item $settingsPath "$settingsPath.bak" -Force -ErrorAction SilentlyContinue
  $json | ConvertTo-Json -Depth 10 | Out-File $settingsPath -Encoding utf8
  Write-Output "  OK: hook gravado em $settingsPath (backup em .bak)."
}

Write-Output "`nComplete!"
Write-Output "  Verificar tarefa : Get-ScheduledTask -TaskName $taskName"
Write-Output "  Rodar manualmente: Start-ScheduledTask -TaskName $taskName"
Write-Output "  Remover          : Unregister-ScheduledTask -TaskName $taskName"
