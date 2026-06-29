# Changelog

All notable changes to this project are documented here. The version tracks the plugin/marketplace version in `.claude-plugin/marketplace.json`; individual skills carry their own `metadata.version`.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2026-06-18

### Added
- **toolbelt** (2.0.0): Added modern CLI tools (`yq`, `tokei`, `grex`, `zellij`).

### Changed
- **asobi** (2.0.0): Upgraded to the new v0.2 command API:
  - Switched `create-entities` $\rightarrow$ `new`
  - Switched `add-observations` $\rightarrow$ `obs`
  - Switched `create-relations` $\rightarrow$ `link`
  - Switched `add-truth` $\rightarrow$ `truth`
  - Switched `delete-truth` $\rightarrow$ `rm-truth`
  - Switched `delete-entities` $\rightarrow$ `rm`
  - Switched `delete-observations` $\rightarrow$ `rm-obs`
  - Switched `delete-relations` $\rightarrow$ `unlink`
  - Switched `search-nodes` $\rightarrow$ `search`
  - Switched `open-nodes` $\rightarrow$ `show`
  - Switched `read-graph` $\rightarrow$ `graph`
  - Added a Table of Contents and step-by-step observations pruning guide.
- **init-project** (2.0.0): Updated to use the new `asobi` v0.2 commands, implemented dynamic loading of global preference entities (`asobi show`), and added automatic allowed permissions for Nix-first project commands in `settings.json`.
- Root `README.md` and `CLAUDE.md`: Replaced all legacy Gemini references with Antigravity (`agy`) CLI plugin commands.

### Removed
- **session**: Completely dropped the deprecated MCP-primary `session` skill.

## [2.6.0] - 2026-06-11

### Changed

- **rosemary → asobi**: the underlying CLI was published to crates.io and renamed; the binary, command, and crate are all now `asobi`. The skill is renamed to match (`/asobi`, `skills/asobi/`), every CLI invocation switches `rosemary` → `asobi`, the config file becomes `asobi.toml`, and the project-local cache moves to `.asobi/`. No features changed — same session continuity, task dispatcher, knowledge tier, and skill library.
- **asobi** (1.5.0): install instructions now use crates.io (`cargo install asobi`, `cargo binstall asobi`, or `--features documents`) instead of `cargo install --git`.
- Docs (`CLAUDE.md`, `README.md`), the deprecated `session` skill, and `init-project` updated to reference `asobi`.

## [2.3.0] - 2026-06-04

### Added

- **rosemary** (1.2.0): task dispatcher (`/rosemary tasks plan|list|dispatch|sync|close`) backed by epic + task entities with `part_of` relations and an append-only status lifecycle (`READY_TO_DISPATCH → DISPATCHED → REVIEW → AWAITING_VERIFY → DONE`) — a durable replacement for ephemeral TodoWrite/local jsonl that sub-agents and the lead coordinate through.
- **rosemary** (1.2.0): knowledge tier (`/rosemary recall`) with `ingest`/`query` over docs and an ADR-style decision log (`<project>:decision:<slug>` concept entities with `supersedes`/`depends_on` relations).
- **rosemary** (1.2.0): `:`-hierarchical naming convention (`<project>:<epic>:task-N`), a "Real-World Practices" checklist distilled from production use, and an instruction-file index guardrail (index `CLAUDE.md`/`AGENTS.md` via `ingest`, never duplicate into entities).

### Changed

- **init-project** (1.3.0): refreshed around the rosemary + mise + make stack. Tool provisioning is now mise-first (nix opt-in for repos with an existing flake); memory seeds and reads the rosemary graph with `.agents/` files as fallback.
- **rosemary** (1.2.0): trimmed for clarity — merged Entity Reference subsections, condensed practices, replaced the status ASCII diagram with a one-liner.
- Root `README.md`: documents all three skills, rosemary prerequisites, and the now-optional MCP section.

### Removed

- **init-project** (1.3.0): Gemini and Codex bootstrap (`GEMINI.md`, `.gemini/`, `CODEX.md`, `.codex-plugin/`), project-specific MCP `.mcp.json` scaffolding, and the macOS notification hook. Deleted the orphaned `configs/gemini-infra.md` and `configs/codex-infra.md`.

### Deprecated

- **session** (1.6.1): superseded by **rosemary**. Retained only for environments still on `@modelcontextprotocol/server-memory`; new projects should use `/rosemary`.

## [2.2.0] - earlier

### Added

- **rosemary** (1.0.0): CLI-native session management as a drop-in alternative to the MCP-based `session` skill; prioritizes shared XDG state with project-local opt-in.

## [2.0.2] - earlier

### Changed

- Removed bundled `.mcp.json` and auto-loaded `mcpServers` to fix a plugin conflict; overhauled the `session` skill and expanded `init-project` infrastructure.

[3.0.0]: https://github.com/azusachino/harus-skills/releases/tag/v3.0.0
[2.3.0]: https://github.com/azusachino/harus-skills/releases/tag/v2.3.0
[2.2.0]: https://github.com/azusachino/harus-skills/releases/tag/v2.2.0
[2.0.2]: https://github.com/azusachino/harus-skills/releases/tag/v2.0.2
