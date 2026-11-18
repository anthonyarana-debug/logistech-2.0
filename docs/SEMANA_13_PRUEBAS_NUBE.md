# Pruebas de carga en la nube (AWS Lightsail)

Esta guía responde a la observación de la revisión. Las pruebas anteriores se ejecutaron en local (`https://localhost`) y solo leían datos. Estas pruebas se ejecutan contra el servidor público `https://logistech.stackpe.online`. Además escriben en PostgreSQL: cada registro crea un usuario real, que luego se verifica en pgAdmin.

## Qué se cambió y por qué

| Cambio | Archivo | Motivo |
|---|---|---|
| Ventana `LOAD_TEST_MODE` + `LOAD_TEST_TOKEN` | `backend/config/settings/base.py`, `backend/apps/accounts/throttles.py`, `compose.production.yml` | El rate limit de seguridad (registro 3/hora por IP, API 120/min por usuario) bloqueaba las pruebas masivas y devolvía 429. Durante la ventana, **solo** las solicitudes con la cabecera `X-Load-Test-Token` igual al secreto (mínimo 32 caracteres, comparación en tiempo constante) omiten el límite. El tráfico público sigue limitado. Sin token o con `LOAD_TEST_MODE=false`, el límite se aplica siempre. |
| Aviso `logistech.W010` | `backend/apps/core/checks.py` | `manage.py check --deploy` avisa si el modo de prueba quedó encendido. |
| Script k6 para la nube | `load/nube.js` | Modo del profesor: N iteraciones repartidas entre VU trabajadores, con un tiempo máximo. Clasifica cada error como cuota (429), cliente (4xx), servidor (5xx) o red/timeout. |
| Ejecutor | `scripts/run_cloud_load.ps1` | Corre k6 en Docker y permite escaleras de 50 a 50 000. Los secretos (token, correo, contraseña) pasan a Docker por nombre de variable, nunca como valor en la línea de comandos. La escalera se detiene en el primer escalón que no aprueba, y k6 aborta solo si los errores superan el 5 % durante 10 s. |
| Resumen y gráficas | `scripts/summarize_cloud_load.py` | Genera CSV, una tabla Markdown y un HTML con barras imprimibles en blanco y negro. |
| Conteo y limpieza | `manage.py load_test_users` | Cuenta y elimina solo usuarios `k6-...@example.test` de rol OPERATOR sin empresa. |
| Pruebas | `backend/tests/test_load_test_mode.py` | Comprueban que el límite sigue activo por defecto, que solo el token correcto lo omite, que el público sigue limitado durante la ventana, que un token corto o con el modo apagado no sirve, y que la limpieza no toca usuarios reales. |
| Ensayo local | `scripts/test_cloud_load_local.ps1` | Reproduce todo en Docker, incluida la comprobación de que el público recibe 429 durante la ventana. `-SinToken` demuestra el fallo por cuota y el corte de la escalera. |

## Glosario para la tabla de resultados

- **Iteración**: una operación completa, por ejemplo un registro. **VU**: un usuario o trabajador simultáneo.
- **Fallido por cuota (429)**: el rate limit rechazó la solicitud. No es una caída del servidor, sino la protección funcionando.
- **5xx o timeout**: pueden indicar un problema de capacidad. Un 502 corresponde a un fallo de respuesta del servicio aguas arriba. Un 503 indica indisponibilidad y requiere comprobar qué servicio lo emitió. Un timeout indica que el cliente agotó el plazo de la solicitud. Los logs y las métricas ayudan a identificar la causa.
- **Incompleto**: no terminó todas las iteraciones dentro del tiempo máximo.
- **Cortado**: k6 se detuvo solo porque los errores superaron el 5 % sostenido (protección para no tumbar el servidor).
- **Aprobado**: todas las iteraciones terminaron, con error ≤ 1 % y p95 ≤ 1 s.
- **Lectura / escritura**: GET de categorías es lectura. El registro es escritura, porque inserta en `accounts_user` y calcula el hash de la contraseña.

## Procedimiento

### 1. Desplegar el código nuevo en el servidor (una sola vez)

En la instancia Lightsail, con el commit de esta rama ya revisado:

```bash
git fetch && git checkout <SHA-de-esta-rama>
bash deploy/production/update.sh <SHA-de-esta-rama>
```

### 1b. Cargar categorías por tipo de producto (observación de la revisión)

Crea seis tipos (electrodomésticos, muebles, cerámica y vidrio frágil, electrónica frágil, alimentos perecibles y ferretería), cada uno con su propio prefijo de SKU (ELEC-, MUEB-, FRAG-, TECN-, PERE-, FERR-) y tres productos. No duplica nada si se ejecuta dos veces.

```bash
docker compose -p logistech-production --env-file .env.f7 -f compose.production.yml exec backend python manage.py seed_catalog --company "Tecsup"
```

### 2. Abrir la ventana de prueba

Genera un token nuevo para esta ventana. No lo pegues en chats, documentos ni commits; pásalo a tu PC por un canal privado.

