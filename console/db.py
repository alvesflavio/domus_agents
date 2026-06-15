"""Shared DB helpers — cached connection + all queries used across pages."""
import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st

DB_PATH = Path.home() / ".domus" / "usage.db"


@st.cache_resource
def _conn():
    if not DB_PATH.exists():
        return None
    con = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def conn():
    return _conn()


def has_data() -> bool:
    c = conn()
    if c is None:
        return False
    try:
        return c.execute("SELECT 1 FROM token_usage LIMIT 1").fetchone() is not None
    except Exception:
        return False


# ── KPIs ─────────────────────────────────────────────────────────────────────

def kpis(platform: str = "all", project: str = "all", days: int = 0) -> dict:
    c = conn()
    if c is None:
        return {}
    where, p = _filters(platform, project, days)
    row = c.execute(
        f"SELECT COUNT(*) invocations FROM invocations WHERE 1=1 {where}", p
    ).fetchone()
    invocations = row["invocations"] if row else 0
    row2 = c.execute(
        f"SELECT SUM(output_tokens) output, SUM(input_tokens) inp,"
        f" SUM(cache_read_tokens) cr, SUM(cache_create_tokens) cc"
        f" FROM token_usage WHERE 1=1 {where}", p
    ).fetchone()
    out = row2["output"] or 0
    inp = row2["inp"] or 0
    cr  = row2["cr"] or 0
    cc  = row2["cc"] or 0
    total = inp + cr + cc
    cache_hit = round(cr / total * 100, 1) if total else 0
    projects_q = c.execute(
        f"SELECT COUNT(DISTINCT project) n FROM token_usage WHERE 1=1 {where}", p
    ).fetchone()
    agents_q = c.execute(
        f"SELECT COUNT(DISTINCT agent) n FROM invocations WHERE agent IS NOT NULL {where}", p
    ).fetchone()
    return dict(invocations=invocations, output_tokens=out, input_tokens=inp,
                cache_read=cr, cache_create=cc, cache_hit=cache_hit,
                active_projects=projects_q["n"] if projects_q else 0,
                active_agents=agents_q["n"] if agents_q else 0)


# ── Invocations ───────────────────────────────────────────────────────────────

def invocations_by_agent(platform="all", project="all", days=0) -> pd.DataFrame:
    c = conn()
    if c is None:
        return pd.DataFrame()
    where, p = _filters(platform, project, days)
    return pd.read_sql_query(
        f"SELECT agent, platform, COUNT(*) invocations FROM invocations"
        f" WHERE agent IS NOT NULL {where}"
        f" GROUP BY agent, platform ORDER BY invocations DESC", c, params=p)


def invocations_over_time(platform="all", project="all", days=0) -> pd.DataFrame:
    c = conn()
    if c is None:
        return pd.DataFrame()
    where, p = _filters(platform, project, days)
    return pd.read_sql_query(
        f"SELECT substr(ts,1,10) date, COUNT(*) invocations FROM invocations"
        f" WHERE ts IS NOT NULL {where}"
        f" GROUP BY date ORDER BY date", c, params=p)


def invocations_by_agent_project(platform="all", project="all", days=0) -> pd.DataFrame:
    c = conn()
    if c is None:
        return pd.DataFrame()
    where, p = _filters(platform, project, days)
    return pd.read_sql_query(
        f"SELECT agent, project, COUNT(*) invocations FROM invocations"
        f" WHERE agent IS NOT NULL {where}"
        f" GROUP BY agent, project ORDER BY agent, invocations DESC", c, params=p)


# ── Token usage ───────────────────────────────────────────────────────────────

def usage_by_agent(platform="all", project="all", days=0) -> pd.DataFrame:
    c = conn()
    if c is None:
        return pd.DataFrame()
    where, p = _filters(platform, project, days)
    df = pd.read_sql_query(
        f"SELECT agent, COUNT(*) msgs,"
        f" SUM(input_tokens) input, SUM(output_tokens) output,"
        f" SUM(cache_read_tokens) cache_read, SUM(cache_create_tokens) cache_create"
        f" FROM token_usage WHERE agent IS NOT NULL {where}"
        f" GROUP BY agent ORDER BY output DESC", c, params=p)
    if df.empty:
        return df
    df["total"] = df["input"] + df["cache_read"] + df["cache_create"]
    df["cache_hit_pct"] = (df["cache_read"] / df["total"].replace(0, float("nan")) * 100).round(1)
    return df


