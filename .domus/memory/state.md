# Domus State

Compact current snapshot for low-token cross-agent continuity. Agents should read this before `handoffs.md`.

- Last update: 2026-06-15T16:30:00Z
- Current focus: Agent versioning implementation (TASK-006 design completo, aguarda implementação).
- Active coordinator: workstyle-standards-coordinator (pedro_CTO)
- Open tasks: TASK-20260615-006 (agent versioning, design done → aguarda implementação)
- Blockers: Nenhum bloqueador ativo.

## Completed This Session

- TASK-002 (security): done — bartolomeu_security aplicou fixes (subprocess injection, DATABASE_URL redaction, SQL param safety)
- TASK-003 (code review): done — tome_reviewer corrigiu DbCompat + Postgres compat
- TASK-004 (custo USD): done — MODEL_PRICES, estimated_cost(), cost_by_agent() em db.py; KPIs de custo no dashboard e agent_detail. Commit: 1753043
- TASK-005 (alertas threshold): done — _check_thresholds() em agent-usage.py; threshold_alerts() em db.py; seção "Alertas" em settings.py
- TASK-006 design: done — joao_arquiteto (software-architect) entregou design completo de agent_versions (tabela, captura, correlação, UI spec)

## Agent Status

- workstyle-standards-coordinator: active (coordenando)
- software-architect: design entregue (TASK-006)
- todos os outros: idle

## Notes

- Neon project `domus-agents` (`muddy-hat-61615284`) conectado via `.env.local` (não commitado).
- machine_id implementado em scripts/agent-usage.py — UUID gerado em ~/.domus/machine_id, gravado em invocations e token_usage.
- console/db.py usa SQLAlchemy; scripts/agent-usage.py usa psycopg direto — divergência intencional pelo Codex, ambos funcionam.
- TASK-006 design: tabela agent_versions (SQLite + Postgres), record_agent_version() em db.py, snapshot em run_pipeline(), query de correlação (vigência por versão, portável), aba "Histórico de versões" em agent_detail.py.
