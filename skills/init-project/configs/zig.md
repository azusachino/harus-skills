# Zig Configs

## Editor Config additions

```ini
[*.zig]
indent_size = 4
```

## mise.toml

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

## Makefile

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

## CI steps (non-mise)

```yaml
- uses: mlugg/setup-zig@v2
  with:
    version: 0.15.2
- run: zig fmt --check src/
- run: zig build
- run: zig build test
```

## .gitignore additions

```gitignore
.zig-cache/
zig-out/
```
