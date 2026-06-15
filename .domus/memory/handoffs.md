# Domus Agent Handoffs

Append newest entries at the top of the log. Keep entries compact and factual.

## Log

### 2026-06-15T16:30:00Z | Claude Code | workstyle-standards-coordinator (pedro_CTO)
- Task: TASK-005 — alertas de threshold no coletor e console
- Actions: Adicionou `_check_thresholds()` em scripts/agent-usage.py (3 checks: cache hit <70%, spike tok/inv >50%, inactive 30d); `threshold_alerts()` em console/db.py reutilizando helpers existentes; seção "Alertas de threshold" em console/pages/settings.py.
- Files: scripts/agent-usage.py, console/db.py, console/pages/settings.py
- Status: done
- Next: TASK-006-IMPL (implementação de agent versioning) — aguarda aprovação do usuário.

### 2026-06-15T16:00:00Z | Claude Code | software-architect (joao_arquiteto)
- Task: TASK-006 design — agent versioning
- Actions: Design completo entregue: tabela `agent_versions` (SQLite + Postgres com UNIQUE(agent,version)), `record_agent_version()` + `_canonical_hash()` + `_exec()` + `version_efficiency()` em db.py, bloco de captura em run_pipeline() com try/except (deploy não quebra se gravar falhar), query de correlação portável SQLite/Postgres (Opção A: vigência por versão usando JOIN com próxima versão), UI spec em 4 blocos na aba "Histórico de versões" de agent_detail.py. Riscos documentados: R1 (ISO-8601 timezone), R3 (hash dedup), R5 (concorrência Neon), R7 (new_name fora do form). Não implementou — design only.
- Files: nenhum (output textual)
- Status: design done; implementação pendente (TASK-006-IMPL)
- Next: pedro_CTO despacha implementação quando aprovado pelo usuário.

### 2026-06-15T16:00:00Z | platform: Claude Code | agent: tome_reviewer

- Task: Postgres compatibility review of scripts/agent-usage.py — four specific risk areas (file_changed row access, report() placeholder/params, clear_file_rows single-element tuple, transaction safety).
- Actions: (1) Confirmed row[0]/row[1] in file_changed() is safe — psycopg3 fetchone() returns TupleRow, subscriptable by index. No change needed. (2) Confirmed ?->%s replacement in _postgres_sql() is correct for report() queries (max one ? per query, params is a list, psycopg3 accepts sequences). No change needed. (3) Confirmed (str(path),) 1-tuple in clear_file_rows() works correctly after ?->%s substitution. No change needed. (4) Found three transaction-safety bugs: (a) bare  in connect() migration loop leaves psycopg3 in InFailedSqlTransaction before the subsequent commit() — added con.rollback() in the except clause; (b) per-file block in collect() had no try/except, so any psycopg3 error (network drop, constraint) would kill the whole run with an unreadable error and leave ingested_files inconsistent — wrapped with try/except + con.rollback() + stderr warning; (c) DbCompat had no rollback() method — added it.
- Files touched: scripts/agent-usage.py.
- Status: done.
- Blocker: None.
- Next agent/action: None.

### 2026-06-15T15:30:00Z | platform: Claude Code | agent: bartolomeu_security

- Task: Security review of Domus Console (console/db.py, scripts/agent-usage.py, console/pages/agent_manager.py, .gitignore).
- Actions: Reviewed all files for SQL injection, command injection, credential leakage, and .gitignore adequacy. Applied two high-severity fixes: (1) added `_sanitize_output()` in settings.py to strip DATABASE_URL/postgresql:// from subprocess stderr before st.error(); (2) added `_redact_url()` in db.py wrapping _one/_all/_df to strip connection strings from SQLAlchemy exception messages before they reach Streamlit's traceback renderer.
- Files touched: console/db.py, console/pages/settings.py.
- Status: done.
- Blocker: None.
- Next agent/action: None — three medium/low findings documented for optional remediation.

### 2026-06-09T02:40:48Z | platform: Codex | agent: workstyle-standards-coordinator

