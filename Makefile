# Makefile for managing harus-skills tasks

.PHONY: help install-hooks fmt fmt-check clean verify list-skills check validate link

# Default target
help:
	@echo "harus-skills development tasks:"
	@echo ""
	@echo "  Setup: nix develop  (provides all tools via nixpkgs)"
	@echo ""
	@echo "  make install-hooks - Install git pre-commit hooks"
	@echo "  make fmt          - Format JSON/YAML files"
	@echo "  make check        - Run all checks (format + verify)"
	@echo "  make validate     - PR gate: check + manifest validation"
	@echo "  make verify       - Verify repository structure"
	@echo "  make list-skills  - List all available skills"
	@echo "  make clean        - Remove generated files"
	@echo "  make link         - Link as a Gemini CLI extension"

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
	@echo "Formatting JSON/YAML files..."
	@prettier --write "**/*.{json,yaml,yml}"
	@echo "Done."

fmt-check:
	@echo "Checking JSON/YAML formatting..."
	@prettier --check "**/*.{json,yaml,yml}"
	@echo "All files are properly formatted."

clean:
	@echo "🧹 Cleaning generated lessons..."
	@rm -rf lessons/
	@echo "✅ Clean complete!"

verify:
	@echo "✅ Verifying repository structure..."
	@for skill_dir in skills/*/; do \
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
	@for skill_dir in skills/*/; do \
		if [ -f "$$skill_dir/SKILL.md" ]; then \
			skill_name=$$(basename "$$skill_dir"); \
			description=$$(grep "^description:" "$$skill_dir/SKILL.md" | cut -d':' -f2- | xargs); \
			echo "  • $$skill_name"; \
			if [ -n "$$description" ]; then \
				echo "    $$description"; \
			fi; \
			echo ""; \
		fi; \
	done

check: fmt-check verify
	@echo "✅ All checks passed!"

validate: check
	@echo "🔎 Validating plugin manifests..."
	@jq empty .claude-plugin/marketplace.json gemini-extension.json
	@MP=$$(jq -r '.metadata.version' .claude-plugin/marketplace.json); \
		PV=$$(jq -r '.plugins[0].version' .claude-plugin/marketplace.json); \
		GV=$$(jq -r '.version' gemini-extension.json); \
		if [ "$$MP" != "$$PV" ] || [ "$$MP" != "$$GV" ]; then \
			echo "❌ Version mismatch: marketplace.metadata=$$MP plugin=$$PV gemini=$$GV"; \
			exit 1; \
		fi; \
		echo "  ✓ manifest versions aligned ($$MP)"
	@echo "✅ Validation passed!"

link:
	@gemini extensions link .
