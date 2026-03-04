import { expect, test } from '@playwright/test'

test('user can log in', async ({ page }) => {
  await page.route('**/api/auth/login', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        access_token: 'test-access-token',
        refresh_token: 'test-refresh-token',
        token_type: 'bearer',
      }),
    })
  })

  await page.goto('/login')
  await page.getByLabel('Email').fill('admin@myco.farm')
  await page.getByLabel('Password').fill('admin123')
  await page.getByRole('button', { name: 'Sign In' }).click()

  await expect(page).toHaveURL(/\/dashboard$/)
  await expect.poll(() => page.evaluate(() => localStorage.getItem('token')))
    .toBe('test-access-token')
})
