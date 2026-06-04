---
name: rosemary
description: Use to share state across sessions and agents using the rosemary CLI knowledge graph — session continuity (start/end), a durable task dispatcher (`/rosemary tasks`) that replaces ephemeral TodoWrite/local jsonl, and a knowledge tier (`/rosemary recall`). Auto-triggers when `.agents/` exists at conversation start, or when the user says "start session", "let's continue", "dispatch the next task", "wrap up", "end session".
metadata:
  author: haru
  version: 1.2.0
---

# Rosemary Skill

Share durable state across conversations and sub-agents using the `rosemary` CLI knowledge graph. Rosemary is one primitive — a graph any agent can read and write — exposed through three pillars:

| Pillar | Command | What it backs |
| --- | --- | --- |
| **Session continuity** | `/rosemary start`, `/rosemary end` | resume work after `/clear`, context compaction, or a machine restart |
| **Task dispatcher** | `/rosemary tasks plan\|list\|dispatch\|sync\|close` | durable, cross-agent task state — replaces TodoWrite / local jsonl |
| **Knowledge tier** | `/rosemary recall` | hybrid semantic search over ingested docs + a decision log |

**Core principle**: `rosemary` is the canonical store. Local `.agents/` files are fallback only when `rosemary` is not in `$PATH`. Task state lives in the graph, never in an ephemeral in-conversation todo list — that is the whole point: a dispatched sub-agent and the lead coordinate *through the graph*, not through the user.

**State scope** — prefer **shared (XDG global) state** by default. Project-local state (`rosemary init --local`, creating `./rosemary.toml`) is opt-in only when the user explicitly requests it (e.g. "use project-local rosemary", "isolate this repo's memory"). Cross-project entities (`UserPreferences`, `CodingStyle`, `ToolPreferences`) always live in the global graph regardless of scope.

## Naming Convention

Entity names use `:` as a hierarchy separator. Keep names verbatim — do not flatten to dashes.

| Pattern | Type | Example |
| --- | --- | --- |
| `<project>:session` | `session` | `ame:session` |
| `<project>:<epic>` | `task` | `ame:mobile-support` |
| `<project>:<epic>:task-<n>` | `task` | `ame:mobile-support:task-3` |
| `<project>:decision:<slug>` | `concept` | `ame:decision:no-pwa` |
| `<repo-basename>` | `project` | `ame` |

`<project>` is the repo basename. Use `-` only inside a single segment (`mobile-support`), `:` only between hierarchy levels.

## Detect rosemary (once, at session start)

Run `command -v rosemary`. Record the result — do not re-check during the session. If unavailable, fall back to local files.

**Scope detection**: if `./rosemary.toml` exists in the repo root, rosemary auto-uses project-local state — note this but do not switch modes mid-session. Otherwise the global XDG graph is in effect.

## `/rosemary start`

**Step 1 — Load state**:

- **rosemary**: `rosemary open-nodes UserPreferences CodingStyle ToolPreferences [repo-basename] [project]:session`. If any entity is missing from the output, it doesn't exist yet — seed it from Global Seed Values. If the session entity is missing, treat as a fresh start. If `[project]:session` references an active epic, also load it: `rosemary search-nodes "[epic-name]"` to pull the epic and its task children.
- **No rosemary**: read `.agents/CONTEXT.md` and `.agents/CURRENT_TASK.md`. Skip silently if missing.

**Step 2 — Freshness check**: run `git log --oneline -5`. If recent commits touch feature files but the loaded context looks unchanged, flag: "Context may be stale — sync at session end."

**Step 3 — Report**: "Session resumed. Last task: [X]. Next: [Y]." If an epic is active, append a one-line task board (see `/rosemary tasks list`). Include any freshness warnings.

## `/rosemary end`

**Step 1 — Save session state** (rosemary): full reset — delete the old session entity and recreate it clean so it never accumulates stale lines:

