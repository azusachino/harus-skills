# Node.js Configs

## Editor Config additions

```ini
[*.{js,ts,tsx,jsx}]
indent_size = 2
```

## Tooling: Nix (flake.nix)

Add to `devShells.default` packages:

```nix
packages = with pkgs; [
  nodejs_20
  pnpm
  # Common
  nodePackages.prettier
];
```

## package.json (Lints & Settings)

Inject into `package.json` if missing:

```json
{
  "scripts": {
    "fmt": "prettier --write '**/*.{js,ts,tsx,jsx,md,json,yaml,yml}'",
    "lint": "eslint .",
    "test": "vitest run",
    "check": "npm run fmt && npm run lint && npm run test"
  },
  "prettier": {
    "proseWrap": "always",
    "printWidth": 120,
    "tabWidth": 2,
    "singleQuote": true
  }
}
```

## Makefile

```makefile
NIX_RUN := $(if $(filter $(IN_NIX_SHELL),),nix develop --command ,)

.PHONY: fmt fmt-check lint test check clean

fmt:
	$(NIX_RUN) npm run fmt

fmt-check:
	$(NIX_RUN) npx prettier --check "**/*.{js,ts,tsx,jsx,md,json,yaml,yml}"

lint:
	$(NIX_RUN) npm run lint

test:
	$(NIX_RUN) npm run test

check:
	$(NIX_RUN) npm run check

clean:
	rm -rf node_modules dist build coverage
```

## mise.toml (Fallback)

```toml
[tools]
node = "20"
"npm:prettier" = "latest"

[tasks.fmt]
run = "npm run fmt"

[tasks.lint]
run = "npm run lint"

[tasks.test]
run = "npm run test"

[tasks.check]
depends = ["fmt", "lint", "test"]
```

## CI steps (mise fallback)

For Nix projects, use the Nix-native CI from `common.md` — no language setup step needed.

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: "20"
- run: npm install
- run: make check
```

## .gitignore additions

```gitignore
node_modules/
dist/
build/
coverage/
.next/
.turbo/
```
