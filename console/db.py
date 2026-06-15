"""Shared database helpers for the Domus Console."""
import hashlib
import json
import os
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

ROOT = Path(__file__).parent.parent
DB_PATH = Path.home() / ".domus" / "usage.db"
MACHINE_ID_PATH = Path.home() / ".domus" / "machine_id"


def machine_id() -> str:
    try:
        return MACHINE_ID_PATH.read_text(encoding="utf-8").strip() or "local"
    except OSError:
        return "local"

load_dotenv(ROOT / ".env.local")
load_dotenv(ROOT / ".env")

# ── pricing (USD per 1M tokens) ──────────────────────────────────────────────
MODEL_PRICES = {
    "claude-opus-4-8":   {"input": 15.00, "output": 75.00, "cache_read": 1.50,  "cache_create": 3.75},
    "claude-sonnet-4-6": {"input":  3.00, "output": 15.00, "cache_read": 0.30,  "cache_create": 0.375},
    "claude-haiku-4-5":  {"input":  0.80, "output":  4.00, "cache_read": 0.08,  "cache_create": 0.10},
    "gpt-5.5":           {"input": 10.00, "output": 30.00, "cache_read": 2.50,  "cache_create": 0.00},
}
_DEFAULT_PRICE = {"input": 3.00, "output": 15.00, "cache_read": 0.30, "cache_create": 0.375}


def estimated_cost(input_tokens, output_tokens, cache_read, cache_create, model) -> float:
    """Estimated USD cost for a token bundle. Unknown/NULL model falls back to sonnet pricing."""
    p = MODEL_PRICES.get(model) or _DEFAULT_PRICE
    return (
        (input_tokens  or 0) * p["input"]
        + (output_tokens or 0) * p["output"]
        + (cache_read    or 0) * p["cache_read"]
        + (cache_create  or 0) * p["cache_create"]
    ) / 1_000_000


def _database_url() -> str:
    url = os.getenv("DATABASE_URL", "").strip()
    if url:
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url
    return f"sqlite:///{DB_PATH.as_posix()}"


def is_postgres() -> bool:
    return _database_url().startswith(("postgresql://", "postgresql+"))


def backend_label() -> str:
    return "Neon Postgres" if is_postgres() else "SQLite local"


def database_location() -> str:
    if not is_postgres():
        return str(DB_PATH)
    parsed = urlparse(_database_url())
    return f"{parsed.hostname}/{parsed.path.lstrip('/')}"


@lru_cache(maxsize=1)
def _engine():
    if not is_postgres() and not DB_PATH.exists():
        return None
    return create_engine(_database_url(), pool_pre_ping=True)


def conn():
    return _engine()


def clear_cache():
    _engine.cache_clear()


def _redact_url(message: str) -> str:
    """Strip connection strings from exception messages before they propagate
    to Streamlit's UI traceback renderer."""
    import re
    url = os.getenv("DATABASE_URL", "")
    if url:
        message = message.replace(url, "[DATABASE_URL redacted]")
    message = re.sub(r"postgresql(?:\+\w+)?://[^\s\"']+",
                     "[connection string redacted]", message)
    return message


def _one(sql: str, params: dict | None = None):
    engine = conn()
    if engine is None:
        return None
    try:
        with engine.connect() as con:
            return con.execute(text(sql), params or {}).mappings().first()
    except Exception as exc:
        raise RuntimeError(_redact_url(str(exc))) from None


def _all(sql: str, params: dict | None = None):
    engine = conn()
    if engine is None:
        return []
    try:
        with engine.connect() as con:
            return con.execute(text(sql), params or {}).mappings().all()
    except Exception as exc:
        raise RuntimeError(_redact_url(str(exc))) from None


def _df(sql: str, params: dict | None = None) -> pd.DataFrame:
    engine = conn()
    if engine is None:
        return pd.DataFrame()
    try:
        with engine.connect() as con:
            return pd.read_sql_query(text(sql), con, params=params or {})
    except Exception as exc:
        raise RuntimeError(_redact_url(str(exc))) from None


def has_data() -> bool:
    try:
        row = _one("SELECT 1 FROM token_usage LIMIT 1")
        return row is not None
    except Exception:
        return False


