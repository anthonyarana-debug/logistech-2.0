import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'
import { fileURLToPath } from 'node:url'
import { mkdirSync, readFileSync } from 'node:fs'
import { randomUUID } from 'node:crypto'
import { Workspace, demo } from './workspace.js'

const evidenceDirectory = new URL('../../docs/evidencias/fase6-bloque2/', import.meta.url)
mkdirSync(evidenceDirectory, { recursive: true })
const evidence = name => fileURLToPath(new URL(`${name}.png`, evidenceDirectory))
async function login(page, role) {
  const logged = page.waitForResponse(r => r.url().endsWith('/auth/login/') && r.status() === 200)
  await new Workspace(page).login(role)
  return (await (await logged).json()).access
}
const headers = token => ({ Authorization: `Bearer ${token}` })

test('F6B2 live QR lookup, printable label, uncertain-network replay and immutable history', async ({ page }) => {
  const token = await login(page, 'operator'), w = new Workspace(page)
  const box = await w.box()
  await expect(page.getByRole('img', { name: `QR code for ${box.internal_id}` })).toBeVisible()
  await page.screenshot({ path: evidence('box-qr-live'), fullPage: true })
  const download = page.waitForEvent('download')
  await page.getByRole('button', { name: 'Download printable label' }).click()
  const labelDownload = await download
  expect(labelDownload.suggestedFilename()).toBe(`${box.internal_id}.svg`)
  const labelPath = fileURLToPath(new URL('printable-label-live.svg', evidenceDirectory))
  await labelDownload.saveAs(labelPath)
  const labelPreview = await page.context().newPage()
  try {
    await labelPreview.goto(`data:image/svg+xml,${encodeURIComponent(readFileSync(labelPath, 'utf8'))}`)
    await labelPreview.locator('svg').screenshot({ path: evidence('printable-label-live') })
  } finally { await labelPreview.close() }
  await w.nav('Identify a box')
  for (const code of [`logistech:box:${box.qr_code}`, box.qr_code, box.internal_id]) {
    await page.getByLabel('QR or internal identifier').fill(code)
    const resolved = page.waitForResponse(r => r.url().includes('/identification/resolve/'))
    await page.getByRole('button', { name: 'Find box' }).click()
    expect((await resolved).status()).toBe(200)
    await expect(page.getByRole('heading', { name: box.internal_id, exact: true })).toBeVisible()
  }
  await page.getByLabel('QR or internal identifier').fill(randomUUID())
  await expect(page.getByRole('heading', { name: box.internal_id, exact: true })).toHaveCount(0)
  const missing = page.waitForResponse(r => r.url().includes('/identification/resolve/'))
  await page.getByRole('button', { name: 'Find box' }).click()
  expect((await missing).status()).toBe(404)
  await expect(page.getByRole('link', { name: 'Box details', exact: true })).toHaveCount(0)
  await page.getByLabel('QR or internal identifier').fill(box.internal_id)
  await page.getByRole('button', { name: 'Find box' }).click()
  await expect(page.getByRole('heading', { name: box.internal_id, exact: true })).toBeVisible()
  expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze()).violations).toEqual([])
  await page.screenshot({ path: evidence('identification-manual-live'), fullPage: true })
  await page.getByRole('link', { name: 'Box details', exact: true }).click()
  await page.locator('.qr-content').getByRole('link', { name: 'Receptions', exact: true }).click()
  await expect(page.getByRole('button', { name: 'Record reception', exact: true })).toBeVisible()
  await page.getByLabel('QR or internal identifier').fill(randomUUID())
  await expect(page.getByRole('button', { name: 'Record reception', exact: true })).toHaveCount(0)
  const missingReceptionBox = page.waitForResponse(r => r.url().includes('/identification/resolve/'))
  await page.getByRole('button', { name: 'Find box' }).click()
  expect((await missingReceptionBox).status()).toBe(404)
  await expect(page.getByRole('button', { name: 'Record reception', exact: true })).toHaveCount(0)
  await page.getByLabel('QR or internal identifier').fill(box.internal_id)
  await page.getByRole('button', { name: 'Find box' }).click()
  await expect(page.getByRole('button', { name: 'Record reception', exact: true })).toBeVisible()
  expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze()).violations).toEqual([])
  let firstKey, firstData
  await page.route('**/api/v1/receipts/', async route => {
    if (route.request().method() !== 'POST') return route.continue()
    firstKey = route.request().headers()['idempotency-key']; firstData = route.request().postDataJSON()
    // Labeled network-failure simulation: the live server commits before the browser loses its response.
    expect((await route.fetch()).status()).toBe(201)
    await route.abort('connectionfailed')
  })
  await page.getByRole('button', { name: 'Record reception', exact: true }).click()
  await expect(page.getByRole('alert')).toContainText('No connection')
  await page.unroute('**/api/v1/receipts/')
  const replay = page.waitForResponse(r => r.url().endsWith('/receipts/') && r.request().method() === 'POST')
  await page.getByRole('button', { name: 'Record reception', exact: true }).click()
  const replayResponse = await replay
  expect(replayResponse.status()).toBe(200)
  expect(replayResponse.request().headers()['idempotency-key']).toBe(firstKey)
  expect(replayResponse.request().postDataJSON()).toEqual(firstData)
  await expect(page.getByRole('status').filter({ hasText: 'Reception recorded.' })).toHaveText('Reception recorded.')
  const receipt = await replayResponse.json()
  const duplicate = await page.request.post('/api/v1/receipts/', { headers: { ...headers(token), 'Idempotency-Key': randomUUID() }, data: firstData })
  expect(duplicate.status()).toBe(409)
  const read = await page.request.get(`/api/v1/receipts/${receipt.id}/`, { headers: headers(token) })
  expect(read.status()).toBe(200)
  await page.screenshot({ path: evidence('reception-live-replay'), fullPage: true })
  await page.locator('.detail-panel').getByRole('link', { name: 'History', exact: true }).click()
  await expect(page).toHaveURL(new RegExp(`/app/history\\?box=${box.id}$`))
  await expect(page.getByRole('cell', { name: 'Reception recorded', exact: true })).toBeVisible()
  const receptionEvent = page.getByRole('row').filter({ has: page.getByRole('cell', { name: 'Reception recorded', exact: true }) })
  const eventDetails = receptionEvent.locator('details')
  await expect(eventDetails).not.toHaveAttribute('open', '')
  await eventDetails.locator('summary').click()
  await expect(eventDetails.locator('dt').filter({ hasText: /^Quantity$/ }).locator('..').locator('dd')).toHaveText('7')
  await expect(eventDetails.locator('dt').filter({ hasText: /^Result$/ }).locator('..').locator('dd')).toHaveText('Received')
  await expect(receptionEvent.locator('code')).toHaveCount(0)
  await eventDetails.locator('summary').click()

  const eventsResponse = await page.request.get(`/api/v1/box-events/?box=${box.id}`, { headers: headers(token) })
  expect(eventsResponse.status()).toBe(200)
  const events = await eventsResponse.json()
  expect(events.filter(e => e.event_type === 'RECEIPT_RECORDED')).toHaveLength(1)
  for (const method of ['patch', 'delete']) {
    const denied = await page.request[method](`/api/v1/box-events/${events[0].id}/`, { headers: headers(token), ...(method === 'patch' ? { data: { outcome: 'spoof' } } : {}) })
    expect(denied.status()).toBe(405)
  }
  expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze()).violations).toEqual([])
  await page.screenshot({ path: evidence('history-live-readonly'), fullPage: true })
  await page.goto(`/app/receptions?box=${box.id}`)
  await expect(page.getByText('This box already has a final status', { exact: false })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Record reception' })).toHaveCount(0)
})

