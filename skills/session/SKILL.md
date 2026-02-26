---
name: session
description: Manage agent session context, project memory, and global tier memory
metadata:
  author: haru
  version: 1.0.0
  aliases: ["s"]
---

# Session Skill

Manage the three-tier memory system (Global, Project, Session) to ensure continuity across different agents and sessions.

## Commands

### `/session start` (or `s start`)

Execute the Session Start Protocol:

1. **Global Tier**:
   - Use `save_memory` (if available) to read global facts.
   - Read from the structured global directory `~/.agents/`:
     - `~/.agents/preferences/` (Style, formatting, tool preferences)
     - `~/.agents/facts/` (Personal identity, name, role)
     - `~/.agents/projects/` (Cross-project status or global tracking)
2. **Project Tier**:
   - Read `AGENTS.md` for high-level project briefing.
   - Read `.agents/CONTEXT.md` for internal agent rules and non-public context.
3. **Session Tier**:
   - Read `.agents/CURRENT_TASK.md` to see where the last session left off.
   - Read `.agents/MEMORY.md` to understand recent decisions.
4. **Action**: Briefly summarize the state to the user: "Session resumed. Last task: [X]. Next step: [Y]. I'm also aware of [Z] from global memory."

### `/session end` (or `s end`)

Execute the Session End Protocol:

1. **Update Session State**:
   - Overwrite `.agents/CURRENT_TASK.md` with the latest status, completed steps, and next actions.
   - Append new decisions or discoveries to `.agents/MEMORY.md`.
2. **Sync Global Memory**:
   - If new personal facts or cross-project preferences were learned:
     - Use `save_memory` to update Gemini's global context.
     - Update relevant files in `~/.agents/preferences/` or `~/.agents/facts/`.
3. **Action**: Confirm to the user that the session is saved and provide a 1-sentence "handoff summary".

## Global Memory Structure (`~/.agents/`)

To keep global memory readable, use a sub-folder mechanism:

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

## Core Principles

- **Agent-Led**: Don't wait for the user to ask. If you detect a `.agents/` directory at the start of a session, suggest or automatically run `/session start`.
- **Filesystem as Truth**: While specialized tools like `save_memory` are great, always maintain the Markdown files in `.agents/` as the universal source of truth that any agent can read.
- **Minimal Noise**: Keep the start/end summaries concise. Focus on *intent* and *continuity*.

## Memory Tier Reference

| Tier | Location | Persistence | Purpose |
| --- | --- | --- | --- |
| **Global** | `~/.agents/{preferences,facts}/` | Forever | Cross-project facts, name, habits, tool preferences |
| **Project** | `AGENTS.md` + `.agents/CONTEXT.md` | Life of Project | Architecture, tech stack, hard rules, conventions |
| **Session** | `.agents/CURRENT_TASK.md` + `MEMORY.md` | Task Duration | Active feature state, recent decisions, handoff data |
