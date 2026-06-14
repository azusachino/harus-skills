# harus-skills

A collection of custom Claude Code skills for productivity and project management.

## Skills

**`/asobi`** — Share durable state across sessions and sub-agents via the [`asobi`](https://github.com/azusachino/asobi) CLI knowledge graph. One graph, four pillars: **session continuity** (`start`/`end`), a **task dispatcher** (`tasks plan|list|dispatch|sync|close`) that replaces ephemeral TodoWrite/local jsonl, a **knowledge tier** (`recall` — `ingest`/`query` + an ADR decision log), and a **skill library** (`skills` — install/recall agent skills from git). `asobi` is required — there is no `.agents/` file fallback.

**`/init-project`** (alias: `/init`) — Scaffold agent infrastructure for any project. Scans the codebase, asks targeted questions, and generates `CLAUDE.md`, `.claude/` infra, docs, and tooling configs. Mise-first tool provisioning (nix opt-in); seeds the asobi graph so `/asobi start` has context on first run.

**`/toolbelt`** — Reference for haru's preferred modern CLIs (`eza`/`bat`, `rg`/`fd`, `sd`, `xh`, `dasel`, `procs`, `doggo`, `hexyl`, `duckdb`/`psql`, `hyperfine`/`oha`) plus the core tooling discipline (Nix-first, `make` task runner, `jq` for JSON). Self-contained, so it works on any device.

**`/session`** — **Deprecated.** MCP variant of session management built on `@modelcontextprotocol/server-memory`. Superseded by `/asobi`, which provides the same session continuity plus a task dispatcher and knowledge tier without an MCP dependency. Retained for environments still on `server-memory`; new projects should use `/asobi`.

## Installation

### Prerequisites

- [Claude Code](https://claude.ai/code) CLI
- [`asobi`](https://github.com/azusachino/asobi) CLI for the `/asobi` skill (`cargo install asobi --features documents`)
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

Only the deprecated `/session` skill needs an MCP server. `/asobi` and `/init-project` have no MCP dependency. If you still use `/session`, configure `server-memory` globally in `~/.claude/settings.json`:

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

Tools via nix devShell. Tasks via Makefile.

```bash
nix develop          # Enter dev shell (provides all tools)
make install-hooks   # Install git pre-commit hooks
make fmt             # Format JSON/YAML (not markdown)
make check           # Run all checks (format + verify)
make validate        # PR gate: check + plugin manifest validation
make verify          # Verify repository structure
make list-skills     # List all available skills
```

## Skill Structure

Each skill follows the [Agent Skills Standard](http://agentskills.io) format as a flat directory under `skills/`:

```text
skills/
  asobi/
    SKILL.md          # Skill definition with YAML frontmatter
    README.md
  init-project/
    SKILL.md
    configs/          # Bundled config templates
  toolbelt/
    SKILL.md
  session/            # Deprecated — superseded by asobi
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
