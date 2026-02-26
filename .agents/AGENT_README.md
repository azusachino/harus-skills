# Agent Memory & Session Management Protocol

> This file defines how you (the Agent) manage memory, context, and session handoffs for this project.
> **Read this file once at the start of every session. Then read `CURRENT_TASK.md` to resume work.**

---

## Directory Structure

```text
project/
├── .agents/
│   ├── AGENT_README.md      ← you are here (protocol rules)
│   ├── CONTEXT.md           ← stable project knowledge (tech stack, conventions, architecture)
│   ├── MEMORY.md            ← append-only decisions log
│   ├── CURRENT_TASK.md      ← active task state / session save point
│   └── SESSION_LOG/
│       └── YYYY-MM-DD.md    ← per-session activity log (optional, for audit trail)
```

---

## Session Start Protocol

When a new session begins, you **must**:

1. Read `.agents/AGENT_README.md` (this file) — understand the rules
2. **If available, use `/session start`** — this will:
   - Check **Global Memory** via `save_memory` and `~/.agents/GLOBAL_MEMORY.md` — load user preferences and global facts
   - Read `AGENTS.md` and `.agents/CONTEXT.md` — load stable project knowledge
   - Read `.agents/CURRENT_TASK.md` — reconstruct where we left off
3. If `/session` is not available, perform these reads manually and confirm state.
4. Briefly confirm to the user: current task, last completed step, next action

**Do not read the entire codebase upfront.** Read specific files on demand, only when needed for the current task.

---

## Session End Protocol

When a session ends (user says "wrap up", "end session", "stop here", or similar), you **must**:

1. **If available, use `/session end`** — this will:
   - **Update `CURRENT_TASK.md`** — overwrite with current state (see format below)
   - **Append to `MEMORY.md`** — log any decisions or discoveries made this session
   - **Optionally write `SESSION_LOG/YYYY-MM-DD.md`** — brief activity summary
   - **Sync Global Memory** — if any personal facts or user-wide preferences were learned, save them using `save_memory` AND `~/.agents/GLOBAL_MEMORY.md`.
2. If `/session` is not available, perform these updates manually and confirm done.
3. Confirm to the user that the session is saved and provide a 1-sentence "handoff summary".

Do not end a session without completing these steps. If the user tries to stop abruptly, remind them: *"Should I update CURRENT_TASK.md before we close?"*

---

## Global Memory vs. Project Memory

To ensure multiple agents can work together across different sessions and projects:

- **Project Memory (`.agents/`)**: Store everything specific to THIS project (tech stack, architectural decisions, task state). This is the "source of truth" for the project's current state.
- **Global Memory (via `save_memory`)**: Store high-level user preferences, personal facts, and cross-project habits. This allows "fresh" agents in new sessions to immediately know your preferred working style and identity.

**Always prefer local project memory for technical context to ensure accessibility for any agent (Claude, Gemini, etc.) that has access to the codebase.**

---

## File Formats

### `CONTEXT.md` — Stable Project Knowledge

*Written by human. Updated rarely. Agent reads, rarely writes.*

```markdown
## Project Overview
[what this project does, in 2-3 sentences]

## Tech Stack
[languages, frameworks, runtimes, key libraries]

## Architecture
[high-level structure, key patterns used]

## Conventions & Standards
[naming conventions, file structure rules, code style]

## Hard Rules (DO / DON'T)
- DO: ...
- DON'T: ...

## Key Files & Entry Points
[most important files the agent should know about]
```

---

### `CURRENT_TASK.md` — Session Save Point

*Agent overwrites this at end of every session.*

```markdown
## Objective
[what we are trying to achieve in the current task/feature/bugfix]

## Status
IN_PROGRESS | BLOCKED | REVIEW | DONE

## Completed Steps
- [x] Step one
- [x] Step two

## Remaining Steps
- [ ] Step three
- [ ] Step four

## Open Questions / Blockers
- [question or blocker, and who needs to resolve it]

## Files Modified This Session
- path/to/file.go — [what changed and why]

## Next Action
[single, concrete next thing to do when resuming]

## Last Updated
YYYY-MM-DD HH:MM
```

---

### `MEMORY.md` — Decisions Log

*Agent appends to this. Never rewrites existing entries.*

```markdown
## YYYY-MM-DD — [short title]
**Decision:** [what was decided]
**Reason:** [why]
**Alternatives rejected:** [what else was considered and why it lost]

---
```

---

## Token Budget Rules

| File | When to read | Expected size |
| --- | --- | --- |
| `AGENT_README.md` | Once per session start | < 100 lines |
| `CONTEXT.md` | Once per session start | < 200 lines |
| `CURRENT_TASK.md` | Once per session start | < 80 lines |
| `MEMORY.md` | On demand (when making related decisions) | grows over time |
| Source files | On demand, only when needed | varies |

**Target cold-start token cost: under 1,000 tokens.**
If `CONTEXT.md` or `CURRENT_TASK.md` exceed their size targets, summarize and compress them.

---

## What Agent Should and Should Not Remember

**Agent IS responsible for:**

- Keeping `CURRENT_TASK.md` accurate and up to date
- Logging decisions to `MEMORY.md` (even small ones)
- Telling the user when context is missing or ambiguous

**Agent is NOT responsible for:**

- Memorizing code contents (read files on demand instead)
- Rewriting `CONTEXT.md` without user approval
- Making architectural decisions without logging them to `MEMORY.md`

---

## User Commands

| User says | Agent does |
| --- | --- |
| `"start session"` / `"let's continue"` | Read README + CONTEXT + CURRENT_TASK, confirm state |
| `"wrap up"` / `"end session"` | Update CURRENT_TASK + append MEMORY + confirm done |
| `"what's the context?"` | Summarize CONTEXT.md + CURRENT_TASK.md in plain language |
| `"log this decision: ..."` | Append to MEMORY.md immediately |
| `"reset task"` | Clear CURRENT_TASK.md, ask user for new objective |

---

## First-Time Setup Checklist

If `.agents/` does not exist yet, create it and prompt the user to fill in:

- [ ] `CONTEXT.md` — project overview, tech stack, conventions
- [ ] `CURRENT_TASK.md` — first task objective
- [ ] `MEMORY.md` — empty file with header `# Decision Log`

Then confirm setup is complete before proceeding with any task.

---

*Protocol version: 1.0 — update this file if the workflow changes.*