def usage_by_project(platform="all", project="all", days=0) -> pd.DataFrame:
    c = conn()
    if c is None:
        return pd.DataFrame()
    where, p = _filters(platform, project, days)
    return pd.read_sql_query(
        f"SELECT platform, project, SUM(input_tokens) input,"
        f" SUM(output_tokens) output, SUM(cache_read_tokens) cache_read"
        f" FROM token_usage WHERE 1=1 {where}"
        f" GROUP BY platform, project ORDER BY output DESC", c, params=p)


def usage_for_agent(agent: str, days=0) -> pd.DataFrame:
    c = conn()
    if c is None:
        return pd.DataFrame()
    where, p = " AND ts >= datetime('now', ?)", [f"-{days} days"] if days else ("", [])
    return pd.read_sql_query(
        f"SELECT project, substr(ts,1,10) date,"
        f" SUM(input_tokens) input, SUM(output_tokens) output,"
        f" SUM(cache_read_tokens) cache_read"
        f" FROM token_usage WHERE agent=? {where}"
        f" GROUP BY project, date ORDER BY date", c,
        params=[agent] + (p if days else []))


def recent_invocations(agent: str, limit=20) -> pd.DataFrame:
    c = conn()
    if c is None:
        return pd.DataFrame()
    return pd.read_sql_query(
        "SELECT ts, project, branch, platform FROM invocations"
        " WHERE agent=? ORDER BY ts DESC LIMIT ?", c, params=[agent, limit])


def usage_for_project(project: str, days=0) -> pd.DataFrame:
    c = conn()
    if c is None:
        return pd.DataFrame()
    where, p = " AND ts >= datetime('now', ?)", [f"-{days} days"] if days else ("", [])
    return pd.read_sql_query(
        f"SELECT platform, agent, SUM(input_tokens) input,"
        f" SUM(output_tokens) output, SUM(cache_read_tokens) cache_read"
        f" FROM token_usage WHERE project LIKE ? {where}"
        f" GROUP BY platform, agent ORDER BY output DESC", c,
        params=[f"%{project}%"] + (p if days else []))


# ── Misc ──────────────────────────────────────────────────────────────────────

def all_agents() -> list[str]:
    c = conn()
    if c is None:
        return []
    rows = c.execute(
        "SELECT DISTINCT agent FROM invocations WHERE agent IS NOT NULL ORDER BY agent"
    ).fetchall()
    return [r["agent"] for r in rows]


def all_projects() -> list[str]:
    c = conn()
    if c is None:
        return []
    rows = c.execute(
        "SELECT DISTINCT project FROM token_usage WHERE project IS NOT NULL ORDER BY project"
    ).fetchall()
    return [r["project"] for r in rows]


def all_platforms() -> list[str]:
    c = conn()
    if c is None:
        return []
    rows = c.execute("SELECT DISTINCT platform FROM token_usage ORDER BY platform").fetchall()
    return [r["platform"] for r in rows]


def last_collect_info() -> dict:
    c = conn()
    if c is None:
        return {}
    row = c.execute(
        "SELECT COUNT(*) n, MAX(mtime) last FROM ingested_files"
    ).fetchone()
    sz = DB_PATH.stat().st_size if DB_PATH.exists() else 0
    return dict(n=row["n"] if row else 0, last=row["last"] if row else None, db_size=sz)


# ── helpers ───────────────────────────────────────────────────────────────────

def _filters(platform: str, project: str, days: int):
    clauses, params = [], []
    if platform != "all":
        clauses.append("AND platform=?"); params.append(platform)
    if project != "all":
        clauses.append("AND project LIKE ?"); params.append(f"%{project}%")
    if days:
        clauses.append(f"AND ts >= datetime('now', '-{days} days')")
    return " ".join(clauses), params


def fmt(n) -> str:
    if n is None:
        return "—"
    n = int(n)
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def cache_badge(pct) -> str:
    if pct is None or str(pct) == "nan":
        return "—"
    pct = float(pct)
    if pct >= 85:
        return f'<span class="badge-green">{pct:.0f}%</span>'
    if pct >= 70:
        return f'<span class="badge-yellow">{pct:.0f}%</span>'
    return f'<span class="badge-red">{pct:.0f}%</span>'
