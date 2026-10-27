import { test, expect } from '@playwright/test'
import { Workspace, demo } from './workspace.js'
import { randomUUID } from 'node:crypto'

test('landing, responsive, teclado, movimiento reducido y rutas públicas', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Cada caja.')
  await page.getByRole('link', { name: 'Producto', exact: true }).click()
  await expect
    .poll(() => page.locator('#producto').evaluate((el) => el.getBoundingClientRect().top))
    .toBeLessThan(30)
  await page.goto('/')
  for (const width of [320, 390, 768, 1440]) {
    await page.setViewportSize({ width, height: 1000 })
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
    ).toBeTruthy()
    await page.screenshot({ path: `../docs/evidencias/fase4-landing-${width}.png`, fullPage: true })
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
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Esta ruta no tiene destino.')
  await page.goto('/403')
  await expect(page.getByRole('heading', { level: 1 })).toContainText(
    'Este acceso no está disponible para ti.',
  )
  await page.goto('/sesion-expirada')
  await expect(page.getByRole('heading', { name: 'Tu sesión ha expirado' })).toBeVisible()
})

test('registro real y validación de confirmación; login incorrecto', async ({ page }) => {
  await page.goto('/registro')
  await page.getByLabel('Nombre', { exact: true }).fill('Prueba E2E')
  await page.getByLabel('Correo electrónico').fill(`e2e-${randomUUID()}@example.test`)
  const password = `Prueba!${randomUUID()}`
  await page.getByLabel('Contraseña', { exact: true }).fill(password)
  await page.getByLabel('Confirmar contraseña', { exact: true }).fill(`${password}x`)
  await page.getByRole('button', { name: 'Crear cuenta de operador' }).click()
  await expect(page.getByRole('alert')).toContainText('no coinciden')
  await page.getByLabel('Confirmar contraseña', { exact: true }).fill(password)
  await page.getByRole('button', { name: 'Crear cuenta de operador' }).click()
  await expect(page.getByRole('heading', { name: 'Tu cuenta está creada.' })).toBeVisible()
  await page.getByRole('link', { name: 'Ir a iniciar sesión' }).click()
  await page.getByLabel('Correo electrónico').fill(`invalid-${randomUUID()}@example.test`)
  await page.getByLabel('Contraseña', { exact: true }).fill(password)
  await page.getByRole('button', { name: 'Iniciar sesión', exact: true }).click()
  await expect(page.getByRole('alert')).toBeVisible()
  await expect(page).toHaveURL(/login$/)
})

