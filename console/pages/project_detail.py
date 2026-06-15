"""Detalhe por projeto."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.express as px
import db

st.title("Projetos")

if not db.has_data():
    st.warning("Nenhum dado coletado ainda.")
    st.stop()

all_projects = db.all_projects()
if not all_projects:
    st.info("Nenhum projeto registrado.")
    st.stop()

def short(p):
    return (p or "?").replace("\\","/").rstrip("/").split("/")[-1]

project_map = {short(p): p for p in all_projects}

with st.sidebar:
    st.header("Filtros")
    proj_short = st.selectbox("Projeto", sorted(project_map.keys()))
    period = st.selectbox("Período", ["Tudo", "7 dias", "30 dias", "90 dias"])
    days_map = {"Tudo": 0, "7 dias": 7, "30 dias": 30, "90 dias": 90}
    days = days_map[period]

project = project_map[proj_short]
df = db.usage_for_project(project, days)

st.subheader(f"📁 {proj_short}")

if df.empty:
    st.info("Sem dados no período.")
    st.stop()

# ── KPIs ──────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Tokens output total", db.fmt(df["output"].sum()))
c2.metric("Tokens input total",  db.fmt(df["input"].sum()))
c3.metric("Cache read total",    db.fmt(df["cache_read"].sum()))
c4.metric("Agents usados",       df["agent"].nunique())

st.divider()

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Mix de agents (output tokens)")
    by_agent = df[df["agent"].notna()].groupby("agent")[["output"]].sum().reset_index()
    if not by_agent.empty:
        fig = px.pie(by_agent, names="agent", values="output",
                     color_discrete_sequence=px.colors.qualitative.Vivid,
                     hole=0.4)
        fig.update_layout(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                          font_color="#e2e8f0", margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("Tokens por plataforma")
    by_plat = df.groupby("platform")[["input","output","cache_read"]].sum().reset_index()
    if not by_plat.empty:
        melted = by_plat.melt(id_vars="platform", var_name="tipo", value_name="tokens")
        fig2 = px.bar(melted, x="platform", y="tokens", color="tipo",
                      barmode="group", text_auto=True,
                      color_discrete_map={"output":"#8b5cf6","input":"#6366f1","cache_read":"#22d3ee"})
        fig2.update_layout(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                           font_color="#e2e8f0", margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig2, use_container_width=True)

# ── tabela por agent ──────────────────────────────────────────────────────────
st.subheader("Breakdown por agent")
display = df.copy()
display["project_short"] = display["project"].apply(short)
display["output"] = display["output"].apply(db.fmt)
display["input"] = display["input"].apply(db.fmt)
display["cache_read"] = display["cache_read"].apply(db.fmt)
display["agent"] = display["agent"].fillna("(sessão principal)")
st.dataframe(
    display[["platform","agent","input","output","cache_read"]],
    use_container_width=True, hide_index=True,
)
