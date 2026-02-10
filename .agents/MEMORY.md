# Agent Memory

## Personal Defaults

- Use mise for task running
- Prefer prettier for markdown/json/yaml formatting
- No emojis in git commit messages
- Prose wrap at 200 characters for readability
- 2-space indentation for config files (JSON, YAML, TOML)
- Always ask before committing or pushing
- Format and lint before every commit
- Run checks before creating PRs/MRs
- Keep solutions simple - avoid over-engineering

## Project Patterns

- Skills follow Agent Skills Standard with `SKILL.md` format
- YAML frontmatter contains metadata; markdown body contains instructions
- Plugin system via `.claude-plugin/marketplace.json`
- Generated content (lessons/) is gitignored
- mise.toml defines all dev tasks (fmt, lint, check, verify, clean)
- Prettier config: printWidth 500, proseWrap always, 2-space tabs, LF endings
- markdownlint config: MD013 (line length) disabled, MD033 (inline HTML) disabled

## Decisions

## Debugging Notes
