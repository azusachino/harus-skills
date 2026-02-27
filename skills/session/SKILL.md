---
name: session
description: Use when starting or ending a work session, when a project has a .agents/ directory at the start of a conversation, or when user says "start session", "let's continue", "wrap up", or "end session" — restores prior context and saves session state
metadata:
  author: haru
  version: 1.1.0
---

# Session Skill

Manage the three-tier memory system (Global, Project, Session) to ensure continuity across agents and sessions.

## Auto-Trigger (invoke without being asked)

Run `/session start` automatically when **any** of these are true at the start of a conversation:

- A `.agents/` directory exists in the project root
- The user says "start session", "let's continue", "resume", "pick up where we left off"

Run `/session end` automatically when:

- The user says "wrap up", "end session", "save context", "stop here", "I'm done for now"
- You are closing a conversation where `.agents/` exists and work was done

## Commands

### `/session start`

1. **Global Tier** *(optional — skip silently if `~/.agents/` does not exist or access is denied)*:
   - Try `save_memory` tool (if available) to read global facts.
   - Try reading `~/.agents/preferences/` and `~/.agents/facts/` for user-wide preferences.
   - If access fails for any reason, skip this step entirely without error.
2. **Project Tier**:
   - Read `AGENTS.md` for high-level project briefing.
   - Read `.agents/CONTEXT.md` for internal agent rules and context.
3. **Session Tier**:
   - Read `.agents/CURRENT_TASK.md` to see where the last session left off.
   - Read `.agents/MEMORY.md` to understand recent decisions.
4. **Report**: Summarize briefly — "Session resumed. Last task: [X]. Next step: [Y]." Add any relevant global preference notes if loaded.

### `/session end`

1. **Update Session State**:
   - Overwrite `.agents/CURRENT_TASK.md` with current status, completed steps, and next actions.
   - Append new decisions or discoveries to `.agents/MEMORY.md`.
2. **Sync Global Memory** *(optional — skip silently if inaccessible)*:
   - If new personal facts or cross-project preferences were learned, try `save_memory` or update `~/.agents/preferences/` / `~/.agents/facts/` if accessible.
   - If `~/.agents/` is not accessible, skip. Project-level memory is sufficient.
3. **Confirm**: Tell the user the session is saved with a 1-sentence handoff summary.

## Memory Backend Support

Different agents support different persistence mechanisms. Use whatever is available — the protocol works at any level.

| Backend | Available in | Used for |
| --- | --- | --- |
| `save_memory` tool | Claude Code | Global facts auto-loaded every session without any explicit read |
| `~/.agents/` filesystem | Any agent with home dir access | Global facts for non-Claude-Code agents |
| `.agents/` project dir | Any agent | Project + session memory — always available, universal source of truth |

**Claude Code note:** `save_memory` writes to a memory file that is automatically injected into context at the start of every conversation. Facts stored here cost zero tokens at read time — the agent just "knows" them. Use it as the primary global tier whenever available.

**`~/.agents/` filesystem structure** *(optional fallback for non-Claude-Code agents)*:

```text
~/.agents/
├── preferences/
│   ├── code-style.md    ← naming, linting, indentation
│   └── tools.md         ← preferred CLI tools and shell settings
├── facts/
│   ├── identity.md      ← user name, role, background
│   └── habits.md        ← preferred working hours, communication style
└── projects/
    └── registry.md      ← global list of managed projects and their status
```

## Memory Writing Protocol

At session end, write in this order — skip any step that fails or is unavailable, no errors:

1. **`save_memory` tool** *(if available)*: store user preferences, cross-project habits, and facts that should be present in every future session without explicit file reads. E.g. "User prefers British English", "Always use `mise run` for tasks in this repo".
2. **`.agents/MEMORY.md`** *(always)*: append project-scoped decisions and discoveries. Universal — any agent can read this.
3. **`~/.agents/preferences/` or `~/.agents/facts/`** *(if accessible)*: mirror the same global facts written to `save_memory` so non-Claude-Code agents can load them from the filesystem.

### What to write

Write an entry when you learn something that would change how you'd behave in a future session:

- **Decisions with rationale** — "Chose X over Y because Z." Future agents won't re-litigate.
- **User preferences discovered** — coding style, communication style, tool preferences.
- **Non-obvious codebase patterns** — "This project skips error wrapping in handlers by convention."
- **Things that went wrong** — "Running `mise fmt` on `.md` files breaks prose — skip it."

### What NOT to write

- Active task state → use `CURRENT_TASK.md` instead
- Content already in `AGENTS.md` or `CONTEXT.md` → avoid duplication
- Large code blocks or file contents → read source files on demand
- Ephemeral observations → "currently editing src/foo.ts" is useless next session

### Entry format

```markdown
## YYYY-MM-DD — [topic]
**Fact/Decision:** [one sentence]
**Why it matters:** [one sentence — what changes if ignored]
```

Before appending, scan recent entries. If a similar fact exists, **update it in place** rather than creating a duplicate.

## Core Principles

- **Agent-Led**: Don't wait for the user to ask. Detect `.agents/` at session start and run `/session start` automatically.
- **Filesystem as Truth**: `.agents/` Markdown files are the universal source of truth any agent can read.
- **Graceful Degradation**: Global tier (`~/.agents/`) is best-effort. If it fails for any reason, continue with project + session tiers.
- **Minimal Noise**: Start/end summaries should be concise — focus on intent and continuity.

## Memory Tier Reference

| Tier | Location | Required? | Purpose |
| --- | --- | --- | --- |
| **Global** | `~/.agents/{preferences,facts}/` | Optional | Cross-project facts, name, habits, tool preferences |
| **Project** | `AGENTS.md` + `.agents/CONTEXT.md` | Yes | Architecture, tech stack, hard rules, conventions |
| **Session** | `.agents/CURRENT_TASK.md` + `MEMORY.md` | Yes | Active feature state, recent decisions, handoff data |
