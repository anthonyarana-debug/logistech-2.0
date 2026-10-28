# Evidencias locales F7 — 28/10/2026

Estas son ejecuciones reales sobre el entorno aislado de producción local, no AWS.
Los archivos privados, credenciales y dumps no se incluyen. Los tiempos son de
esta máquina; no representan capacidad ni SLA del futuro servidor.

| Archivos | Qué permiten comprobar |
|---|---|
| `backend-baseline.txt`, `backend-final.txt` | Línea base273 y suite final307 aprobadas sobre PostgreSQL real |
| `frontend-unit.txt`, `frontend-lint.txt`, `frontend-build.txt` | 15 unitarias, lint y compilación |
| `backend-lint.txt`, `pip-check.txt` | Ruff y consistencia de dependencias de la imagen QA |
| `e2e-initial.json/txt` | Primera ejecución 7pass/1fallo de espera de logout; fallo conservado |
| `e2e-logout-recheck.txt` | Caso corregido aprobado esperando HTTP204 |
| `e2e-five-cases.json/txt` | 5 aprobados después del parche DRF; expiración real, QR/recepción/historia, roles/aislamiento, axe/responsive |
| `e2e-patched-proxy.json/txt` | Smoke adicional aprobado tras última compilación proxy/DB |
| `local-verification.json` | 10 checks, configuración pública solo renderizada, origen distinto rechazado y CA local verificada; warnings HSTS visibles |
| `tls-initial.json`, `https-routes.json` | Registro inicial del fallo admin200 y corrección a404, assets/API/static/SPA y cadena TLS |
| `database-restore.json` | Manifiestos de8 modelos origen/restauración nueva; permisos, triggers y TLS |
| `persistence-recreation.json` | Igualdad de manifiestos antes/después de reemplazar imágenes sin quitar volumen |
| `encryption.json` | Roundtrip idéntico de scripts CMS y rechazo de copia alterada |
| `auxiliary-checks.json`, `audit-unit.txt`, `secret-audit.json` | CFN offline, shell, conservación académica y auditoría de publicación |
| `npm-audit.json` | npm audit de dependencias de producción sin hallazgos |
| `vulnerabilities-backend-final.json` | Scan backend final:0critical/44high, sin HIGH con parche indicado |
| `vulnerabilities-proxy-patched.json` | Scan proxy final:0critical/1high sin parche indicado |
| `vulnerabilities-postgres-patched.json` | Scan PostgreSQL final:3critical/69high; gate retenido, no resultado limpio |
| Otros `vulnerabilities-*.json` | Scans iniciales/intermedios íntegros, conservados para contrastar correcciones |
| `compiled-https-dashboard.png`, `regression/*` | Capturas reales del ensayo F7; nombres SIMULATED identifican denegación de cámara simulada |
| `manifest-sha256.json` | Integridad de evidencias de este directorio; no contiene hashes ni archivos de secretos |

Trivy0.76.1 conserva informes completos HIGH/CRITICAL sin ignorar unfixed. Las
ocurrencias se cuentan por paquete/CVE, no como vulnerabilidades únicas. Los logs
de presentación normalizan finales de línea y espacios finales; los resultados
no se editan y los originales completos permanecen en el directorio QA ignorado.
El manifest usa bytes canónicos de los blobs Git (texto LF), para evitar diferencias
de autocrlf entre sistemas. La revisión
del proveedor y el bloqueo se explican en [CHECKLIST_SEGURIDAD_F7](../../CHECKLIST_SEGURIDAD_F7.md).

Repetición controlada: `python scripts/verify_f7.py` contra la pila F7 previamente
instalada. Backend con `compose.production-tests.yml --profile qa run --rm -T tests`;
E2E requiere variables de ensayo documentadas en el informe y credenciales locales
ignoradas. Las cuotas siguen activas: no reiniciar ni borrar contadores para forzar
aprobación. La ejecución manual GitHub del workflow no se ha realizado.
