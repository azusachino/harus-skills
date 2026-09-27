---
name: asobi
description: Use Asobi's knowledge graph, local or shared through asobi-server, for task state, cross-agent dispatch, and keyword recall.
metadata:
  author: haru
  version: 3.0.0
---

# Asobi Skill

Use Asobi as the agents' shared working memory: open work as tasks, decisions and pitfalls as concepts, and cross-project preferences, instead of chat-only notes or local todo files. The project's issue tracker and documentation stay the durable record; promote anything that must outlive the work there when an epic closes.

This skill targets Asobi 0.8 or later. Asobi 0.7 still has session entities and `asobi skills`, both gone in 0.8; check `asobi --version`, and if it is older, say so rather than following this skill. Check command help against the installed CLI before relying on an unfamiliar operation, and use `asobi schema --command NAME` when a scripted caller needs the exact response contract.

Read commands emit JSON on stdout. Mutating commands print a one-line confirmation to **stderr** and leave stdout empty, so branch on the exit code; pass the global `--json` flag when a mutation's result needs parsing.

## Graph scope

Resolve which graph you are in before reading or writing:

- **Local or remote.** A workspace is remote when `remote` is set in its `asobi.toml` or `ASOBI_REMOTE` is set; every command then runs against that server's graph. Otherwise the graph is a local SQLite file.
- **Which graph.** In remote mode, `graph` in `asobi.toml` or `ASOBI_GRAPH` names it (default `asobi`). Locally, Asobi searches ancestors for `asobi.toml`, then `.asobi/`, then uses shared XDG state; `ASOBI_HOME` overrides discovery.
- **Nested repositories inherit.** A command run inside a nested repository or submodule uses the nearest ancestor's `asobi.toml`, including its graph, which may not be the graph that repository's work belongs to. Follow the workspace's convention; where the intended graph differs, set `ASOBI_GRAPH` (or `ASOBI_HOME` locally) for those commands.

Confirm with `asobi stats` before the first write: its `databasePath` names the graph file (on the server in remote mode).

**If a command prints `warning: remote Asobi server unavailable`,** it ran against the local graph instead. Its reads miss shared state, and its writes stay on this device and never reach the server. Tell the user, and do not rely on those writes being visible to other agents. `server does not speak API v3` means `remote` points somewhere that is not an Asobi server: stop and report the configuration.

## State model

- **Truth** — current state, such as `status`, `next`, `branch`, `commit`, or a date. Writing the same key replaces it.
- **Observation** — append-only history: an implementation note, a decision, a lesson.
- **Relation** — a directed connection between entities.

`graph` and `search` are lean reads: truths, observation counts, and relations without observation bodies. Use `show` for full content (`--with-ids` for observation IDs, `--expand part_of` for an epic and its tasks, `--limit 0` for a whole trail).

## Types and naming

| Type | Use for |
| --- | --- |
| `project` | Stable per-project facts and architecture decisions |
| `task` | Epics, their child tasks, and standalone tasks |
| `concept` | Decisions, pitfalls, technical definitions |
| `preference` | Cross-project user or tool preferences |
| `standard` | Conventions that apply everywhere |
| `reference` | Pointers to external resources and URLs |

`compact` projects only the durable types (`project`, `concept`, `reference`, `preference`, `standard`) to Markdown; tasks stay graph-only, and `purge` reaches only terminal tasks. Typing a decision as `task` therefore loses it on both counts.

Names are hierarchical and colon-separated: `[project]`, `[project]:[epic]` with `tasks plan` naming its children `[project]:[epic]:task-N`, standalone `[project]:task:[name]`, `[project]:decision:[slug]`, `[project]:pitfall:[slug]`. Cross-project entities keep bare names: `UserPreferences`, `CodingStyle`, `ToolPreferences`. Relations read as verb phrases: `part_of`, `depends_on`, `supersedes`, `extends`, `uses`, `blocks`.

Create in batches: `new` takes repeated `NAME TYPE` pairs and seeds observations with repeatable `--obs`; `link` takes repeated `FROM TO TYPE` triples. `new` no-ops on existing names, so it is safe to re-run. `obs` and `truth` need the entity to exist; create it with `new` first.

## Detect Asobi

Run `command -v asobi` once before relying on it. If it is unavailable, report that persistence is unavailable and continue independent work; if the task itself requires graph access, explain that and request installation. Never claim that state was loaded or saved when it was not.

## Starting work

There is no session entity. Where work stands is the set of open tasks.

```bash
asobi show UserPreferences CodingStyle ToolPreferences "[project]"
asobi tasks list                                  # open work in this graph
asobi search "pitfall" --where status=active      # active pitfalls
```