```bash
echo 'LOAD_TEST_MODE=true' >> .env.f7
echo "LOAD_TEST_TOKEN=$(openssl rand -hex 32)" >> .env.f7
grep '^LOAD_TEST_TOKEN=' .env.f7 | cut -d= -f2    # cópialo a tu PC por un canal privado
docker compose -p logistech-production --env-file .env.f7 -f compose.production.yml up -d --wait backend
docker compose -p logistech-production --env-file .env.f7 -f compose.production.yml exec backend python manage.py check --deploy   # debe mostrar W010
```

### 3. Ejecutar las pruebas desde tu PC (PowerShell, con Docker Desktop encendido)

```powershell
# El mismo token del servidor (solo en esta ventana de PowerShell)
$env:K6_LOAD_TEST_TOKEN = Read-Host 'Token de prueba'

# Registro masivo, que escribe en la BD: 50, 100, 200, 500 y 1000 con 10 VU
.\scripts\run_cloud_load.ps1 -Ladder register

# Modo del profesor: 10 000 en 30 s con 10 VU
.\scripts\run_cloud_load.ps1 -Scenario register -Iterations 10000 -VUs 10 -Duration 30s

# Lectura autenticada de 100 a 50 000 (requiere una cuenta con rol asignado)
$env:K6_EMAIL = 'tu-admin@...'; $env:K6_PASSWORD = Read-Host 'Contraseña admin'
.\scripts\run_cloud_load.ps1 -Ladder get
```

Los resultados quedan en `docs/evidencias/semana13-nube/`: un JSON por prueba más `resumen.csv`, `resumen.md` y `resumen.html` con las gráficas.

### 4. Verificar en la base de datos (para pgAdmin o la consola)

```bash
docker compose -p logistech-production --env-file .env.f7 -f compose.production.yml exec backend python manage.py load_test_users --prefix k6-<RUN_ID>
```

En pgAdmin:

```sql
SELECT count(*) AS usuarios_creados, min(created_at) AS primero, max(created_at) AS ultimo,
       max(created_at) - min(created_at) AS duracion
FROM accounts_user WHERE email LIKE 'k6-%@example.test';

SELECT date_trunc('second', created_at) AS segundo, count(*) AS altas_por_segundo
FROM accounts_user WHERE email LIKE 'k6-%@example.test'
GROUP BY 1 ORDER BY 1;
```

### 5. Cerrar la ventana de prueba (obligatorio)

```bash
sed -i 's/^LOAD_TEST_MODE=true$/LOAD_TEST_MODE=false/; /^LOAD_TEST_TOKEN=/d' .env.f7
docker compose -p logistech-production --env-file .env.f7 -f compose.production.yml up -d --wait backend
docker compose -p logistech-production --env-file .env.f7 -f compose.production.yml exec backend python manage.py check --deploy   # W010 ya no debe aparecer
# Opcional, después de tomar las capturas:
docker compose -p logistech-production --env-file .env.f7 -f compose.production.yml exec backend python manage.py load_test_users --prefix k6- --delete
```

## Qué esperar y cómo explicarlo

El backend en producción tiene 1 CPU y 512 MB (`compose.production.yml`), con Gunicorn de 2 workers × 2 threads. Cada registro calcula un hash PBKDF2 de la contraseña, que es costoso a propósito para resistir ataques. Por eso la escritura llega a su techo mucho antes que la lectura.

Referencia medida en local el 18/11/2026 con `scripts/test_cloud_load_local.ps1` (Docker, `runserver`, sin límite de CPU). Es un ensayo local y no reemplaza la prueba en la nube:

| Prueba | Hechas/objetivo | VU | Duración | Req/s | p95 ms | Error % | Usuarios en BD | Resultado |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Registro 200 | 200/200 | 10 | 3,58 s | 58,64 | 218,01 | 0 | 200 | Aprobado |
| Registro 10 000 en 30 s | 1806/10 000 | 10 | 30,14 s | 60,26 | 191,79 | 0 | 1806 | Incompleto |
| GET 1000 | 1000/1000 | 10 | 5,87 s | 173,74 | 67,86 | 0 | — | Aprobado |

Interpretación del caso de 10 000 en 30 s: no hubo errores ni caída. El servidor atendió todas las solicitudes que recibió en 0,19 s (p95), pero su techo de escritura es de unas 60 altas por segundo (pico de 66), así que en 30 s solo caben unas 1800. El límite es la CPU: cada alta calcula el hash PBKDF2 de la contraseña. Para alcanzar 10 000 en 30 s harían falta unas 333 altas por segundo, es decir, unas cinco veces más CPU o workers. No se debe bajar la seguridad del hash para lograrlo. En la nube, con 1 CPU, el techo será menor; ese es el número que va al informe.

Escalera local del 18/11/2026 con token (`test_cloud_load_local.ps1 -Ladder register`): 50, 100, 200, 500 y 1000 registros aprobados, con 0 % de errores, entre 58 y 63 req/s y p95 entre 180 y 242 ms. PostgreSQL confirmó 1850 usuarios. En la misma ventana, el tráfico sin token recibió `[400, 400, 400, 429]`: el público siguió limitado. Con `-SinToken`, el escalón de 50 terminó FALLIDO con 47 respuestas 429 de cuota y solo 3 altas (el límite de 3 por hora), y la escalera se detuvo sola.

