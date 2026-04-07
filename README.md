# harus-skills

A collection of custom Claude Code skills for productivity and project management.

## Skills

**`/init-project`** (v1.0.0, alias: `/init`) — Scaffold agent infrastructure for any project. Scans the codebase, asks targeted questions, and generates `AGENTS.md`, `.agents/` files, `CLAUDE.md`, `.claude/rules/` (core + optional config/release/testing), `.claude/settings.json` (permissions + hooks), `.mcp.json` (project-specific MCP servers only), `.worktreeinclude`, docs, and tooling configs. Nix-first tool provisioning. Merges global MCP memory facts into generated files.

**`/session`** (v1.5.0) — MCP-primary session management. When `@modelcontextprotocol/server-memory` is available, session state lives in a `[project]:session` MCP entity — no local file writes. Syncs and trims `AGENTS.md`/`CONTEXT.md` at session boundaries.

- `/session start` — Load MCP entities + project context, flag stale docs
- `/session end` — Write session state to MCP, sync docs

## Installation

### Prerequisites

- [Claude Code](https://claude.ai/code) CLI installed
- Node.js (for `npx`-based MCP servers)

### Marketplace Plugin (Recommended)

```bash
/plugin marketplace add azusachino/harus-skills
/plugin install harus-skills
```

Restart Claude Code for changes to take effect.

### Gemini CLI Extension

```bash
gemini extensions install https://github.com/azusachino/harus-skills
```

Or for local development:

```bash
gemini extensions link /path/to/harus-skills
```

## MCP Servers

This repo ships a `.mcp.json` with three servers used by the skills:

| Server | Purpose |
| --- | --- |
| `memory` (`@modelcontextprotocol/server-memory`) | Persistent session state across conversations |
| `fetch` (`mcp-server-fetch` via uvx) | HTTP fetching for skills that need web access |
| `sequential-thinking` (`@modelcontextprotocol/server-sequential-thinking`) | Structured reasoning for complex tasks |

When installed as a Claude Code plugin, server names are namespaced to `plugin:harus-skills:<name>` — but tool function names (`search_nodes`, `fetch`, `sequentialthinking`) are unchanged, so skill detection logic works regardless. For Codex, `.mcp.json` is read directly with no prefix.

**Recommended**: configure these globally in `~/.claude/settings.json` (Claude Code) or `~/.gemini/settings.json` (Gemini CLI) to avoid duplicates and the namespace prefix.

## Development

Tools via nix devShell (mise as fallback). Tasks via Makefile.

```bash
nix develop          # Enter dev shell (provides all tools)
make install-hooks   # Install git pre-commit hooks
make fmt             # Format JSON, YAML, TOML files
make lint            # Lint Python files
make check           # Run all checks (fmt + lint + verify)
make verify          # Verify repository structure
make list-skills     # List all available skills
```

## Skill Structure

Each skill follows the [Agent Skills Standard](http://agentskills.io) format, organized as a flat directory under `skills/`:

```text
skills/
  init-project/
    SKILL.md          # Skill definition with YAML frontmatter
    configs/          # Bundled config templates
  session/
    SKILL.md
```

## Contributing

1. Create a new directory directly under `skills/`
2. Add a `SKILL.md` with YAML frontmatter (`name`, `description`, `metadata.version`)
3. Register it in `.claude-plugin/marketplace.json` under the matching plugin
4. Run `make check` before submitting
5. Open a pull request

## Resources

- [Agent Skills Standard](http://agentskills.io)
- [Claude Code Documentation](https://code.claude.com/docs)