```bash
rosemary delete-entities "[project]:session"
rosemary create-entities "[project]:session" "session"
rosemary add-observations "[project]:session" "objective: [what we worked toward; name the active epic if any]"
rosemary add-observations "[project]:session" "status: [IN_PROGRESS|BLOCKED|REVIEW|DONE]"
rosemary add-observations "[project]:session" "completed: [finished items this session]"
rosemary add-observations "[project]:session" "remaining: [what's left]"
rosemary add-observations "[project]:session" "next: [single most important next action]"
rosemary add-observations "[project]:session" "last-updated: YYYY-MM-DD"
```

- **No rosemary**: overwrite `.agents/CURRENT_TASK.md` with the same fields.

**Step 2 — Save new facts** (cross-project): `rosemary search-nodes "[topic]"` to check for duplicates, then `rosemary add-observations [UserPreferences|CodingStyle|ToolPreferences] "[fact]"`. No rosemary: append to `.agents/MEMORY.md`.

**Step 3 — Save project context** (conventions, patterns, decisions): `rosemary search-nodes "[topic]"`, then `rosemary add-observations [repo-basename] "[fact]"`. No rosemary: update `.agents/CONTEXT.md`, keep concise.

**Step 4 — Compact** (optional): if `rosemary` was built with the `documents` feature, run `rosemary compact` to archive session state to Markdown and refresh the FTS/vector index. Skip silently if unavailable.

**Step 5 — Confirm**: "Session saved. Next: [one-sentence handoff]."

## `/rosemary tasks` — Task Dispatcher

A durable replacement for in-conversation todo lists. An **epic** entity holds the objective and scope; **task** entities hold one dispatchable unit each, linked `part_of` the epic. Status lives as append-only observations — the trail *is* the audit log. The session entity points at the active epic and the next task.

### `tasks plan <epic-name>`

Break work into an epic + tasks. Create once, then never overwrite:

```bash
rosemary create-entities "[project]:[epic]" "task"
rosemary add-observations "[project]:[epic]" "objective: [what this epic delivers]"
rosemary add-observations "[project]:[epic]" "scope: [in / out of scope, decided constraints]"

rosemary create-entities "[project]:[epic]:task-1" "task"
rosemary add-observations "[project]:[epic]:task-1" "title: [one-line goal] — [file paths + line numbers + plan]"
rosemary add-observations "[project]:[epic]:task-1" "status: READY_TO_DISPATCH"
rosemary create-relations "[project]:[epic]:task-1" "[project]:[epic]" "part_of"
# ...repeat per task; dependent tasks start "status: BLOCKED_ON [project]:[epic]:task-N"
```

Then point the session at it: `rosemary add-observations "[project]:session" "objective: [epic] — see [project]:[epic]"`. Order tasks **smallest → biggest** to build momentum. Put concrete file paths and line numbers in each `title:` so the dispatched agent needs zero discovery.

### `tasks list [epic-name]`

`rosemary search-nodes "[epic]"` (or `open-nodes` each task), then render a board from the latest `status:` observation of each task:

```
[project]:[epic]
  task-1  Responsive app shell          DONE
  task-2  Taking flow + flashcards      REVIEW
  task-3  Mobile e2e smoke              READY_TO_DISPATCH
  task-4  Explore page minWidth         BLOCKED_ON task-1
```

### `tasks dispatch [task]`

Pick the next `READY_TO_DISPATCH` task (or the named one). Mark it dispatched, spawn a sub-agent, and have the agent write results **back into the task entity** — not just into the conversation:

```bash
rosemary add-observations "[project]:[epic]:task-N" "status: DISPATCHED to [agent] YYYY-MM-DD"
```

Brief the sub-agent from the task's `title:` observation. Default agent is `haiku-developer` (efficient model for scoped work) unless the task is correctness-critical. Require the agent to end by recording:

```bash
rosemary add-observations "[project]:[epic]:task-N" "impl: [what changed; files touched; make check result]"
rosemary add-observations "[project]:[epic]:task-N" "status: REVIEW"
```

**Dispatch models** — pick per epic:

