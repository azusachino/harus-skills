# AGENTS

## Project Overview

A collection of custom Claude Code skills for productivity and learning. Skills are user-invocable commands that extend Claude Code's capabilities, following the Agent Skills Standard (agentskills.io). Published as a Claude plugin marketplace at `azusachino/harus-skills`.

## Architecture

```text
harus-skills/
  skills/                        # Skill definitions (SKILL.md + optional README)
    daily-language-lesson/       # Language lesson generator (en/ja/es)
    mkmr/                        # Merge request creation helper
    init-project/                # Project initialization (this skill)
  docs/                          # Project documentation
    plans/                       # Design documents
  lessons/                       # Generated lesson output (gitignored)
  .claude-plugin/
    marketplace.json             # Plugin marketplace registration
```

Each skill is a directory containing a `SKILL.md` with YAML frontmatter (name, description, metadata, allowed-tools) and a markdown body with execution instructions for Claude.

### Plugin Structure

- **Marketplace**: `harus-skills`
- **Plugin**: `harus-skills` (all skills in one plugin)
- Skills invoked via `/skill-name` or `/harus-skills:skill-name`

## Build & Run

No compilation. This is a content repository managed with mise.

```bash
mise install          # Install tools (prettier, markdownlint-cli2, taplo, shfmt)
mise run dev          # Setup dev environment + git hooks
mise fmt              # Format all files
mise lint             # Lint markdown
mise check            # Run all checks (format + lint + verify)
mise list-skills      # List available skills
mise verify           # Verify repo structure
mise clean            # Remove generated lessons
```

## Conventions

- Skill files use YAML frontmatter + markdown body
- Prettier for md/json/yaml (prose wrap always, printWidth 500, 2-space indent)
- Taplo for TOML formatting
- shfmt for shell scripts (2-space indent)
- markdownlint-cli2 for markdown linting
- No emojis in git commit messages
- Conventional commit style (`feat:`, `fix:`, `docs:`, etc.)
- Always run `mise fmt` before committing
- Ask user permission before executing destructive operations in skills

## Key Files

| File                              | Purpose                                      |
| --------------------------------- | -------------------------------------------- |
| `CLAUDE.md`                       | Claude Code project instructions             |
| `.claude-plugin/marketplace.json` | Plugin marketplace config                    |
| `mise.toml`                       | Task runner and tool management              |
| `.prettierrc.json`                | Prettier formatter config                    |
| `.markdownlint.json`              | Markdown linter config                       |
| `.gitignore`                      | Ignored files (lessons/, editor files, etc.) |

## Quality Standards

1. `mise fmt` - all files formatted
2. `mise lint` - markdown lint passes
3. `mise verify` - repo structure valid (all skills have SKILL.md, marketplace.json exists)
