<#
Initialize Domus shared project memory in a target repository.

The memory lives inside the project that Claude Code and Codex will work on,
so both platforms can read the same handoff log and durable project context.
#>

param(
  [string]$ProjectRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

$resolvedRoot = (Resolve-Path -Path $ProjectRoot).Path
$memoryDir = Join-Path $resolvedRoot ".domus\memory"
$agentsMemoryDir = Join-Path $memoryDir "agents"
$archiveDir = Join-Path $memoryDir "archive"
$statePath = Join-Path $memoryDir "state.md"
$inboxPath = Join-Path $memoryDir "inbox.md"
$sharedPath = Join-Path $memoryDir "shared.md"
$handoffsPath = Join-Path $memoryDir "handoffs.md"
$archiveReadmePath = Join-Path $archiveDir "README.md"
$agentsReadmePath = Join-Path $agentsMemoryDir "README.md"
$agentsPath = Join-Path $resolvedRoot "AGENTS.md"
$claudePath = Join-Path $resolvedRoot "CLAUDE.md"

function Write-NewFileIfMissing([string]$Path, [string]$Content) {
  if (-not (Test-Path $Path)) {
    New-Item -ItemType File -Force -Path $Path > $null
    Set-Content -Path $Path -Value $Content -Encoding UTF8
    Write-Output "  created $Path"
  } else {
    Write-Output "  exists  $Path"
  }
}

function Add-SectionIfMissing([string]$Path, [string]$Marker, [string]$Content) {
  if (-not (Test-Path $Path)) {
    Set-Content -Path $Path -Value $Content -Encoding UTF8
    Write-Output "  created $Path"
    return
  }

  $existing = Get-Content -Raw -Path $Path
  if ($existing -notlike "*$Marker*") {
    Add-Content -Path $Path -Value "`n$Content" -Encoding UTF8
    Write-Output "  updated $Path"
  } else {
    Write-Output "  already configured $Path"
  }
}

Write-Output "Initializing Domus shared memory in $resolvedRoot"

New-Item -ItemType Directory -Force -Path $agentsMemoryDir > $null
New-Item -ItemType Directory -Force -Path $archiveDir > $null

$stateContent = @'
# Domus State

Compact current snapshot for low-token cross-agent continuity. Agents should read this before `handoffs.md`.

- Last update: 0000-00-00T00:00:00Z
- Current focus: None
- Active coordinator: None
- Open tasks: None
- Blockers: None

## Agent Status

- workstyle-standards-coordinator: idle
- product-strategist: idle
- software-architect: idle
- ux-ui-designer: idle
- copy-strategist: idle
- security-reviewer: idle
- devops-release-manager: idle
- task-ops-manager: idle
- implementation-planner: idle
- code-reviewer: idle
- test-debugger: idle

## Notes

- Keep this file short. Update it after delegation, completion, or blocker changes.
'@

$inboxContent = @'
# Domus Inbox

Active task queue for cross-agent work. Agents should read this before `handoffs.md`.

## Open Tasks

- None

## Task Format

```md
### TASK-YYYYMMDD-001 | status: queued | owner: agent-name

- Requested by: workstyle-standards-coordinator
- Platform: Claude Code | Codex | Antigravity | unknown
- Summary: One-line outcome.
- Context: Minimal context needed to act.
- Files/areas: Relevant paths or domains.
- Expected output: Concrete deliverable.
- Blocker: None
- Updated: 0000-00-00T00:00:00Z
```

Move completed task summaries to `handoffs.md` and keep only active work here.
'@

$sharedContent = @'
# Domus Shared Memory

Durable project context shared by Claude Code and Codex agents.

## Project Facts

- Add stable architecture, domain, workflow, and repository facts here.

## Decisions

- Record decisions that future agents should not re-litigate without new evidence.

## User Preferences

- Record durable working preferences only when the user explicitly states them or repeatedly corrects the agents.

## Conventions

- Record project-specific commands, naming, review, testing, and deployment conventions.
'@

$handoffsContent = @'
# Domus Agent Handoffs

Append newest entries at the top of the log. Keep entries compact and factual.

## Log

### 0000-00-00T00:00:00Z | platform: unknown | agent: example-agent

- Task: Example task title.
- Actions: Example action summary.
- Files touched: `path/to/file`.
- Status: pending | in-progress | blocked | done.
- Blocker: None.
- Next agent/action: `agent-name` should do the next concrete action.
'@

$agentsReadmeContent = @'
# Agent-Specific Memory

Use one file per specialist when context is useful only to that agent.

Examples:

- `workstyle-standards-coordinator.md`
- `software-architect.md`
- `code-reviewer.md`

Do not store secrets, credentials, tokens, private personal data, or noisy transient logs.
'@

$archiveReadmeContent = @'
# Domus Memory Archive

Store old `handoffs.md` chunks here when the active log becomes too large.

Suggested pattern:

- Keep compact current state in `../state.md`.
- Keep active tasks in `../inbox.md`.
- Keep only recent operational history in `../handoffs.md`.
- Move older history to files such as `handoffs-YYYY-MM.md`.

Do not archive secrets, credentials, private personal data, or noisy raw logs.
'@

$agentsContent = @'
# Domus Shared Agent Instructions

This project uses Domus shared memory so Claude Code and Codex agents can continue each other's work.

## Shared Memory Protocol

Before delegated, cross-agent, continuation, coordination, planning, review, or debugging work, read:

- `.domus/memory/state.md` for the current compact project snapshot.
- `.domus/memory/inbox.md` for active delegated tasks, owners, blockers, and next actions.
- `.domus/memory/shared.md` for durable project facts, decisions, conventions, and user preferences.
- `.domus/memory/agents/<agent-name>.md` when it exists for specialist-specific context.
- `.domus/memory/handoffs.md` only when state/inbox are insufficient or when the user asks for history.

If a user says an agent assigned, handed off, continued, remembered, or queued work, inspect shared memory before acting.

When `workstyle-standards-coordinator` is invoked for delegation, cross-agent continuation, or memory setup, ensure this stack exists:

- `.domus/memory/state.md`
- `.domus/memory/inbox.md`
- `.domus/memory/shared.md`
- `.domus/memory/handoffs.md`
- `.domus/memory/archive/`
- `.domus/memory/agents/`

When delegating, update `.domus/memory/inbox.md` with owner, status, context, expected output, blocker, and next action before the specialist starts. Update `.domus/memory/state.md` with the current focus, open tasks, blockers, and agent status.

After meaningful work, update `state.md` and `inbox.md` first, then append a concise entry to `.domus/memory/handoffs.md` with:

- Timestamp
- Platform if known
- Agent name
- Task
- Actions taken
- Files touched
- Status
- Blocker
- Next agent/action

Update `.domus/memory/shared.md` only for durable facts, decisions, conventions, and explicit user preferences.

Do not store secrets, credentials, tokens, private personal data, or noisy transient logs. Keep `state.md` and `inbox.md` compact; use `handoffs.md` as append-only history and `.domus/memory/archive/` for old log chunks.
'@

$lowTokenStackContent = @'
## Domus Low-Token Memory Stack

Before delegated, cross-agent, continuation, coordination, planning, review, or debugging work, read:

- `.domus/memory/state.md` for the current compact project snapshot.
- `.domus/memory/inbox.md` for active delegated tasks, owners, blockers, and next actions.
- `.domus/memory/shared.md` for durable project facts, decisions, conventions, and user preferences.
- `.domus/memory/agents/<agent-name>.md` when it exists for specialist-specific context.
- `.domus/memory/handoffs.md` only when state/inbox are insufficient or when the user asks for history.

When `workstyle-standards-coordinator` is invoked for delegation, cross-agent continuation, or memory setup, ensure this stack exists: `state.md`, `inbox.md`, `shared.md`, `handoffs.md`, `archive/`, and `agents/`. When delegating, update `inbox.md` and `state.md` before the specialist starts; after meaningful work, update compact memory first and append only a concise historical entry to `handoffs.md`.
'@

$claudeContent = @'
@AGENTS.md

## Claude Code

Follow the Domus shared memory protocol from `AGENTS.md`.
'@

Write-NewFileIfMissing $statePath $stateContent
Write-NewFileIfMissing $inboxPath $inboxContent
Write-NewFileIfMissing $sharedPath $sharedContent
Write-NewFileIfMissing $handoffsPath $handoffsContent
Write-NewFileIfMissing $archiveReadmePath $archiveReadmeContent
Write-NewFileIfMissing $agentsReadmePath $agentsReadmeContent
Add-SectionIfMissing $agentsPath "# Domus Shared Agent Instructions" $agentsContent
Add-SectionIfMissing $agentsPath "## Domus Low-Token Memory Stack" $lowTokenStackContent

if (-not (Test-Path $claudePath)) {
  Set-Content -Path $claudePath -Value $claudeContent -Encoding UTF8
  Write-Output "  created $claudePath"
} else {
  $claudeExisting = Get-Content -Raw -Path $claudePath
  if ($claudeExisting -notmatch '(?m)^@AGENTS\.md\s*$') {
    $updatedClaude = "@AGENTS.md`n`n" + $claudeExisting
    Set-Content -Path $claudePath -Value $updatedClaude -Encoding UTF8
    Write-Output "  updated $claudePath"
  } else {
    Write-Output "  already configured $claudePath"
  }
}

Write-Output ""
Write-Output "Done. Restart Claude Code and Codex sessions in this project so they load the shared memory instructions."
