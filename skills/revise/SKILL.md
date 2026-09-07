---
name: revise
description: Persist project lessons, findings, and wrong approaches so future sessions can recall them
metadata:
  author: haru
  version: 1.1.0
user-invokable: true
disable-auto-invoke: true
---

# Revise

Persist durable lessons from the current work into the asobi graph. `/asobi end` records *where we are* (session status); `/revise` records *what should change future behavior*.

## When to use

After a meaningful discovery — a workflow worth repeating, a non-obvious project fact, or (most importantly) a dead end an agent should not re-walk. Capture while context is fresh. Not for ordinary task status; that is `/asobi end`.

## Classify

Read the user's free-form text and classify it yourself; ask only if it is too vague to preserve. Keep each lesson short and actionable — "do X because Y", not a transcript.

| Class | Means | Destination |
| --- | --- | --- |
| `work-experience` | how work was actually done | `[project]` observation |
| `finding` | a non-obvious fact or gotcha (an architectural *choice* → a decision entity, see `/asobi recall`) | `[project]` observation |
| `wrong-approach` | something tried and rejected | `[project]:pitfall:<slug>` entity |

## Flow

1. Detect asobi: `command -v asobi`. If absent, use the fallback files below.
2. Derive `[project]` from the owning repository and confirm graph scope using the Asobi skill's discovery rules. Ancestor configuration can select a parent workspace graph. Use the intended graph; do not initialize or migrate state as a side effect of lesson capture.
3. Dedup first: `asobi search "<topic>" --limit 10`. Inspect matching entities. Append `seen-again YYYY-MM-DD: <evidence>` only for genuinely new evidence; skip an unchanged repeat. If the lesson contradicts an old one, record the correction and resolve the obsolete pitfall rather than reinforcing it.
4. Write — ensure the project entity exists (`asobi new "[project]" "project"`), then:
   ```bash
   asobi obs "[project]" "experience YYYY-MM-DD: <lesson>"   # work-experience
   asobi obs "[project]" "finding YYYY-MM-DD: <lesson>"      # finding
   ```
   For a wrong-approach, write the pitfall entity below.
5. Confirm in one line.

## Pitfall entity

A pitfall warns future agents away from a rejected path — it is not an ADR (ADRs explain *chosen* paths). One entity per dead end; `status` and `title` are truths so `/asobi start` can surface active pitfalls cheaply.

```bash
asobi new "[project]:pitfall:<slug>" "concept"
asobi truth "[project]:pitfall:<slug>" status active        # active | resolved
asobi truth "[project]:pitfall:<slug>" title "<short warning>"
asobi obs "[project]:pitfall:<slug>" "tried: <approach attempted>"
asobi obs "[project]:pitfall:<slug>" "why-it-failed: <root cause / symptom>"
asobi obs "[project]:pitfall:<slug>" "do-instead: <better path, or 'open'>"
asobi obs "[project]:pitfall:<slug>" "date: YYYY-MM-DD"
```

When the dead end is obsolete: upsert `status resolved` and append `obs "resolved YYYY-MM-DD: <why it no longer applies>"`. If it belongs to an active task, link it with `asobi link "[project]:[epic]:task-N" "[project]:pitfall:<slug>" "depends_on"`. The agent must read those relations and the relevant lesson before dispatch; claiming a task does not load the warning automatically. Slugs are lowercase, `-` inside a segment and `:` only between levels — e.g. `harus-skills:pitfall:bump-tool-overreach`.

## Recall

Revise captures lessons; the Asobi skill handles session recall and the agent's pre-dispatch lesson search. Prefer pitfall titles that state a concrete warning. Preserve evidence and its limits: an observed failure is not proof of a root cause, and one task's workaround is not a universal policy.

## Fallback (asobi unavailable)

A lesson-capture fallback; it does not provide graph-backed session continuity. Use the repository's existing lesson or pitfall convention first. If none exists, append to these repo-tracked files with the header `> Project-local fallback lessons captured when asobi was unavailable. Migrate into asobi when possible.`

- `docs/lessons/pitfalls.md` — `## YYYY-MM-DD — <slug>`, then Status / Tried / Why it failed / Do instead
- `docs/lessons/learnings.md` — `## YYYY-MM-DD — <title>`, then Type (`work-experience`|`finding`) / Lesson

## Confirmation

After a write, confirm its destination. For an unchanged repeat, say `No revision needed: existing lesson already covers this evidence.` Do not claim a save when nothing was written.

```text
Revision saved: <class> -> <destination>.            # or: -> docs/lessons/<file>.md (asobi unavailable)
```
