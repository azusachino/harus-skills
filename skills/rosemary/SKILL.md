---
name: rosemary
description: Use to share state across sessions and agents via the rosemary CLI knowledge graph — session continuity (start/end), a durable task dispatcher (`/rosemary tasks`) that replaces ephemeral TodoWrite/local jsonl, a knowledge tier (`/rosemary recall`), and a skill library (`/rosemary skills`). Auto-triggers when the user says "start session", "let's continue", "dispatch the next task", "wrap up", "end session".
metadata:
  author: haru
  version: 1.4.0
---

# Rosemary Skill

Share durable state across conversations and sub-agents using the `rosemary` CLI knowledge graph. Rosemary is one primitive — a graph any agent can read and write — exposed through three pillars:

| Pillar | Command | What it backs |
| --- | --- | --- |
| **Session continuity** | `/rosemary start`, `/rosemary end` | resume work after `/clear`, context compaction, or a machine restart |
| **Task dispatcher** | `/rosemary tasks plan\|list\|dispatch\|sync\|close` | durable, cross-agent task state — replaces TodoWrite / local jsonl |
| **Knowledge tier** | `/rosemary recall` | hybrid semantic search over ingested docs + a decision log |
| **Skill library** | `/rosemary skills` | install/update agent skills from git into the graph, recalled alongside docs |

**Core principle**: `rosemary` is the canonical store and is required — there is no local-file fallback. Task state lives in the graph, never in an ephemeral in-conversation todo list — that is the whole point: a dispatched sub-agent and the lead coordinate *through the graph*, not through the user.

**State scope** — default to **shared (XDG global) state**. Project-local state (`rosemary init --local` → `./rosemary.toml`) is opt-in only on explicit request. Cross-project entities (`UserPreferences`, `CodingStyle`, `ToolPreferences`) always live in the global graph regardless of scope.

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

Run `command -v rosemary`. Record the result — do not re-check during the session. If unavailable, stop and tell the user to install it (`cargo install --git https://github.com/azusachino/rosemary`); there is no file fallback.

**Scope detection**: if `./rosemary.toml` exists in the repo root, rosemary auto-uses project-local state — note this but do not switch modes mid-session. Otherwise the global XDG graph is in effect.

## `/rosemary start`

**Step 1 — Load state**:

`rosemary open-nodes UserPreferences CodingStyle ToolPreferences [repo-basename] [project]:session`. If any entity is missing from the output, it doesn't exist yet — seed it from Global Seed Values. If the session entity is missing, treat as a fresh start. If `[project]:session` references an active epic, also load it: `rosemary search-nodes "[epic-name]"` to pull the epic and its task children.

**Step 2 — Freshness check**: run `git log --oneline -5`. If recent commits touch feature files but the loaded context looks unchanged, flag: "Context may be stale — sync at session end."

**Step 3 — Report**: "Session resumed. Last task: [X]. Next: [Y]." If an epic is active, append a one-line task board (see `/rosemary tasks list`). Include any freshness warnings.

## `/rosemary end`

**Step 1 — Save session state**: full reset — delete the old session entity and recreate it clean so it never accumulates stale lines:

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

**Step 2 — Save new facts** (cross-project): `rosemary search-nodes "[topic]"` to check for duplicates, then `rosemary add-observations [UserPreferences|CodingStyle|ToolPreferences] "[fact]"`.

**Step 3 — Save project context** (conventions, patterns, decisions): `rosemary search-nodes "[topic]"`, then `rosemary add-observations [repo-basename] "[fact]"`.

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

- **Sequential (default, proven)** — one agent at a time, no worktrees; lead reviews the working-tree diff and commits after each task. Use when tasks overlap files or need a verify-gate.
- **Worktree-per-task (opt-in)** — each independent task in its own worktree under the project, dispatched in parallel, merged per task. Use only for genuinely disjoint files.

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

