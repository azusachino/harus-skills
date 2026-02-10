# Common Configs

Configs used regardless of language. Always read this file first.

## Editor Config

Create `.editorconfig` if missing. Only include sections relevant to the detected language(s).

```ini
root = true

[*]
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
charset = utf-8
indent_style = space
indent_size = 4

[*.{json,yaml,yml,toml,xml}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab

# Shell
[*.{sh,bash,zsh}]
indent_size = 2
```

## Prettier

`.prettierrc.json`:

```json
{
  "proseWrap": "always",
  "printWidth": 300,
  "tabWidth": 2,
  "useTabs": false,
  "singleQuote": false,
  "trailingComma": "none",
  "endOfLine": "lf"
}
```

`.prettierignore`:

```text
node_modules/
dist/
build/
coverage/
.agents/
.claude/
.cursor/
.aider/
*.min.js
*.min.css
```

Add language-specific ignores (e.g. `*.zig`, `target/`, `__pycache__/`).

## Markdownlint

**always use markdownlint-cli to format markdown files**, if user already configured prettier, suggest tool switch.

`.markdownlint.json`:

```json
{
  "default": true,
  "MD010": { "code_blocks": false },
  "MD013": false,
  "MD033": false,
  "MD041": false,
  "MD024": { "siblings_only": true }
}
```

`.markdownlintignore`:

```text
node_modules/
dist/
build/
CHANGELOG.md
```

## CI: GitHub Actions (generic with mise)

`.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: jdx/mise-action@v2
      - run: mise run check
```

## Git Hooks

Offer to create a pre-commit hook. If the project uses mise, use `mise run`:

`.git/hooks/pre-commit` (or via lefthook/husky):

```bash
#!/usr/bin/env bash
set -euo pipefail

# Format staged files
mise run fmt

# Re-add formatted files
git diff --cached --name-only --diff-filter=ACM | xargs git add
```

If not using mise, use language-native commands directly.

## .gitignore (common base)

Suggest missing entries for the detected language. Common base:

```gitignore
# OS
.DS_Store
Thumbs.db

# Editors
.vscode/
.idea/
*.swp
*.swo

# Agent infrastructure (keep tracked but ignore generated state)
.agents/*.log

# Environment
.env
.env.local
.env.*.local
```
