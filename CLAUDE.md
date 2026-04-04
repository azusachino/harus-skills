# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repository contains custom Claude Code skills for productivity, project management, and language learning. Skills are user-invocable commands that extend Claude Code's capabilities. The repository uses Claude's plugin marketplace system via `.claude-plugin/marketplace.json` configuration.

## Repository Structure

```text
skills/                           # Custom skill definitions
  code-skills/                    # Project and session management skills
    init-project/                 # Project initialization skill
      SKILL.md
      configs/                    # Bundled config templates
    session/                      # Session and memory management
      SKILL.md
  lang-skills/                    # Language learning skills
    daily-language-lesson/        # Language lesson generator (Obsidian vault output)
      SKILL.md                    # Skill definition with YAML frontmatter
      README.md                   # User documentation
    notion-language-lesson/       # Language lesson generator (Notion output)
      SKILL.md
      README.md
      scripts/                    # nll-push.py, nll-status.py
docs/                             # Project documentation
  plans/                          # Design documents
.claude-plugin/
  marketplace.json                # Plugin marketplace registration (two plugins: code-skills, lang-skills)
gemini-extension.json             # Gemini CLI extension manifest
```

## Architecture

### Skill System

All skills follow the [Agent Skills Standard](http://agentskills.io) format with `SKILL.md` files:

- YAML frontmatter: `name`, `description`, `metadata` (author, version), optional `allowed-tools`
- Markdown body: execution instructions for Claude
- Optional `README.md` for user-facing documentation

### Plugin Configuration

The `.claude-plugin/marketplace.json` defines two plugins under the `harus-skills` marketplace:

- **Marketplace name**: `harus-skills`
- **Plugin `code-skills`**: `init-project`, `session`
- **Plugin `lang-skills`**: `daily-language-lesson`, `notion-language-lesson`

### Skill Invocation

| Invocation | Plugin | Skill |
| --- | --- | --- |
| `/daily-language-lesson`, `/dll`, `/lesson` | `lang-skills` | Language lessons → Obsidian vault |
| `/notion-language-lesson`, `/nll` | `lang-skills` | Language lessons → Notion database |
| `/init-project`, `/init` | `code-skills` | Initialize project with agent infrastructure |
| `/session` | `code-skills` | Session and memory management |

## Skill Reference

### `session` (v1.5.0)

MCP-primary session management. When `@modelcontextprotocol/server-memory` is available, session state lives in a `[project]:session` MCP entity — `CURRENT_TASK.md` is skipped entirely. Syncs docs (`AGENTS.md`, `CONTEXT.md`) at session boundaries. Integrates with context-mode (`ctx_batch_execute`, `ctx_search`) when available.

- `/session start` — load MCP entities + project context, flag stale docs
- `/session end` — write session state to MCP, sync/trim docs

### `init-project` (v1.0.0)

Scans a project, asks targeted questions, and generates `AGENTS.md`, `.agents/` files, docs, and tooling configs. Nix-first tool provisioning (mise as fallback). Adds `CURRENT_TASK.md`/`MEMORY.md` to `.gitignore`. Offers nix-run or npx for MCP server invocation.

### `daily-language-lesson`

Generates multi-language lessons saved directly to the Obsidian vault daily note (`$VAULT_PATH/YYYY/YYYY-MM-DD.md`) using `ad-note` callout blocks.

- English: advanced (native-level literature, idioms, sophisticated grammar)
- Japanese: N1 level (advanced kanji, keigo, literary expressions)
- Spanish: B1–B2 (intermediate vocabulary and grammar)

### `notion-language-lesson` (v1.1.0, alias: `/nll`)

Same lesson content as `daily-language-lesson`, pushed to a Notion database as structured toggle-block pages. Falls back to Obsidian vault if Notion push fails. Requires `NOTION_API_KEY` and `NOTION_DATABASE_ID` env vars — see `skills/notion-language-lesson/README.md`.

## Agent Behavior

- **Session Management**: Run `/session start` at the start of any session if `.agents/` exists. Run `/session end` before wrapping up.
- **Version Bump Rule**: After editing any `skills/*/*/SKILL.md`, bump in the same commit: (1) the skill's `metadata.version`, (2) `gemini-extension.json` version, (3) `.claude-plugin/marketplace.json` metadata.version. Check the actual files for current versions — do not rely on a cached value here.
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
