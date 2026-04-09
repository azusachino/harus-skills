---
name: init-project
description: Initialize project with agent infrastructure, documentation structure, and tooling gaps filled
metadata:
  author: haru
  version: 1.2.0
user-invokable: true
disable-auto-invoke: true
---

# Init Project

Initialize the current project with agent infrastructure, documentation, and tooling. Agent-agnostic.

## Phase 1: Scan

Silently collect before asking anything:

- **Language/framework**: file extensions, config files, dependency manifests
- **Build system**: `Makefile`, `Cargo.toml`, `go.mod`, `package.json`, `build.zig`, etc.
- **Existing agent infra**: `AGENTS.md`, `.agents/`, `CLAUDE.md`, `.cursor/`, `.aider/`, `.mcp.json`, `.worktreeinclude`
- **Tooling**:
  - Nix: `flake.nix`, `shell.nix`, `default.nix`, `devenv.nix`, `flake.lock` — preferred
  - Mise: `mise.toml`, `.mise.toml` — fallback when nix absent
  - Formatters, linters, git hooks, CI/CD, editor config
  - Task runner: `Makefile` (primary), `justfile`, `Taskfile.yml`
- **Docs**: `README.md`, `docs/`, existing architecture or design docs
- **Git state**: branch, remotes, recent commits
- **MCP**: check if `search_nodes`, `create_entities`, `add_observations` are in available tools

## Phase 2: Report & Ask

Present scan summary, then ask **one question at a time** for anything not inferable:

1. "What does this project do?" — for AGENTS.md overview
2. "Architecture style?" — monolith / library / CLI / API / microservice
3. "Key coding conventions?" — naming, error handling, testing philosophy
4. "Quality checks that must pass?" — format, lint, test, coverage
5. "Prefer Nix + Makefile for tooling? (Opt-in)" — If yes, generate `flake.nix` and `Makefile`.
6. "Does this project have config management (env files, secrets, migrations) or a release process (tagging, changelogs, CI gates)?" — if yes, generate `rules/config.md` and/or `rules/release.md` in Phase 3.
7. Per tooling gap: "No [tool] found. Want me to add [suggestion]?"

Tool provisioning: if Nix chosen or detected, recommend nix devShell — do not suggest mise alongside it. If neither detected, ask which the user prefers.

**Do not re-scaffold MCPs that are already global.** First check `~/.claude/settings.json` (and `~/.claude.json`) for existing `mcpServers`. Servers already configured there (memory, sequential-thinking, fetch, git, context7, etc.) are available in every project — do not add them to `.mcp.json`.

`.mcp.json` is for **project-specific** servers only: services, credentials, or tools scoped to this repository. Ask only if the project has one of these:

```
Does this project need any project-specific MCP servers in .mcp.json?
(Servers already in ~/.claude/settings.json are available globally — skip those.)

  [ ] github     @modelcontextprotocol/server-github  — if this repo uses GitHub and PAT is project-scoped
  [ ] postgres   (connection string for this project's DB)
  [ ] supabase   @supabase/mcp-server-supabase        — if project uses Supabase
  [ ] sqlite     mcp-server-sqlite                    — if project has a local SQLite DB
  [ ] filesystem @modelcontextprotocol/server-filesystem — if project accesses paths outside the repo

If none apply, skip .mcp.json entirely.
```

Write selected servers to `.mcp.json` in Phase 3.

## Phase 3: Generate Agent Infrastructure

If MCP available, call `read_graph()` first. Merge retrieved facts into generated files:

- `CodingStyle` → `AGENTS.md` Coding Conventions
- `ToolPreferences` → `AGENTS.md` Build/Run/Test
- `UserPreferences` → `.agents/CONTEXT.md` Agent Rules

Ask permission before writing each file. Never overwrite without asking.

After generating files, if MCP is available:

1. Seed the project entity (repo basename, lowercased, hyphens) with key observations so `session start` has meaningful context on first run:
   - Tech stack and architecture style
   - Tool provisioning method (nix devShell / mise / other)
   - Task runner and key make targets
   - Any non-obvious conventions captured during the scan

