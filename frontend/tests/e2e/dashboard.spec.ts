import { expect, test } from '@playwright/test'

// Route-level API mocks keep this spec hermetic: it runs against the Next.js
// dev server without needing a live backend, exactly like login.spec.ts.
test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('token', 'e2e-access-token')
  })

  await page.route('**/api/analytics/dashboard', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        active_batches: 4,
        total_production_kg: 485,
        success_rate: 92,
        contamination_rate: 6,
        average_cultivation_days: 27,
        average_yield: 810,
      }),
    })
  })

  await page.route('**/api/analytics/environment', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        temperature: [
          { date: '08/21', value: 22.5 },
          { date: '08/22', value: 23.1 },
        ],
        humidity: [],
        co2: [],
      }),
    })
  })
})

test('dashboard loads correctly', async ({ page }) => {
  await page.goto('/dashboard')

  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible()
  await expect(page.getByText('Active Batches', { exact: true })).toBeVisible()
  await expect(page.getByText('Expected Harvest', { exact: true })).toBeVisible()
  await expect(page.getByText('485 kg')).toBeVisible()
})

test('navigation works', async ({ page }) => {
  await page.goto('/dashboard')

  await page.getByRole('link', { name: 'Batches' }).click()
  await expect(page).toHaveURL(/\/batches$/)

  await page.getByRole('link', { name: 'Analytics' }).click()
  await expect(page).toHaveURL(/\/analytics$/)
})
