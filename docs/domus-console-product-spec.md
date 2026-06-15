# Domus Console — Especificação de Negócio e Produto

**Versão:** 1.0 · **Data:** 2026-06-09 · **Status:** Aprovado para implementação
**Produto:** Aplicação local de observabilidade e gestão de agents de IA multi-plataforma

---

## 1. Visão de Negócio

### 1.1 Problema

Times e desenvolvedores que usam agents de IA (Claude Code, Codex, Antigravity) em múltiplos projetos não têm visibilidade sobre:

- **Quais agents são usados, onde e com que frequência** — o uso fica espalhado em transcripts locais que ninguém lê.
- **Quanto cada agent custa em tokens** — sem isso, não dá para otimizar prompts, escolher modelos ou justificar custo.
- **Se os agents são eficientes** — um agent verboso ou com cache ruim desperdiça contexto e dinheiro silenciosamente.
- **Gestão fragmentada** — criar/editar um agent exige editar YAML, rodar scripts de geração, validação e deploy em 3 plataformas manualmente.

### 1.2 Solução

O **Domus Console** é uma aplicação local (zero custo de tokens, zero nuvem obrigatória) com dois pilares:

1. **Observabilidade** — coleta automática dos transcripts já gravados pelo Claude Code e Codex, agregando uso, tokens e eficiência por agent × projeto × plataforma.
2. **Gestão** — interface única para criar, editar, validar e implantar agents a partir da spec canônica (`specs/agents.yaml`), substituindo o fluxo manual de scripts.

### 1.3 Princípios de produto

| Princípio | Implicação |
|---|---|
| **Zero-token** | Nenhuma funcionalidade core chama um LLM. Tudo é leitura de arquivos locais + SQLite. |
| **Local-first** | Dados ficam em `~/.domus/usage.db`. Sem telemetria externa, sem conta, sem servidor remoto. |
| **Spec como fonte da verdade** | A UI de gestão edita `specs/agents.yaml`; arquivos por plataforma continuam gerados, nunca editados à mão. |
| **Incremental e idempotente** | A coleta só processa arquivos novos/alterados; pode rodar 1000x por dia sem custo perceptível. |
| **Multi-plataforma desde o início** | Claude Code + Codex no MVP; Antigravity quando houver formato de log estável. |

### 1.4 Público-alvo

- **Persona primária — "Builder solo" (Flavio):** desenvolvedor que mantém um kit de agents portável usado em ~10 projetos pessoais/profissionais. Quer saber o que funciona, o que custa caro, e gerir agents sem fricção.
- **Persona secundária — "Tech lead de squad":** lidera time que padroniza agents; precisa de relatórios para decidir quais agents promover, aposentar ou re-especificar.

### 1.5 Métricas de sucesso do produto

- Tempo para responder "qual agent mais usei este mês e quanto custou?" — de *impossível* para **< 10 segundos**.
- Tempo de ciclo criar/editar agent → implantado em 3 plataformas — de ~5 passos manuais para **1 fluxo na UI**.
- Custo de operação contínua: **0 tokens de LLM**.

---

## 2. Arquitetura de Alto Nível

```
┌─────────────────────────────────────────────────────────────┐
│                      DOMUS CONSOLE (Streamlit, localhost)    │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌───────────┐ │
│  │ Dashboard  │ │  Agents    │ │  Projetos  │ │  Gestão   │ │
│  │ (overview) │ │ (detalhe)  │ │ (detalhe)  │ │ de Agents │ │
│  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬─────┘ │
└────────┼──────────────┼──────────────┼──────────────┼───────┘
         │   leitura SQL │              │              │ leitura/escrita
         ▼              ▼              ▼              ▼
  ┌──────────────────────────────┐   ┌─────────────────────────┐
  │   ~/.domus/usage.db (SQLite) │   │   specs/agents.yaml     │
  └──────────────▲───────────────┘   └───────────┬─────────────┘
                 │ collect (incremental)         │ generate/validate/deploy
  ┌──────────────┴───────────────┐   ┌───────────▼─────────────┐
  │  scripts/agent-usage.py      │   │  scripts/*.py / *.ps1   │
  │  (coletor zero-token)        │   │  (pipeline existente)   │
  └──────────────▲───────────────┘   └─────────────────────────┘
                 │ leitura de arquivos
  ┌──────────────┴──────────────────────────────────────────────┐
  │  ~/.claude/projects/**/*.jsonl  +  <sessão>/subagents/*.jsonl│
  │  ~/.codex/sessions/** + archived_sessions (rollout-*.jsonl)  │
  └──────────────────────────────────────────────────────────────┘
```

