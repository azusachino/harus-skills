---
name: session
description: Use when starting or ending a work session, when a project has a .agents/ directory at the start of a conversation, or when user says "start session", "let's continue", "wrap up", or "end session" — restores prior context and saves session state
metadata:
  author: haru
  version: 1.2.0
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

1. **Global Tier** *(optional — skip silently at any failure)*:
   - Check if `search_nodes`, `create_entities`, and `add_observations` are all in the available tool list (indicates MCP `@modelcontextprotocol/server-memory` is active). If any are missing, skip MCP and proceed to the next fallback. (Check tool availability once at the start of `/session start`. Use MCP for all global tier operations in this session. If any MCP call fails at runtime, fall back silently to `save_memory` without retrying MCP.)
   - If MCP available: call `read_graph()`, then filter and load:
     - All category entities: `UserPreferences`, `CodingStyle`, `ToolPreferences`, `Standard`
     - Project entity matching the current project name (basename of cwd)
   - If MCP not available: try `save_memory` tool.
   - If `save_memory` not available: try reading `~/.agents/preferences/` and `~/.agents/facts/`.
   - If all fail: skip silently without error.
2. **Project Tier**:
   - Read `AGENTS.md` for high-level project briefing.
   - Read `.agents/CONTEXT.md` for internal agent rules and context.
   - If any file does not exist, skip it silently and continue.
3. **Session Tier**:
   - Read `.agents/CURRENT_TASK.md` to see where the last session left off.
   - Read `.agents/MEMORY.md` to understand recent decisions.
4. **Report**: Summarize briefly — "Session resumed. Last task: [X]. Next step: [Y]." Add any relevant global preference notes if loaded.

### `/session end`

1. **Update Session State**:
   - Overwrite `.agents/CURRENT_TASK.md` with current status, completed steps, and next actions.
   - Append new decisions or discoveries to `.agents/MEMORY.md`.
2. **Sync Global Memory** *(optional — first success wins, skip silently on all failures)*:
   - If MCP available (`search_nodes` in tools):
     - For each new cross-project fact or preference learned this session:
       - Call `search_nodes` with the target entity name to check if it exists.
       - If exists: call `add_observations` with new facts only (avoid duplicates).
       - If not exists: call `create_entities` then `add_observations`.
     - Use category entities (`UserPreferences`, `CodingStyle`, `ToolPreferences`, `Standard`) for user-wide facts.
     - Use a project entity named after the current repo (cwd basename) for project-scoped facts.
   - Else if `save_memory` available: write cross-project facts.
   - Else if `~/.agents/` accessible: write to `preferences/` or `facts/` markdown files.
3. **Confirm**: Tell the user the session is saved with a 1-sentence handoff summary.

## Memory Backend Support

Different agents support different persistence mechanisms. Use whatever is available — the protocol works at any level.

| Backend | Available in | Used for |
| --- | --- | --- |
| MCP `server-memory` | Any agent with MCP configured | Primary global tier — knowledge graph, cross-project and category facts |
| `save_memory` tool | Claude Code | Fallback — auto-loaded facts, zero read-time cost |
| `~/.agents/` filesystem | Any agent with home dir access | Last resort — markdown files for non-MCP agents |
| `.agents/` project dir | Any agent | Project + session memory — always available |

**MCP note:** When `@modelcontextprotocol/server-memory` is configured, use it as the primary global tier. It provides a knowledge graph for cross-project facts, user preferences, and category entities without filesystem I/O. Check for `search_nodes` in the available tool list to detect MCP availability.

## MCP Knowledge Graph Entity Conventions

When MCP `@modelcontextprotocol/server-memory` is the active global tier, use these entity naming conventions:

### Category entities (cross-project user facts)

| Entity name | Purpose |
| --- | --- |
| `UserPreferences` | Language, communication style, formatting preferences |
| `CodingStyle` | Naming conventions, error handling, commit style |
| `ToolPreferences` | Preferred CLIs, shells, task runners |
| `Standard` | Cross-project system requirements, global configurations, tool exclusions |

### Project entities (repo-scoped facts)

Named after the repository (e.g., `harus-skills`). Use the basename of the current working directory, lowercased, with spaces and special characters replaced by hyphens (e.g., `harus-skills`, `my-project`). Observations describe project-specific conventions:

- "Uses mise for all tasks"
- "Never run prettier on .md files — use markdownlint-cli2 only"

Both category and project entities are supported and used together.

### Deduplication rule

Before adding any observation, call `search_nodes` with the entity name to retrieve its current observations. Compare the new fact against existing observations — only add if the concept is not already captured (exact wording need not match). When uncertain, prefer updating an existing observation over creating a duplicate.

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
| **Global — MCP** | `@modelcontextprotocol/server-memory` | Optional | Primary: cross-project facts, user preferences, knowledge graph |
| **Global — Claude Code** | `save_memory` tool | Optional | Fallback: auto-loaded facts, zero read-time cost |
| **Global — Filesystem** | `~/.agents/` | Optional | Last resort: markdown files for non-MCP agents |
| **Project** | `AGENTS.md` + `.agents/CONTEXT.md` | Yes | Architecture, tech stack, hard rules, conventions |
| **Session** | `.agents/CURRENT_TASK.md` + `MEMORY.md` | Yes | Active feature state, recent decisions, handoff data |
