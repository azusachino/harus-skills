# Python Configs

## Editor Config additions

```ini
[*.py]
indent_size = 4
```

## Ruff

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

## mise.toml

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

## Makefile

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

## CI steps (non-mise)

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"
- run: pip install ruff pytest
- run: ruff check .
- run: ruff format --check .
- run: pytest
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
