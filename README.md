<h1 align="center">harus-skills</h1>

<p align="center">
  <em>Portable agent skills for durable work state, evidence-backed lessons, and practical tooling.</em>
</p>

<p align="center">
  <a href="https://github.com/azusachino/harus-skills/actions/workflows/ci.yml"><img src="https://github.com/azusachino/harus-skills/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT license"></a>
  <img src="https://img.shields.io/badge/Agent%20Skills-Standard-blue.svg" alt="Agent Skills Standard">
  <img src="https://img.shields.io/badge/Works%20with-Claude%20Code%20%7C%20Codex%20%7C%20Antigravity-blueviolet.svg" alt="Works with Claude Code, Codex, and Antigravity">
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
| 🧰 **`/toolbelt`** | Preferred modern CLIs and usage recipes. Mise pins project tools, Make owns tasks, and `jq` handles JSON; the project's declared toolchain takes precedence. |

Skills support the current task and its authorization. They resolve routine uncertainty through evidence, keep task state separate from durable lessons, and verify results in proportion to risk. Current user and project instructions override portable defaults or recalled preferences. Tool availability is checked on the actual machine.

Asobi discovers configuration in ancestor directories, so a nested repository can share its parent's graph. Task dispatch records ownership; the agent still reads relevant lessons and starts any delegated work. Workspaces with a `[skills]` declaration in `asobi.toml` use `asobi skills sync` to reconcile installed skills, including removals.

### 🧰 What's in the toolbelt

Modern OSS CLIs, reached for by default over the classic Unix tools:

- **Search & edit** — [`rg`](https://github.com/BurntSushi/ripgrep)/[`fd`](https://github.com/sharkdp/fd) (text/file), [`ast-grep`](https://ast-grep.github.io/) (AST-aware structural search & rewrite), [`sd`](https://github.com/chmln/sd) (find/replace), [`difftastic`](https://github.com/Wilfred/difftastic) (syntax-aware diffs), [`typos`](https://github.com/crate-ci/typos) (source spell-check)
- **View & inspect** — [`eza`](https://github.com/eza-community/eza)/[`bat`](https://github.com/sharkdp/bat)/[`dust`](https://github.com/bootandy/dust), [`procs`](https://github.com/dalance/procs) (ps), [`doggo`](https://github.com/mr-karan/doggo) (dig), [`hexyl`](https://github.com/sharkdp/hexyl) (hex), [`tailspin`](https://github.com/bensadeh/tailspin) (log highlight)
- **HTTP & data** — [`xh`](https://github.com/ducaale/xh) (curl), [`dasel`](https://github.com/TomWright/dasel) (YAML/TOML/XML/CSV), [`duckdb`](https://duckdb.org/), [`miller`](https://github.com/johnkerl/miller) (CSV/TSV), [`hyperfine`](https://github.com/sharkdp/hyperfine)/[`oha`](https://github.com/hatoo/oha) (benchmarks)
- **Runtimes** — [`uv`](https://github.com/astral-sh/uv)/`uvx` (Python), [`bun`](https://github.com/oven-sh/bun)/`bunx` (JS/TS)

## 📦 Installation

### Prerequisites

- A supported agent host (Claude Code, Codex, or Antigravity)
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

This repository currently uses a Nix devShell and Nix-based CI. The portable tooling default is Mise; migrating this repository's development setup is tracked in the harus-kb remediation plan.

```bash
nix develop          # Enter dev shell (provides all tools)
make fmt             # Format JSON/YAML (not markdown)
make check           # Run all checks (format + verify)
make validate        # PR gate: check + plugin manifest validation
make verify          # Verify repository structure
make list-skills     # List all available skills
```

Run checks explicitly: the current hook installer assumes a directory-backed `.git` and restages files, so it is unsuitable for vendored submodules or partial staging. Manifest validation proves JSON validity and aligned versions; it does not exercise installation in each agent host.

## 🗂️ Skill Structure

Each skill follows the [Agent Skills Standard](http://agentskills.io) format as a flat directory under `skills/`:

```text
skills/
  asobi/
    SKILL.md          # Skill definition with YAML frontmatter
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
- [**ponytail**](https://github.com/DietrichGebert/ponytail) — reuse existing capabilities and keep solutions small
- [**karpathy-guidelines**](https://github.com/multica-ai/andrej-karpathy-skills) — surgical changes and goal-driven verification

## 📚 Resources

- [Agent Skills Standard](http://agentskills.io)
- [Claude Code Documentation](https://code.claude.com/docs)
