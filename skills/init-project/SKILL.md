---
name: init-project
description: Initialize project with agent infrastructure, documentation structure, and tooling gaps filled
metadata:
  author: haru
  version: 0.2.0
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

- Mise for tooling management (local, exclusively)
- Formatters (prettier, markdownlint-cli2, zig fmt, rustfmt, gofmt, black, etc.)
- Linters (eslint, markdownlint-cli2, clippy, golangci-lint, pylint, etc.)
- Git hooks (husky, pre-commit, `github.com/j178/prek`, lefthook, .git/hooks/)
- CI/CD (.github/workflows/, .gitlab-ci.yml, Jenkinsfile)
- Editor config (.editorconfig, .vscode/, .idea/)
- Task runner (Makefile, justfile, Taskfile.yml)

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

### MCP Memory Check

After presenting scan findings and asking tooling questions:

1. Check if `search_nodes`, `create_entities`, and `add_observations` are all in the available tool list (MCP `@modelcontextprotocol/server-memory` already active).
2. If **not** detected, ask: "No MCP memory server detected. Want me to add `@modelcontextprotocol/server-memory` to your Claude config? This enables persistent global memory (user preferences, cross-project facts) that persists across all projects and sessions."
3. If user **accepts**: write the MCP server config in Phase 3 (see below).
4. If user **declines** or MCP is already active: skip the config write, but still document MCP conventions in the generated `AGENT_README.md`.

## Phase 3: Generate Agent Infrastructure

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

Store **internal agent-specific rules** and state that doesn't belong in the public `AGENTS.md`.

```markdown
## Agent Rules (Hard DO / DON'T)
- DO: Update `CURRENT_TASK.md` before session end.
- DO: *(Optional)* Check `~/.agents/` or `save_memory` at session start for global preferences — skip silently if inaccessible.
- DO: *(Optional)* Sync learned personal facts to global memory via `save_memory` or `~/.agents/` if accessible.
- DO: Check MCP memory at session start — if `search_nodes`, `create_entities`, and `add_observations` are all available, call `read_graph()` and load category entities (`UserPreferences`, `CodingStyle`, `ToolPreferences`) plus the project entity matching the repo name.
- DO: At session end, persist new cross-project facts to MCP. Use `search_nodes` to check for existing observations before adding new ones. Use category entities for user-wide facts and a project entity (named after repo) for project-scoped facts.
- DON'T: Commit without user confirmation.

## Project Context (Internal)
[specific technical notes, non-obvious patterns, or agent-only instructions]
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

#### .claude/settings.json (MCP server config) — only if user accepted MCP setup

Read `.claude/settings.json` first if it exists. Merge the following `mcpServers.memory` key into the existing content without overwriting any other keys. If the file does not exist, create it with this content:

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

If the file already has `mcpServers.memory`, skip this step silently.

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
  .claude/settings.json  - MCP memory server config (if enabled)
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

- **Take token usage into consideration**: while running user scripts (lint, fmt, compile), if there was no explicit error, you should not read the output (reduce token usage)
- **Never overwrite existing files** without asking. If `AGENTS.md` already exists, ask whether to merge, replace, or skip.
- **Local first** while processing user prompt, any decision made shall store to local, as context, memory, new-plan, etc. both user and Agents could review these decisions.
- **Ask permission** before writing each group of files.
- **Be concise** in generated content. Avoid boilerplate filler.
- **Populate from scan** wherever possible. Don't leave everything as TODO if the information is available.
- **Language-aware**: adapt templates to the detected language and ecosystem.
- **Respect existing conventions**: if the project already has patterns, follow them rather than imposing new ones.
- **Code Quality**: make sure the project availablity (run `fmt`, `lint`, `compile` after finishing new feature implementation)