**Gatilhos da coleta (camadas independentes):**
1. Manual — botão "Atualizar dados" na UI ou CLI.
2. Agendado — Windows Task Scheduler (a cada hora).
3. Tempo real — hook `SubagentStop` do Claude Code dispara `collect` ao fim de cada subagent.

---

## 3. Modelo de Dados

Banco: `~/.domus/usage.db` (SQLite).

| Tabela | Propósito | Campos-chave |
|---|---|---|
| `invocations` | Cada vez que um agent foi acionado | platform, project, branch, agent, session_id, ts |
| `token_usage` | Tokens por mensagem de assistant | platform, project, agent (NULL = sessão principal), model, input/output/cache_read/cache_create tokens, ts |
| `agent_map` | Liga agentId do Claude Code ao tipo de agent | agent_id → agent_type |
| `ingested_files` | Controle incremental | path, mtime, size |

**Métricas derivadas (calculadas na UI, não armazenadas):**

| Métrica | Fórmula | O que indica |
|---|---|---|
| Tokens/invocação | Σ tokens do agent ÷ nº invocações | Custo médio de chamar o agent |
| Razão output/input | Σ output ÷ Σ input efetivo | Verbosidade |
| Cache hit rate | cache_read ÷ (input + cache_read + cache_create) | Reaproveitamento de contexto (meta: > 85%) |
| Msgs/invocação | nº mensagens ÷ nº invocações | Idas e voltas até concluir |

---

## 4. Funcionalidades (escopo do front-end)

### 4.1 Tela: Dashboard (home)

**Objetivo:** responder em 5 segundos "como está o uso dos meus agents?"

- **Cards de KPI (topo):** total de invocações (período), total de tokens output, custo estimado*, cache hit médio, nº de projetos ativos, nº de agents ativos.
- **Filtros globais (sidebar):** período (7d/30d/90d/tudo), plataforma (Claude/Codex/todas), projeto.
- **Gráfico 1 — Invocações por agent** (barras horizontais, ordenado desc).
- **Gráfico 2 — Tokens output por agent** (barras).
- **Gráfico 3 — Uso ao longo do tempo** (linha/área, invocações por semana).
- **Tabela — Ranking de eficiência:** agent, invocações, tokens/invocação, cache hit, razão O/I, com semáforo (verde/amarelo/vermelho) por limiar.

*Custo estimado = tokens × tabela de preço configurável por modelo (default: preços públicos Anthropic/OpenAI).

### 4.2 Tela: Detalhe do Agent

**Objetivo:** "esse agent vale o que custa?"

- Header: nome, descrição (da spec), plataformas onde está implantado, status de sincronia (spec vs implantado).
- KPIs do agent: invocações, tokens in/out, cache hit, tokens/invocação, tendência vs período anterior.
- **Distribuição por projeto** (barras): onde esse agent é mais usado.
- **Linha do tempo** de invocações.
- **Comparativo:** posição do agent no ranking de eficiência geral.
- Lista das últimas N invocações (timestamp, projeto, branch, plataforma).

### 4.3 Tela: Detalhe do Projeto

**Objetivo:** "quanto custa a IA neste projeto e quem trabalha nele?"

- KPIs do projeto: tokens totais por plataforma, agents usados, sessões.
- **Mix de agents** (pizza/barras): participação de cada agent no projeto.
- Tokens da sessão principal vs trabalho de subagents (mostra quanto do custo é delegação).

### 4.4 Tela: Gestão de Agents

**Objetivo:** ciclo completo criar → editar → validar → implantar sem sair da UI.

