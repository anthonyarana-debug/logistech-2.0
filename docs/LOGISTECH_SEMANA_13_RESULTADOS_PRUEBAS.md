# Resultados de pruebas de Semana 13

Entorno de ensayo del 10 de noviembre de 2026, Lima. Windows con Docker Desktop Linux, PostgreSQL 17.11 Alpine, Gunicorn y Caddy. Se usó `logistech-week13` para integración y un proyecto Docker con volumen nuevo para cada escenario k6.

| Prueba | Estado | Resultado |
|---|---|---|
| pytest, API y PostgreSQL | Aprobado | 316 pruebas, 32.83 s. Incluye nueve casos de paginación |
| Frontend unitarias | Aprobado | 15 pruebas |
| ESLint y build React | Aprobado | Compilación Vite y lint sin errores |
| Ruff | Aprobado | `ruff check --no-cache` en imagen QA |
| Playwright regresión | Aprobado | Ocho flujos en 5.4 min. Incluye expiración real de JWT |
| Playwright paginación | Aprobado | Un caso, 26 categorías sintéticas, filtro y página 2 |
| Playwright sobre imágenes actualizadas | Aprobado | Dos casos en 5.9 s, paginación y HTTPS con sesión y rutas privadas |
| Django deploy check | Aprobado con avisos | W005 y W021 sobre HSTS de subdominios y preload |
| Migraciones | Aprobado | Aplicación en volumen nuevo, verificación y sin drift |
| Proxy y HTTPS | Aprobado | Configuración Caddy válida, salud y verificación con CA de ensayo |
| Plantillas AWS | Aprobado | cfn-lint 1.58.0 sobre Lightsail y EC2 para us-east-2, con red deshabilitada |
| CORS | Aprobado | Origen externo sin `Access-Control-Allow-Origin` en la consulta verificada |
| Backup, restauración y persistencia | Aprobado | 90 497 bytes, checksum correcto, ocho modelos coincidentes y rechazo de destino existente |
| k6 en AWS | Parcial | 50/50 registros persistidos. La escalera se detuvo por p95 de 17,32 s. Pendientes los escalones restantes y GET hasta 50.000. [Resultados en la nube](SEMANA_13_PRUEBAS_NUBE.md#resultados-en-la-nube-18-de-noviembre-de-2026) |
| Despliegue y validación externos | Operativo | El 18/11/2026 AWS ejecutó `90b8b7c`. Portada, login y salud respondieron HTTP 200. [Evidencia](evidencias/semana13-nube/despliegue.txt) |

## Auditoría de las imágenes

Trivy 0.76.1 evaluó los archivos exportados de las tres imágenes que estaban ejecutándose. Los identificadores se verificaron antes de exportar. La imagen de PostgreSQL quedó con 0 CRITICAL y 0 HIGH. Backend quedó con 47 HIGH y proxy con 1 HIGH, todos sin versión corregida indicada por el escáner. El gate final dio 0 CRITICAL y 0 HIGH corregibles. npm audit de dependencias de producción reportó 0 hallazgos.

La actualización corrigió las alertas con parche de apt, zlib, libxslt y x/net que aparecieron en la primera revisión de Semana 13. Se conservó el reporte anterior F7 de 45 HIGH como evidencia histórica con otra fecha y base de vulnerabilidades. Antes de publicación se debe revisar la exposición a los 48 hallazgos residuales. [Parche Debian para apt](https://security-tracker.debian.org/tracker/DSA-6607-1) · [Parche Debian para zlib](https://security-tracker.debian.org/tracker/DSA-6613-1) · [Versión x/net](https://pkg.go.dev/golang.org/x/net@v0.62.0)

## k6 del ensayo previo

Una iteración representa una ejecución del escenario. Las operaciones compuestas generan varias solicitudes. Cada corrida usó un VU y un clúster independiente. El escenario recuperación prueba disponibilidad. La recuperación tras un reinicio se midió con el verificador PostgreSQL.

El script k6 declara los perfiles de 100 a 50000 iteraciones. El runner de Windows de aquel ensayo ejecutaba hasta 100 porque sus volúmenes carecen de cuota de disco verificada. Un perfil mayor requiere un ejecutor aislado con cuota, presupuesto de solicitudes por identidad y duración revisada. [Documentación de iteraciones compartidas](https://grafana.com/docs/k6/latest/using-k6/scenarios/executors/shared-iterations/)

| Escenario | Iteraciones | HTTP | Req/s | Promedio ms | p90 ms | p95 ms | p99 ms | Fallos |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GET paginado | 100 | 100 | 13.85 | 21.47 | 24.62 | 26.30 | 28.35 | 0 % |
| CRUD | 2 | 8 | 24.87 | 27.00 | 34.78 | 41.22 | 46.38 | 0 % |
| Registro | 2 | 4 | 7.83 | 101.60 | 139.54 | 142.94 | 145.67 | 0 % |
| Cajas y QR | 2 | 6 | 14.32 | 52.46 | 97.18 | 126.19 | 149.41 | 0 % |
| Historial | 2 | 2 | 12.71 | 26.89 | 31.01 | 31.52 | 31.94 | 0 % |
| Salud | 2 | 2 | 15.15 | 12.34 | 12.35 | 12.36 | 12.36 | 0 % |

Las 122 respuestas fueron 2xx. Dos altas se comprobaron en PostgreSQL. CPU y RAM de backend y PostgreSQL se conservaron como capturas puntuales antes y después. Los percentiles de muestras de dos iteraciones son descriptivos. El ensayo histórico reportado por el usuario fue de 200 altas HTTP 201 con 10 VU y aproximadamente 10.4 segundos en otra computadora.

[JSON y recursos Docker](evidencias/semana13/k6.json) · [CSV](evidencias/semana13/k6.csv) · [HTML con gráfica](evidencias/semana13/k6.html)

## Incidentes de ensayo

| Problema | Causa | Impacto | Solución | Verificación |
|---|---|---|---|---|
| Motor Docker no disponible | Docker Desktop detenido | Inicio bloqueado | Arrancar motor Linux | Servicios sanos |
| Ruff no pudo escribir cache | Usuario de contenedor sin permisos en el directorio de trabajo | Primer intento fallido | Ejecutar con `--no-cache` | Lint aprobado |
| Exportación del archivo demo | Docker cp no encontró el archivo en tmpfs | Credenciales E2E no disponibles en host | Copiar mediante stdout directamente a archivo ignorado | Inicio de sesión E2E |
| Red agotada | Corridas anteriores dejaban redes al detener contenedores | Dos inicios de k6 fallaron | Retirar redes y contenedores de esas corridas con Compose down, conservando volúmenes | Historial y salud ejecutados en proyectos nuevos |
| Verificación de certificado local en Schannel | CA local sin servicio de revocación accesible | Primer curl falló | Confiar en CA de ensayo y limitar la excepción de revocación al curl local | HTTPS y salud comprobados |

## Recuperación

En el primer ensayo el backup tardó 1.160 s, la restauración 1.782 s y la verificación tras el reinicio 3.697 s. Con las imágenes actualizadas los tiempos fueron 1.036 s, 1.258 s y 3.271 s respectivamente. Incluyen los contenedores auxiliares y la verificación posterior cuando corresponde. La DB activa y los destinos restaurados quedaron conservados. [Evidencia final de recuperación](evidencias/semana13/recovery.json)

## Validación de cierre del 11 de noviembre de 2026

Pytest con PostgreSQL real registró 316 pruebas aprobadas, Vitest 15, y Playwright 9 de la suite completa más 3 de recuperación visual. ESLint, Ruff, build, comprobación de migraciones y cfn-lint pasaron. Django check --deploy conservó W005 y W021 de HSTS. npm audit de producción registró cero hallazgos. El ensayo compilado respondió 200 por HTTPS. Las capturas etiquetadas SIMULATED corresponden a fallos provocados. [Evidencias de cierre](evidencias/semana13-cierre/)

### Capacidad con PostgreSQL aislado

k6 1.5.0, Docker Linux local, API HTTPS y 10.000 categorías sintéticas para consultas GET a página 400 con 25 filas por página. Se verificó la salud al terminar las corridas completas. Los perfiles de CRUD, registro, cajas, historial y salud tienen operaciones distintas. Las dos altas persistieron. Los tamaños mayores son volúmenes de iteraciones GET. Para decidir el avance se exigieron iteraciones completas, cero errores y p95 inferior a 500 ms.

| Escenario | Hechas/objetivo | VU | HTTP | Req/s | Media ms | p90 ms | p95 ms | p99 ms | Error % | WAL y datos KiB | Decisión |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| get | 100/100 | 2 | 100 | 3.17 | 30.36 | 34.31 | 39.85 | 129.81 | 0 | 2152 | passed |
| get | 500/500 | 5 | 500 | 7.94 | 28.06 | 33.55 | 42.42 | 57.87 | 0 | 2460 | passed |
| get | 1000/1000 | 10 | 1000 | 15.83 | 29.21 | 36.78 | 46.15 | 85.87 | 0 | 2540 | passed |
| get | 0/2500 | 10 | 10 | 23.45 | 140.99 | 215.32 | 238.63 | 257.27 | 0 | 1896 | incomplete |
| get | 2500/2500 | 10 | 2500 | 15.65 | 36.95 | 36.09 | 51.09 | 190.6 | 0 | 19152 | passed |
| get | 2500/2500 | 20 | 2500 | 26.18 | 144.55 | 341.6 | 734.64 | 2385.55 | 0 | 19152 | threshold_failed |
| get | 5000/5000 | 20 | 5000 | 20.01 | 27.42 | 31.42 | 39.94 | 80.14 | 0 | 19184 | passed |
| boxes | 2/2 | 1 | 6 | 1.56 | 40.54 | 52.41 | 53.81 | 54.93 | 0 | 136 | passed |
| crud | 2/2 | 1 | 8 | 1.59 | 28.47 | 35.25 | 42.69 | 48.64 | 0 | 88 | passed |
| history | 2/2 | 1 | 2 | 1.6 | 24.56 | 28.0 | 28.43 | 28.78 | 0 | 32 | passed |
| recovery | 2/2 | 1 | 2 | 1.55 | 41.01 | 64.8 | 67.78 | 70.16 | 0 | 56 | passed |
| register | 2/2 | 1 | 4 | 1.46 | 83.74 | 153.98 | 160.12 | 165.03 | 0 | 88 | passed |

La primera ejecución en PowerShell 5.1 falló por tratamiento de stderr nativo. Se corrigió la comprobación de códigos de salida y se validaron 100 GET y dos altas en 5.1. Los escalones mayores se ejecutaron con PowerShell 7. Un intento de 2.500 se abortó al leer un campo de salud que el proxy no tenía. Se corrigió la lectura del estado y se repitió. El ensayo de 2.500 con 20 VU completó el volumen pero excedió el umbral. El de 10 VU sostuvo 15,65 req/s y pasó. Esto muestra sensibilidad a la configuración de concurrencia, con atribución exacta pendiente. CPU y RAM son muestras de Docker anteriores y posteriores, y el crecimiento de datos y WAL se vigiló cada tres segundos. [HTML](evidencias/semana13-cierre/capacity.html) · [CSV](evidencias/semana13-cierre/capacity.csv) · [JSON y recursos](evidencias/semana13-cierre/capacity.json)

EXPLAIN ANALYZE en el ensayo de 1.000 registró 1,303 ms en la primera página y 2,094 ms en la página profunda. La consulta completa de API ejecutó seis sentencias SQL al serializar una fila y seis al serializar cinco. Se conservó la consulta existente porque la muestra no reveló una regresión que justificara modificar índices. La conclusión se limita a categorías y a la muestra observada.

### Seguridad y recuperación

Trivy confirmó 0 CRITICAL, 47 HIGH en backend, 0 HIGH en PostgreSQL y 1 HIGH en el proxy. La revisión agrupa alertas Debian de util-linux y sus bibliotecas de sistema, además de otros paquetes detallados por el escáner. En el proxy, Trivy vinculó CVE-2026-116587 a github.com/go-jose/go-jose/v3 v3.0.5. El escaneo no indicó versiones corregidas para los HIGH. Se conservaron imágenes, identificadores y resultados para evaluar exposición y correcciones del proveedor antes de la publicación. PostgreSQL sigue privado y el origen CORS ajeno quedó sin permiso. [Backend](evidencias/semana13-cierre/trivy-backend.json) · [Proxy](evidencias/semana13-cierre/trivy-proxy.json)

Un backup PostgreSQL de 93.836 bytes tomó 6,994 s. La restauración a un destino independiente tomó 6,429 s y rechazó una base existente. Coincidieron ocho manifiestos y no aparecieron recepciones vinculadas a otra empresa. El reinicio confirmó persistencia en 19,855 s. El cifrado AES-256-GCM recuperó el checksum de origen y rechazó el archivo alterado. En el ensayo de fallos, PostgreSQL produjo 503 y volvió a 200 en 7,193 s. Gunicorn produjo 502 y volvió a 200. El rollback a F7 y el retorno a Semana 13 mantuvieron seis categorías y salud 200. [Restauración](evidencias/semana13-cierre/recovery.json) · [Cifrado](evidencias/semana13-cierre/encryption.txt) · [Fallos y rollback](evidencias/semana13-cierre/faults.json)

En el perfil de 5.000 se usó una pausa de 0,97 s entre solicitudes, frente a 0,6 s en los escalones anteriores. El tiempo total fue 249,827 s. PostgreSQL pasó la comprobación de migraciones posterior. El máximo aumento observado de datos y WAL fue 19.184 KiB. La muestra Docker posterior registró 139,3 MiB de 512 MiB y 14,56 % de CPU para Gunicorn, y 41,66 MiB de 768 MiB y 0,54 % para PostgreSQL. Son muestras puntuales y no máximos del intervalo.

El perfil GET que alcanzó el objetivo se reproduce con:

```powershell
pwsh -NoProfile -File scripts/run_week13_load.ps1 -Scenario get -Iterations 5000 -VUs 20 -Rows 10000 -Page 400 -PaceSeconds 0.97 -DurationSeconds 270
```