test('administrador: CRUD, integridad, filtros, sesión y responsive operacional', async ({
  page,
  context,
}) => {
  const app = new Workspace(page)
  await app.login('admin')
  await app.nav('Categorías')
  const name = `E2E ${randomUUID().slice(0, 8)}`
  await page.getByRole('button', { name: 'Crear categoría', exact: true }).click()
  await page.getByLabel('Nombre de categoría').fill(name)
  await page.getByRole('button', { name: 'Guardar categoría' }).click()
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await page.getByRole('button', { name: `Editar categoría ${name}`, exact: true }).click()
  await page.getByLabel('Nombre de categoría').fill(`${name} editada`)
  await page.getByRole('button', { name: 'Guardar categoría' }).click()
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await page
    .getByRole('button', { name: `Eliminar categoría ${name} editada`, exact: true })
    .click()
  await page.getByRole('button', { name: 'Eliminar definitivamente' }).click()
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await page.getByRole('button', { name: 'Eliminar categoría Instrumentos', exact: true }).click()
  await page.getByRole('button', { name: 'Eliminar definitivamente' }).click()
  await expect(page.getByRole('alert')).toBeVisible()
  await page.getByRole('button', { name: 'Cancelar', exact: true }).click()
  const box = await app.box()
  await page.getByRole('button', { name: 'Editar caja', exact: true }).click()
  await page.getByLabel('Cantidad', { exact: true }).fill('0')
  await page.getByRole('button', { name: 'Guardar caja' }).click()
  await expect(page.getByRole('dialog')).toBeVisible()
  expect(
    await page.getByLabel('Cantidad', { exact: true }).evaluate((el) => el.validity.rangeUnderflow),
  ).toBeTruthy()
  await page.getByLabel('Cantidad', { exact: true }).fill('9')
  await page.getByRole('button', { name: 'Guardar caja' }).click()
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await expect(page.locator('dd').filter({ hasText: /^9$/ })).toBeVisible()
  await app.nav('Cajas')
  await page.getByLabel('Buscar por', { exact: true }).selectOption('qr_code')
  await page.getByRole('searchbox').fill(box.qr_code)
  await expect(page.getByRole('table').locator('tbody tr')).toHaveCount(1)
  await page.getByLabel('Prioridad', { exact: true }).selectOption('HIGH')
  await expect(
    page.getByRole('heading', { name: 'No hay coincidencias con estos filtros' }),
  ).toBeVisible()
  await page.getByLabel('Prioridad', { exact: true }).selectOption('NORMAL')
  await page.getByLabel('Estado', { exact: true }).selectOption('REGISTERED')
  await expect(page.getByRole('table').locator('tbody tr')).toHaveCount(1)
  await page.getByLabel('Buscar por', { exact: true }).selectOption('internal_id')
  await page.getByRole('searchbox').fill(box.internal_id)
  await expect(page.getByRole('table').locator('tbody tr')).toHaveCount(1)
  await page.getByLabel('Buscar por', { exact: true }).selectOption('qr_code')
  await page.getByRole('searchbox').fill(box.qr_code)
  await expect(page.getByRole('table').locator('tbody tr')).toHaveCount(1)
  for (const width of [320, 390, 768, 1440]) {
    await page.setViewportSize({ width, height: 1000 })
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
    ).toBeTruthy()
    await page.screenshot({ path: `../docs/evidencias/fase4-cajas-${width}.png`, fullPage: true })
  }
  await page.getByRole('link', { name: box.internal_id, exact: true }).click()
  await page.getByRole('button', { name: 'Marcar recibida', exact: true }).click()
  await page.getByRole('button', { name: 'Confirmar estado' }).click()
  await expect(page.getByRole('heading', { name: 'Estado final protegido' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Eliminar caja', exact: true })).toHaveCount(0)
  await app.box()
  await page.getByRole('button', { name: 'Eliminar caja', exact: true }).click()
  await page.getByRole('button', { name: 'Eliminar definitivamente' }).click()
  await expect(page).toHaveURL(/\/app\/cajas$/)
  await page.reload()
  await expect(page.getByRole('heading', { name: 'Cada caja tiene identidad.' })).toBeVisible()
  expect(await page.evaluate(() => [localStorage.length, sessionStorage.length])).toEqual([0, 0])
  const cookies = await context.cookies()
  expect(cookies.find((c) => c.name === 'lt_refresh').httpOnly).toBeTruthy()
  await page.getByRole('button', { name: 'Cerrar sesión', exact: true }).click()
  await expect(page).toHaveURL(/login$/)
  await page.reload()
  await page.goto('/app')
  await expect(page).toHaveURL(/login$/)
})

test('operador asignado: lectura de categorías y caja autorizada', async ({ page }) => {
  const app = new Workspace(page)
  await app.login('operator')
  await app.nav('Categorías')
  await expect(page.getByRole('heading', { name: 'Clasificar para cuidar.' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Crear categoría', exact: true })).toHaveCount(0)
  await expect(page.getByRole('button', { name: /Eliminar categoría/ })).toHaveCount(0)
  await app.box()
  await expect(page.getByRole('button', { name: 'Eliminar caja', exact: true })).toHaveCount(0)
  await page.getByRole('button', { name: 'Marcar rechazada', exact: true }).click()
  await page.getByRole('button', { name: 'Confirmar estado' }).click()
  await expect(page.getByRole('heading', { name: 'Estado final protegido' })).toBeVisible()
})

test('operador pendiente: sin consultas de inventario privado', async ({ page }) => {
  const requests = []
  page.on('request', (r) => {
    if (/\/api\/v1\/(boxes|categories|references)\//.test(r.url())) requests.push(r.url())
  })
  await new Workspace(page).login('pending')
  await expect(
    page.getByRole('heading', { name: 'Tu cuenta está lista. Falta una asignación.' }),
  ).toBeVisible()
  await page.getByRole('button', { name: 'Comprobar asignación' }).click()
  expect(requests).toHaveLength(0)
  await page.getByRole('button', { name: 'Cerrar sesión', exact: true }).click()
})

test('superadmin: ámbito, referencias legibles y menú móvil', async ({ page }) => {
  const app = new Workspace(page)
  await app.login('root')
  await page.getByLabel('Ámbito empresarial').selectOption(demo.companies[1])
  await app.nav('Cajas')
  await expect(page.getByRole('table').locator('tbody tr')).toHaveCount(6)
  await page.getByRole('button', { name: 'Registrar caja', exact: true }).click()
  await expect(page.getByLabel('Producto', { exact: true }).locator('option')).toHaveCount(4)
  await page.keyboard.press('Escape')
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await page.setViewportSize({ width: 390, height: 844 })
  await page.getByRole('button', { name: 'Abrir menú' }).click()
  await expect(page.getByRole('dialog')).toBeVisible()
  await page.keyboard.press('Escape')
  await expect(page.getByRole('dialog')).not.toBeVisible()
  await app.nav('Vista general')
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
  await page.setViewportSize({ width: 1440, height: 1000 })
  await page
    .getByRole('link', { name: /Recepciones/ })
    .filter({ visible: true })
    .click()
  await expect(
    page.getByRole('heading', { name: 'El siguiente tramo está en desarrollo.' }),
  ).toBeVisible()
})

test('fallo de red simulado: error de servicio seguro y recuperable', async ({ page }) => {
  await page.route('**/api/v1/**', (route) => route.abort('connectionfailed'))
  await page.goto('/app')
  await expect(page.getByRole('alert')).toContainText('No hay conexión')
  await expect(page.getByRole('button', { name: 'Volver a intentar' })).toBeVisible()
  await page.unroute('**/api/v1/**')
  await page.getByRole('button', { name: 'Volver a intentar' }).click()
  await expect(page).toHaveURL(/login$/)
})
