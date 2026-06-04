# rosemary skill

Share durable state across conversations and sub-agents using the [`rosemary`](https://github.com/azusachino/rosemary) CLI — a persistent knowledge graph backed by SQLite/FTS5. One graph, three pillars:

- **Session continuity** (`/rosemary start`, `/rosemary end`) — resume work after `/clear`, context compaction, or a restart.
- **Task dispatcher** (`/rosemary tasks plan|list|dispatch|sync|close`) — durable, cross-agent task state stored as epic + task entities. Replaces ephemeral TodoWrite / local jsonl: a dispatched sub-agent and the lead coordinate through the graph.
- **Knowledge tier** (`/rosemary recall`) — hybrid semantic search over ingested docs (`ingest`/`query`) plus an ADR-style decision log.

It is a CLI-native alternative to the `session` skill: `rosemary` shell commands instead of MCP `server-memory`, using the same entity model (`UserPreferences`, `CodingStyle`, `ToolPreferences`, `[project]:session`) extended with `:` -hierarchical epic/task/decision names.

## Prerequisites

Install `rosemary` from source (requires Rust 1.85+):

```bash
# Standard build
cargo install --git https://github.com/azusachino/rosemary

# With document ingestion + vector search + compact support
cargo install --git https://github.com/azusachino/rosemary --features documents
```

Initialize a project-local graph in your project root (run once):

```bash
rosemary init --local
```

This creates `.rosemary/` and `rosemary.toml` in your project. Add `.rosemary/` to `.gitignore` if you don't want to commit the graph.

## Invocation

```
/harus-skills:rosemary start                 # load session state and project context
/harus-skills:rosemary end                    # persist state, compact graph
/harus-skills:rosemary tasks plan <epic>      # break work into epic + task entities
/harus-skills:rosemary tasks list [epic]      # render the status board
/harus-skills:rosemary tasks dispatch [task]  # spawn a sub-agent on the next ready task
/harus-skills:rosemary tasks sync [task]      # record review outcome, advance status
/harus-skills:rosemary tasks close <epic>     # promote lessons, rest the epic
/harus-skills:rosemary recall                 # ingest/query docs, decision log
```

Auto-triggers when `.agents/` exists at conversation start, or when you say "start session", "let's continue", "dispatch the next task", "wrap up", or "end session".

## Fallback

When `rosemary` is not in `$PATH`, session continuity falls back to local `.agents/` files (`CURRENT_TASK.md`, `CONTEXT.md`, `MEMORY.md`). The task dispatcher and knowledge tier require rosemary — they have no file fallback.

## Storage

Data lives in `.rosemary/data/rosemary.db` (project-local) or under `$XDG_DATA_HOME` (user-level). `rosemary compact` (available with `--features documents`) archives session state to Markdown snapshots and refreshes the FTS/vector index.
