# harus-skills

A collection of custom Claude Code skills for productivity and project management.

## Skills

**`/init-project`** (v1.0.0, alias: `/init`) — Scaffold agent infrastructure for any project. Scans the codebase, asks targeted questions, and generates `AGENTS.md`, `.agents/` files, `CLAUDE.md`, `.claude/rules/`, `.claude/settings.json` (permissions + hooks), `.mcp.json` (project-specific MCP servers only), `.worktreeinclude`, docs, and tooling configs. Nix-first tool provisioning. Merges global MCP memory facts into generated files.

**`/session`** (v1.5.0) — MCP-primary session management. When `@modelcontextprotocol/server-memory` is available, session state lives in a `[project]:session` MCP entity — no local file writes. Syncs and trims `AGENTS.md`/`CONTEXT.md` at session boundaries.

- `/session start` — load MCP entities + project context, flag stale docs
- `/session end` — write session state to MCP, sync docs

## Installation

### Prerequisites

- [Claude Code](https://claude.ai/code) CLI
- Node.js (for `npx`-based MCP servers)
- `uvx` / Python (for `mcp-server-fetch`)

### Claude Code — Marketplace Plugin

```bash
/plugin marketplace add azusachino/harus-skills
/plugin install harus-skills
```

Restart Claude Code after installing.

### Gemini CLI — Extension

```bash
gemini extensions install https://github.com/azusachino/harus-skills
# or for local development:
gemini extensions link /path/to/harus-skills
```

### Codex

```bash
codex plugin install https://github.com/azusachino/harus-skills
```

## MCP Servers

`.mcp.json` bundles three servers used by the skills:

| Server | Command | Purpose |
| --- | --- | --- |
| `memory` | `npx @modelcontextprotocol/server-memory` | Persistent session state across conversations |
| `fetch` | `uvx mcp-server-fetch` | HTTP fetching for live docs and references |
| `sequential-thinking` | `npx @modelcontextprotocol/server-sequential-thinking` | Structured reasoning for complex tasks |

These are installed automatically with the plugin. When installed via Claude Code, server names are namespaced to `plugin:harus-skills:<name>` — but skill detection uses tool function names (`search_nodes`, `fetch`, `sequentialthinking`) which are unaffected.

**Recommended**: configure these globally to avoid the namespace prefix and duplication. Add to `~/.claude/settings.json` (Claude Code) or `~/.gemini/settings.json` (Gemini CLI):

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

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

Each skill follows the [Agent Skills Standard](http://agentskills.io) format as a flat directory under `skills/`:

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
3. Run `make check` before submitting
4. Open a pull request

## Resources

- [Agent Skills Standard](http://agentskills.io)
- [Claude Code Documentation](https://code.claude.com/docs)
