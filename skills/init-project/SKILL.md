---
name: init-project
description: Initialize project with agent infrastructure, documentation structure, and tooling gaps filled
metadata:
  author: haru
  version: 2.0.0
user-invokable: true
disable-auto-invoke: true
---

# Init Project

Initialize the current project with agent infrastructure, documentation, and tooling. Stack assumption: **asobi** (memory), **mise** (tools), **make** (commands). Nix is supported as an opt-in for repos that already use it.

## Table of Contents
- [Phase 1: Scan](#phase-1-scan)
- [Phase 2: Report & Ask](#phase-2-report--ask)
- [Phase 3: Generate Agent Infrastructure](#phase-3-generate-agent-infrastructure)
- [Phase 4: Generate Documentation](#phase-4-generate-documentation)
- [Phase 5: Fill Tooling Gaps](#phase-5-fill-tooling-gaps)
- [Phase 6: Summary](#phase-6-summary)
- [Rules](#rules)

## Phase 1: Scan

Silently collect before asking anything:

- **Language/framework**: file extensions, config files, dependency manifests
- **Build system**: `Makefile`, `Cargo.toml`, `go.mod`, `package.json`, `build.zig`, etc.
- **Existing agent infra**: `CLAUDE.md`, `.claude/`, `asobi.toml`
- **Tooling**:
  - Mise: `mise.toml`, `.mise.toml` — primary tool source
  - Nix: `flake.nix`, `shell.nix`, `default.nix`, `flake.lock` — optional, only when already present
  - Formatters, linters, git hooks, CI/CD, editor config
  - Task runner: `Makefile` (primary), `justfile`, `Taskfile.yml`
- **Memory**: run `command -v asobi` — the memory store, seeded in Phase 3 (no file fallback)
- **Docs**: `README.md`, `docs/`, existing architecture or design docs
- **Git state**: branch, remotes, recent commits

## Phase 2: Report & Ask

Present scan summary, then ask **one question at a time** for anything not inferable:

1. "What does this project do?" — for CLAUDE.md overview
2. "Architecture style?" — monolith / library / CLI / API / microservice
3. "Key coding conventions?" — naming, error handling, testing philosophy
4. "Quality checks that must pass?" — format, lint, test, coverage
5. "Tooling: mise (default) or nix?" — default to mise + Makefile. Choose nix only if `flake.nix` is already present or the user asks; then generate `flake.nix` + the NIX_RUN Makefile wrapper.
6. "Does this project have config management (env files, secrets, migrations) or a release process (tagging, changelogs, CI gates)?" — if yes, generate `rules/config.md` and/or `rules/release.md` in Phase 3.
7. Per tooling gap: "No [tool] found. Want me to add [suggestion]?"

## Phase 3: Generate Agent Infrastructure

If `asobi` is available, load the global preference entities first to dynamically customize generated files rather than relying on static templates.
Run:
```bash
asobi show UserPreferences CodingStyle ToolPreferences
```
Map and merge the retrieved observations:
- `CodingStyle` observations $\rightarrow$ `CLAUDE.md` Coding Conventions
- `ToolPreferences` observations $\rightarrow$ `CLAUDE.md` Build/Run/Test
- `UserPreferences` observations $\rightarrow$ `.claude/rules/core.md` Agent Rules

Ask permission before writing each file. Never overwrite without asking.

After generating files, if `asobi` is available, seed the graph so `/asobi start` has context on first run:

1. Project entity (repo basename): `asobi new "[repo-basename]" "project"` then `obs` for tech stack + architecture, tool provisioning method (mise / nix), task runner + key make targets, and any non-obvious conventions from the scan.
2. Missing category entities (`UserPreferences`, `CodingStyle`, `ToolPreferences`): seed from the **Global Seed Values in the asobi skill** — it is the canonical source for these defaults.

### `.claude/` directory

Load `configs/claude-infra.md` for templates. Ask permission once for the whole group before writing.

#### CLAUDE.md (root)

The single source of truth for all agents. Generate if not already present; never overwrite an existing CLAUDE.md — offer to merge instead. Sections:

- **Project Overview** — description, purpose
- **Tech Stack & Architecture** — detected stack, structure, key patterns
- **Build, Run & Test** — `make fmt`, `make lint`, `make test`, `make check`, etc. All daily operations go through `make <target>`. Tools come from mise (`mise install` to provision). If nix was chosen: enter the shell with `nix develop`, or run a one-off via `nix develop --command <cmd>`.
- **Coding Conventions** — naming, error handling, formatting rules
- **Key Files & Entry Points** — important paths for quick orientation
- **Quality Standards** — required checks before commit/merge

Close with a Rules pointer:

```markdown
## Rules

- See `.claude/rules/core.md` for agent DO/DON'T rules
[- See `.claude/rules/config.md` for config management rules  # only if config.md generated]
[- See `.claude/rules/release.md` for release process rules   # only if release.md generated]
```

#### `.claude/rules/core.md`

Always generate. Hard DO/DON'T rules for all agents. Use the template from `configs/claude-infra.md`, adapting the tool-provisioning section to the chosen stack (mise / nix).

Rules without `paths:` frontmatter load every session start. Rules with `paths:` frontmatter load only when Claude reads a matching file — use this for topic-scoped conventions.

#### `.claude/rules/config.md` / `release.md`

Generate only if the user confirmed config management / a release process in Phase 2.

#### `.claude/rules/testing.md` (optional, path-scoped)

Offer if a test directory or pattern is detected. Use `paths:` frontmatter so it loads only on test files:

```markdown
---
paths:
  - "**/*.test.*"
  - "**/*_test.*"
  - "test/**"
  - "tests/**"
---

# Testing conventions

[project-specific testing rules]
```

#### `.claude/agents/` — skip

Do NOT generate `.claude/agents/` files. Global agents (`haiku-developer`, `gemini-developer`, `codex-developer`, `dispatch-debugger`, `repo-scout`) live in `~/.claude/agents/` and apply to every project.

#### `.claude/commands/help.md`

Offer optionally: "Want a `/help` slash command stub?" Generate if accepted.

#### `.claude/settings.json`

Scaffold permissions + hooks. Ask permission before writing. Adapt `allow` to the detected task runner and tooling:

```json
{
  "permissions": {
    "allow": ["Bash(make *)", "Bash(mise *)", "Bash(git log *)", "Bash(git diff *)", "Bash(git status *)"],
    "deny": ["Bash(rm -rf *)"]
  }
}
```

If nix was chosen, add `"Bash(nix develop *)"` to the allow list.

Always include the `block-no-verify` hook — lightweight, protects git hooks on every project:

```json
"hooks": {
  "PreToolUse": [{
    "matcher": "Bash",
    "hooks": [{ "type": "command", "command": "npx -y block-no-verify" }],
    "description": "Block --no-verify flag to protect pre-commit/commit-msg/pre-push hooks"
  }]
}
```

Use `npx -y block-no-verify` (no version pin) — npm caches the resolved version, so repeat invocations are fast; a pin silently goes stale and adds cold-cache latency on every Bash call.

If a formatter is detected (prettier, ruff, taplo, etc.), offer a `PostToolUse` hook scoped to the edited file:

```json
"PostToolUse": [{
  "matcher": "Edit|Write",
  "hooks": [{
    "type": "command",
    "command": "jq -r '.tool_input.file_path // empty' | xargs -I{} prettier --write {} 2>/dev/null || true"
  }],
  "description": "Auto-format file after each edit (prettier)"
}]
```

Scope to `tool_input.file_path` — never run the formatter on the whole project per edit. Do not put MCP config here. Tell the user they can create `.claude/settings.local.json` (auto-gitignored) for personal permission overrides.

#### `.worktreeinclude`

Generate at the project root. Lists gitignored files Claude copies into new worktrees (`isolation: worktree` / `EnterWorktree`). Uses `.gitignore` syntax.

Cross-reference `.gitignore` from Phase 1 to pre-populate real entries (`.env`, `.envrc`, `secrets.yaml`, etc.) — not stubs. Fall back to the template only when no gitignored dev files exist:

```text
# Local environment — copied into every new worktree
.env
.env.local

# Add project-specific gitignored secrets/config here
```

Ask permission before writing.

### .gitignore additions

Nothing session-volatile to ignore by default — asobi state lives in the global XDG graph. Only if the user opted into a project-local graph (`asobi init --local`), add `.asobi/` to `.gitignore`.

## Phase 4: Generate Documentation

Ask permission, then create `docs/` files. Populate from scan; leave `[TODO]` only for genuinely unknown sections.

- **docs/architecture.md** — system overview, project structure tree, module map, data flow, dependencies
- **docs/setup.md** — prerequisites, install, build, run, test commands
- **docs/plan.md** — current phase, roadmap milestones, completed items
- **docs/todo.md** — in progress, blocked, done tasks

Skip docs that already exist unless the user asks to regenerate.

## Phase 5: Fill Tooling Gaps

For each gap from Phase 1, offer to create the config. Ask permission individually.

Tool provisioning priority:

1. **Mise + Makefile** — default; tools from `mise.toml`, tasks from `Makefile`.
2. **Nix + Makefile** — only when `flake.nix` is already present or the user chose nix; tools from the flake.
3. **Makefile** — always generate; include `fmt`, `lint`, `test`, `check` targets.

Reference configs: read `CONFIGS.md` (same directory) for the index, then load only `configs/common.md` and the relevant language file. Read on demand — do not preload all configs.

When generating the `Makefile` for a **nix** project, use a fallback wrapper so commands work outside the dev shell:

```makefile
NIX_RUN := $(if $(IN_NIX_SHELL),,nix develop --command )
# Inside the shell IN_NIX_SHELL is non-empty → empty prefix (run directly).
# Outside → prefix with "nix develop --command ". Use: $(NIX_RUN)<cmd>
```

For a **mise** project no wrapper is needed — `make` targets call tools directly (mise shims them onto `$PATH`).

## Phase 6: Summary

Print a concise list of everything created, then the session reminder:

```text
Init complete:
  CLAUDE.md                          ← single source of truth for all agents
  .worktreeinclude                   ← gitignored files copied into worktrees
  .claude/settings.json              ← permissions + hooks
  .claude/rules/core.md [+ config.md, release.md, testing.md if applicable]
  .claude/commands/help.md [if accepted]
  .gitignore (updated, if project-local asobi)
  docs/architecture.md, docs/setup.md, docs/plan.md, docs/todo.md
  Makefile, mise.toml [+ flake.nix if nix], [other tooling configs]

Personal overrides: create .claude/settings.local.json (auto-gitignored).
Global agents (haiku-developer, gemini-developer, codex-developer,
dispatch-debugger, repo-scout) apply automatically — no per-project setup.

Next: run `/asobi start` at the start of each work session,
      run `/asobi end` before wrapping up to save state.
```

## Rules

- **Never overwrite** existing files without asking (merge, replace, or skip).
- **Ask permission** before writing each group of files.
- **Populate from scan** — don't leave TODO when the info is available.
- **Make is the task runner** — reference `make <target>` everywhere. No mise *task* references (mise provides tools, make runs commands).
- **Mise-first** — tools come from mise; use nix only when the repo already has a flake or the user chose it.
- **Asobi for memory** — seed and read the asobi graph; it is required and has no file fallback.
- **Token efficiency** — if a script runs without error, don't read its output.
- **Language-aware** — adapt all templates to the detected language/ecosystem.
