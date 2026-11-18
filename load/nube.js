// Prueba de carga contra el servidor en la nube (AWS Lightsail).
//
// Escenarios (SCENARIO):
//   register  -> crea usuarios reales en PostgreSQL (k6-<RUN_ID>-...@example.test)
//   login     -> inicia sesión con la cuenta indicada en EMAIL/PASSWORD
//   get       -> consulta paginada autenticada de categorías
//   mixed     -> 70 % GET, 20 % registro, 10 % salud (simula uso real)
//
// Modo profesor: N iteraciones repartidas entre VUS usuarios, con un tiempo máximo.
//   ITERATIONS=10000 VUS=10 DURATION=30s
//
// El servidor debe tener LOAD_TEST_MODE=true; si no, las respuestas 429 aparecen
// contadas como "cuota" (rate limit) y no como caída del servidor.
import http from 'k6/http'
import { check } from 'k6'
import { Counter, Trend } from 'k6/metrics'
import exec from 'k6/execution'

const BASE = (__ENV.BASE_URL || 'https://logistech.stackpe.online').replace(/\/$/, '')
const API = BASE + '/api/v1'
const SCENARIO = __ENV.SCENARIO || 'register'
const ITERATIONS = Number(__ENV.ITERATIONS || 100)
const VUS = Number(__ENV.VUS || 10)
const DURATION = __ENV.DURATION || '60s'
const RUN_ID = (__ENV.RUN_ID || String(Date.now())).toLowerCase().replace(/[^a-z0-9]/g, '')
const TAG = __ENV.TAG || `${SCENARIO}-${ITERATIONS}-${VUS}vu`
const OUT = __ENV.OUT_DIR || '/results'

if (!['register', 'login', 'get', 'mixed'].includes(SCENARIO)) throw new Error('SCENARIO inválido')
if (!(ITERATIONS >= 1 && VUS >= 1 && VUS <= ITERATIONS)) throw new Error('ITERATIONS/VUS inválidos')
if (SCENARIO !== 'register' && !(__ENV.EMAIL && __ENV.PASSWORD))
  throw new Error('SCENARIO get/login/mixed requiere EMAIL y PASSWORD de una cuenta con rol')

export const options = {
  scenarios: {
    [SCENARIO]: { executor: 'shared-iterations', vus: VUS, iterations: ITERATIONS, maxDuration: DURATION },
  },
  insecureSkipTLSVerify: __ENV.INSECURE === 'true',
  noCookiesReset: true, // cada VU conserva su cookie CSRF entre iteraciones
  summaryTrendStats: ['avg', 'min', 'med', 'p(90)', 'p(95)', 'p(99)', 'max'],
  // Umbrales informativos: no abortan, para poder documentar dónde empieza a fallar.
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<1000'],
  },
}

const created = new Counter('usuarios_creados')
const quota = new Counter('fallo_cuota_429')
const client4xx = new Counter('fallo_cliente_4xx')
const server5xx = new Counter('fallo_servidor_5xx')
const network = new Counter('fallo_red_timeout')
const registerTime = new Trend('tiempo_registro', true)

// Estado por VU (cada VU es un "trabajador" con su propio navegador y cookies).
let csrfToken = null
let access = null

function classify(res) {
  if (!res.status) network.add(1)
  else if (res.status === 429) quota.add(1)
  else if (res.status >= 500) server5xx.add(1)
  else if (res.status >= 400) client4xx.add(1)
}

function csrf() {
  if (csrfToken) return csrfToken
  const res = http.get(API + '/auth/csrf/', { tags: { name: 'GET csrf' }, timeout: '10s' })
  classify(res)
  if (res.status === 200) csrfToken = res.json('csrfToken')
  return csrfToken
}

function jsonHeaders(extra = {}) {
  return { 'Content-Type': 'application/json', 'X-CSRFToken': csrf() || '', Origin: BASE, Referer: BASE + '/', ...extra }
}

function register() {
  const n = exec.scenario.iterationInTest
  const email = `k6-${RUN_ID}-${n}@example.test`
  const res = http.post(API + '/auth/register/',
    // Contraseña aleatoria y distinta del correo (el validador rechaza las parecidas).
    JSON.stringify({ email, password: `Qz7#${Math.random().toString(36).slice(2, 12)}!Wm`, first_name: 'Carga', last_name: 'K6' }),
    { headers: jsonHeaders(), tags: { name: 'POST register' }, timeout: '30s' })
  classify(res)
  registerTime.add(res.timings.duration)
  if (check(res, { 'registro 201': r => r.status === 201 })) created.add(1)
}

