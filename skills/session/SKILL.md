---
name: session
description: Use when starting or ending a work session, when a project has a .agents/ directory at the start of a conversation, or when user says "start session", "let's continue", "wrap up", or "end session" — restores prior context and saves session state
metadata:
  author: haru
  version: 1.4.0
---

# Session Skill

Manage the memory system (Global via MCP, Project via local docs) to ensure continuity across agents and sessions.

**Core principle**: When MCP `@modelcontextprotocol/server-memory` is available, it is the canonical source of truth for all session state. `.agents/CURRENT_TASK.md` is skipped entirely — it exists only for agents without MCP access.

## Auto-Trigger (invoke without being asked)

Run `/session start` automatically when **any** of these are true at the start of a conversation:

- A `.agents/` directory exists in the project root
- The user says "start session", "let's continue", "resume", "pick up where we left off"

Run `/session end` automatically when:

- The user says "wrap up", "end session", "save context", "stop here", "I'm done for now"
- You are closing a conversation where `.agents/` exists and work was done

## Commands

### `/session start`

1. **Detect MCP availability**: Check if `search_nodes`, `create_entities`, and `add_observations` are all in the available tool list. Record result — use consistently throughout this session.
2. **If MCP available** (primary path):
   - Call `read_graph()`, then load:
     - Category entities: `UserPreferences`, `CodingStyle`, `ToolPreferences`, `Standard`
     - Project entity matching the current repo name (cwd basename, lowercased, hyphens)
     - Session entity `[project-name]:session` — holds the last saved task state
   - **Skip `.agents/CURRENT_TASK.md` entirely** — MCP is the session source of truth.
3. **If MCP not available** (fallback path):
   - Try `save_memory` tool for global preferences; skip silently on failure.
   - Read `.agents/CURRENT_TASK.md` to resume the last task state.
   - Read `.agents/MEMORY.md` for recent decisions.
4. **Always load project context** (independent of MCP):
   - Read `AGENTS.md` — project briefing, tech stack, commands.
   - Read `.agents/CONTEXT.md` — living doc of internal rules, patterns, and architecture notes. This is updated whenever core features change and is always authoritative.
   - Skip silently if either file does not exist.
5. **Report**: "Session resumed. Last task: [X]. Next step: [Y]." Include relevant preferences loaded from MCP or global memory.

### `/session end`

1. **If MCP available** (primary path — no local file writes for session state):
   - Determine session entity: `[project-name]:session`.
   - `search_nodes("[project-name]:session")` — check if it exists.
   - If exists: `delete_entities(["[project-name]:session"])` to clear stale state.
   - `create_entities` + `add_observations` with fresh session state:
     - `objective: [current goal]`
     - `status: IN_PROGRESS | BLOCKED | REVIEW | DONE`
     - `completed: [comma-separated completed steps]`
     - `remaining: [comma-separated remaining steps]`
     - `next: [single concrete next action]`
     - `last-updated: YYYY-MM-DD`
   - For new cross-project facts: `search_nodes` → deduplicate → `add_observations` on category entities.
   - For project-scoped decisions: `add_observations` on the project entity.
   - **Do not write `.agents/CURRENT_TASK.md`** — writing it when MCP is available only creates git noise.
2. **If MCP not available** (fallback path):
   - Overwrite `.agents/CURRENT_TASK.md` with current task state (see format below).
   - Append new decisions to `.agents/MEMORY.md`.
   - If `save_memory` available: write cross-project preferences.
3. **Update `.agents/CONTEXT.md`** if anything changed about the project's core behavior, architecture, or non-obvious conventions. This file is shared with all future sessions regardless of memory backend.
4. **Confirm**: "Session saved. Next: [one-sentence handoff summary]."

## MCP Entity Conventions

### Session entities (volatile — task state per project)

| Entity name | Purpose |
| --- | --- |
| `[project-name]:session` | Current task state — deleted and recreated each session end |

### Category entities (cross-project user facts)

| Entity name | Purpose |
| --- | --- |
| `UserPreferences` | Language, communication style, formatting preferences |
| `CodingStyle` | Naming conventions, error handling, commit style |
| `ToolPreferences` | Preferred CLIs, shells, task runners |
| `Standard` | Cross-project system requirements, global configurations, tool exclusions |

### Project entities (repo-scoped stable facts)

Named after the repository (cwd basename, lowercased, hyphens). Observations describe stable project conventions that don't change session-to-session:

- "Uses nix devShell for all tool provisioning"
- "Never run prettier on .md files — use markdownlint-cli2 only"

**Deduplication rule**: before adding any observation, `search_nodes` the entity name, compare against existing observations, only add if not already captured.

## Local Files Reference

### `.agents/CONTEXT.md` — living project context (always loaded, update when needed)

Holds internal agent-specific rules, architecture notes, and non-obvious patterns. Updated whenever core features or project conventions change. Every session reads this.

### `.agents/CURRENT_TASK.md` — fallback task state (only when MCP unavailable)

```markdown
## Objective
[what we are trying to achieve]

## Status
IN_PROGRESS | BLOCKED | REVIEW | DONE

## Completed Steps
- [x] Step

## Remaining Steps
- [ ] Step

## Open Questions / Blockers
- [question or blocker]

## Next Action
[single concrete next step]

## Last Updated
YYYY-MM-DD
```

### `.agents/MEMORY.md` — fallback decision log (only when MCP unavailable)

```markdown
## YYYY-MM-DD — [topic]
**Fact/Decision:** [one sentence]
**Why it matters:** [one sentence — what changes if ignored]
```

Update in place if a similar fact exists; do not create duplicates.

## Memory Tier Reference

| Tier | Location | When used | Purpose |
| --- | --- | --- | --- |
| **MCP session** | `[project]:session` entity | MCP available | Canonical task state — no file I/O |
| **MCP global** | Category + project entities | MCP available | User prefs, cross-project facts, project conventions |
| **Claude Code** | `save_memory` tool | MCP fallback | Auto-loaded preferences |
| **Project context** | `AGENTS.md` + `.agents/CONTEXT.md` | Always | Architecture, conventions — living docs |
| **Local fallback** | `.agents/CURRENT_TASK.md` + `MEMORY.md` | MCP unavailable only | Task state and decisions for non-MCP agents |

## Core Principles

- **MCP as Truth**: When MCP is available, session state lives in MCP exclusively. `CURRENT_TASK.md` is not read or written.
- **CONTEXT.md is living**: Update it whenever project behavior, architecture, or key conventions change. It is always authoritative regardless of memory backend.
- **Agent-Led**: Detect `.agents/` at session start and run `/session start` automatically.
- **Graceful Degradation**: Fall back to local files silently if MCP is not configured.
- **Minimal Noise**: Start/end summaries concise — focus on intent and continuity.
