import { test, expect } from '@playwright/test'
import { Workspace, demo, evidencePath } from './workspace.js'
import { randomUUID } from 'node:crypto'

test('landing, responsive, teclado, movimiento reducido y rutas públicas', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { level: 1 })).toContainText("Every box.")
  await page.getByRole('link', { name: "Product", exact: true }).click()
  await expect
    .poll(() => page.locator('#producto').evaluate((el) => el.getBoundingClientRect().top))
    .toBeLessThan(30)
  await page.goto('/')
  for (const width of [320, 390, 768, 1440]) {
    await page.setViewportSize({ width, height: 1000 })
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
    ).toBeTruthy()
    await page.screenshot({ path: evidencePath(`landing-${width}`), fullPage: true })
  }
  await page.keyboard.press('Tab')
  await expect(page.locator(':focus')).toBeVisible()
  expect(await page.locator(':focus').evaluate((el) => getComputedStyle(el).outlineStyle)).not.toBe(
    'none',
  )
  await page.emulateMedia({ reducedMotion: 'reduce' })
  expect(
    await page.evaluate(() => matchMedia('(prefers-reduced-motion: reduce)').matches),
  ).toBeTruthy()
  await page.goto('/no-existe')
  await expect(page.getByRole('heading', { level: 1 })).toContainText("This route has no destination.")
  await page.goto('/403')
  await expect(page.getByRole('heading', { level: 1 })).toContainText(
    "This access is unavailable to you.",
  )
  await page.goto('/sesion-expirada')
  await expect(page.getByRole('heading', { name: "Your session has expired" })).toBeVisible()
})

test('registro real y validación de confirmación; login incorrecto', async ({ page }) => {
  await page.goto('/registro')
  await page.getByLabel("First name", { exact: true }).fill('Prueba E2E')
  await page.getByLabel("Email address").fill(`e2e-${randomUUID()}@example.test`)
  const password = `Prueba!${randomUUID()}`
  await page.getByLabel("Password", { exact: true }).fill(password)
  await page.getByLabel("Confirm password", { exact: true }).fill(`${password}x`)
  await page.getByRole('button', { name: "Create operator account" }).click()
  await expect(page.getByRole('alert')).toContainText("do not match")
  await page.getByLabel("Confirm password", { exact: true }).fill(password)
  await page.getByRole('button', { name: "Create operator account" }).click()
  await expect(page.getByRole('heading', { name: "Your account has been created." })).toBeVisible()
  await page.getByRole('link', { name: "Go to sign in" }).click()
  await page.getByLabel("Email address").fill(`invalid-${randomUUID()}@example.test`)
  await page.getByLabel("Password", { exact: true }).fill(password)
  await page.getByRole('button', { name: "Sign in", exact: true }).click()
  await expect(page.getByRole('alert')).toBeVisible()
  await expect(page).toHaveURL(/login$/)
})

test('administrador: CRUD, integridad, filtros, sesión y responsive operacional', async ({
  page,
  context,
}) => {
  const app = new Workspace(page)
  await app.login('admin')
  await app.nav("Categories")
  const name = `E2E ${randomUUID().slice(0, 8)}`
  await page.getByRole('button', { name: "Create category", exact: true }).click()
  await page.getByLabel("Category name").fill(name)
  await page.getByRole('button', { name: "Save category" }).click()
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await page.getByRole('button', { name: `Edit category ${name}`, exact: true }).click()
  await page.getByLabel("Category name").fill(`${name} editada`)
  await page.getByRole('button', { name: "Save category" }).click()
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await page
    .getByRole('button', { name: `Delete category ${name} editada`, exact: true })
    .click()
  await page.getByRole('button', { name: "Delete permanently" }).click()
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await page.getByRole('button', { name: "Delete category Instrumentos", exact: true }).click()
  await page.getByRole('button', { name: "Delete permanently" }).click()
  await expect(page.getByRole('alert')).toBeVisible()
  await page.getByRole('button', { name: "Cancel", exact: true }).click()
  const box = await app.box()
  await page.getByRole('button', { name: "Edit box", exact: true }).click()
  await page.getByLabel("Quantity", { exact: true }).fill('0')
  await page.getByRole('button', { name: "Save box" }).click()
  await expect(page.getByRole('dialog')).toBeVisible()
  expect(
    await page.getByLabel("Quantity", { exact: true }).evaluate((el) => el.validity.rangeUnderflow),
  ).toBeTruthy()
  await page.getByLabel("Quantity", { exact: true }).fill('9')
  await page.getByRole('button', { name: "Save box" }).click()
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await expect(page.locator('dd').filter({ hasText: /^9$/ })).toBeVisible()
  await app.nav("Boxes")
  await page.getByLabel("Search by", { exact: true }).selectOption('qr_code')
  await page.getByRole('searchbox').fill(box.qr_code)
  await expect(page.getByRole('table').locator('tbody tr')).toHaveCount(1)
  await page.getByLabel("Priority", { exact: true }).selectOption('HIGH')
  await expect(
    page.getByRole('heading', { name: "No matches for these filters" }),
  ).toBeVisible()
  await page.getByLabel("Priority", { exact: true }).selectOption('NORMAL')
  await page.getByLabel("Status", { exact: true }).selectOption('REGISTERED')
  await expect(page.getByRole('table').locator('tbody tr')).toHaveCount(1)
  await page.getByLabel("Search by", { exact: true }).selectOption('internal_id')
  await page.getByRole('searchbox').fill(box.internal_id)
  await expect(page.getByRole('table').locator('tbody tr')).toHaveCount(1)
  await page.getByLabel("Search by", { exact: true }).selectOption('qr_code')
  await page.getByRole('searchbox').fill(box.qr_code)
  await expect(page.getByRole('table').locator('tbody tr')).toHaveCount(1)
  for (const width of [320, 390, 768, 1440]) {
    await page.setViewportSize({ width, height: 1000 })
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
    ).toBeTruthy()
    await page.screenshot({ path: evidencePath(`cajas-${width}`), fullPage: true })
  }
  await page.getByRole('link', { name: box.internal_id, exact: true }).click()
  await page.getByRole('button', { name: "Mark as received", exact: true }).click()
  await page.getByRole('button', { name: "Confirm status" }).click()
  await expect(page.getByRole('heading', { name: "Final status protected" })).toBeVisible()
  await expect(page.getByRole('button', { name: "Delete box", exact: true })).toHaveCount(0)
  await app.box()
  await page.getByRole('button', { name: "Delete box", exact: true }).click()
  await page.getByRole('button', { name: "Delete permanently" }).click()
  await expect(page).toHaveURL(/\/app\/cajas$/)
  await page.reload()
  await expect(page.getByRole('heading', { name: "Every box has an identity." })).toBeVisible()
  expect(await page.evaluate(() => [localStorage.length, sessionStorage.length])).toEqual([0, 0])
  const cookies = await context.cookies()
  expect(cookies.find((c) => c.name === 'lt_refresh').httpOnly).toBeTruthy()
  await page.getByRole('button', { name: "Sign out", exact: true }).click()
  await expect(page).toHaveURL(/login$/)
  await page.reload()
  await page.goto('/app')
  await expect(page).toHaveURL(/login$/)
})

