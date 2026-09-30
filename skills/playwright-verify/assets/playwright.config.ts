// Headless Chromium verification, cloned from the playwright-verify skill.
// Set the values marked EDIT. When a project script has already started the
// app, it exports E2E_BASE_URL and this config starts no server of its own.
import { defineConfig, devices } from "@playwright/test"

const PORT = 5173 // EDIT: the port the dev server listens on
const COMMAND = `bun run dev --port ${PORT} --strictPort` // EDIT: starts the app without interaction
const external = process.env.E2E_BASE_URL
const CI = !!process.env.CI
const chrome = devices["Desktop Chrome"]

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  expect: { timeout: 5_000 },
  // Playwright's recommended CI settings: no stray test.only, retries that
  // expose flaky tests instead of hiding them, one worker.
  forbidOnly: CI,
  retries: CI ? 2 : 0,
  failOnFlakyTests: CI,
  workers: CI ? 1 : undefined,
  // A text reporter, because agents read the terminal; the html report needs a browser.
  reporter: "list",
  use: {
    baseURL: external ?? `http://127.0.0.1:${PORT}`,
    // Local runs do not retry, so keep a trace of every failure rather than of the first retry.
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  // `make e2e` runs the checks; `make e2e-probe` runs only the probe.
  projects: [
    { name: "chromium", use: chrome, testIgnore: /probe\.spec\.ts$/ },
    { name: "probe", use: chrome, testMatch: /probe\.spec\.ts$/ },
  ],
  // No reuse: a port already in use fails the run instead of testing a server someone else is using.
  webServer: external
    ? undefined
    : { command: COMMAND, url: `http://127.0.0.1:${PORT}`, reuseExistingServer: false, timeout: 60_000 },
})
