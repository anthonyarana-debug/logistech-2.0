import { test } from 'node:test'
import assert from 'node:assert/strict'
import { randomUUID } from 'node:crypto'

const user = { id: 'test-only', role: 'OPERATOR', company: { id: 'a' } }
const response = (body, status = 200, headers = {}) =>
  new Response(status === 204 ? null : JSON.stringify(body), { status, headers })
async function isolated(handler) {
  const previous = globalThis.fetch
  globalThis.fetch = handler
  const module = await import(`../src/services/api.js?test=${randomUUID()}`)
  return {
    module,
    cleanup: () => {
      globalThis.fetch = previous
    },
  }
}

test('restauración deduplicada; CSRF y access solo en cabecera', async () => {
  const calls = []
  const { module: api, cleanup } = await isolated(async (url, options) => {
    calls.push({ url, options })
    if (url.endsWith('/csrf/')) return response({ csrfToken: 'csrf-test' })
    if (url.endsWith('/refresh/')) return response({ access: 'access-test', user })
    return response([])
  })
  try {
    await Promise.all([api.restore(), api.restore(), api.restore()])
    assert.equal(calls.filter((c) => c.url.endsWith('/refresh/')).length, 1)
    await api.api('/boxes/')
    assert.equal(calls.at(-1).options.headers.Authorization, 'Bearer access-test')
    assert.equal(calls[1].options.headers['X-CSRFToken'], 'csrf-test')
    assert.equal(calls[1].options.credentials, 'same-origin')
    assert.deepEqual(api.snapshot().user, user)
  } finally {
    cleanup()
  }
})

test('dos 401 simultáneos comparten refresh; se reintenta una vez', async () => {
  let refreshes = 0
  const { module: api, cleanup } = await isolated(async (url, options) => {
    if (url.endsWith('/csrf/')) return response({ csrfToken: 'csrf-test' })
    if (url.endsWith('/refresh/')) return response({ access: `access-${++refreshes}`, user })
    return options.headers.Authorization === 'Bearer access-1' ? response({}, 401) : response([])
  })
  try {
    await api.restore()
    await Promise.all([api.api('/boxes/'), api.api('/categories/')])
    assert.equal(refreshes, 2)
  } finally {
    cleanup()
  }
})

test('refresh rechazado: termina sesión, sin bucle ni datos sensibles', async () => {
  let refreshes = 0
  const { module: api, cleanup } = await isolated(async (url) => {
    if (url.endsWith('/csrf/')) return response({ csrfToken: 'csrf-test' })
    if (url.endsWith('/refresh/'))
      return ++refreshes === 1 ? response({ access: 'test', user }) : response({}, 401)
    return response({}, 401)
  })
  try {
    await api.restore()
    await assert.rejects(api.api('/boxes/'))
    assert.equal(refreshes, 2)
    assert.equal(api.snapshot().user, null)
    assert.equal(api.snapshot().reason, 'expired')
  } finally {
    cleanup()
  }
})

test('logout concurrente a refresh: no resucita la identidad', async () => {
  let finish, started
  const gate = new Promise((resolve) => {
    started = resolve
  })
  const { module: api, cleanup } = await isolated(async (url) => {
    if (url.endsWith('/csrf/')) return response({ csrfToken: 'csrf-test' })
    if (url.endsWith('/refresh/')) {
      started()
      return new Promise((resolve) => {
        finish = () => resolve(response({ access: 'test', user }))
      })
    }
    return response(null, 204)
  })
  try {
    const restoring = api.restore()
    await gate
    const closing = api.logout()
    assert.equal(api.snapshot().user, null)
    finish()
    await Promise.all([restoring, closing])
    assert.equal(api.snapshot().user, null)
    assert.equal(api.snapshot().status, 'anonymous')
  } finally {
    cleanup()
  }
})

test('fallo de logout: conserva estado de error; 500 y 429 tienen mensajes seguros', async () => {
  const { module: api, cleanup } = await isolated(async (url) => {
    if (url.endsWith('/csrf/')) return response({ csrfToken: 'csrf-test' })
    return response({ detalle: 'TRACE INTERNO NO MOSTRAR' }, 500)
  })
  try {
    await assert.rejects(api.logout(), (error) => !error.message.includes('TRACE'))
    assert.equal(api.snapshot().user, null)
    assert.equal(api.snapshot().reason, 'logout-pending')
    const rate = new api.ApiError(429, { detalle: 'Demasiadas solicitudes.' }, '12')
    assert.equal(rate.retryAfter, 12)
  } finally {
    cleanup()
  }
})
