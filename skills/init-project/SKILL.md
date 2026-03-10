---
name: init-project
description: Initialize project with agent infrastructure, documentation structure, and tooling gaps filled
metadata:
  author: haru
  version: 0.4.0
user-invokable: true
disable-model-invocation: true
---

# Init Project

Initialize the current project with agent infrastructure, documentation, and tooling. This skill is agent-agnostic and sets up infrastructure for any AI coding agent.

## Phase 1: Scan

Before asking any questions, silently scan the project to build a profile.

Collect:

### Project Identity

- Detect primary language(s) from file extensions and config files
- Detect framework(s) from dependencies and config
- Detect build system (build.zig, Cargo.toml, package.json, go.mod, pom.xml, CMakeLists.txt, Makefile, etc.)
- Detect package manager and lock files

### Existing Agent Infrastructure

- Check for: `AGENTS.md`, `.agents/` directory, `CLAUDE.md`, `.cursor/`, `.aider/`, any agent config files
- Note what already exists to avoid overwriting

### Existing Tooling

- Nix environment (`flake.nix`, `shell.nix`, `default.nix`, `flake.lock`, `devenv.nix`) — preferred tool provisioning
- Mise (`mise.toml`, `.mise.toml`) — fallback tool manager when nix is absent
- Formatters (prettier, markdownlint-cli2, zig fmt, rustfmt, gofmt, black, etc.)
- Linters (eslint, markdownlint-cli2, clippy, golangci-lint, pylint, etc.)
- Git hooks (husky, pre-commit, `github.com/j178/prek`, lefthook, .git/hooks/)
- CI/CD (.github/workflows/, .gitlab-ci.yml, Jenkinsfile)
- Editor config (.editorconfig, .vscode/, .idea/)
- Task runner (Makefile — primary; justfile, Taskfile.yml as alternatives)

### Existing Documentation

- README.md, docs/ directory, any design documents
- Existing architecture or setup docs

### Git State

- Current branch, remotes, recent commit history

## Phase 2: Report & Ask

Present the scan findings as a concise summary, then ask interactive questions for anything the scan could not determine. Ask **one question at a time**. Only ask questions whose answers cannot be inferred from the scan.

Possible questions (skip if already known):

1. "What does this project do?" (short description for AGENTS.md)
2. "What is the architecture style?" (monolith / microservice / library / CLI tool / API server / other)
3. "What are your key coding conventions?" (naming style, error handling approach, testing philosophy)
4. "What quality checks must pass?" (format, lint, test, coverage threshold, etc.)
5. For each detected tooling gap: "No [tool] found. Want me to add [suggested tool]?"

Note on tool provisioning: if nix is detected, recommend nix devShell/devenv as the source of tools. If nix is not detected and mise is absent, suggest one — ask which the user prefers. Do not suggest both.

### MCP Memory Check

After presenting scan findings and asking tooling questions:

1. Check if `search_nodes`, `create_entities`, and `add_observations` are all in the available tool list (indicates MCP `@modelcontextprotocol/server-memory` is active).
2. If **not** detected, ask: "No MCP memory server detected. Want me to add `@modelcontextprotocol/server-memory` to your Claude config? This enables persistent global memory (user preferences, cross-project facts) that persists across all projects and sessions."
3. If user **accepts**: write the MCP server config in Phase 3 (see below).
4. If user **declines** or if MCP **was** already detected in step 1: skip the config write, but still document MCP conventions in the generated `AGENT_README.md`.

## Phase 3: Generate Agent Infrastructure

If the `@modelcontextprotocol/server-memory` MCP is available, call `read_graph()` first to retrieve global facts.

When generating the templates below, dynamically merge the retrieved facts naturally:

- `CodingStyle` facts → merge into `AGENTS.md` (Coding Conventions) and `.agents/config.yaml`.
- `ToolPreferences` facts → merge into `AGENTS.md` (Build, Run & Test) and `.agents/config.yaml`.
- `UserPreferences` & `Standard` facts → merge into `.agents/CONTEXT.md` (Agent Rules) and `AGENTS.md` (Quality Standards).

Ask permission before writing each file.

### AGENTS.md (project root)

Generate a comprehensive project briefing document for both humans and agents. This is the **primary reference** for anyone (or any agent) starting work on the project.

