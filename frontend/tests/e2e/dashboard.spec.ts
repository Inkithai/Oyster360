import { expect, test } from '@playwright/test'

test('dashboard loads correctly', async ({ page }) => {
  await page.goto('/dashboard')

  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible()
  await expect(page.getByText('Active Batches', { exact: true })).toBeVisible()
  await expect(page.getByText('Expected Harvest', { exact: true })).toBeVisible()
})

test('navigation works', async ({ page }) => {
  await page.goto('/dashboard')

  await page.getByRole('link', { name: 'Batches' }).click()
  await expect(page).toHaveURL(/\/batches$/)

  await page.getByRole('link', { name: 'Analytics' }).click()
  await expect(page).toHaveURL(/\/analytics$/)
})
