# harus-skills

A collection of custom Claude Code skills for productivity, project management, and language learning.

## Skills

### Session & Project Management

**`/session`** (v1.5.0) — MCP-primary session management. When `@modelcontextprotocol/server-memory` is available, session state lives in a `[project]:session` MCP entity — no local file writes. Syncs and trims `AGENTS.md`/`CONTEXT.md` at session boundaries. Context-mode aware.

- `/session start` — Load MCP entities + project context, flag stale docs
- `/session end` — Write session state to MCP, sync docs

**`/init-project`** (v0.8.0) — Scaffold agent infrastructure for any project. Scans the codebase, asks targeted questions, and generates `AGENTS.md`, `.agents/` files, a root `CLAUDE.md`, `.claude/rules/` (core + optional config/release), `.claude/agents/` (reviewer + explorer), `.claude/commands/`, docs, and tooling configs. Nix-first tool provisioning. Gitignores session-volatile files. Offers nix-run or npx for MCP server setup.

### Language Learning

**`/daily-language-lesson`** (v1.0.0, aliases: `/dll`, `/lesson`) — Generate multi-language lessons and save them directly to your Obsidian vault daily note.

- **English**: Advanced level — literature, idioms, sophisticated grammar
- **Japanese**: N1 level — advanced kanji, keigo, literary expressions
- **Spanish**: B1–B2 level — intermediate vocabulary and grammar

Each lesson includes a reading passage, vocabulary section, comprehension questions, a grammar point, and writing exercises.

**`/notion-language-lesson`** (alias: `/nll`, v1.1.0) — Same lesson content as above, pushed directly to a Notion database as structured toggle-block pages. Falls back to Obsidian vault if Notion push fails. Requires `NOTION_API_KEY` and `NOTION_DATABASE_ID` — see [`skills/notion-language-lesson/README.md`](skills/notion-language-lesson/README.md) for setup.

## Installation

### Prerequisites

- [Claude Code](https://claude.ai/code) CLI installed
- Node.js (for `npx`-based MCP servers)

### Method 1: Marketplace Plugin (Recommended)

```bash
/plugin marketplace add azusachino/harus-skills
/plugin install harus-skills@harus-skills
```

Restart Claude Code for changes to take effect.

### Method 2: Skill Directory (Legacy)

Clone the repo and add to Claude Code config:

```bash
git clone https://github.com/azusachino/harus-skills
```

Edit `~/.config/claude/config.json`:

```json
{
  "skillDirectories": ["/path/to/harus-skills/skills"]
}
```

### Method 3: Gemini CLI Extension

```bash
gemini extensions install https://github.com/azusachino/harus-skills
```

Or for local development:

```bash
gemini extensions link /path/to/harus-skills
```

## MCP Memory Setup (Optional)

The `session` and `init-project` skills support `@modelcontextprotocol/server-memory` for persistent global memory across projects and sessions. User preferences and project-scoped facts are stored in a knowledge graph and loaded automatically at each session start.

Add to your agent config:

**Claude Code** (`.claude/settings.json`) and **Gemini CLI** (`.gemini/settings.json`):

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

Or via nix:

```json
{
  "mcpServers": {
    "memory": {
      "command": "nix",
      "args": ["run", "nixpkgs#nodePackages_latest.@modelcontextprotocol/server-memory"]
    }
  }
}
```

**Codex** (`.codex/config.toml`):

```toml
[mcp_servers.memory]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-memory"]
```

`/init-project` will offer to write this config automatically during project setup.

## Development

Tools via nix devShell (mise as fallback). Tasks via Makefile.

```bash
make fmt          # Format JSON, YAML, TOML files
make lint         # Lint markdown and Python files
make check        # Run all checks
make verify       # Verify repository structure
make list-skills  # List all available skills
```

## Skill Structure

Each skill follows the [Agent Skills Standard](http://agentskills.io) format:

```text
skills/
  skill-name/
    SKILL.md    # Skill definition with YAML frontmatter and instructions
    README.md   # Optional: User-facing documentation
```

## Contributing

1. Create a new directory under `skills/`
2. Add a `SKILL.md` with YAML frontmatter (`name`, `description`, `metadata.version`)
3. Register it in `.claude-plugin/marketplace.json`
4. Run `make check` before submitting
5. Open a pull request

## Resources

- [Agent Skills Standard](http://agentskills.io)
- [Claude Code Documentation](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
