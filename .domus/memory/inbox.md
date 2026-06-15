# Domus Inbox

Active task queue for cross-agent work. Agents should read this before `handoffs.md`.

## Open Tasks

### TASK-20260615-006-IMPL | status: queued | owner: pedro_CTO (aguarda aprovação)
- Requested by: workstyle-standards-coordinator (pedro_CTO)
- Platform: Claude Code
- Summary: Implementar agent versioning conforme design de joao_arquiteto.
- Context: Design completo em `.domus/memory/handoffs.md` (entrada TASK-006 design). Tabela `agent_versions` (SQLite + Postgres), `record_agent_version()` em db.py, snapshot em run_pipeline(), aba "Histórico de versões" em agent_detail.py. Riscos documentados: R1 (timestamp format), R5 (concorrência Neon), R7 (new_name session_state).
- Files/areas: scripts/agent-usage.py (schemas + migrations), console/db.py (escrita + versioning), console/pages/agent_manager.py (run_pipeline), console/pages/agent_detail.py (nova aba)
- Expected output: Deploy via console grava versão; agent_detail mostra histórico e correlação de eficiência.
- Blocker: Aguarda aprovação do usuário.
- Updated: 2026-06-15T16:30:00Z

## Recently Completed

### TASK-20260615-005 | status: done | owner: pedro_CTO
- Summary: Alertas de threshold no coletor e no console.
- Result: `_check_thresholds()` em scripts/agent-usage.py (cache hit <70%, spike tok/inv >50%, inactive 30d); `threshold_alerts()` em console/db.py; seção "Alertas de threshold" em console/pages/settings.py.
- Files: scripts/agent-usage.py, console/db.py, console/pages/settings.py
- Updated: 2026-06-15T16:30:00Z

### TASK-20260615-006 | status: done (design) | owner: software-architect (joao_arquiteto)
- Summary: Design de agent versioning entregue.
- Result: Design completo — tabela agent_versions, record_agent_version(), _diff_summary(), query de correlação (Opção A: vigência por versão), UI spec (4 blocos na aba "Histórico de versões"). Ver handoffs.md para o design completo.
- Updated: 2026-06-15T16:30:00Z

### TASK-20260615-004 | status: done | owner: pedro_CTO
- Summary: Custo estimado USD no dashboard e agent_detail.
- Result: MODEL_PRICES, estimated_cost(), cost_by_agent() em console/db.py; 7 KPIs em dashboard.py (incluindo custo); 7 KPIs em agent_detail.py. Commit: 1753043.
- Updated: 2026-06-15T16:00:00Z

### TASK-20260615-002 | status: done | owner: security-reviewer (bartolomeu_security)
- Summary: Security audit — subprocess injection, DATABASE_URL redaction, SQL params.
- Result: Fixes aplicados em console/db.py (_redact_url), console/pages/settings.py (_sanitize_output), console/pages/agent_manager.py (subprocess path safety).
- Updated: 2026-06-15T15:00:00Z

### TASK-20260615-003 | status: done | owner: code-reviewer (tome_reviewer)
- Summary: Compatibilidade Postgres do DbCompat.
- Result: rollback() adicionado ao DbCompat, try/except por-arquivo em collect(), bug 4a/4b/4c corrigidos.
- Updated: 2026-06-15T15:00:00Z

### TASK-20260615-001 | status: done | owner: workstyle-standards-coordinator
- Summary: Neon project criado e integrado ao Domus Console.
- Result: Neon `domus-agents` (muddy-hat-61615284); schema aplicado; console + coletor usam DATABASE_URL com SQLite fallback.
- Updated: 2026-06-15T14:44:46Z

### TASK-20260615-007 | status: done | owner: pedro_CTO
- Summary: machine_id no coletor e schemas.
- Result: UUID gerado em ~/.domus/machine_id; migrations idempotentes; print do collect mostra destino real.
- Updated: 2026-06-15T15:00:00Z

### TASK-20260609-001 | status: done | owner: workstyle-standards-coordinator
- Summary: Low-token Domus memory stack implementado e agents atualizados globalmente.
- Updated: 2026-06-09T02:40:48Z

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
