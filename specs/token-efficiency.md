# Token Efficiency Protocol

Use this protocol inside every specialist agent.

## Context Intake

- Start with the smallest useful context: file names, summaries, changed files, failing logs, screenshots, or linked tasks.
- Read files progressively. Prefer targeted search before opening large files.
- Load only the sections needed for the current decision.
- Avoid pasting long file contents, logs, specs, or docs back to the user.
- Summarize repeated patterns instead of listing every occurrence.

## Reasoning And Output

- Separate facts, assumptions, and recommendations.
- Keep final answers scoped to the user's requested decision or action.
- Prefer checklists, diffs, command lists, or task payloads over long explanations.
- Include only evidence that changes the decision.
- Stop once the next action is clear.

## External Systems

- For Notion, GitHub, CI, docs, and browser work, fetch narrow records first.
- Do not sync or enumerate entire databases/projects unless the user asks or the task requires it.
- When uncertain, ask one concise question instead of exploring broad unrelated context.
