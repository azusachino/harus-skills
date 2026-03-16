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

## Tooling: Nix (flake.nix)

Base template for `flake.nix`:

```nix
{
  description = "Project development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            # Base tools
            nodePackages.prettier
            taplo
            shfmt
          ];
        };
      });
}
```

## CI: GitHub Actions (Nix-native)

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
      - uses: cachix/install-nix-action@v25
      - run: make check
```

## Git Hooks (Nix-native)

`.git/hooks/pre-commit`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Format staged files using make (which uses nix if needed)
make fmt

# Re-add formatted files
git diff --cached --name-only --diff-filter=ACM | xargs git add
```

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
