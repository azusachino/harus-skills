# MCP Memory Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Integrate `@modelcontextprotocol/server-memory` as the primary global memory tier in the `session` and `init-project` skills, with graceful fallback to `save_memory` and `~/.agents/`.

**Architecture:** Additive approach — MCP memory is detected at runtime via tool list check (`search_nodes` in available tools), used when present, fallen back from when absent. Both skills are updated to document and implement the new tier order. Project-tier markdown files remain unchanged.

**Tech Stack:** SKILL.md (markdown), `@modelcontextprotocol/server-memory` MCP tools (`read_graph`, `create_entities`, `add_observations`, `search_nodes`), `.claude/settings.json` for MCP config.

**Design doc:** `docs/plans/2026-03-01-mcp-memory-refactor-design.md`

---

## Task 1: Update `session` skill — global tier detection and read protocol

**Files:**

- Modify: `skills/session/SKILL.md`

### Step 1: Update the Memory Backend Support table

Replace the existing backend table with the new four-tier table:

```markdown
| Backend | Available in | Used for |
| --- | --- | --- |
| MCP `server-memory` | Any agent with MCP configured | Primary global tier — knowledge graph, cross-project and category facts |
| `save_memory` tool | Claude Code | Fallback — auto-loaded facts, zero read-time cost |
| `~/.agents/` filesystem | Any agent with home dir access | Last resort — markdown files for non-MCP agents |
| `.agents/` project dir | Any agent | Project + session memory — always available |
```

### Step 2: Update `/session start` — Global Tier step

Replace the current step 1 with:

```markdown
1. **Global Tier** *(optional — skip silently at any failure)*:
   - Check if `search_nodes` is in the available tool list (indicates MCP `@modelcontextprotocol/server-memory` is active).
   - If MCP available: call `read_graph()`, then filter and load:
     - All category entities: `UserPreferences`, `CodingStyle`, `ToolPreferences`
     - Project entity matching the current project name (basename of cwd)
   - If MCP not available: try `save_memory` tool.
   - If `save_memory` not available: try reading `~/.agents/preferences/` and `~/.agents/facts/`.
   - If all fail: skip silently without error.
```

### Step 3: Update `/session end` — Sync Global Memory step

Replace the current step 2 with:

```markdown
2. **Sync Global Memory** *(optional — first success wins, skip silently on all failures)*:
   - If MCP available (`search_nodes` in tools):
     - For each new cross-project fact or preference learned this session:
       - Call `search_nodes` with the target entity name to check if it exists.
       - If exists: call `add_observations` with new facts only (avoid duplicates).
       - If not exists: call `create_entities` then `add_observations`.
     - Use category entities (`UserPreferences`, `CodingStyle`, `ToolPreferences`) for user-wide facts.
     - Use a project entity named after the current repo (cwd basename) for project-scoped facts.
   - Else if `save_memory` available: write cross-project facts.
   - Else if `~/.agents/` accessible: write to `preferences/` or `facts/` markdown files.
```

### Step 4: Add MCP Knowledge Graph Entity Conventions section

Add a new section after "Memory Backend Support":

```markdown
## MCP Knowledge Graph Entity Conventions

When MCP `@modelcontextprotocol/server-memory` is the active global tier, use these entity naming conventions:

### Category entities (cross-project user facts)

| Entity name | Purpose |
| --- | --- |
| `UserPreferences` | Language, communication style, formatting preferences |
| `CodingStyle` | Naming conventions, error handling, commit style |
| `ToolPreferences` | Preferred CLIs, shells, task runners |

### Project entities (repo-scoped facts)

Named after the repository (e.g., `harus-skills`). Observations describe project-specific conventions:
- "Uses mise for all tasks"
- "Never run prettier on .md files — use markdownlint-cli2 only"

### Deduplication rule

Before adding any observation, call `search_nodes` with the entity name. Add only facts not already present. Never add the same observation twice.
```

### Step 5: Update version in SKILL.md frontmatter

Bump `version: 1.1.0` → `version: 1.2.0`

### Step 6: Lint

```bash
make lint
```

Expected: no errors on `skills/session/SKILL.md`

### Step 7: Commit

```bash
git add skills/session/SKILL.md
git commit -m "feat(session): add MCP memory as primary global tier"
```

---

## Task 2: Update `init-project` skill — MCP detection and setup prompt

**Files:**

