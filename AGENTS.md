# AGENTS

## Project Overview

A collection of custom agent skills for productivity and project management. Compatible with Claude Code, Gemini CLI, and Codex. Skills are user-invocable commands following the [Agent Skills Standard](http://agentskills.io). Published as a Claude plugin marketplace at `azusachino/harus-skills` and a Gemini CLI extension.

## Architecture

```text
harus-skills/
  skills/                        # Flat skill directories
    init-project/                # Project scaffolding and agent infrastructure
    session/                     # MCP-primary memory management, CONTEXT.md as living doc
  docs/
    plans/                       # Design documents
  .claude-plugin/
    marketplace.json             # Plugin marketplace registration (harus-skills plugin)
  gemini-extension.json          # Gemini CLI extension manifest
  Makefile                       # Task runner (fmt, lint, test, check, verify)
```

Each skill is a directory with a `SKILL.md` (YAML frontmatter + markdown body) and an optional `README.md`.

### Plugin Structure

- **Marketplace**: `azusachino/harus-skills`
- **Plugin**: `harus-skills` (init-project, session) — skills auto-discovered from `skills/`
- Install: `/plugin marketplace add azusachino/harus-skills` → `/plugin install harus-skills`
- Invocation: `/skill-name` or `/harus-skills:skill-name`

## Skills

| Skill | Version | Invocation | Purpose |
| --- | --- | --- | --- |
| `session` | 1.5.0 | `/session` | MCP-primary session state; doc sync at start/end; context-mode aware |
| `init-project` | 0.5.0 | `/init-project`, `/init` | Scaffold AGENTS.md, .agents/, docs, MCP config; nix-first tooling |

## Build & Run

No compilation. Content repository — tools via nix devShell (or mise as fallback), tasks via Makefile.

```bash
make fmt          # Format JSON, YAML, TOML (not markdown)
make lint         # Lint Python (ruff)
make check        # Run all checks (format + lint + verify)
make list-skills  # List available skills
make verify       # Verify repo structure
make clean        # Remove generated lessons
```

## Conventions

- Skill files: YAML frontmatter + markdown body, no line length limit on prose
- **Markdown**: no linting — do not run markdownlint or Prettier on `.md` files
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
| `Makefile` | All task definitions |
| `.codex-plugin/plugin.json` | Codex plugin manifest — skills |
| `.env.example` | Documents VAULT_PATH and other env vars |

## MCP Servers

MCP servers are not bundled — configure them globally in `~/.claude/settings.json`. Detect availability by checking the tool list at session start.

### `memory` (`@modelcontextprotocol/server-memory`)

**Detect**: `search_nodes`, `create_entities`, `add_observations` present in tool list.

**When to use**: persisting facts and session state that must survive across conversations — user preferences, project conventions, in-progress task summaries.

**How**:
- `create_entities` — create named nodes (`UserPreferences`, `CodingStyle`, `[project]:session`)
- `add_observations` — append facts to an existing entity
- `search_nodes` — retrieve relevant entities by keyword before starting work
- `delete_entities` — clean up stale session entities at session end

Entity conventions:
- Category entities: `UserPreferences`, `CodingStyle`, `ToolPreferences`, `Standard`
- Session entities: `[project-name]:session` — volatile, deleted and recreated each session end
- Project entities: named after repo (e.g. `harus-skills`), lowercased, hyphens for spaces

When active, `CURRENT_TASK.md` is skipped entirely — session state lives in `[project]:session`. Fallback: `~/.agents/` → skip silently.

### `fetch` (`mcp-server-fetch`)

**Detect**: `fetch` present in tool list.

**When to use**: retrieving live content that isn't in the codebase — documentation pages, API specs, GitHub raw files, external references needed by a skill.

**How**: call `fetch` with a URL. Prefer this over `WebFetch` when the MCP is available — it handles redirects and encoding more reliably. Do not use for internal filesystem reads.

### `sequential-thinking` (`@modelcontextprotocol/server-sequential-thinking`)

**Detect**: `sequentialthinking` present in tool list.

**When to use**: tasks that require explicit multi-step planning before acting — complex refactors, architectural decisions, multi-file changes where order matters, or any task where rushing to code risks missing dependencies.

**How**: invoke `sequentialthinking` at the start of the task with a clear problem statement. It returns a structured chain of reasoning steps; follow them in order. Skip for simple, well-scoped tasks — the overhead isn't worth it.

## Quality Standards

1. `make fmt` — all non-markdown files formatted
2. `make lint` — markdown lint + Python lint passes
3. `make verify` — all skills have SKILL.md, marketplace.json exists
