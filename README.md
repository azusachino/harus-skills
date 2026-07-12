# harus-skills

A collection of custom Claude Code skills for productivity and project management.

## Skills

**`/asobi`** — Share durable state across sessions and sub-agents via the [`asobi`](https://github.com/azusachino/asobi) CLI knowledge graph. One graph, four pillars: **session continuity** (`start`/`end`), a **task dispatcher** (`tasks plan|list|dispatch|sync|close`) that replaces ephemeral TodoWrite/local jsonl, a **knowledge tier** (`recall` — `ingest`/`query` + an ADR decision log), and a **skill library** (`skills` — install/recall agent skills from git). `asobi` is required — there is no `.agents/` file fallback.

**`/revise`** — Persist project lessons, findings, and wrong approaches so future sessions can recall them. Stores positive lessons on the project entity, wrong approaches as active `[project]:pitfall:<slug>` warnings, and falls back to `docs/lessons/` only when asobi is unavailable.

**`/toolbelt`** — Reference for haru's preferred modern CLIs plus the core tooling discipline (Nix-first, `make` task runner, `jq` for JSON, `mise x -- <tool>` for project-pinned runtimes). Self-contained, so it works on any device. Covers the whole kit:

- **Search & edit** — `rg`/`fd` (text/file search), `ast-grep` (AST-aware structural search & rewrite), `sd` (find/replace), `difftastic` (syntax-aware diffs), `typos` (source spell-check)
- **View & inspect** — `eza`/`bat`/`dust`, `procs` (ps), `doggo` (dig), `hexyl` (hex), `tailspin` (log highlight), `btop`
- **HTTP & data** — `xh` (curl), `dasel` (YAML/TOML/XML/CSV), `duckdb`/`psql`, `miller` (CSV/TSV), `hyperfine`/`oha` (benchmarks)
- **Runtimes** — `uv`/`uvx` (Python), `bun`/`bunx` (JS/TS)

## Installation

### Prerequisites

- [Claude Code](https://claude.ai/code) CLI
- [`asobi`](https://github.com/azusachino/asobi) CLI for the `/asobi` skill (`cargo install asobi --features documents`)

### Claude Code — Marketplace Plugin

```bash
/plugin marketplace add azusachino/harus-skills
/plugin install harus-skills
```

Restart Claude Code after installing.

### Antigravity (agy) — Plugin

```bash
agy plugin install https://github.com/azusachino/harus-skills
# or for local development:
agy plugin link /path/to/harus-skills
```

### Codex

```bash
codex plugin install https://github.com/azusachino/harus-skills
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
  revise/
    SKILL.md
  toolbelt/
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
