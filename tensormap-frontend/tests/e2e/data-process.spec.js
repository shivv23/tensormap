import { test, expect } from "@playwright/test";

test.describe("Data Process Page", () => {
  test.use({ baseURL: "http://localhost:3300" });

  test("shows loading state initially", async ({ page }) => {
    await page.goto("/workspace/test-project-id/dataset");
    await expect(page.getByText(/loading/i)).toBeVisible();
  });

  test("redirects /data-upload to /projects", async ({ page }) => {
    await page.goto("/data-upload");
    await expect(page).toHaveURL(/\/projects/);
  });

  test("redirects /data-process to /projects", async ({ page }) => {
    await page.goto("/data-process");
    await expect(page).toHaveURL(/\/projects/);
  });
});

test.describe("Deep Learning Page", () => {
  test.use({ baseURL: "http://localhost:3300" });

  test("redirects /deep-learning to /projects", async ({ page }) => {
    await page.goto("/deep-learning");
    await expect(page).toHaveURL(/\/projects/);
  });

  test("redirects /home to /projects", async ({ page }) => {
    await page.goto("/home");
    await expect(page).toHaveURL(/\/projects/);
  });
});