- Modify: `skills/init-project/SKILL.md`

### Step 1: Add MCP detection to Phase 2 (Report & Ask)

After the existing tooling gap questions, add a new check block at the end of Phase 2:

```markdown
### MCP Memory Check

After scanning existing tooling:

1. Check if `search_nodes` is in the available tool list (MCP memory already active).
2. If **not** detected, prompt:
   > "No MCP memory server detected. Want me to add `@modelcontextprotocol/server-memory` to your Claude config? This enables persistent global memory (user preferences, cross-project facts) across all projects."
3. If user **accepts**: proceed to write MCP config (see Phase 3 addition below).
4. If user **declines**: skip config write, but still document MCP in generated `AGENT_README.md`.
```

### Step 2: Add MCP config write to Phase 3

Add after the `.agents/config.yaml` generation step. The section instructs Claude to read `.claude/settings.json` first if it exists, merge `mcpServers.memory` without overwriting other keys, or create the file if absent. The JSON to write:

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

Skip silently if `mcpServers.memory` is already present.

### Step 3: Update `AGENT_README.md` template — add Global Memory section

Inside the generated `AGENT_README.md` template (the content Claude writes into new projects), add a **Global Memory** section after the Session End Protocol:

```markdown
## Global Memory (MCP)

If `@modelcontextprotocol/server-memory` is configured, it is the primary global memory tier.

### Entity conventions

**Category entities** (cross-project user facts):
- `UserPreferences` — language, formatting, communication style
- `CodingStyle` — naming, error handling, commit conventions
- `ToolPreferences` — preferred CLIs, shells, task runners

**Project entities** (repo-scoped facts):
- Named after this repository (e.g., `my-project`)
- Observations: project-specific conventions Claude should remember

### User commands

| User says | Agent does |
| --- | --- |
| "log this globally: [fact]" | Writes to appropriate MCP category entity |
| "remember for this project: [fact]" | Writes to project entity in MCP |

### Fallback chain

If MCP is not available: `save_memory` → `~/.agents/` → skip silently.
```

### Step 4: Update `CONTEXT.md` template — add MCP agent rules

In the generated `CONTEXT.md` template, add to the Agent Rules section:

```markdown
- DO: Check MCP memory at session start — if `search_nodes` is available, call `read_graph()` and load category entities + project entity.
- DO: At session end, persist new cross-project facts to MCP via `create_entities` / `add_observations`. Check for duplicates first with `search_nodes`.
- DO: Use category entities (`UserPreferences`, `CodingStyle`, `ToolPreferences`) and a project entity named after the repo.
```

### Step 5: Update Phase 6 summary

Add to the summary print block:

```text
  .claude/settings.json  - MCP memory server config (if enabled)
```

### Step 6: Update version in SKILL.md frontmatter

Bump `version: 0.1.1` → `version: 0.2.0`

### Step 7: Lint

```bash
make lint
```

Expected: no errors on `skills/init-project/SKILL.md`

### Step 8: Commit

```bash
git add skills/init-project/SKILL.md
git commit -m "feat(init-project): prompt MCP memory setup and update templates"
```

---

## Task 3: Bump version files and open PR

**Files:**

- Modify: `gemini-extension.json`
- Modify: `.claude-plugin/marketplace.json`

### Step 1: Bump `gemini-extension.json`

`version` field: `1.0.2` → `1.0.3`

### Step 2: Bump `.claude-plugin/marketplace.json`

`metadata.version` field: `1.0.2` → `1.0.3`

### Step 3: Format JSON files

```bash
make fmt
```

Expected: no changes to markdown files, JSON formatted cleanly.

### Step 4: Commit

```bash
git add gemini-extension.json .claude-plugin/marketplace.json
git commit -m "chore: bump version to 1.0.3 for MCP memory integration"
```

### Step 5: Push and open PR

```bash
git push -u origin HEAD
gh pr create --title "feat: integrate MCP memory as primary global tier in session and init-project" \
  --body "Adds @modelcontextprotocol/server-memory as the primary global memory tier. See docs/plans/2026-03-01-mcp-memory-refactor-design.md for full design."
```

---

### Checklist

- [ ] Task 1: `session` skill updated — MCP detection, read/write protocol, entity conventions, version bumped
- [ ] Task 2: `init-project` skill updated — MCP check in Phase 2, config write, template updates, version bumped
- [ ] Task 3: Version files bumped, PR opened
