# Design: MCP Memory Integration for `session` and `init-project` Skills

**Date:** 2026-03-01
**Status:** Approved

## Overview

Integrate `@modelcontextprotocol/server-memory` as the primary global memory tier in the `session` and `init-project` skills. This resolves the unreliable `~/.agents/` filesystem access issue by replacing it with an MCP-managed knowledge graph that is always available when the server is configured.

## Problem

The current global memory tier relies on `~/.agents/` filesystem access, which frequently fails due to permission issues in sandboxed or restricted environments. `save_memory` (Claude Code native) works but is Claude Code-only. Neither provides cross-project structured memory for non-Claude agents.

## Approach: Additive (Approach A)

MCP memory becomes the primary global tier when available. The existing tiers remain intact as fallbacks. Both project-tier markdown files (`.agents/MEMORY.md`, `CURRENT_TASK.md`) and session behavior are preserved — only the global tier resolution order changes.

## Memory Tier Table

| Priority | Backend | Required? | Detection |
| --- | --- | --- | --- |
| 1 | MCP `@modelcontextprotocol/server-memory` | Optional | `search_nodes` in available tools |
| 2 | `save_memory` tool | Optional | tool availability |
| 3 | `~/.agents/` filesystem | Optional | filesystem access |
| 4 | `.agents/` project dir | Yes | always present |

## MCP Knowledge Graph Entity Conventions

Two entity families are supported:

### Category entities (cross-project user facts)

| Entity name | Purpose |
| --- | --- |
| `UserPreferences` | Language, communication style, formatting preferences |
| `CodingStyle` | Naming conventions, error handling, commit style |
| `ToolPreferences` | Preferred CLIs, shells, task runners |

### Project entities (repo-scoped facts)

Named after the project (e.g., `harus-skills`). Each entity holds observations scoped to that project:

- "Uses mise for all tasks"
- "Never run prettier on .md files — use markdownlint-cli2 only"
- "Conventional commits, no emoji in commit messages"

Relations between project and category entities are optional (e.g., `harus-skills` → `has_convention` → `CodingStyle`).

## `session` Skill Changes

### `session start` — updated flow

```text
1. Detect MCP: is `search_nodes` in available tools?
   YES → call read_graph()
         filter: all category entities + project entity matching cwd name
         load observations into context
   NO  → try save_memory
         → try ~/.agents/preferences/ and ~/.agents/facts/
         → skip silently if inaccessible
2. Project tier (unchanged): read AGENTS.md + .agents/CONTEXT.md
3. Session tier (unchanged): read CURRENT_TASK.md + MEMORY.md
4. Report: "Session resumed. Last task: [X]. Next: [Y]."
```

### `session end` — updated flow

```text
1. Session tier (always):
   - Overwrite .agents/CURRENT_TASK.md
   - Append new entries to .agents/MEMORY.md
2. Global tier (first success wins):
   a. MCP available → create_entities / add_observations for new facts
   b. save_memory available → write cross-project facts
   c. ~/.agents/ accessible → write markdown files
```

### Memory Writing — MCP conventions

When writing to MCP at session end:

- Check if the target entity already exists (`search_nodes` by name)
- If exists: `add_observations` with new facts only (avoid duplicates)
- If not exists: `create_entities` then `add_observations`
- Use the project name (from `cwd` basename) as the project entity name

### Updated Memory Tier Reference table (in SKILL.md)

| Backend | Available in | Used for |
| --- | --- | --- |
| MCP `server-memory` | Any agent with MCP configured | Primary global tier — knowledge graph, cross-project facts |
| `save_memory` tool | Claude Code | Fallback — auto-loaded facts, zero read-time cost |
| `~/.agents/` filesystem | Any agent with home dir access | Last resort — markdown files for non-MCP agents |
| `.agents/` project dir | Any agent | Always — project + session memory |

## `init-project` Skill Changes

### Phase 2: Report & Ask — new MCP check

After scanning existing tooling, add:

1. Check if `search_nodes` is in available tools (MCP memory already active)
2. If not detected, prompt: "No MCP memory server detected. Want me to add `@modelcontextprotocol/server-memory` to your Claude config for persistent global memory across projects?"
3. If user accepts: write the MCP server entry to `.claude/settings.json` under `mcpServers`
4. Regardless of choice: document entity conventions in generated `AGENT_README.md`

### MCP server config written to `.claude/settings.json`

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

If `.claude/settings.json` already exists, merge the `mcpServers` key — do not overwrite the file.

### Updated `AGENT_README.md` template

Add a **Global Memory** section documenting:

- MCP as primary global tier
- Entity naming conventions (category + project)
- Fallback chain
- New user command: `"log this globally: [fact]"` → agent writes to MCP entity

### Updated `CONTEXT.md` template

Add to Agent Rules:

```markdown
- DO: Check MCP memory tools at session start. If `search_nodes` is available, use read_graph() to load global facts.
- DO: At session end, persist new cross-project facts to MCP via create_entities / add_observations.
- DO: Use category entities (UserPreferences, CodingStyle, ToolPreferences) and project entities (named after repo) in MCP.
```

## Files to Modify

| File | Change |
| --- | --- |
| `skills/session/SKILL.md` | Update global tier detection order, add MCP read/write protocol, update backend table |
| `skills/init-project/SKILL.md` | Add MCP detection check in Phase 2, add config write step, update templates |

## Out of Scope

- Deleting or migrating existing `~/.agents/` data
- Adding MCP memory to any skill other than `session` and `init-project`
- Relations between entities (optional, not required for v1)
