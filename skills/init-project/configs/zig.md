# Zig Configs

## Editor Config additions

```ini
[*.zig]
indent_size = 4
```

## Tooling: Nix (flake.nix)

Add to `devShells.default` packages:

```nix
packages = with pkgs; [
  zig
  zls
  # Common
  nodePackages.prettier
  nodePackages.markdownlint-cli2
];
```

## Makefile

```makefile
NIX_RUN := $(if $(filter $(IN_NIX_SHELL),),nix develop --command ,)

.PHONY: fmt fmt-check build test lint check clean

fmt:
	$(NIX_RUN) zig fmt .
	$(NIX_RUN) prettier --write "**/*.{md,json,yaml,yml}"

fmt-check:
	$(NIX_RUN) zig fmt --check .
	$(NIX_RUN) prettier --check "**/*.{md,json,yaml,yml}"

build:
	$(NIX_RUN) zig build

test:
	$(NIX_RUN) zig build test

lint: fmt-check

check: fmt-check build test

clean:
	rm -rf zig-out .zig-cache
```

## mise.toml (Fallback)

```toml
[tools]
zig = "latest"
"npm:prettier" = "latest"

[tasks.fmt]
run = "zig fmt . && prettier --write '**/*.{md,json,yaml,yml}'"

[tasks.build]
run = "zig build"

[tasks.test]
run = "zig build test"

[tasks.check]
depends = ["fmt", "build", "test"]
```

## CI steps (mise fallback)

For Nix projects, use the Nix-native CI from `common.md` — no language setup step needed.

```yaml
- uses: mlugg/setup-zig@v2
  with:
    version: master
- run: make check
```

## .gitignore additions

```gitignore
.zig-cache/
zig-out/
```
