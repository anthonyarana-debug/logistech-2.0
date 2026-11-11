import { test, expect } from '@playwright/test'
import { Workspace, evidencePath } from './workspace.js'

for (const fault of [500, 503, 'offline']) {
  test(`simulated ${fault} shows a safe error and retry reloads categories`, async ({ page }) => {
    const workspace = new Workspace(page)
    await workspace.login('admin')
    let pending = true
    await page.route('**/api/v1/categories/?*', async (route) => {
      if (!pending) return route.continue()
      pending = false
      if (fault === 'offline') return route.abort('failed')
      return route.fulfill({
        status: fault,
        contentType: 'application/json',
        body: JSON.stringify({ detalle: 'internal sentinel' }),
      })
    })
    await workspace.nav('Categories')
    const alert = page.getByRole('alert')
    await expect(alert).toBeVisible()
    await expect(alert).not.toContainText('internal sentinel')
    await page.screenshot({ path: evidencePath(`fault-${fault}-SIMULATED`), fullPage: true })
    const recovered = page.waitForResponse(
      (response) => response.url().includes('/api/v1/categories/?') && response.status() === 200,
    )
    await alert.getByRole('button', { name: 'Try again' }).click()
    await recovered
    await expect(alert).toHaveCount(0)
    await expect(page.getByRole('table')).toBeVisible()
  })
}
