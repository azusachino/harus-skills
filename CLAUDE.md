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
  session/                        # Deprecated — MCP-primary session management (use asobi)
    SKILL.md
  asobi/                          # Session, task dispatcher, knowledge tier, skill library (asobi CLI)
    SKILL.md
  toolbelt/                       # Modern CLI tool reference (eza/rg/fd/sd/xh/dasel/...)
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
- **Plugin `harus-skills`**: skills auto-discovered (`init-project`, `session`, `asobi`, `toolbelt`)

### Skill Invocation

| Invocation | Skill |
| --- | --- |
| `/init-project`, `/init` | Initialize project with agent infrastructure |
| `/session` | **Deprecated** — MCP `server-memory` session management; use `/asobi` |
| `/asobi` | Session continuity, task dispatcher, knowledge tier, and skill library (`asobi` CLI) |
| `/toolbelt` | Reference for preferred modern CLIs (`eza`/`rg`/`fd`/`sd`/`xh`/`dasel`/...) |

## Skill Reference

### `session` (v1.6.2) — Deprecated

Superseded by `asobi`. MCP-primary session management on `@modelcontextprotocol/server-memory`: session state lives in a `[project]:session` MCP entity, docs sync at boundaries. Retained only for environments still on `server-memory`; new work should use `/asobi`.

### `asobi` (v1.6.0)

CLI-native shared state via the `asobi` knowledge graph — one graph, four pillars. Prefers shared XDG state; project-local (`asobi init --local`) is opt-in. `asobi` is required — there is no `.agents/` file fallback.

- `/asobi start` / `/asobi end` — session continuity (load/save the `[project]:session` entity)
- `/asobi tasks plan|list|dispatch|sync|close` — durable task dispatcher (epic + task entities, status lifecycle) replacing TodoWrite/local jsonl
- `/asobi recall` — knowledge tier: `ingest`/`query` over docs + an ADR decision log
- `/asobi skills` — install/update agent skills from a git repo or local path into the graph, recalled alongside docs
- Pruning & maintenance: each entity caps at 50 observations by default — append during active work, then rewrite/consolidate (`asobi stats` → `delete-observations`) to stay under the cap

### `toolbelt` (v1.0.0)

Self-contained reference for haru's preferred modern CLIs. Carries both the substitution table (`ls`/`cat`→`eza`/`bat`, `grep`/`find`→`rg`/`fd`, `sed`→`sd`, `curl`→`xh`, non-JSON→`dasel`, etc.) and the core tooling discipline (Nix-first, `make` task runner, `jq` for JSON, `rtk` proxy) so it works on any device regardless of the local global `CLAUDE.md`.

### `init-project` (v1.4.0)

Scans a project, asks targeted questions, and generates `CLAUDE.md` (single source of truth), `.claude/` infra, docs, and tooling configs. Mise-first tool provisioning (nix opt-in for repos with a flake). Seeds the asobi graph so `/asobi start` has context on first run; asobi is required (no `.agents/` fallback).

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

- **Session Management**: Run `/asobi start` at the start of any session. Run `/asobi end` before wrapping up.
- **Version Bump Rule**: There is one universal `harus-skills` version, shared across all plugin manifests. After editing any `skills/*/SKILL.md`, bump in the same commit: (1) the skill's own `metadata.version`, and (2) the single universal version in every manifest, all kept identical — `.claude-plugin/marketplace.json` (both top-level `metadata.version` and the plugin entry's `version`), `gemini-extension.json` `version`, and `.codex-plugin/plugin.json` `version`. Check the actual files for current versions — do not rely on a cached value here.
- **Staging discipline**: Always `git add <specific files>`. Never `git add -A` or `git add .`.

## Development Workflow

### Setup

```bash
nix develop       # Enter dev shell (provides all tools via nixpkgs)
make install-hooks  # Install git pre-commit hooks
```

### Common Commands

```bash
make fmt          # Format JSON/YAML (NOT markdown)
make fmt-check    # Check formatting without modifying
make check        # Run all checks (format + verify)
make validate     # PR gate: check + plugin manifest validation
make list-skills  # List all available skills
make verify       # Verify repository structure
make clean        # Remove generated lessons
```

CI (`.github/workflows/ci.yml`) runs `nix develop --command make validate` on every push to `main` and every PR.

### File Formatting

- **Markdown**: no linting. Never run Prettier on `.md` files — it wraps prose and breaks formatting. Never manually wrap prose lines either.
- **JSON/YAML**: Prettier with 2-space indentation (the only formatter; tools come from the nix devShell)

## Key Conventions

- All skills use SKILL.md format with YAML frontmatter
- Skills ask user permission before executing commands
- No emojis in git commit messages or MR descriptions
- Conventional commit style: `feat:`, `fix:`, `docs:`, `chore:`
- Always run `make check` before committing; `make validate` before PRs
- Never overwrite existing files without asking
