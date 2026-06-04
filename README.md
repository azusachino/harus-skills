# harus-skills

A collection of custom Claude Code skills for productivity and project management.

## Skills

**`/rosemary`** (v1.2.0) — Share durable state across sessions and sub-agents via the [`rosemary`](https://github.com/azusachino/rosemary) CLI knowledge graph. One graph, three pillars: **session continuity** (`start`/`end`), a **task dispatcher** (`tasks plan|list|dispatch|sync|close`) that replaces ephemeral TodoWrite/local jsonl, and a **knowledge tier** (`recall` — `ingest`/`query` + an ADR decision log). Falls back to `.agents/` files when rosemary is absent.

**`/init-project`** (v1.3.0, alias: `/init`) — Scaffold agent infrastructure for any project. Scans the codebase, asks targeted questions, and generates `AGENTS.md`, `.agents/` files, `CLAUDE.md`, `.claude/rules/`, `.claude/settings.json` (permissions + hooks), `.worktreeinclude`, docs, and tooling configs. Mise-first tool provisioning (nix opt-in); seeds the rosemary graph so `/rosemary start` has context on first run.

**`/session`** (v1.6.0) — **Deprecated.** MCP variant of session management built on `@modelcontextprotocol/server-memory`. Superseded by `/rosemary`, which provides the same session continuity plus a task dispatcher and knowledge tier without an MCP dependency. Retained for environments still on `server-memory`; new projects should use `/rosemary`.

## Installation

### Prerequisites

- [Claude Code](https://claude.ai/code) CLI
- [`rosemary`](https://github.com/azusachino/rosemary) CLI for the `/rosemary` skill (`cargo install --git https://github.com/azusachino/rosemary --features documents`)
- Node.js (for `npx`-based MCP servers, only if using the `/session` MCP variant)

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

## MCP Servers (optional)

Only the deprecated `/session` skill needs an MCP server. `/rosemary` and `/init-project` have no MCP dependency. If you still use `/session`, configure `server-memory` globally in `~/.claude/settings.json`:

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
  rosemary/
    SKILL.md          # Skill definition with YAML frontmatter
    README.md
  init-project/
    SKILL.md
    configs/          # Bundled config templates
  session/            # Deprecated — superseded by rosemary
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
