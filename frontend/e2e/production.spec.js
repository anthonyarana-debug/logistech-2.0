import { test, expect } from '@playwright/test'
import { fileURLToPath } from 'node:url'
import { mkdirSync } from 'node:fs'
import { Workspace } from './workspace.js'

test.skip(process.env.PW_PRODUCTION !== 'true', 'Requires the isolated production rehearsal.')
const directory = new URL('../../docs/evidencias/fase7/', import.meta.url)
mkdirSync(directory, { recursive: true })

test('F7 compiled HTTPS application, security headers, cookies and private routes', async ({ page, context }) => {
  test.setTimeout(180000)
  const response = await page.goto('/')
  expect(response.status()).toBe(200)
  expect(response.headers()['content-security-policy']).toContain("connect-src 'self'")
  expect(response.headers()['permissions-policy']).toContain('camera=(self)')
  expect(response.headers()['x-frame-options']).toBe('DENY')
  expect(await page.evaluate(() => globalThis.isSecureContext)).toBe(true)
  const scripts = await page.locator('script[src]').evaluateAll(nodes => nodes.map(n => n.src))
  expect(scripts.length).toBeGreaterThan(0)
  expect(scripts.every(src => src.startsWith(`${locationOrigin()}/assets/`))).toBe(true)
  for (const [path, status] of [['/admin/', 404], ['/assets/missing.js', 404], ['/api/v1/missing/', 404], ['/api/v1/companies/', 401]]) {
    const result = await page.request.get(path)
    expect(result.status()).toBe(status)
    if (path.startsWith('/api/')) expect(result.headers()['content-type']).toContain('application/json')
  }
  const app = new Workspace(page)
  await app.login('root')
  const refresh = (await context.cookies()).find(c => c.name === 'lt_refresh')
  expect(refresh.secure && refresh.httpOnly).toBe(true)
  expect(refresh.sameSite).toBe('Lax')
  expect(await page.evaluate(() => document.cookie.includes('lt_refresh'))).toBe(false)
  await expect(page.getByRole('heading', { name: 'Latest records', exact: true })).toBeVisible()
  await page.screenshot({ path: fileURLToPath(new URL('compiled-https-dashboard.png', directory)), fullPage: true })
  const logout = page.waitForResponse(r => r.url().endsWith('/auth/logout/') && r.request().method() === 'POST')
  await page.getByRole('button', { name: 'Sign out', exact: true }).click()
  expect((await logout).status()).toBe(204)
  await expect(page).toHaveURL(/login$/)
  expect((await context.cookies()).some(c => c.name === 'lt_refresh')).toBe(false)
})

function locationOrigin() { return new URL(process.env.PW_BASE_URL).origin }

test('F7 real expiration and a single refresh through compiled React and Gunicorn', async ({ page, context }) => {
  test.setTimeout(450000)
  let expires = 0, successfulRefreshes = 0
  page.on('response', async response => {
    if (response.url().endsWith('/auth/login/') && response.status() === 200) {
      const body = await response.json()
      expires = JSON.parse(Buffer.from(body.access.split('.')[1], 'base64url').toString()).exp * 1000
    }
    if (response.url().endsWith('/auth/refresh/') && response.status() === 200) successfulRefreshes++
  })
  const app = new Workspace(page)
  await app.login('operator')
  await app.nav('Boxes')
  await expect.poll(() => expires).toBeGreaterThan(0)
  await expect.poll(() => Date.now(), { timeout: 315000, intervals: [1000] }).toBeGreaterThan(expires + 1000)
  // Overview mounts three API reads; the compiled client shares one renewal.
  await app.nav('Overview')
  await expect(page.getByRole('heading', { name: 'Latest records', exact: true })).toBeVisible()
  expect(successfulRefreshes).toBe(1)
  await context.clearCookies({ name: 'lt_refresh' })
  await page.route('**/api/v1/boxes/**', route => route.continue({
    headers: { ...route.request().headers(), authorization: 'Bearer invalid' },
  }))
  await app.nav('Boxes')
  await expect(page.getByRole('heading', { name: 'Your session has expired' })).toBeVisible()
  expect(successfulRefreshes).toBe(1)
})
