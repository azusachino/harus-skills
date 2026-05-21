---
name: rosemary
description: Use when starting or ending a work session — auto-triggers when `.agents/` exists at conversation start, or when user says "start session", "let's continue", "wrap up", "end session". Uses the rosemary CLI for persistent knowledge graph storage instead of MCP server-memory.
metadata:
  author: haru
  version: 1.1.0
---

# Rosemary Session Skill

Manage memory and session state across agents and conversations using the `rosemary` CLI.

**Core principle**: `rosemary` is the canonical store. Local `.agents/` files are fallback only when `rosemary` is not in `$PATH`.

**State scope** — prefer **shared (XDG global) state** by default. Project-local state (`rosemary init --local` creating `./rosemary.toml`) is opt-in only when the user explicitly requests it (e.g., "use project-local rosemary", "isolate this repo's memory"). Cross-project entities (`UserPreferences`, `CodingStyle`, `ToolPreferences`) always live in the global graph regardless of scope.

## Detect rosemary (once, at session start)

Run `command -v rosemary` (or `rosemary help`). Record the result — do not re-check during the session. If unavailable, fall back to local files.

**Scope detection**: if `./rosemary.toml` exists in the repo root, rosemary auto-uses project-local state — note this but do not switch modes mid-session. Otherwise the global XDG graph is in effect.

## `/rosemary start`

**Step 1 — Load state**:

- **rosemary**: load known entities with `rosemary open-nodes UserPreferences CodingStyle ToolPreferences [repo-basename] [project-name]:session`. If any entity is missing from the output, it doesn't exist yet — seed it from the Global Seed Values section below. If the session entity is missing, treat as a fresh start.
- **No rosemary**: read `.agents/CONTEXT.md` and `.agents/CURRENT_TASK.md`. Skip silently if missing.

**Step 2 — Freshness check**: run `git log --oneline -5`. If recent commits touch feature files but context looks unchanged, flag: "Context may be stale — sync at session end."

**Step 3 — Report**: "Session resumed. Last task: [X]. Next: [Y]." Include any freshness warnings.

## `/rosemary end`

**Step 1 — Save session state**:

- **rosemary**: full reset — delete the old session entity and recreate it clean:

  ```bash
  rosemary delete-entities "[project-name]:session"
  rosemary create-entities "[project-name]:session" "session"
  rosemary add-observations "[project-name]:session" "objective: [what we worked toward]"
  rosemary add-observations "[project-name]:session" "status: [IN_PROGRESS|BLOCKED|REVIEW|DONE]"
  rosemary add-observations "[project-name]:session" "completed: [list of finished items]"
  rosemary add-observations "[project-name]:session" "remaining: [what's left]"
  rosemary add-observations "[project-name]:session" "next: [single most important next action]"
  rosemary add-observations "[project-name]:session" "last-updated: YYYY-MM-DD"
  ```

- **No rosemary**: overwrite `.agents/CURRENT_TASK.md` with the same fields.

**Step 2 — Save new facts** (cross-project):

- **rosemary**: `rosemary search-nodes "[topic]"` to check for duplicates, then `rosemary add-observations [entity] "[fact]"` on the appropriate category entity (`UserPreferences`, `CodingStyle`, `ToolPreferences`).
- **No rosemary**: append to `.agents/MEMORY.md` (`## YYYY-MM-DD — [topic]` / `**Fact:** ...` / `**Why:** ...`). Update in place if a similar entry exists.

**Step 3 — Save project context** (conventions, patterns, decisions):

- **rosemary**: `rosemary search-nodes "[topic]"` to check for duplicates, then `rosemary add-observations [repo-basename] "[fact]"`.
- **No rosemary**: update `.agents/CONTEXT.md`. Keep it concise — remove stale entries.

**Step 4 — Compact** (optional): if `rosemary` was built with the `documents` feature (`cargo install --features documents`), run `rosemary compact` to archive session state to Markdown and refresh the FTS/vector index. Skip silently if the command is unavailable.

**Step 5 — Confirm**: "Session saved. Next: [one-sentence handoff]."

## Entity Reference

### Entity Lifecycle

| Entity                   | Lifecycle  | Mechanism                                                                               |
| ------------------------ | ---------- | --------------------------------------------------------------------------------------- |
| `[project-name]:session` | Volatile   | `delete-entities` + `create-entities` every session end — full reset, no accumulation  |
| `[repo-basename]`        | Persistent | `create-entities` once if missing; `add-observations` only — never delete               |
| `UserPreferences`        | Persistent | same as above                                                                           |
| `CodingStyle`            | Persistent | same as above                                                                           |
| `ToolPreferences`        | Persistent | same as above                                                                           |

