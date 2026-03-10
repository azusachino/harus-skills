---
name: init-project
description: Initialize project with agent infrastructure, documentation structure, and tooling gaps filled
metadata:
  author: haru
  version: 0.5.0
user-invokable: true
disable-model-invocation: true
---

# Init Project

Initialize the current project with agent infrastructure, documentation, and tooling. Agent-agnostic.

## Phase 1: Scan

Silently collect before asking anything:

- **Language/framework**: file extensions, config files, dependency manifests
- **Build system**: `Makefile`, `Cargo.toml`, `go.mod`, `package.json`, `build.zig`, etc.
- **Existing agent infra**: `AGENTS.md`, `.agents/`, `CLAUDE.md`, `.cursor/`, `.aider/`
- **Tooling**:
  - Nix: `flake.nix`, `shell.nix`, `default.nix`, `devenv.nix`, `flake.lock` — preferred
  - Mise: `mise.toml`, `.mise.toml` — fallback when nix absent
  - Formatters, linters, git hooks, CI/CD, editor config
  - Task runner: `Makefile` (primary), `justfile`, `Taskfile.yml`
- **Docs**: `README.md`, `docs/`, existing architecture or design docs
- **Git state**: branch, remotes, recent commits
- **MCP**: check if `search_nodes`, `create_entities`, `add_observations` are in available tools

## Phase 2: Report & Ask

Present scan summary, then ask **one question at a time** for anything not inferable:

1. "What does this project do?" — for AGENTS.md overview
2. "Architecture style?" — monolith / library / CLI / API / microservice
3. "Key coding conventions?" — naming, error handling, testing philosophy
4. "Quality checks that must pass?" — format, lint, test, coverage
5. Per tooling gap: "No [tool] found. Want me to add [suggestion]?"

Tool provisioning: if nix detected, recommend nix devShell — do not suggest mise alongside it. If neither detected, ask which the user prefers.

If MCP not detected: "No MCP memory server found. Add `@modelcontextprotocol/server-memory`? It enables persistent cross-project memory." Write config in Phase 3 if accepted.

## Phase 3: Generate Agent Infrastructure

If MCP available, call `read_graph()` first. Merge retrieved facts into generated files:

- `CodingStyle` → `AGENTS.md` Coding Conventions
- `ToolPreferences` → `AGENTS.md` Build/Run/Test
- `UserPreferences`, `Standard` → `.agents/CONTEXT.md` Agent Rules

Ask permission before writing each file. Never overwrite without asking.

### AGENTS.md

Public project briefing for humans and agents. Sections:

- **Project Overview** — description, purpose
- **Tech Stack & Architecture** — detected stack, structure, key patterns
- **Build, Run & Test** — `make fmt`, `make lint`, `make test`, `make check`, etc.
- **Coding Conventions** — naming, error handling, formatting rules
- **Key Files & Entry Points** — important paths for quick orientation
- **Quality Standards** — required checks before commit/merge

### .agents/CONTEXT.md

Internal living doc — always read at session start, updated when core things change. Sections:

- **Agent Rules** — hard DO/DON'T for this project:
  - DO: Use `make <target>` for all task execution
  - DO: At session start, load MCP entities if available; skip `CURRENT_TASK.md` when MCP active
  - DO: At session end, write state to `[project]:session` MCP entity; do not write `CURRENT_TASK.md` when MCP active
  - DO: Update this file when architecture or conventions change
  - DON'T: Commit without user confirmation
- **Project Context** — non-obvious patterns, technical notes, agent-only instructions
- **Tool Provisioning** — how tools are obtained (nix devShell / mise / other)

### .agents/CURRENT_TASK.md (fallback only)

Seed with initial DONE state. This file is used only when MCP is unavailable. Add it to `.gitignore`.

Fields: `Objective`, `Status`, `Completed Steps`, `Remaining Steps`, `Next Action`, `Last Updated`.

### .agents/MEMORY.md (fallback only)

Seed with empty decision log header. Used only when MCP is unavailable. Add to `.gitignore`.

### .markdownlint-cli2.yaml

```yaml
ignores:
  - ".agents/**"
  - "docs/plans/**"
```

### .gitignore additions

Add to `.gitignore` (or `.agents/.gitignore`):

```gitignore
.agents/CURRENT_TASK.md
.agents/MEMORY.md
```

These are session-volatile — keeping them tracked creates git noise.

### MCP server config (if user accepted)

Write to each detected agent config, skipping any that already have `memory` configured.

**Default invocation** (npx):

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

**Nix alternative** (offer if nix detected):

```json
{
  "mcpServers": {
    "memory": {
      "command": "nix",
      "args": ["run", "nixpkgs#nodePackages_latest.@modelcontextprotocol/server-memory"]
    }
  }
}
```

Targets: `.claude/settings.json` (Claude Code), `.gemini/settings.json` (Gemini CLI), `.codex/config.toml` (Codex). Default to `.claude/settings.json` if no agent config detected.

## Phase 4: Generate Documentation

Ask permission, then create `docs/` files. Populate from scan; leave `[TODO]` only for genuinely unknown sections.

- **docs/architecture.md** — system overview, project structure tree, module map, data flow, dependencies
- **docs/setup.md** — prerequisites, install, build, run, test commands
- **docs/plan.md** — current phase, roadmap milestones, completed items
- **docs/todo.md** — in progress, blocked, done tasks

Skip docs that already exist unless user asks to regenerate.

## Phase 5: Fill Tooling Gaps

For each gap found in Phase 1, offer to create the config. Ask permission individually.

Tool provisioning priority:

1. **Nix** — preferred; tools come from devShell. Don't add mise if nix present.
2. **Mise** — only if nix absent and no other manager detected.
3. **Makefile** — always generate if missing; include `fmt`, `lint`, `test`, `check` targets.

Reference configs: read `CONFIGS.md` (same directory) for the index, then load only `configs/common.md` and the relevant language file. Read on demand — do not preload all configs.

## Phase 6: Summary

Print a concise list of everything created, e.g.:

```text
Init complete:
  AGENTS.md, .agents/CONTEXT.md, .agents/CURRENT_TASK.md, .agents/MEMORY.md
  .gitignore (updated), .markdownlint-cli2.yaml
  .claude/settings.json (MCP memory)
  docs/architecture.md, docs/setup.md, docs/plan.md, docs/todo.md
  Makefile, [other tooling configs]
```

## Rules

- **Never overwrite** existing files without asking (merge, replace, or skip).
- **Ask permission** before writing each group of files.
- **Populate from scan** — don't leave TODO when the info is available.
- **Make is the task runner** — reference `make <target>` everywhere. No mise task references.
- **Nix-first** — if nix detected, all tool references point to nix.
- **Token efficiency** — if a script runs without error, don't read its output.
- **Language-aware** — adapt all templates to the detected language/ecosystem.
