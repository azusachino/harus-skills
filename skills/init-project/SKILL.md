---
name: init-project
description: Initialize project with agent infrastructure, documentation structure, and tooling gaps filled
metadata:
  author: haru
  version: 0.0.1
  aliases: ["init"]
allowed-tools: Bash(ls *) Bash(mkdir *) Bash(git *) Bash(mise *)
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

- Formatters (prettier, markdownlint-cli2, zig fmt, rustfmt, gofmt, black, etc.)
- Linters (eslint, markdownlint-cli2, clippy, golangci-lint, pylint, etc.)
- Git hooks (husky, pre-commit, `github.com/j178/prek`, lefthook, .git/hooks/)
- CI/CD (.github/workflows/, .gitlab-ci.yml, Jenkinsfile)
- Editor config (.editorconfig, .vscode/, .idea/)
- Task runner (mise.toml, Makefile, justfile, Taskfile.yml)

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

## Phase 3: Generate Agent Infrastructure

Ask permission before writing each file.

### AGENTS.md (project root)

Generate a comprehensive agent briefing document with these sections:

```markdown
# AGENTS

## Project Overview

[description from scan + user input]

## Architecture

[project structure, key modules, data flow, tech stack]

## Build & Run

[detected build, test, run commands]

## Conventions

[coding standards, naming, error handling, testing approach]

## Key Files

[important entry points, configs, and directories]

## Quality Standards

[required checks: format, lint, test, etc.]
```

Populate each section using scan results and user answers. Be concise but thorough. This file is the primary reference for any agent working on the project.

### .agents/MEMORY.md

Create `.agents/` directory and seed `MEMORY.md` with:

```markdown
# Agent Memory

## Personal Defaults

- Check tools with `mise ls`, suggest user to manage tools with mise if not installed
- Always store context and memory within local project (best accessibility for all Agents)
- Always update docs PLAN/TODO/TRACKING files after implementing new features
- Disable the line-length restriction of markdown files
- Use `mise` to run task if `Makefile` didn't exist
- Prefer language-native formatters (zig fmt, rustfmt, gofmt, prettier)
- No emojis in git commit messages
- Always ask before committing or pushing
- Format and lint before every commit
- Run tests before creating PRs/MRs
- Keep solutions simple - avoid over-engineering

## Project Patterns

[findings from the scan: detected patterns, tech stack notes, key paths]

## Decisions

[empty - to be filled as decisions are made]

## Debugging Notes

[empty - to be filled as issues are encountered]
```

### .agents/config.yaml

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
  task_runner: [mise or make]
  formatter: [detected]
  linter: [detected]
conventions:
  commit_style: conventional
  naming: [detected or asked]
  indent: [detected or asked]
```

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
  .agents/MEMORY.md      - shared agent memory
  .agents/config.yaml    - agent configuration
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
