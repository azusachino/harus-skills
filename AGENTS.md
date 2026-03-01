# AGENTS

## Project Overview

A collection of custom agent skills for productivity, project management, and language learning. Compatible with Claude Code, Gemini CLI, and Codex. Skills are user-invocable commands following the [Agent Skills Standard](http://agentskills.io). Published as a Claude plugin marketplace at `azusachino/harus-skills` and a Gemini CLI extension.

## Architecture

```text
harus-skills/
  skills/
    daily-language-lesson/       # Language lessons → Obsidian vault (en/ja/es)
    notion-language-lesson/      # Language lessons → Notion database (en/ja/es)
      scripts/                   # nll-push.py, nll-status.py
    mkmr/                        # Merge request creation helper
    init-project/                # Project scaffolding and agent infrastructure
    session/                     # Three-tier memory management (MCP/save_memory/.agents/)
    next-session/                # Lightweight context restore fallback
  docs/
    plans/                       # Design documents
  .claude-plugin/
    marketplace.json             # Plugin marketplace registration
  gemini-extension.json          # Gemini CLI extension manifest
  mise.toml                      # Tool management and task runner
```

Each skill is a directory with a `SKILL.md` (YAML frontmatter + markdown body) and an optional `README.md`.

### Plugin Structure

- **Marketplace**: `azusachino/harus-skills`
- **Plugin**: `harus-skills` (single plugin — all skills)
- Install: `/plugin marketplace add azusachino/harus-skills` → `/plugin install harus-skills@harus-skills`
- Invocation: `/skill-name` or `/harus-skills:skill-name`

## Skills

| Skill | Version | Invocation | Purpose |
| --- | --- | --- | --- |
| `session` | 1.2.0 | `/session` | Three-tier memory: MCP → save_memory → ~/.agents/ |
| `init-project` | 0.2.0 | `/init-project`, `/init` | Scaffold AGENTS.md, .agents/, docs, MCP config |
| `next-session` | 1.0.0 | `/next-session` | Lightweight context restore from .agents/ only |
| `mkmr` | 1.0.0 | `/mkmr` | Create merge requests via gh/glab |
| `daily-language-lesson` | — | `/dll`, `/lesson` | Language lessons saved to Obsidian vault |
| `notion-language-lesson` | 1.1.0 | `/nll` | Language lessons pushed to Notion database |

## Build & Run

No compilation. Content repository managed with mise (tools) and Makefile (tasks).

```bash
make install      # Install tools via mise
make dev          # Setup dev environment + git hooks
make fmt          # Format JSON, YAML, TOML (not markdown)
make lint         # Lint markdown (markdownlint-cli2) and Python (ruff)
make check        # Run all checks (format + lint + verify)
make list-skills  # List available skills
make verify       # Verify repo structure
make clean        # Remove generated lessons
```

## Conventions

- Skill files: YAML frontmatter + markdown body, no line length limit on prose
- **Markdown**: markdownlint-cli2 only — never Prettier, never manual 80-char wrapping
- **JSON/YAML**: Prettier, 2-space indent
- **TOML**: Taplo
- **Python**: ruff
- No emojis in git commit messages
- Conventional commits: `feat:`, `fix:`, `docs:`, `chore:`
- Always run `make fmt` + `make lint` before committing
- Stage files explicitly — never `git add -A`
- **Version bump** (required after any skill edit): bump skill `metadata.version` + `gemini-extension.json` + `.claude-plugin/marketplace.json` in the same commit

## Key Files

| File | Purpose |
| --- | --- |
| `CLAUDE.md` | Claude Code project instructions (detailed) |
| `AGENTS.md` | This file — high-level briefing for all agents |
| `.agents/` | Project-local session memory (CURRENT_TASK.md, MEMORY.md, CONTEXT.md) |
| `.claude-plugin/marketplace.json` | Plugin registration — bump version on every skill change |
| `gemini-extension.json` | Gemini CLI manifest — bump version on every skill change |
| `mise.toml` | All task definitions |
| `.env.example` | Documents VAULT_PATH, NOTION_API_KEY, NOTION_DATABASE_ID |

## Global Memory (MCP)

The `session` skill uses `@modelcontextprotocol/server-memory` as the primary global tier when available. Detected by checking for `search_nodes`, `create_entities`, `add_observations` in the tool list.

Entity conventions:

- Category entities: `UserPreferences`, `CodingStyle`, `ToolPreferences`
- Project entities: named after repo (e.g. `harus-skills`), lowercased, hyphens for spaces

Fallback chain: MCP → `save_memory` → `~/.agents/` → skip silently.

## Quality Standards

1. `make fmt` — all non-markdown files formatted
2. `make lint` — markdown lint + Python lint passes
3. `make verify` — all skills have SKILL.md, marketplace.json exists
