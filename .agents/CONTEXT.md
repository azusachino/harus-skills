## Agent Rules (Hard DO / DON'T)

- DO: At session start — if MCP available (`search_nodes` in tools), call `read_graph()`, load category entities + `[harus-skills]:session`. Skip `CURRENT_TASK.md` entirely.
- DO: At session end — if MCP available, write state to `[harus-skills]:session` entity (delete old, recreate). Do not write `CURRENT_TASK.md` when MCP is active.
- DO: Update `CONTEXT.md` when project conventions or core behavior changes.
- DO: Use `make <target>` for all task execution (fmt, lint, check, verify).
- DO: Bump `metadata.version` in the skill + `gemini-extension.json` + `.claude-plugin/marketplace.json` in the same commit after any skill edit.
- DON'T: Commit without user confirmation.
- DON'T: Run Prettier on `.md` files — use `markdownlint-cli2` only.
- DON'T: Use `git add -A` or `git add .` — stage files explicitly.

## Project Context (Internal)

- Skills live in `skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`, `metadata.version`).
- Task runner is `make`. Tool provisioning is nix devShell (mise as fallback).
- `CURRENT_TASK.md` and `MEMORY.md` are gitignored — session-volatile, not tracked.
- Version bump rule: every skill edit → bump skill version + both manifest files in same commit.

## Tool Provisioning

Nix devShell (primary). Mise (`mise.toml`) present as fallback if nix unavailable.
