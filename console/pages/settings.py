"""Settings page: collection, automation, and data sources."""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

import db


def _sanitize_output(text: str) -> str:
    """Remove DATABASE_URL value and any postgresql:// connection strings from
    output that will be rendered in the UI, preventing credential leakage via
    subprocess stderr or SQLAlchemy/psycopg tracebacks."""
    db_url = os.getenv("DATABASE_URL", "")
    if db_url:
        text = text.replace(db_url, "[DATABASE_URL redacted]")
    # Catch any residual postgresql(+psycopg)://user:pass@host/db patterns.
    text = re.sub(
        r"postgresql(?:\+\w+)?://[^\s\"']+",
        "[connection string redacted]",
        text,
    )
    return text

ROOT = Path(__file__).parent.parent.parent
COLLECTOR = ROOT / "scripts" / "agent-usage.py"


st.title("Configuracoes")

st.subheader("Status da coleta")

info = db.last_collect_info()
col1, col2, col3 = st.columns(3)
col1.metric("Arquivos ingeridos", info.get("n", 0))
col2.metric("Backend", db.backend_label())
col3.metric("Ultima ingestao", str(info.get("last") or "-")[:10])
st.caption(f"Destino atual: `{db.database_location()}`")

if st.button("Coletar agora", type="primary"):
    with st.spinner("Coletando..."):
        r = subprocess.run(
            [sys.executable, str(COLLECTOR), "collect"],
            capture_output=True,
            text=True,
        )
    if r.returncode == 0:
        st.success(r.stdout.strip() or "Coleta concluida.")
        db.clear_cache()
    else:
        st.error(f"Erro:\n{_sanitize_output(r.stderr)}")

st.divider()

st.subheader("Automacao")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("**Task Scheduler (Windows)**")
    r = subprocess.run(
        ["schtasks", "/Query", "/TN", "DomusUsageCollect", "/FO", "LIST"],
        capture_output=True,
        text=True,
    )
    if r.returncode == 0:
        next_run = [
            line
            for line in r.stdout.splitlines()
            if "proxima" in line.lower() or "next" in line.lower()
        ]
        st.success("Tarefa instalada - roda a cada hora.")
        if next_run:
            st.caption(next_run[0].strip())
    else:
        st.warning("Tarefa nao instalada.")
        st.code("powershell -File scripts\\setup-usage-automation.ps1", language="powershell")

with col_b:
    st.markdown("**Hook SubagentStop (Claude Code)**")
    settings_path = Path.home() / ".claude" / "settings.json"
    hook_present = False
    if settings_path.exists():
        try:
            cfg = json.loads(settings_path.read_text(encoding="utf-8"))
            hook_present = bool(cfg.get("hooks", {}).get("SubagentStop"))
        except Exception:
            hook_present = False

    if hook_present:
        st.success("Hook ativo - coleta ao fim de cada subagent.")
    else:
        st.warning("Hook nao instalado.")
        st.code("powershell -File scripts\\setup-usage-automation.ps1", language="powershell")

st.divider()

st.subheader("Fontes de dados")

sources = {
    "Claude Code transcripts": Path.home() / ".claude" / "projects",
    "Codex sessions": Path.home() / ".codex" / "sessions",
    "Codex archived sessions": Path.home() / ".codex" / "archived_sessions",
    "Banco SQLite fallback": db.DB_PATH,
}

for label, path in sources.items():
    icon = "OK" if path.exists() else "Nao encontrado"
    st.markdown(f"**{label}** ({icon})  \n`{path}`")

st.divider()

st.subheader("Alertas de threshold")
st.caption("Baseado nos dados coletados ate agora.")

try:
    alerts = db.threshold_alerts()
except Exception as exc:
    alerts = []
    st.error(f"Erro ao calcular alertas: {_sanitize_output(str(exc))}")

_ALERT_ICON = {"cache": "Cache hit baixo", "spike": "Spike de tokens", "inactive": "Agent inativo"}

if not alerts:
    if db.has_data():
        st.success("Nenhum alerta de threshold ativo.")
    else:
        st.info("Sem dados coletados ainda.")
else:
    for a in alerts:
        label = _ALERT_ICON.get(a["type"], "Alerta")
        st.warning(f"**{label} — {a['agent']}:** {a['msg']}")

st.divider()

st.subheader("Referencia de precos (por 1M tokens)")
st.caption("Usado apenas para estimativa de custo - nao afeta a coleta.")

prices = {
    m: {k: v for k, v in p.items() if k != "cache_create"}
    for m, p in db.MODEL_PRICES.items()
}

df = pd.DataFrame(prices).T.reset_index().rename(
    columns={
        "index": "Modelo",
        "input": "Input $",
        "output": "Output $",
        "cache_read": "Cache Read $",
    }
)
st.dataframe(df, use_container_width=True, hide_index=True)
st.caption("Valores em USD. Atualize diretamente em `pages/settings.py` se os precos mudarem.")
