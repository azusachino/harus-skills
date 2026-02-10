# Rust Configs

## Editor Config additions

```ini
[*.rs]
indent_size = 4
```

## rustfmt.toml

```toml
edition = "2021"
max_width = 100
tab_spaces = 4
use_field_init_shorthand = true
use_try_shorthand = true
imports_granularity = "Crate"
group_imports = "StdExternalCrate"
```

## Clippy

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

## mise.toml

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

## Makefile

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

## CI steps (non-mise)

```yaml
- uses: dtolnay/rust-toolchain@stable
  with:
    components: clippy, rustfmt
- run: cargo fmt -- --check
- run: cargo clippy -- -D warnings
- run: cargo test
```

## .gitignore additions

```gitignore
target/
```
