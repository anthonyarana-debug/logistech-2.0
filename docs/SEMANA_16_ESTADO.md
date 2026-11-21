# LogisTech 2.0 en la semana 16

## Estado de AWS

El 20 de noviembre de 2026 a las 23:22 de Lima, la comprobación por SSH encontró activa la ventana de carga. Se retiró el token, se fijó `LOAD_TEST_MODE=false` y se recreó solo el backend. PostgreSQL y Caddy mantuvieron su configuración. Dieron positivo la comprobación de salud HTTPS y la ausencia de W010. La versión desplegada es `b0d385d68c1877405e610eb990aa17828fd6bcdc`. [Evidencia de cierre](evidencias/semana16/cierre-carga.txt)

## Rendimiento

Estos resultados de AWS proceden del Anexo D y de sus JSON de k6. Cada iteración de lectura representa una consulta lógica. El contador HTTP incluye solicitudes de autenticación y reintentos. Las escrituras de registro se reportan como altas.

| Entorno | Escenario | Completado | Duración | p95 | Errores HTTP |
|---|---|---:|---:|---:|---:|
| AWS | GET 1.000 | 1.000/1.000 | 51,68 s | 1,19 s | 0 % |
| AWS | GET 5.000 | 5.000/5.000 | 165,14 s | 0,79 s | 0 % |
| AWS | GET 10.000 | 10.000/10.000 | 317,89 s | 0,89 s | 0,10 % |
| AWS | GET 25.000 | 19.441/25.000 | 600,78 s | 0,91 s | 0,10 % |
| AWS | GET 50.000 | Pendiente | — | — | — |
| AWS | Registro 10.000, ventana configurada de 30 s | 34 altas | 39,27 s observados, incluido el cierre de iteraciones | 16,15 s | 0 % |
| Docker local | GET 50.000 | 50.000/50.000 | 169,90 s | 147,35 ms | 0 % |

El Anexo D atribuye los HTTP 401 de las dos corridas largas de lectura al vencimiento del acceso seguido de renovación. Un ritmo de 32 iteraciones/s requiere aproximadamente 26 minutos para 50.000 GET. Hacerlos en 600 s exige 83,33 iteraciones/s. El escenario de 50.000 necesita un plazo acordado y un entorno de capacidad aprobado. Registrar 10.000 en 30 s exigiría más de 333 altas/s. [Anexo D](ANEXO_D_PRUEBAS_NUBE.pdf) · [JSON y tablas históricas](evidencias/semana13-nube/resumen.html)

Las 50.000 lecturas locales usaron 20 VU, un backend con 2 vCPU, una cuenta sintética, 100 categorías en PostgreSQL y una red Docker privada. k6 registró 50.040 solicitudes HTTP incluyendo autenticación y 294,52 req/s. El tráfico local entró directamente a Gunicorn. El escenario de AWS añade Caddy, TLS público y la capacidad de Lightsail. [Resultados locales](evidencias/semana16/get-local/resumen.html)

La comparación nueva se hizo en Docker local con Gunicorn, PostgreSQL aislado, 10 usuarios virtuales y una corrida de 100 registros por perfil. Cada worker conservó dos hilos.

| Cuota de backend | Workers | Altas | Duración | Altas/s | p95 HTTP | Errores |
|---:|---:|---:|---:|---:|---:|---:|
| 1 vCPU | 2 | 100/100 | 12,951 s | 7,72 | 1.811,05 ms | 0 % |
| 2 vCPU | 2 | 100/100 | 6,431 s | 15,55 | 893,90 ms | 0 % |
| 2 vCPU | 4 | 100/100 | 10,087 s | 9,91 | 1.568,57 ms | 0 % |