def kpis(platform: str = "all", project: str = "all", days: int = 0) -> dict:
    where, params = _filters(platform, project, days)
    row = _one(f"SELECT COUNT(*) invocations FROM invocations WHERE 1=1 {where}", params)
    invocations = row["invocations"] if row else 0
    row2 = _one(
        f"SELECT SUM(output_tokens) output, SUM(input_tokens) inp,"
        f" SUM(cache_read_tokens) cr, SUM(cache_create_tokens) cc"
        f" FROM token_usage WHERE 1=1 {where}",
        params,
    )
    out = (row2["output"] or 0) if row2 else 0
    inp = (row2["inp"] or 0) if row2 else 0
    cr = (row2["cr"] or 0) if row2 else 0
    cc = (row2["cc"] or 0) if row2 else 0
    total = inp + cr + cc
    cache_hit = round(cr / total * 100, 1) if total else 0
    projects_q = _one(
        f"SELECT COUNT(DISTINCT project) n FROM token_usage WHERE 1=1 {where}",
        params,
    )
    agents_q = _one(
        f"SELECT COUNT(DISTINCT agent) n FROM invocations WHERE agent IS NOT NULL {where}",
        params,
    )
    return dict(
        invocations=invocations,
        output_tokens=out,
        input_tokens=inp,
        cache_read=cr,
        cache_create=cc,
        cache_hit=cache_hit,
        active_projects=projects_q["n"] if projects_q else 0,
        active_agents=agents_q["n"] if agents_q else 0,
    )


def invocations_by_agent(platform="all", project="all", days=0) -> pd.DataFrame:
    where, params = _filters(platform, project, days)
    return _df(
        f"SELECT agent, platform, COUNT(*) invocations FROM invocations"
        f" WHERE agent IS NOT NULL {where}"
        f" GROUP BY agent, platform ORDER BY invocations DESC",
        params,
    )


def invocations_over_time(platform="all", project="all", days=0) -> pd.DataFrame:
    where, params = _filters(platform, project, days)
    return _df(
        f"SELECT substr(ts,1,10) date, COUNT(*) invocations FROM invocations"
        f" WHERE ts IS NOT NULL {where}"
        f" GROUP BY date ORDER BY date",
        params,
    )


def invocations_by_agent_project(platform="all", project="all", days=0) -> pd.DataFrame:
    where, params = _filters(platform, project, days)
    return _df(
        f"SELECT agent, project, COUNT(*) invocations FROM invocations"
        f" WHERE agent IS NOT NULL {where}"
        f" GROUP BY agent, project ORDER BY agent, invocations DESC",
        params,
    )


def usage_by_agent(platform="all", project="all", days=0) -> pd.DataFrame:
    where, params = _filters(platform, project, days)
    df = _df(
        f"SELECT agent, COUNT(*) msgs,"
        f" SUM(input_tokens) input, SUM(output_tokens) output,"
        f" SUM(cache_read_tokens) cache_read, SUM(cache_create_tokens) cache_create"
        f" FROM token_usage WHERE agent IS NOT NULL {where}"
        f" GROUP BY agent ORDER BY output DESC",
        params,
    )
    if df.empty:
        return df
    df["total"] = df["input"] + df["cache_read"] + df["cache_create"]
    df["cache_hit_pct"] = (df["cache_read"] / df["total"].replace(0, float("nan")) * 100).round(1)
    return df


def cost_by_agent(platform="all", project="all", days=0) -> pd.DataFrame:
    """Estimated USD cost per agent, computed in Python using per-model pricing."""
    where, params = _filters(platform, project, days)
    raw = _df(
        f"SELECT agent, model,"
        f" SUM(input_tokens) input, SUM(output_tokens) output,"
        f" SUM(cache_read_tokens) cache_read, SUM(cache_create_tokens) cache_create,"
        f" COUNT(*) msgs"
        f" FROM token_usage WHERE agent IS NOT NULL {where}"
        f" GROUP BY agent, model",
        params,
    )
    if raw.empty:
        return pd.DataFrame(columns=["agent", "msgs", "output_tokens", "estimated_cost_usd"])
    raw["estimated_cost_usd"] = raw.apply(
        lambda r: estimated_cost(r["input"], r["output"], r["cache_read"], r["cache_create"], r["model"]),
        axis=1,
    )
    return (
        raw.groupby("agent")
        .agg(msgs=("msgs", "sum"), output_tokens=("output", "sum"),
             estimated_cost_usd=("estimated_cost_usd", "sum"))
        .reset_index()
        .sort_values("estimated_cost_usd", ascending=False)
    )


