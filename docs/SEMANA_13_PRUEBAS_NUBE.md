# Pruebas de carga en la nube (AWS Lightsail)

Esta guía responde a la observación de la revisión. Las pruebas anteriores se ejecutaron en local (`https://localhost`) y solo leían datos. Estas pruebas se ejecutan contra el servidor público `https://logistech.stackpe.online`. Además escriben en PostgreSQL: cada registro crea un usuario real, que luego se verifica en pgAdmin.

## Qué se cambió y por qué

| Cambio | Archivo | Motivo |
|---|---|---|
| Interruptor `LOAD_TEST_MODE` | `backend/config/settings/base.py`, `backend/apps/accounts/throttles.py`, `compose.production.yml` | El rate limit de seguridad (registro 3/hora por IP, API 120/min por usuario) bloqueaba las pruebas masivas y devolvía 429. Con `LOAD_TEST_MODE=true` los límites se desactivan solo durante la ventana de prueba. Por defecto vale `false`. |
| Aviso `logistech.W010` | `backend/apps/core/checks.py` | `manage.py check --deploy` avisa si el modo de prueba quedó encendido. |
| Script k6 para la nube | `load/nube.js` | Modo del profesor: N iteraciones repartidas entre VU trabajadores, con un tiempo máximo. Clasifica cada error como cuota (429), cliente (4xx), servidor (5xx) o red/timeout. |
| Ejecutor | `scripts/run_cloud_load.ps1` | Corre k6 en Docker y permite escaleras de 50 a 50 000. |
| Resumen y gráficas | `scripts/summarize_cloud_load.py` | Genera CSV, una tabla Markdown y un HTML con barras imprimibles en blanco y negro. |
| Conteo y limpieza | `manage.py load_test_users` | Cuenta y elimina solo usuarios `k6-...@example.test` de rol OPERATOR sin empresa. |
| Pruebas | `backend/tests/test_load_test_mode.py` | Comprueban que el límite sigue activo por defecto, que el modo de prueba lo desactiva y que la limpieza no toca usuarios reales. |

## Glosario para la tabla de resultados

- **Iteración**: una operación completa, por ejemplo un registro. **VU**: un usuario o trabajador simultáneo.
- **Fallido por cuota (429)**: el rate limit rechazó la solicitud. No es una caída del servidor, sino la protección funcionando.
- **Fallido por volumen o capacidad (5xx o timeout)**: el servidor no pudo atender la cantidad de solicitudes. 502 significa que Gunicorn no respondió, 503 que la base de datos no estaba disponible y timeout que la respuesta superó 30 s.
- **Incompleto**: no terminó todas las iteraciones dentro del tiempo máximo.
- **Aprobado**: todas las iteraciones terminaron, con error ≤ 1 % y p95 ≤ 1 s.
- **Lectura / escritura**: GET de categorías es lectura. El registro es escritura, porque inserta en `accounts_user` y calcula el hash de la contraseña.

## Procedimiento

### 1. Desplegar el código nuevo en el servidor (una sola vez)

En la instancia Lightsail, con el commit de esta rama ya revisado:

```bash
git fetch && git checkout <SHA-de-esta-rama>
bash deploy/production/update.sh <SHA-de-esta-rama>
```

### 2. Abrir la ventana de prueba

```bash
echo 'LOAD_TEST_MODE=true' >> .env.f7
docker compose -p logistech-production --env-file .env.f7 -f compose.production.yml up -d --wait backend
docker compose -p logistech-production --env-file .env.f7 -f compose.production.yml exec backend python manage.py check --deploy   # debe mostrar W010
```

### 3. Ejecutar las pruebas desde tu PC (PowerShell, con Docker Desktop encendido)

```powershell
# Registro masivo, que escribe en la BD: 50, 100, 200, 500 y 1000 con 10 VU
.\scripts\run_cloud_load.ps1 -Ladder register

# Modo del profesor: 10 000 en 30 s con 10 VU
.\scripts\run_cloud_load.ps1 -Scenario register -Iterations 10000 -VUs 10 -Duration 30s

# Lectura autenticada de 100 a 50 000 (requiere una cuenta con rol asignado)
$env:K6_EMAIL = 'tu-admin@...'; $env:K6_PASSWORD = '...'
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
sed -i 's/^LOAD_TEST_MODE=true$/LOAD_TEST_MODE=false/' .env.f7
docker compose -p logistech-production --env-file .env.f7 -f compose.production.yml up -d --wait backend
docker compose -p logistech-production --env-file .env.f7 -f compose.production.yml exec backend python manage.py check --deploy   # W010 ya no debe aparecer
# Opcional, después de tomar las capturas:
docker compose -p logistech-production --env-file .env.f7 -f compose.production.yml exec backend python manage.py load_test_users --prefix k6- --delete
```

## Qué esperar y cómo explicarlo

El backend en producción tiene 1 CPU y 512 MB (`compose.production.yml`), con Gunicorn de 2 workers × 2 threads. Cada registro calcula un hash PBKDF2 de la contraseña, que es costoso a propósito para resistir ataques. Por eso la escritura llega a su techo mucho antes que la lectura.

Referencia medida en local el 18/11/2026, con `runserver` y sin límite de CPU: 200 registros en 3,7 s (pico de 60 altas por segundo, p95 de 221 ms) y 1000 GET en 5,9 s (174 req/s, p95 de 68 ms). En la nube se espera menos. Lo que se mida allí es el dato que va al informe.

Si una prueba falla, documentarla en la tabla de incidentes con causa, impacto, solución y verificación. Ejemplos probables:

| Síntoma | Causa probable | Solución |
|---|---|---|
| Muchos 429 | `LOAD_TEST_MODE` no está activo | Paso 2 y repetir |
| 502 o timeouts en registro masivo | CPU del backend al 100 % por el hash de contraseñas | Subir workers o `cpus` del backend, o escalar la instancia; repetir con menos VU |
| 503 | PostgreSQL saturado o reiniciándose | Revisar `docker compose logs db`, esperar la salud y repetir |
| Incompleto en 30 s | Volumen mayor que la capacidad por segundo | Reportar el máximo alcanzado y el escalón donde falló |
