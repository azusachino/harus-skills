# Architecture

## System Overview

harus-skills is a Claude Code plugin marketplace containing reusable skills. Skills are markdown-based instruction files that Claude Code executes as user-invocable commands. No runtime code; the "architecture" is file organization and metadata conventions.

## Project Structure

```text
harus-skills/
  skills/                        # Each subdirectory is one skill
    daily-language-lesson/       # Generates language learning lessons
      SKILL.md                   # Skill definition
      README.md                  # User documentation
    notion-language-lesson/      # Same lessons pushed to Notion
      SKILL.md
      README.md
      scripts/                   # nll-push.py, nll-status.py
    init-project/                # Project initialization
      SKILL.md
      CONFIGS.md                 # Reference configs for tooling setup
    session/                     # MCP-primary session management
      SKILL.md
  docs/                          # Project documentation
    plans/                       # Design documents and proposals
  lessons/                       # Generated output (gitignored)
  .claude-plugin/
    marketplace.json             # Plugin registry
  .agents/                       # Agent infrastructure
    CONTEXT.md                   # Living project context (always read)
```

## Module Map

| Skill                  | Purpose                      | Invocation                 |
| ---------------------- | ---------------------------- | -------------------------- |
| daily-language-lesson  | Generate en/ja/es lessons    | `/lesson`, `/dll`          |
| notion-language-lesson | Same lessons → Notion DB     | `/nll`                     |
| init-project           | Initialize project infra     | `/init-project`, `/init`   |
| session                | Session state + memory mgmt  | `/session`                 |

## Data Flow

1. User invokes a skill via `/command`
2. Claude Code reads the skill's `SKILL.md`
3. YAML frontmatter configures metadata and tool restrictions
4. Markdown body provides execution instructions
5. Claude follows instructions, interacting with user and filesystem

## Dependencies

- **nix**: Tool provisioning via devShell (mise as fallback)
- **make**: Task runner (`fmt`, `lint`, `check`, `verify`)
- **prettier**: JSON/YAML formatter
- **markdownlint-cli2**: Markdown linter
- **taplo**: TOML formatter
- **ruff**: Python linter/formatter