- **Sequential (default, proven)** — no worktrees, one agent at a time, lead reviews the diff in the working tree, commit after each task. Use when tasks touch overlapping files, need a human verify-gate, or want tight per-task review. This is the cadence that works in practice.
- **Worktree-per-task (opt-in)** — each task gets its own git worktree under the project; dispatch independent tasks in parallel; merge per task. Matches the global worktrees-by-default preference. Use only when tasks are genuinely independent (disjoint files).

### `tasks sync [task]`

The lead reviews the dispatched diff, records the outcome, and advances status. Never blind-trust a sub-agent's diff — note anything you trimmed:

```bash
rosemary add-observations "[project]:[epic]:task-N" "TL-review YYYY-MM-DD: [diff verdict; what was adjusted]"
rosemary add-observations "[project]:[epic]:task-N" "status: AWAITING_VERIFY"   # human/device check needed
# or
rosemary add-observations "[project]:[epic]:task-N" "status: DONE — committed on [branch] YYYY-MM-DD"
```

Then re-point the session `next:` at the following task, and unblock dependents (`tasks list` will now show them `READY_TO_DISPATCH`).

### `tasks close <epic-name>`

When every task is `DONE`: lift the durable lessons out of the volatile task entities into the persistent project entity, then let the epic rest (no delete — the history stays queryable):

```bash
rosemary add-observations "[repo-basename]" "[convention or decision learned during the epic]"
rosemary add-observations "[project]:[epic]" "status: DONE — [outcome, PR link] YYYY-MM-DD"
```

### Status lifecycle

`READY_TO_DISPATCH → DISPATCHED → REVIEW → AWAITING_VERIFY → DONE`. Dependents sit at `BLOCKED_ON task-N` until their dependency is `DONE`. Each transition is a new appended `status:` observation — the latest wins, the rest are the audit trail.

## `/rosemary recall` — Knowledge Tier

Semantic recall over your own docs and a decision log. Requires the `documents` feature for `ingest`/`query`; degrade to `search-nodes` otherwise.

### Ingest + query

```bash
rosemary ingest docs/specs/          # load ONE file or directory into the document tier (one path per call)
rosemary ingest ~/.claude/CLAUDE.md  # index an instruction file for semantic recall
rosemary query "how does session auth verify tokens"   # hybrid semantic + keyword recall
```

`ingest` takes exactly one `<PATH>` (file or directory) — call it once per path, not as a list. Prefer `query` before re-reading a large doc — it returns the relevant chunks, not the whole file. Re-`ingest` after meaningful doc changes.

**Guardrail — index, never duplicate.** `CLAUDE.md` / `AGENTS.md` are the canonical, harness-loaded source of truth. `ingest` makes them *queryable*; it does not make the graph their owner. Never copy a file's content into entities — that creates a second source that drifts. The seed entities (`UserPreferences` / `CodingStyle` / `ToolPreferences`) are the curated cross-project *slice* of global `CLAUDE.md`, kept as entities because they are agent-writable and queryable; everything else in those files stays in the files and is reached via `query`.

**Ranking caveat (verified).** `query` hybrid-ranks graph topics *above* ingested document chunks — an ingested `CLAUDE.md` surfaces, but below the `codingstyle`/`toolpreferences` topic entities. So the curated entities remain the primary recall path; ingested instruction files are a full-text safety net for content that isn't captured as an entity, not a replacement for the seed trio.

### Decision log (ADRs)

Record non-obvious choices as decision entities so the *why* survives:

```bash
rosemary create-entities "[project]:decision:[slug]" "concept"
rosemary add-observations "[project]:decision:[slug]" "decision: [what was chosen]"
rosemary add-observations "[project]:decision:[slug]" "context: [the forces / constraints]"
rosemary add-observations "[project]:decision:[slug]" "consequences: [trade-offs accepted]"
rosemary add-observations "[project]:decision:[slug]" "date: YYYY-MM-DD"
# link related decisions and the work they constrain
rosemary create-relations "[project]:decision:[new]" "[project]:decision:[old]" "supersedes"
rosemary create-relations "[project]:[epic]:task-N" "[project]:decision:[slug]" "depends_on"
```

Surface them with `rosemary search-nodes "[topic]"` or `rosemary query "why [topic]"`.

## Real-World Practices

