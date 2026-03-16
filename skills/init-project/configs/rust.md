# Rust Configs

## Editor Config additions

```ini
[*.rs]
indent_size = 4
```

## Tooling: Nix (flake.nix)

Add to `devShells.default` packages:

```nix
packages = with pkgs; [
  rustc
  cargo
  rustfmt
  clippy
  # Common
  nodePackages.prettier
];
```

## Cargo.toml (Lints & Settings)

Inject into `Cargo.toml` if missing:

```toml
[lints.clippy]
pedantic = { level = "warn", priority = -1 }
module_name_repetitions = "allow"
must_use_candidate = "allow"
missing_errors_doc = "allow"

[profile.release]
lto = true
codegen-units = 1
panic = "abort"
```

## Makefile

```makefile
NIX_RUN := $(if $(filter $(IN_NIX_SHELL),),nix develop --command ,)

.PHONY: fmt fmt-check lint test check clean

fmt:
	$(NIX_RUN) cargo fmt
	$(NIX_RUN) prettier --write "**/*.{md,json,yaml,yml}"

fmt-check:
	$(NIX_RUN) cargo fmt -- --check
	$(NIX_RUN) prettier --check "**/*.{md,json,yaml,yml}"

lint:
	$(NIX_RUN) cargo clippy -- -D warnings

test:
	$(NIX_RUN) cargo test

check: fmt-check lint test

clean:
	$(NIX_RUN) cargo clean
```

## mise.toml (Fallback)

```toml
[tools]
rust = "stable"
"npm:prettier" = "latest"

[tasks.fmt]
run = "cargo fmt && prettier --write '**/*.{md,json,yaml,yml}'"

[tasks.lint]
run = "cargo clippy -- -D warnings"

[tasks.test]
run = "cargo test"

[tasks.check]
depends = ["fmt", "lint", "test"]
```

## CI steps (mise fallback)

For Nix projects, use the Nix-native CI from `common.md` — no language setup step needed.

```yaml
- uses: dtolnay/rust-toolchain@stable
  with:
    components: clippy, rustfmt
- run: make check
```

## .gitignore additions

```gitignore
target/
```
