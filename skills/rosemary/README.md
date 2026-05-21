# rosemary skill

Session and memory management using the [`rosemary`](https://github.com/azusachino/rosemary) CLI — a persistent, project-local knowledge graph backed by SQLite/FTS5.

This skill is a CLI-native alternative to the `session` skill. It replaces MCP `server-memory` tool calls with `rosemary` shell commands, using the same entity model (`UserPreferences`, `CodingStyle`, `ToolPreferences`, `[project]:session`).

## Prerequisites

Install `rosemary` from source (requires Rust 1.85+):

```bash
cargo install --git https://github.com/azusachino/rosemary
```

Initialize a project-local graph in your project root (run once):

```bash
rosemary init --local
```

This creates `.rosemary/` and `rosemary.toml` in your project. Add `.rosemary/` to `.gitignore` if you don't want to commit the graph.

## Invocation

```
/harus-skills:rosemary start    # load session state and project context
/harus-skills:rosemary end      # persist state, compact graph
```

Auto-triggers when `.agents/` exists at conversation start, or when you say "start session", "let's continue", "wrap up", or "end session".

## Fallback

When `rosemary` is not in `$PATH`, the skill falls back to local `.agents/` files (`CURRENT_TASK.md`, `CONTEXT.md`, `MEMORY.md`).

## Storage

Data lives in `.rosemary/data/rosemary.db` (project-local) or under `$XDG_DATA_HOME` (user-level). Run `rosemary compact` to archive session state to Markdown snapshots and refresh the FTS index.
