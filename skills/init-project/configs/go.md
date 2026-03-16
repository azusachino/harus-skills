# Go Configs

## Editor Config additions

```ini
[*.go]
indent_style = tab
indent_size = 4
```

## Tooling: Nix (flake.nix)

Add to `devShells.default` packages:

```nix
packages = with pkgs; [
  go
  gofumpt
  goimports-reviser
  golangci-lint
  # Common
  nodePackages.prettier
  nodePackages.markdownlint-cli2
];
```

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

## Makefile

```makefile
MODULE := $(shell head -1 go.mod | cut -d' ' -f2)
NIX_RUN := $(if $(filter $(IN_NIX_SHELL),),nix develop --command ,)

.PHONY: fmt fmt-check lint test bench check clean

fmt:
	$(NIX_RUN) gofmt -w .
	$(NIX_RUN) goimports-reviser -rm-unused -set-alias -format ./...
	$(NIX_RUN) prettier --write "**/*.{md,json,yaml,yml}"

fmt-check:
	@$(NIX_RUN) gofmt -l . | grep . && exit 1 || true
	$(NIX_RUN) prettier --check "**/*.{md,json,yaml,yml}"

lint:
	$(NIX_RUN) golangci-lint run ./...

test:
	$(NIX_RUN) go test ./...

bench:
	$(NIX_RUN) go test -bench=. -benchmem ./...

check: fmt-check lint test

clean:
	$(NIX_RUN) go clean -cache -testcache
```

## mise.toml (Fallback)

```toml
[tools]
go = "latest"
golangci-lint = "latest"
"npm:prettier" = "latest"

[tasks.fmt]
run = "goimports-reviser -rm-unused -set-alias -format ./... && prettier --write '**/*.{md,json,yaml,yml}'"

[tasks.lint]
run = "golangci-lint run ./..."

[tasks.test]
run = "go test ./..."

[tasks.check]
depends = ["fmt", "lint", "test"]
```

## CI steps (mise fallback)

For Nix projects, use the Nix-native CI from `common.md` — no language setup step needed.

```yaml
- uses: actions/setup-go@v5
  with:
    go-version: stable
- uses: golangci/golangci-lint-action@v6
- run: make check
```

## .gitignore additions

Go modules handle most things; add binary names as needed.