Si una prueba falla, documentarla en la tabla de incidentes con causa, impacto, solución y verificación. Ejemplos probables:

| Síntoma | Causa probable | Solución |
|---|---|---|
| Muchos 429 | `LOAD_TEST_MODE` no está activo | Paso 2 y repetir |
| 502 o timeouts en registro masivo | CPU del backend al 100 % por el hash de contraseñas | Subir workers o `cpus` del backend, o escalar la instancia; repetir con menos VU |
| 503 | PostgreSQL saturado o reiniciándose | Revisar `docker compose logs db`, esperar la salud y repetir |
| Incompleto en 30 s | Volumen mayor que la capacidad por segundo | Reportar el máximo alcanzado y el escalón donde falló |

## Resultados en la nube (18 de noviembre de 2026)

La instancia Lightsail ejecutó `90b8b7c77856cf09c72ed26f30e608cea9dc67f0`. El respaldo previo pasó SHA-256. La siembra en Tecsup creó seis categorías y 18 productos. Una segunda ejecución creó cero. [Despliegue](evidencias/semana13-nube/despliegue.txt) · [Catálogo](evidencias/semana13-nube/catalogo.txt)

| Entorno | Escenario | Iteraciones | VU | Duración | Req/s | p95 | Error | Altas en PostgreSQL | Resultado |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Local, referencia histórica | Registro | 200/200 | 10 | 3,58 s | 58,64 | 218,01 ms | 0 % | 200 | Aprobado |
| Local, referencia histórica | Registro | 1.806/10.000 | 10 | 30,14 s | 60,26 | 191,79 ms | 0 % | 1.806 | Incompleto |
| Local, referencia histórica | GET | 1.000/1.000 | 10 | 5,87 s | 173,74 | 67,86 ms | 0 % | — | Aprobado |
| AWS, base de producción | Registro | 50/50 | 10 | 58,829 s | 1,02 | 17.321,05 ms | 0 % | 50 | Lento |
| AWS, base de producción | Registro 100, 200, 500, 1.000 y 10.000 | — | — | — | — | — | — | — | Pendiente |
| AWS, base de producción | GET hasta 50.000 y mixto | — | — | — | — | — | — | — | Pendiente |

El primer escalón en AWS superó el límite de p95 de 1 s, así que la escalera se detuvo antes de 100. El p95 específico del POST de registro fue 17.345,83 ms. El p95 de espera HTTP fue 17.320,74 ms y el de conexión 184,85 ms. La mayor parte de la latencia observada fue espera por la respuesta. El hash PBKDF2, el límite de una CPU y los cuatro hilos de Gunicorn son hipótesis que requieren mediciones durante la corrida. Las muestras puntuales antes y después no confirman el cuello de botella. Si se confirma presión de CPU o cola de Gunicorn, evaluar CPU disponible y concurrencia de workers antes de cambiar la instancia o sus límites. [Tabla k6](evidencias/semana13-nube/resumen.md) · [Gráficas](evidencias/semana13-nube/resumen.html)

La consulta SQL y el comando Django coinciden en 50 usuarios. El primer y último registro quedaron separados por 54,28 s, con 0,92 altas/s según el intervalo de PostgreSQL y un pico de 4 altas en un segundo. Los 1,02 req/s de k6 incluyen diez consultas CSRF y los 50 POST. La evidencia SQL se obtuvo con `psql` dentro del contenedor. [Conteo y serie por segundo](evidencias/semana13-nube/postgresql.txt)

| Servicio | CPU antes | CPU después | RAM antes | RAM después |
|---|---:|---:|---:|---:|
| Backend | 0,04 % | 0,03 % | 119,6 MiB | 132,2 MiB |
| PostgreSQL | 0,66 % | 4,48 % | 22,25 MiB | 22,49 MiB |

[Muestras de recursos](evidencias/semana13-nube/recursos.txt)

| Hora de Lima | Incidente | Impacto | Acción y verificación |
|---|---|---|---|
| 01:47 | Docker rechazó la ruta relativa de evidencias | Cero solicitudes en ese intento | Se cerró la ventana y se repitió con ruta absoluta. La API de salud respondió antes y después. |
| 01:49 | El p95 del escalón de 50 superó el umbral | Se cancelaron los escalones siguientes | Se confirmaron 50 altas y cero errores 429, 5xx o timeout. La API de salud respondió antes y después. |

La segunda ventana se cerró a las 01:49:54 de Lima. El backend y su configuración quedaron con `LOAD_TEST_MODE=false`, sin token y sin W010. Salud devolvió HTTP 200. Las cuatro solicitudes de registro inválidas sin token devolvieron 400, 400, 400 y 429. [Ventana](evidencias/semana13-nube/ventana.txt) · [Cuota](evidencias/semana13-nube/cuota.txt)