- **Lista de agents** da spec (`specs/agents.yaml`): nome, specialist_name, descrição, tools, nº de seções; badge de status de deploy por plataforma (project/.claude, ~/.claude, ~/.codex agents+skills, ~/.antigravity).
- **Editor de agent:** formulário com nome (somente leitura após criado — é chave de roteamento), specialist_name, description (textarea com contador — descrições guiam o roteamento nas 3 plataformas), tools (multi-select), seções heading/body (lista editável e reordenável).
- **Criar novo agent:** mesmo formulário, validações: nome kebab-case único, descrição plataforma-neutra obrigatória.
- **Ações de pipeline (botões):** `Gerar` (generate-agent-kit.py) → `Validar` (validate-agent-kit.ps1) → `Implantar` (deploy-agents.ps1), com output do console exibido na tela e estado de sucesso/erro.
- **Diff antes de salvar:** mostrar o que muda no YAML.
- Aviso pós-deploy: "Reinicie sessões do Claude Code/Codex para descobrir as alterações."

### 4.5 Tela: Coleta & Configurações

- Status da coleta: último run, arquivos ingeridos, tamanho do banco.
- Botão **"Coletar agora"** (roda `collect`, mostra resultado).
- Status da automação: tarefa agendada instalada? hook ativo? — com botões/instruções de instalação.
- Tabela de preços por modelo (editável) para o custo estimado.
- Caminhos das fontes de dados (somente leitura, com botão revelar no Explorer).

### 4.6 Fora de escopo (MVP)

- Multiusuário, autenticação, deploy em nuvem.
- Antigravity (sem formato de log mapeado — entra quando houver).
- Atribuição de tokens por agent no Codex (o formato só dá tokens por sessão; mostrar invocações e marcar tokens como "nível sessão").
- Edição de agents fora da spec (arquivos gerados são intocáveis).

---

## 5. Requisitos de UX para o front-end

- **Layout:** sidebar de navegação (Dashboard / Agents / Projetos / Gestão / Configurações) + filtros globais persistentes.
- **Tema:** dark-first (público é dev), acento único, tipografia mono para números/tokens.
- **Números grandes formatados:** 1.2K / 3.4M — nunca 3412876.
- **Semáforos de eficiência:** cache hit ≥ 85% verde, 70–85% amarelo, < 70% vermelho; tokens/invocação comparado à mediana dos agents.
- **Estados vazios:** primeira execução sem dados → CTA "Coletar agora"; agent sem uso → "Sem invocações no período".
- **Tudo clicável navega:** nome de agent → detalhe do agent; nome de projeto → detalhe do projeto.
- **Idioma:** PT-BR na UI; nomes técnicos de agents permanecem em inglês (são chaves de roteamento).
- **Responsivo o suficiente** para meia-tela (dev usa lado a lado com o editor).

---

## 6. Roadmap

| Fase | Entrega | Status |
|---|---|---|
| **1 — Coletor + CLI** | `agent-usage.py collect/report`, SQLite, Claude + Codex | ✅ Entregue (2026-06-09) |
| **2 — Automação** | Task Scheduler horário + hook `SubagentStop` | Em execução |
| **3 — Console (MVP UI)** | Streamlit: Dashboard, Detalhe Agent/Projeto, Gestão de Agents, Configurações | Em execução |
| **4 — Refinamentos** | Custo estimado por preço de modelo, comparativo de períodos, export CSV/HTML | Backlog |
| **5 — Plataformas** | Parser Antigravity; atribuição por skill no Codex se o formato evoluir | Backlog |

---

## 7. Riscos e mitigação

| Risco | Impacto | Mitigação |
|---|---|---|
| Claude/Codex mudarem formato de transcript | Coleta quebra silenciosamente | Parsers tolerantes (linhas inválidas são ignoradas); tela de Configurações mostra "última ingestão"; testes de fumaça no collect |
| Transcripts antigos serem rotacionados/apagados | Perda de histórico | O SQLite é o registro durável — coletar com frequência (Fase 2) preserva tudo |
| Sessões antigas sem mapa agentId→tipo | Fatia "unknown-subagent" | Aceito no MVP; fração diminui com o tempo pois sessões novas mapeiam corretamente |
| Editar YAML pela UI corromper a spec | Pipeline de deploy quebra | Diff antes de salvar + validação obrigatória + backup automático do YAML antes de cada escrita |
