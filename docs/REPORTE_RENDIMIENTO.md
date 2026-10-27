# Rendimiento — Fase 5

Fecha: 27/10/2026, America/Lima. Pruebas **exclusivamente locales y controladas**, sin carga a terceros. Locust 2.47.0/gevent 26.9.0 en Python 3.13 aislado en .venv-load; versiones fijadas en load-requirements.txt. Destino permitido por código: solo `http://127.0.0.1:8001` del proyecto Compose logistech-f5, con DB/volumen/red separados del entorno de demostración.

## Método y recursos

Equipo identificado: Windows, AMD Ryzen 9 9950X, 16 núcleos/32 hilos y aproximadamente 15.15 GiB de RAM visible. Docker Linux 29.5.3 informa 32 CPU y 7.33 GiB de memoria. Backend Django runserver con hilos y PostgreSQL 17.11 privado; **no es Gunicorn/HTTPS/cloud**. El generador está en el mismo equipo. La memoria libre del host varió; no se capturó una serie continua de CPU/RAM del generador. Recursos de backend/DB muestreados aproximadamente cada cinco segundos con docker stats, no picos continuos.

Humo inicial: 2 usuarios, 1/s, 5 s de warmup y 14.49 s efectivos medidos; 17 solicitudes, 0 fallos, p95 26 ms. Solo después se ejecutaron A y B, en secuencia y sin suites intensivas simultáneas. Ambos siguieron PLAN: 30 s de calentamiento, objetivo de 3 min de medida, spawn 5/s y 10/s. CLI total 210 s. Se reinician contadores al segundo 30; duraciones reales difieren ligeramente del objetivo por arranque/cierre del generador y se reportan, no se redondean a 180 exactos.

Cada escenario tiene dos empresas DEMO, categoría/producto/sucursal por empresa y 50/100 operadores autorizados. Un usuario hace login HTTP real con CSRF; los demás usan AccessToken de fixtures, válido cinco minutos con la misma autenticación/roles/DB del servidor, y contraseña inutilizable. **No se probaron 50/100 logins simultáneos.** Esta separación evita convertir el límite legítimo de 5 logins/min/IP en una falsa medición de capacidad de inventario. No se cambió TTL, throttle, CSRF, NUM_PROXIES, validación ni permisos, ni se falsificó IP.

Al iniciar, todos consultan identidad autenticada. Tareas con espera aleatoria de 1–3 s: cajas (peso 7), categorías (3), ID exacto (3) y escritura limitada (1). Por usuario: como máximo un POST de caja y un PATCH, incluso ante error; sin generación ilimitada. Consultas y escrituras están aisladas por empresa. Al finalizar se desactivan exclusivamente los usuarios de ese namespace y se eliminan manifiestos privados; se conservan registros DEMO para auditoría, no se tocan inventarios previos. Un logout HTTP por ejecución revoca la sesión de la cuenta que inició sesión.

## Resultados reales

| Escenario | Usuarios configurados / activos en toda la medida | Spawn | Warmup | Medición real | Solicitudes | RPS | Media | p95 | Fallos HTTP |
|---|---|---|---|---|---|---|---|---|---|
| A | 50 / 50 | 5/s | 30 s | 179.45 s | 4 161 | 23.19 | 14.44 ms | 22 ms | 0 / 0.00% |
| B | 100 / 100 | 10/s | 30 s | 180.44 s | 8 368 | 46.37 | 19.23 ms | 38 ms | 0 / 0.00% |

La serie de usuarios autenticados muestreada cada segundo mantiene min=max=50 y min=max=100 durante la medida. Configuración, pico y activos medidos son campos separados. No son 100 pestañas ni 100 solicitudes/s, ni se demuestra el máximo de capacidad del sistema.

