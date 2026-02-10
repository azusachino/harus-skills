# Go Configs

## Editor Config additions

```ini
[*.go]
indent_style = tab
indent_size = 4
```

## Formatter

Go uses `gofmt`/`goimports` with no config file needed. Add to mise tasks instead.

## golangci-lint

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

## mise.toml

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

## Makefile

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

## CI steps (non-mise)

```yaml
- uses: actions/setup-go@v5
  with:
    go-version: stable
- uses: golangci/golangci-lint-action@v6
- run: go test ./...
```

## .gitignore additions

Go modules handle most things; add binary names as needed.
