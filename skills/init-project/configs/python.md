# Python Configs

## Editor Config additions

```ini
[*.py]
indent_size = 4
```

## Tooling: Nix (flake.nix)

Add to `devShells.default` packages:

```nix
packages = with pkgs; [
  python312
  ruff
  uv
  # Common
  nodePackages.prettier
  nodePackages.markdownlint-cli2
];
```

## pyproject.toml (Lints & Settings)

Inject into `pyproject.toml` if missing:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM"]
ignore = ["E501"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

## Makefile

```makefile
NIX_RUN := $(if $(filter $(IN_NIX_SHELL),),nix develop --command ,)

.PHONY: fmt fmt-check lint test check clean

fmt:
	$(NIX_RUN) ruff format .
	$(NIX_RUN) ruff check --fix .
	$(NIX_RUN) prettier --write "**/*.{md,json,yaml,yml}"

fmt-check:
	$(NIX_RUN) ruff format --check .
	$(NIX_RUN) ruff check .
	$(NIX_RUN) prettier --check "**/*.{md,json,yaml,yml}"

lint:
	$(NIX_RUN) ruff check .

test:
	$(NIX_RUN) pytest

check: fmt-check lint test

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov dist build *.egg-info
```

## mise.toml (Fallback)

```toml
[tools]
python = "3.12"
ruff = "latest"
"npm:prettier" = "latest"

[tasks.fmt]
run = "ruff format . && ruff check --fix . && prettier --write '**/*.{md,json,yaml,yml}'"

[tasks.lint]
run = "ruff check ."

[tasks.test]
run = "pytest"

[tasks.check]
depends = ["fmt", "lint", "test"]
```

## CI steps (mise fallback)

For Nix projects, use the Nix-native CI from `common.md` — no language setup step needed.

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"
- run: make check
```

## .gitignore additions

```gitignore
__pycache__/
*.pyc
.ruff_cache/
.pytest_cache/
.venv/
dist/
*.egg-info/
```
