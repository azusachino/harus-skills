# Makefile for managing harus-skills tasks

.PHONY: help install-hooks fmt fmt-check lint lint-fix clean verify list-skills check link lesson lesson-date test lint-links bump-version

# Default target
help:
	@echo "harus-skills development tasks:"
	@echo ""
	@echo "  Setup: nix develop  (provides all tools via nixpkgs)"
	@echo ""
	@echo "  make install-hooks - Install git pre-commit hooks"
	@echo "  make fmt          - Format all files"
	@echo "  make lint         - Lint Python files"
	@echo "  make test         - Run pytest suite"
	@echo "  make lint-links   - Verify all internal documentation links"
	@echo "  make check        - Run all checks (format, lint, verify, test, links)"
	@echo "  make verify       - Verify repository structure"
	@echo "  make list-skills  - List all available skills"
	@echo "  make clean        - Remove generated lesson files"
	@echo "  make link         - Link as a Gemini CLI extension"
	@echo "  make lesson       - Generate today's lesson"
	@echo "  make lesson-date DATE=YYYY-MM-DD - Generate lesson for specific date"
	@echo "  make bump-version VERSION=x.y.z - Synchronize versions across manifests"

install-hooks:
	@echo "🪝 Installing git hooks..."
	@mkdir -p .git/hooks
	@echo '#!/usr/bin/env bash' > .git/hooks/pre-commit
	@echo 'echo "🎨 Auto-formatting staged files..."' >> .git/hooks/pre-commit
	@echo 'STAGED_MD=$$(git diff --cached --name-only --diff-filter=ACM | grep -E "\.md$$" || true)' >> .git/hooks/pre-commit
	@echo 'if [ -n "$$STAGED_MD" ]; then' >> .git/hooks/pre-commit
	@echo '  echo "$$STAGED_MD" | xargs git add' >> .git/hooks/pre-commit
	@echo 'fi' >> .git/hooks/pre-commit
	@echo 'STAGED_DATA=$$(git diff --cached --name-only --diff-filter=ACM | grep -E "\.(json|yaml|yml)$$" || true)' >> .git/hooks/pre-commit
	@echo 'if [ -n "$$STAGED_DATA" ]; then' >> .git/hooks/pre-commit
	@echo '  echo "  📦 Formatting JSON/YAML files..."' >> .git/hooks/pre-commit
	@echo '  echo "$$STAGED_DATA" | xargs prettier --write' >> .git/hooks/pre-commit
	@echo '  echo "$$STAGED_DATA" | xargs git add' >> .git/hooks/pre-commit
	@echo 'fi' >> .git/hooks/pre-commit
	@echo 'echo "✅ Pre-commit formatting complete!"' >> .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "✅ Git hooks installed!"

fmt:
	@echo "Formatting files..."
	@prettier --write "**/*.{json,yaml,yml}"
	@taplo format "**/*.toml" 2>/dev/null || true
	@if find . -name "*.sh" -o -name "*.bash" | grep -q .; then \
		shfmt -w -i 2 -ci -bn $$(find . -name "*.sh" -o -name "*.bash" | grep -v node_modules); \
	fi
	@if find . -name "*.py" | grep -q .; then \
		uv run ruff format .; \
	fi
	@echo "Done."

fmt-check:
	@echo "Checking file formatting..."
	@prettier --check "**/*.{json,yaml,yml}"
	@taplo format --check "**/*.toml" 2>/dev/null || true
	@if find . -name "*.sh" -o -name "*.bash" | grep -q .; then \
		shfmt -d -i 2 -ci -bn $$(find . -name "*.sh" -o -name "*.bash" | grep -v node_modules); \
	fi
	@if find . -name "*.py" | grep -q .; then \
		uv run ruff format --check .; \
	fi
	@echo "All files are properly formatted."

lint:
	@echo "Linting Python files..."
	@if find . -name "*.py" | grep -q .; then \
		uv run ruff check .; \
	fi
	@echo "Done."

lint-fix:
	@echo "Linting and fixing Python files..."
	@if find . -name "*.py" | grep -q .; then \
		uv run ruff check . --fix; \
	fi
	@echo "Done."

lint-links:
	@echo "Checking markdown links..."
	@find . -name "*.md" -not -path "./node_modules/*" -not -path "./.git/*" | xargs -I{} grep -o '\[.*\](.*)' {} | grep -o '(.*)' | tr -d '()' | grep -v '^http' | grep -v '^#' | xargs -I{} ls {} > /dev/null

clean:
	@echo "🧹 Cleaning generated lessons..."
	@rm -rf lessons/
	@echo "✅ Clean complete!"

verify:
	@echo "✅ Verifying repository structure..."
	@for skill_dir in skills/code-skills/*/ skills/lang-skills/*/; do \
		skill_name=$$(basename "$$skill_dir"); \
		if [ ! -f "$$skill_dir/SKILL.md" ]; then \
			echo "❌ Missing SKILL.md in $$skill_name"; \
			exit 1; \
		fi; \
		echo "  ✓ $$skill_name has SKILL.md"; \
	done
	@if [ ! -f ".claude-plugin/marketplace.json" ]; then \
		echo "❌ Missing .claude-plugin/marketplace.json"; \
		exit 1; \
	fi
	@echo "  ✓ marketplace.json exists"
	@if [ ! -f "CLAUDE.md" ]; then \
		echo "❌ Missing CLAUDE.md"; \
		exit 1; \
	fi
	@echo "  ✓ CLAUDE.md exists"
	@if [ ! -f "gemini-extension.json" ]; then \
		echo "❌ Missing gemini-extension.json"; \
		exit 1; \
	fi
	@echo "  ✓ gemini-extension.json exists"
	@echo "✅ Repository structure is valid!"

list-skills:
	@echo "📚 Available skills:"
	@echo ""
	@for skill_dir in skills/code-skills/*/ skills/lang-skills/*/; do \
		if [ -f "$$skill_dir/SKILL.md" ]; then \
			category=$$(basename "$$(dirname "$$skill_dir")"); \
			skill_name=$$(basename "$$skill_dir"); \
			description=$$(grep "^description:" "$$skill_dir/SKILL.md" | cut -d':' -f2- | xargs); \
			echo "  • [$$category] $$skill_name"; \
			if [ -n "$$description" ]; then \
				echo "    $$description"; \
			fi; \
			echo ""; \
		fi; \
	done

test:
	@echo "Running tests..."
	@uv run pytest tests/

check: fmt-check lint verify test lint-links
	@echo "✅ All checks passed!"

link:
	@gemini extensions link .

lesson:
	@claude "/daily-language-lesson"

lesson-date:
	@if [ -z "$(DATE)" ]; then \
		echo "❌ Error: DATE not provided. Usage: make lesson-date DATE=2026-03-01"; \
		exit 1; \
	fi
	@claude "/daily-language-lesson $(DATE)"

bump-version:
	@if [ -z "$(VERSION)" ]; then \
		echo "❌ Error: VERSION not provided. Usage: make bump-version VERSION=1.9.0"; \
		exit 1; \
	fi
	@uv run scripts/bump_version.py $(VERSION)
	@echo "✅ Bumped version to $(VERSION)"