2. Seed any missing category entities (`UserPreferences`, `CodingStyle`, `ToolPreferences`) using the Global Seed Values defined in the session skill — the session skill is the canonical source for these defaults.

### AGENTS.md

Public project briefing for humans and agents. Sections:

- **Project Overview** — description, purpose
- **Tech Stack & Architecture** — detected stack, structure, key patterns
- **Build, Run & Test** — `make fmt`, `make lint`, `make test`, `make check`, etc. If Nix detected, add: enter dev shell with `nix develop`, or run any tool without entering via `nix develop --command <cmd>`. All daily operations go through `make <target>`.
- **Coding Conventions** — naming, error handling, formatting rules
- **Key Files & Entry Points** — important paths for quick orientation
- **Quality Standards** — required checks before commit/merge

### .agents/CONTEXT.md

Fallback doc — read at session start only when MCP is unavailable. When MCP is active, project context comes from the MCP project entity instead. Still generate this file at init so projects work without MCP.

Sections:

- **Agent Rules** — hard DO/DON'T for this project:
  - DO: Use `make <target>` for all task execution
  - DO: At session start, load MCP entities if available; skip `CURRENT_TASK.md` and `CONTEXT.md` when MCP active
  - DO: At session end, write state to `[project]:session` MCP entity; save conventions to project entity — do not write local files when MCP active
  - DO: Dispatch sub-agents for independent parallel tasks by default — don't run them sequentially when they can be parallelized
  - DON'T: Commit without user confirmation
  - DON'T: Use plan mode for small, well-scoped tasks — plan only for complex multi-step features
  - DON'T: Install tools globally (pip install, npm install -g, cargo install) — use nix devShell or `make <target>` instead (if nix detected)
- **Project Context** — non-obvious patterns, technical notes, agent-only instructions
- **Tool Provisioning** — how tools are obtained. If nix:
  - Enter dev shell: `nix develop`
  - One-off command: `nix develop --command <cmd>` (or just `make <target>`, which handles this automatically via NIX_RUN)
  - Never install tools outside the flake — add them to `devShells.default.packages` instead

### .agents/CURRENT_TASK.md (fallback only)

Seed with initial DONE state. This file is used only when MCP is unavailable. Add it to `.gitignore`.

Fields: `Objective`, `Status`, `Completed Steps`, `Remaining Steps`, `Next Action`, `Last Updated`.

### .agents/MEMORY.md (fallback only)

Seed with empty decision log header. Used only when MCP is unavailable. Add to `.gitignore`.

### `.claude/` directory

Load `configs/claude-infra.md` for all templates below. Ask permission once for the whole group before writing.

#### CLAUDE.md (root)

Generate if not already present. Keep minimal — `AGENTS.md` is the single source of truth:

```markdown
@AGENTS.md

## Rules

- See `.claude/rules/core.md` for agent DO/DON'T rules
[- See `.claude/rules/config.md` for config management rules  # only if config.md generated]
[- See `.claude/rules/release.md` for release process rules   # only if release.md generated]
```

Never overwrite an existing CLAUDE.md — offer to merge instead.

#### `.claude/rules/core.md`

Always generate. Contains hard DO/DON'T rules for all agents. Use the template from `configs/claude-infra.md`, adapting the tool provisioning section to the detected stack (nix/mise/other).

Rules without `paths:` frontmatter load at every session start (like CLAUDE.md). Rules with `paths:` frontmatter load only when Claude reads a file matching those globs — use this for topic-scoped conventions.

#### `.claude/rules/config.md`

Generate only if user confirmed config management in Phase 2.

#### `.claude/rules/release.md`

Generate only if user confirmed a release process in Phase 2.

#### `.claude/rules/testing.md` (optional, path-scoped)

Offer if a test directory or test file pattern is detected. Use `paths:` frontmatter so it only loads when Claude touches test files:

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

Do NOT generate any `.claude/agents/` files. Global agents (`haiku-developer`, `gemini-developer`, `codex-developer`, `dispatch-debugger`, `repo-scout`) are managed in `~/.claude/agents/` via home-manager and apply to every project automatically.

#### `.claude/commands/help.md`

Offer optionally: "Want a `/help` slash command stub?" Generate if accepted.

