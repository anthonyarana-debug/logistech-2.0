import test from 'node:test'
import assert from 'node:assert/strict'
import { readdirSync, readFileSync } from 'node:fs'
import { catalogs, t } from '../src/i18n/index.js'
import { canAdminister, canEditUser, dashboardKey } from '../src/services/operations.js'

test('operational navigation follows current role and assignment', () => {
  const operator = { id: 'o', role: 'OPERATOR', company: { id: 'a' } }
  const admin = { id: 'a', role: 'COMPANY_ADMIN', company: { id: 'a' } }
  const root = { id: 'r', role: 'SUPERADMIN', company: null }
  assert.equal(canAdminister(operator, 'users'), false)
  assert.equal(canAdminister(admin, 'companies'), false)
  assert.equal(canAdminister(admin, 'products'), true)
  assert.equal(canAdminister(root, 'companies'), true)
  assert.equal(canAdminister({ ...operator, company: null }, 'branches'), false)
  assert.equal(canAdminister({ ...admin, company: null }, 'users'), false)
})

test('user editor never offers self, superadmin or cross-company escalation', () => {
  const admin = { id: 'a', role: 'COMPANY_ADMIN', company: { id: 'tenant' } }
  assert.equal(canEditUser(admin, { id: 'b', role: 'OPERATOR', company: 'tenant' }), true)
  assert.equal(canEditUser(admin, { id: 'a', role: 'COMPANY_ADMIN', company: 'tenant' }), false)
  assert.equal(canEditUser(admin, { id: 'b', role: 'COMPANY_ADMIN', company: 'tenant' }), false)
  assert.equal(canEditUser(admin, { id: 'b', role: 'OPERATOR', company: 'other' }), false)
  assert.equal(canEditUser({ id: 'r', role: 'SUPERADMIN' }, { id: 's', role: 'SUPERADMIN' }), false)
})

test('dashboards resolve English catalog keys for the three roles', () => {
  assert.equal(dashboardKey('SUPERADMIN'), 'global_operations')
  assert.equal(dashboardKey('COMPANY_ADMIN'), 'company_operations')
  assert.equal(dashboardKey('OPERATOR'), 'operator_workspace')
})

test('all literal application message references resolve in the English catalog', () => {
  const directory = new URL('../src/', import.meta.url)
  for (const path of readdirSync(directory, { recursive: true })) {
    if (!/\.(jsx|js)$/.test(path)) continue
    const source = readFileSync(new URL(path.replaceAll('\\', '/'), directory), 'utf8')
    for (const match of source.matchAll(/\bt\(\s*['"]([a-z0-9_]+)['"]/g)) {
      assert.equal(typeof catalogs.en[match[1]], 'string', `${path}: ${match[1]}`)
    }
  }
  assert.equal(t('last_name'), 'Last name')
})
