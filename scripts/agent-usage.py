#!/usr/bin/env python3
"""Domus agent usage tracker.

Reads Claude Code and Codex session transcripts already on disk (zero model
tokens spent) and aggregates per-agent / per-project token usage into a local
SQLite database.

Usage:
  python scripts/agent-usage.py collect          # incremental ingest
  python scripts/agent-usage.py report           # summary tables
  python scripts/agent-usage.py report --agent security-reviewer
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
DB_PATH = HOME / ".domus" / "usage.db"
CLAUDE_PROJECTS = HOME / ".claude" / "projects"
CODEX_SESSION_DIRS = [HOME / ".codex" / "sessions", HOME / ".codex" / "archived_sessions"]

DOMUS_AGENTS = {
    "software-architect", "product-strategist", "copy-strategist",
    "ux-ui-designer", "security-reviewer", "task-ops-manager",
    "devops-release-manager", "workstyle-standards-coordinator",
    "code-reviewer", "test-debugger", "implementation-planner",
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS ingested_files (
    path TEXT PRIMARY KEY,
    mtime REAL NOT NULL,
    size INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS invocations (
    id INTEGER PRIMARY KEY,
    platform TEXT NOT NULL,            -- claude | codex
    project TEXT,                      -- cwd of the session
    branch TEXT,
    agent TEXT NOT NULL,               -- subagent/skill name
    session_id TEXT,
    ts TEXT,                           -- ISO timestamp
    source_file TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS token_usage (
    id INTEGER PRIMARY KEY,
    platform TEXT NOT NULL,
    project TEXT,
    branch TEXT,
    agent TEXT,                        -- NULL = main session (not a subagent)
    session_id TEXT,
    ts TEXT,
    model TEXT,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    cache_read_tokens INTEGER DEFAULT 0,
    cache_create_tokens INTEGER DEFAULT 0,
    source_file TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS agent_map (
    agent_id TEXT PRIMARY KEY,         -- Claude Code spawned-agent id
    agent_type TEXT NOT NULL,
    source_file TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_usage_agent ON token_usage(agent);
CREATE INDEX IF NOT EXISTS idx_usage_project ON token_usage(project);
CREATE INDEX IF NOT EXISTS idx_inv_agent ON invocations(agent);
"""


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA)
    return con


def file_changed(con, path: Path) -> bool:
    st = path.stat()
    row = con.execute("SELECT mtime, size FROM ingested_files WHERE path=?", (str(path),)).fetchone()
    return row is None or row[0] != st.st_mtime or row[1] != st.st_size


def mark_ingested(con, path: Path):
    st = path.stat()
    con.execute(
        "INSERT OR REPLACE INTO ingested_files(path, mtime, size) VALUES (?,?,?)",
        (str(path), st.st_mtime, st.st_size),
    )


def clear_file_rows(con, path: Path):
    con.execute("DELETE FROM invocations WHERE source_file=?", (str(path),))
    con.execute("DELETE FROM token_usage WHERE source_file=?", (str(path),))


# ---------------------------------------------------------------- Claude Code

def _walk_agent_ids(obj, found):
    """Recursively find {agentId, agentType} pairs anywhere in a record."""
    if isinstance(obj, dict):
        if obj.get("agentId") and obj.get("agentType"):
            found[obj["agentId"]] = obj["agentType"]
        for v in obj.values():
            _walk_agent_ids(v, found)
    elif isinstance(obj, list):
        for v in obj:
            _walk_agent_ids(v, found)


def _insert_usage(con, platform, r, msg, agent, path):
    usage = msg.get("usage")
    if not isinstance(usage, dict):
        return
    con.execute(
        "INSERT INTO token_usage(platform, project, branch, agent, session_id, ts, model,"
        " input_tokens, output_tokens, cache_read_tokens, cache_create_tokens, source_file)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (platform, r.get("cwd"), r.get("gitBranch"), agent, r.get("sessionId"),
         r.get("timestamp"), msg.get("model"),
         usage.get("input_tokens", 0) or 0,
         usage.get("output_tokens", 0) or 0,
         usage.get("cache_read_input_tokens", 0) or 0,
         usage.get("cache_creation_input_tokens", 0) or 0,
         str(path)),
    )


