"""Detalhe por agent."""
import difflib
import json
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

# ── dados comuns ──────────────────────────────────────────────────────────────
inv_df   = db.invocations_by_agent(project="all", days=days)
tok_df   = db.usage_by_agent(project="all", days=days)
cost_df  = db.cost_by_agent(project="all", days=days)
detail_df = db.usage_for_agent(agent, days)

agent_inv_row = inv_df[inv_df["agent"] == agent]["invocations"].sum() if not inv_df.empty else 0
agent_tok_row = (tok_df[tok_df["agent"] == agent].iloc[0]
                 if not tok_df.empty and (tok_df["agent"] == agent).any() else None)
agent_cost = float(cost_df[cost_df["agent"] == agent]["estimated_cost_usd"].sum()) if not cost_df.empty else 0.0

tab_overview, tab_versions = st.tabs(["Visão geral", "Histórico de versões"])

# ══════════════════════════════════════════════════════════════════════════════
with tab_overview:

    st.subheader(f"🤖 {agent}")

    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    c1.metric("Invocações", int(agent_inv_row))
    if agent_tok_row is not None:
        c2.metric("Tokens output", db.fmt(agent_tok_row["output"]))
        c3.metric("Tokens input (efetivo)", db.fmt(agent_tok_row["input"]))
        c4.metric("Cache hit", f"{agent_tok_row['cache_hit_pct']:.1f}%"
                  if pd.notna(agent_tok_row["cache_hit_pct"]) else "—")
        tok_per_inv = agent_tok_row["output"] / agent_inv_row if agent_inv_row else 0
        c5.metric("Tokens/invocação", db.fmt(tok_per_inv))
        c6.metric("Custo total (USD est.)", f"${agent_cost:,.2f}")
        cost_per_inv = agent_cost / agent_inv_row if agent_inv_row else 0.0
        c7.metric("Custo/invocação (USD)", f"${cost_per_inv:,.4f}")

    st.divider()

    # ── distribuição por projeto ──────────────────────────────────────────────
    col_a, col_b = st.columns([2, 2])

    with col_a:
        st.subheader("Uso por projeto")
        proj_df = db.invocations_by_agent_project(project="all", days=days)
        proj_df = proj_df[proj_df["agent"] == agent] if not proj_df.empty else proj_df
        if not proj_df.empty:
            proj_df["project_short"] = proj_df["project"].apply(
                lambda p: (p or "?").replace("\\", "/").rstrip("/").split("/")[-1]
            )
            fig = px.bar(proj_df, x="invocations", y="project_short",
                         orientation="h", text_auto=True,
                         color_discrete_sequence=["#8b5cf6"], height=300)
            fig.update_layout(yaxis={"categoryorder": "total ascending"},
                              plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                              font_color="#e2e8f0", margin=dict(l=0, r=0, t=10, b=0),
                              yaxis_title="", xaxis_title="Invocações")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem dados de projeto.")

    with col_b:
        st.subheader("Tokens output por projeto")
        if not detail_df.empty:
            by_proj = detail_df.groupby("project")[["input", "output", "cache_read"]].sum().reset_index()
            by_proj["project_short"] = by_proj["project"].apply(
                lambda p: (p or "?").replace("\\", "/").rstrip("/").split("/")[-1]
            )
            fig2 = px.bar(by_proj, x="output", y="project_short",
                          orientation="h", text=by_proj["output"].apply(db.fmt),
                          color_discrete_sequence=["#6366f1"], height=300)
            fig2.update_layout(yaxis={"categoryorder": "total ascending"},
                               plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                               font_color="#e2e8f0", margin=dict(l=0, r=0, t=10, b=0),
                               yaxis_title="", xaxis_title="Tokens output")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Sem dados de tokens.")

    # ── linha do tempo ────────────────────────────────────────────────────────
    if not detail_df.empty:
        st.subheader("Tokens ao longo do tempo")
        by_date = detail_df.groupby("date")[["output", "cache_read"]].sum().reset_index()
        fig3 = px.area(by_date, x="date", y="output",
                       color_discrete_sequence=["#8b5cf6"])
        fig3.update_layout(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                           font_color="#e2e8f0", margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig3, use_container_width=True)

    # ── últimas invocações ────────────────────────────────────────────────────
    st.subheader("Últimas invocações")
    recent = db.recent_invocations(agent, limit=20)
    if not recent.empty:
        recent["project"] = recent["project"].apply(
            lambda p: (p or "?").replace("\\", "/").rstrip("/").split("/")[-1]
        )
        st.dataframe(recent, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma invocação registrada.")

# ══════════════════════════════════════════════════════════════════════════════
with tab_versions:
    st.subheader(f"Histórico de versões — {agent}")

    hist_df = db.version_history(agent)
    eff_df  = db.version_efficiency(agent)

    if hist_df.empty:
        st.info("Nenhuma versão registrada ainda. Faça um deploy via Gestão de Agents para começar.")
    else:
        # ── tabela de versões ─────────────────────────────────────────────────
        display = hist_df.copy()
        display["deployed_at"] = display["deployed_at"].str[:19].str.replace("T", " ")
        display["deployed_by"] = display["deployed_by"].str[:8]

        # merge efficiency
        if not eff_df.empty:
            eff_slim = eff_df[["version", "avg_cache_hit_pct", "avg_tokens_per_inv", "invocations"]].copy()
            eff_slim.columns = ["version", "Cache hit %", "Tok/inv", "Invocações"]
            eff_slim["Cache hit %"] = eff_slim["Cache hit %"].apply(lambda x: f"{x:.0f}%")
            eff_slim["Tok/inv"] = eff_slim["Tok/inv"].apply(lambda x: db.fmt(int(x)) if x else "—")
            display = display.merge(eff_slim, on="version", how="left")

        display = display.rename(columns={
            "version": "v", "deployed_at": "Implantado em",
            "deployed_by": "Por (machine)", "diff_summary": "O que mudou",
        })
        cols_show = [c for c in ["v", "Implantado em", "Por (machine)", "O que mudou",
                                  "Cache hit %", "Tok/inv", "Invocações"] if c in display.columns]
        st.dataframe(display[cols_show], use_container_width=True, hide_index=True)

        # ── delta de eficiência entre versões ─────────────────────────────────
        if not eff_df.empty and len(eff_df) > 1:
            st.subheader("Delta de eficiência entre versões")
            eff_sorted = eff_df.sort_values("version").reset_index(drop=True)
            delta_cols = st.columns(len(eff_sorted) - 1)
            for i, col in enumerate(delta_cols):
                prev_row = eff_sorted.iloc[i]
                curr_row = eff_sorted.iloc[i + 1]
                d_cache = curr_row["avg_cache_hit_pct"] - prev_row["avg_cache_hit_pct"]
                d_tok_pct = ((curr_row["avg_tokens_per_inv"] - prev_row["avg_tokens_per_inv"])
                             / prev_row["avg_tokens_per_inv"] * 100
                             if prev_row["avg_tokens_per_inv"] else 0)
                with col:
                    st.markdown(f"**v{int(prev_row['version'])} → v{int(curr_row['version'])}**")
                    st.metric("Δ Cache hit", f"{d_cache:+.1f}pp",
                              delta=f"{d_cache:+.1f}pp")
                    st.metric("Δ Tok/inv", f"{d_tok_pct:+.1f}%",
                              delta=f"{d_tok_pct:+.1f}%", delta_color="inverse")

        # ── gráfico timeline com marcadores de deploy ─────────────────────────
        if not detail_df.empty and not eff_df.empty:
            st.subheader("Eficiência ao longo do tempo com deploys")
            by_date = detail_df.groupby("date")[["output", "cache_read"]].sum().reset_index()
            figv = px.area(by_date, x="date", y="output",
                           color_discrete_sequence=["#8b5cf6"],
                           labels={"output": "Tokens output", "date": "Data"})
            for _, vrow in eff_df.iterrows():
                figv.add_vline(
                    x=str(vrow["deployed_at"])[:10],
                    line_dash="dash", line_color="#f59e0b",
                    annotation_text=f"v{int(vrow['version'])}",
                    annotation_position="top left",
                )
            figv.update_layout(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                               font_color="#e2e8f0", margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(figv, use_container_width=True)

        # ── inspeção de snapshot ──────────────────────────────────────────────
        st.subheader("Inspecionar spec por versão")
        versions_available = sorted(hist_df["version"].tolist(), reverse=True)

        if len(versions_available) >= 2:
            ca, cb = st.columns(2)
            va = ca.selectbox("Versão A", versions_available, index=1, key="va")
            vb = cb.selectbox("Versão B", versions_available, index=0, key="vb")
            if va != vb:
                snap_a = db.version_snapshot(agent, va)
                snap_b = db.version_snapshot(agent, vb)
                if snap_a and snap_b:
                    lines_a = json.dumps(snap_a, indent=2, ensure_ascii=False).splitlines(keepends=True)
                    lines_b = json.dumps(snap_b, indent=2, ensure_ascii=False).splitlines(keepends=True)
                    diff = list(difflib.unified_diff(
                        lines_a, lines_b,
                        fromfile=f"v{va}", tofile=f"v{vb}", lineterm=""
                    ))
                    if diff:
                        st.code("\n".join(diff), language="diff")
                    else:
                        st.info("Specs idênticas (re-deploy sem mudança).")
        else:
            v_sel = st.selectbox("Versão", versions_available)
            snap = db.version_snapshot(agent, v_sel)
            if snap:
                st.code(json.dumps(snap, indent=2, ensure_ascii=False), language="json")
