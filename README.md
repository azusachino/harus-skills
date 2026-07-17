<h1 align="center">harus-skills</h1>

<p align="center">
  <em>Curated Claude Code skills for durable memory, disciplined tooling, and lazy-senior-dev code.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-3.2.1-111111?style=flat-square" alt="version">
  <img src="https://img.shields.io/badge/license-MIT-111111?style=flat-square" alt="MIT license">
  <img src="https://img.shields.io/badge/works%20with-Claude%20Code%20%7C%20Codex%20%7C%20Antigravity-111111?style=flat-square" alt="works with Claude Code, Codex, Antigravity">
  <img src="https://img.shields.io/badge/format-Agent%20Skills%20Standard-111111?style=flat-square" alt="Agent Skills Standard">
</p>

<p align="center">
  <sub>Three skills. One graph for memory. One toolbelt for the terminal. Zero runtime code — just markdown an agent reads.</sub>
</p>

---

## ✨ Skills

| Skill | What it does |
| --- | --- |
| 🧠 **`/asobi`** | Durable state across sessions and sub-agents via the [`asobi`](https://github.com/azusachino/asobi) CLI knowledge graph. One graph, four pillars: **session continuity** (`start`/`end`), a **task dispatcher** (`tasks plan\|list\|dispatch\|sync\|close`) with atomic claims that replaces ephemeral TodoWrite/jsonl, SQLite FTS5/BM25 **keyword recall** (`search` + an ADR log), and a **skill library** (`skills` — install/update skills from git). |
| 📝 **`/revise`** | Persist lessons, findings, and dead ends so future sessions recall them — positive lessons on the project entity, wrong approaches as active `pitfall` warnings surfaced at the next `/asobi start`. |
| 🧰 **`/toolbelt`** | Reference for haru's preferred modern CLIs + the core tooling discipline (Nix-first, `make` runner, `jq` for JSON, `mise x -- <tool>`). Self-contained, works on any device. |

### 🧰 What's in the toolbelt

Modern OSS CLIs, reached for by default over the classic Unix tools:

- **Search & edit** — [`rg`](https://github.com/BurntSushi/ripgrep)/[`fd`](https://github.com/sharkdp/fd) (text/file), [`ast-grep`](https://ast-grep.github.io/) (AST-aware structural search & rewrite), [`sd`](https://github.com/chmln/sd) (find/replace), [`difftastic`](https://github.com/Wilfred/difftastic) (syntax-aware diffs), [`typos`](https://github.com/crate-ci/typos) (source spell-check)
- **View & inspect** — [`eza`](https://github.com/eza-community/eza)/[`bat`](https://github.com/sharkdp/bat)/[`dust`](https://github.com/bootandy/dust), [`procs`](https://github.com/dalance/procs) (ps), [`doggo`](https://github.com/mr-karan/doggo) (dig), [`hexyl`](https://github.com/sharkdp/hexyl) (hex), [`tailspin`](https://github.com/bensadeh/tailspin) (log highlight)
- **HTTP & data** — [`xh`](https://github.com/ducaale/xh) (curl), [`dasel`](https://github.com/TomWright/dasel) (YAML/TOML/XML/CSV), [`duckdb`](https://duckdb.org/), [`miller`](https://github.com/johnkerl/miller) (CSV/TSV), [`hyperfine`](https://github.com/sharkdp/hyperfine)/[`oha`](https://github.com/hatoo/oha) (benchmarks)
- **Runtimes** — [`uv`](https://github.com/astral-sh/uv)/`uvx` (Python), [`bun`](https://github.com/oven-sh/bun)/`bunx` (JS/TS)

## 📦 Installation

### Prerequisites

- [Claude Code](https://claude.ai/code) CLI
- [`asobi`](https://github.com/azusachino/asobi) CLI for the `/asobi` skill (`cargo install asobi`)

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

## 🛠️ Development

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

## 🗂️ Skill Structure

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

## 🤝 Contributing

1. Create a new directory directly under `skills/`
2. Add a `SKILL.md` with YAML frontmatter (`name`, `description`, `metadata.version`)
3. Run `make check` before submitting
4. Open a pull request

## 🙏 Credits & inspiration

Design decisions are recorded as [ADRs](docs/adr/). The skills stand on the shoulders of the OSS agent-skill community:

- [**asobi**](https://github.com/azusachino/asobi) — the knowledge-graph CLI that backs `/asobi`
- [**Agent Skills Standard**](http://agentskills.io) — the `SKILL.md` format every skill targets
- [**ponytail**](https://github.com/DietrichGebert/ponytail) — the "lazy senior dev" YAGNI ladder distilled into the `CodingStyle` seed
- [**karpathy-guidelines**](https://github.com/multica-ai/andrej-karpathy-skills) — surgical changes + goal-driven verification, folded into the seed values
- [**superpowers**](https://github.com/obra/superpowers) — the ethos of distilling the *gist* into a few load-bearing principles

## 📚 Resources

- [Agent Skills Standard](http://agentskills.io)
- [Claude Code Documentation](https://code.claude.com/docs)
