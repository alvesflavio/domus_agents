"""Domus Console — entry point.

Run:  streamlit run console/app.py
"""
import streamlit as st

st.set_page_config(
    page_title="Domus Console",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── shared CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stSidebar"] { min-width: 220px; max-width: 220px; }
  .metric-card {
    background: #1e1e2e; border: 1px solid #313244;
    border-radius: 10px; padding: 1rem 1.2rem;
  }
  .metric-val  { font-size: 2rem; font-weight: 700; font-family: monospace; }
  .metric-lbl  { font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: .06em; }
  .badge-green  { background:#1a3a2a; color:#4ade80; padding:2px 8px; border-radius:99px; font-size:.75rem; }
  .badge-yellow { background:#3a3010; color:#facc15; padding:2px 8px; border-radius:99px; font-size:.75rem; }
  .badge-red    { background:#3a1010; color:#f87171; padding:2px 8px; border-radius:99px; font-size:.75rem; }
</style>
""", unsafe_allow_html=True)

pg = st.navigation([
    st.Page("pages/dashboard.py",    title="Dashboard",       icon="📊", default=True),
    st.Page("pages/agent_detail.py", title="Agents",          icon="🤖"),
    st.Page("pages/project_detail.py",title="Projetos",       icon="📁"),
    st.Page("pages/agent_manager.py", title="Gestão de Agents",icon="⚙️"),
    st.Page("pages/settings.py",      title="Configurações",  icon="🔧"),
])
pg.run()