def usage_by_project(platform="all", project="all", days=0) -> pd.DataFrame:
    where, params = _filters(platform, project, days)
    return _df(
        f"SELECT platform, project, SUM(input_tokens) input,"
        f" SUM(output_tokens) output, SUM(cache_read_tokens) cache_read"
        f" FROM token_usage WHERE 1=1 {where}"
        f" GROUP BY platform, project ORDER BY output DESC",
        params,
    )


def usage_for_agent(agent: str, days=0) -> pd.DataFrame:
    where, params = _days_filter(days)
    params["agent"] = agent
    return _df(
        f"SELECT project, substr(ts,1,10) date,"
        f" SUM(input_tokens) input, SUM(output_tokens) output,"
        f" SUM(cache_read_tokens) cache_read"
        f" FROM token_usage WHERE agent=:agent {where}"
        f" GROUP BY project, date ORDER BY date",
        params,
    )


def recent_invocations(agent: str, limit=20) -> pd.DataFrame:
    return _df(
        "SELECT ts, project, branch, platform FROM invocations"
        " WHERE agent=:agent ORDER BY ts DESC LIMIT :limit",
        {"agent": agent, "limit": limit},
    )


def usage_for_project(project: str, days=0) -> pd.DataFrame:
    where, params = _days_filter(days)
    params["project"] = f"%{project}%"
    return _df(
        f"SELECT platform, agent, SUM(input_tokens) input,"
        f" SUM(output_tokens) output, SUM(cache_read_tokens) cache_read"
        f" FROM token_usage WHERE project LIKE :project {where}"
        f" GROUP BY platform, agent ORDER BY output DESC",
        params,
    )


def all_agents() -> list[str]:
    rows = _all("SELECT DISTINCT agent FROM invocations WHERE agent IS NOT NULL ORDER BY agent")
    return [r["agent"] for r in rows]


def all_projects() -> list[str]:
    rows = _all("SELECT DISTINCT project FROM token_usage WHERE project IS NOT NULL ORDER BY project")
    return [r["project"] for r in rows]


def all_platforms() -> list[str]:
    rows = _all("SELECT DISTINCT platform FROM token_usage ORDER BY platform")
    return [r["platform"] for r in rows]


def last_collect_info() -> dict:
    row = _one("SELECT COUNT(*) n, MAX(mtime) last FROM ingested_files")
    if is_postgres():
        return dict(n=row["n"] if row else 0, last=row["last"] if row else None, db_size=0)
    size = DB_PATH.stat().st_size if DB_PATH.exists() else 0
    return dict(n=row["n"] if row else 0, last=row["last"] if row else None, db_size=size)


def _filters(platform: str, project: str, days: int):
    clauses, params = [], {}
    if platform != "all":
        clauses.append("AND platform=:platform")
        params["platform"] = platform
    if project != "all":
        clauses.append("AND project LIKE :project")
        params["project"] = f"%{project}%"
    if days:
        clause, day_params = _days_filter(days)
        clauses.append(clause)
        params.update(day_params)
    return " ".join(clauses), params


def _days_filter(days: int):
    if not days:
        return "", {}
    if is_postgres():
        return "AND CAST(ts AS timestamp) >= now() - (:days * interval '1 day')", {"days": days}
    return "AND ts >= datetime('now', :days_expr)", {"days_expr": f"-{days} days"}


def fmt(n) -> str:
    if n is None:
        return "-"
    n = int(n)
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


# ── agent versioning ─────────────────────────────────────────────────────────

