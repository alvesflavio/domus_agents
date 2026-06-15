# Domus Inbox

Active task queue for cross-agent work. Agents should read this before `handoffs.md`.

## Open Tasks

### TASK-20260615-002 | status: in_progress | owner: security-reviewer (bartolomeu_security)
- Requested by: workstyle-standards-coordinator (pedro_CTO)
- Platform: Claude Code
- Summary: Security audit do console Streamlit e coletor com foco em SQL injection, subprocess injection e exposição de DATABASE_URL.
- Files/areas: console/db.py, scripts/agent-usage.py, console/pages/agent_manager.py
- Expected output: findings com severidade + fixes aplicados para alta, documentados para média/baixa.
- Blocker: None
- Updated: 2026-06-15T15:00:00Z

### TASK-20260615-003 | status: in_progress | owner: code-reviewer (tome_reviewer)
- Requested by: workstyle-standards-coordinator (pedro_CTO)
- Platform: Claude Code
- Summary: Verificar compatibilidade Postgres do DbCompat — fetchone() indexing, params style, transação sem rollback em exceção.
- Files/areas: scripts/agent-usage.py (DbCompat, file_changed, report, connect)
- Expected output: findings + fixes aplicados para issues que quebram Postgres.
- Blocker: None
- Updated: 2026-06-15T15:00:00Z

### TASK-20260615-004 | status: queued | owner: implementation-planner (tiago_planner)
- Requested by: workstyle-standards-coordinator (pedro_CTO)
- Platform: Claude Code
- Summary: Planejar e implementar custo estimado em USD por invocação no console.
- Context: console/db.py tem todos os tokens + model por linha de token_usage. A tabela de preços está em console/pages/settings.py. Precisa cruzar os dois e adicionar coluna `estimated_cost_usd` ou calculá-la on-the-fly nas queries.
- Files/areas: console/db.py, console/pages/dashboard.py, console/pages/agent_detail.py, console/pages/settings.py
- Expected output: custo em USD visível no dashboard e no detalhe de agent.
- Blocker: aguardar TASK-20260615-002 e 003 finalizarem para não conflitar em arquivos.
- Updated: 2026-06-15T15:00:00Z

### TASK-20260615-005 | status: queued | owner: implementation-planner (tiago_planner)
- Requested by: workstyle-standards-coordinator (pedro_CTO)
- Platform: Claude Code
- Summary: Implementar alertas de threshold no coletor (cache hit < 70%, spike de tokens/invocação > 50% vs média histórica, agents inativos há 30 dias).
- Context: scripts/agent-usage.py já tem a lógica de collect; alertas podem ser warnings no terminal ou gravados numa tabela `alerts` no banco.
- Files/areas: scripts/agent-usage.py, opcionalmente console/pages/settings.py para configurar thresholds.
- Expected output: alertas impressos no final do `collect` + visíveis na tela de Configurações.
- Blocker: aguardar TASK-20260615-002 e 003.
- Updated: 2026-06-15T15:00:00Z

### TASK-20260615-006 | status: queued | owner: software-architect (joao_arquiteto)
- Requested by: workstyle-standards-coordinator (pedro_CTO)
- Platform: Claude Code
- Summary: Projetar agent versioning — gravar snapshot da spec ao fazer deploy pelo console, correlacionar mudanças de spec com mudanças de eficiência.
- Context: console/pages/agent_manager.py já tem o pipeline gerar/validar/implantar. Falta registrar o "antes e depois" no banco para análise histórica.
- Files/areas: console/pages/agent_manager.py, console/db.py, scripts/agent-usage.py (schema)
- Expected output: design de tabela `agent_versions` + plano de implementação (não implementar ainda).
- Blocker: None
- Updated: 2026-06-15T15:00:00Z

## Recently Completed

### TASK-20260615-001 | status: done | owner: workstyle-standards-coordinator
- Requested by: user
- Platform: Codex
- Summary: Created Neon project and wired Domus Console localhost integration.
- Result: Neon project `domus-agents` created; schema applied; console and collector use `DATABASE_URL` when present and SQLite fallback otherwise; Streamlit verified at localhost.
- Blocker: None
- Updated: 2026-06-15T14:44:46Z

### TASK-20260615-007 | status: done | owner: workstyle-standards-coordinator (pedro_CTO)
- Requested by: user
- Platform: Claude Code
- Summary: Aplicar machine_id ao coletor e schemas + corrigir print de destino.
- Result: MACHINE_ID gerado em ~/.domus/machine_id (UUID persistente); adicionado às tabelas invocations e token_usage com DEFAULT 'local'; migrations idempotentes (SQLITE/POSTGRES_MIGRATIONS) aplicadas no connect(); print do collect agora mostra destino real (neon: ou sqlite:) e machine_id.
- Files: scripts/agent-usage.py
- Updated: 2026-06-15T15:00:00Z

### TASK-20260609-001 | status: done | owner: workstyle-standards-coordinator
- Requested by: user
- Platform: Codex
- Summary: Implemented low-token Domus memory stack and updated agents globally.
- Result: Added `state.md`, `inbox.md`, `archive/`, compact read order, and coordinator-owned stack initialization instructions; regenerated, validated, and globally deployed agents.
- Blocker: None
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
