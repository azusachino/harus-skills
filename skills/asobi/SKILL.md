---
name: asobi
description: Use Asobi's persistent SQLite knowledge graph to share state across sessions and agents — session continuity, durable task dispatch, keyword recall, and the skill library. Auto-triggers when the user says "start session", "let's continue", "dispatch the next task", "wrap up", "end session".
metadata:
  author: haru
  version: 2.3.0
---

# Asobi Skill

Share durable state across conversations and sub-agents using the `asobi` CLI knowledge graph. Asobi is one primitive — a graph any agent can read and write — exposed through four pillars:

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
| **Task dispatcher** | `/asobi tasks plan\|list\|dispatch\|sync\|close` | primary durable, cross-agent task workflow with atomic claiming — replaces TodoWrite / local jsonl |
| **Knowledge tier** | `/asobi recall` | keyword/entity search over the SQLite graph + a decision log |
| **Skill library** | `/asobi skills` | install/update agent skills from git into the graph |

**Core principle**: `asobi` is the canonical store and is required — there is no local-file fallback. Task state lives in the graph, never in an ephemeral in-conversation todo list — that is the whole point: a dispatched sub-agent and the lead coordinate *through the graph*, not through the user.

**State scope** — default to **shared (XDG global) state**. Project-local state (`asobi init --local` → `./asobi.toml`) is opt-in only on explicit request. Cross-project entities (`UserPreferences`, `CodingStyle`, `ToolPreferences`) always live in the global graph regardless of scope.

**CLI stream contract** — read commands write JSON to stdout. Mutating commands write a confirmation to stderr and leave stdout empty unless the global `--json` flag is passed; use `asobi schema --command NAME` to inspect a command's JSON contract.

## Primitives — trail vs state

One graph, two ways to write a fact onto an entity — picking the right one *is* the skill:

- **Observation** — an append-only log line. The *trail*: what happened, in order. Capped (oldest evicted past 200 per entity). Use for history: `completed:`, `impl:`, `TL-review:`, decision context. Each observation carries a stable integer ID (`show --with-ids`) — edit one in place with `update-obs` or delete it with `rm-obs`, by ID or by exact content.
- **Truth** — a `key → value` fact that **upserts in place**. The *current state*: `status`, `next`, `version`, dates. Writing the same key again overwrites the old value — no stale accumulation, no delete-then-recreate dance.
- **Relation** — a directed edge `(from, to, type)` between two entities (`part_of`, `supersedes`, `depends_on`).

