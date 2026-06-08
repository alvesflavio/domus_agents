#!/usr/bin/env python3
"""Generate the Domus Agents kit from the canonical spec.

Reads specs/agents.yaml and writes platform outputs for each agent according
to its `platforms` list (defaults to all three if omitted):

  - claude-agents/<name>.md             Claude Code subagents
  - codex-skills/<name>/SKILL.md        Codex skills
  - .codex/agents/<name>.toml           Codex agents
  - antigravity-agents/<name>.md        Antigravity agents

The body (identity + sections + language note) is identical across platforms.
Only the frontmatter differs, because each platform requires a different shape:

  - Claude frontmatter:       name, description, tools, model
  - Codex frontmatter:        name, description   (plus an H1 title in the body)
  - Antigravity frontmatter:  name, description, model, platform: antigravity

Run from the repo root:
    python scripts/generate-agent-kit.py
"""

from __future__ import annotations

import argparse
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
CODEX_AGENTS_DIR = REPO_ROOT / ".codex" / "agents"
ANTIGRAVITY_DIR = REPO_ROOT / "antigravity-agents"

GENERATED_HEADER = (
    "<!-- Generated from specs/agents.yaml by scripts/generate-agent-kit.py. "
    "Do not edit by hand. -->"
)


def load_spec() -> dict:
    with SPEC_PATH.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def render_body(agent: dict, defaults: dict, *, title: str | None) -> str:
    """Render the shared body: optional H1 title, identity, role, sections, notes."""
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

    memory_note = defaults.get("shared_memory_note", "").strip()
    if memory_note:
        parts.append("## Shared Project Memory")
        parts.append(memory_note)

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


def toml_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def toml_multiline_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
    return f'"""\n{escaped}"""'


def render_antigravity(agent: dict, defaults: dict) -> str:
    model = agent.get("model", defaults.get("model", "inherit"))
    lines = [
        "---",
        f"name: {agent['name']}",
        f"description: {agent['description']}",
        f"model: {model}",
        "platform: antigravity",
        "---",
    ]
    frontmatter = "\n".join(lines)
    body = render_body(agent, defaults, title=None)
    return f"{frontmatter}\n\n{GENERATED_HEADER}\n\n{body}"


def render_codex_agent(agent: dict, defaults: dict) -> str:
    body = f"{GENERATED_HEADER}\n\n{render_body(agent, defaults, title=None)}"
    return "\n".join(
        [
            f"name = {toml_string(agent['name'])}",
            f"description = {toml_string(agent['description'])}",
            f"developer_instructions = {toml_multiline_string(body)}",
            "",
        ]
    )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"  wrote {path.relative_to(REPO_ROOT)}")


ALL_PLATFORMS = {"claude", "codex", "antigravity"}


def agent_platforms(agent: dict, defaults: dict) -> set[str]:
    raw = agent.get("platforms", defaults.get("platforms", sorted(ALL_PLATFORMS)))
    return set(raw)


def expected_outputs(agent: dict, defaults: dict) -> dict[Path, str]:
    name = agent["name"]
    platforms = agent_platforms(agent, defaults)
    outputs: dict[Path, str] = {}
    if "claude" in platforms:
        outputs[CLAUDE_DIR / f"{name}.md"] = render_claude(agent, defaults)
    if "codex" in platforms:
        outputs[CODEX_DIR / name / "SKILL.md"] = render_codex(agent, defaults)
        outputs[CODEX_AGENTS_DIR / f"{name}.toml"] = render_codex_agent(agent, defaults)
    if "antigravity" in platforms:
        outputs[ANTIGRAVITY_DIR / f"{name}.md"] = render_antigravity(agent, defaults)
    return outputs


def check_outputs(outputs: dict[Path, str]) -> int:
    stale: list[Path] = []
    for path, expected in outputs.items():
        if not path.exists() or path.read_text(encoding="utf-8") != expected:
            stale.append(path)

    if stale:
        print("Generated agent files are out of sync. Run: python scripts/generate-agent-kit.py")
        for path in stale:
            print(f"  stale: {path.relative_to(REPO_ROOT)}")
        return 1

    print(f"OK: {len(outputs)} generated files are in sync with {SPEC_PATH.relative_to(REPO_ROOT)}.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the Domus Agents kit.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify generated files are current without writing them.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    spec = load_spec()
    defaults = spec.get("defaults", {})
    agents = spec.get("agents", [])
    if not agents:
        sys.exit("No agents found in specs/agents.yaml")

    outputs: dict[Path, str] = {}
    for agent in agents:
        outputs.update(expected_outputs(agent, defaults))

    if args.check:
        return check_outputs(outputs)

    platform_counts: dict[str, int] = {p: 0 for p in ALL_PLATFORMS}
    for agent in agents:
        for p in agent_platforms(agent, defaults):
            if p in platform_counts:
                platform_counts[p] += 1

    print(f"Generating {len(agents)} agents from {SPEC_PATH.relative_to(REPO_ROOT)}")
    for path, content in outputs.items():
        write(path, content)

    print(
        f"Done. {platform_counts['claude']} Claude, {platform_counts['codex']} Codex, "
        f"and {platform_counts['antigravity']} Antigravity agents generated."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