test('operador asignado: lectura de categorías y caja autorizada', async ({ page }) => {
  const app = new Workspace(page)
  await app.login('operator')
  await app.nav("Categories")
  await expect(page.getByRole('heading', { name: "Classify to care." })).toBeVisible()
  await expect(page.getByRole('button', { name: "Create category", exact: true })).toHaveCount(0)
  await expect(page.getByRole('button', { name: /Delete category/ })).toHaveCount(0)
  await app.box()
  await expect(page.getByRole('button', { name: "Delete box", exact: true })).toHaveCount(0)
  await page.getByRole('button', { name: "Mark as rejected", exact: true }).click()
  await page.getByRole('button', { name: "Confirm status" }).click()
  await expect(page.getByRole('heading', { name: "Final status protected" })).toBeVisible()
})

test('operador pendiente: sin consultas de inventario privado', async ({ page }) => {
  const requests = []
  page.on('request', (r) => {
    if (/\/api\/v1\/(boxes|categories|references)\//.test(r.url())) requests.push(r.url())
  })
  await new Workspace(page).login('pending')
  await expect(
    page.getByRole('heading', { name: "Your account is ready. Assignment pending." }),
  ).toBeVisible()
  await page.getByRole('button', { name: "Check assignment" }).click()
  expect(requests).toHaveLength(0)
  await page.getByRole('button', { name: "Sign out", exact: true }).click()
})

test('superadmin: ámbito, referencias legibles y menú móvil', async ({ page }) => {
  const app = new Workspace(page)
  await app.login('root')
  await page.getByLabel("Company scope").selectOption(demo.companies[1])
  await app.nav("Boxes")
  await expect(page.getByRole('table').locator('tbody tr')).toHaveCount(6)
  await page.getByRole('button', { name: "Register box", exact: true }).click()
  await expect(page.getByLabel("Product", { exact: true }).locator('option')).toHaveCount(4)
  await page.keyboard.press('Escape')
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await page.setViewportSize({ width: 390, height: 844 })
  await page.getByRole('button', { name: "Open menu" }).click()
  await expect(page.getByRole('dialog')).toBeVisible()
  await page.keyboard.press('Escape')
  await expect(page.getByRole('dialog')).not.toBeVisible()
  await app.nav("Overview")
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
  await page.setViewportSize({ width: 1440, height: 1000 })
  await page
    .getByRole('link', { name: /Receptions/ })
    .filter({ visible: true })
    .click()
  await expect(
    page.getByRole('heading', { name: "The next stage is in development." }),
  ).toBeVisible()
})

test('fallo de red simulado: error de servicio seguro y recuperable', async ({ page }) => {
  await page.route('**/api/v1/**', (route) => route.abort('connectionfailed'))
  await page.goto('/app')
  await expect(page.getByRole('alert')).toContainText("No connection")
  await expect(page.getByRole('button', { name: "Try again" })).toBeVisible()
  await page.unroute('**/api/v1/**')
  await page.getByRole('button', { name: "Try again" }).click()
  await expect(page).toHaveURL(/login$/)
})