- Task: Implement low-token Domus memory stack and deploy updated agents globally.
- Actions: Added compact memory files `state.md`, `inbox.md`, and `archive/`; updated shared memory instructions so agents read compact state/inbox before historical handoffs; made `workstyle-standards-coordinator` responsible for stack initialization and task queue updates when invoked for delegation or shared memory; regenerated and validated all generated agents; installed updated Claude and Codex agents globally and copied Antigravity agents globally; initialized the stack in `C:\dev\domus_agents` and `C:\dev\doulus_ai`.
- Files touched: `specs/agents.yaml`, `scripts/init-shared-memory.ps1`, `AGENTS.md`, `README.md`, `INSTALL.md`, `QUICK-START.md`, `SHARED-MEMORY.md`, generated agent outputs, `.domus/memory/state.md`, `.domus/memory/inbox.md`, `.domus/memory/archive/README.md`, `.domus/memory/shared.md`, `.domus/memory/handoffs.md`.
- Status: done.
- Blocker: None.
- Next agent/action: Restart Claude Code, Codex, and Antigravity sessions so the globally installed agents load the new compact memory protocol.

### 2026-06-08T00:00:00Z | platform: Claude Code | agent: pedro_CTO (workstyle-standards-coordinator)

- Task: Confirmar a validacao da memoria Domus compartilhada e os nomes dos 11 agentes registrados pelo Codex.
- Actions: Li a entrada mais recente do Codex (`2026-06-09T02:09:03Z`) e validei o roster completo. Os 11 agentes confirmados (tecnico -> persona): `workstyle-standards-coordinator` -> pedro_CTO; `product-strategist` -> andre_produto; `software-architect` -> joao_arquiteto; `ux-ui-designer` -> filipe_UX; `copy-strategist` -> judas_tadeu_copy; `security-reviewer` -> bartolomeu_security; `devops-release-manager` -> tiago_release; `task-ops-manager` -> mateus_ops; `implementation-planner` -> tiago_planner; `code-reviewer` -> tome_reviewer; `test-debugger` -> simao_debugger.
- Files touched: `.domus/memory/handoffs.md`.
- Status: done.
- Blocker: None.
- Next agent/action: Continuidade Codex <-> Claude Code validada com sucesso; nenhuma acao pendente.

### 2026-06-09T02:09:03Z | platform: Codex | agent: workstyle-standards-coordinator

- Task: Validate shared Domus memory with all registered agents.
- Actions: Registered the full agent roster for Claude Code validation: `workstyle-standards-coordinator` -> `pedro_CTO`; `product-strategist` -> `andre_produto`; `software-architect` -> `joao_arquiteto`; `ux-ui-designer` -> `filipe_UX`; `copy-strategist` -> `judas_tadeu_copy`; `security-reviewer` -> `bartolomeu_security`; `devops-release-manager` -> `tiago_release`; `task-ops-manager` -> `mateus_ops`; `implementation-planner` -> `tiago_planner`; `code-reviewer` -> `tome_reviewer`; `test-debugger` -> `simao_debugger`.
- Files touched: `.domus/memory/handoffs.md`.
- Status: done.
- Blocker: None.
- Next agent/action: User will ask Claude Code to read the latest Domus memory entry and confirm all 11 agents are present.

### 2026-06-09T02:05:26Z | platform: Codex | agent: workstyle-standards-coordinator

- Task: Test shared Domus memory visibility between Codex and Claude Code.
- Actions: Registered this deliberate test entry so the user can open Claude Code and ask for the latest memory record.
- Files touched: `.domus/memory/handoffs.md`.
- Status: done.
- Blocker: None.
- Next agent/action: User will ask Claude Code what the latest Domus memory entry is; Claude should report this timestamp and task.

### 2026-06-09T02:02:13Z | platform: Codex | agent: Codex

- Task: Run the latest Domus agents update across projects.
- Actions: Regenerated and validated the kit; installed Claude agents globally to `$HOME\.claude\agents`; installed Codex skills/agents globally to `$HOME\.codex`; copied Antigravity agents to `$HOME\.antigravity\agents`; updated local `.claude\agents` copies in existing Domus projects `C:\dev\domus_agents` and `C:\dev\doulus_ai`.
- Files touched: Global user agent directories; local `.claude\agents` in `C:\dev\doulus_ai`; generated files in this repo from regeneration; `.domus/memory/handoffs.md`.
- Status: done.
- Blocker: Codex Desktop may still ignore `display_name`; requires restart/new session to verify.
- Next agent/action: Restart Claude Code, Codex Desktop/session, and Antigravity sessions to reload global agents.

### 2026-06-09T01:47:10Z | platform: Codex | agent: Codex

