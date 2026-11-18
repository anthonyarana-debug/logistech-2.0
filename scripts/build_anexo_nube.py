"""Genera el Anexo D (formato APA 7) con las corridas k6 en la nube del 18/11/2026.

Uso: python scripts/build_anexo_nube.py  ->  docs/ANEXO_D_PRUEBAS_NUBE.html
El PDF se obtiene con Edge/Chrome headless (ver scripts/pruebas.ps1 o el README del kit).
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
for r in rows:  # mediana del tiempo por solicitud, desde el JSON completo de k6
    try:
        k6 = json.loads((EVID / f"{r['tag']}-{r['run_id']}.json").read_text(encoding="utf-8"))["k6"]
        r["_med"] = k6["metrics"]["http_req_duration"]["values"]["med"]
    except (OSError, KeyError, ValueError):
        r["_med"] = None

LOCAL = {
    ("register", 50): "60 / 0,18", ("register", 100): "60 / 0,20", ("register", 200): "58 / 0,24",
    ("register", 500): "62 / 0,22", ("get", 1000): "174 / 0,07",
}


def n(v, d=0):
    return f"{v:,.{d}f}".replace(",", " ").replace(".", ",")


def lima(iso):
    return f"{(int(iso[11:13]) - 5) % 24:02d}:{iso[14:16]}"


def apa_table(num, title, head, body, note):
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in body)
    return (f'<div class="tabla"><p class="lab">Tabla {num}</p><p class="tit">{title}</p>'
            f"<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>"
            f'<p class="nota"><i>Nota.</i> {note}</p></div>')


def run_rows(items, writes):
    out = []
    for r in items:
        med = r["_med"]
        row = [lima(r["fecha"]), n(r["objetivo"]), n(r["completadas"]), n(r["duracion_s"], 1),
               n(r["req_s"], 2), n(med / 1000, 2) if med else "—", n(r["p95_ms"] / 1000, 2),
               n(r["error_pct"], 2)]
        if writes:
            row.append(n(r["usuarios_creados"]))
        row += [LOCAL.get((r["escenario"], r["objetivo"]), "—"), r["resultado"].split(" (")[0]]
        out.append(row)
    return out


def head(writes):
    h = ["Hora (Lima)", "Objetivo", "Completadas", "Duración (s)", "Solicitudes/s",
         "Mediana (s)", "p95 (s)", "Errores (%)"]
    return h + (["Filas en BD"] if writes else []) + ["Local: sol./s / p95 (s)", "Resultado"]


def figure(num, title, items, key, fmt, note):
    w, bh, gap, lw = 640, 20, 9, 120
    top = max(r[key] for r in items) or 1
    h = len(items) * (bh + gap) + 10
    p = [f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{escape(title)}">']
    for i, r in enumerate(items):
        y = i * (bh + gap) + 5
        bw = max(2, (w - lw - 90) * r[key] / top)
        p.append(f'<text x="{lw - 8}" y="{y + 15}" text-anchor="end" font-size="12" '
                 f'font-family="Times New Roman">{n(r["objetivo"])} solicitudes</text>')
        p.append(f'<rect x="{lw}" y="{y}" width="{bw:.1f}" height="{bh}" fill="#444"/>')
        p.append(f'<text x="{lw + bw + 6:.1f}" y="{y + 15}" font-size="12" '
                 f'font-family="Times New Roman">{fmt(r[key])}</text>')
    p.append("</svg>")
    return (f'<div class="figura"><p class="lab">Figura {num}</p><p class="tit">{title}</p>'
            f'{"".join(p)}<p class="nota"><i>Nota.</i> {note}</p></div>')


gets = [r for r in rows if r["escenario"] == "get"]
regs = [r for r in rows if r["escenario"] == "register" and r["tiempo_max"] == "300s"
        and r["cuota_429"] == 0]
quota = [r for r in rows if r["cuota_429"] > 0]
teacher = [r for r in rows if r["objetivo"] == 10000 and r["escenario"] == "register"]
written = sum(r["usuarios_creados"] for r in rows)
reads_ok = sum(r["completadas"] for r in gets)
q = quota[0] if quota else None

t1 = apa_table("D1", "Comparación del entorno local y del servidor en la nube",
               ["Aspecto", "Local (PC del operador)", "Nube (AWS Lightsail)"],
               [["Ubicación del backend", "Docker en la misma PC que k6", "Servidor público por internet con TLS"],
                ["CPU disponible", "32 hilos", "1 vCPU (cuota del contenedor), instancia con ráfagas"],
                ["Costo de un hash PBKDF2 (10<sup>6</sup> iteraciones)", "0,117 s", "0,54–0,64 s"],
                ["Registros por segundo", "≈ 60", "≈ 0,9–1,0"],
                ["Lecturas por segundo (20 VUs)", "≈ 174", "≈ 31"]],
               "El costo del hash se midió dentro del contenedor de producción sin carga (dos series). "
               "Las cifras locales provienen del Anexo B y se conservan solo como referencia.")
t2 = apa_table("D2", "Lecturas autenticadas de categorías en el servidor en la nube (20 usuarios virtuales)",
               head(False), run_rows(gets, False),
               "Tiempo máximo por escalón: 600 s. El p95 de los escalones de 100 y 1000 incluye los 20 "
               "inicios de sesión iniciales, cada uno con cálculo de hash. El 0,10 % de errores en 10 000 y "
               "25 000 corresponde a respuestas 401 por vencimiento del token JWT (5 min); k6 inicia sesión "
               "otra vez y repite la consulta, por lo que todas las consultas terminaron con código 200. "
               "El escalón de 25 000 alcanzó el tiempo máximo con 19 441 consultas y sin errores.")
t3 = apa_table("D3", "Escrituras reales en PostgreSQL mediante registro de usuarios (10 usuarios virtuales)",
               head(True), run_rows(regs, True),
               "Tiempo máximo por escalón: 300 s. Cada registro crea un usuario "
               "<code>k6-&lt;RUN_ID&gt;-&lt;n&gt;@example.test</code> con rol de operador. No hubo errores "
               "4xx, 5xx ni de red; la lentitud proviene de la CPU y no de caídas del servicio.")
t4 = apa_table("D4", "Caso solicitado por el docente: 10 000 registros en 30 s con 10 usuarios virtuales",
               head(True), run_rows(teacher, True),
               "El resultado INCOMPLETO es el esperado: con 1 vCPU y ≈ 0,6 s por hash el servidor crea "
               "alrededor de un usuario por segundo. En el entorno local el mismo caso alcanzó 1806 "
               "registros (≈ 60/s). No hubo errores 5xx y el servidor siguió respondiendo.")
t5 = apa_table("D5", "Interpretación de los resultados y de los tipos de fallo",
               ["Término", "Significado"],
               [["APROBADO", "Terminaron todas las iteraciones, errores ≤ 1 % y p95 ≤ 1 s."],
                ["LENTO", "Terminó sin errores, pero el p95 superó 1 s; es un dato de capacidad, no una falla."],
                ["INCOMPLETO", "Se alcanzó el tiempo máximo antes de completar el volumen solicitado."],
                ["FALLIDO", "Más del 1 % de las solicitudes devolvió error."],
                ["CORTADO", "k6 se detuvo porque los errores superaron el 5 % durante 10 s (protección del servidor)."],
                ["Cuota (429)", "El límite de solicitudes rechazó la petición; es una defensa, no una caída."],
                ["Cliente (4xx)", "Datos inválidos, CSRF o credenciales (400, 401, 403)."],
                ["Servidor (5xx) o red", "Error interno o tiempo de espera agotado; indicaría saturación o caída."]],
               "En todas las corridas en la nube los errores 5xx y de red fueron 0.")

f1 = figure("D1", "Solicitudes por segundo por escalón de lectura en la nube", gets, "req_s",
            lambda v: n(v, 1) + " sol./s",
            "El rendimiento se estabiliza en ≈ 31 solicitudes por segundo desde 5000 consultas.")
f2 = figure("D2", "Percentil 95 del tiempo de registro por escalón en la nube", regs, "p95_ms",
            lambda v: n(v / 1000, 1) + " s",
            "El p95 se mantiene entre 14 y 19 s porque las solicitudes esperan turno en la única vCPU.")

quota_text = (f" Como control, una corrida con token inválido obtuvo {q['cuota_429']} respuestas 429 de "
              f"{q['http']} solicitudes y solo {q['usuarios_creados']} usuarios creados, lo que demuestra que el "
              f"límite público permaneció activo.") if q else ""

html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>Anexo D. Pruebas de carga en la nube</title>
<style>
@page {{ size: A4; margin: 2.54cm; @top-right {{ content: counter(page); font: 12pt "Times New Roman"; }} }}
body {{ font-family: "Times New Roman", Times, serif; font-size: 12pt; line-height: 2; color: #000; background: #fff; max-width: 16cm; margin: auto; }}
h1 {{ font-size: 12pt; font-weight: bold; text-align: center; margin: 0; }}
h2 {{ font-size: 12pt; font-weight: bold; text-align: left; margin: 0; }}
p {{ margin: 0; text-indent: 1.27cm; text-align: left; }}
.sin {{ text-indent: 0; }}
.tabla, .figura {{ margin: 12pt 0; break-inside: avoid; }}
.lab {{ font-weight: bold; text-indent: 0; }}
.tit {{ font-style: italic; text-indent: 0; margin-bottom: 4pt; line-height: 1.5; }}
.nota {{ text-indent: 0; font-size: 10pt; line-height: 1.4; margin-top: 4pt; }}
table {{ border-collapse: collapse; width: 100%; font-size: 9pt; line-height: 1.25; }}
thead th {{ border-top: 1.5px solid #000; border-bottom: 1px solid #000; padding: 3pt 3pt; font-weight: bold; text-align: center; }}
td {{ padding: 2.5pt 3pt; text-align: center; vertical-align: top; }}
tbody tr:last-child td {{ border-bottom: 1.5px solid #000; }}
td:first-child {{ text-align: left; }}
code {{ font-family: Consolas, monospace; font-size: 9.5pt; }}
.sql {{ text-indent: 0; font-family: Consolas, monospace; font-size: 9.5pt; line-height: 1.4; margin: 6pt 0 6pt 1.27cm; }}
.ref p {{ text-indent: -1.27cm; padding-left: 1.27cm; }}
.pb {{ break-before: page; }}
</style></head><body>

<h1>Anexo D</h1>
<h1>Pruebas de Carga y Persistencia en el Servidor en la Nube (AWS Lightsail)</h1>

<h2>Propósito y Entorno</h2>
<p>Este anexo documenta las pruebas de carga ejecutadas el 18 de noviembre de 2026 contra el servidor de producción <code>https://logistech.stackpe.online</code>, a diferencia de las pruebas del Anexo B, que se realizaron en un entorno local y se conservan solo como referencia. El servidor es una instancia de AWS Lightsail en Ohio con 2 vCPU y 4 GB de memoria; el backend Django está limitado a 1 vCPU y atiende con Gunicorn (2 procesos y 2 hilos), detrás de Caddy, con PostgreSQL 17 conectado mediante TLS. El generador de carga fue k6 1.5.0 en Docker, ejecutado desde una PC en Lima a través de internet (Grafana Labs, s.f.). La Tabla D1 resume las diferencias entre ambos entornos.</p>
<p>En total se realizaron {n(reads_ok)} consultas autenticadas con respuesta correcta y se escribieron {n(written)} usuarios reales en la base de datos del servidor, sin errores 5xx ni de red en ninguna corrida.</p>
{t1}

<h2>Lecturas Autenticadas</h2>
<p>El escenario de lectura inicia sesión una vez por usuario virtual y consulta de forma paginada la lista de categorías. Los escalones de 1000, 5000 y 10 000 consultas terminaron con todas las respuestas correctas, lo que cumple el requisito de ejecutar entre 1000 y 5000 solicitudes en el servidor (Tabla D2 y Figura D1).</p>
{t2}
{f1}

<h2 class="pb">Escrituras Reales en PostgreSQL</h2>
<p>El escenario de registro crea usuarios nuevos a través de la API pública, con protección CSRF y validación de contraseñas. Cada alta exige calcular un hash PBKDF2 de un millón de iteraciones, valor recomendado para almacenar contraseñas de forma segura (Django Software Foundation, s.f.; OWASP Foundation, s.f.). Los escalones de 50, 100 y 200 registros confirmaron exactamente 50, 100 y 200 filas en PostgreSQL (Tabla D3 y Figura D2).</p>
{t3}
{f2}
<p>Las filas pueden verificarse en pgAdmin con la siguiente consulta, que devuelve 616 registros de la escalera:</p>
<p class="sql">SELECT count(*), min(created_at), max(created_at)<br>FROM accounts_user<br>WHERE email LIKE 'k6-1118070526%@example.test';</p>
{t4}

<h2>Interpretación de Resultados y Fallos</h2>
<p>La Tabla D5 define cada resultado y cada tipo de fallo registrado por el script de prueba. El servidor no se cayó en ninguna corrida. Si ocurriera una caída, Docker reinicia el contenedor de forma automática (<code>restart: unless-stopped</code>), el chequeo de salud de <code>/api/v1/health/</code> lo verifica cada 15 s y los respaldos previos se validan con SHA-256.</p>
{t5}

<h2>Seguridad durante las Pruebas</h2>
<p>Los límites de solicitudes no se desactivaron para el público. Durante una ventana temporal (<code>LOAD_TEST_MODE=true</code>) solo las solicitudes que envían la cabecera secreta <code>X-Load-Test-Token</code>, de 64 caracteres y comparada en tiempo constante, omiten dichos límites.{quota_text} Al cerrar la ventana se restablece <code>LOAD_TEST_MODE=false</code>, se elimina el token y se comprueba la respuesta 429 al cuarto registro sin token.</p>

<h2>Cuello de Botella y Solución Propuesta</h2>
<p>El techo teórico de registro equivale a la CPU disponible dividida entre el costo del hash: 1 vCPU ÷ 0,54–0,64 s ≈ 1,6–1,9 registros por segundo; el valor medido (≈ 1 por segundo) incluye además el trabajo de Django, TLS y PostgreSQL. Las instancias de Lightsail con rendimiento en ráfagas pueden reducir la CPU bajo carga sostenida (Amazon Web Services, s.f.). No se propone reducir la seguridad del hash. Las alternativas, de menor a mayor costo, son: (a) subir la cuota del backend de 1 a 2 vCPU y 4 procesos de Gunicorn en la misma instancia, sin costo adicional; (b) contratar un plan de Lightsail con más vCPU; y (c) ejecutar varias instancias del backend detrás del proxy. Las lecturas, que no calculan hash, ya sostienen ≈ 31 solicitudes por segundo con p95 menor a 1 s.</p>

<h2>Referencias</h2>
<div class="ref">
<p>Amazon Web Services. (s.f.). <i>Baseline CPU performance in Amazon Lightsail</i>. Recuperado el 18 de noviembre de 2026, de https://docs.aws.amazon.com/lightsail/latest/userguide/baseline-cpu-performance.html</p>
<p>Django Software Foundation. (s.f.). <i>Password management in Django</i>. Recuperado el 18 de noviembre de 2026, de https://docs.djangoproject.com/en/stable/topics/auth/passwords/</p>
<p>Grafana Labs. (s.f.). <i>Grafana k6 documentation</i>. Recuperado el 18 de noviembre de 2026, de https://grafana.com/docs/k6/latest/</p>
<p>OWASP Foundation. (s.f.). <i>Password storage cheat sheet</i>. Recuperado el 18 de noviembre de 2026, de https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html</p>
</div>
</body></html>
"""
OUT.write_text(html, encoding="utf-8")
print(OUT)
