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
| k6 1000–50000 | No ejecutado | Perfiles parametrizados. Falta dimensionamiento y prueba escalonada |
| Despliegue y validación externos | Bloqueado por autorización | Se validó el ensayo local |

## Auditoría de las imágenes

Trivy 0.76.1 evaluó los archivos exportados de las tres imágenes que estaban ejecutándose. Los identificadores se verificaron antes de exportar. La imagen de PostgreSQL quedó con 0 CRITICAL y 0 HIGH. Backend quedó con 47 HIGH y proxy con 1 HIGH, todos sin versión corregida indicada por el escáner. El gate final dio 0 CRITICAL y 0 HIGH corregibles. npm audit de dependencias de producción reportó 0 hallazgos.

La actualización corrigió las alertas con parche de apt, zlib, libxslt y x/net que aparecieron en la primera revisión de Semana 13. Se conservó el reporte anterior F7 de 45 HIGH como evidencia histórica con otra fecha y base de vulnerabilidades. Antes de publicación se debe revisar la exposición a los 48 hallazgos residuales. [Parche Debian para apt](https://security-tracker.debian.org/tracker/DSA-6607-1) · [Parche Debian para zlib](https://security-tracker.debian.org/tracker/DSA-6613-1) · [Versión x/net](https://pkg.go.dev/golang.org/x/net@v0.62.0)

## k6

Una iteración representa una ejecución del escenario. Las operaciones compuestas generan varias solicitudes. Cada corrida usó un VU y un clúster independiente. El escenario recuperación prueba disponibilidad. La recuperación tras un reinicio se midió con el verificador PostgreSQL.

El script k6 declara los perfiles de 100 a 50000 iteraciones. El runner de Windows ejecuta hasta 100 porque sus volúmenes carecen de cuota de disco verificada. Un perfil mayor requiere un ejecutor aislado con cuota, presupuesto de solicitudes por identidad y duración revisada. [Documentación de iteraciones compartidas](https://grafana.com/docs/k6/latest/using-k6/scenarios/executors/shared-iterations/)

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
