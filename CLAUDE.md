# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repository contains custom Claude Code skills for productivity and project management. Skills are user-invocable commands that extend Claude Code's capabilities. The repository uses Claude's plugin marketplace system via `.claude-plugin/marketplace.json` configuration.

## Repository Structure

```text
skills/                           # Custom skill definitions (flat)
  init-project/                   # Project initialization skill
    SKILL.md
    configs/                      # Bundled config templates
  session/                        # Session and memory management
    SKILL.md
docs/                             # Project documentation
  plans/                          # Design documents
.claude-plugin/
  marketplace.json                # Plugin marketplace registration
.codex-plugin/
  plugin.json                     # Codex plugin manifest
gemini-extension.json             # Gemini CLI extension manifest
```

Note: language learning skills (`notion-language-lesson`) live in `harus-nix/.claude/skills/` as personal-only skills.

## Architecture

### Skill System

All skills follow the [Agent Skills Standard](http://agentskills.io) format with `SKILL.md` files:

- YAML frontmatter: `name`, `description`, `metadata` (author, version), optional `allowed-tools`
- Markdown body: execution instructions for Claude
- Optional `README.md` for user-facing documentation

### Plugin Configuration

The `.claude-plugin/marketplace.json` defines a single plugin under the `harus-skills` marketplace. Skills are auto-discovered from `skills/` — no explicit listing required.

- **Marketplace name**: `harus-skills`
- **Plugin `harus-skills`**: skills auto-discovered (`init-project`, `session`)

### Skill Invocation

| Invocation | Skill |
| --- | --- |
| `/init-project`, `/init` | Initialize project with agent infrastructure |
| `/session` | Session and memory management |

## Skill Reference

### `session` (v1.5.0)

MCP-primary session management. When `@modelcontextprotocol/server-memory` is available, session state lives in a `[project]:session` MCP entity — `CURRENT_TASK.md` is skipped entirely. Syncs docs (`AGENTS.md`, `CONTEXT.md`) at session boundaries. Integrates with context-mode (`ctx_batch_execute`, `ctx_search`) when available.

- `/session start` — load MCP entities + project context, flag stale docs
- `/session end` — write session state to MCP, sync/trim docs

### `init-project` (v1.0.0)

Scans a project, asks targeted questions, and generates `AGENTS.md`, `.agents/` files, docs, and tooling configs. Nix-first tool provisioning (mise as fallback). Adds `CURRENT_TASK.md`/`MEMORY.md` to `.gitignore`. Offers nix-run or npx for MCP server invocation.

## MCP Servers

MCP servers are not bundled — configure them globally in `~/.claude/settings.json`. Detect availability by checking the tool list.

| Server | Detect via | When to use |
| --- | --- | --- |
| `memory` | `search_nodes`, `create_entities`, `add_observations` | Persisting session state and facts across conversations |
| `fetch` | `fetch` | Retrieving live URLs, docs, or external references |
| `sequential-thinking` | `sequentialthinking` | Complex multi-step planning before acting on large changes |

**`memory` usage**: `search_nodes` before starting work to load prior context; `create_entities` / `add_observations` to save; `delete_entities` on stale session nodes at session end. Entity naming: `[project-name]:session` for session state, `UserPreferences` / `CodingStyle` / `ToolPreferences` for global facts.

**`fetch` usage**: prefer over `WebFetch` when available — pass a URL and get back the page content. Do not use for local file reads.

**`sequential-thinking` usage**: invoke at the start of complex tasks with a clear problem statement; follow the returned steps in order. Skip for simple well-scoped tasks.

## Agent Behavior

- **Session Management**: Run `/session start` at the start of any session if `.agents/` exists. Run `/session end` before wrapping up.
- **Version Bump Rule**: After editing any `skills/*/SKILL.md`, bump in the same commit: (1) the skill's `metadata.version`, (2) `gemini-extension.json` version, (3) `.claude-plugin/marketplace.json` metadata.version. Check the actual files for current versions — do not rely on a cached value here.
- **Staging discipline**: Always `git add <specific files>`. Never `git add -A` or `git add .`.

## Development Workflow

### Setup

```bash
nix develop       # Enter dev shell (provides all tools via nixpkgs)
make install-hooks  # Install git pre-commit hooks
```

### Common Commands

```bash
make fmt          # Format JSON, YAML, TOML (NOT markdown)
make fmt-check    # Check formatting without modifying
make lint         # Lint Python (ruff)
make lint-fix     # Lint and auto-fix
make check        # Run all checks (format + lint + verify)
make list-skills  # List all available skills
make verify       # Verify repository structure
make clean        # Remove generated lessons
```

### File Formatting

- **Markdown**: no linting. Never run Prettier on `.md` files — it wraps prose and breaks formatting. Never manually wrap prose lines either.
- **JSON/YAML**: Prettier with 2-space indentation
- **TOML**: Taplo formatter
- **Shell scripts**: shfmt with 2-space indentation
- **Python**: ruff

## Key Conventions

- All skills use SKILL.md format with YAML frontmatter
- Skills ask user permission before executing commands
- No emojis in git commit messages or MR descriptions
- Conventional commit style: `feat:`, `fix:`, `docs:`, `chore:`
- Always run `make fmt` + `make lint` before committing
- Never overwrite existing files without asking
