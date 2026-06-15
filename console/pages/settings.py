"""Configurações — coleta, automação, caminhos."""
import sys, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import db

ROOT = Path(__file__).parent.parent.parent
COLLECTOR = ROOT / "scripts" / "agent-usage.py"


def fmt_bytes(n):
    if n >= 1_048_576: return f"{n/1_048_576:.1f} MB"
    if n >= 1_024:     return f"{n/1_024:.1f} KB"
    return f"{n} B"


st.title("Configurações")

# ── status da coleta ──────────────────────────────────────────────────────────
st.subheader("Status da coleta")

info = db.last_collect_info()
col1, col2, col3 = st.columns(3)
col1.metric("Arquivos ingeridos", info.get("n", 0))
col2.metric("Tamanho do banco",   fmt_bytes(info.get("db_size", 0)))
col3.metric("Última ingestão", str(info.get("last") or "—")[:10])

if st.button("🔄 Coletar agora", type="primary"):
    import sys as _sys
    with st.spinner("Coletando..."):
        r = subprocess.run(
            [_sys.executable, str(COLLECTOR), "collect"],
            capture_output=True, text=True
        )
    if r.returncode == 0:
        st.success(r.stdout.strip() or "Coleta concluída.")
        st.cache_resource.clear()
    else:
        st.error(f"Erro:\n{r.stderr}")

st.divider()

# ── automação ─────────────────────────────────────────────────────────────────
st.subheader("Automação")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("**Task Scheduler (Windows)**")
    r = subprocess.run(
        ["schtasks", "/Query", "/TN", "DomusUsageCollect", "/FO", "LIST"],
        capture_output=True, text=True
    )
    if r.returncode == 0:
        next_run = [l for l in r.stdout.splitlines() if "próxima" in l.lower() or "next" in l.lower()]
        st.success("✅ Tarefa instalada — roda a cada hora.")
        if next_run:
            st.caption(next_run[0].strip())
    else:
        st.warning("❌ Tarefa não instalada.")
        st.code("powershell -File scripts\\setup-usage-automation.ps1", language="powershell")

with col_b:
    st.markdown("**Hook SubagentStop (Claude Code)**")
    settings_path = Path.home() / ".claude" / "settings.json"
    if settings_path.exists():
        import json
        try:
            cfg = json.loads(settings_path.read_text(encoding="utf-8"))
            hook_present = bool(cfg.get("hooks", {}).get("SubagentStop"))
        except Exception:
            hook_present = False
    else:
        hook_present = False

    if hook_present:
        st.success("✅ Hook ativo — coleta ao fim de cada subagent.")
    else:
        st.warning("❌ Hook não instalado.")
        st.code("powershell -File scripts\\setup-usage-automation.ps1", language="powershell")

st.divider()

# ── fontes de dados ────────────────────────────────────────────────────────────
st.subheader("Fontes de dados")

sources = {
    "Claude Code transcripts":   Path.home() / ".claude" / "projects",
    "Codex sessions":            Path.home() / ".codex" / "sessions",
    "Codex archived sessions":   Path.home() / ".codex" / "archived_sessions",
    "Banco SQLite":              db.DB_PATH,
}

for label, path in sources.items():
    exists = path.exists()
    icon = "✅" if exists else "❌"
    st.markdown(f"{icon} **{label}**  \n`{path}`")

st.divider()

# ── preços por modelo (informativo) ──────────────────────────────────────────
st.subheader("Referência de preços (por 1M tokens)")
st.caption("Usado apenas para estimativa de custo — não afeta a coleta.")

prices = {
    "claude-opus-4-8":   {"input": 15.00, "output": 75.00, "cache_read": 1.50},
    "claude-sonnet-4-6": {"input":  3.00, "output": 15.00, "cache_read": 0.30},
    "claude-haiku-4-5":  {"input":  0.80, "output":  4.00, "cache_read": 0.08},
    "gpt-5.5":           {"input": 10.00, "output": 30.00, "cache_read": 2.50},
}

import pandas as pd
df = pd.DataFrame(prices).T.reset_index().rename(columns={"index":"Modelo","input":"Input $","output":"Output $","cache_read":"Cache Read $"})
st.dataframe(df, use_container_width=True, hide_index=True)
st.caption("Valores em USD. Atualize diretamente no código `pages/settings.py` se os preços mudarem.")
