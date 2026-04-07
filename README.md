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

## MCP Memory Setup

The `session` and `init-project` skills use `@modelcontextprotocol/server-memory` for persistent global memory across projects. Configure it globally so it's available in every project — do not add it to per-project `.mcp.json`.

**Claude Code** — add to `~/.claude/settings.json`:

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

**Gemini CLI** — add to `~/.gemini/settings.json` (same `mcpServers` structure).

`/init-project` checks for existing global MCP config and skips re-scaffolding servers you already have. It only writes `.mcp.json` for project-specific servers (databases, GitHub PATs, etc.).

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
