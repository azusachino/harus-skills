# AGENTS

## Project Overview

A collection of custom agent skills for productivity and learning, compatible with [Claude Code](https://claude.ai/code) and [Gemini CLI](https://geminicli.com). Skills are user-invocable commands that extend agent capabilities, following the [Agent Skills Standard](http://agentskills.io). Published as a Claude plugin marketplace at `azusachino/harus-skills` and a Gemini CLI extension.

## Architecture

```text
harus-skills/
  skills/                        # Skill definitions (SKILL.md + optional README)
    daily-language-lesson/       # Language lesson generator (en/ja/es)
    mkmr/                        # Merge request creation helper
    init-project/                # Project initialization (this skill)
    session/                     # Session and memory management (three-tier protocol)
  docs/                          # Project documentation
    plans/                       # Design documents
  lessons/                       # Generated lesson output (gitignored)
  .claude-plugin/
    marketplace.json             # Plugin marketplace registration
  gemini-extension.json          # Gemini CLI extension manifest
```

Each skill is a directory containing a `SKILL.md` with YAML frontmatter (name, description, metadata, allowed-tools) and a markdown body with execution instructions for Claude.

### Plugin Structure

- **Marketplace**: `harus-skills`
- **Plugin**: `harus-skills` (all skills in one plugin)
- Skills invoked via `/skill-name` or `/harus-skills:skill-name`

## Build & Run

No compilation. This is a content repository managed with mise (tools) and Makefile (tasks).

```bash
make install          # Install tools via mise
make dev              # Setup dev environment + git hooks
make fmt              # Format all files
make lint             # Lint markdown and Python files
make check            # Run all checks (format + lint + verify)
make list-skills      # List available skills
make verify           # Verify repo structure
make clean            # Remove generated lessons
```

## Conventions

- Skill files use YAML frontmatter + markdown body
- Prettier for md/json/yaml (prose wrap always, printWidth 500, 2-space indent)
- Taplo for TOML formatting
- shfmt for shell scripts (2-space indent)
- markdownlint-cli2 for markdown linting
- ruff for Python formatting and linting
- No emojis in git commit messages
- Conventional commit style (`feat:`, `fix:`, `docs:`, etc.)
- Always run `make fmt` before committing
- Ask user permission before executing destructive operations in skills

## Key Files

| File                              | Purpose                                      |
| --------------------------------- | -------------------------------------------- |
| `CLAUDE.md`                       | Claude Code project instructions             |
| `.agents/`                        | Project-local session & task memory          |
| `~/.agents/`                      | Global agent memory (preferences, facts)     |
| `.claude-plugin/marketplace.json` | Plugin marketplace config                    |
| `mise.toml`                       | Task runner and tool management              |
| `.prettierrc.json`                | Prettier formatter config                    |
| `.markdownlint.json`              | Markdown linter config                       |
| `.gitignore`                      | Ignored files (lessons/, editor files, etc.) |

## Quality Standards

1. `mise fmt` - all files formatted
2. `mise lint` - markdown lint passes
3. `mise verify` - repo structure valid (all skills have SKILL.md, marketplace.json exists)
