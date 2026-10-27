const apiBase = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '')

export async function getHealth() {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 6000)
  try {
    const response = await fetch(`${apiBase}/health/`, {
      signal: controller.signal,
      headers: { Accept: 'application/json' },
      cache: 'no-store',
    })
    const body = await response.json()
    if (!response.ok || body.estado !== 'disponible') {
      throw new Error('La API no puede confirmar la conexión con PostgreSQL.')
    }
    return body
  } finally {
    clearTimeout(timeout)
  }
}