**Guardrail — index, never duplicate.** `CLAUDE.md` is the canonical, harness-loaded source of truth; `ingest` makes it *queryable*, not graph-owned. Never copy file content into entities — that creates a second source that drifts. The seed entities (`UserPreferences`/`CodingStyle`/`ToolPreferences`) are the curated, agent-writable slice of global `CLAUDE.md` and stay the primary recall path: `query` hybrid-ranks them *above* ingested chunks, so an ingested instruction file is a full-text safety net, not a replacement for the seed trio.

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

## `/rosemary skills` — Skill Library

Install reusable agent skills straight into the graph from a git repo or local path. Each skill's frontmatter + body is stored as an entity and (with the `documents` feature) indexed for vector search, so an installed skill is reachable from `rosemary query` alongside your ingested docs — one recall path for docs *and* skills.

```bash
rosemary skills install <git-url|path> --all          # ingest every skill found
rosemary skills install <git-url|path> --select a b   # ingest only the named skills
rosemary skills install <git-url|path>                # interactive picker (TTY required)
rosemary skills                                       # list installed skills, grouped by source
rosemary skills show <name>                           # print one skill's raw body
rosemary skills update [source]                       # refresh from source (all, or one slug/URL)
rosemary skills remove <name|source>                  # drop one skill or a whole source
```

Git sources are shallow-cloned to a reused cache (`.rosemary/caches/<slug>`); `update` does `git fetch` + `reset --hard`, re-cloning if that fails (needs `git` on `$PATH`). Installed names are `skill:<slug>:<name>`; `show`/`remove` also accept the short name.

**Efficient use**: ingest a curated set in one call with `--select a b c` (use `--all` only for a whole repo); afterward recall via `rosemary query "<task>"` instead of re-fetching the repo; refresh with `update`, treating upstream as source of truth — never hand-edit installed skill entities. Example: `rosemary skills install https://github.com/azusachino/rosemary --all`.

## Pruning & Maintenance

Each entity caps at **50 observations** by default — you can't append forever. Append freely during active work, but when an entity fills (check `rosemary stats`), **rewrite and consolidate** rather than pile on: merge duplicate facts, replace stale lines with the current one, and collapse a closed task's `status:` trail to its final `DONE` + `impl:`. Decisions are the exception — never delete one; supersede it (`create-relations [new] [old] "supersedes"`) so the *why* of the reversal survives.

`delete-observations` matches the **exact** string — copy it from `open-nodes`, don't paraphrase. Never prune an in-flight session or an open epic's live trail. With the `documents` feature, follow a prune with `rosemary compact` to rebuild the index.

## Entity Reference

| Entity | Type | Lifecycle | Holds |
| --- | --- | --- | --- |
| `[project]:session` | `session` | Volatile — `delete`+`create` each `end` | `objective`, `status`, `completed`, `remaining`, `next`, `last-updated` |
| `[project]:[epic]` / `:task-N` | `task` | Epic-scoped — `create` once, append-only `status:` trail, rests `DONE` on close | epic objective/scope; per-task `title`, `status`, `impl` |
| `[project]:decision:<slug>` | `concept` | Persistent — `create` once, link with relations | `decision`, `context`, `consequences`, `date` |
| `[repo-basename]` | `project` | Persistent — append, then consolidate under the 50-obs cap; never delete the entity | architecture decisions + why, non-obvious conventions, key commands, stack |
| `UserPreferences` / `CodingStyle` / `ToolPreferences` | `preference` / `standard` | Persistent, global — append, then consolidate under the 50-obs cap | cross-project prefs (see Global Seed Values) |

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

# Skills
rosemary skills install <git-url|path> --all  # ingest a repo's skills into the graph
rosemary skills                               # list installed skills
rosemary skills update [source]               # refresh installed skills
rosemary skills remove <name|source>          # drop a skill or source

# Delete
rosemary delete-entities "name1" "name2" ...
rosemary delete-observations "name" "exact content"
rosemary delete-relations "from" "to" "relation_type"

# Maintenance
rosemary compact          # archive + refresh FTS/vector (requires --features documents)
rosemary stats            # entity / relation / observation counts — check before a prune pass
rosemary init --local     # opt-in: project-local graph (only on explicit user request)
```