```markdown
# AGENTS

## Project Overview

[description from scan + user input]

## Tech Stack & Architecture

[detected tech stack, high-level structure, key patterns]

## Build, Run & Test

[detected commands: make X, npm run Y, etc.]

## Coding Conventions

[naming style, error handling, testing philosophy, formatting rules]

## Key Files & Entry Points

[important files and directories for quick orientation]

## Quality Standards

[required checks: format, lint, test, coverage, etc.]
```

### .markdownlint-cli2.yaml (project root)

Generate this file to enforce standard markdown exclusions:

```yaml
ignores:
  - ".agents/**"
  - "docs/plans/**"
```

### .agents/ Directory (Agent Memory & Session Protocol)

Create `.agents/` directory and populate it with the following files to implement the **Agent Memory & Session Management Protocol**. Ask permission before writing each file.

#### .agents/AGENT_README.md

Generate with the following content (adjust project name and date):

```markdown
# Agent Memory & Session Management Protocol

> **Read this file at the start of every session. Then read `CURRENT_TASK.md` to resume work.**

## Session Start Protocol

1. **Invoke `/session start`** if the skill is available — it loads all tiers automatically.
2. If `/session` is unavailable, do manually:
   - *(Optional)* Read `~/.agents/preferences/` and `~/.agents/facts/` if accessible. **If access is denied or the directory does not exist, skip silently — do not error.**
   - Read `AGENTS.md` and `.agents/CONTEXT.md` for project context.
   - Read `.agents/CURRENT_TASK.md` to resume the last state.
3. Confirm to user: current task, last completed step, next action.

**Do not read the entire codebase upfront.** Read files on demand only when needed.

## Session End Protocol

1. **Invoke `/session end`** if the skill is available.
2. If unavailable, do manually:
   - Overwrite `CURRENT_TASK.md` with current state (see format below).
   - Append new decisions to `MEMORY.md`.
   - *(Optional)* Sync global memory via `save_memory` or `~/.agents/` if accessible. **Skip silently if not accessible.**
3. Confirm: "Session saved. Next: [one-sentence handoff]."

## Global Memory (MCP)

If `@modelcontextprotocol/server-memory` is configured, it is the primary global memory tier. Check for `search_nodes`, `create_entities`, and `add_observations` in available tools at session start.

### Entity conventions

**Category entities** (cross-project user facts):
- `UserPreferences` — language, formatting, communication style
- `CodingStyle` — naming, error handling, commit conventions
- `ToolPreferences` — preferred CLIs, shells, task runners

**Project entities** (repo-scoped facts):
- Named after this repository (cwd basename, lowercased, hyphens for spaces)
- Observations: project-specific conventions Claude should remember

Both category and project entities are supported and used together.

### User commands

| User says | Agent does |
| --- | --- |
| "log this globally: [fact]" | Writes observation to appropriate MCP category entity |
| "remember for this project: [fact]" | Writes observation to project entity in MCP |

### Fallback chain

If MCP is not available: `save_memory` → `~/.agents/` → skip silently.

## File Formats

### `CURRENT_TASK.md` — overwrite each session end

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

## Files Modified This Session
- path/to/file — [what changed and why]

## Next Action
[single concrete next step]

## Last Updated
YYYY-MM-DD
\```

### `MEMORY.md` — append only, never rewrite existing entries

```markdown
## YYYY-MM-DD — [short title]
**Decision:** [what was decided]
**Reason:** [why]
**Alternatives rejected:** [what else was considered]

---
\```

## Token Budget

| File | Read when | Max size |
| --- | --- | --- |
| `AGENT_README.md` | Session start | < 100 lines |
| `CONTEXT.md` | Session start | < 200 lines |
| `CURRENT_TASK.md` | Session start | < 80 lines |
| `MEMORY.md` | On demand | grows over time |

## User Commands

| User says | Agent does |
| --- | --- |
| "start session" / "let's continue" | Load README + CONTEXT + CURRENT_TASK, confirm state |
| "wrap up" / "end session" | Update CURRENT_TASK + append MEMORY + confirm done |
| "what's the context?" | Summarize CONTEXT + CURRENT_TASK in plain language |
| "log this decision: ..." | Append to MEMORY.md immediately |
| "reset task" | Clear CURRENT_TASK.md, ask user for new objective |
```

