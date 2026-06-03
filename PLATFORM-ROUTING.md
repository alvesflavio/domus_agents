# Platform Routing Guide

When to use Claude Code vs Codex for each specialist.

## Quick Reference

| Specialist | Claude Code | Codex |
|------------|-------------|-------|
| **workstyle-standards-coordinator** | Complex routing | Quick coordination |
| **product-strategist** | Strategy docs | Quick feedback |
| **software-architect** | Detailed designs | Architecture sketches |
| **ux-ui-designer** | Full flow design | Quick UI critique |
| **copy-strategist** | Brand voice, long copy | Microcopy, quick fixes |
| **security-reviewer** | Deep security audits | Quick threat check |
| **devops-release-manager** | Complex deployments | Troubleshooting |
| **task-ops-manager** | Full task management | Quick updates |
| **implementation-planner** | Detailed plans | Quick sequencing |
| **code-reviewer** | Thorough reviews | Quick feedback |
| **test-debugger** | Root cause analysis | Quick fixes |

## When to Use Each Platform

### Claude Code (Opus/Sonnet/Haiku Models)
- **When**: Deep analysis needed, complex decisions, detailed planning
- **Why**: Full context, specialized models per agent, multi-file analysis
- **Example**: "Architect a complex migration" → `@software-architect` (Claude Code)

### Codex (Single Platform)
- **When**: Quick feedback, iteration speed, conversational flow
- **Why**: Integrated IDE experience, immediate feedback
- **Example**: "Quick copy fix" → `/copy-strategist` (Codex)

## Workflow Examples

### Example 1: Product Feature (Both Platforms)

```
Claude Code:
  @product-strategist → Define full spec, roadmap

Codex:
  /copy-strategist → Write landing page copy
  /ux-ui-designer → Iterate on UI feedback

Claude Code:
  @software-architect → Technical architecture
  @implementation-planner → Detailed implementation plan

Codex:
  /code-reviewer → Review implementation PRs
  /test-debugger → Help with test failures
```

### Example 2: Quick Bug Fix (Single Platform)

```
Claude Code (immediate deep dive):
  @test-debugger → Root cause analysis
  @code-reviewer → Review fix
  
OR

Codex (quick turnaround):
  /test-debugger → Quick diagnosis
  /code-reviewer → Quick feedback
```

### Example 3: Security Review (Deep Work)

```
Claude Code (Opus model):
  @security-reviewer → Full threat modeling
  @code-reviewer → Follow-up on fixes

Codex (if quick threat check needed):
  /security-reviewer → Preliminary review
```

## Decision Tree

```
Is this a quick task (< 5 min)?
├─ YES → Use Codex (/skill-name)
└─ NO → Is this strategic/complex?
    ├─ YES → Use Claude Code (@agent-name)
    └─ NO → Use Codex or your preference
```

## Key Insight

Both platforms have the same 11 specialists with identical training. The choice is about:

- **Claude Code**: Deep analysis, full context, specialized models
- **Codex**: Quick iteration, IDE integration, conversational flow

Pick the platform that matches your workflow speed. For large features, use Claude Code. For rapid feedback loops, use Codex. For enterprise-grade decisions, use Claude Code.

## Switching Between Platforms

You don't need to leave either platform:

- In **Claude Code**: Get feedback, then switch to Codex for implementation notes
- In **Codex**: Get quick direction, then switch to Claude Code for deep work

The specialists are **fully synchronized** across platforms via git hooks, so they always have the latest training and reasoning.
