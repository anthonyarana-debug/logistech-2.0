import { api } from './api.js'

export const resolveCode = (code, options) => api(`/identification/resolve/?${new URLSearchParams({ code: code.trim() })}`, options)
export const receiptBody = (box, result, reason) => ({ box: box.id, branch: box.branch, result, reason: result === 'RECEIVED' ? '' : reason })
// A retry of the same submission retains its key, including after an uncertain network failure.
export function receiptAttempt(previous, data, uuid = () => globalThis.crypto.randomUUID()) {
  const fingerprint = JSON.stringify(data)
  return previous?.fingerprint === fingerprint ? previous : { fingerprint, key: uuid(), data }
}
export async function downloadLabel(id, internalId) {
  const blob = await api(`/boxes/${id}/label/`, { responseType: 'blob' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `${internalId}.svg`
  anchor.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