### Write Protocol

1. `rosemary search-nodes "[topic]"` — check if observation already exists
2. If entity missing: `rosemary create-entities [name] [type]` first
3. `rosemary add-observations [name] "[fact]"` — never overwrite, always append
4. To correct a single stale observation: `rosemary delete-observations [name] "[exact old content]"` then re-add

### Entity Types

| Type         | Use for                                          |
| ------------ | ------------------------------------------------ |
| `project`    | Per-project stable facts, architecture decisions |
| `session`    | Volatile task state — reset each session end     |
| `preference` | Cross-project user or tool preferences           |
| `standard`   | Global conventions that apply everywhere         |
| `concept`    | Technical concepts, definitions                  |
| `task`       | In-progress task lists, status tracking          |
| `reference`  | Pointers to external resources, URLs             |

### What Goes Where

**`UserPreferences`** (type: `preference`) — cross-project behavioral preferences:

- Communication style (terse responses, no emojis, ask before committing)
- Workflow habits (worktrees by default, parallel agents opt-in)
- Decision preferences (simple over clever, no speculative abstractions)

**`CodingStyle`** (type: `standard`) — cross-project code conventions:

- Commit format (conventional commits: `feat:`, `fix:`, `chore:`)
- Formatting rules (2-space indent for config, no prose wrapping)
- Language idioms that apply broadly

**`ToolPreferences`** (type: `preference`) — cross-project tool choices:

- Runtime/env manager (nix-first, mise for language runtimes)
- Task runner (make)
- Shell, editor, CLI preferences

**`[repo-basename]`** (type: `project`) — project-specific, stable:

- Architecture decisions and why they were made
- Non-obvious conventions not in AGENTS.md
- Key commands, tech stack, dependency notes

**`[project-name]:session`** (type: `session`) — volatile task state, reset every session:

- `objective` — what we're working toward
- `status` — `IN_PROGRESS` | `BLOCKED` | `REVIEW` | `DONE`
- `completed` — list of finished items this session
- `remaining` — what's left
- `next` — the single most important next action
- `last-updated` — ISO date

## Global Seed Values

If an entity is missing from `open-nodes` output, create and seed it immediately. These are established cross-project defaults — do not ask the user to confirm them.

**`UserPreferences`** (type: `preference`)

- Project-local worktrees by default for isolated work; parallel sessions are opt-in only
- Sub-agents by default — dispatch independent work; don't do everything inline
- Simple solutions over clever ones — avoid over-engineering and speculative abstractions
- Use haiku or other efficient models for dispatch/sub-agent tasks
- Terse responses — no trailing summaries, no preamble

**`CodingStyle`** (type: `standard`)

- Conventional commits: `feat:`, `fix:`, `chore:`, `deploy:` — no emojis in commit messages
- 2-space indentation for config files (YAML, TOML, JSON)
- No emojis anywhere unless explicitly requested
- No manually wrapped prose — let formatters handle line length
- Staging discipline: `git add <specific files>` only, never `git add -A` or `git add .`

**`ToolPreferences`** (type: `preference`)

- Nix-first: all tools come from devShell (`nix develop`)
- `mise` for language runtimes only (not general tooling)
- `make` is the task runner — always reference `make <target>`
- `make check` runs before commits; `make validate` before PRs (enforced by hooks)
- `rtk` CLI proxy active — git and other commands are transparently rewritten for token savings

## Command Quick Reference

```bash
# Read
rosemary read-graph
rosemary search-nodes "query"
rosemary open-nodes "name1" "name2" ...

# Write
rosemary create-entities "name" "type"
rosemary add-observations "name" "content"

# Delete
rosemary delete-entities "name1" "name2" ...
rosemary delete-observations "name" "exact content"
rosemary delete-relations "from" "to" "relation_type"

# Maintenance
rosemary compact          # archive + refresh FTS/vector (requires --features documents)
rosemary init --local     # opt-in: project-local graph (only on explicit user request)
```

## Fallback: Local Files

Used only when `rosemary` is not available. All three belong in `.gitignore`.

- `.agents/CURRENT_TASK.md` — task state (overwrite each session end)
- `.agents/CONTEXT.md` — project conventions (update in place; remove stale entries)
- `.agents/MEMORY.md` — cross-project facts (append; update in place for duplicates)