def ingest_claude_file(con, path: Path):
    """Main-session transcript: records Task invocations, the agentId->agentType
    map (used to attribute subagent transcripts), and main-session usage."""
    agent_ids = {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                # cheap pre-filter keeps the JSON walk off irrelevant lines
                walk = '"agentId"' in line
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if walk:
                    _walk_agent_ids(r, agent_ids)
                msg = r.get("message")
                if not isinstance(msg, dict):
                    continue
                if msg.get("role") == "assistant":
                    _insert_usage(con, "claude", r, msg, None, path)
                for block in msg.get("content") or []:
                    if isinstance(block, dict) and block.get("type") == "tool_use" \
                            and block.get("name") in ("Task", "Agent"):
                        inp = block.get("input") or {}
                        agent = inp.get("subagent_type") or "general-purpose"
                        con.execute(
                            "INSERT INTO invocations(platform, project, branch, agent,"
                            " session_id, ts, source_file) VALUES ('claude',?,?,?,?,?,?)",
                            (r.get("cwd"), r.get("gitBranch"), agent,
                             r.get("sessionId"), r.get("timestamp"), str(path)),
                        )
    except OSError:
        return
    for agent_id, agent_type in agent_ids.items():
        con.execute(
            "INSERT OR REPLACE INTO agent_map(agent_id, agent_type, source_file) VALUES (?,?,?)",
            (agent_id, agent_type, str(path)),
        )


def ingest_claude_subagent_file(con, path: Path):
    """Subagent transcript (<session>/subagents/agent-<id>.jsonl): all assistant
    usage is attributed to the agent type resolved via agent_map."""
    agent_id = path.stem.removeprefix("agent-")
    row = con.execute("SELECT agent_type FROM agent_map WHERE agent_id=?", (agent_id,)).fetchone()
    agent = row[0] if row else None
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if agent is None and r.get("agentId"):
                    sub = con.execute(
                        "SELECT agent_type FROM agent_map WHERE agent_id=?",
                        (r["agentId"],)).fetchone()
                    agent = sub[0] if sub else None
                msg = r.get("message")
                if isinstance(msg, dict) and msg.get("role") == "assistant":
                    _insert_usage(con, "claude", r, msg, agent or "unknown-subagent", path)
    except OSError:
        return


# --------------------------------------------------------------------- Codex

def ingest_codex_file(con, path: Path):
    """One Codex rollout = one session.

    token_count events carry cumulative + last-turn usage; we record the
    per-turn delta (last_token_usage). Agent attribution is best-effort:
    Codex skills/agents matching the Domus set are detected from payload text.
    """
    cwd = branch = model = session_id = None
    agents_seen = set()
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                p = d.get("payload") or {}
                t = d.get("type")
                if t == "session_meta":
                    cwd = p.get("cwd") or cwd
                    session_id = p.get("id") or session_id
                    git = p.get("git") or {}
                    branch = git.get("branch") or branch
                elif t == "turn_context":
                    cwd = p.get("cwd") or cwd
                    model = p.get("model") or model
                elif t == "event_msg" and p.get("type") == "token_count":
                    info = p.get("info") or {}
                    last = info.get("last_token_usage") or {}
                    if not last:
                        continue
                    cached = last.get("cached_input_tokens", 0) or 0
                    con.execute(
                        "INSERT INTO token_usage(platform, project, branch, agent, session_id, ts,"
                        " model, input_tokens, output_tokens, cache_read_tokens, cache_create_tokens,"
                        " source_file) VALUES ('codex',?,?,?,?,?,?,?,?,?,0,?)",
                        (cwd, branch, None, session_id, d.get("timestamp"), model,
                         (last.get("input_tokens", 0) or 0) - cached,
                         last.get("output_tokens", 0) or 0,
                         cached, str(path)),
                    )
                elif t == "response_item":
                    # Detect Domus skill/agent invocations in tool calls.
                    if p.get("type") in ("function_call", "custom_tool_call", "local_shell_call"):
                        blob = json.dumps(p)
                        for a in DOMUS_AGENTS:
                            if a in blob and a not in agents_seen:
                                agents_seen.add(a)
                                con.execute(
                                    "INSERT INTO invocations(platform, project, branch, agent,"
                                    " session_id, ts, source_file) VALUES ('codex',?,?,?,?,?,?)",
                                    (cwd, branch, a, session_id, d.get("timestamp"), str(path)),
                                )
    except OSError:
        return


# ------------------------------------------------------------------- collect

def collect(args):
    con = connect()
    scanned = ingested = 0

    claude_files = sorted(CLAUDE_PROJECTS.glob("*/*.jsonl")) if CLAUDE_PROJECTS.exists() else []
    claude_subagent_files = sorted(CLAUDE_PROJECTS.glob("*/*/subagents/agent-*.jsonl")) \
        if CLAUDE_PROJECTS.exists() else []
    codex_files = []
    for base in CODEX_SESSION_DIRS:
        if base.exists():
            codex_files.extend(sorted(base.rglob("rollout-*.jsonl")))

    # Main sessions first: they populate agent_map used by subagent attribution.
    for path, fn in [(p, ingest_claude_file) for p in claude_files] + \
                    [(p, ingest_claude_subagent_file) for p in claude_subagent_files] + \
                    [(p, ingest_codex_file) for p in codex_files]:
        scanned += 1
        if not file_changed(con, path):
            continue
        clear_file_rows(con, path)
        fn(con, path)
        mark_ingested(con, path)
        ingested += 1
        con.commit()

    con.commit()
    print(f"Scanned {scanned} files, ingested/updated {ingested}.")
    print(f"Database: {DB_PATH}")


# -------------------------------------------------------------------- report

def fmt(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def print_table(headers, rows):
    widths = [len(h) for h in headers]
    rows = [[str(c) for c in r] for r in rows]
    for r in rows:
        for i, c in enumerate(r):
            widths[i] = max(widths[i], len(c))
    line = "  ".join(h.ljust(w) for h, w in zip(headers, widths))
    print(line)
    print("-" * len(line))
    for r in rows:
        print("  ".join(c.ljust(w) for c, w in zip(r, widths)))


def short_project(p):
    if not p:
        return "(unknown)"
    return p.replace("\\", "/").rstrip("/").split("/")[-1]


def report(args):
    con = connect()
    where, params = "", []
    if args.agent:
        where = " AND agent = ?"
        params = [args.agent]

    print("\n=== Invocations per agent (all platforms) ===\n")
    rows = con.execute(
        "SELECT agent, platform, COUNT(*) FROM invocations WHERE 1=1" + where +
        " GROUP BY agent, platform ORDER BY COUNT(*) DESC", params).fetchall()
    print_table(["Agent", "Platform", "Invocations"], rows)

    print("\n=== Token usage per agent (subagent work only) ===\n")
    rows = con.execute(
        "SELECT agent, COUNT(*) AS msgs, SUM(input_tokens), SUM(output_tokens),"
        " SUM(cache_read_tokens), SUM(cache_create_tokens)"
        " FROM token_usage WHERE agent IS NOT NULL" + where +
        " GROUP BY agent ORDER BY SUM(output_tokens) DESC", params).fetchall()
    table = []
    for agent, msgs, inp, out, cr, cc in rows:
        total = (inp or 0) + (cr or 0) + (cc or 0)
        hit = f"{(cr or 0) / total * 100:.0f}%" if total else "-"
        table.append([agent, msgs, fmt(inp or 0), fmt(out or 0), fmt(cr or 0), fmt(cc or 0), hit])
    print_table(["Agent", "Msgs", "Input", "Output", "CacheRead", "CacheCreate", "CacheHit"], table)

    print("\n=== Agent x Project (invocations) ===\n")
    rows = con.execute(
        "SELECT agent, project, COUNT(*) FROM invocations WHERE 1=1" + where +
        " GROUP BY agent, project ORDER BY agent, COUNT(*) DESC", params).fetchall()
    print_table(["Agent", "Project", "Invocations"],
                [[a, short_project(p), c] for a, p, c in rows])

    print("\n=== Session totals per project/platform ===\n")
    rows = con.execute(
        "SELECT platform, project, SUM(input_tokens), SUM(output_tokens),"
        " SUM(cache_read_tokens) FROM token_usage"
        " GROUP BY platform, project ORDER BY platform, SUM(output_tokens) DESC").fetchall()
    print_table(["Platform", "Project", "Input", "Output", "CacheRead"],
                [[pl, short_project(pr), fmt(i or 0), fmt(o or 0), fmt(c or 0)]
                 for pl, pr, i, o, c in rows])
    print()


def main():
    ap = argparse.ArgumentParser(description="Domus agent usage tracker (zero-token, local)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("collect", help="incrementally ingest Claude/Codex transcripts")
    rp = sub.add_parser("report", help="print usage report")
    rp.add_argument("--agent", help="filter by agent name")
    args = ap.parse_args()
    if args.cmd == "collect":
        collect(args)
    else:
        report(args)


if __name__ == "__main__":
    main()
