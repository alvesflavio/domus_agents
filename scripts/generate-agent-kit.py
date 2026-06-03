#!/usr/bin/env python3
"""Generate the Domus Agents kit from the canonical spec.

Reads specs/agents.yaml and writes both platform outputs so Claude Code and
Codex stay uniform:

  - claude-agents/<name>.md        Claude Code subagents
  - codex-skills/<name>/SKILL.md   Codex skills

The body (identity + sections + language note) is identical across platforms.
Only the frontmatter differs, because each platform requires a different shape:

  - Claude frontmatter: name, description, tools, model
  - Codex frontmatter:  name, description   (plus an H1 title in the body)

Run from the repo root:
    python scripts/generate-agent-kit.py
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required. Install it with: python -m pip install pyyaml")

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC_PATH = REPO_ROOT / "specs" / "agents.yaml"
CLAUDE_DIR = REPO_ROOT / "claude-agents"
CODEX_DIR = REPO_ROOT / "codex-skills"

GENERATED_HEADER = (
    "<!-- Generated from specs/agents.yaml by scripts/generate-agent-kit.py. "
    "Do not edit by hand. -->"
)


def load_spec() -> dict:
    with SPEC_PATH.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def render_body(agent: dict, defaults: dict, *, title: str | None) -> str:
    """Render the shared body: optional H1 title, identity, role, sections, note."""
    specialist_name = agent.get("specialist_name", defaults.get("specialist_name", "TODO"))
    parts: list[str] = []

    if title is not None:
        parts.append(f"# {title}")

    parts.append("## Agent Identity")
    parts.append(f"- specialist_name: {specialist_name}")

    parts.append(agent["role"].strip())

    for section in agent.get("sections", []):
        parts.append(f"## {section['heading']}")
        parts.append(section["body"].strip())

    note = defaults.get("language_note", "").strip()
    if note:
        parts.append(note)

    return "\n\n".join(parts) + "\n"


def render_claude(agent: dict, defaults: dict) -> str:
    tools = agent["tools"]["claude"]
    lines = ["---", f"name: {agent['name']}", f"description: {agent['description']}"]
    # An explicit tool list restricts the subagent; "inherit" grants all tools,
    # which Claude Code expresses by omitting the tools field entirely.
    if isinstance(tools, list):
        lines.append(f"tools: {', '.join(tools)}")
    lines.append(f"model: {agent.get('model', defaults.get('model', 'inherit'))}")
    lines.append("---")
    frontmatter = "\n".join(lines)
    body = render_body(agent, defaults, title=None)
    return f"{frontmatter}\n\n{GENERATED_HEADER}\n\n{body}"


def render_codex(agent: dict, defaults: dict) -> str:
    frontmatter = "\n".join(
        ["---", f"name: {agent['name']}", f"description: {agent['description']}", "---"]
    )
    body = render_body(agent, defaults, title=agent["display_name"])
    return f"{frontmatter}\n\n{GENERATED_HEADER}\n\n{body}"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"  wrote {path.relative_to(REPO_ROOT)}")


def main() -> int:
    spec = load_spec()
    defaults = spec.get("defaults", {})
    agents = spec.get("agents", [])
    if not agents:
        sys.exit("No agents found in specs/agents.yaml")

    print(f"Generating {len(agents)} agents from {SPEC_PATH.relative_to(REPO_ROOT)}")
    for agent in agents:
        name = agent["name"]
        write(CLAUDE_DIR / f"{name}.md", render_claude(agent, defaults))
        write(CODEX_DIR / name / "SKILL.md", render_codex(agent, defaults))

    print(f"Done. {len(agents)} Claude agents and {len(agents)} Codex skills generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
