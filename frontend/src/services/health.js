import { t } from '../i18n/index.js'
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
      const error = new Error(t('the_api_cannot_confirm_its_connection_to_postgresql'))
      error.code = 'health_unavailable'
      throw error
    }
    return body
  } catch (error) {
    if (error.code === 'health_unavailable') throw error
    throw new Error(
      t("could_not_connect_to_the_service_check_your"),
      { cause: error },
    )
  } finally {
    clearTimeout(timeout)
  }
}