Checklist distilled from running this dispatcher on a production project:

- One agent at a time unless tasks touch disjoint files; parallel only pays when worktrees don't fight.
- Lead reviews every sub-agent diff before commit and trims stray changes — never blind-trust.
- Commit after each task passes review — a bisectable branch beats one squash.
- Pin file paths + line numbers in each task `title:` so dispatch is execution, not rediscovery.
- Order tasks smallest → biggest; early wins de-risk the larger ones.
- `AWAITING_VERIFY` for anything needing human/device confirmation — don't auto-close.
- `status:` is append-only — the trail is the audit log.
- Keep the session `next:` to a single action.
- On `tasks close`, promote durable lessons into `[repo-basename]` or a decision entity before they're lost.

## Entity Reference

| Entity | Type | Lifecycle | Holds |
| --- | --- | --- | --- |
| `[project]:session` | `session` | Volatile — `delete`+`create` each `end` | `objective`, `status`, `completed`, `remaining`, `next`, `last-updated` |
| `[project]:[epic]` / `:task-N` | `task` | Epic-scoped — `create` once, append-only `status:` trail, rests `DONE` on close | epic objective/scope; per-task `title`, `status`, `impl` |
| `[project]:decision:<slug>` | `concept` | Persistent — `create` once, link with relations | `decision`, `context`, `consequences`, `date` |
| `[repo-basename]` | `project` | Persistent — append-only, never delete | architecture decisions + why, non-obvious conventions, key commands, stack |
| `UserPreferences` / `CodingStyle` / `ToolPreferences` | `preference` / `standard` | Persistent, global — append-only | cross-project prefs (see Global Seed Values) |

Remaining types: `reference` (external URLs/resources). Write protocol for every entity:

1. `rosemary search-nodes "[topic]"` — check the observation doesn't already exist.
2. If the entity is missing: `rosemary create-entities [name] [type]` first.
3. `rosemary add-observations [name] "[fact]"` — never overwrite, always append.
4. To fix a stale line: `rosemary delete-observations [name] "[exact old content]"`, then re-add.

## Global Seed Values

If an entity is missing from `open-nodes`, create and seed it immediately. These are established cross-project defaults — do not ask the user to confirm them.

**`UserPreferences`** (`preference`)

- Project-local worktrees by default for isolated work; parallel sessions are opt-in only
- Sub-agents by default — dispatch independent work; don't do everything inline
- Simple solutions over clever ones — avoid over-engineering and speculative abstractions
- Use haiku or other efficient models for dispatch/sub-agent tasks
- Terse responses — no trailing summaries, no preamble

**`CodingStyle`** (`standard`)

- Conventional commits: `feat:`, `fix:`, `chore:`, `deploy:` — no emojis in commit messages
- 2-space indentation for config files (YAML, TOML, JSON)
- No emojis anywhere unless explicitly requested
- No manually wrapped prose — let formatters handle line length
- Staging discipline: `git add <specific files>` only, never `git add -A` or `git add .`

**`ToolPreferences`** (`preference`)

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
rosemary query "natural-language question"   # hybrid semantic (requires --features documents)

# Write
rosemary create-entities "name" "type"
rosemary add-observations "name" "content"
rosemary create-relations "from" "to" "relation_type"

# Documents
rosemary ingest <path>                        # load docs into the document tier

# Delete
rosemary delete-entities "name1" "name2" ...
rosemary delete-observations "name" "exact content"
rosemary delete-relations "from" "to" "relation_type"

# Maintenance
rosemary compact          # archive + refresh FTS/vector (requires --features documents)
rosemary stats            # entity / relation / observation counts
rosemary init --local     # opt-in: project-local graph (only on explicit user request)
```

## Fallback: Local Files

Used only when `rosemary` is not available. All belong in `.gitignore`. The task dispatcher and knowledge tier have no file fallback — they require rosemary.

- `.agents/CURRENT_TASK.md` — task state (overwrite each session end)
- `.agents/CONTEXT.md` — project conventions (update in place; remove stale entries)
- `.agents/MEMORY.md` — cross-project facts (append; update in place for duplicates)
