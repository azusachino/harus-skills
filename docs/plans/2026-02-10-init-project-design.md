# init-project Skill Design (v0.0.1)

## Purpose

An agent-agnostic skill that initializes any project with:

1. Agent infrastructure (AGENTS.md, .agents/MEMORY.md)
2. Project documentation structure (docs/)
3. Missing tooling and configuration

## What It Produces

### Agent Infrastructure

```text
AGENTS.md                # Project root: architecture overview + conventions
.agents/
  MEMORY.md              # Shared agent memory, seeded with personal defaults
  config.yaml            # Agent preferences (tools, conventions, quality bar)
```

### Project Documentation

```text
docs/
  architecture.md        # System design, module map, data flow
  requirements.md        # Functional and non-functional requirements
  project-design.md      # High-level design decisions and trade-offs
  setup.md               # Dev environment setup, build, run, test
  plan.md                # Current implementation plan / roadmap
  todo.md                # Task tracking (done, in-progress, blocked)
  status.md              # Feature implementation status tracking table
```

### Tooling (gap-filling, offered per-file)

- `.editorconfig`
- Git hooks / pre-commit config
- CI workflow templates
- Enhanced `mise.toml` tasks (fmt, lint, test, check)
- `.gitignore` additions

## Execution Flow

### Phase 1: Scan

Silently analyze the project to build a profile:

- **Project identity**: language(s), framework(s), build system, package manager
- **Existing agent files**: AGENTS.md, .agents/, CLAUDE.md, etc.
- **Existing tooling**: formatters, linters, git hooks, CI/CD, editor config, task runner
- **Existing docs**: README, docs/ directory, any design documents
- **Git state**: current branch, remotes, recent activity

### Phase 2: Interactive Questions

Ask targeted questions based on scan gaps (one at a time):

1. Project description (what does this project do?)
2. Architecture style (monolith, microservice, library, CLI, etc.)
3. Key conventions (naming, error handling, testing approach)
4. Quality bar (which checks must pass: fmt, lint, test, coverage)
5. Tool preferences (only for detected gaps)

Each question is skipped if the scan already determined the answer.

### Phase 3: Generate Agent Infrastructure

1. Generate `AGENTS.md` at project root:
   - Architecture overview (structure, modules, data flow)
   - Coding conventions and rules
   - Key file locations
   - Build/test/run commands
2. Create `.agents/MEMORY.md` seeded with:
   - Personal defaults (tool preferences, code style, workflow patterns)
   - Project-specific findings from the scan
3. Create `.agents/config.yaml` with tool and quality preferences

### Phase 4: Generate Documentation

Create `docs/` with templated files populated from scan + answers:

- `architecture.md` - from project scan
- `requirements.md` - template with sections
- `project-design.md` - from architecture style + decisions
- `setup.md` - from detected build/test commands
- `plan.md` - empty roadmap template
- `todo.md` - empty task tracker
- `status.md` - feature status table template

### Phase 5: Fill Tooling Gaps

Offer to create missing configs one-by-one:

- `.editorconfig` (language-appropriate defaults)
- Git hooks (format on commit, test on push)
- CI workflow (build + test for detected platform)
- Enhanced `mise.toml` tasks
- `.gitignore` additions

Each file requires user permission before creation.

### Phase 6: Summary

Report everything that was created/modified.

## Personal Defaults (seeded into MEMORY.md)

These are cross-project preferences:

- **Tool preferences**: use mise for task running, prefer language-native formatters
- **Code style**: no emojis in commits, prose wrap at 80 chars, 2-space indent for configs
- **Workflow**: always ask before committing, format before commit, run tests before PR
- **Quality**: format + lint + test must pass before merge

## SKILL.md Metadata

```yaml
name: init-project
description: Initialize project with agent infrastructure, docs, and tooling
metadata:
  author: haru
  version: 0.0.1
  aliases: ["init"]
allowed-tools: Bash(mise *) Bash(git *) Bash(ls *) Bash(mkdir *)
```

## Plugin Registration

Add to `harus-skills` plugin in marketplace.json:

```json
"./skills/init-project"
```
