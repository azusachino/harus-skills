// Exploration probe cloned from the playwright-verify skill: renders one route
// through the same config and server as the checks and prints what an agent
// needs before writing a spec: title, URL, console errors, and the page's ARIA
// snapshot, whose roles and names become getByRole locators. It also saves a
// full-page screenshot as probe.png in its test-results folder, and asserts
// nothing. Run it with `make e2e-probe ROUTE=/path`.
import { expect, test } from "@playwright/test"

test("probe", async ({ page }, testInfo) => {
  const errors: string[] = []
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text())
  })
  page.on("pageerror", (error) => errors.push(error.message))

  await page.goto(process.env.PROBE_ROUTE || "/")
  // A client-rendered page paints after the load event: wait for visible text
  // (innerText, so inline scripts do not count) rather than for the network.
  await expect(page.locator("body")).toHaveText(/\S/, { useInnerText: true, timeout: 15_000 })
  await page.screenshot({ path: testInfo.outputPath("probe.png"), fullPage: true })

  console.log(JSON.stringify({ title: await page.title(), url: page.url(), errors }, null, 2))
  console.log(await page.locator("body").ariaSnapshot())
})