_VERSIONS_DDL_SQLITE = """
CREATE TABLE IF NOT EXISTS agent_versions (
    id INTEGER PRIMARY KEY,
    agent TEXT NOT NULL,
    version INTEGER NOT NULL,
    spec_snapshot TEXT NOT NULL,
    spec_hash TEXT NOT NULL,
    diff_summary TEXT,
    platforms TEXT,
    deployed_at TEXT NOT NULL,
    deployed_by TEXT DEFAULT 'local',
    UNIQUE (agent, version)
);
CREATE INDEX IF NOT EXISTS idx_versions_agent ON agent_versions(agent);
CREATE INDEX IF NOT EXISTS idx_versions_deployed_at ON agent_versions(deployed_at);
"""

_VERSIONS_DDL_POSTGRES = """
CREATE TABLE IF NOT EXISTS agent_versions (
    id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    agent TEXT NOT NULL,
    version INTEGER NOT NULL,
    spec_snapshot TEXT NOT NULL,
    spec_hash TEXT NOT NULL,
    diff_summary TEXT,
    platforms TEXT,
    deployed_at TEXT NOT NULL,
    deployed_by TEXT DEFAULT 'local',
    UNIQUE (agent, version)
);
CREATE INDEX IF NOT EXISTS idx_versions_agent ON agent_versions(agent);
CREATE INDEX IF NOT EXISTS idx_versions_deployed_at ON agent_versions(deployed_at);
"""


def _exec(sql: str, params: dict):
    engine = conn()
    if engine is None:
        raise RuntimeError("Banco indisponível para gravação.")
    with engine.begin() as con:
        con.execute(text(sql), params)


def _ensure_versions_table():
    engine = conn()
    if engine is None:
        return
    ddl = _VERSIONS_DDL_POSTGRES if is_postgres() else _VERSIONS_DDL_SQLITE
    with engine.begin() as con:
        for stmt in ddl.split(";"):
            if stmt.strip():
                con.execute(text(stmt))


