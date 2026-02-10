# Node.js / TypeScript Configs

## Editor Config additions

```ini
[*.{js,jsx,ts,tsx,mjs,cjs}]
indent_size = 2
```

## ESLint

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

## mise.toml

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

## Makefile

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

## CI steps (non-mise)

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: lts/*
    cache: npm
- run: npm ci
- run: npm run lint
- run: npm test
```

## .gitignore additions

```gitignore
node_modules/
dist/
coverage/
.next/
.nuxt/
```
