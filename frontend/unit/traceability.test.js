import test from 'node:test'
import assert from 'node:assert/strict'
import { randomUUID } from 'node:crypto'
import { receiptAttempt, receiptBody } from '../src/services/traceability.js'

test('reception command only contains authorized input fields; received clears rejection reason', () => {
  const box = { id: 'box', branch: 'branch', company: 'tenant', actor: 'spoof', created_at: 'spoof' }
  assert.deepEqual(receiptBody(box, 'RECEIVED', 'DAMAGED'), { box: 'box', branch: 'branch', result: 'RECEIVED', reason: '' })
  assert.deepEqual(receiptBody(box, 'REJECTED', 'DAMAGED'), { box: 'box', branch: 'branch', result: 'REJECTED', reason: 'DAMAGED' })
})

test('uncertain reception retries retain the same key and payload; changed commands receive a fresh key', () => {
  let minted = 0
  const uuid = () => `key-${++minted}`
  const data = receiptBody({ id: 'box', branch: 'branch' }, 'REJECTED', 'DAMAGED')
  const initial = receiptAttempt(null, data, uuid)
  assert.strictEqual(receiptAttempt(initial, { ...data }, uuid), initial)
  assert.equal(minted, 1)
  assert.notEqual(receiptAttempt(initial, { ...data, reason: 'OTHER' }, uuid).key, initial.key)
  assert.notEqual(receiptAttempt(initial, { ...data, box: 'different-box' }, uuid).key, initial.key)
})

test('authenticated SVG download preserves idempotency headers over session renewal without putting tokens in URL', async () => {
  const previous = globalThis.fetch, calls = []
  let refreshes = 0
  globalThis.fetch = async (url, options) => {
    calls.push({ url, options })
    if (url.endsWith('/csrf/')) return Response.json({ csrfToken: 'test-csrf' })
    if (url.endsWith('/refresh/')) return Response.json({ access: `test-${++refreshes}`, user: { id: 'u' } })
    if (options.headers.Authorization === 'Bearer test-1') return Response.json({}, { status: 401 })
    return new Response('<svg xmlns="http://www.w3.org/2000/svg"/>', { headers: { 'Content-Type': 'image/svg+xml' } })
  }
  try {
    const api = await import(`../src/services/api.js?trace=${randomUUID()}`)
    await api.restore()
    const blob = await api.api('/boxes/box/label/', { responseType: 'blob', headers: { 'Idempotency-Key': 'stable-test-key' } })
    assert.match(await blob.text(), /^<svg/)
    const labels = calls.filter(c => c.url.endsWith('/label/'))
    assert.equal(labels.length, 2)
    assert.equal(labels[1].options.headers['Idempotency-Key'], 'stable-test-key')
    assert.equal(labels[1].options.headers.Authorization, 'Bearer test-2')
    assert.equal(labels.every(c => !c.url.includes('test-')), true)
  } finally { globalThis.fetch = previous }
})