- Task: Replicate custom display names for all Codex agents.
- Actions: Updated `scripts/generate-agent-kit.py` so every `.codex/agents/*.toml` includes `display_name = "<specialist_name>"`; regenerated all 11 agents; deployed updated Codex skills/agents to `$HOME\.codex`; documented the experimental UI hint in README and INSTALL; validated generated parity.
- Files touched: `scripts/generate-agent-kit.py`, `.codex/agents/*.toml`, `README.md`, `INSTALL.md`, `.domus/memory/handoffs.md`.
- Status: done.
- Blocker: Codex Desktop may ignore `display_name` if the runtime does not support custom Subagents labels.
- Next agent/action: Restart Codex Desktop/session and verify whether Subagents shows persona names; if ignored, the UI is runtime-controlled.

### 2026-06-09T01:41:52Z | platform: Codex | agent: Codex

- Task: Explore how user-defined agent names could appear in Codex Desktop Subagents UI.
- Actions: Inspected generated `.codex/agents/*.toml`, `specs/agents.yaml`, and `scripts/generate-agent-kit.py`; discovered `specialist_name` is rendered only inside prompts and `display_name` is used only as Codex skill H1; checked available `multi_agent_v1.spawn_agent` schema and found no `display_name`/`label` parameter for visible subagent naming.
- Files touched: `.domus/memory/handoffs.md`.
- Status: done.
- Blocker: Codex Desktop subagent UI naming appears controlled by runtime/tooling, not by generated agent prompt fields.
- Next agent/action: If desired, add an experimental `display_name = "<specialist_name>"` or `alias = "<specialist_name>"` TOML field behind documentation, then manually verify whether Codex Desktop reads it.

### 2026-06-08T03:00:00Z | platform: Claude Code | agent: workstyle-standards-coordinator

- Task: Add Antigravity platform support so agents stay uniform across Claude Code, Codex, and Antigravity.
- Actions: Added `render_antigravity()` to `generate-agent-kit.py` (YAML frontmatter with `platform: antigravity`); updated `expected_outputs()` to write `antigravity-agents/<name>.md`; regenerated all 11 agents; updated `specs/agents.yaml` header and `shared_memory_note`; updated README, INSTALL, AUTOMATION, and `shared.md`.
- Files touched: `scripts/generate-agent-kit.py`, `specs/agents.yaml`, `antigravity-agents/*.md` (11 new), `README.md`, `INSTALL.md`, `AUTOMATION.md`, `.domus/memory/shared.md`, `.domus/memory/handoffs.md`.
- Status: done.
- Blocker: None.
- Next agent/action: If Antigravity uses a different install path than `$HOME\.antigravity\agents`, update `INSTALL.md` accordingly.

### 2026-06-08T02:31:26Z | platform: Codex | agent: Codex

- Task: Apply apostle-inspired persona names to all agents.
- Actions: Added per-agent `specialist_name` values for all 11 agents, expanded README rationale for each apostolic persona, updated quick-start customization docs, regenerated generated outputs, deployed to Claude/Codex locations, and validated generated parity.
- Files touched: `specs/agents.yaml`, `README.md`, `QUICK-START.md`, `claude-agents/*`, `codex-skills/*/SKILL.md`, `.codex/agents/*.toml`, `.claude/agents/*`, `.domus/memory/shared.md`, `.domus/memory/handoffs.md`.
- Status: done.
- Blocker: None.
- Next agent/action: Continue calling agents by technical names; personas are in `specialist_name`.

### 2026-06-08T01:55:50Z | platform: Codex | agent: Codex

- Task: Make coordinator persona name configurable without changing behavior.
- Actions: Set `workstyle-standards-coordinator` `specialist_name` to `wojtyla_CTO`, documented per-agent naming configuration, regenerated generated outputs, and validated parity.
- Files touched: `specs/agents.yaml`, `claude-agents/workstyle-standards-coordinator.md`, `codex-skills/workstyle-standards-coordinator/SKILL.md`, `.codex/agents/workstyle-standards-coordinator.toml`, `README.md`, `QUICK-START.md`, `.domus/memory/shared.md`, `.domus/memory/handoffs.md`.
- Status: done.
- Blocker: None.
- Next agent/action: Use `specialist_name` for persona names; keep technical `name` fields stable for routing.

### 2026-06-08T01:53:19Z | platform: Codex | agent: Codex

- Task: Record user-defined agent name.
- Actions: Added durable naming convention that `workstyle-standards-coordinator` is named `wojtyla_CTO`.
- Files touched: `.domus/memory/shared.md`, `.domus/memory/handoffs.md`.
- Status: done.
- Blocker: None.
- Next agent/action: Use `wojtyla_CTO` when referring to `workstyle-standards-coordinator`.

### 2026-06-08T01:44:37Z | platform: Codex | agent: workstyle-standards-coordinator