#### .agents/CONTEXT.md

Store **internal agent rules and living project context**. This file is always read at session start and updated whenever core features, architecture, or non-obvious conventions change. It is the authoritative source for anything that doesn't fit in the public `AGENTS.md`.

```markdown
## Agent Rules (Hard DO / DON'T)
- DO: At session start — if MCP is available (`search_nodes` in tools), call `read_graph()` and load category entities + `[project]:session`. Skip `CURRENT_TASK.md` entirely when MCP is active.
- DO: At session end — if MCP is available, write session state to `[project]:session` entity (delete old, recreate). Do not write `CURRENT_TASK.md` when MCP is active.
- DO: Update this file (`CONTEXT.md`) when core project behavior, architecture, or conventions change.
- DO: Use `make <target>` for all task execution (format, lint, test, check).
- DON'T: Commit without user confirmation.
- DON'T: Write `CURRENT_TASK.md` when MCP is active — it creates git noise.

## Project Context (Internal)
[specific technical notes, non-obvious patterns, or agent-only instructions]

## Tool Provisioning
[nix devShell / mise / other — how tools are obtained in this project]
```

#### .agents/CURRENT_TASK.md

Seed with the initial state:

```markdown
## Objective
Initial project setup and agent infrastructure implementation.

## Status
DONE

## Completed Steps
- [x] Project scanned
- [x] Agent infrastructure generated (.agents/, AGENTS.md, docs/)
- [x] Tooling gaps identified

## Remaining Steps
- [ ] Begin development of the first feature

## Open Questions / Blockers
- None

## Files Modified This Session
- AGENTS.md
- .agents/*
- docs/*
- [detected tool configs]

## Next Action
Wait for user instructions to begin the first development task.

## Last Updated
[current date]
```

#### .agents/MEMORY.md

Seed with:

```markdown
# Decision Log

---
```

#### .agents/config.yaml

```yaml
version: 0.0.1
project:
  language: [detected]
  framework: [detected]
  build_system: [detected]
quality:
  format: true
  lint: true
  test: true
tools:
  task_runner: [make]
  formatter: [detected]
  linter: [detected]
conventions:
  commit_style: conventional
  naming: [detected or asked]
  indent: [detected or asked]
```

#### MCP server config — only if user accepted MCP setup

Write to each agent config file detected in the Phase 1 scan. Skip any file that already has the `memory` server configured. For each detected agent:

**Invocation command**: use `npx -y @modelcontextprotocol/server-memory` by default. If nix is the primary tool manager, offer the nix alternative:

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

Ask the user which invocation style to use if nix is detected. Default to `npx` if unsure.

**Claude Code** (detected: `.claude/` exists):
Read `.claude/settings.json` if it exists, merge `mcpServers.memory` without overwriting other keys, or create the file with the chosen invocation.

**Gemini CLI** (detected: `.gemini/` exists):
Read `.gemini/settings.json` if it exists, merge `mcpServers.memory` without overwriting other keys.

**Codex** (detected: `.codex/` exists):
Read `.codex/config.toml` if it exists, append `[mcp_servers.memory]` block if not already present.

If no agent config directory is detected, default to writing `.claude/settings.json` and ask the user to confirm or specify their agent.

**Also**: add `.agents/CURRENT_TASK.md` and `.agents/MEMORY.md` to `.gitignore` (or create `.agents/.gitignore`) so session-volatile files don't pollute git history. Ask permission before doing this.

## Phase 4: Generate Documentation

Ask permission, then create `docs/` with these files:

### docs/architecture.md

```markdown
# Architecture

## System Overview

[high-level description]

## Project Structure

[directory tree with descriptions]

## Module Map

[key modules and their responsibilities]

## Data Flow

[how data moves through the system]

## Dependencies

[external dependencies and their purpose]
```

Populate from scan results. Leave sections as `[TODO]` if unknown.

### docs/requirements.md

```markdown
# Requirements

## Functional Requirements

- [ ] [TODO: list functional requirements]

## Non-Functional Requirements

- Performance: [TODO]
- Security: [TODO]
- Reliability: [TODO]

## Constraints

- [TODO: list technical constraints]
```

