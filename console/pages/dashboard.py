"""Dashboard — visão geral de uso de todos os agents."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.express as px
import pandas as pd
import db

st.title("Dashboard")

if not db.has_data():
    st.warning("Nenhum dado coletado ainda.")
    st.code("python scripts/agent-usage.py collect", language="bash")
    st.stop()

# ── filtros globais ───────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filtros")
    period = st.selectbox("Período", ["Tudo", "7 dias", "30 dias", "90 dias"])
    days_map = {"Tudo": 0, "7 dias": 7, "30 dias": 30, "90 dias": 90}
    days = days_map[period]

    platforms = ["all"] + db.all_platforms()
    platform = st.selectbox("Plataforma", platforms, format_func=lambda x: "Todas" if x=="all" else x.capitalize())

    projects = ["all"] + [p.split("/")[-1].split("\\")[-1] for p in db.all_projects()]
    project_label = st.selectbox("Projeto", ["all"] + projects[1:], format_func=lambda x: "Todos" if x=="all" else x)
    project = project_label if project_label != "all" else "all"

# ── KPI cards ─────────────────────────────────────────────────────────────────
kpis = db.kpis(platform, project, days)

c1, c2, c3, c4, c5, c6 = st.columns(6)
for col, label, val in [
    (c1, "Invocações",      kpis.get("invocations", 0)),
    (c2, "Tokens output",   db.fmt(kpis.get("output_tokens", 0))),
    (c3, "Cache hit médio", f"{kpis.get('cache_hit', 0):.1f}%"),
    (c4, "Tokens input",    db.fmt(kpis.get("input_tokens", 0))),
    (c5, "Projetos ativos", kpis.get("active_projects", 0)),
    (c6, "Agents ativos",   kpis.get("active_agents", 0)),
]:
    col.metric(label, val)

st.divider()

# ── gráficos ──────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("Invocações por agent")
    inv_df = db.invocations_by_agent(platform, project, days)
    if not inv_df.empty:
        fig = px.bar(
            inv_df, y="agent", x="invocations", color="platform",
            orientation="h", text_auto=True,
            color_discrete_map={"claude": "#8b5cf6", "codex": "#3b82f6"},
            height=max(350, len(inv_df) * 26),
        )
        fig.update_layout(yaxis={"categoryorder":"total ascending"},
                          plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                          font_color="#e2e8f0", legend_title="Plataforma",
                          margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem invocações no período.")

with col_right:
    st.subheader("Tokens output por agent")
    tok_df = db.usage_by_agent(platform, project, days)
    if not tok_df.empty:
        fig2 = px.bar(
            tok_df, y="agent", x="output", orientation="h",
            text=tok_df["output"].apply(db.fmt),
            color_discrete_sequence=["#6366f1"],
            height=max(350, len(tok_df) * 26),
        )
        fig2.update_layout(yaxis={"categoryorder":"total ascending"},
                           plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                           font_color="#e2e8f0",
                           margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Sem dados de tokens no período.")

# ── linha do tempo ────────────────────────────────────────────────────────────
st.subheader("Invocações ao longo do tempo")
time_df = db.invocations_over_time(platform, project, days)
if not time_df.empty:
    fig3 = px.area(time_df, x="date", y="invocations",
                   color_discrete_sequence=["#8b5cf6"])
    fig3.update_layout(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                       font_color="#e2e8f0", margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig3, use_container_width=True)

# ── tabela de eficiência ──────────────────────────────────────────────────────
st.subheader("Ranking de eficiência")
eff = db.usage_by_agent(platform, project, days)
inv = db.invocations_by_agent(platform, project, days)
if not eff.empty and not inv.empty:
    total_inv = inv.groupby("agent")["invocations"].sum().reset_index()
    merged = eff.merge(total_inv, on="agent", how="left")
    merged["tok_per_inv"] = (merged["output"] / merged["invocations"].replace(0, float("nan"))).round(0)
    merged["ratio_o_i"] = (merged["output"] / merged["input"].replace(0, float("nan"))).round(2)

    display = merged[["agent","invocations","tok_per_inv","cache_hit_pct","ratio_o_i","output","cache_read"]].copy()
    display.columns = ["Agent","Invocações","Tok/Inv","Cache Hit %","Ratio O/I","Output","Cache Read"]
    display["Output"] = display["Output"].apply(db.fmt)
    display["Cache Read"] = display["Cache Read"].apply(db.fmt)
    display["Cache Hit %"] = display["Cache Hit %"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "—")
    st.dataframe(display, use_container_width=True, hide_index=True)