#### `.claude/settings.json`

Scaffold with permissions and hooks. Ask permission before writing. Adapt `allow` list to detected task runner and tooling.

```json
{
  "permissions": {
    "allow": [
      "Bash(make *)",
      "Bash(git log *)",
      "Bash(git diff *)",
      "Bash(git status *)"
    ],
    "deny": [
      "Bash(rm -rf *)"
    ]
  }
}
```

If Nix detected, add `"Bash(nix develop *)"` to the allow list.

Always include the `block-no-verify` hook — it is lightweight and protects git hooks on every project:

```json
"hooks": {
  "PreToolUse": [{
    "matcher": "Bash",
    "hooks": [{ "type": "command", "command": "npx -y block-no-verify" }],
    "description": "Block --no-verify flag to protect pre-commit/commit-msg/pre-push hooks"
  }]
}
```

Use `npx -y block-no-verify` (no version pin) — npm caches the resolved version, so repeated invocations are fast. A pinned version silently becomes stale and adds cold-cache latency on every Bash tool call.

If OS is macOS (detected via `uname` = `Darwin` in Phase 1), also offer a desktop notification hook:

```json
"Stop": [{
  "matcher": "*",
  "hooks": [{ "type": "command", "command": "bash -c 'command -v osascript >/dev/null && osascript -e '\"'\"'display notification \"Claude finished\" with title \"Claude Code\"'\"'\"''", "async": true, "timeout": 5 }],
  "description": "macOS desktop notification when Claude finishes a response"
}]
```

The `command -v osascript` guard ensures it degrades silently if run on Linux/WSL. Do not scaffold this hook unconditionally — only offer it when macOS is confirmed.

If a formatter is detected (prettier, ruff, taplo, etc.), also offer a `PostToolUse` hook scoped to the edited file path. Use this template, adapting the formatter command:

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

Scope to the specific file path (`tool_input.file_path`) — never run the formatter on the whole project on every edit, as this causes unexpected diffs and performance regression.

Do not put MCP config here — MCP goes in `.mcp.json` at the project root.

Note: tell the user they can create `.claude/settings.local.json` (gitignored automatically) for personal permission overrides on top of this shared config.

#### `.worktreeinclude`

Generate at the project root (not inside `.claude/`). Lists gitignored files that Claude should copy into new worktrees when using `isolation: worktree` or the `EnterWorktree` tool. Uses `.gitignore` syntax.

Cross-reference the project's `.gitignore` during Phase 1 to find actual ignored files that exist locally (`.env`, `.envrc`, `secrets.yaml`, `config/credentials.*`, etc.) and pre-populate real entries — not stubs. Fall back to the common template only when no gitignored dev files are found:

```text
# Local environment — copied into every new worktree
.env
.env.local

# Add project-specific gitignored secrets/config here
```

Ask permission before writing.

#### Gemini bootstrap

Load `configs/gemini-infra.md` for templates. Generate:

- `GEMINI.md` — extracted from `AGENTS.md`, under 80 lines
- `.gemini/system.md` — copy from `~/.gemini/system.md` if it exists; scaffold from template if not
- `.gemini/settings.json` — only if project-specific MCP servers were selected in Phase 2

#### Codex bootstrap

Load `configs/codex-infra.md` for requirements. Codex reads `AGENTS.md` natively — verify it meets the Codex requirements in the config. Generate `CODEX.md` only for monorepos. Generate `.codex-plugin/plugin.json` only for skill/plugin repos.

### .gitignore additions

Add to `.gitignore` (or `.agents/.gitignore`):

```gitignore
.agents/CURRENT_TASK.md
.agents/CONTEXT.md
.agents/MEMORY.md
```

All three are session-volatile MCP fallbacks — keeping them tracked creates git noise.

### MCP server config (if user accepted)

Write to each detected agent config, skipping any that already have the server configured.