function login() {
  const res = http.post(API + '/auth/login/', JSON.stringify({ email: __ENV.EMAIL, password: __ENV.PASSWORD }),
    { headers: jsonHeaders(), tags: { name: 'POST login' }, timeout: '30s' })
  classify(res)
  if (check(res, { 'login 200': r => r.status === 200 })) access = res.json('access')
  return res.status === 200
}

function getCategories() {
  if (!access && !login()) return
  const page = 1 + (exec.scenario.iterationInTest % Number(__ENV.PAGES || 1))
  let res = http.get(`${API}/categories/?page_size=25&page=${page}`,
    { headers: { Authorization: 'Bearer ' + access }, tags: { name: 'GET categories' }, timeout: '30s' })
  if (res.status === 401 && login()) // el access token dura 5 min
    res = http.get(`${API}/categories/?page_size=25&page=${page}`,
      { headers: { Authorization: 'Bearer ' + access }, tags: { name: 'GET categories' }, timeout: '30s' })
  classify(res)
  check(res, { 'consulta 200': r => r.status === 200 })
}

function health() {
  const res = http.get(API + '/health/', { tags: { name: 'GET health' }, timeout: '10s' })
  classify(res)
  check(res, { 'salud 200': r => r.status === 200 })
}

export default function () {
  if (SCENARIO === 'register') return register()
  if (SCENARIO === 'login') return login()
  if (SCENARIO === 'get') return getCategories()
  const roll = exec.scenario.iterationInTest % 10
  if (roll < 7) getCategories()
  else if (roll < 9) register()
  else health()
}

const val = (data, name, key = 'count') => (data.metrics[name] && data.metrics[name].values[key]) || 0
const ms = v => (Math.round(v * 100) / 100).toFixed(2)

export function handleSummary(data) {
  const d = data.metrics.http_req_duration.values
  const done = val(data, 'iterations')
  const row = {
    tag: TAG, fecha: new Date().toISOString(), servidor: BASE, escenario: SCENARIO,
    objetivo: ITERATIONS, completadas: done, vus: VUS, tiempo_max: DURATION,
    duracion_s: Math.round(data.state.testRunDurationMs) / 1000,
    http: val(data, 'http_reqs'), req_s: val(data, 'http_reqs', 'rate'),
    avg_ms: d.avg, p90_ms: d['p(90)'], p95_ms: d['p(95)'], p99_ms: d['p(99)'], max_ms: d.max,
    error_pct: 100 * val(data, 'http_req_failed', 'rate'),
    usuarios_creados: val(data, 'usuarios_creados'), run_id: RUN_ID,
    cuota_429: val(data, 'fallo_cuota_429'), cliente_4xx: val(data, 'fallo_cliente_4xx'),
    servidor_5xx: val(data, 'fallo_servidor_5xx'), red_timeout: val(data, 'fallo_red_timeout'),
  }
  row.resultado = done < ITERATIONS ? 'INCOMPLETO (no terminó en el tiempo)'
    : row.error_pct > 1 ? 'FALLIDO (errores > 1 %)'
    : row.p95_ms > 1000 ? 'LENTO (p95 > 1 s)' : 'APROBADO'
  const text = [
    '', `=== ${TAG} -> ${row.resultado} ===`,
    `Servidor: ${BASE}   Escenario: ${SCENARIO}   VUs: ${VUS}   Tiempo máx: ${DURATION}`,
    `Iteraciones: ${done}/${ITERATIONS} en ${row.duracion_s} s   HTTP: ${row.http}   ${ms(row.req_s)} req/s`,
    `Tiempo de respuesta ms -> prom ${ms(d.avg)}  p90 ${ms(d['p(90)'])}  p95 ${ms(d['p(95)'])}  p99 ${ms(d['p(99)'])}  máx ${ms(d.max)}`,
    `Errores: ${ms(row.error_pct)} %  (cuota/429: ${row.cuota_429}, cliente 4xx: ${row.cliente_4xx}, servidor 5xx: ${row.servidor_5xx}, red/timeout: ${row.red_timeout})`,
    SCENARIO === 'register' || SCENARIO === 'mixed'
      ? `Usuarios creados en BD: ${row.usuarios_creados}   (RUN_ID=${RUN_ID}, prefijo k6-${RUN_ID}-)` : '',
    '',
  ].join('\n')
  return {
    stdout: text,
    [`${OUT}/${TAG}-${RUN_ID}.json`]: JSON.stringify({ resumen: row, k6: data }, null, 2),
    [`${OUT}/${TAG}-${RUN_ID}.row.json`]: JSON.stringify(row),
  }
}
