---
name: playwright-verify
description: Verify a web app's behavior in headless Chromium with Playwright, and give a web project that check as `make e2e`. Use after changing a web UI, when asked to confirm a page works in a real browser, or when a web project has no browser check yet. Use it instead of an interactive browser session such as agent-browser.
metadata:
  author: haru
  version: 1.0.1
---

# Playwright verify

State the behavior as a Playwright spec, run it headless through the project's `make e2e`, and keep the spec as the project's regression check.

Keep everything in source: settings in `playwright.config.ts`, checks and probes in spec files, setup and runs behind Make targets. Do not verify with one-off commands or logic typed on a command line; anything worth running belongs in one of those files, where the next person or agent can rerun it.

The practices below follow [Playwright's best practices](https://playwright.dev/docs/best-practices); the deliberate departures are listed under Limits.

## Fit

A project fits when it serves its web UI from a dev or preview server that starts without interaction, on local or fixture data. Headless Chromium needs no display: it runs over plain SSH on a Mac with no console session. A desktop or mobile shell (Tauri, Compose, Android) is out of scope, though its web frontend alone may fit.

## Add it to a project

1. Add `@playwright/test` as a dev dependency with the project's package manager, so its lockfile pins the version. Each Playwright version needs its own Chromium build; choose a version another project already uses to skip a download.
2. Copy the templates from `assets/`: `playwright.config.ts` next to the web app's `package.json`, `e2e/smoke.spec.ts` and `e2e/probe.spec.ts` into its `e2e/`, and `e2e.mk` next to the project's `Makefile`.
3. Set the values marked `EDIT`: the dev command and its port in the config, and in the smoke spec the first route and a landmark it must show.
4. In the `Makefile`, set `E2E_DIR` to the web app's directory and add `include e2e.mk`. It defines `e2e`, `e2e-probe` and `e2e-install`.
5. Run `make e2e-install` once, then `make e2e`.
6. Add `test-results/` and `playwright-report/` to the web app's `.gitignore`.
7. Mention `make e2e` in the project's own instructions, so an agent finds it without this skill.

When the app needs more than one server, seeded data, or checks after the run, give the lifecycle to a project script that starts everything, exports `E2E_BASE_URL`, and runs the checks; the config then starts no server of its own. felicia's admin E2E harness works this way.

In CI, run `make e2e-install E2E_INSTALL_FLAGS=--with-deps` and then `make e2e` with `CI` set. The config then forbids a committed `test.only`, retries failures twice but fails the run on a test that only passed on retry, and uses one worker.

## Look before you write

Run `make e2e-probe ROUTE=/path` before writing a spec for a page you have not seen. The probe renders the route through the same config and server as the checks, waits until the page shows visible text (a client-rendered app paints after the load event), prints its title, URL, console errors and ARIA snapshot, and saves a full-page `probe.png` under `test-results/`. A page that stays blank fails the probe, with its screenshot kept. The snapshot lists the page's roles and accessible names: write locators from it rather than from guesses. Read the screenshot back for anything visual. To see something the probe does not capture, extend `probe.spec.ts` rather than running a one-off script.

## Verify a change

1. Write or extend a spec for the behavior the change promises, in user terms:
   - Locate by role first (`getByRole`), then by label for form fields (`getByLabel`), by text for non-interactive content (`getByText`), and by test id only as a fallback (`getByTestId`). Never use CSS or XPath selectors.
   - Assert with web-first assertions, which wait and retry: `await expect(locator).toBeVisible()`, `toHaveText`, `toHaveURL`. Never `expect(await locator.isVisible()).toBe(true)`, fixed sleeps, or `networkidle` waits, which Playwright discourages for tests.
   - Check a region's structure with `toMatchAriaSnapshot` rather than a pixel comparison.
2. Keep each test independent: set up its state in the test, a `beforeEach` or a fixture, never from another test's leftovers. Fake third-party services with `page.route`, so a check does not depend on someone else's server. For an app behind a login, a setup project signs in once and saves `storageState` for the others.
3. Run `make e2e`. While iterating, filter with `ARGS='-g "<test name>"'`, rerun only failures with `ARGS=--last-failed`, or only changed specs with `ARGS=--only-changed`.
4. On a failure, read what Playwright kept in the failing test's folder under `test-results/`: `error-context.md`, the `test-failed-1.png` screenshot and `trace.zip`. The error context and the screenshot are enough without a display; the trace viewer needs one.
5. Fix and rerun until it passes, then run the whole suite once.
6. Report the spec that covers the change and its result. For a visual change, attach a screenshot to the PR.

## Limits

- Chromium only, headless: Playwright recommends every browser, but these projects add another only when one needs it.
- The `list` reporter and `retain-on-failure` traces replace Playwright's `html` and `on-first-retry` defaults, because an agent reads the terminal and local runs do not retry.
- Use Playwright's own timeouts (`timeout`, `expect.timeout`, `webServer.timeout`) rather than a shell `timeout`: macOS has none unless GNU coreutils supplies `gtimeout`.
- Let `webServer` or the project's script start the app on its own port. The config refuses a port already in use, so it never tests a server someone else is running.
- Update Playwright deliberately: change the pinned version, run `make e2e-install`, then `make e2e`.
- For a suite large enough to plan, generate and repair tests at scale, Playwright's Test Agents (`playwright init-agents`, 1.56+) automate that loop but add an MCP server; this skill does not need them.
