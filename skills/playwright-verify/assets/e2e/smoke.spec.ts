// Smoke check cloned from the playwright-verify skill: the first route renders
// its main landmark without console errors. Replace it with the app's own
// behavior checks as they are written.
import { expect, test } from "@playwright/test"

const ROUTE = "/" // EDIT: the first route to check

test("first route renders without console errors", async ({ page }) => {
  const errors: string[] = []
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text())
  })
  page.on("pageerror", (error) => errors.push(error.message))

  await page.goto(ROUTE)

  await expect(page.getByRole("main")).toBeVisible() // EDIT: a landmark this page must show
  expect(errors).toEqual([])
})
