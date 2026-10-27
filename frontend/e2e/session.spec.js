import { test, expect } from '@playwright/test'
import { Workspace } from './workspace.js'

test('access expira realmente a cinco minutos: renovación única y pérdida de refresh', async ({
  page,
  context,
}) => {
  test.setTimeout(450000)
  let expires = 0,
    refreshes = 0
  page.on('response', async (response) => {
    if (response.url().endsWith('/auth/login/') && response.status() === 200) {
      const body = await response.json()
      expires =
        JSON.parse(Buffer.from(body.access.split('.')[1], 'base64url').toString()).exp * 1000
    }
    if (response.url().endsWith('/auth/refresh/') && response.status() === 200) refreshes++
  })
  await new Workspace(page).login('operator')
  await expect.poll(() => expires).toBeGreaterThan(0)
  await expect
    .poll(() => Date.now(), { timeout: 315000, intervals: [1000] })
    .toBeGreaterThan(expires + 1000)
  // Dos solicitudes con el access vencido deben compartir una sola renovación.
  const result = await page.evaluate(async () => {
    const { api } = await import('/src/services/api.js')
    const responses = await Promise.all([api('/boxes/'), api('/categories/')])
    return responses.map(Array.isArray)
  })
  expect(result).toEqual([true, true])
  expect(refreshes).toBe(1)
  await context.clearCookies({ name: 'lt_refresh' })
  // Inyecta credencial inválida solo en esta petición; el servidor decide ambos 401.
  await page.route('**/api/v1/boxes/**', (route) =>
    route.continue({ headers: { ...route.request().headers(), authorization: 'Bearer invalid' } }),
  )
  await page.evaluate(async () => {
    const { api } = await import('/src/services/api.js')
    await api('/boxes/').catch(() => {})
  })
  await expect(page.getByRole('heading', { name: 'Tu sesión ha expirado' })).toBeVisible()
  expect(refreshes).toBe(1)
})
