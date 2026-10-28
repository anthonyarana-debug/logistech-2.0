import { test, expect } from '@playwright/test'

test('English remains the default with Spanish browser preferences', async ({ browser }) => {
  const context = await browser.newContext({ locale: 'es-PE' })
  const page = await context.newPage()
  try {
    await page.goto('/')
    await expect(page.locator('html')).toHaveAttribute('lang', 'en')
    await expect(page).toHaveTitle('LogisTech 2.0 · Logistics with a clear identity')
    await expect(page.getByRole('heading', { level: 1 })).toContainText('Every box.')
    await page.goto('/login')
    await expect(page.getByLabel('Email address')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Show password' })).toBeVisible()
    await page.getByRole('button', { name: 'Show password' }).click()
    await expect(page.getByRole('button', { name: 'Hide password' })).toBeVisible()
    await page.goto('/estado')
    await page.getByRole('button', { name: 'Check service' }).click()
    await expect(page.getByRole('status')).toContainText('API and PostgreSQL are available.')
  } finally {
    await context.close()
  }
})