### docs/project-design.md

```markdown
# Project Design

## Design Goals

[TODO: what this project optimizes for]

## Key Decisions

| Decision     | Choice     | Rationale |
| ------------ | ---------- | --------- |
| Language     | [detected] | [TODO]    |
| Build System | [detected] | [TODO]    |

## Trade-offs

[TODO: document trade-offs made]
```

### docs/setup.md

```markdown
# Setup

## Prerequisites

[detected tools and versions]

## Installation

[detected install steps or TODO]

## Build

[detected build commands]

## Run

[detected run commands]

## Test

[detected test commands]
```

Populate from scan results.

### docs/plan.md

```markdown
# Implementation Plan

## Current Phase

[TODO: describe current development phase]

## Roadmap

- [ ] [TODO: milestone 1]
- [ ] [TODO: milestone 2]

## Completed

- [none yet]
```

### docs/todo.md

```markdown
# Task Tracking

## In Progress

- [none]

## Blocked

- [none]

## Done

- [x] Project initialized with agent infrastructure and docs
```

### docs/status.md

```markdown
# Feature Status

| Feature | Status  | Owner | Notes |
| ------- | ------- | ----- | ----- |
| [TODO]  | planned | -     | -     |

## Status Legend

- **planned**: not started
- **in-progress**: actively being worked on
- **review**: implementation complete, under review
- **done**: merged and verified
- **blocked**: cannot proceed, see notes
```

## Phase 5: Fill Tooling Gaps

For each missing tool detected in the scan, offer to create the config. Ask permission for each one individually.

**Tool provisioning priority**:

1. **Nix** (`flake.nix` / `shell.nix` / `devenv.nix`) — preferred. Tools come from nix devShell. Do not suggest mise if nix is present.
2. **Mise** (`mise.toml`) — only suggest if nix is absent and no other tool manager is detected.
3. **Task runner**: always `make`. Generate a `Makefile` with standard targets (`fmt`, `lint`, `test`, `check`) if one doesn't exist.

**Reference configs are in `CONFIGS.md`** (same directory as this file). Read `CONFIGS.md` for the index, then read `configs/common.md` and the language-specific config file (e.g., `configs/rust.md`) based on the detected language. Only read what is needed to minimize token usage.

## Phase 6: Summary

Print a summary of everything created:

```text
Init complete! Created:
  AGENTS.md              - project briefing for agents
  .agents/AGENT_README.md - memory protocol rules
  .agents/CONTEXT.md      - stable project knowledge
  .agents/MEMORY.md       - append-only decision log
  .agents/CURRENT_TASK.md - session save point
  .agents/config.yaml     - agent configuration
  .claude/settings.json  - MCP memory server config (Claude Code, if enabled)
  .gemini/settings.json  - MCP memory server config (Gemini CLI, if enabled)
  .codex/config.toml     - MCP memory server config (Codex, if enabled)
  docs/architecture.md   - system architecture
  docs/requirements.md   - project requirements
  docs/project-design.md - design decisions
  docs/setup.md          - development setup
  docs/plan.md           - implementation roadmap
  docs/todo.md           - task tracking
  docs/status.md         - feature status
  .editorconfig          - editor settings
  [any other files created]
```

## Important Rules

- **Token efficiency**: while running user scripts (lint, fmt, compile), if there was no explicit error, do not read the output.
- **Never overwrite existing files** without asking. If `AGENTS.md` already exists, ask whether to merge, replace, or skip.
- **Ask permission** before writing each group of files.
- **Be concise** in generated content. Avoid boilerplate filler.
- **Populate from scan** wherever possible. Don't leave everything as TODO if the information is available.
- **Language-aware**: adapt templates to the detected language and ecosystem.
- **Respect existing conventions**: if the project already has patterns, follow them rather than imposing new ones.
- **Task runner is always `make`**: reference `make <target>` in all generated docs and configs. Never reference mise tasks.
- **Nix-first tooling**: if nix is detected, all tool provisioning references should point to nix. Do not introduce mise alongside nix.
- **Reduce git noise**: add `.agents/CURRENT_TASK.md` and `.agents/MEMORY.md` to `.gitignore` — session-volatile files should not pollute git history.