def _canonical_hash(agent_spec: dict) -> str:
    blob = json.dumps(agent_spec, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def latest_version(agent: str) -> dict | None:
    row = _one(
        "SELECT version, spec_snapshot, spec_hash FROM agent_versions"
        " WHERE agent=:agent ORDER BY version DESC LIMIT 1",
        {"agent": agent},
    )
    return dict(row) if row else None


def record_agent_version(agent: str, agent_spec: dict,
                         platforms: list[str], diff_summary: str) -> int | None:
    """Persist a spec snapshot. Returns the new version number, or None if unchanged."""
    _ensure_versions_table()
    prev = latest_version(agent)
    new_hash = _canonical_hash(agent_spec)
    if prev and prev["spec_hash"] == new_hash:
        return None
    next_v = (prev["version"] + 1) if prev else 1
    _exec(
        "INSERT INTO agent_versions"
        " (agent, version, spec_snapshot, spec_hash, diff_summary,"
        "  platforms, deployed_at, deployed_by)"
        " VALUES (:agent, :version, :snap, :hash, :diff, :plats, :at, :by)",
        {
            "agent": agent, "version": next_v,
            "snap": json.dumps(agent_spec, ensure_ascii=False),
            "hash": new_hash, "diff": diff_summary,
            "plats": json.dumps(platforms, ensure_ascii=False),
            "at": datetime.now(timezone.utc).isoformat(),
            "by": machine_id(),
        },
    )
    return next_v


def version_history(agent: str) -> pd.DataFrame:
    _ensure_versions_table()
    return _df(
        "SELECT version, deployed_at, deployed_by, platforms, diff_summary, spec_hash"
        " FROM agent_versions WHERE agent=:agent ORDER BY version DESC",
        {"agent": agent},
    )


def version_efficiency(agent: str) -> pd.DataFrame:
    """Efficiency metrics per version window (until next deploy or open-ended)."""
    _ensure_versions_table()
    return _df(
        "SELECT"
        " v.version, v.deployed_at,"
        " COALESCE("
        "   CAST(SUM(u.cache_read_tokens) AS REAL)"
        "   / NULLIF(SUM(u.input_tokens + u.cache_read_tokens + u.cache_create_tokens), 0)"
        "   * 100, 0) AS avg_cache_hit_pct,"
        " COALESCE("
        "   CAST(SUM(u.output_tokens) AS REAL)"
        "   / NULLIF(COUNT(DISTINCT i.id), 0), 0) AS avg_tokens_per_inv,"
        " COUNT(DISTINCT i.id) AS invocations"
        " FROM agent_versions v"
        " LEFT JOIN agent_versions nx"
        "        ON nx.agent = v.agent AND nx.version = v.version + 1"
        " LEFT JOIN token_usage u"
        "        ON u.agent = v.agent"
        "       AND u.ts >= v.deployed_at"
        "       AND (nx.deployed_at IS NULL OR u.ts < nx.deployed_at)"
        " LEFT JOIN invocations i"
        "        ON i.agent = v.agent"
        "       AND i.ts  >= v.deployed_at"
        "       AND (nx.deployed_at IS NULL OR i.ts  < nx.deployed_at)"
        " WHERE v.agent = :agent"
        " GROUP BY v.version, v.deployed_at"
        " ORDER BY v.version",
        {"agent": agent},
    )


def version_snapshot(agent: str, version: int) -> dict | None:
    row = _one(
        "SELECT spec_snapshot FROM agent_versions WHERE agent=:agent AND version=:v",
        {"agent": agent, "v": version},
    )
    if row is None:
        return None
    try:
        return json.loads(row["spec_snapshot"])
    except Exception:
        return None


def threshold_alerts() -> list[dict]:
    """Return threshold violations for the Settings page.

    Each dict: {type: 'cache'|'spike'|'inactive', agent: str, msg: str}
    """
    alerts = []

    # 1. Cache hit < 70% (all-time, min 10K input-side tokens)
    eff = usage_by_agent()
    if not eff.empty:
        for _, r in eff.iterrows():
            total = (r["input"] or 0) + (r["cache_read"] or 0) + (r.get("cache_create", 0) or 0)
            if total >= 10_000 and pd.notna(r["cache_hit_pct"]) and r["cache_hit_pct"] < 70:
                alerts.append({"type": "cache", "agent": r["agent"],
                                "msg": f"Cache hit {r['cache_hit_pct']:.0f}% (limite: 70%)"})

    # 2. Spike > 50%: tok/inv last 7d vs all-time
    recent_tok = usage_by_agent(days=7)
    recent_inv = invocations_by_agent(days=7)
    all_inv    = invocations_by_agent()

    if not recent_tok.empty and not recent_inv.empty and not all_inv.empty:
        r_inv = recent_inv.groupby("agent")["invocations"].sum()
        h_inv = all_inv.groupby("agent")["invocations"].sum()
        for _, row in recent_tok.iterrows():
            agent = row["agent"]
            inv_r = r_inv.get(agent, 0)
            inv_h = h_inv.get(agent, 0)
            if inv_r < 3 or inv_h < 5:
                continue
            avg_r = row["output"] / inv_r if inv_r else 0
            h_row = eff[eff["agent"] == agent]
            avg_h = float(h_row["output"].sum() / inv_h) if not h_row.empty and inv_h else 0
            if avg_h > 0 and avg_r > avg_h * 1.5:
                pct = (avg_r / avg_h - 1) * 100
                alerts.append({"type": "spike", "agent": agent,
                                "msg": f"{avg_r/1000:.1f}K tok/inv (7d) vs {avg_h/1000:.1f}K histórico (+{pct:.0f}%)"})

    # 3. Inactive 30 days
    active_30d = set(invocations_by_agent(days=30)["agent"].tolist()) \
        if not invocations_by_agent(days=30).empty else set()
    for agent in all_agents():
        if agent not in active_30d:
            alerts.append({"type": "inactive", "agent": agent,
                            "msg": "Sem invocações nos últimos 30 dias"})

    return alerts


def cache_badge(pct) -> str:
    if pct is None or str(pct) == "nan":
        return "-"
    pct = float(pct)
    if pct >= 85:
        return f'<span class="badge-green">{pct:.0f}%</span>'
    if pct >= 70:
        return f'<span class="badge-yellow">{pct:.0f}%</span>'
    return f'<span class="badge-red">{pct:.0f}%</span>'
