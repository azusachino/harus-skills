# Tooling Reference Configs

Configs are split by language to reduce token usage. Read only the files relevant to the detected project.

## Always read first

- `configs/common.md` - editorconfig, prettier, CI (nix-native), git hooks, gitignore base
- `configs/claude-infra.md` - `.claude/` directory templates (rules, commands, CLAUDE.md)
- `configs/gemini-infra.md` - `GEMINI.md`, `.gemini/system.md`, `.gemini/settings.json`
- `configs/codex-infra.md` - `AGENTS.md` requirements for Codex, CODEX.md (monorepo), plugin.json (skill repos only)

## Then read the language-specific file

- `configs/zig.md`
- `configs/rust.md`
- `configs/go.md`
- `configs/node.md` - JavaScript / TypeScript
- `configs/python.md`
- `configs/java.md` - Gradle and Maven

For multi-language projects, read multiple language files.
