"""Detalhe por agent."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.express as px
import pandas as pd
import db

st.title("Agents")

if not db.has_data():
    st.warning("Nenhum dado coletado ainda.")
    st.stop()

agents = db.all_agents()
if not agents:
    st.info("Nenhum agent com invocações registradas.")
    st.stop()

with st.sidebar:
    st.header("Filtros")
    agent = st.selectbox("Agent", agents)
    period = st.selectbox("Período", ["Tudo", "7 dias", "30 dias", "90 dias"])
    days_map = {"Tudo": 0, "7 dias": 7, "30 dias": 30, "90 dias": 90}
    days = days_map[period]

# ── KPIs do agent ─────────────────────────────────────────────────────────────
kpis = db.kpis(project="all", days=days)
inv_df = db.invocations_by_agent(project="all", days=days)
tok_df = db.usage_by_agent(project="all", days=days)

agent_inv_row = inv_df[inv_df["agent"] == agent]["invocations"].sum() if not inv_df.empty else 0
agent_tok_row = tok_df[tok_df["agent"] == agent].iloc[0] if not tok_df.empty and (tok_df["agent"] == agent).any() else None

st.subheader(f"🤖 {agent}")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Invocações", int(agent_inv_row))
if agent_tok_row is not None:
    c2.metric("Tokens output", db.fmt(agent_tok_row["output"]))
    c3.metric("Tokens input (efetivo)", db.fmt(agent_tok_row["input"]))
    c4.metric("Cache hit", f"{agent_tok_row['cache_hit_pct']:.1f}%" if pd.notna(agent_tok_row["cache_hit_pct"]) else "—")
    tok_per_inv = agent_tok_row["output"] / agent_inv_row if agent_inv_row else 0
    c5.metric("Tokens/invocação", db.fmt(tok_per_inv))

st.divider()

# ── distribuição por projeto ──────────────────────────────────────────────────
col_a, col_b = st.columns([2, 2])

with col_a:
    st.subheader("Uso por projeto")
    proj_df = db.invocations_by_agent_project(project="all", days=days)
    proj_df = proj_df[proj_df["agent"] == agent] if not proj_df.empty else proj_df
    if not proj_df.empty:
        proj_df["project_short"] = proj_df["project"].apply(
            lambda p: (p or "?").replace("\\","/").rstrip("/").split("/")[-1]
        )
        fig = px.bar(proj_df, x="invocations", y="project_short",
                     orientation="h", text_auto=True,
                     color_discrete_sequence=["#8b5cf6"], height=300)
        fig.update_layout(yaxis={"categoryorder":"total ascending"},
                          plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                          font_color="#e2e8f0", margin=dict(l=0,r=0,t=10,b=0),
                          yaxis_title="", xaxis_title="Invocações")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados de projeto.")

with col_b:
    st.subheader("Tokens output por projeto")
    detail_df = db.usage_for_agent(agent, days)
    if not detail_df.empty:
        by_proj = detail_df.groupby("project")[["input","output","cache_read"]].sum().reset_index()
        by_proj["project_short"] = by_proj["project"].apply(
            lambda p: (p or "?").replace("\\","/").rstrip("/").split("/")[-1]
        )
        fig2 = px.bar(by_proj, x="output", y="project_short",
                      orientation="h", text=by_proj["output"].apply(db.fmt),
                      color_discrete_sequence=["#6366f1"], height=300)
        fig2.update_layout(yaxis={"categoryorder":"total ascending"},
                           plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                           font_color="#e2e8f0", margin=dict(l=0,r=0,t=10,b=0),
                           yaxis_title="", xaxis_title="Tokens output")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Sem dados de tokens.")

# ── linha do tempo ────────────────────────────────────────────────────────────
if not detail_df.empty:
    st.subheader("Tokens ao longo do tempo")
    by_date = detail_df.groupby("date")[["output","cache_read"]].sum().reset_index()
    fig3 = px.area(by_date, x="date", y="output",
                   color_discrete_sequence=["#8b5cf6"])
    fig3.update_layout(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                       font_color="#e2e8f0", margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig3, use_container_width=True)

# ── últimas invocações ────────────────────────────────────────────────────────
st.subheader("Últimas invocações")
recent = db.recent_invocations(agent, limit=20)
if not recent.empty:
    recent["project"] = recent["project"].apply(
        lambda p: (p or "?").replace("\\","/").rstrip("/").split("/")[-1]
    )
    st.dataframe(recent, use_container_width=True, hide_index=True)
else:
    st.info("Nenhuma invocação registrada.")
