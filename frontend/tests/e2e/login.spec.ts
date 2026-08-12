import { test, expect } from '@playwright/test';

test('user can login', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  
  await page.fill('input[type="email"]', 'admin@myco.farm');
  await page.fill('input[type="password"]', 'admin123');
  await page.click('button[type="submit"]');
  
  await expect(page).toHaveURL(/dashboard/);
});