A shared graph lists every project's open work; report the tasks under `[project]:` and anything assigned to you. Report only `[project]:pitfall:*` pitfalls. Compare a task's `commit` truth with `git log --oneline -5` in its repository: the checkpoint says exactly how far the tree has moved since. Current user instructions override recalled preferences; verify drift-prone state against Git and the live system. Do not invent continuity for an empty board.

## Ending work or handing off

Record progress on the tasks you actually worked, in the graph you verified:

```bash
asobi tasks sync "[project]:[epic]:task-N" --status REVIEW \
  --note "[what changed; verification result; what remains; next action]"
asobi truth "[project]:[epic]:task-N" branch "$(git -C '[repository-path]' branch --show-current)"
asobi truth "[project]:[epic]:task-N" commit "$(git -C '[repository-path]' rev-parse HEAD)"
```

For work that has no task yet, create one rather than leaving state in chat:

```bash
asobi new "[project]:task:[name]" task --obs "[what this is]"
asobi truth "[project]:task:[name]" status DISPATCHED
```

Record the repository revision explicitly: one graph serves several repositories, so Asobi cannot infer it. Put durable project facts on `[project]`, cross-project facts on `UserPreferences`, `CodingStyle`, or `ToolPreferences`, and decisions or pitfalls in their own entities. Check `asobi search "[topic]"` before adding a duplicate.

## Tasks

An epic is the objective; its child tasks are ordered dispatchable units. The dispatcher owns task creation, links, status transitions, dispatch notes, and closeout. Human-facing plans belong in the project's documentation; keep status and a pointer in Asobi rather than two competing plans.

### Plan

List tasks in dependency order; dispatch by name, since creation order does not enforce dependencies:

```bash
asobi tasks plan "[project]:[epic]" \
  --objective "[what this epic delivers]" \
  --task "[first dispatchable task]" \
  --task "[next dispatchable task]"
```

### List

```bash
asobi tasks list                      # open work in this graph
asobi tasks list "[project]:[epic]"   # one board
asobi tasks list --all                # include finished work
```

An epic whose children are all `DONE` but which has no `status` of its own was finished and never closed; close it.

### Dispatch

Dispatch by name so a claim never lands on unrelated work in a shared graph:

```bash
asobi show "[project]:[epic]:task-N" --expand depends_on
asobi search "[task title]"
asobi tasks dispatch "[project]:[epic]:task-N" --agent "[worker]"
```

A claim is atomic and records who holds the task; it does not start an agent. With a shared graph, the claim and every later note are visible to agents on every machine. A lead coordinating workers, for example over Herdr, plans the epic, dispatches each task to a named worker, and reads progress from the board. Workers sync the task they hold and never re-claim another agent's task. Follow the workspace's delegation policy; worktrees and parallel sessions stay explicit opt-in.

### Sync

```bash
asobi tasks sync "[project]:[epic]:task-N" \
  --status REVIEW \
  --note "[files changed; verification result; review notes]"
```

Use `AWAITING_VERIFY` when a human or device check remains, and `DONE` only after the required verification.

### Close

```bash
asobi tasks close "[project]:[epic]" --lesson "[convention or decision learned]"
```

The lifecycle is `READY_TO_DISPATCH → DISPATCHED → REVIEW → AWAITING_VERIFY → DONE`, plus `ABANDONED` (below). Keep a task's next action in its notes or a `next` truth.

## Recall and decisions

```bash
asobi search "WAL concurrency"
asobi search "auth" --limit 500
asobi search --where status=READY
```

Record non-obvious decisions as concepts:

```bash
asobi new "[project]:decision:[slug]" concept
asobi obs "[project]:decision:[slug]" "decision: [chosen path]"
asobi obs "[project]:decision:[slug]" "context: [constraints]"
asobi obs "[project]:decision:[slug]" "consequences: [accepted trade-offs]"
asobi link "[project]:decision:[new]" "[project]:decision:[old]" supersedes
```

Rejected approaches become `[project]:pitfall:[slug]` entities with a `status` truth, which is what makes the start-of-work search cheap. The revise skill owns writing them.

## Lifecycle and recovery

- **Idle tasks are abandoned.** An open task with no activity (no truth or observation change) for `abandon_days` (7 by default) becomes `ABANDONED`, with an observation saying so. An epic with an open child is never abandoned. Sync or annotate tasks you intend to keep; revive one by setting its `status` truth back.
- **Finished tasks are deleted** `retention_days` (7) after they finish or are abandoned. Locally the sweep runs once per process before its first write; a server sweeps hourly. Treat it as already done rather than adding a closeout purge.
- `purge --older-than N` previews a narrower sweep; `--apply` runs it. It reaches terminal tasks only.
- Observations are capped at 200 per entity; keep current state in truths.
- **Backup.** A local graph is one SQLite file: copy it. A server graph is backed up on the server host, and `reset` is refused over the network.

Skills are not managed by Asobi (0.8 removed `asobi skills`); install them with the [`skills` CLI](https://github.com/vercel-labs/skills).
