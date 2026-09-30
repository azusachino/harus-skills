# Browser verification targets, cloned from the playwright-verify skill.
# Set E2E_DIR to the web app directory before `include e2e.mk`.
E2E_DIR ?= .
# CI sets E2E_INSTALL_FLAGS=--with-deps to add the system libraries Chromium needs.
E2E_INSTALL_FLAGS ?=

.PHONY: e2e e2e-probe e2e-install

e2e: ## Verify the web UI in headless Chromium (ARGS='-g "name"' to filter)
	cd $(E2E_DIR) && bunx playwright test --project=chromium $(ARGS)

e2e-probe: ## Screenshot one route before a spec exists (ROUTE=/path)
	cd $(E2E_DIR) && PROBE_ROUTE=$(ROUTE) bunx playwright test --project=probe

e2e-install: ## Install the Chromium build this Playwright version needs
	cd $(E2E_DIR) && bunx playwright install $(E2E_INSTALL_FLAGS) chromium
