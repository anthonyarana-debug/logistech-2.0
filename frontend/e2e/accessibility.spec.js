import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'
import { Workspace, evidencePath } from './workspace.js'

async function accessible(page) {
  const result = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
    .analyze()
  expect(
    result.violations.map((v) => ({ id: v.id, targets: v.nodes.map((n) => n.target) })),
  ).toEqual([])
}

test('accesibilidad automática, ampliación CSS 200%, vacío, 403 y 500', async ({ page }) => {
  test.setTimeout(180000)
  await page.goto('/')
  await accessible(page)
  await page.goto('/login')
  await accessible(page)
  await page.goto('/registro')
  await accessible(page)
  const app = new Workspace(page)
  await app.login('admin')
  await accessible(page)
  await app.nav('Categorías')
  await accessible(page)
  await page.getByRole('button', { name: 'Crear categoría', exact: true }).click()
  await accessible(page)
  await page.keyboard.press('Escape')
  await app.nav('Cajas')
  await accessible(page)
  await page.evaluate(() => {
    document.documentElement.style.zoom = '2'
  })
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy()
  await page.screenshot({ path: evidencePath('cajas-css-200'), fullPage: true })
  await page.evaluate(() => {
    document.documentElement.style.zoom = ''
  })
  await page.getByRole('searchbox').fill('sin-resultados-fase4')
  await expect(
    page.getByRole('heading', { name: 'No hay coincidencias con estos filtros' }),
  ).toBeVisible()
  await page.route('**/api/v1/boxes/**', (route) =>
    route.fulfill({ status: 403, json: { detalle: 'No tienes permiso para esta operación.' } }),
  )
  await page.getByRole('searchbox').fill('prohibido')
  await expect(page.getByRole('alert')).toContainText('No tienes permiso')
  await accessible(page)
  await page.unroute('**/api/v1/boxes/**')
  await page.route('**/api/v1/boxes/**', (route) =>
    route.fulfill({ status: 500, json: { detalle: 'TRACE INTERNO NO MOSTRAR' } }),
  )
  await page.getByRole('searchbox').fill('fallo')
  await expect(page.getByRole('alert')).toContainText('El servicio no pudo completar')
  await expect(page.getByRole('alert')).not.toContainText('TRACE')
})
