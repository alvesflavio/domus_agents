# Domus State

Compact current snapshot for low-token cross-agent continuity. Agents should read this before `handoffs.md`.

- Last update: 2026-06-15T15:00:00Z
- Current focus: Aplicando roadmap de gestão do Domus Console pós-integração Neon.
- Active coordinator: workstyle-standards-coordinator (pedro_CTO)
- Open tasks: TASK-20260615-002 (security, in_progress), TASK-20260615-003 (code review, in_progress), TASK-20260615-004 (custo USD, queued), TASK-20260615-005 (alertas, queued), TASK-20260615-006 (agent versioning design, queued)
- Blockers: TASK-004 e 005 aguardam conclusão de 002 e 003 para evitar conflito de arquivos.

## Agent Status

- workstyle-standards-coordinator: active (coordenando)
- security-reviewer: active (TASK-002)
- code-reviewer: active (TASK-003)
- software-architect: queued (TASK-006)
- implementation-planner: queued (TASK-004, TASK-005)
- product-strategist: idle
- ux-ui-designer: idle
- copy-strategist: idle
- devops-release-manager: idle
- task-ops-manager: idle
- test-debugger: idle

## Notes

- Neon project `domus-agents` (`muddy-hat-61615284`) conectado via `.env.local` (não commitado).
- machine_id implementado em scripts/agent-usage.py — UUID gerado em ~/.domus/machine_id, gravado em invocations e token_usage.
- console/db.py usa SQLAlchemy; scripts/agent-usage.py usa psycopg direto — divergência intencional pelo Codex, ambos funcionam.
