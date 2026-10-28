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
  await app.nav("Categories")
  await accessible(page)
  await page.getByRole('button', { name: "Create category", exact: true }).click()
  await accessible(page)
  await page.keyboard.press('Escape')
  await app.nav("Boxes")
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
    page.getByRole('heading', { name: "No matches for these filters" }),
  ).toBeVisible()
  await page.route('**/api/v1/boxes/**', (route) =>
    route.fulfill({ status: 403, json: { detalle: "You do not have permission to perform this operation." } }),
  )
  await page.getByRole('searchbox').fill('prohibido')
  await expect(page.getByRole('alert')).toContainText("You do not have permission")
  await accessible(page)
  await page.unroute('**/api/v1/boxes/**')
  await page.route('**/api/v1/boxes/**', (route) =>
    route.fulfill({ status: 500, json: { detalle: 'TRACE INTERNO NO MOSTRAR' } }),
  )
  await page.getByRole('searchbox').fill('fallo')
  await expect(page.getByRole('alert')).toContainText("The service could not complete")
  await expect(page.getByRole('alert')).not.toContainText('TRACE')
})
