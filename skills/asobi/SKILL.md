---
name: asobi
description: Use to share state across sessions and agents via the asobi CLI knowledge graph — session continuity (start/end), a durable task dispatcher (`/asobi tasks`) that replaces ephemeral TodoWrite/local jsonl, a knowledge tier (`/asobi recall`), and a skill library (`/asobi skills`). Auto-triggers when the user says "start session", "let's continue", "dispatch the next task", "wrap up", "end session".
metadata:
  author: haru
  version: 2.1.1
---

# Asobi Skill

Share durable state across conversations and sub-agents using the `asobi` CLI knowledge graph. Asobi is one primitive — a graph any agent can read and write — exposed through three pillars:

## Table of Contents
- [Primitives — trail vs state](#primitives--trail-vs-state)
- [Naming Convention](#naming-convention)
- [Detect asobi (once, at session start)](#detect-asobi-once-at-session-start)
- [/asobi start](#asobi-start)
- [/asobi end](#asobi-end)
- [/asobi tasks — Task Dispatcher](#asobi-tasks--task-dispatcher)
- [/asobi recall — Knowledge Tier](#asobi-recall--knowledge-tier)
- [/asobi skills — Skill Library](#asobi-skills--skill-library)
- [Pruning & Maintenance](#pruning--maintenance)
- [Entity Reference](#entity-reference)
- [Global Seed Values](#global-seed-values)
- [Command Quick Reference](#command-quick-reference)

| Pillar | Command | What it backs |
| --- | --- | --- |
| **Session continuity** | `/asobi start`, `/asobi end` | resume work after `/clear`, context compaction, or a machine restart |
| **Task dispatcher** | `/asobi tasks plan\|list\|dispatch\|sync\|close` | durable, cross-agent task state — replaces TodoWrite / local jsonl |
| **Knowledge tier** | `/asobi recall` | hybrid semantic search over ingested docs + a decision log |
| **Skill library** | `/asobi skills` | install/update agent skills from git into the graph, recalled alongside docs |

**Core principle**: `asobi` is the canonical store and is required — there is no local-file fallback. Task state lives in the graph, never in an ephemeral in-conversation todo list — that is the whole point: a dispatched sub-agent and the lead coordinate *through the graph*, not through the user.

**State scope** — default to **shared (XDG global) state**. Project-local state (`asobi init --local` → `./asobi.toml`) is opt-in only on explicit request. Cross-project entities (`UserPreferences`, `CodingStyle`, `ToolPreferences`) always live in the global graph regardless of scope.

## Primitives — trail vs state

One graph, two ways to write a fact onto an entity — picking the right one *is* the skill:

- **Observation** — an append-only log line. The *trail*: what happened, in order. Capped (oldest evicted past 50 per entity). Use for history: `completed:`, `impl:`, `TL-review:`, decision context.
- **Truth** — a `key → value` fact that **upserts in place**. The *current state*: `status`, `next`, `version`, dates. Writing the same key again overwrites the old value — no stale accumulation, no delete-then-recreate dance.
- **Relation** — a directed edge `(from, to, type)` between two entities (`part_of`, `supersedes`, `depends_on`).

`search` / `graph` return **truths + `observationCount` only** (cheap, lazy-read) — so anything you scan often (a task's `status`) belongs in a truth: readable without `show`. `show` additionally returns the full observation list and a skill body.

Write current state with `asobi truth <name> <key> <value>` (upserts); append history with `asobi obs`. The 50-observation cap applies to observations only — truths upsert and never accumulate toward it.

## Naming Convention

Entity names use `:` as a hierarchy separator. Keep names verbatim — do not flatten to dashes.

| Pattern | Type | Example |
| --- | --- | --- |
| `<project>:session` | `session` | `ame:session` |
| `<project>:<epic>` | `task` | `ame:mobile-support` |
| `<project>:<epic>:task-<n>` | `task` | `ame:mobile-support:task-3` |
| `<project>:decision:<slug>` | `concept` | `ame:decision:no-pwa` |
| `<project>:pitfall:<slug>` | `concept` | `ame:pitfall:no-local-jsonl` |
| `<repo-basename>` | `project` | `ame` |

`<project>` is the repo basename. Use `-` only inside a single segment (`mobile-support`), `:` only between hierarchy levels.

## Detect asobi (once, at session start)

Run `command -v asobi`. Record the result — do not re-check during the session. If unavailable, stop and tell the user to install it (`cargo install asobi`, or `cargo binstall asobi`); there is no file fallback.

**Scope detection**: if `./asobi.toml` exists in the repo root, asobi auto-uses project-local state — note this but do not switch modes mid-session. Otherwise the global XDG graph is in effect.

## `/asobi start`

**Step 1 — Load state**:

`asobi show UserPreferences CodingStyle ToolPreferences [repo-basename] [project]:session`. If any entity is missing from the output, it doesn't exist yet — seed it from Global Seed Values. If the session entity is missing, treat as a fresh start. If `[project]:session` references an active epic, also load it: `asobi search "[epic-name]"` to pull the epic and its task children.

Then load active project pitfalls:

```bash
asobi search "pitfall" --where status=active
```

From the result, report only entities whose names start with `[project]:pitfall:`. `search` returns truths + observation counts, so this should stay cheap; do not `show` every pitfall during start.

**Step 2 — Freshness check**: run `git log --oneline -5`. If recent commits touch feature files but the loaded context looks unchanged, flag: "Context may be stale — sync at session end."

**Step 3 — Report**: "Session resumed. Last task: [X]. Next: [Y]." If an epic is active, append a one-line task board (see `/asobi tasks list`). Include any freshness warnings. If active pitfalls exist, append: "Active pitfalls: [N] — [title/title/title]." This line is the human-visible proof that pitfall recall ran.

## `/asobi end`

**Step 1 — Save session state**: upsert the current-state fields as **truths** (they overwrite in place, so state never accumulates stale lines — no reset needed), and append one `completed:` observation for the history trail:

```bash
asobi new "[project]:session" "session"   # no-op if it already exists
asobi truth "[project]:session" objective "[what we worked toward; name the active epic if any]"
asobi truth "[project]:session" status "[IN_PROGRESS|BLOCKED|REVIEW|DONE]"
asobi truth "[project]:session" remaining "[what's left]"
asobi truth "[project]:session" next "[single most important next action]"
asobi truth "[project]:session" last-updated "YYYY-MM-DD"
asobi obs "[project]:session" "completed YYYY-MM-DD: [finished items this session]"
```

The truths upsert, so the session entity stays clean on its own — the `completed:` trail is the only thing that grows, and it is useful history (prune it only if it nears the 50-cap).

**Step 2 — Save new facts** (cross-project): `asobi search "[topic]"` to check for duplicates, then `asobi obs [UserPreferences|CodingStyle|ToolPreferences] "[fact]"`.

**Step 3 — Save project context** (conventions, patterns, decisions): `asobi search "[topic]"`, then `asobi obs [repo-basename] "[fact]"`.

**Step 4 — Compact** (optional): if `asobi` was built with the `documents` feature, run `asobi compact` to archive session state to Markdown and refresh the FTS/vector index. Skip silently if unavailable.

**Step 5 — Confirm**: "Session saved. Next: [one-sentence handoff]."

## `/asobi tasks` — Task Dispatcher

A durable replacement for in-conversation todo lists. An **epic** entity holds the objective and scope; **task** entities hold one dispatchable unit each, linked `part_of` the epic. Each task's current `status` is a **truth** (upserts in place; cheaply readable via `search` without loading observations); the `impl:` / `TL-review:` observations are the append-only audit trail. The session entity points at the active epic and the next task.

### `tasks plan <epic-name>`

Break work into an epic + tasks. Create once, then never overwrite:

```bash
asobi new "[project]:[epic]" "task"
asobi truth "[project]:[epic]" objective "[what this epic delivers]"
asobi obs "[project]:[epic]" "scope: [in / out of scope, decided constraints]"

asobi new "[project]:[epic]:task-1" "task"
asobi truth "[project]:[epic]:task-1" title "[one-line goal]"
asobi truth "[project]:[epic]:task-1" status READY_TO_DISPATCH
asobi obs "[project]:[epic]:task-1" "plan: [file paths + line numbers + approach]"
asobi link "[project]:[epic]:task-1" "[project]:[epic]" "part_of"
# ...repeat per task; dependent tasks start with status "BLOCKED_ON task-N"
```

Then point the session at it: `asobi truth "[project]:session" objective "[epic] — see [project]:[epic]"`. Order tasks **smallest → biggest** to build momentum. `title` + `status` are truths so the board renders from a cheap `search`; put concrete file paths and line numbers in the `plan:` observation so the dispatched agent (briefed via `show`) needs zero discovery.

### `tasks list [epic-name]`

`asobi search "[epic]"` returns each task's `status` truth + `observationCount` without loading observations — render the board straight from the truths (no `show` per task):

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
asobi truth "[project]:[epic]:task-N" status DISPATCHED
asobi obs "[project]:[epic]:task-N" "dispatched to [agent] YYYY-MM-DD"
```

Before briefing the sub-agent, query task-relevant lessons:

```bash
asobi query "[task title]"
```

Also inspect the shown task for `depends_on` relations to `[project]:pitfall:<slug>` and include those linked pitfalls as explicit warnings. The relation direction is `task --depends_on--> pitfall`, meaning the task depends on knowing the warning.

Brief the sub-agent from the task's `title` truth, `plan:` observation (`show` the task), task-relevant query results, and any linked active pitfalls. Default agent is `haiku-developer` (efficient model for scoped work) unless the task is correctness-critical. Require the agent to end by recording:

```bash
asobi obs "[project]:[epic]:task-N" "impl: [what changed; files touched; make check result]"
asobi truth "[project]:[epic]:task-N" status REVIEW
```

**Dispatch models** — pick per epic:

- **Sequential (default, proven)** — one agent at a time, no worktrees; lead reviews the working-tree diff and commits after each task. Use when tasks overlap files or need a verify-gate.
- **Worktree-per-task (opt-in)** — each independent task in its own worktree under the project, dispatched in parallel, merged per task. Use only for genuinely disjoint files.

### `tasks sync [task]`

The lead reviews the dispatched diff, records the outcome, and advances status. Never blind-trust a sub-agent's diff — note anything you trimmed:

```bash
asobi obs "[project]:[epic]:task-N" "TL-review YYYY-MM-DD: [diff verdict; what was adjusted]"
asobi truth "[project]:[epic]:task-N" status AWAITING_VERIFY   # human/device check needed
# or
asobi truth "[project]:[epic]:task-N" status DONE
asobi obs "[project]:[epic]:task-N" "done: committed on [branch] YYYY-MM-DD"
```

Then re-point the session `next` truth at the following task, and unblock dependents — upsert each dependent's `status` truth from `BLOCKED_ON task-N` to `READY_TO_DISPATCH` (`tasks list` will now show them ready).

### `tasks close <epic-name>`

When every task is `DONE`: lift the durable lessons out of the volatile task entities into the persistent project entity, then let the epic rest (no delete — the history stays queryable):

```bash
asobi obs "[repo-basename]" "[convention or decision learned during the epic]"
asobi truth "[project]:[epic]" status DONE
asobi obs "[project]:[epic]" "outcome: [PR link] YYYY-MM-DD"
```

### Status lifecycle

`READY_TO_DISPATCH → DISPATCHED → REVIEW → AWAITING_VERIFY → DONE`. Dependents hold a `status` truth of `BLOCKED_ON task-N` until their dependency is `DONE`. Each transition **upserts** the `status` truth — the current state is always one cheap read, while the `impl:` / `TL-review:` / `done:` observations stay the append-only audit trail.

## `/asobi recall` — Knowledge Tier

Semantic recall over your own docs and a decision log. Requires the `documents` feature for `ingest`/`query`; degrade to `search` otherwise.

### Ingest + query

```bash
asobi ingest docs/specs/          # load ONE file or directory into the document tier (one path per call)
asobi ingest ~/.claude/CLAUDE.md  # index an instruction file for semantic recall
asobi query "how does session auth verify tokens"   # hybrid semantic + keyword recall
```

`ingest` takes exactly one `<PATH>` (file or directory) — call it once per path, not as a list. Prefer `query` before re-reading a large doc — it returns the relevant chunks, not the whole file. Re-`ingest` after meaningful doc changes.

**Guardrail — index, never duplicate.** `CLAUDE.md` is the canonical, harness-loaded source of truth; `ingest` makes it *queryable*, not graph-owned. Never copy file content into entities — that creates a second source that drifts. The seed entities (`UserPreferences`/`CodingStyle`/`ToolPreferences`) are the curated, agent-writable slice of global `CLAUDE.md` and stay the primary recall path: `query` hybrid-ranks them *above* ingested chunks, so an ingested instruction file is a full-text safety net, not a replacement for the seed trio.

### Decision log (ADRs)

Record non-obvious choices as decision entities so the *why* survives:

```bash
asobi new "[project]:decision:[slug]" "concept"
asobi obs "[project]:decision:[slug]" "decision: [what was chosen]"
asobi obs "[project]:decision:[slug]" "context: [the forces / constraints]"
asobi obs "[project]:decision:[slug]" "consequences: [trade-offs accepted]"
asobi obs "[project]:decision:[slug]" "date: YYYY-MM-DD"
# link related decisions and the work they constrain
asobi link "[project]:decision:[new]" "[project]:decision:[old]" "supersedes"
asobi link "[project]:[epic]:task-N" "[project]:decision:[slug]" "depends_on"
```

Surface them with `asobi search "[topic]"` or `asobi query "why [topic]"`.

### Pitfall log

Record wrong approaches and dead ends as pitfall entities. A pitfall is not an ADR: decisions explain the path chosen; pitfalls warn future agents away from paths already tried and rejected.

```bash
asobi new "[project]:pitfall:[slug]" "concept"
asobi truth "[project]:pitfall:[slug]" status active          # active | resolved
asobi truth "[project]:pitfall:[slug]" title "[short warning]"
asobi obs "[project]:pitfall:[slug]" "tried: [approach attempted]"
asobi obs "[project]:pitfall:[slug]" "why-it-failed: [root cause / symptom]"
asobi obs "[project]:pitfall:[slug]" "do-instead: [approach that worked, or 'open']"
asobi obs "[project]:pitfall:[slug]" "date: YYYY-MM-DD"
asobi link "[project]:[epic]:task-N" "[project]:pitfall:[slug]" "depends_on"
```

Keep `status` as a truth so `/asobi start` can cheaply surface active pitfalls with `asobi search "pitfall" --where status=active`. When a dead end becomes obsolete, upsert `status` to `resolved` and append a `resolved YYYY-MM-DD:` observation.

## `/asobi skills` — Skill Library

Install reusable agent skills straight into the graph from a git repo or local path. Each skill's frontmatter + body is stored as an entity and (with the `documents` feature) indexed for vector search, so an installed skill is reachable from `asobi query` alongside your ingested docs — one recall path for docs *and* skills.

```bash
asobi skills install <git-url|path> --all          # ingest every skill found
asobi skills install <git-url|path> --select a b   # ingest only the named skills
asobi skills install <git-url|path>                # interactive picker (TTY required)
asobi skills                                       # list installed skills, grouped by source
asobi skills show <name>                           # print one skill's raw body
asobi skills update [source]                       # refresh from source (all, or one slug/URL)
asobi skills remove <name|source>                  # drop one skill or a whole source
```

Git sources are shallow-cloned to a reused cache (`.asobi/caches/<slug>`); `update` does `git fetch` + `reset --hard`, re-cloning if that fails (needs `git` on `$PATH`). Installed names are `skill:<slug>:<name>`; `show`/`remove` also accept the short name.

**Efficient use**: ingest a curated set in one call with `--select a b c` (use `--all` only for a whole repo); afterward recall via `asobi query "<task>"` instead of re-fetching the repo; refresh with `update`, treating upstream as source of truth — never hand-edit installed skill entities. Example: `asobi skills install https://github.com/azusachino/asobi --all`.

## Pruning & Maintenance

Each entity caps at **50 observations** by default — you can't append forever. **Truths are exempt: they upsert in place and never count toward the cap** — keeping current state (`status`, `next`, dates) in truths is the first defense against fill-up. Only observations accumulate. Append freely during active work, but when an entity fills (check `asobi stats`), **rewrite and consolidate** rather than pile on: merge duplicate facts and collapse a closed task's observation trail to its final `impl:` + `done:` (its `status` truth is already just `DONE`). Decisions are the exception — never delete one; supersede it (`link [new] [old] "supersedes"`) so the *why of the reversal survives.

`rm-obs` matches the **exact** string — copy it from `show`, don't paraphrase. To correct a truth, just `truth` the new value (it overwrites) or `rm-truth [name] [key]`. Never prune an in-flight session or an open epic's live trail. With the `documents` feature, follow a prune with `asobi compact` to rebuild the index.

## Entity Reference

| Entity | Type | Lifecycle | Holds (truths = current state · observations = trail) |
| --- | --- | --- | --- |
| `[project]:session` | `session` | `new` once; state truths upsert, `completed:` trail appends | truths: `objective`, `status`, `remaining`, `next`, `last-updated` · obs: `completed:` log |
| `[project]:[epic]` / `:task-N` | `task` | Epic-scoped — `new` once, `status` truth upserts, obs trail appends, rests `DONE` on close | truths: `title`, `status` (epic: `objective`) · obs: `plan:`, `impl:`, `TL-review:`, `done:` (epic: `scope:`, `outcome:`) |
| `[project]:decision:<slug>` | `concept` | Persistent — `new` once, link with relations | obs: `decision`, `context`, `consequences`, `date` |
| `[project]:pitfall:<slug>` | `concept` | Persistent warning — `status` truth starts `active`, flips to `resolved` when obsolete | truths: `status`, `title` · obs: `tried:`, `why-it-failed:`, `do-instead:`, `date:`, `resolved:` |
| `[repo-basename]` | `project` | Persistent — append, then consolidate under the 50-obs cap; never delete the entity | obs: architecture decisions + why, non-obvious conventions, key commands, stack |
| `UserPreferences` / `CodingStyle` / `ToolPreferences` | `preference` / `standard` | Persistent, global — append, then consolidate under the 50-obs cap | obs: cross-project prefs (see Global Seed Values) |

Remaining types: `reference` (external URLs/resources). Write protocol for every entity:

1. `asobi search "[topic]"` — check the fact doesn't already exist.
2. If the entity is missing: `asobi new [name] [type]` first.
3. **Current-state** field (`status`, `version`, a date, `next`): `asobi truth [name] [key] [value]` — it upserts, so just write the new value (no delete needed). **Append-only history**: `asobi obs [name] "[fact]"` — never overwrite, always append.
4. To fix a stale observation: `asobi rm-obs [name] "[exact old content]"`, then re-add. To fix a truth: just `truth` again (overwrites), or `asobi rm-truth [name] [key]`.

## Global Seed Values

If an entity is missing from `show`, create and seed it immediately. These are established cross-project defaults — do not ask the user to confirm them.

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

## Command Quick Reference

```bash
# Read
asobi graph
asobi search "query" [--limit <N>] [--where KEY=VALUE ...]
asobi show "name1" "name2" ...
asobi query "natural-language question"   # hybrid semantic (requires --features documents)

# Write
asobi new "name" "type" [--obs "content" ...]
asobi obs "name" "content" [<content> ...]        # append-only trail
asobi link "from" "to" "relation_type" [<from> <to> <relation_type> ...]

# Truths (current-state key→value, upserts in place)
asobi truth "name" "key" "value"
asobi rm-truth "name" "key"

# Documents
asobi ingest <path>                        # load docs into the document tier

# Skills
asobi skills install <git-url|path> --all  # ingest a repo's skills into the graph
asobi skills                               # list installed skills
asobi skills update [source]               # refresh installed skills
asobi skills remove <name|source>          # drop a skill or source
asobi skills show <name>                   # print raw body of installed skill

# Delete
asobi rm "name1" "name2" ...               # delete entities (cascades to obs and relations)
asobi rm-obs "name" "exact content"        # delete specific observation
asobi unlink "from" "to" "relation_type"   # delete specific relation

# Maintenance
asobi compact          # archive + refresh FTS/vector (requires --features documents)
asobi stats            # entity / relation / observation counts — check before a prune pass
asobi init --local     # opt-in: project-local graph (only on explicit user request)
```
