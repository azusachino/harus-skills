# Tooling Reference Configs

Reference configurations for the `init-project` skill. Read the relevant sections based on the detected language when filling tooling gaps.

## 1. Editor Config

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

# Zig
[*.zig]
indent_size = 4

# Rust
[*.rs]
indent_size = 4

# Go
[*.go]
indent_style = tab
indent_size = 4

# JavaScript/TypeScript
[*.{js,jsx,ts,tsx,mjs,cjs}]
indent_size = 2

# Python
[*.py]
indent_size = 4

# Java/Kotlin
[*.{java,kt,kts}]
indent_size = 4

# C/C++
[*.{c,h,cpp,hpp,cc}]
indent_size = 4

# Shell
[*.{sh,bash,zsh}]
indent_size = 2
```

---

## 2. Formatter Configs

### Prettier (JS/TS, markdown, JSON, YAML, CSS, HTML)

`.prettierrc.json`:

```json
{
  "proseWrap": "always",
  "printWidth": 500,
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

### Rustfmt (Rust)

`rustfmt.toml`:

```toml
edition = "2021"
max_width = 100
tab_spaces = 4
use_field_init_shorthand = true
use_try_shorthand = true
imports_granularity = "Crate"
group_imports = "StdExternalCrate"
```

### clang-format (C/C++)

`.clang-format`:

```yaml
BasedOnStyle: LLVM
IndentWidth: 4
ColumnLimit: 100
BreakBeforeBraces: Attach
AllowShortFunctionsOnASingleLine: Inline
SortIncludes: CaseInsensitive
IncludeBlocks: Regroup
```

### goimports (Go)

Go uses `gofmt`/`goimports` with no config file needed. Add to mise tasks instead.

---

## 3. Linter Configs

### Clippy (Rust)

`clippy.toml`:

```toml
too-many-arguments-threshold = 7
type-complexity-threshold = 250
```

Cargo.toml lint section (suggest adding if missing):

```toml
[lints.clippy]
pedantic = { level = "warn", priority = -1 }
module_name_repetitions = "allow"
must_use_candidate = "allow"
missing_errors_doc = "allow"
```

### golangci-lint (Go)

`.golangci.yml`:

```yaml
run:
  timeout: 5m

linters:
  enable:
    - errcheck
    - govet
    - staticcheck
    - unused
    - gosimple
    - ineffassign
    - typecheck
    - gofmt
    - goimports
    - misspell
    - unconvert
    - gocritic

linters-settings:
  gocritic:
    enabled-tags:
      - diagnostic
      - style
      - performance
  goimports:
    local-prefixes: [detected-module-path]

issues:
  exclude-use-default: false
  max-issues-per-linter: 0
  max-same-issues: 0
```

### ESLint (JS/TS)

`eslint.config.js` (flat config):

```javascript
import js from "@eslint/js";

export default [
  js.configs.recommended,
  {
    rules: {
      "no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
      "no-console": "warn",
      eqeqeq: "error",
      curly: "error"
    }
  },
  {
    ignores: ["node_modules/", "dist/", "build/", "coverage/"]
  }
];
```

For TypeScript, add `typescript-eslint`:

```javascript
import js from "@eslint/js";
import tseslint from "typescript-eslint";

export default tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    rules: {
      "@typescript-eslint/no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
      "@typescript-eslint/explicit-function-return-type": "off",
      "@typescript-eslint/no-explicit-any": "warn"
    }
  },
  {
    ignores: ["node_modules/", "dist/", "build/", "coverage/"]
  }
);
```

### Ruff (Python)

`ruff.toml`:

```toml
line-length = 100
target-version = "py312"

[lint]
select = [
  "E",   # pycodestyle errors
  "W",   # pycodestyle warnings
  "F",   # pyflakes
  "I",   # isort
  "B",   # flake8-bugbear
  "C4",  # flake8-comprehensions
  "UP",  # pyupgrade
  "SIM", # flake8-simplify
]
ignore = [
  "E501", # line too long (handled by formatter)
]

[lint.isort]
known-first-party = ["[detected-package-name]"]

[format]
quote-style = "double"
indent-style = "space"
```

### Markdownlint (all projects with docs)

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

---

## 4. Task Runner: mise.toml

Use mise to manage tool versions and define project tasks. Each config includes tools, formatting, linting, testing, and a unified `check` task.

### Zig

```toml
[tools]
zig = "0.15"
"npm:prettier" = "latest"
"npm:markdownlint-cli2" = "latest"

[tasks.fmt]
description = "Format all files"
run = """
#!/usr/bin/env bash
set -euo pipefail
zig fmt src/
prettier --write "**/*.{md,json,yaml,yml}"
"""

[tasks.fmt-check]
description = "Check formatting"
run = """
#!/usr/bin/env bash
set -euo pipefail
zig fmt --check src/
prettier --check "**/*.{md,json,yaml,yml}"
"""

[tasks.build]
description = "Build the project"
run = "zig build"

[tasks.test]
description = "Run tests"
run = "zig build test"

[tasks.lint]
description = "Lint markdown files"
run = 'markdownlint-cli2 "**/*.md"'

[tasks.check]
description = "Run all checks"
depends = ["fmt-check", "lint", "build", "test"]
```

### Rust

```toml
[tools]
rust = "stable"
"npm:prettier" = "latest"
"npm:markdownlint-cli2" = "latest"

[tasks.fmt]
description = "Format all files"
run = """
#!/usr/bin/env bash
set -euo pipefail
cargo fmt
prettier --write "**/*.{md,json,yaml,yml}"
"""

[tasks.fmt-check]
description = "Check formatting"
run = """
#!/usr/bin/env bash
set -euo pipefail
cargo fmt -- --check
prettier --check "**/*.{md,json,yaml,yml}"
"""

[tasks.lint]
description = "Lint source files"
run = "cargo clippy -- -D warnings"

[tasks.test]
description = "Run tests"
run = "cargo test"

[tasks.check]
description = "Run all checks"
depends = ["fmt-check", "lint", "test"]
```

### Go

```toml
[tools]
go = "latest"
golangci-lint = "latest"
"npm:prettier" = "latest"
"npm:markdownlint-cli2" = "latest"

[tasks.fmt]
description = "Format all files"
run = """
#!/usr/bin/env bash
set -euo pipefail
goimports -w .
prettier --write "**/*.{md,json,yaml,yml}"
"""

[tasks.fmt-check]
description = "Check formatting"
run = """
#!/usr/bin/env bash
set -euo pipefail
test -z "$(goimports -l .)"
prettier --check "**/*.{md,json,yaml,yml}"
"""

[tasks.lint]
description = "Lint source files"
run = "golangci-lint run ./..."

[tasks.test]
description = "Run tests"
run = "go test ./..."

[tasks.bench]
description = "Run benchmarks"
run = "go test -bench=. -benchmem ./..."

[tasks.check]
description = "Run all checks"
depends = ["fmt-check", "lint", "test"]
```

### Node.js / TypeScript

```toml
[tools]
node = "lts"
"npm:prettier" = "latest"
"npm:eslint" = "latest"
"npm:markdownlint-cli2" = "latest"

[tasks.fmt]
description = "Format all files"
run = "prettier --write ."

[tasks.fmt-check]
description = "Check formatting"
run = "prettier --check ."

[tasks.lint]
description = "Lint source files"
run = "eslint ."

[tasks.lint-fix]
description = "Lint and fix source files"
run = "eslint --fix ."

[tasks.test]
description = "Run tests"
run = "npm test"

[tasks.check]
description = "Run all checks"
depends = ["fmt-check", "lint", "test"]
```

### Python

```toml
[tools]
python = "3.12"
"npm:prettier" = "latest"
"npm:markdownlint-cli2" = "latest"

[tasks.fmt]
description = "Format all files"
run = """
#!/usr/bin/env bash
set -euo pipefail
ruff format .
ruff check --fix .
prettier --write "**/*.{md,json,yaml,yml}"
"""

[tasks.fmt-check]
description = "Check formatting"
run = """
#!/usr/bin/env bash
set -euo pipefail
ruff format --check .
ruff check .
prettier --check "**/*.{md,json,yaml,yml}"
"""

[tasks.lint]
description = "Lint source files"
run = "ruff check ."

[tasks.test]
description = "Run tests"
run = "pytest"

[tasks.test-cov]
description = "Run tests with coverage"
run = "pytest --cov --cov-report=term-missing"

[tasks.check]
description = "Run all checks"
depends = ["fmt-check", "lint", "test"]
```

### Java / Kotlin (Gradle)

```toml
[tools]
java = "21"
"npm:prettier" = "latest"
"npm:markdownlint-cli2" = "latest"

[tasks.fmt]
description = "Format all files"
run = """
#!/usr/bin/env bash
set -euo pipefail
./gradlew spotlessApply
prettier --write "**/*.{md,json,yaml,yml}"
"""

[tasks.fmt-check]
description = "Check formatting"
run = """
#!/usr/bin/env bash
set -euo pipefail
./gradlew spotlessCheck
prettier --check "**/*.{md,json,yaml,yml}"
"""

[tasks.lint]
description = "Lint source files"
run = "./gradlew spotlessCheck"

[tasks.test]
description = "Run tests"
run = "./gradlew test"

[tasks.build]
description = "Build the project"
run = "./gradlew build"

[tasks.check]
description = "Run all checks"
depends = ["fmt-check", "test"]
```

### Java / Kotlin (Maven)

```toml
[tools]
java = "21"
"npm:prettier" = "latest"
"npm:markdownlint-cli2" = "latest"

[tasks.fmt]
description = "Format all files"
run = """
#!/usr/bin/env bash
set -euo pipefail
mvn spotless:apply
prettier --write "**/*.{md,json,yaml,yml}"
"""

[tasks.fmt-check]
description = "Check formatting"
run = """
#!/usr/bin/env bash
set -euo pipefail
mvn spotless:check
prettier --check "**/*.{md,json,yaml,yml}"
"""

[tasks.test]
description = "Run tests"
run = "mvn test"

[tasks.build]
description = "Build the project"
run = "mvn package -DskipTests"

[tasks.check]
description = "Run all checks"
depends = ["fmt-check", "test"]
```

For multi-language projects, combine relevant tool and task sections. Always include a `[tasks.check]` that runs all quality gates.

---

## 5. Task Runner: Makefile

Offer a Makefile as alternative (or complement) to mise.toml. Some teams prefer make for CI compatibility.

### Zig

```makefile
.PHONY: fmt fmt-check build test lint check clean

fmt:
	zig fmt src/

fmt-check:
	zig fmt --check src/

build:
	zig build

test:
	zig build test

lint: fmt-check

check: fmt-check build test

clean:
	rm -rf zig-out .zig-cache
```

### Rust

```makefile
.PHONY: fmt fmt-check lint test check clean

fmt:
	cargo fmt

fmt-check:
	cargo fmt -- --check

lint:
	cargo clippy -- -D warnings

test:
	cargo test

check: fmt-check lint test

clean:
	cargo clean
```

### Go

```makefile
MODULE := $(shell head -1 go.mod | cut -d' ' -f2)

.PHONY: fmt fmt-check lint test bench check clean

fmt:
	goimports -w .

fmt-check:
	@test -z "$$(goimports -l .)" || (echo "files need formatting:" && goimports -l . && exit 1)

lint:
	golangci-lint run ./...

test:
	go test ./...

bench:
	go test -bench=. -benchmem ./...

check: fmt-check lint test

clean:
	go clean -cache -testcache
```

### Node.js / TypeScript

```makefile
.PHONY: fmt fmt-check lint lint-fix test check clean

fmt:
	prettier --write .

fmt-check:
	prettier --check .

lint:
	eslint .

lint-fix:
	eslint --fix .

test:
	npm test

check: fmt-check lint test

clean:
	rm -rf node_modules dist coverage
```

### Python

```makefile
.PHONY: fmt fmt-check lint test test-cov check clean

fmt:
	ruff format .
	ruff check --fix .

fmt-check:
	ruff format --check .
	ruff check .

lint:
	ruff check .

test:
	pytest

test-cov:
	pytest --cov --cov-report=term-missing

check: fmt-check lint test

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov dist build *.egg-info
```

### Java (Gradle)

```makefile
.PHONY: fmt fmt-check lint test build check clean

fmt:
	./gradlew spotlessApply

fmt-check:
	./gradlew spotlessCheck

lint: fmt-check

test:
	./gradlew test

build:
	./gradlew build

check: fmt-check test

clean:
	./gradlew clean
```

---

## 6. CI Workflows

### GitHub Actions (generic with mise)

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

If not using mise, provide language-specific setup:

**Zig:**

```yaml
- uses: mlugg/setup-zig@v2
  with:
    version: 0.15.2
- run: zig fmt --check src/
- run: zig build
- run: zig build test
```

**Rust:**

```yaml
- uses: dtolnay/rust-toolchain@stable
  with:
    components: clippy, rustfmt
- run: cargo fmt -- --check
- run: cargo clippy -- -D warnings
- run: cargo test
```

**Go:**

```yaml
- uses: actions/setup-go@v5
  with:
    go-version: stable
- uses: golangci/golangci-lint-action@v6
- run: go test ./...
```

**Node.js:**

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: lts/*
    cache: npm
- run: npm ci
- run: npm run lint
- run: npm test
```

**Python:**

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"
- run: pip install ruff pytest
- run: ruff check .
- run: ruff format --check .
- run: pytest
```

**Java (Gradle):**

```yaml
- uses: actions/setup-java@v4
  with:
    distribution: temurin
    java-version: 21
- uses: gradle/actions/setup-gradle@v4
- run: ./gradlew check
```

---

## 7. Git Hooks

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

---

## 8. .gitignore

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

Language-specific additions:

- **Zig**: `.zig-cache/`, `zig-out/`
- **Rust**: `target/`
- **Go**: (Go modules handle this; add binary names)
- **Node.js**: `node_modules/`, `dist/`, `coverage/`, `.next/`, `.nuxt/`
- **Python**: `__pycache__/`, `*.pyc`, `.ruff_cache/`, `.pytest_cache/`, `.venv/`, `dist/`, `*.egg-info/`
- **Java**: `build/`, `.gradle/`, `*.class`, `target/` (Maven)
