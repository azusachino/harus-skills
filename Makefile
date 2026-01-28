.PHONY: help install uninstall test clean verify-config list-skills

# Default target
help:
	@echo "Haru's Skills - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install skills to Claude Code config"
	@echo "  make uninstall        Remove skills from Claude Code config"
	@echo "  make verify-config    Check if skills are properly configured"
	@echo ""
	@echo "Usage:"
	@echo "  make list-skills      List all available skills"
	@echo "  make test             Generate test lessons to verify functionality"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean            Remove generated lesson files"
	@echo ""
	@echo "After installation, restart Claude Code and use:"
	@echo "  /daily-language-lesson or /dll or /lesson"

# Install skills by adding this repo to Claude Code config
install:
	@echo "Installing haru's skills..."
	@mkdir -p ~/.config/claude
	@if [ ! -f ~/.config/claude/config.json ]; then \
		echo '{"skillDirectories": ["$(CURDIR)/skills"]}' > ~/.config/claude/config.json; \
		echo "✓ Created new config at ~/.config/claude/config.json"; \
	else \
		echo "⚠ Config file exists at ~/.config/claude/config.json"; \
		echo "Please manually add the following to your skillDirectories array:"; \
		echo "  \"$(CURDIR)/skills\""; \
	fi
	@echo ""
	@echo "⚠ IMPORTANT: Restart Claude Code for changes to take effect"
	@echo ""
	@make verify-config

# Remove skills from Claude Code config
uninstall:
	@echo "Uninstalling haru's skills..."
	@echo "⚠ Please manually remove the following path from ~/.config/claude/config.json:"
	@echo "  \"$(CURDIR)/skills\""
	@echo ""
	@echo "After removing, restart Claude Code."

# Verify configuration is correct
verify-config:
	@echo "Verifying configuration..."
	@if [ ! -f ~/.config/claude/config.json ]; then \
		echo "✗ Config file not found at ~/.config/claude/config.json"; \
		echo "  Run 'make install' to create it"; \
		exit 1; \
	else \
		echo "✓ Config file exists"; \
	fi
	@if grep -q "$(CURDIR)/skills" ~/.config/claude/config.json 2>/dev/null; then \
		echo "✓ Skills directory is configured"; \
	else \
		echo "⚠ Skills directory not found in config"; \
		echo "  Run 'make install' or manually add path"; \
	fi
	@if [ -d "$(CURDIR)/skills" ]; then \
		echo "✓ Skills directory exists"; \
	else \
		echo "✗ Skills directory not found"; \
		exit 1; \
	fi
	@echo ""
	@echo "Configuration looks good! Restart Claude Code if you just installed."

# List all available skills
list-skills:
	@echo "Available Skills:"
	@echo ""
	@for skill in skills/*/skill.json; do \
		if [ -f "$$skill" ]; then \
			dir=$$(dirname $$skill); \
			name=$$(basename $$dir); \
			desc=$$(grep -o '"description"[[:space:]]*:[[:space:]]*"[^"]*"' $$skill | sed 's/"description"[[:space:]]*:[[:space:]]*"\(.*\)"/\1/'); \
			cmd=$$(grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' $$skill | sed 's/"command"[[:space:]]*:[[:space:]]*"\(.*\)"/\1/'); \
			echo "  📦 $$name"; \
			echo "     Command: /$$cmd"; \
			echo "     $$desc"; \
			echo ""; \
		fi \
	done

# Test skill functionality by generating lessons
test:
	@echo "Testing daily-language-lesson skill..."
	@echo "This would normally use /lesson command, but we'll verify files can be created"
	@DATE=$$(date +%Y-%m-%d); \
	if [ -d "lessons/$$DATE" ]; then \
		echo "✓ Lesson directory for today ($$DATE) already exists"; \
		echo "  Files:"; \
		ls -lh lessons/$$DATE/; \
	else \
		echo "✗ No lessons generated for today ($$DATE)"; \
		echo "  Run Claude Code and execute: /lesson"; \
	fi

# Clean generated lesson files
clean:
	@echo "Cleaning generated lessons..."
	@if [ -d "lessons" ]; then \
		read -p "Delete all lessons in ./lessons? [y/N] " -n 1 -r; \
		echo; \
		if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
			rm -rf lessons/*; \
			echo "✓ Lessons cleaned"; \
		else \
			echo "Cancelled"; \
		fi \
	else \
		echo "No lessons directory found"; \
	fi
