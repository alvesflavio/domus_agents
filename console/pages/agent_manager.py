"""Gestão de agents — criar, editar, validar, implantar."""
import sys, subprocess, shutil, copy, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import yaml

ROOT = Path(__file__).parent.parent.parent  # C:\dev\domus_agents
SPEC = ROOT / "specs" / "agents.yaml"
SCRIPTS = ROOT / "scripts"

TOOL_OPTIONS = [
    "Glob", "Grep", "Read", "Edit", "Write", "Bash",
    "WebFetch", "WebSearch", "Agent",
]

CLAUDE_PROJECT_AGENTS = ROOT / ".claude" / "agents"
CLAUDE_USER_AGENTS    = Path.home() / ".claude" / "agents"
CODEX_AGENTS          = Path.home() / ".codex" / "agents"
CODEX_SKILLS          = Path.home() / ".codex" / "skills"
ANTIGRAVITY_AGENTS    = Path.home() / ".antigravity" / "agents"


def load_spec():
    if not SPEC.exists():
        return {}
    with open(SPEC, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_spec(data: dict):
    backup = SPEC.with_suffix(".yaml.bak")
    if SPEC.exists():
        shutil.copy2(SPEC, backup)
    with open(SPEC, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)


def deploy_status(name: str) -> dict:
    return {
        ".claude (projeto)":  (CLAUDE_PROJECT_AGENTS / f"{name}.md").exists(),
        "~/.claude (global)": (CLAUDE_USER_AGENTS    / f"{name}.md").exists(),
        "~/.codex/agents":    (CODEX_AGENTS           / f"{name}.toml").exists(),
        "~/.codex/skills":    (CODEX_SKILLS / name / "SKILL.md").exists(),
        "~/.antigravity":     (ANTIGRAVITY_AGENTS     / f"{name}.md").exists(),
    }


def run_pipeline(label: str):
    steps = [
        ("Gerar",    ["python", str(SCRIPTS / "generate-agent-kit.py")]),
        ("Validar",  ["powershell", "-File", str(SCRIPTS / "validate-agent-kit.ps1")]),
        ("Implantar",["powershell", "-File", str(SCRIPTS / "deploy-agents.ps1")]),
    ]
    box = st.empty()
    log = []
    for step_label, cmd in steps:
        log.append(f"▶ {step_label}...")
        box.code("\n".join(log))
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
        if r.stdout.strip():
            log += r.stdout.strip().splitlines()
        if r.returncode != 0:
            log.append(f"✗ Erro em '{step_label}':")
            log += (r.stderr or "").strip().splitlines()
            box.code("\n".join(log))
            st.error(f"Pipeline falhou em '{step_label}'. Veja o log acima.")
            return False
        log.append(f"✓ {step_label} OK")
        box.code("\n".join(log))
    st.success("Pipeline completo! Reinicie sessões do Claude Code e Codex.")
    return True


# ── página ────────────────────────────────────────────────────────────────────
st.title("Gestão de Agents")

spec = load_spec()
agents_list: list = spec.get("agents", []) if spec else []

tab_list, tab_edit, tab_new = st.tabs(["Lista", "Editar", "Novo agent"])

# ──────── TAB: LISTA ──────────────────────────────────────────────────────────
with tab_list:
    if not agents_list:
        st.info("Spec não encontrada ou sem agents.")
    else:
        for ag in agents_list:
            name = ag.get("name", "?")
            with st.expander(f"**{name}**  —  {ag.get('specialist_name','TODO')}", expanded=False):
                col_info, col_status = st.columns([3, 2])
                with col_info:
                    st.markdown(f"**Descrição:**  \n{ag.get('description','—')}")
                    st.markdown(f"**Tools:** `{'`, `'.join(ag.get('tools',[]))}`")
                    st.markdown(f"**Seções:** {len(ag.get('sections',[]))}")
                with col_status:
                    status = deploy_status(name)
                    st.markdown("**Status de deploy:**")
                    for dest, ok in status.items():
                        icon = "✅" if ok else "❌"
                        st.markdown(f"{icon} {dest}")
        st.divider()
        if st.button("▶ Regenerar + Validar + Implantar todos", type="primary"):
            run_pipeline("full")

# ──────── TAB: EDITAR ─────────────────────────────────────────────────────────
with tab_edit:
    if not agents_list:
        st.info("Nenhum agent na spec.")
    else:
        names = [a.get("name","?") for a in agents_list]
        selected = st.selectbox("Agent a editar", names)
        ag_idx = next((i for i,a in enumerate(agents_list) if a.get("name")==selected), None)
        ag = copy.deepcopy(agents_list[ag_idx]) if ag_idx is not None else {}

        with st.form(f"edit_{selected}"):
            st.markdown(f"**Nome (chave de roteamento — imutável):** `{ag.get('name')}`")
            specialist = st.text_input("specialist_name", value=ag.get("specialist_name","TODO"))
            description = st.text_area("description", value=ag.get("description",""),
                                       height=120, help="Use linguagem neutra de plataforma — guia o roteamento no Claude Code, Codex e Antigravity.")
            st.caption(f"{len(description)} chars")
            tools = st.multiselect("tools", TOOL_OPTIONS,
                                   default=[t for t in ag.get("tools",[]) if t in TOOL_OPTIONS])
            st.markdown("**Seções** (heading + body):")
            sections = ag.get("sections", [])
            new_sections = []
            for i, sec in enumerate(sections):
                c1, c2 = st.columns([1, 3])
                heading = c1.text_input(f"heading #{i+1}", value=sec.get("heading",""), key=f"h{selected}{i}")
                body    = c2.text_area(f"body #{i+1}", value=sec.get("body",""), key=f"b{selected}{i}", height=80)
                new_sections.append({"heading": heading, "body": body})

            submitted = st.form_submit_button("Salvar alterações")
            if submitted:
                updated = copy.deepcopy(ag)
                updated["specialist_name"] = specialist
                updated["description"] = description
                updated["tools"] = tools
                updated["sections"] = new_sections
                spec["agents"][ag_idx] = updated
                save_spec(spec)
                st.success("Spec salva (backup em specs/agents.yaml.bak).")
                st.info("Clique em 'Implantar' para propagar às plataformas.")

        if st.button("▶ Gerar + Validar + Implantar", key=f"deploy_{selected}"):
            run_pipeline(selected)

# ──────── TAB: NOVO AGENT ─────────────────────────────────────────────────────
with tab_new:
    with st.form("new_agent"):
        st.markdown("#### Novo agent")
        new_name = st.text_input("name (kebab-case único)", placeholder="meu-agent")
        new_specialist = st.text_input("specialist_name", placeholder="Maria")
        new_desc = st.text_area("description", height=100,
                                help="Descreva quando este agent deve ser invocado. Neutro de plataforma.")
        new_tools = st.multiselect("tools", TOOL_OPTIONS, default=["Read","Glob","Grep"])
        new_heading = st.text_input("Seção inicial — heading")
        new_body = st.text_area("Seção inicial — body", height=80)

        submitted_new = st.form_submit_button("Criar agent")
        if submitted_new:
            if not new_name:
                st.error("Nome obrigatório.")
            elif not re.match(r'^[a-z][a-z0-9-]*$', new_name):
                st.error("Nome deve ser kebab-case (letras minúsculas, números e hífens).")
            elif new_name in [a.get("name") for a in agents_list]:
                st.error(f"Já existe um agent com o nome '{new_name}'.")
            elif not new_desc.strip():
                st.error("Descrição obrigatória (guia o roteamento nas 3 plataformas).")
            else:
                new_agent = {
                    "name": new_name,
                    "specialist_name": new_specialist or "TODO",
                    "description": new_desc,
                    "tools": new_tools,
                    "sections": [{"heading": new_heading, "body": new_body}]
                                if new_heading else [],
                }
                spec.setdefault("agents", []).append(new_agent)
                save_spec(spec)
                st.success(f"Agent '{new_name}' adicionado à spec.")
                st.info("Clique em 'Implantar' para gerar e propagar.")

    if st.button("▶ Gerar + Validar + Implantar (após criar)", key="deploy_new"):
        run_pipeline("new")
