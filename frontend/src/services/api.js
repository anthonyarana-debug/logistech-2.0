import { t } from '../i18n/index.js'
// Access solo en este módulo en memoria. Ningún token se persiste en almacenamiento web.
const base = (import.meta.env?.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '')
let access = null
let state = { status: 'loading', user: null, error: null, reason: null }
let csrfPromise, refreshPromise, bootstrapPromise
let revision = 0
const listeners = new Set()
const pendingKey = 'logistech.logout-pending'
function pendingLogout(value) {
  try {
    if (value === undefined) return globalThis.sessionStorage?.getItem(pendingKey) === 'true'
    if (value) globalThis.sessionStorage?.setItem(pendingKey, 'true')
    else globalThis.sessionStorage?.removeItem(pendingKey)
  } catch {
    /* Almacenamiento opcional: nunca contiene tokens o identidad. */
  }
}
function publish(next) {
  state = { ...state, ...next }
  listeners.forEach((fn) => fn())
}
export const subscribe = (fn) => {
  listeners.add(fn)
  return () => listeners.delete(fn)
}
export const snapshot = () => state

function messages(value) {
  if (typeof value === 'string') return [value]
  if (Array.isArray(value)) return value.flatMap(messages)
  return value && typeof value === 'object' ? Object.values(value).flatMap(messages) : []
}
export class ApiError extends Error {
  constructor(status, data, retryAfter) {
    super(
      status >= 500
        ? t("the_service_could_not_complete_the_operation_please")
        : messages(data).join(' ') || t("the_operation_could_not_be_completed_2"),
    )
    this.status = status
    this.fields = data?.errores || {}
    this.retryAfter = Number(retryAfter) || null
  }
}
async function raw(path, { method = 'GET', data, token, signal, csrf } = {}) {
  let response
  try {
    response = await fetch(`${base}${path}`, {
      method,
      signal: signal
        ? AbortSignal.any([signal, AbortSignal.timeout(15000)])
        : AbortSignal.timeout(15000),
      credentials: 'same-origin',
      cache: 'no-store',
      headers: {
        Accept: 'application/json',
        ...(data !== undefined ? { 'Content-Type': 'application/json' } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(csrf ? { 'X-CSRFToken': csrf } : {}),
      },
      ...(data !== undefined ? { body: JSON.stringify(data) } : {}),
    })
  } catch (error) {
    if (signal?.aborted) throw error
    throw new ApiError(0, {
      detalle: t("no_connection_to_the_service_check_your_connection"),
    })
  }
  const body = response.status === 204 ? null : await response.json().catch(() => null)
  if (!response.ok) throw new ApiError(response.status, body, response.headers.get('Retry-After'))
  return body
}
async function csrf() {
  if (!csrfPromise)
    csrfPromise = raw('/auth/csrf/')
      .then((x) => x.csrfToken)
      .catch((error) => {
        csrfPromise = null
        throw error
      })
  return csrfPromise
}
async function authPost(path, data = {}) {
  try {
    return await raw(path, { method: 'POST', data, csrf: await csrf() })
  } catch (error) {
    if (error.status === 403) csrfPromise = null
    throw error
  }
}
function accept(session) {
  access = session.access
  publish({ status: 'ready', user: session.user, reason: null, error: null })
}
export async function renew() {
  if (refreshPromise) return refreshPromise
  const started = revision
  refreshPromise = authPost('/auth/refresh/')
    .then((session) => {
      if (started === revision) accept(session)
      return session
    })
    .catch((error) => {
      if (error.status === 401 && started === revision) {
        access = null
        publish({ status: 'anonymous', user: null, reason: 'expired', error: null })
      }
      throw error
    })
    .finally(() => {
      refreshPromise = null
    })
  return refreshPromise
}
export function restore(force = false) {
  if (force) bootstrapPromise = null
  if (!bootstrapPromise) {
    publish({ status: 'loading', error: null })
    bootstrapPromise = (pendingLogout() ? logout() : renew()).catch((error) => {
      if (error.status === 401)
        publish({ status: 'anonymous', user: null, reason: null, error: null })
      else publish({ status: 'error', user: null, error })
    })
  }
  return bootstrapPromise
}
export async function login(data) {
  await bootstrapPromise
  if (refreshPromise) await refreshPromise.catch(() => {})
  if (pendingLogout()) await logout()
  revision++
  accept(await authPost('/auth/login/', data))
}
export async function register(data) {
  return authPost('/auth/register/', data)
}
export async function logout() {
  pendingLogout(true)
  revision++
  access = null
  publish({ status: 'anonymous', user: null, reason: null, error: null })
  if (refreshPromise) await refreshPromise.catch(() => {})
  try {
    await authPost('/auth/logout/')
    pendingLogout(false)
  } catch (error) {
    publish({ status: 'error', user: null, error, reason: 'logout-pending' })
    throw error
  }
}
export async function api(path, options = {}) {
  const usedToken = access
  const started = revision
  try {
    return await raw(path, { ...options, token: usedToken })
  } catch (error) {
    if (error.status !== 401 || options.signal?.aborted || started !== revision) throw error
    if (!access || access === usedToken) await renew()
    if (started !== revision) throw new ApiError(401, { detalle: t("the_session_changed") })
    try {
      return await raw(path, { ...options, token: access })
    } catch (retryError) {
      if (retryError.status === 401) {
        access = null
        publish({ status: 'anonymous', user: null, reason: 'expired' })
      }
      throw retryError
    }
  }
}
export async function updateProfile() {
  const user = await api('/auth/me/')
  publish({ user })
  return user
}
