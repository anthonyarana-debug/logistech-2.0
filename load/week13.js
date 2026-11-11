import http from 'k6/http'
import { check, fail, sleep } from 'k6'
import { Counter } from 'k6/metrics'
import { randomBytes } from 'k6/crypto'
import { b64encode } from 'k6/encoding'

const base = 'https://localhost/api/v1'
const fixture = JSON.parse(open('/fixture.json'))
const scenario = __ENV.SCENARIO || 'get'
const iterations = Number(__ENV.ITERATIONS || 100)
const vus = Number(__ENV.VUS || 1)
const profiles = [1, 2, 3, 100, 500, 1000, 2500, 5000, 10000, 25000, 50000]
if (!['get', 'crud', 'register', 'boxes', 'history', 'recovery'].includes(scenario) ||
    !profiles.includes(iterations) || !Number.isInteger(vus) || vus < 1 ||
    vus > Math.min(20, iterations) || (iterations > 100 && __ENV.LARGE_RUN !== 'isolated'))
  throw new Error('Use a supported profile and explicitly enable larger isolated runs.')

export const options = {
  scenarios: { [scenario]: { executor: 'shared-iterations', vus, iterations, maxDuration: '2m', gracefulStop: '5s' } },
  maxRedirects: 0,
  summaryTrendStats: ['avg', 'p(90)', 'p(95)', 'p(99)', 'max'],
  thresholds: { checks: [{ threshold: 'rate>0.99', abortOnFail: true, delayAbortEval: '5s' }], iterations: ['count==' + iterations] },
}
const created = new Counter('registrations_created')
const statuses = Object.fromEntries(['2xx', '3xx', '4xx', '5xx', 'connection'].map(key => [key, new Counter('responses_' + key)]))
const headers = { Authorization: 'Bearer ' + fixture.access, 'Content-Type': 'application/json' }
const tag = () => b64encode(randomBytes(18), 'rawurl')

function request(method, path, body, expected, requestHeaders = headers) {
  const response = http.request(method, base + path, body ? JSON.stringify(body) : null,
    { headers: requestHeaders, timeout: '5s', tags: { name: method + ' ' + path.split('/')[1] } })
  const group = response.status ? Math.floor(response.status / 100) + 'xx' : 'connection'
  statuses[group]?.add(1)
  if (!check(response, { ['HTTP ' + expected]: r => r.status === expected }))
    fail('Unexpected status ' + response.status + ' in ' + scenario)
  return response
}

export default function () {
  if (scenario === 'register') {
    const csrf = request('GET', '/auth/csrf/', null, 200, {}).json('csrfToken')
    request('POST', '/auth/register/', {
      email: 'week13-' + tag().toLowerCase() + '@example.test', password: 'T!9' + tag(),
    }, 201, { 'Content-Type': 'application/json', 'X-CSRFToken': csrf, Origin: 'https://localhost' })
    created.add(1)
  } else if (scenario === 'crud') {
    const row = request('POST', '/categories/', { name: 'QA ' + tag() }, 201).json()
    const path = '/categories/' + row.id + '/'
    request('GET', path, null, 200)
    request('PATCH', path, { description: 'Week 13 rehearsal' }, 200)
    request('DELETE', path, null, 204)
  } else if (scenario === 'boxes') {
    const row = request('POST', '/boxes/', { product: fixture.product, branch: fixture.branch, quantity: 1 }, 201).json()
    request('GET', '/boxes/' + row.id + '/qr/', null, 200)
    request('DELETE', '/boxes/' + row.id + '/', null, 204)
  } else {
    request('GET', { get: '/categories/?page=1', history: '/box-events/?page=1', recovery: '/health/' }[scenario], null, 200)
  }
  sleep(0.05)
}

export function handleSummary(data) {
  return { '/results/summary.json': JSON.stringify({ scenario, iterations, vus, ...data }, null, 2) }
}