Ambos escenarios: login 200 y logout 204. A: 29 POST de caja en warmup y 21 en medida (50 total). B: 55 + 45 (100 total). En la medida: A tuvo 4 139 respuestas 200, 21 respuestas 201 y una 204; B, 8 322/45/1 respectivamente. No hubo 401, 403, 409, 429, 5xx, timeouts o fallos de red en esas mediciones. Los errores de rate limiting se estudian por separado: primera regresión E2E obtuvo 429 reales de refresh y los tests verifican ventanas/límites, sin mezclarlos con errores de capacidad.

| Muestra de recursos | A: pico observado | B: pico observado |
|---|---|---|
| CPU backend, escala docker (100%=un núcleo lógico) | 41.00% | 63.09% |
| Memoria backend | 91.27 MiB | 116.00 MiB |
| CPU PostgreSQL | 16.96% | 34.47% |
| Memoria PostgreSQL | 50.18 MiB | 55.24 MiB |

No se acreditó saturación de CPU/DB con esta mezcla. Límites demostrados: cuotas de autenticación y cache LocMem por proceso. PostgreSQL tiene max_connections=100 configurado; eso no significa 100 conexiones simultáneas medidas. Apertura de conexiones por request, listas sin paginar y crecimiento del dataset son riesgos para estudiar, **no cuellos de botella probados** en estos ensayos. No se midieron Web Vitals, memoria de navegadores, ancho de banda externo o rendimiento cloud; no se extrapolan estos números.

## Incidencia del exportador y calidad de la evidencia

Locust 2.47.0 en Windows lanzó `ValueError: I/O operation on closed file` desde su greenlet de CSV **al cerrar** A y B; el código de salida fue 0. Se conserva la excepción completa y no se declara ejecución del generador libre de incidentes. Las solicitudes ya habían terminado y los eventos finales registraron 4 161/8 368 con cero fallos HTTP. El último CSV periódico tenía 4 143/8 360 (18/8 solicitudes menos), por ser snapshot previo al cierre; no se presenta como total definitivo.

Se corrigió el wrapper: exportación síncrona CSV desde estadísticas Locust en test_stop, historial propio y JSON final oficial, sin el escritor periódico problemático. Un humo posterior aprobado verificó la corrección: 2 usuarios, 0 fallos HTTP y sin excepción de cierre; produce `_final.csv`, `_timeline.csv` y JSON final. En ese humo Locust añadió una segunda extensión y el original conserva el nombre `_stats_final.json.json`; el wrapper actual pasa el prefijo sin extensión para futuras ejecuciones. No se renombró ni reemplazó la evidencia. No se reemplazaron los originales de A/B por datos recreados. `resumen-escenarios.csv` consolida los **eventos finales originales** y coincide con los JSON de cierre; los CSV `_stats.csv` permanecen identificados como snapshots.

## Evidencia y reproducción

- [Consolidado CSV](evidencias/carga-fase5/resumen-escenarios.csv) y [resumen JSON con recursos](evidencias/fase5-carga-resumen.json).
- Prefijos A `a-50-20261027142759`, B `b-100-20261027143141`: `_summary.json`, `_resources.json`, `_stats.csv`, `_stats_history.csv`, `_failures.csv`, `_exceptions.csv`, `_console.txt` y HTML dentro de `evidencias/carga-fase5/`.
- Humo posterior `smoke-20261027143711`: exportador corregido y sin error de cierre. Se conserva también el humo inicial `smoke-20261027075410`.

Preparar el proyecto aislado según README, instalar load-requirements.txt en .venv-load y ejecutar:

```powershell
.venv-load/Scripts/python.exe load/run.py --scenario smoke
.venv-load/Scripts/python.exe load/run.py --scenario a-50
.venv-load/Scripts/python.exe load/run.py --scenario b-100
python scripts/resumir_carga_fase5.py
```

Ejecutar en secuencia, no contra producción ni sustituyendo host. Cada ejecución crea namespace y archivos nuevos; nunca sobrescribe las series anteriores. La latencia de Locust incluye la petición HTTP, serialización y acceso a DB locales; no mide tiempo de interacción humana ni renderizado React.
