# Contributing to harus-skills

## Development Workflow

1. **Setup**: Run `nix develop` (or `mise install`) to enter the development environment.
2. **Checks**: Run `make check` before committing.
3. **Tests**: Run `make test` for Python logic.
4. **Versioning**: Use `make bump-version VERSION=x.y.z` to synchronize versions across all manifests.

## Conventions

- **Commits**: Follow Conventional Commits (`feat:`, `fix:`, `chore:`, etc.).
- **Formatting**: JSON, YAML, TOML, and Python are auto-formatted by `make fmt`.
- **Markdown**: Do NOT format markdown files manually; prose is left as-is.
- **Skills**: Each skill must have a `SKILL.md` with YAML frontmatter.
