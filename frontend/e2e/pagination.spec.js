import { randomUUID } from 'node:crypto'
import { test, expect } from '@playwright/test'
import { Workspace, evidencePath } from './workspace.js'

test('category navigation uses server totals and resets on a new filter', async ({ page }) => {
  const workspace = new Workspace(page)
  const login = page.waitForResponse(response =>
    response.url().endsWith('/auth/login/') && response.request().method() === 'POST')
  await workspace.login('admin')
  const { access } = await (await login).json()
  const headers = { Authorization: 'Bearer ' + access }
  const prefix = 'Page QA ' + randomUUID().slice(0, 8)
  const created = []
  try {
    for (let index = 1; index <= 26; index++) {
      const response = await page.request.post('/api/v1/categories/', {
        headers, data: { name: prefix + ' ' + String(index).padStart(2, '0') },
      })
      expect(response.status()).toBe(201)
      created.push((await response.json()).id)
    }
    await workspace.nav('Categories')
    const search = page.getByRole('searchbox', { name: 'Search categories' })
    await search.fill(prefix)
    await expect(page.getByText('Page 1 · 26 records')).toBeVisible()
    await page.getByRole('button', { name: 'Next page' }).click()
    await expect(page.getByText('Page 2 · 26 records')).toBeVisible()
    await expect(page.getByRole('cell', { name: prefix + ' 26', exact: true })).toBeVisible()
    await page.screenshot({ path: evidencePath('pagination'), fullPage: true })
    await search.fill(prefix + ' 01')
    await expect(page.getByRole('cell', { name: prefix + ' 01', exact: true })).toBeVisible()
    await expect(page.getByRole('navigation', { name: 'Pagination' })).toHaveCount(0)
  } finally {
    for (const id of created) await page.request.delete('/api/v1/categories/' + id + '/', { headers })
  }
})