`search` / `graph` return **truths, `observationCount`, and matching relations only** (cheap, lazy-read) — observations and skill bodies are omitted. Anything you scan often (a task's `status`) belongs in a truth: readable without `show`. `show` additionally returns the full observation list and a skill body; add `--with-ids` for each observation's integer ID, or `--expand <relation_type>` to pull linked entities into the same payload. Use `export` or `backup` when a complete archival payload is required.

Write current state with `asobi truth <name> <key> <value>` (upserts); append history with `asobi obs`. The 200-observation cap (overridable via `ASOBI_OBSERVATION_LIMIT` or `asobi.toml`) applies to observations only — truths never count toward it. Overwriting a truth keeps the old value in a valid-time audit trail; read it with `asobi history <name> [key]`.

Two ergonomics worth habituating: add `--json` to any mutating command to print the affected entity and skip a follow-up `show`; and batch — `new A task B concept`, `link A B part_of C D supersedes`, `new X task --obs "seed"` all take repeated args in one call.

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

`asobi show UserPreferences CodingStyle ToolPreferences [repo-basename] [project]:session`. If any entity is missing from the output, it doesn't exist yet — seed it from Global Seed Values. If the session entity is missing, treat as a fresh start. If `[project]:session` references an active epic, also load it: `asobi show "[project]:[epic]" --expand part_of` pulls the epic and all its task children in a single payload (or `asobi search "[epic-name]"` for a truths-only board).

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

The truths upsert, so the session entity stays clean on its own — the `completed:` trail is the only thing that grows, and it is useful history (prune it only if it nears the 200-cap).

**Step 2 — Save new facts** (cross-project): `asobi search "[topic]"` to check for duplicates, then `asobi obs [UserPreferences|CodingStyle|ToolPreferences] "[fact]"`.

**Step 3 — Save project context** (conventions, patterns, decisions): `asobi search "[topic]"`, then `asobi obs [repo-basename] "[fact]"`.

**Step 4 — Compact** (optional): run `asobi compact` to refresh Markdown projections for durable knowledge. It syncs **durable knowledge only** (`project`/`concept`/`reference`/`preference`/`standard`) — volatile `session`/`task` and self-indexing `skill` entities remain graph-only and are read with `search`/`show`. Use `asobi compact --older-than DAYS` when pruning old session Markdown files.

**Step 5 — Confirm**: "Session saved. Next: [one-sentence handoff]."

## `/asobi tasks` — Task Dispatcher

Asobi 0.6.0 added the durable task dispatcher commands `tasks plan`, `list`, `dispatch`, `sync`, and `close`, with nested help, lifecycle validation, and JSON response schemas. Dispatch claiming is atomic: the status transition, claimant truth, and dispatch observation commit together, so concurrent agents produce one winner. Use these commands as the normal task workflow; do not recreate task state in an in-conversation todo list.

The dispatcher stores an **epic** with an objective and ordered child **task** entities. It owns task links, status truths, dispatch observations, and lifecycle transitions; the session entity points at the active epic and next task. Treat those graph details as implementation context — use `asobi tasks`, not manual `new`/`truth`/`obs`/`link` commands, for task planning and state transitions.

### `tasks plan <epic-name>`

Create an epic and its child tasks in execution order:

```bash
asobi tasks plan "[project]:[epic]" \
  --objective "[what this epic delivers]" \
  --task "[first dispatchable task]" \
  --task "[next dispatchable task]"
```

The command creates the epic and task children, links them with `part_of`, and preserves the supplied execution order. Order tasks **smallest → biggest** to build momentum. Point the session at the epic with `asobi truth "[project]:session" objective "[epic] — see [project]:[epic]"`.

### `tasks list [epic-name]`

Use the task board directly:

```bash
asobi tasks list "[project]:[epic]"
```

For lower-level graph inspection, `asobi search "[epic]"` returns each task's `status` truth + `observationCount` without loading observations, while `asobi show "[epic]" --expand part_of` loads the epic and child details:

```
[project]:[epic]
  task-1  Responsive app shell          DONE
  task-2  Taking flow + flashcards      REVIEW
  task-3  Mobile e2e smoke              READY_TO_DISPATCH
  task-4  Explore page minWidth         BLOCKED_ON task-1
```

### `tasks dispatch [task]`

Pick the next `READY_TO_DISPATCH` task (or the named one). **Sub-agent dispatch is opt-in** — by default the lead executes the task inline and records the outcome back into the task entity itself. Spawn a sub-agent only when the user asks or the work is genuinely independent; either way, the result is written **back into the task entity** — not just into the conversation:

```bash
asobi tasks dispatch "[project]:[epic]:task-N" --agent "[agent]"
```

Before briefing the sub-agent, search task-relevant lessons:

```bash
asobi search "[task title]"
```

Also inspect the shown task for `depends_on` relations to `[project]:pitfall:<slug>` and include those linked pitfalls as explicit warnings. The relation direction is `task --depends_on--> pitfall`, meaning the task depends on knowing the warning.

When you do dispatch, brief the sub-agent from the task's `title` truth, task plan (`show` the task), task-relevant search results, and any linked active pitfalls. The default agent is `lead`; pass `--agent` for an explicit agent name. The command records the dispatch state atomically.

```bash
asobi tasks sync "[project]:[epic]:task-N" \
  --status REVIEW \
  --note "[what changed; files touched; make check result]"
```

**Dispatch models** — pick per epic:

- **Sequential (default, proven)** — one agent at a time, no worktrees; lead reviews the working-tree diff and commits after each task. Use when tasks overlap files or need a verify-gate.
- **Worktree-per-task (opt-in)** — each independent task in its own worktree under the project, dispatched in parallel, merged per task. Use only for genuinely disjoint files.

### `tasks sync [task]`

The lead reviews the dispatched diff, records the outcome, and advances status. Never blind-trust a sub-agent's diff — note anything you trimmed:

```bash
asobi tasks sync "[project]:[epic]:task-N" \
  --status AWAITING_VERIFY \
  --note "TL-review YYYY-MM-DD: [diff verdict; what was adjusted]"
# or
asobi tasks sync "[project]:[epic]:task-N" \
  --status DONE \
  --note "done: committed on [branch] YYYY-MM-DD"
```

Then re-point the session `next` truth at the following task, and unblock dependents — upsert each dependent's `status` truth from `BLOCKED_ON task-N` to `READY_TO_DISPATCH` (`tasks list` will now show them ready).

### `tasks close <epic-name>`

When every task is `DONE`, close the epic and optionally promote lessons to the project entity:

```bash
asobi tasks close "[project]:[epic]" \
  --lesson "[convention or decision learned during the epic]"
```

### Status lifecycle

`READY_TO_DISPATCH → DISPATCHED → REVIEW → AWAITING_VERIFY → DONE`. Dependents hold a `status` truth of `BLOCKED_ON task-N` until their dependency is `DONE`. Each transition **upserts** the `status` truth — the current state is always one cheap read, while the `impl:` / `TL-review:` / `done:` observations stay the append-only audit trail.

## `/asobi recall` — Knowledge Tier

Asobi 0.6 uses SQLite FTS5/BM25 keyword search over graph observations, with an entity-name/type fallback.

```bash
asobi search "WAL concurrency"
asobi search "auth" --limit 500
asobi search --where status=READY
```

Use `search` for ranked recall and `show` for the selected entities' full observations and skill bodies. Use `graph` when the full lean graph is required; do not treat a broad `search` as a complete export.

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

Surface them with `asobi search "[topic]"`.

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

Install reusable agent skills straight into the graph from a git repo or local path. Each skill's frontmatter + body is stored as an entity. Skill bodies are lazy in `graph`/`search`; use `asobi skills show` or `asobi show` when the instructions are needed.

```bash
asobi skills install <git-url|path> --all          # install/sync every skill found
asobi skills install <git-url|path> --select a b   # install only the named skills
asobi skills install <git-url|path>                # interactive picker (TTY required)
asobi skills                                       # list installed skills, grouped by source
asobi skills show <name>                           # print one skill's raw body
asobi skills update [source]                       # refresh from source (all, or one slug/URL)
asobi skills remove <name|source>                  # drop one skill or a whole source
```

Git sources are shallow-cloned to a reused cache (`.asobi/caches/<slug>`); `update` does `git fetch` + `reset --hard`, re-cloning if that fails (needs `git` on `$PATH`). Installed names are `skill:<slug>:<name>`; `show`/`remove` also accept the short name.

**Efficient use**: install a curated set in one call with `--select a b c` (use `--all` only for a whole repo); afterward use `asobi skills show <name>` instead of re-fetching the repo; refresh with `update`, treating upstream as source of truth — never hand-edit installed skill entities. `--all` synchronizes the source and prunes skills removed upstream; `--select` remains additive. Example: `asobi skills install https://github.com/azusachino/asobi --all`.

## Pruning & Maintenance

Each entity caps at **200 observations** by default (overridable via `ASOBI_OBSERVATION_LIMIT` or `asobi.toml`'s `observation_limit`) — you can't append forever. **Truths are exempt: they upsert in place and never count toward the cap** — keeping current state (`status`, `next`, dates) in truths is the first defense against fill-up. Only observations accumulate. Run `asobi stats --per-entity` to see which entities are near their cap. Append freely during active work, but when an entity fills, **rewrite and consolidate** rather than pile on: merge duplicate facts and collapse a closed task's observation trail to its final `impl:` + `done:` (its `status` truth is already just `DONE`). Decisions are the exception — never delete one; supersede it (`link [new] [old] "supersedes"`) so the *why* of the reversal survives.

Edit or delete a single observation by its integer ID (from `show --with-ids`), which sidesteps fragile string matching: `asobi update-obs [name] [id] "[new content]" --id` rewrites it in place; `asobi rm-obs [name] [id] --id` removes it. Content matching still works when you'd rather copy the exact string from `show`: `asobi rm-obs [name] "[exact content]"`, and `asobi rm-obs [name] "prefix" --prefix` clears every observation sharing a prefix in one call. To correct a truth, just `truth` the new value (it overwrites) or `rm-truth [name] [key]`. Never prune an in-flight session or an open epic's live trail.

### Safe retention

`purge` is preview-first and restricted to operational entities: `session` plus terminal `task` statuses (`DONE`, `CLOSED`, or `ABANDONED`). It never purges durable knowledge or skills and does not run implicitly during `graph`, `search`, `compact`, or startup. Review the candidates first, then add `--apply`:

```bash
asobi purge --type task --status DONE --older-than 90
asobi purge --type task --status DONE --older-than 90 --apply
```

Use `--dry-run` explicitly when scripting a preview. Purge is transactional and cleans related observations, relations, and search data.

**Handoff & archival** — the graph is the store, but two paths move it out-of-band. `asobi export [--scope <entity>] [--rationale]` writes a portable JSON bundle (whole graph, or one epic + its task subtree with `--scope`, optionally including the cited decision chain via `--rationale`); `asobi import` reads it back — this is the format for teammate, machine, or backend handoff. `asobi backup [--keep N]` / `asobi restore <file>` take physical SQLite snapshots including graph state and skill bodies for local disaster recovery. Truth history is local physical state and rides along with `backup`, not with JSON `export`.

## Entity Reference

| Entity | Type | Lifecycle | Holds (truths = current state · observations = trail) |
| --- | --- | --- | --- |
| `[project]:session` | `session` | `new` once; state truths upsert, `completed:` trail appends | truths: `objective`, `status`, `remaining`, `next`, `last-updated` · obs: `completed:` log |
| `[project]:[epic]` / `:task-N` | `task` | Epic-scoped — `new` once, `status` truth upserts, obs trail appends, rests `DONE` on close | truths: `title`, `status` (epic: `objective`) · obs: `plan:`, `impl:`, `TL-review:`, `done:` (epic: `scope:`, `outcome:`) |
| `[project]:decision:<slug>` | `concept` | Persistent — `new` once, link with relations | obs: `decision`, `context`, `consequences`, `date` |
| `[project]:pitfall:<slug>` | `concept` | Persistent warning — `status` truth starts `active`, flips to `resolved` when obsolete | truths: `status`, `title` · obs: `tried:`, `why-it-failed:`, `do-instead:`, `date:`, `resolved:` |
| `[repo-basename]` | `project` | Persistent — append, then consolidate under the 200-obs cap; never delete the entity | obs: architecture decisions + why, non-obvious conventions, key commands, stack |
| `UserPreferences` / `CodingStyle` / `ToolPreferences` | `preference` / `standard` | Persistent, global — append, then consolidate under the 200-obs cap | obs: cross-project prefs (see Global Seed Values) |

Remaining types: `reference` (external URLs/resources). Write protocol for every entity:

1. `asobi search "[topic]"` — check the fact doesn't already exist.
2. If the entity is missing: `asobi new [name] [type]` first.
3. **Current-state** field (`status`, `version`, a date, `next`): `asobi truth [name] [key] [value]` — it upserts, so just write the new value (no delete needed). **Append-only history**: `asobi obs [name] "[fact]"` — never overwrite, always append.
4. To fix a stale observation: `asobi update-obs [name] [id] "[new content]" --id` rewrites it in place (get the ID from `show --with-ids`), or `asobi rm-obs [name] [id] --id` then re-add. To fix a truth: just `truth` again (overwrites), or `asobi rm-truth [name] [key]`.

## Global Seed Values

If an entity is missing from `show`, create and seed it immediately. These are established cross-project defaults — do not ask the user to confirm them.

**`UserPreferences`** (`preference`) — how you work with me

- **Think first, then stop-and-ask (fail-fast)** — surface assumptions and tradeoffs before acting; if multiple interpretations exist, present them rather than pick silently; on any ambiguity (an error you don't understand, a missing tool, state that contradicts your assumptions) halt and ask instead of improvising a fallback or guessing flags. One clear question beats three speculative attempts. This is the canonical rule other skills point to.
- **Goal-driven** — turn the task into a verifiable check and loop until it's green ("fix the bug" → a test that reproduces it, then make it pass); leave one runnable check behind for non-trivial logic
- Work inline by default; worktrees and sub-agents are **opt-in** — reach for them only when the user asks or the work is genuinely isolated/parallel
- When you do dispatch, use haiku or other efficient models for scoped sub-agent tasks
- Terse responses — no preamble, no trailing summaries

**`CodingStyle`** (`standard`) — how code is written

- **KISS + YAGNI — climb the lazy ladder**: does it need to exist? → reuse what's already in the codebase → stdlib/native platform feature → an already-installed dep → one line → minimal code that works. Deletion over addition, boring over clever
- **Understand before you change** — trace the full flow first; the smallest diff in the wrong place is a second bug. Never simplify away validation at trust boundaries, error handling, security, or accessibility
- **Surgical changes** — every changed line traces to the request; match existing style, don't refactor or reformat adjacent code; remove only the orphans your change creates (mention other dead code, don't delete it)
- **Bug fix = root cause** — grep the callers and fix once where they route through, not per-symptom
- **Mark a deliberately cut corner** with a comment naming the ceiling + upgrade path
- Conventional commits (`feat:`/`fix:`/`chore:`/`deploy:`, emojis welcome); atomic commits — one logical change per commit; SemVer + Keep a Changelog
- 2-space indentation for config files (YAML, TOML, JSON); no manually wrapped prose; `git add <specific files>` only, never `git add -A`

**`ToolPreferences`** (`preference`)

- Nix-first: all tools come from devShell (`nix develop`)
- `mise` for language runtimes only (not general tooling); run a project-pinned runtime/tool with `mise x -- <tool>` (alias `mise exec`)
- `make` is the task runner — always reference `make <target>`
- `make check` runs before commits; `make validate` before PRs (enforced by hooks)

## Command Quick Reference

```bash
# Read
asobi graph
asobi search "query" [--limit <N>] [--where KEY=VALUE ...]
asobi show "name1" "name2" ... [--with-ids] [--expand <relation_type> ...]
asobi history "name" [key]                 # superseded truth values + valid-time windows
asobi schema --command NAME                 # inspect a command's JSON response contract
asobi stats [--per-entity] [--json]       # obs counts + limits; --per-entity flags near-cap entities

# Write (append --json to any mutating command to print the affected entity)
asobi new "name" "type" ["name2" "type2" ...] [--obs "content" ...]   # batch: repeated NAME TYPE pairs
asobi obs "name" "content" [<content> ...]        # append-only trail
asobi update-obs "name" "old"|<id> "new" [--id]   # atomic in-place edit (by content, or by ID with --id)
asobi link "from" "to" "relation_type" [<from> <to> <relation_type> ...]   # batch: repeated triples

# Truths (current-state key→value, upserts in place; overwrite is logged to history)
asobi truth "name" "key" "value"
asobi rm-truth "name" "key"

# Skills
asobi skills install <git-url|path> --all  # install/sync a repo's skills into the graph
asobi skills                               # list installed skills
asobi skills update [source]               # refresh installed skills
asobi skills remove <name|source>          # drop a skill or source
asobi skills show <name>                   # print raw body of installed skill

# Delete
asobi rm "name1" "name2" ...               # delete entities (cascades to obs and relations)
asobi rm-obs "name" "exact content"        # delete specific observation (by content)
asobi rm-obs "name" <id> --id              # delete specific observation (by integer ID)
asobi rm-obs "name" "prefix" --prefix      # delete all observations matching a prefix
asobi unlink "from" "to" "relation_type"   # delete specific relation

# Handoff & archival
asobi export [--scope <entity>] [--rationale] [-o file.json]   # portable JSON bundle (whole graph or one epic subtree)
asobi import "file.json"                    # read a JSON bundle back in
asobi backup [--keep <N>] [-o file.db]      # physical SQLite snapshot (graph + skills)
asobi restore "file.db" [--force]           # replace live DB from a snapshot

# Maintenance
asobi compact [--older-than <DAYS>]         # sync durable Markdown projections and prune old sessions
asobi purge [--dry-run]                     # preview operational retention candidates
asobi purge --type task --status DONE --older-than 90 --apply
asobi completions bash|elvish|fish|powershell|zsh
asobi stats            # entity / relation / observation counts — check before a prune pass
asobi init --local     # opt-in: project-local graph (only on explicit user request)
```
