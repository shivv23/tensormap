import { test, expect } from "@playwright/test";

test.describe("Projects Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.route("**/api/v1/project", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, data: [] }) });
    });
  });

  test("renders the projects page with heading", async ({ page }) => {
    await page.goto("/projects");
    await expect(page.getByRole("heading", { name: "Projects" })).toBeVisible();
  });

  test("shows New Project button", async ({ page }) => {
    await page.goto("/projects");
    await expect(page.getByRole("button", { name: /new project/i })).toBeVisible();
  });

  test("opens create project dialog on button click", async ({ page }) => {
    await page.goto("/projects");
    await page.getByRole("button", { name: /new project/i }).click();
    await expect(page.getByRole("dialog")).toBeVisible();
  });

  test("shows empty state when no projects exist", async ({ page }) => {
    await page.goto("/projects");
    await expect(page.getByText(/no projects yet/i)).toBeVisible();
  });

  test("redirects root route to /projects", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveURL(/\/projects/);
  });
});

test.describe("Legacy Route Redirects", () => {
  test("redirects /data-upload to /projects", async ({ page }) => {
    await page.goto("/data-upload");
    await expect(page).toHaveURL(/\/projects/);
  });

  test("redirects /data-process to /projects", async ({ page }) => {
    await page.goto("/data-process");
    await expect(page).toHaveURL(/\/projects/);
  });

  test("redirects /deep-learning to /projects", async ({ page }) => {
    await page.goto("/deep-learning");
    await expect(page).toHaveURL(/\/projects/);
  });

  test("redirects /home to /projects", async ({ page }) => {
    await page.goto("/home");
    await expect(page).toHaveURL(/\/projects/);
  });
});

test.describe("404 Catch-All", () => {
  test("redirects unknown routes to /projects", async ({ page }) => {
    await page.goto("/this-route-does-not-exist");
    await expect(page).toHaveURL(/\/projects/);
  });
});