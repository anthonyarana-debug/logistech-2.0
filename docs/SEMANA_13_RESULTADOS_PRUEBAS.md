# Revalidación técnica de Semana 13

Fecha de ejecución local 11 de noviembre de 2026. El código base es `53af6f3feb7c9a1df510632c7d8d2ca6e1f89f49`. Los cambios de verificación están en `d92ecad`. El [informe anterior](LOGISTECH_SEMANA_13_RESULTADOS_PRUEBAS.md) conserva los resultados previos por separado.

| Resultado | Entorno | Fecha | Evidencia | Incidencias |
|---|---|---|---|---|
| 316 pytest aprobadas | Docker y PostgreSQL real, árbol de trabajo montado en lectura | 11/11/2026 | [Salida](evidencias/semana13-integral/pytest-current.txt) | El primer intento usó una imagen QA anterior que solo descubrió 307 casos. El overlay fija el checkout real |
| 15 unitarias, ESLint y build aprobados | Frontend local | 11/11/2026 | [Unitarias](evidencias/semana13-integral/vitest.txt) · [Build](evidencias/semana13-integral/build.txt) | npm audit de producción devolvió cero hallazgos |
| Playwright, primera ejecución | Ensayo previo en 8453 | 11/11/2026 | [Salida inicial](evidencias/semana13-integral/playwright.txt) | 16 aprobadas, 4 fallidas y 2 omitidas. Cuotas reales de login/refresh e importación de módulo Vite inexistente en build compilado |
| Playwright, repetición focalizada | Ensayo nuevo en 8459 con sus propios datos, cuota normal y React compilado | 11/11/2026 | [Repetición](evidencias/semana13-integral/playwright-recheck.txt) | 5 aprobadas, incluidos 3 casos antes afectados y 2 verificaciones HTTPS de producción. El caso de Vite se conserva para desarrollo |
| Migraciones al día | PostgreSQL real y migración desde base nueva en ensayo 8459 | 11/11/2026 | [Comprobación de cambios](evidencias/semana13-integral/makemigrations.txt) | Sin cambios de esquema pendientes |
| Django check --deploy | Imagen de producción local | 11/11/2026 | [Salida](evidencias/semana13-integral/django-check.txt) | W005 y W021 por política HSTS de subdominios y preload |
| Ruff | Backend y generadores de documentos modificados | 11/11/2026 | Comando `.venv/Scripts/ruff.exe check --no-cache backend scripts/build_week13_integral.py scripts/week13_manual_figures.py` | Alcance aprobado. El barrido ampliado de scripts históricos reportó 27 observaciones preexistentes |
| Trivy 0.76.1 | Tres imágenes exactas de ensayo | 11/11/2026 | [Backend](evidencias/semana13-integral/trivy-backend.json) · [PostgreSQL](evidencias/semana13-integral/trivy-postgres.json) · [Proxy](evidencias/semana13-integral/trivy-proxy.json) | 0 CRITICAL, 47 HIGH backend y 1 HIGH proxy. Cero HIGH con parche indicado |
| Lanzador k6 de demostración | PowerShell 5.1, HTTPS, PostgreSQL aislado y página 400 | 11/11/2026 | [Resumen de 100 GET](evidencias/semana13-integral/k6-ps51-100.json) | El ensayo anterior de 5.000 se conserva sin repetirlo |

## Rendimiento histórico conservado

Los 5.000 GET con 20 VU, 0,97 s de pausa, p95 de 39,94 ms y cero errores duraron 249,827 s. El escalón de 2.500 con 20 VU, ritmo de 0,6 s y 26,18 req/s registró p95 de 734,64 ms y p99 de 2.385,55 ms. La repetición con 10 VU y 15,65 req/s registró p95 de 51,09 ms. Las muestras Docker antes/después no atribuyen la cola larga a PostgreSQL. El plan en página profunda midió 2,094 ms en otra corrida y solo representa esa consulta. Para atribuir la saturación se necesita muestreo continuo de CPU, espera, E/S, tiempos Gunicorn y PostgreSQL durante el pico. [Evidencias k6](evidencias/semana13-cierre/capacity.html)

## Revisión de riesgo de las imágenes

- El backend ejecuta Gunicorn como usuario de aplicación, sin capacidades Linux, con no-new-privileges y sin puerto publicado. El grupo de 36 hallazgos de util-linux corresponde a cuatro CVE repetidas entre nueve paquetes. Afectan operaciones privilegiadas de montaje y namespaces que la aplicación no ofrece. Debian mantiene hallazgos abiertos para la rama de esta imagen. [Seguimiento Debian](https://security-tracker.debian.org/tracker/source-package/util-linux)
- Los otros HIGH de backend afectan ncurses, SQLite, libacl, systemd y Archive::Tar. La API usa PostgreSQL, no procesa bases SQLite ni archivos tar del usuario, no abre terminales y no ejecuta systemd-homed. Las bibliotecas siguen instaladas y los informes conservan todas las entradas.
- El proxy incluye go-jose/v3 3.0.5, que no tiene parche para CVE-2026-116587. El v4 se fijó en 4.1.6 en el build de la entrega anterior. La configuración observada sirve archivos, reenvía HTTP y solicita TLS mediante ACME. No configura entrada JWK, middleware OIDC ni un servidor ACME público. El paquete sigue en el binario. [Aviso del mantenedor](https://github.com/go-jose/go-jose/security/advisories/GHSA-mgcc-cww5-fp2q)
- La revisión de alcance reduce exposición. Los resultados permanecen visibles y requieren seguimiento de las actualizaciones del proveedor.
