---
name: asobi
description: Use Asobi's persistent SQLite knowledge graph for session continuity, durable task dispatch, keyword recall, and reusable skills.
metadata:
  author: haru
  version: 2.7.2
---

# Asobi Skill

Use Asobi as the canonical shared state store. Session state, task state, decisions and pitfalls belong in the graph rather than in chat-only notes or local todo files. Skills live on the filesystem — see [Skills](#skills).

Resolve graph scope before reading or writing. Asobi searches ancestors for `asobi.toml`, then `.asobi/`, and otherwise uses shared XDG state; `ASOBI_HOME` overrides discovery. A nested repository can inherit its parent's graph. Follow the workspace's intended ownership and inspect the discovered configuration; changing directories into a submodule does not guarantee shared state. Create local state with `asobi init --local` only when requested.

Read commands emit their JSON payload on stdout; `asobi skills show` emits Markdown. Mutating commands print a one-line confirmation to **stderr** and leave stdout empty, so branch on the exit code rather than on stdout being non-empty. Pass the global `--json` flag when a mutation's result needs parsing — it prints the affected entities to stdout and removes the follow-up `show`. Check `asobi --version` and command help against the installed CLI before relying on an unfamiliar operation.

## State model

- **Truth** — current state, such as `status`, `next`, `version`, or a date. Writing the same key updates it.
- **Observation** — append-only history, such as a completed session, implementation note, decision, or lesson.
- **Relation** — a directed connection between entities.

`graph` and `search` are lean reads: they return truths, observation counts, and relations without observation bodies. Use `show` for selected full content, `--with-ids` for observation IDs, and `--expand part_of` for an epic and its tasks.

Use `asobi schema --command NAME` when a scripted caller needs the exact response contract.

## Types and naming

The type passed to `asobi new` decides what later `--where` filters and `compact` see, so choose it deliberately:

| Type | Use for |
| --- | --- |
| `project` | Stable per-project facts and architecture decisions |
| `session` | Volatile session state, rewritten each closeout |
| `task` | Epics and their dispatchable child tasks |
| `concept` | Decisions, pitfalls, technical definitions |
| `preference` | Cross-project user or tool preferences |
| `standard` | Conventions that apply everywhere |
| `reference` | Pointers to external resources and URLs |

`compact` projects only the durable types (`project`, `concept`, `reference`, `preference`, `standard`) to Markdown; `session` and `task` stay graph-only. `purge` accepts only `session` and terminal `task`. Typing a decision as `session` therefore loses it on both counts.

Names are hierarchical and colon-separated: `[project]`, `[project]:session`, `[project]:[epic]`, `[project]:[epic]:task-N`, `[project]:decision:[slug]`, `[project]:pitfall:[slug]`. Cross-project entities keep their bare names — `UserPreferences`, `CodingStyle`, `ToolPreferences`. Relations read as verb phrases: `part_of`, `depends_on`, `supersedes`, `extends`, `uses`, `blocks`.

Create in batches rather than one call per entity: `new` takes repeated `NAME TYPE` pairs (`new A task B concept`) and seeds observations onto all of them with repeatable `--obs`, and `link` takes repeated `FROM TO TYPE` triples. `new` no-ops on names that already exist, so it is safe to re-run.

## Detect Asobi

Run `command -v asobi` once at session start. If unavailable, report that persistence is unavailable and continue independent work. If the task itself requires graph access, explain that dependency and request installation; do not claim that state was loaded or saved.

## Session start

In the selected graph, load the project and session plus any preferences stored there. Shared preferences may require a separate read from the configured shared graph. Current user instructions override recalled preferences; verify drift-prone state against Git and the relevant live system.

```bash
asobi show UserPreferences CodingStyle ToolPreferences "[project]" "[project]:session"
```

Then read what is open, which needs no epic name:

```bash
asobi tasks list
```

Load active project pitfalls without opening every entity:

```bash
asobi search "pitfall" --where status=active
```

Report only `[project]:pitfall:*` entities. Compare the session's or task's `commit` truth against `git log --oneline -5`: a checkpoint records the revision it was taken at, so a mismatch says exactly how far the tree has moved since, rather than leaving staleness to be judged by eye.

Briefly report the relevant last task and next action when a prior session exists. Surface applicable active pitfalls and discrepancies without dumping the graph or inventing continuity for an empty result.

## Session end

First resolve the project name from the repository or workspace you actually
worked in, then read that project's session before writing it. Replace every
`[project]` below with that verified name; never copy a session entity from a
different project or write a generic session name into a shared graph. If the
existing session's prefix does not match the current project, correct the
target before continuing. Record the repository revision as part of the
handoff, because session writes do not capture it automatically.

```bash
asobi new "[project]:session" session
asobi truth "[project]:session" objective "[objective or active epic]"
asobi truth "[project]:session" status "[IN_PROGRESS|BLOCKED|REVIEW|DONE]"
asobi truth "[project]:session" remaining "[what remains]"
asobi truth "[project]:session" next "[single most important next action]"
asobi truth "[project]:session" last-updated "YYYY-MM-DD"
asobi truth "[project]:session" branch "$(git branch --show-current)"
asobi truth "[project]:session" commit "$(git rev-parse HEAD)"
asobi obs "[project]:session" "completed YYYY-MM-DD: [finished work]"
```

Record durable project facts on `[project]`, cross-project facts on `UserPreferences`, `CodingStyle`, or `ToolPreferences`, and decisions or pitfalls in their dedicated entities. Check `asobi search "[topic]"` before adding a duplicate.

`tasks sync` and `tasks close` record `commit` and `branch` truths automatically inside a git worktree, so a task checkpoint already carries its revision; a session truth does not. Use `asobi compact` only as requested maintenance — ordinary closeout needs the state writes above and nothing else.

## Tasks — primary workflow

Use the task dispatcher for work that benefits from durable checkpoints or handoff. A small one-step task can use session closeout alone. Human-facing plans belong in the project's documentation; store status and a pointer in Asobi instead of maintaining two competing plans.

An epic is the objective; its child tasks are ordered dispatchable units. The dispatcher owns task creation, links, status transitions, dispatch notes, and closeout.

### Plan

Create a finite epic with concrete completion criteria. List tasks in dependency order; use explicit task names when dispatching, since creation order alone does not enforce dependencies:

```bash
asobi tasks plan "[project]:[epic]" \
  --objective "[what this epic delivers]" \
  --task "[first dispatchable task]" \
  --task "[next dispatchable task]"
```

Point the session at the epic:

```bash
asobi truth "[project]:session" objective "[project]:[epic]"
```

### List

`asobi tasks list` with no epic is the "what is open" read across every project — it returns only unfinished work, so it is cheap enough for session start. Name an epic for that board alone:

```bash
asobi tasks list                      # open work everywhere
asobi tasks list "[project]:[epic]"   # one board
asobi tasks list --all                # include finished work
```

An epic with all children `DONE` but no `status` of its own appears alone, with no open children under it: that is an epic whose work finished and which nobody closed. Close it rather than leaving it to reappear every session.

Use `asobi show "[project]:[epic]" --expand part_of` only when task observations or linked details are needed.

### Dispatch

Dispatch the intended task by name to avoid claiming unrelated work in the same graph:

```bash
asobi tasks dispatch "[project]:[epic]:task-N"
asobi tasks dispatch "[project]:[epic]:task-N" --agent "[agent]"
```

Dispatch claiming is atomic. It records a claim; it does not launch an agent. Follow the current workspace's delegation policy, use subagents for independent bounded work, and reserve worktrees or parallel sessions for explicit opt-in. `--agent` labels the claim for the chosen worker.

Before dispatch, read the task and search relevant lessons:

```bash
asobi show "[project]:[epic]:task-N" --expand depends_on
asobi search "[task title]"
```

### Sync

Record implementation or review notes and advance the task:

```bash
asobi tasks sync "[project]:[epic]:task-N" \
  --status REVIEW \
  --note "[files changed; verification result; review notes]"
```

Use `AWAITING_VERIFY` when a human or device check remains, and `DONE` only after the required verification is complete.

### Close

Close an all-DONE epic and promote a durable lesson when useful:

```bash
asobi tasks close "[project]:[epic]" \
  --lesson "[convention or decision learned]"
```

The task lifecycle is `READY_TO_DISPATCH → DISPATCHED → REVIEW → AWAITING_VERIFY → DONE`. Keep the next action in the session truth.

## Recall and decisions

Use SQLite FTS5/BM25 keyword search for graph recall:

```bash
asobi search "WAL concurrency"
asobi search "auth" --limit 500
asobi search --where status=READY
```

Use `show` for the full observations of selected entities. Use `graph` only when the full lean graph is required.

Record non-obvious decisions as concepts:

```bash
asobi new "[project]:decision:[slug]" concept
asobi obs "[project]:decision:[slug]" "decision: [chosen path]"
asobi obs "[project]:decision:[slug]" "context: [constraints]"
asobi obs "[project]:decision:[slug]" "consequences: [accepted trade-offs]"
asobi link "[project]:decision:[new]" "[project]:decision:[old]" supersedes
```

Rejected approaches become `[project]:pitfall:[slug]` entities with a `status` truth, which is what makes the session-start search above cheap. The revise skill owns writing them.

## Skills

**The skills directory is the store of record** — `.agents/skills` by default. Search a skill with `rg` over that directory; `asobi skills show` prints one.

Prefer the declarative path. When `asobi.toml` declares `[skills]`, edit that selection and run `asobi skills sync` from its workspace root:

```bash
asobi skills sync
asobi skills               # what is installed, with each one's source commit
asobi skills show "[name]"
```

`sync` treats the config as the whole truth: it installs what is declared and prunes what is not, so removing a source from the config removes its skills. Where no `[skills]` block exists, install imperatively instead — this is the only option under a plain `asobi init`, which writes no `asobi.toml`:

```bash
asobi skills install "[git-url-or-path]" --select skill-a skill-b
asobi skills install "[git-url-or-path]" --all
asobi skills update "[source]"
```

`--all` synchronizes one source and drops what vanished upstream; `--select` is additive. Neither disturbs another source's skills. A skill is a directory containing `SKILL.md`; Asobi installs that file and sibling Markdown files (including `references/`) inside the same skill directory. It does not create or copy a shared `.agents/references/` directory. Non-Markdown files such as `scripts/` and `assets/` are skipped with a warning, so a skill must not depend on them being installed. Keep relative references inside the skill's own directory and verify them after installation.

Four things that decide whether a declaration works:

- `select` names come from each skill's frontmatter `name:`, which is often not its directory name.
- When a source mirrors the same skills across several tool-specific directories, scope the walk with `subdir`, or the duplicate copies collide on name.
- `rev` pins a source to a commit, tag, or branch. Without it a re-sync adopts whatever the source moved to.
- Never hand-edit an installed skill; the next sync overwrites it. Edit the source repository.

**Review before trusting.** A skill is natural-language instruction loaded straight into an agent's context, and the published skill ecosystem has a measured supply-chain problem, so an unreviewed skill update is an unreviewed behaviour change. Where the repository tracks the skills directory, commit the materialized files together with the declaration and read the diff — that is what makes an upstream change reviewable at all. `sync` records each installed skill's directory, source and resolved commit in `skills.json` under Asobi's resolved `data_dir`; the manifest names the skills directory it describes and is regenerated, so it normally does not belong in the project tree. The declaration and reviewed skill files are the durable installation record.

## Retention and recovery

Observations are capped at 200 per entity by default. Keep current state in truths and consolidate old observation trails when needed.

Retention is automatic: finished sessions and terminal tasks older than `retention_days` (7 by default, configurable in `asobi.toml` or `ASOBI_RETENTION_DAYS`) are deleted once per process, immediately before that process's first mutating write. Read-only commands do not trigger it, and later writes in the same process do not repeat it. Treat the sweep as already done rather than adding a separate closeout purge.

`purge` previews that policy, or sweeps a narrower window:

```bash
asobi purge --older-than 30          # preview, the default
asobi purge --older-than 30 --apply
```

It reaches terminal sessions and tasks only.

Back up by copying the file; move one entity between graphs with `new`/`truth`/`obs` against the target.

```bash
cp .asobi/data/asobi.db backup.db          # project-local
cp ~/.local/share/asobi/data/asobi.db .    # XDG
```
