# Evidencias de Semana 13

| Periodo | Evidencia | Alcance |
|---|---|---|
| Entrega 25 % | [Pruebas y metodología](PRUEBAS.md) | Resultados de las primeras fases, con entorno propio |
| F6 | [Recepción y trazabilidad](INFORME_FASE_6_BLOQUE_2.md) | QR, recepción, historial y aislamiento |
| Cierre Semana 13 | [k6 JSON](evidencias/semana13-cierre/capacity.json) · [CSV](evidencias/semana13-cierre/capacity.csv) · [HTML](evidencias/semana13-cierre/capacity.html) | Escalones de carga, abortos, planes SQL y recursos |
| Cierre Semana 13 | [Restauración](evidencias/semana13-cierre/recovery.json) · [Cifrado](evidencias/semana13-cierre/encryption.txt) · [Fallos y rollback](evidencias/semana13-cierre/faults.json) | Ensayos locales controlados |
| Revalidación integral | [Resultados](SEMANA_13_RESULTADOS_PRUEBAS.md) | Ejecuciones nuevas separadas de las históricas |
| AWS público | [Evidencia HTTPS](evidencias/semana13-integral/cloud-public.txt) · [Despliegue](SEMANA_13_DESPLIEGUE_AWS.md) | Landing, salud, login de administrador y lectura paginada |

El manual visual distingue las capturas de la fuente académica, las de Playwright y las de fallos simulados. Los recuadros señalan acciones y campos con números que se explican debajo.

## Aceptación F7 en AWS y ensayo local

- [Comprobaciones externas](evidencias/semana13-aceptacion/public.json) y [prueba de CSRF](evidencias/semana13-aceptacion/csrf.txt). Incluyen expiración real del acceso, renovación y cierre de sesión.
- [Métricas del host](evidencias/semana13-aceptacion/host-metrics.txt) y escaneos de las capas desplegadas de [Django](evidencias/semana13-aceptacion/current-backend.json), [PostgreSQL](evidencias/semana13-aceptacion/current-postgres.json) y [proxy](evidencias/semana13-aceptacion/current-proxy.json).
- [pytest](evidencias/semana13-aceptacion/pytest.txt), [Vitest](evidencias/semana13-aceptacion/vitest.txt), [Playwright inicial](evidencias/semana13-aceptacion/playwright.txt), [trazabilidad](evidencias/semana13-aceptacion/playwright-traceability.txt), [resiliencia](evidencias/semana13-aceptacion/playwright-resilience.txt) y [repetición final](evidencias/semana13-aceptacion/playwright-final.txt).
- [k6 local con 100 solicitudes GET](evidencias/semana13-aceptacion/k6-get-100.json). La interpretación, el entorno y los límites figuran en [Resultados de pruebas](SEMANA_13_RESULTADOS_PRUEBAS.md).
