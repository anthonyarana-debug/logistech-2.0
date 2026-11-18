"""Genera el Anexo D imprimible (HTML) con las corridas k6 en la nube del 18/11/2026.

Uso: python scripts/build_anexo_nube.py  ->  docs/ANEXO_D_PRUEBAS_NUBE.html
Abrir en el navegador y Ctrl+P (A4, sin encabezados) para imprimir o guardar como PDF.
"""

import glob
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "docs" / "evidencias" / "semana13-nube"
OUT = ROOT / "docs" / "ANEXO_D_PRUEBAS_NUBE.html"
DAY = "2026-11-18T11:3"  # corridas de esta tanda (desde las 11:30 UTC)

rows = []
for f in glob.glob(str(EVID / "*.row.json")):
    r = json.loads(Path(f).read_text(encoding="utf-8"))
    if r["fecha"] >= DAY:
        rows.append(r)
rows.sort(key=lambda r: r["fecha"])

LOCAL = {  # línea base local (PC del operador, 32 hilos), ver SEMANA_13_PRUEBAS_NUBE.md
    ("register", 50): "60 req/s · p95 0,18 s",
    ("register", 100): "60 req/s · p95 0,20 s",
    ("register", 200): "58 req/s · p95 0,24 s",
    ("register", 500): "62 req/s · p95 0,22 s",
    ("register", 1000): "63 req/s · p95 0,24 s",
    ("get", 1000): "174 req/s · p95 0,07 s",
}


def n(v, d=0):
    return f"{v:,.{d}f}".replace(",", " ").replace(".", ",")


def lima(iso):
    h, m = int(iso[11:13]), iso[14:16]
    return f"{(h - 5) % 24:02d}:{m}"


def table(items, kind):
    head = ("<tr><th>Hora Lima</th><th>Objetivo</th><th>Hechas</th><th>VUs</th><th>Duración</th>"
            "<th>Req/s</th><th>Mediana*</th><th>p95</th><th>Errores</th>"
            + ("<th>Filas en BD</th>" if kind == "register" else "")
            + "<th>Local (referencia)</th><th>Resultado</th></tr>")
    body = []
    for r in items:
        med = r.get("_med")
        body.append(
            "<tr>"
            f"<td>{lima(r['fecha'])}</td><td>{n(r['objetivo'])}</td><td>{n(r['completadas'])}</td>"
            f"<td>{r['vus']}</td><td>{n(r['duracion_s'], 1)} s</td><td>{n(r['req_s'], 2)}</td>"
            f"<td>{n(med / 1000, 2) + ' s' if med else '—'}</td><td>{n(r['p95_ms'] / 1000, 2)} s</td>"
            f"<td>{n(r['error_pct'], 2)} %</td>"
            + (f"<td>{n(r['usuarios_creados'])}</td>" if kind == "register" else "")
            + f"<td>{LOCAL.get((r['escenario'], r['objetivo']), '—')}</td>"
            f"<td><b>{escape(r['resultado'].split(' (')[0])}</b></td></tr>")
    return f"<table>{head}{''.join(body)}</table>"


