import { expect } from '@playwright/test'
import { readFileSync } from 'node:fs'

export const demo = JSON.parse(
  readFileSync(
    process.env.PW_DEMO_FILE || new URL('../../.env.demo.json', import.meta.url),
    'utf8',
  ),
)
export const evidencePath = (name) =>
  `../docs/evidencias/${process.env.PW_EVIDENCE_PREFIX || 'fase5'}-${name}.png`
export class Workspace {
  constructor(page) {
    this.page = page
  }
  async login(role) {
    const p = this.page
    await p.goto('/login')
    await p.getByLabel('Correo electrónico').fill(demo.users[role].email)
    await p.getByLabel('Contraseña', { exact: true }).fill(demo.users[role].password)
    const response = p.waitForResponse(
      (r) => r.url().endsWith('/auth/login/') && r.request().method() === 'POST',
    )
    await p.getByRole('button', { name: 'Iniciar sesión', exact: true }).click()
    const result = await response
    // Respeta los límites reales entre ejecuciones, sin cambiarlos ni evadir IP.
    if (result.status() === 429) {
      const seconds = Number(result.headers()['retry-after']) || 60
      await expect
        .poll(() => Date.now(), { timeout: (seconds + 2) * 1000, intervals: [1000] })
        .toBeGreaterThan(Date.now() + seconds * 1000)
      await p.getByRole('button', { name: 'Iniciar sesión', exact: true }).click()
    } else expect(result.status()).toBe(200)
    await expect(p).toHaveURL(/\/app$/)
  }
  async nav(name) {
    if (await this.page.getByRole('button', { name: 'Abrir menú' }).isVisible())
      await this.page.getByRole('button', { name: 'Abrir menú' }).click()
    await this.page
      .getByRole('navigation', { name: /Navegación (del sistema|móvil)/ })
      .filter({ visible: true })
      .getByRole('link', { name, exact: true })
      .click()
  }
  async box() {
    const p = this.page
    await this.nav('Cajas')
    await p.getByRole('button', { name: 'Registrar caja', exact: true }).click()
    await expect(p.getByLabel('Producto', { exact: true }).locator('option')).not.toHaveCount(1)
    await p.getByLabel('Producto', { exact: true }).selectOption({ index: 1 })
    await p.getByLabel('Sucursal', { exact: true }).selectOption({ index: 1 })
    await p.getByLabel('Cantidad', { exact: true }).fill('7')
    const result = p.waitForResponse(
      (r) => r.url().endsWith('/boxes/') && r.request().method() === 'POST',
    )
    await p.getByRole('button', { name: 'Guardar caja' }).click()
    const response = await result
    expect(response.status()).toBe(201)
    const box = await response.json()
    await expect(p.getByRole('dialog')).toHaveCount(0)
    await p.getByRole('link', { name: box.internal_id, exact: true }).click()
    await expect(p.getByRole('heading', { name: 'Detalle de caja' })).toBeVisible()
    return box
  }
}
