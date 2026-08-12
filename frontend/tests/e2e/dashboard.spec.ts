import { test, expect } from '@playwright/test';

test('dashboard loads correctly', async ({ page }) => {
  await page.goto('http://localhost:3000/dashboard');
  
  // Check if dashboard elements exist
  await expect(page.locator('h1')).toContainText('Dashboard');
  await expect(page.locator('text=Active Batches')).toBeVisible();
  await expect(page.locator('text=Expected Harvest')).toBeVisible();
});

test('navigation works', async ({ page }) => {
  await page.goto('http://localhost:3000/dashboard');
  
  // Navigate to batches
  await page.click('text=Batches');
  await expect(page).toHaveURL(/batches/);
  
  // Navigate to analytics
  await page.click('text=Analytics');
  await expect(page).toHaveURL(/analytics/);
});