def bars(items, key, label, fmt):
    if not items:
        return ""
    w, bh, gap, lw = 640, 20, 8, 110
    top = max(r[key] for r in items) or 1
    h = len(items) * (bh + gap) + 10
    parts = [f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{escape(label)}">']
    for i, r in enumerate(items):
        y = i * (bh + gap) + 5
        bw = max(2, (w - lw - 90) * r[key] / top)
        parts.append(f'<text x="{lw - 8}" y="{y + 15}" text-anchor="end" font-size="12">'
                     f'{r["escenario"]} {n(r["objetivo"])}</text>')
        parts.append(f'<rect x="{lw}" y="{y}" width="{bw:.1f}" height="{bh}" fill="#333"/>')
        parts.append(f'<text x="{lw + bw + 6:.1f}" y="{y + 15}" font-size="12">{fmt(r[key])}</text>')
    parts.append("</svg>")
    return f"<figure>{''.join(parts)}<figcaption>{escape(label)}</figcaption></figure>"


# Mediana del tiempo de espera del servidor (sin TLS ni red), desde el JSON completo de k6.
for r in rows:
    full = EVID / f"{r['tag']}-{r['run_id']}.json"
    try:
        k6 = json.loads(full.read_text(encoding="utf-8"))["k6"]
        r["_med"] = k6["metrics"]["http_req_duration"]["values"]["med"]
    except (OSError, KeyError, ValueError):
        r["_med"] = None

gets = [r for r in rows if r["escenario"] == "get"]
regs = [r for r in rows if r["escenario"] == "register" and r["tiempo_max"] == "300s"
        and r["cuota_429"] == 0]
quota = [r for r in rows if r["cuota_429"] > 0]
teacher = [r for r in rows if r["objetivo"] == 10000 and r["escenario"] == "register"]
written = sum(r["usuarios_creados"] for r in rows)
reads_ok = sum(r["completadas"] for r in gets)

html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>Anexo D — Pruebas en la nube</title>
<style>
@page {{ size: A4; margin: 18mm 16mm; }}
body {{ font-family: "Times New Roman", serif; font-size: 11pt; color: #000; background: #fff; max-width: 180mm; margin: auto; line-height: 1.35; }}
h1 {{ font-size: 15pt; margin: 0 0 4pt; }} h2 {{ font-size: 12.5pt; margin: 14pt 0 4pt; border-bottom: 1px solid #000; }}
table {{ border-collapse: collapse; width: 100%; font-size: 8.6pt; margin: 4pt 0 6pt; }}
th, td {{ border: 1px solid #000; padding: 2pt 3pt; text-align: center; }} th {{ background: #e6e6e6; }}
td:first-child {{ white-space: nowrap; }}
figure {{ margin: 4pt 0 8pt; }} figcaption {{ font-size: 9pt; font-style: italic; text-align: center; }}
.nota {{ font-size: 9pt; }} .box {{ border: 1px solid #000; padding: 5pt 7pt; margin: 6pt 0; }}
code {{ font-family: Consolas, monospace; font-size: 9pt; }}
.pb {{ page-break-before: always; }}
</style></head><body>
<h1>Anexo D — Pruebas de carga en la nube (AWS Lightsail)</h1>
<p class="nota">Fecha: 18 de noviembre de 2026. Servidor: <code>https://logistech.stackpe.online</code> (AWS Lightsail, Ohio, 2 vCPU, 4 GB; backend limitado a 1 vCPU, Gunicorn 2 procesos × 2 hilos; PostgreSQL 17 con TLS). Generador: k6 1.5.0 en Docker desde la PC del operador en Lima, por internet. Las corridas locales anteriores (Anexo B) se conservan solo como referencia.</p>

<div class="box"><b>Resumen.</b> En el servidor de producción se ejecutaron {n(reads_ok)} consultas autenticadas con 100 % de respuestas correctas (escalones 100, 1000, 5000, 10 000 y 25 000) y se escribieron <b>{n(written)} usuarios reales en PostgreSQL</b>. El cuello de botella medido es la CPU del backend al calcular el hash de contraseñas (PBKDF2 de 1 000 000 de iteraciones: 0,54–0,64 s por hash en Lightsail frente a 0,117 s en la PC local). Las lecturas, que no calculan hash, sostienen unas 31 solicitudes/s con p95 menor a 1 s.</div>

<h2>D.1 Local frente a nube</h2>
<table><tr><th></th><th>Local (PC del operador)</th><th>Nube (AWS Lightsail)</th></tr>
<tr><td>Dónde corre el backend</td><td>Docker en la misma PC que k6</td><td>Servidor público, acceso por internet y TLS</td></tr>
<tr><td>CPU disponible</td><td>32 hilos</td><td>1 vCPU (cuota del contenedor) en instancia con ráfagas</td></tr>
<tr><td>Hash PBKDF2 (1 M iteraciones)</td><td>0,117 s</td><td>0,54–0,64 s</td></tr>
<tr><td>Registros por segundo</td><td>≈ 60</td><td>≈ 0,9–1,0</td></tr>
<tr><td>Lecturas por segundo (20 VUs)</td><td>≈ 174</td><td>≈ 31</td></tr></table>

<h2>D.2 Lecturas autenticadas (GET de categorías, 20 VUs)</h2>
{table(gets, "get")}
<p class="nota">* Mediana del tiempo total por solicitud. El p95 de los escalones 100 y 1000 sube porque incluye los 20 inicios de sesión iniciales (cada uno calcula un hash). El 0,10 % de errores en 10 000 y 25 000 corresponde a respuestas 401 por vencimiento del token JWT de 5 minutos: k6 vuelve a iniciar sesión y repite la consulta, de modo que todas las consultas terminaron con 200. El escalón de 25 000 quedó INCOMPLETO al llegar al tiempo máximo de 600 s (19 441 consultas), sin errores: marca la capacidad sostenida del servidor.</p>
{bars(gets, "req_s", "Figura D1. Solicitudes por segundo por escalón de lectura", lambda v: n(v, 1) + " req/s")}

<h2>D.3 Escrituras reales en PostgreSQL (registro, 10 VUs)</h2>
{table(regs, "register")}
<p class="nota">Cada registro crea un usuario <code>k6-&lt;RUN_ID&gt;-&lt;n&gt;@example.test</code> con rol OPERADOR. Las filas se comprueban en pgAdmin con la consulta de D.6. No hubo errores 4xx, 5xx ni de red: la lentitud se debe a la CPU, no a caídas.</p>
{bars(regs, "p95_ms", "Figura D2. p95 (ms) por escalón de registro", lambda v: n(v / 1000, 1) + " s")}

<h2 class="pb">D.4 Caso del profesor: 10 000 registros en 30 s con 10 VUs</h2>
{table(teacher, "register") if teacher else "<p>Pendiente de ejecución.</p>"}
<p class="nota">Resultado esperado: INCOMPLETO. Con 1 vCPU y un hash de ≈ 0,6 s, el servidor puede crear alrededor de 1 usuario por segundo; en 30 s no es posible crear 10 000 sin reducir la seguridad del hash. En local el mismo caso llegó a 1806 registros (≈ 60/s). No es una caída: no hubo errores 5xx y el servidor siguió respondiendo.</p>

<h2>D.5 Significado de cada resultado y de cada tipo de fallo</h2>
<table><tr><th>Término</th><th>Significado</th></tr>
<tr><td>APROBADO</td><td>Todas las iteraciones terminaron, errores ≤ 1 % y p95 ≤ 1 s.</td></tr>
<tr><td>LENTO</td><td>Todo terminó sin errores, pero el p95 superó 1 s. Es un dato de capacidad, no una falla.</td></tr>
<tr><td>INCOMPLETO</td><td>Se alcanzó el tiempo máximo antes de terminar el volumen pedido (volumen mayor que la capacidad).</td></tr>
<tr><td>FALLIDO</td><td>Más de 1 % de solicitudes con error.</td></tr>
<tr><td>CORTADO</td><td>k6 se detuvo solo porque los errores superaron 5 % durante 10 s (protección para no tumbar el servidor).</td></tr>
<tr><td>Cuota (429)</td><td>El rate limit rechazó la solicitud (por ejemplo, 3 registros por hora por IP). Es una defensa, no una caída.</td></tr>
<tr><td>Cliente 4xx</td><td>Datos inválidos, CSRF o credenciales (400, 401, 403).</td></tr>
<tr><td>Servidor 5xx / red</td><td>Error interno o tiempo de espera agotado: indicaría saturación o caída. <b>En todas las corridas en la nube fue 0.</b></td></tr></table>
<p class="nota">El servidor no se cayó en ninguna corrida. Si ocurriera, Docker lo reinicia (<code>restart: unless-stopped</code>) y el healthcheck de <code>/api/v1/health/</code> lo verifica cada 15 s; los respaldos previos tienen verificación SHA-256.</p>

<h2>D.6 Seguridad durante las pruebas</h2>
<p>Los límites (rate limits) no se desactivaron para el público. Durante una ventana temporal (<code>LOAD_TEST_MODE=true</code>), solo las solicitudes que envían la cabecera secreta <code>X-Load-Test-Token</code> (64 caracteres, comparación en tiempo constante) omiten los límites. {"Una corrida con token inválido obtuvo " + n(quota[0]['cuota_429']) + " respuestas 429 de " + n(quota[0]['http']) + " solicitudes y solo " + n(quota[0]['usuarios_creados']) + " usuarios creados: el límite público siguió activo." if quota else ""} Al cerrar la ventana se vuelve a <code>LOAD_TEST_MODE=false</code>, se borra el token y se comprueba un 429 al cuarto registro sin token.</p>
<p><b>Verificación en pgAdmin:</b></p>
<p><code>SELECT count(*), min(created_at), max(created_at), max(created_at) - min(created_at) AS duracion FROM accounts_user WHERE email LIKE 'k6-1118070526%@example.test';</code></p>

<h2>D.7 Cuello de botella y solución propuesta</h2>
<p>Techo teórico de registro = CPU disponible ÷ costo del hash = 1 vCPU ÷ 0,54–0,64 s ≈ 1,6–1,9 registros/s; lo medido (≈ 1/s) incluye además Django, TLS y PostgreSQL. La seguridad del hash no se reduce. Soluciones, de menor a mayor costo: (1) subir la cuota del backend de 1 a 2 vCPU y 4 procesos Gunicorn dentro de la misma instancia (costo adicional US$0, duplica el techo teórico); (2) un plan de Lightsail con más vCPU o sin ráfagas; (3) varias instancias del backend detrás del proxy. Las lecturas no dependen del hash y ya cumplen 1000–5000 solicitudes en el servidor con 0 % de errores.</p>
</body></html>
"""
OUT.write_text(html, encoding="utf-8")
print(OUT)
