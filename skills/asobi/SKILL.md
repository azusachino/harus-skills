---
name: asobi
description: Use Asobi's persistent SQLite knowledge graph for session continuity, durable task dispatch, keyword recall, and reusable skills.
metadata:
  author: haru
  version: 2.4.0
---

# Asobi Skill

Use Asobi as the canonical shared state store. Session state, task state, decisions, pitfalls, and reusable skills belong in the graph rather than in chat-only notes or local todo files.

Asobi uses shared XDG state by default and automatically uses project-local state when `./asobi.toml` or `./.asobi/` exists. Create project-local state explicitly with `asobi init --local`.

Read commands emit JSON on stdout. Mutating commands emit a confirmation on stderr; pass the global `--json` flag when the affected entities are needed immediately.

## State model

- **Truth** — current state, such as `status`, `next`, `version`, or a date. Writing the same key updates it.
- **Observation** — append-only history, such as a completed session, implementation note, decision, or lesson.
- **Relation** — a directed connection between entities.

`graph` and `search` are lean reads: they return truths, observation counts, and relations without observation bodies or skill bodies. Use `show` for selected full content, `--with-ids` for observation IDs, and `--expand part_of` for an epic and its tasks.

Use `asobi schema --command NAME` when a scripted caller needs the exact response contract.

## Detect Asobi

Run `command -v asobi` once at session start. If it is unavailable, stop and ask the user to install it with `cargo install asobi` or `cargo binstall asobi`.

## Session start

Load shared preferences, the project entity, and the project session:

```bash
asobi show UserPreferences CodingStyle ToolPreferences "[project]" "[project]:session"
```

If an active epic is named in the session, load its board:

```bash
asobi tasks list "[project]:[epic]"
```

Load active project pitfalls without opening every entity:

```bash
asobi search "pitfall" --where status=active
```

Report only `[project]:pitfall:*` entities. Also run `git log --oneline -5` and flag stale context when recent feature commits are not reflected in the loaded state.

Report: `Session resumed. Last task: [X]. Next: [Y].` Include the active task board and active pitfall titles when present.

## Session end

Save current session state as truths and append one completion observation:

```bash
asobi new "[project]:session" session
asobi truth "[project]:session" objective "[objective or active epic]"
asobi truth "[project]:session" status "[IN_PROGRESS|BLOCKED|REVIEW|DONE]"
asobi truth "[project]:session" remaining "[what remains]"
asobi truth "[project]:session" next "[single most important next action]"
asobi truth "[project]:session" last-updated "YYYY-MM-DD"
asobi obs "[project]:session" "completed YYYY-MM-DD: [finished work]"
```

Record durable project facts on `[project]`, cross-project facts on `UserPreferences`, `CodingStyle`, or `ToolPreferences`, and decisions or pitfalls in their dedicated entities. Check `asobi search "[topic]"` before adding a duplicate.

Run `asobi compact` to sync durable knowledge to Markdown topics. It does not replace graph reads for sessions, tasks, or skills.

## Tasks — primary workflow

The task dispatcher is the favored workflow for all non-trivial work. Do not maintain task state in an in-conversation todo list or recreate task state manually with graph primitives.

An epic is the objective; its child tasks are ordered dispatchable units. The dispatcher owns task creation, links, status transitions, dispatch notes, and closeout.

### Plan

Create the epic and its tasks in execution order, smallest to largest:

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

Use the task board as the normal status read:

```bash
asobi tasks list "[project]:[epic]"
```

Use `asobi show "[project]:[epic]" --expand part_of` only when task observations or linked details are needed.

### Dispatch

Dispatch the next ready task, or name one explicitly:

```bash
asobi tasks dispatch
asobi tasks dispatch "[project]:[epic]:task-N" --agent "[agent]"
```

Dispatch claiming is atomic, so concurrent agents produce one winner. Sub-agent dispatch is opt-in; run work inline by default and use `--agent` only for an explicitly independent dispatch.

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

Use `show` for the full observations of selected entities. Use `graph` only when the full lean graph is required. Use `export` for portable graph handoff and `backup` for full-fidelity local recovery.

Record non-obvious decisions as concepts:

```bash
asobi new "[project]:decision:[slug]" concept
asobi obs "[project]:decision:[slug]" "decision: [chosen path]"
asobi obs "[project]:decision:[slug]" "context: [constraints]"
asobi obs "[project]:decision:[slug]" "consequences: [accepted trade-offs]"
asobi link "[project]:decision:[new]" "[project]:decision:[old]" supersedes
```

Record rejected approaches as active pitfalls:

```bash
asobi new "[project]:pitfall:[slug]" concept
asobi truth "[project]:pitfall:[slug]" status active
asobi truth "[project]:pitfall:[slug]" title "[short warning]"
asobi obs "[project]:pitfall:[slug]" "tried: [rejected approach]"
asobi obs "[project]:pitfall:[slug]" "why-it-failed: [cause]"
asobi obs "[project]:pitfall:[slug]" "do-instead: [working approach]"
```

## Skills

Use the skill library as the source of truth for installed skills. Prefer explicit non-interactive selection:

```bash
asobi skills install "[git-url-or-path]" --select skill-a skill-b
asobi skills install "[git-url-or-path]" --all
asobi skills update "[source]"
asobi skills show "[name]"
```

`--all` synchronizes a source and removes skills deleted upstream. `--select` is additive. Never hand-edit installed skill entities.

## Retention and recovery

Observations are capped at 200 per entity by default. Keep current state in truths and consolidate old observation trails when needed.

Preview stale operational records before applying retention:

```bash
asobi purge --type task --status DONE --older-than 90
asobi purge --type task --status DONE --older-than 90 --apply
```

Purge is restricted to terminal sessions and tasks; durable knowledge and skills are protected. It is never implicit.

Use SQLite backup/restore for local recovery and JSON export/import for portable handoff:

```bash
asobi backup --keep 5
asobi restore "/secure/asobi.db" --force
asobi export --scope "[project]:[epic]" --rationale -o handoff.json
asobi import handoff.json
```

Generate shell completions from the installed binary:

```bash
asobi completions bash|elvish|fish|powershell|zsh
```
