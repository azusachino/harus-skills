---
name: revise
description: Persist project lessons, findings, and wrong approaches so future sessions can recall them
metadata:
  author: haru
  version: 1.0.0
user-invokable: true
disable-auto-invoke: true
---

# Revise

Persist durable lessons from the current work: work-experiences, findings, and wrong approaches. `/asobi end` records session continuity; `/revise` records what should change future behavior.

## Table of Contents
- [When to Use](#when-to-use)
- [Inputs](#inputs)
- [Flow](#flow)
- [Asobi Route](#asobi-route)
- [Pitfall Entity](#pitfall-entity)
- [Fallback Files](#fallback-files)
- [Recall Contract](#recall-contract)
- [Confirmation](#confirmation)

## When to Use

Use `/revise` after a meaningful discovery, especially when an agent tried something that looked plausible but failed. Capture the lesson while the context is still fresh.

Good candidates:
- A workflow that succeeded and should be repeated
- A non-obvious project fact, gotcha, or convention
- A dead end, incorrect assumption, or rejected approach
- A task-specific warning that future agents should see before dispatch

Do not use `/revise` for ordinary task status. Use `/asobi end` for status, next action, and session handoff.

## Inputs

If the user gives free-form text, classify it yourself. Do not ask follow-up questions unless the lesson is too vague to preserve.

Classification:
- `work-experience`: how work was actually done; store as a project observation
- `finding`: a non-obvious fact, gotcha, or decision context; store as a project observation unless it is an architectural choice, then use a decision entity
- `wrong-approach`: something tried and rejected; store as a `pitfall` entity

Keep lessons short and actionable. Prefer "do X because Y" over a transcript of what happened.

## Flow

1. Detect asobi once: `command -v asobi`.
2. Derive the repo basename for `[project]`.
3. Classify the lesson.
4. Deduplicate before writing:
   ```bash
   asobi search "<topic>" --limit 10
   ```
5. If a matching entity already exists, append a `seen-again: YYYY-MM-DD: <new evidence>` observation instead of creating a duplicate.
6. Route the lesson to asobi when available; otherwise use the project-local fallback files.
7. Confirm in one line with what was persisted and where.

Use shared XDG asobi state unless the repo has opted into project-local state with `./asobi.toml`. Do not run `asobi init --local` unless the user explicitly asks.

## Asobi Route

Before any write, ensure the project entity exists:

```bash
asobi new "[project]" "project"
```

Route by classification:

| Classification | Destination | Write |
| --- | --- | --- |
| `work-experience` | `[project]` | `asobi obs "[project]" "experience YYYY-MM-DD: <lesson>"` |
| `finding` | `[project]` | `asobi obs "[project]" "finding YYYY-MM-DD: <lesson>"` |
| `finding` that records a choice | `[project]:decision:<slug>` | decision observations, then link related tasks if known |
| `wrong-approach` | `[project]:pitfall:<slug>` | pitfall schema below |

Decision entity format:

```bash
asobi new "[project]:decision:<slug>" "concept"
asobi obs "[project]:decision:<slug>" "decision: <what was chosen>"
asobi obs "[project]:decision:<slug>" "context: <forces or constraints>"
asobi obs "[project]:decision:<slug>" "consequences: <trade-offs accepted>"
asobi obs "[project]:decision:<slug>" "date: YYYY-MM-DD"
```

If the lesson belongs to an active epic or task, link from the task to the lesson entity:

```bash
asobi link "[project]:[epic]:task-N" "[project]:pitfall:<slug>" "depends_on"
```

The direction means "this task depends on knowing this warning."

## Pitfall Entity

A pitfall is a rejected approach, not an ADR. ADRs explain chosen paths; pitfalls prevent repeated dead ends.

Use one entity per dead end:

```bash
asobi new "[project]:pitfall:<slug>" "concept"
asobi truth "[project]:pitfall:<slug>" status active
asobi truth "[project]:pitfall:<slug>" title "<short warning>"
asobi obs "[project]:pitfall:<slug>" "tried: <approach attempted>"
asobi obs "[project]:pitfall:<slug>" "why-it-failed: <root cause, symptom, or evidence>"
asobi obs "[project]:pitfall:<slug>" "do-instead: <known better path, or 'open'>"
asobi obs "[project]:pitfall:<slug>" "date: YYYY-MM-DD"
```

Use `status active` while the warning should be surfaced. When the dead end is resolved or obsolete, update the truth:

```bash
asobi truth "[project]:pitfall:<slug>" status resolved
asobi obs "[project]:pitfall:<slug>" "resolved YYYY-MM-DD: <why it no longer applies>"
```

Slug rules:
- Lowercase words
- Use `-` inside the slug
- Keep the hierarchy separator as `:`
- Example: `harus-skills:pitfall:bump-tool-overreach`

## Fallback Files

If asobi is unavailable, use repo-tracked Markdown fallback files. This fallback belongs to `/revise` only; it does not change the `/asobi` skill requirement that asobi is mandatory for session continuity.

Create files only as needed:

- `docs/lessons/pitfalls.md`
- `docs/lessons/learnings.md`

Add this header when creating either file:

```markdown
# Lessons

Project-local fallback lessons captured when asobi was unavailable. Migrate into asobi when possible.
```

For pitfalls, append:

```markdown
## YYYY-MM-DD - <slug>

Status: active

Tried: <approach attempted>

Why it failed: <root cause, symptom, or evidence>

Do instead: <known better path, or open>
```

For work-experiences and findings, append:

```markdown
## YYYY-MM-DD - <short title>

Type: <work-experience|finding>

Lesson: <short actionable lesson>
```

## Recall Contract

Persistence is only useful if future sessions surface the lesson:

- `/asobi start` must report active pitfalls for the project.
- `/asobi tasks dispatch` must query task-relevant lessons before briefing a sub-agent.
- A pitfall linked with `task --depends_on--> pitfall` must be included in the dispatch context when that task is shown.

When recording a pitfall, prefer titles that work as warnings in a dispatch brief.

## Confirmation

End with one terse line:

```text
Revision saved: <classification> -> <destination>.
```

If only fallback files were used:

```text
Revision saved: <classification> -> docs/lessons/<file>.md because asobi was unavailable.
```