**Claude Code** — write to `.mcp.json` at project root (team-shared, committed). Only include servers the user selected; omit any already configured globally. Use `${ENV_VAR}` references for secrets — never hardcode values. Example for a project using GitHub + Postgres:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}" }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "${DATABASE_URL}"]
    }
  }
}
```

If no project-specific servers were selected, **skip `.mcp.json` entirely** — do not create an empty file.

**Gemini CLI** — write to `.gemini/settings.json` (same `mcpServers` structure). Note: verify whether Gemini CLI gitignores this file by default — if so, inform the user it will not be shared with teammates automatically.
**Codex** — Codex reads `AGENTS.md` natively; no separate MCP config file needed. Skip Codex MCP scaffolding.

Default to `.mcp.json` if no agent config detected. Do NOT write MCP config into `.claude/settings.json` — that file is for permissions and hooks only.

## Phase 4: Generate Documentation

Ask permission, then create `docs/` files. Populate from scan; leave `[TODO]` only for genuinely unknown sections.

- **docs/architecture.md** — system overview, project structure tree, module map, data flow, dependencies
- **docs/setup.md** — prerequisites, install, build, run, test commands
- **docs/plan.md** — current phase, roadmap milestones, completed items
- **docs/todo.md** — in progress, blocked, done tasks

Skip docs that already exist unless user asks to regenerate.

## Phase 5: Fill Tooling Gaps

For each gap found in Phase 1, offer to create the config. Ask permission individually.

Tool provisioning priority:

1. **Nix + Makefile** — preferred; tools come from `flake.nix`, tasks from `Makefile`.
2. **Mise** — only if Nix absent or declined, and no other manager detected.
3. **Makefile** — always generate; include `fmt`, `lint`, `test`, `check` targets.

Reference configs: read `CONFIGS.md` (same directory) for the index, then load only `configs/common.md` and the relevant language file. Read on demand — do not preload all configs.

When generating the `Makefile` for a Nix project, use a fallback wrapper to ensure commands work outside the dev shell:

```makefile
NIX_RUN := $(if $(IN_NIX_SHELL),,nix develop --command )
# $(IN_NIX_SHELL) is non-empty inside the shell, empty outside.
# $(if var, true, false): if inside shell → empty prefix (run directly);
#                          if outside shell → prefix with "nix develop --command "
# Then use: $(NIX_RUN)<cmd>  (no space before cmd when NIX_RUN is empty)
```

## Phase 6: Summary

Print a concise list of everything created, followed by the session workflow reminder:

```text
Init complete:
  AGENTS.md                          ← single source of truth for all agents
  CLAUDE.md                          ← @AGENTS.md + .claude/rules refs only
  .mcp.json                          ← project-specific MCP servers only (omit if none needed)
  .worktreeinclude                   ← gitignored files copied into worktrees
  .claude/settings.json              ← permissions + hooks (no MCP here)
  .claude/rules/core.md [+ config.md, release.md, testing.md if applicable]
  .claude/commands/help.md [if accepted]
  GEMINI.md                          ← generated from AGENTS.md (Gemini context)
  .gemini/system.md                  ← executor behavior (copied or scaffolded)
  .gemini/settings.json              ← project-specific MCP servers for Gemini (if any)
  CODEX.md                           ← monorepo only; .codex-plugin/plugin.json for skill repos only
  .agents/CONTEXT.md, .agents/CURRENT_TASK.md, .agents/MEMORY.md  ← MCP fallback only
  .gitignore (updated)
  docs/architecture.md, docs/setup.md, docs/plan.md, docs/todo.md
  Makefile, [other tooling configs]

Personal overrides: create .claude/settings.local.json (auto-gitignored) for
permissions that apply only to your machine.

Global agents (haiku-developer, gemini-developer, codex-developer,
dispatch-debugger, repo-scout) apply automatically — no per-project setup.

Next: run `/session start` at the beginning of each future work session.
      run `/session end` before wrapping up to save state.
```

## Rules

- **Never overwrite** existing files without asking (merge, replace, or skip).
- **Ask permission** before writing each group of files.
- **Populate from scan** — don't leave TODO when the info is available.
- **Make is the task runner** — reference `make <target>` everywhere. No mise task references.
- **Nix-first** — if nix detected, all tool references point to nix.
- **Token efficiency** — if a script runs without error, don't read its output.
- **Language-aware** — adapt all templates to the detected language/ecosystem.
