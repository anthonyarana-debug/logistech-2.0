import test from 'node:test'
import assert from 'node:assert/strict'
import { catalogs, defaultLocale, formatDate, formatNumber, resultCount, t } from '../src/i18n/index.js'
import { ApiError } from '../src/services/api.js'

test('English is explicit; user data and template interpolation remain literal', () => {
  assert.equal(defaultLocale, 'en')
  assert.equal(t('every_box'), 'Every box.')
  assert.equal(t('view_box_label', { identifier: 'Caja <script>{name}</script>' }), 'View box Caja <script>{name}</script>')
  assert.throws(() => t('missing_key'), /Unknown message key/)
  assert.throws(() => t('view_box_label'), /Missing message argument/)
  for (const text of Object.values(catalogs.en)) assert.equal(typeof text, 'string')
})
test('English plural forms and numeric/date formatting use centralized locale', () => {
  assert.equal(resultCount(1, true), '1 box in this query')
  assert.equal(resultCount(2, true), '2 boxes in this query')
  assert.equal(resultCount(1, false), '1 category in this query')
  assert.equal(resultCount(0, false), '0 categories in this query')
  assert.equal(formatNumber(1234), '1,234')
  assert.match(formatDate('2026-10-27T17:00:00Z'), /Oct 27, 2026/)
})
test('English safe errors preserve the legacy API error contract', () => {
  const failure = new ApiError(500, { detalle: 'INTERNAL TRACE' })
  assert.equal(failure.message, 'The service could not complete the operation. Please try again.')
  assert.equal(failure.message.includes('TRACE'), false)
  const invalid = new ApiError(400, { errores: { quantity: ['Must be positive.'] } })
  assert.deepEqual(invalid.fields, { quantity: ['Must be positive.'] })
})