- Task: Make shared-memory initialization token-efficient and coordinator-owned.
- Actions: Added a coordinator-only initialization rule, documented that other specialists consume existing memory instead of auto-initializing it, regenerated agent outputs, and validated generated parity.
- Files touched: `specs/agents.yaml`, `SHARED-MEMORY.md`, `README.md`, `QUICK-START.md`, generated coordinator outputs, generated shared-memory sections.
- Status: done.
- Blocker: None.
- Next agent/action: Commit the shared-memory integration changes.

### 2026-06-08T01:32:38Z | platform: Codex | agent: workstyle-standards-coordinator

- Task: Add project-local shared memory so Claude Code and Codex agents can hand off work.
- Actions: Added shared memory protocol to generated agents, created `scripts/init-shared-memory.ps1`, documented the workflow, regenerated all agent outputs, and initialized memory in this repository.
- Files touched: `specs/agents.yaml`, `scripts/generate-agent-kit.py`, `scripts/init-shared-memory.ps1`, `SHARED-MEMORY.md`, `README.md`, `INSTALL.md`, `QUICK-START.md`, `AGENTS.md`, `CLAUDE.md`, `.domus/memory/*`, generated agent outputs.
- Status: done.
- Blocker: None.
- Next agent/action: `code-reviewer` can review the shared-memory protocol and generated output before commit.

### 0000-00-00T00:00:00Z | platform: unknown | agent: example-agent

- Task: Example task title.
- Actions: Example action summary.
- Files touched: `path/to/file`.
- Status: pending | in-progress | blocked | done.
- Blocker: None.
- Next agent/action: `agent-name` should do the next concrete action.

## 2026-06-09 — Claude Code (Opus) — agent usage tracker
- Task: rastrear uso/eficiência/tokens de cada agent por projeto, sem custo de tokens.
- Actions: criado `scripts/agent-usage.py` (collect incremental + report CLI); ingere transcripts do Claude Code (sessões + `subagents/agent-*.jsonl`, atribuição via agentId→agentType) e rollouts do Codex (`token_count`); grava em SQLite `~/.domus/usage.db`. Primeira coleta: 381 arquivos, 7 projetos Claude + ~20 projetos Codex.
- Files: scripts/agent-usage.py (novo).
- Status: fase 1 (manual) funcionando. Próximo: agendamento (Task Scheduler/hook SubagentStop) e fase 3 = app Streamlit com dashboard + criação/gestão de agents (decisão do usuário).

## 2026-06-09 — Claude Code (Sonnet) — Domus Console: spec + automação + app
- Task: doc de produto, fase 2 (automação), fase 3 (app Streamlit).
- Actions:
  - docs/domus-console-product-spec.md criado (visão de negócio, arquitetura, modelo de dados, 5 telas, requisitos UX, roadmap, riscos).
  - Fase 2: scripts/setup-usage-automation.ps1 + tarefa "DomusUsageCollect" (schtasks, horária) + hook SubagentStop em ~/.claude/settings.json instalados.
  - Fase 3: console/ com app.py (Streamlit multi-page), db.py (queries SQLite), pages/dashboard.py, agent_detail.py, project_detail.py, agent_manager.py, settings.py + requirements.txt.
- Files: docs/domus-console-product-spec.md, scripts/setup-usage-automation.ps1, console/app.py, console/db.py, console/pages/*.py, console/requirements.txt
- Status: código pronto. Dependências não instaladas (usuário interrompeu pip install — deve rodar manualmente). Nada commitado ainda.
- Next: instalar deps (pip install -r console/requirements.txt) → testar UI → commit.
# 2026-06-15T14:44:46Z | Codex | workstyle-standards-coordinator

- Task: Create Neon Postgres project and integrate Domus Console localhost.
- Actions taken: Read Domus memory; created Neon project `domus-agents`; applied Postgres schema; added local env loading; updated console DB layer for Neon/Postgres with SQLite fallback; updated collector for Postgres writes; added dependency declarations and ignored local env files; verified dashboard/settings through Streamlit at `http://127.0.0.1:8501`.
- Files touched: `.domus/memory/state.md`, `.domus/memory/inbox.md`, `.domus/memory/shared.md`, `.domus/memory/handoffs.md`, `console/db.py`, `console/pages/settings.py`, `console/requirements.txt`, `scripts/agent-usage.py`, `.gitignore`, `.env.example`, `.env.local`.
- Status: Done.
- Blocker: None.
- Next agent/action: Use `.env.local` for localhost; future agents must not commit or disclose the Neon connection string.