La mejor muestra local fue 2 vCPU y dos workers. Cuatro workers aumentaron el tiempo acumulado de throttling de los procesos y empeoraron el p95 en esta corrida. En Lightsail los tres servicios comparten dos vCPU de host, por lo que corresponde repetir con mediciones de CPU, memoria, cgroups y créditos de ráfaga antes de cambiar la cuota. PBKDF2 conserva un millón de iteraciones. [1 vCPU, 2 workers](evidencias/semana16/cpu-local/cpu1-workers2/resumen.html) · [2 vCPU, 2 workers](evidencias/semana16/cpu-local/cpu2-workers2/resumen.html) · [2 vCPU, 4 workers](evidencias/semana16/cpu-local/cpu2-workers4/resumen.html) · [Cgroups](evidencias/semana16/cpu-local/cpu-cgroup.txt)

## Operación y recuperación

- Django genera `X-Request-ID` y registra fallos en JSON. Gunicorn incluye el mismo ID en accesos y emite errores de proceso en JSON. Los campos de diagnóstico excluyen cuerpos de solicitudes, credenciales, cookies, valores de excepción y cabeceras de autenticación. Caddy elimina el objeto de solicitud de sus logs de ejecución.
- En el ensayo local, PostgreSQL detenido devolvió 503 y volvió a 200 en **8,054 s**. El ID de la respuesta coincidió con el log de acceso. Backend detenido devolvió 502 desde Caddy y volvió a 200 en **7,615 s**. En el registro del 502 se verificó el filtro de Caddy mediante una cabecera y una consulta sintéticas. Se comprobó rollback y retorno a la versión nueva con seis categorías antes y después. [Ensayo nuevo](evidencias/semana16/fallos-local.json)
- El ensayo de migración transfirió una copia entre dos PostgreSQL independientes en Docker local. El dump de 72.798 bytes conservó su checksum y el manifiesto de origen y destino coincidió en compañías, sucursales, productos, cajas, migraciones y triggers de historial. El restore tomó 0,335 s y el ciclo hasta comparar ambos manifiestos tomó 1,093 s. [Evidencia](evidencias/semana16/migracion-local.json) · [Procedimiento entre servidores](MIGRACION_SEGUNDO_SERVIDOR.md)
- El workflow de CI configura PostgreSQL, Ruff, comprobación de migraciones y pytest, además de ESLint, pruebas unitarias y build para frontend. `actionlint` verificó la definición. La ejecución en GitHub queda pendiente de publicación. El despliegue sigue el procedimiento manual por SHA. [Workflow](../.github/workflows/ci.yml) · [Guía AWS](AWS_F7_GUIA.md)

La regresión local aprobó 332 pruebas de backend con PostgreSQL, Ruff y el chequeo de migraciones. Frontend aprobó 15 pruebas unitarias, ESLint y build. Playwright verificó cuatro fallos simulados en la interfaz (500, 502, 503 y desconexión) y un flujo con API real de QR, ID interno, recepción idempotente e historial. [Backend](evidencias/semana16/backend.txt) · [Resiliencia de la interfaz](evidencias/semana16/playwright.txt) · [Trazabilidad web](evidencias/semana16/trazabilidad-web.txt)

## Demo para la presentación

1. Abrir la [landing](https://logistech.stackpe.online/) y el [inicio de sesión web](https://logistech.stackpe.online/login).
2. En el ensayo local, cargar una empresa ficticia con `python manage.py create_demo --namespace semana16 --scenario warehouse --output /tmp/semana16-credentials.json` dentro del backend. La empresa se identifica como **Distribuidora Costa Central**. Callao tiene sensores y cintas de embalaje. Ate tiene conservas selladas. El escenario incluye un segundo tenant para comprobar aislamiento.
3. Mostrar las cajas de ambas sucursales, luego identificar una caja registrada por código interno `CJ-…` y por QR. Confirmar la recepción y revisar su evento en el historial. Mostrar el acceso restringido del operador sin empresa. La recepción verifica trazabilidad. Movimientos, saldos por sucursal y reportes de inventario continúan pendientes. [Plan F8](PLAN_FASE_8.md)
4. Mostrar el arranque del APK Kotlin en Android y explicar qué datos son locales. La aceptación móvil termina cuando el teléfono físico escanea una caja de la API, confirma su recepción y el evento aparece en la web. [Auditoría móvil](ANDROID_SEMANA_16.md)
