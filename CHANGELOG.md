# Changelog

All notable changes to this project are documented here. The version tracks the plugin/marketplace version in `.claude-plugin/marketplace.json`; individual skills carry their own `metadata.version`.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.2.1] - 2026-07-17

### Changed
- **asobi** (2.4.0): Consolidated current Asobi 0.6.1 guidance around the favored session, task-dispatcher, recall, skill, retention, and recovery workflows; removed duplicated and obsolete instructions.
- **toolbelt** (2.2.0): Added provider-native `gh` and `glab` guidance for repository, PR/MR, release, workflow, and API operations.
- Bumped the universal plugin version to 3.2.1 across all manifests.

## [3.2.0] - 2026-07-12

### Removed
- **init-project** skill dropped entirely (superseded — no longer maintained). Removed from `skills/`, manifests, README, and CLAUDE.md.
- **Stale `docs/`** cleared — the entire pre-asobi legacy tree (`architecture`/`status`/`setup`/`plan`/`todo`/`requirements`/`project-design` + 17 dated `docs/plans/` design archives, all describing the retired `session`/`.agents`/MCP model). The still-true decisions were salvaged into ADRs first.

### Added
- **`docs/adr/`** — Architecture Decision Records capturing the durable, non-obvious choices: pure-markdown skills (0001), single plugin + auto-discovery (0002), Agent Skills Standard with parallel agent manifests (0003).

### Changed
- **asobi** (2.2.0): Updated for the `asobi 0.5.2` CLI API.
  - Added `--json` on mutating commands (skip the follow-up `show`), batched `new`/`link` and `new --obs` seeding, `rm-obs --prefix`.
  - Added `history <name> [key]` (valid-time truth audit trail) and the **Handoff & archival** path: `export --scope`/`import` (portable JSON) and `backup`/`restore` (physical libSQL snapshots).
  - **Preference reversal**: worktrees and sub-agents are now **opt-in** (inline work by default); **emojis are welcome**. Added the `mise x -- <tool>` idiom.
  - **Seed principles curated** — distilled the gist of popular OSS agent skills ([ponytail](https://github.com/DietrichGebert/ponytail), [karpathy-guidelines](https://github.com/multica-ai/andrej-karpathy-skills)) into the core context every agent/session loads, named for recall and deduped:
    - `UserPreferences`: canonical **think-first / stop-and-ask (fail-fast)** rule (toolbelt now points to it) and **goal-driven** (verifiable check, loop until green).
    - `CodingStyle`: **KISS + YAGNI as the lazy ladder** (reuse → stdlib/native → installed dep → one line), **understand-before-you-change** + safety carve-out, **surgical changes**, **bug fix = root cause**, **mark cut corners**, plus **atomic commits / SemVer / Keep a Changelog**.
- **toolbelt** (2.1.0): Reconciled with the actual `harus-config` nix tool set — dropped tools not installed (`yq`, `awscli2`, `ffmpeg`, `unar`, `minikube`-as-installed, `colima`), fixed archives to `ouch`. Added `ast-grep` (structural search/rewrite), `typos` (spell-check), `difftastic` (syntax-aware diffs), and the `mise x -- <tool>` discipline. Emojis welcome.

## [3.1.2] - 2026-07-02

### Changed
- **asobi** (2.1.2): Updated for the `asobi 0.3.0` CLI API, verified against the live binary:
  - Default observation cap raised **50 → 200** (overridable via `ASOBI_OBSERVATION_LIMIT` / `observation_limit`).
  - Documented sequential integer **observation IDs**: `show --with-ids`, atomic `update-obs <name> <id> "…" --id`, and `rm-obs <name> <id> --id`.
  - Added `show --expand <relation_type>` (load an epic + its task children in one payload) to `/asobi start` and `tasks list`.
  - Added `stats --per-entity` to the pruning guidance for finding near-cap entities.
  - Corrected `compact` behavior: it syncs **durable-knowledge entities only** (session/task/skill excluded) and is idempotent.
- **toolbelt** (2.0.2): Dropped `zellij` (haru uses `tmux`); added a **Domain & infra tools** table for the specialised tools harus-nix provisions (k8s, cloud, containers, secrets, lint/format, media); added a **stop-and-ask hard-stop rule** — halt and ask on any ambiguous situation instead of improvising a fallback.

## [3.1.1] - 2026-06-29

### Changed
- Removed stale RTK references across the skills and docs.

## [3.1.0] - 2026-06-24

### Added
- **revise** (1.0.0): New `/revise` skill that persists project lessons, findings, and wrong approaches — positive lessons on the project entity, rejected approaches as active `[project]:pitfall:<slug>` warnings, with a `docs/lessons/` fallback when asobi is unavailable.

### Changed
- **asobi** (2.1.0): Documented the pitfall log and surfaced active pitfalls at `/asobi start` and during task dispatch.

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