test('F6B2 live tenant isolation, assigned-role access and simulated camera denial', async ({ page, browser }) => {
  const rootToken = await login(page, 'root')
  const foreignList = await page.request.get(`/api/v1/boxes/?company=${demo.companies[1]}`, { headers: headers(rootToken) })
  expect(foreignList.status()).toBe(200)
  const foreign = (await foreignList.json())[0]
  expect(foreign).toBeTruthy()
  const operatorContext = await browser.newContext(), operatorPage = await operatorContext.newPage()
  try {
    const operatorToken = await login(operatorPage, 'operator')
    await new Workspace(operatorPage).nav('Identify a box')
    await operatorPage.getByLabel('QR or internal identifier').fill(`logistech:box:${foreign.qr_code}`)
    const forbidden = operatorPage.waitForResponse(r => r.url().includes('/identification/resolve/'))
    await operatorPage.getByRole('button', { name: 'Find box' }).click()
    expect((await forbidden).status()).toBe(404)
    await expect(operatorPage.getByRole('heading', { name: /^Box unavailable\.?$/ })).toBeVisible()
    for (const path of [`/boxes/${foreign.id}/qr/`, `/boxes/${foreign.id}/label/`]) {
      expect((await operatorPage.request.get(`/api/v1${path}`, { headers: headers(operatorToken) })).status()).toBe(404)
    }
    await operatorPage.evaluate(() => {
      globalThis.__cameraRequests = 0
      globalThis.BarcodeDetector = class { detect() { return [] } }
      Object.defineProperty(globalThis.navigator, 'mediaDevices', { configurable: true, value: { getUserMedia: async () => {
        globalThis.__cameraRequests++
        throw new Error('Simulated permission denial for E2E')
      } } })
    })
    await expect(operatorPage.getByRole('button', { name: 'Start camera' })).toBeVisible()
    expect(await operatorPage.evaluate(() => globalThis.__cameraRequests)).toBe(0)
    await operatorPage.getByRole('button', { name: 'Start camera' }).click()
    await expect(operatorPage.getByRole('status')).toContainText('enter the code manually above')
    expect(await operatorPage.evaluate(() => globalThis.__cameraRequests)).toBe(1)
    for (const width of [320, 768, 1440]) {
      await operatorPage.setViewportSize({ width, height: 1000 })
      expect(await operatorPage.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
    }
    await operatorPage.screenshot({ path: evidence('camera-denial-SIMULATED'), fullPage: true })
  } finally { await operatorContext.close() }
  for (const endpoint of ['/receipts/', '/box-events/']) {
    expect((await page.request.get(`/api/v1${endpoint}`, { headers: headers(rootToken) })).status()).toBe(200)
    expect((await page.request.post(`/api/v1${endpoint}`, { headers: headers(rootToken), data: {} })).status()).toBe(endpoint === '/box-events/' ? 405 : 400)
  }
})

test('F6B2 company admin records a justified rejection; unassigned operator is denied by the API', async ({ page, browser }) => {
  const token = await login(page, 'admin'), w = new Workspace(page)
  const box = await w.box()
  await page.locator('.qr-content').getByRole('link', { name: 'Receptions', exact: true }).click()
  await page.getByLabel('Result', { exact: true }).selectOption('REJECTED')
  await page.getByRole('button', { name: 'Record reception' }).click()
  expect(await page.getByLabel('Rejection reason').evaluate(el => el.validity.valueMissing)).toBe(true)
  await page.getByLabel('Rejection reason').selectOption('DAMAGED')
  const saved = page.waitForResponse(r => r.url().endsWith('/receipts/') && r.request().method() === 'POST')
  await page.getByRole('button', { name: 'Record reception' }).click()
  const response = await saved
  expect(response.status()).toBe(201)
  const receipt = await response.json()
  expect(receipt.result).toBe('REJECTED')
  expect(receipt.reason).toBe('DAMAGED')
  expect(response.request().postDataJSON()).toEqual({ box: box.id, branch: box.branch, result: 'REJECTED', reason: 'DAMAGED' })
  const records = await page.request.get('/api/v1/receipts/', { headers: headers(token) })
  expect(records.status()).toBe(200)
  expect((await records.json()).every(r => r.company === box.company)).toBe(true)
  await expect(page.getByRole('status').filter({ hasText: 'Reception recorded.' })).toHaveText('Reception recorded.')
  await page.screenshot({ path: evidence('rejection-admin-live'), fullPage: true })
  const pendingContext = await browser.newContext(), pendingPage = await pendingContext.newPage()
  try {
    const pendingToken = await login(pendingPage, 'pending')
    for (const endpoint of ['/receipts/', '/box-events/', `/identification/resolve/?code=${box.qr_code}`]) {
      expect((await pendingPage.request.get(`/api/v1${endpoint}`, { headers: headers(pendingToken) })).status()).toBe(403)
    }
    const denied = await pendingPage.request.post('/api/v1/receipts/', {
      headers: { ...headers(pendingToken), 'Idempotency-Key': randomUUID() },
      data: { box: box.id, branch: box.branch, result: 'RECEIVED', reason: '' },
    })
    expect(denied.status()).toBe(403)
  } finally { await pendingContext.close() }
})
