---
name: session
description: Use when starting or ending a work session — auto-triggers when `.agents/` exists at conversation start, or when user says "start session", "let's continue", "wrap up", "end session"
metadata:
  author: haru
  version: 1.6.0
---

# Session Skill

Manage memory and session state across agents and conversations.

**Core principle**: MCP `@modelcontextprotocol/server-memory` is the canonical store. Local `.agents/` files are fallback only.

## Detect MCP (once, at session start)

Check if `search_nodes`, `create_entities`, `add_observations` are in the tool list. Record the result — do not re-check during the session.

## `/session start`

**Step 1 — Load state**:

- **MCP**: call `read_graph()`. Load: category entities (`UserPreferences`, `CodingStyle`, `ToolPreferences`), project entity (`[repo-basename]`), session entity (`[project-name]:session`). If any category entity is missing or empty, seed it from the Global Seed Values section below.
- **No MCP**: read `.agents/CONTEXT.md` and `.agents/CURRENT_TASK.md`. Skip silently if missing.

**Step 2 — Freshness check**: run `git log --oneline -5`. If recent commits touch feature files but context looks unchanged, flag: "Context may be stale — sync at session end."

**Step 3 — Report**: "Session resumed. Last task: [X]. Next: [Y]." Include any freshness warnings.

## `/session end`

**Step 1 — Save session state**:

- **MCP**: delete `[project-name]:session`, recreate with: `objective`, `status` (IN_PROGRESS | BLOCKED | REVIEW | DONE), `completed`, `remaining`, `next`, `last-updated`.
- **No MCP**: overwrite `.agents/CURRENT_TASK.md` with the same fields.

**Step 2 — Save new facts** (cross-project):

- **MCP**: `search_nodes` to deduplicate, then `add_observations` on the appropriate category entity (`UserPreferences`, `CodingStyle`, `ToolPreferences`).
- **No MCP**: append to `.agents/MEMORY.md` (`## YYYY-MM-DD — [topic]` / `**Fact:** ...` / `**Why:** ...`). Update in place if a similar entry exists.

**Step 3 — Save project context** (conventions, patterns, decisions):

- **MCP**: `search_nodes` to deduplicate, then `add_observations` on the project entity.
- **No MCP**: update `.agents/CONTEXT.md`. Keep it concise — remove stale entries.

**Step 4 — Confirm**: "Session saved. Next: [one-sentence handoff]."

## MCP Entity Reference

### Entity Lifecycle

| Entity                   | Lifecycle  | Mechanism                                                                             |
| ------------------------ | ---------- | ------------------------------------------------------------------------------------- |
| `[project-name]:session` | Volatile   | `delete_entities` + `create_entities` every session end — full reset, no accumulation |
| `[repo-basename]`        | Persistent | `create_entities` once if missing; `add_observations` only — never delete             |
| `UserPreferences`        | Persistent | same as above                                                                         |
| `CodingStyle`            | Persistent | same as above                                                                         |
| `ToolPreferences`        | Persistent | same as above                                                                         |

### Write Protocol

1. `search_nodes("[topic]")` — check if observation already exists
2. If entity missing: `create_entities` first
3. `add_observations` with the new fact — never overwrite, always append

### What Goes Where

**`UserPreferences`** — cross-project behavioral preferences:

- Communication style (terse responses, no emojis, ask before committing)
- Workflow habits (worktrees by default, parallel agents opt-in)
- Decision preferences (simple over clever, no speculative abstractions)

**`CodingStyle`** — cross-project code conventions:

- Commit format (conventional commits: `feat:`, `fix:`, `chore:`)
- Formatting rules (2-space indent for config, no prose wrapping)
- Language idioms that apply broadly

**`ToolPreferences`** — cross-project tool choices:

- Runtime/env manager (nix-first, mise for language runtimes)
- Task runner (make)
- Shell, editor, CLI preferences

**`[repo-basename]`** — project-specific, stable:

- Architecture decisions and why they were made
- Non-obvious conventions not in AGENTS.md
- Key commands, tech stack, dependency notes

**`[project-name]:session`** — volatile task state, reset every session:

- `objective` — what we're working toward
- `status` — `IN_PROGRESS` | `BLOCKED` | `REVIEW` | `DONE`
- `completed` — list of finished items this session
- `remaining` — what's left
- `next` — the single most important next action
- `last-updated` — ISO date

## Global Seed Values

If `read_graph()` returns a category entity with no observations, seed it immediately using `add_observations`. These are the established cross-project defaults — do not ask the user to confirm them.

**`UserPreferences`**

- Project-local worktrees by default for isolated work; parallel sessions are opt-in only
- Sub-agents by default — dispatch independent work; don't do everything inline
- Simple solutions over clever ones — avoid over-engineering and speculative abstractions
- Use haiku or other efficient models for dispatch/sub-agent tasks
- Terse responses — no trailing summaries, no preamble

**`CodingStyle`**

- Conventional commits: `feat:`, `fix:`, `chore:`, `deploy:` — no emojis in commit messages
- 2-space indentation for config files (YAML, TOML, JSON)
- No emojis anywhere unless explicitly requested
- No manually wrapped prose — let formatters handle line length
- Staging discipline: `git add <specific files>` only, never `git add -A` or `git add .`

**`ToolPreferences`**

- Nix-first: all tools come from devShell (`nix develop`)
- `mise` for language runtimes only (not general tooling)
- `make` is the task runner — always reference `make <target>`
- `make check` runs before commits; `make validate` before PRs (enforced by hooks)
- `rtk` CLI proxy active — git and other commands are transparently rewritten for token savings

## Fallback: Local Files

Used only when MCP is unavailable. All three belong in `.gitignore`.

- `.agents/CURRENT_TASK.md` — task state (overwrite each session end)
- `.agents/CONTEXT.md` — project conventions (update in place; remove stale entries)
- `.agents/MEMORY.md` — cross-project facts (append; update in place for duplicates)

## Context-Mode Integration

If `ctx_search` / `ctx_batch_execute` are available: use `ctx_batch_execute` to load memory + run `git log` in one call; use `ctx_search` for targeted retrieval from large files instead of reading them in full.
