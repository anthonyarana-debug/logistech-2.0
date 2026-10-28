# Informe F7 — preparación AWS y ensayo de producción

Fecha: 28/10/2026. **Preparación local implementada y verificada; despliegue AWS
no ejecutado.** Objetivo público previsto: https://logistech.stackpe.online.
DNS permanece en Porkbun. No se creó infraestructura, cambió plan, consumió crédito
AWS, emitió certificado público ni modificó DNS. La revisión de seguridad conserva
hallazgos residuales que deben resolverse/revisarse antes de publicar.

## Estado recuperado y conservación

Base estable F6 Bloque 2: `118eed3`, con recepción, QR e historial sobre `ff58947`
y correcciones `3ad72cf`. Se verificó Git antes de implementar; `main` (`e7e437c`)
es anterior a la adaptación y F6, por lo que no se usó como base. Consulta remota de solo lectura confirmó `codex/respaldo-f6-bloque-2` en `118eed33a6e7f9657d8fa3ede5bc8b84d30cf17a`; F7 todavía no está en el remoto. La adaptación
`codex/documentacion-internacionalizacion` y documentación académica están en la
ascendencia conservada. Rama nueva **codex/fase-7-despliegue**, commits locales
consultables con `git log`; ninguna publicación F7 ni force-push. Código de esta
preparación: **`8642d9904747aac76825156ec012c3da45c7822d`**. El commit posterior
registra documentación/evidencias y espera la carga de datos antes de capturar la pantalla. Las imágenes del ensayo usan una etiqueta QA
basada en el nombre de su ejecución, no una versión cloud aprobada; para producción
se requiere compilar/identificar el SHA revisado mediante el preflight.

Se conservaron ramas, documentación histórica F0–F6, diseño Industrial Precision,
contratos `/api/v1`, estados, permisos y datos introducidos por usuarios. El
repositorio Android original no fue modificado. Las capturas históricas F6 que el
runner anterior había actualizado se conservaron como nuevas evidencias F7 y se
restauraron a sus bytes históricos; el runner ahora admite un directorio F7 separado.

Docker Desktop motor Linux 29.5.3 disponible. Pilas `logistech-f6` y
`logistech-f6-b2` y sus volúmenes conservados. Ensayo nuevo
`logistech-f7-rehearsal`, con PostgreSQL propio y proxy solo en loopback 8087/8447.
Una invocación local sin nombre de proyecto explícito creó adicionalmente una
pila vacía `logistech-production`; se detuvo y no se eliminaron sus volúmenes.
Los scripts ahora seleccionan explícitamente el proyecto según modo para evitar
esa confusión. No se modificó ni restauró sobre una base de trabajo.

## Implementación real

- Compose independiente de producción: React compilado, Caddy, Gunicorn y DB
  persistente privada; límites de recursos, logs rotados y health checks.
- Mismo origen para aplicación/API. Plantilla pública apunta al subdominio acordado,
  cookies seguras, DEBUG false, hosts y CSRF explícitos. Caddy prepara HTTPS ACME
  con renovación y almacenamiento persistente. No requiere Route 53 ni token DNS.
- Secretos por archivos ignorados y excluidos de builds; certificados PostgreSQL
  SAN db, CA explícita, `sslmode=verify-full`. CA privada y clave de recuperación
  de backup permanecen offline, sin montarse en la aplicación.
- Rol runtime sin privilegios administrativos/DDL/TRUNCATE; migración y backups
  por jobs de propietario. Restricciones/triggers históricos permanecen activos.
- Rate limiting atómico entre workers con PostgreSQL y claves HMAC; limpieza
  únicamente de contadores expirados y fallo cerrado si DB no está disponible.
- Parches de dependencias detectados durante auditoría: DRF 3.18.3, Caddy 2.11.7
  compilado con Go 1.27.3 y dependencias corregidas, gosu 1.20 recompilado y paquetes
  de SO actualizados. Instaladores pip/setuptools/wheel fuera del runtime final;
  pip check se ejecuta en la imagen de pruebas aislada.
- Scripts reproducibles de instalación Ubuntu, preflight, actualización, salud,
  generación de secretos, backup, restauración a DB nueva y cifrado autenticado.
- Plantillas CloudFormation Lightsail/EC2 sin credenciales, sin ejecución remota;
  workflow manual de imágenes/Trivy, sin permisos AWS ni despliegue automático.

No se incorporaron nuevas funcionalidades F8, se duplicaron modelos de negocio,
se reemplazó PostgreSQL por SQLite ni se realizó carga contra un servidor público.

## Archivos y migraciones

| Grupo | Archivos principales |
|---|---|
| Despliegue | `compose.production.yml`, `compose.production-rehearsal.yml`, `compose.production-tests.yml`, `.dockerignore`, `deploy/production.env.example` |
| Imágenes y proxy | `backend/Dockerfile`, `backend/.dockerignore`, `deploy/production/{proxy,postgres,provision,lint}.Dockerfile`, `Caddyfile`, `Caddyfile.local`, `routes.caddy` |
| Operación | `deploy/production/*.sh`, `pg_hba.conf`, `preflight.py`; `deploy/aws/lightsail.yaml`, `ec2.yaml` |
| Backend | `config/settings/{base,production,testing}.py`, `requirements.in/txt`, `apps/accounts/throttles.py`, `apps/core/models.py`, `cleanup_throttles.py` |
| Migración nueva | **`backend/apps/core/migrations/0001_initial.py`**, tabla técnica ThrottleWindow; no cambios de modelos/migraciones de negocio o auth |
| Pruebas | `test_database_throttles.py`, `test_production_settings.py`, `test_framework_security.py`, `frontend/e2e/production.spec.js`, configuración Playwright y ruta de evidencias de traceability |
| Verificadores | `scripts/verify_f7.py`, `production_database_check.py`, `check_image_vulnerabilities.py`, ampliación de `auditar_publicacion.py`, workflow manual |
| Documentos actuales | README, ARQUITECTURA, BASE_DE_DATOS, SEGURIDAD, PRUEBAS, MATRIZ_ENTREGABLES, nota de continuidad CLOUD_FASE_6 y documentos F7 enlazados abajo |

El listado completo y contenido exacto se obtienen con `git show --stat` y `git
diff 118eed3..codex/fase-7-despliegue`; no se incluyen `.env*`, claves, backups,
credenciales DEMO, cachés, imágenes Docker exportadas ni volúmenes.

## Pruebas ejecutadas y evidencia

Evidencias saneadas en [evidencias/fase7](evidencias/fase7/README.md). Logs de
construcción y datos privados completos permanecen en `output/qa/f7` ignorado.
No sumar repeticiones ni presentar estos resultados como pruebas sobre AWS.

| Verificación real | Resultado |
|---|---|
| Línea base F6 B2 antes de cambios | 273 passed, 26.97s |
| Backend F7 inicial | 298 passed; después del parche DRF, 307 passed |
| Backend final sobre PostgreSQL 17.11 actualizado y TLS | **307 passed, 32.75s** |
| Concurrencia/rate limiting y seguridad de dependencias | Incluidas en suite; carrera real de 12 threads, ventanas, limpieza concurrente, proxy, errores y fallo cerrado |
| Frontend unitarias | **15 passed**, sin fallos |
| Frontend lint/build; backend Ruff/pip check | Aprobados; bundle de producción generado |
| Playwright inicial: operations + traceability + production | 7 aprobados / 1 fallo de sincronización del test logout |
| Corrección de espera explícita logout HTTP 204 | Repetición del caso: 1 aprobado |
| Revalidación HTTPS con DRF corregido | **5/5 aprobados**, incluyendo expiración real JWT de 5min, único refresh, roles/aislamiento, QR, recepción, idempotencia, historial, accesibilidad y responsive |
| Smoke después de la última recompilación del proxy | **1/1 aprobado**, cookies/rutas/HTTPS/frontend compilado |
| Verificador F7, lectura y configuración | **10 checks aprobados**, incluyendo parser del dominio real sin conexión externa, rechazo de origen distinto, TLS con CA explícita y rutas/JSON |
| Migraciones | Aplicadas en ensayo; `migrate --check` y `makemigrations --check --dry-run` aprobados |
| Django `check --deploy` | Exit0, **2 warnings** HSTS includeSubDomains/preload documentados |
| PostgreSQL runtime/integridad | TLS1.3 verify-full; flags de privilegios false; triggers activos; cruces inválidos=0 |
| Backup/restore | Dump real, restauración en `restore_f7_validation` nueva; manifiestos de 8 modelos coincidentes; rechaza DB existente y DB fuente |
| Persistencia tras reemplazo de imágenes DB/proxy | Manifiestos de negocio antes/después idénticos; sin borrar volúmenes |
| Cifrado con scripts y corrupción controlada | Descifrado idéntico SHA-256; archivo alterado rechazado sin publicar plaintext |
| Plantillas AWS | cfn-lint1.58.0, validación offline de ambas plantillas en us-east-2, exit0 |
| Shell | Todos los scripts pasan `bash -n`; bootstrap remoto no ejecutado |
| npm audit producción | 0 vulnerabilidades reportadas en dependencias de producción |
| Auditor de publicación | 6 pruebas negativas aprobadas; revisión del índice y todo el historial local, sin valores privados impresos |
| Trivy runtime final | Backend0C/44H, proxy0C/1H, PostgreSQL3C/69H; ninguna HIGH con parche indicado pendiente; **gate falla por CRITICAL remanentes** |

Las pruebas Playwright usan DB/cuentas sintéticas exclusivamente de ensayo, no
simulan backend. La denegación de cámara se identifica expresamente como simulada;
no se afirma una captura física de cámara. La excepción de CA del navegador está
limitada por código a localhost; Python verificó la cadena con CA explícita y
rechazó el acceso sin confianza. No se resetean cuotas para hacer pasar pruebas.

## Errores encontrados y correcciones

1. Ruta `/admin/` heredaba fallback SPA; se corrigió a 404 independiente. Assets
   inexistentes ahora 404, nunca HTML ni cache immutable erróneo.
2. El test de logout inspeccionaba cookies antes de completar el POST204: espera
   explícita añadida y caso repetido aprobado; no se relajó la autenticación.
3. Permisos ACL de secretos Windows impedían lectura Docker: se corrigieron permisos
   explícitos por archivo, sin abrir a Everyone. Linux mantiene modos restrictivos.
4. `docker cp` no recuperaba el archivo DEMO del tmpfs aunque existía en el proceso:
   se capturó por canal privado sin imprimirlo, excluido de Git y de cloud.
5. Escaneo detectó vulnerabilidades corregibles de framework/Go/OpenSSL y herramientas
   de build. Se parchearon/recompilaron imágenes y repitieron pruebas. El metadata
   de Caddy se corrigió compilando como dependencia versionada para no confundir una
   versión pseudo con v2.11.7; no se ocultaron vulnerabilidades reales.
6. Selección accidental de proyecto Compose corregida y documentada arriba; scripts
   ahora separan explícitamente nombres. Ningún volumen/dato previo eliminado.
7. La primera auditoría clasificó la ruta pública `F7_SECRETS_DIR` como valor privado.
   Se corrigió esa clasificación específica; sigue comparando los valores reales de
   los archivos montados. Dos pruebas nuevas verifican detección y no divulgación
   de secretos, y aceptación de esa referencia pública.

Para repetir E2E **solo en el ensayo previamente preparado** con cuentas privadas
de validación, desde `frontend` (Bash; en PowerShell exportar variables equivalentes):

```bash
PW_BASE_URL=https://localhost:8447 PW_DEMO_FILE="$PWD/../.env.f7-demo.json" \
PW_REPORT=../output/qa/f7/e2e-repeat.json PW_REHEARSAL_TLS=true \
PW_PRODUCTION=true PW_EVIDENCE_PREFIX=fase7/regression \
node node_modules/@playwright/test/cli.js test e2e/operations.spec.js e2e/traceability.spec.js e2e/production.spec.js --workers=1
```

No ejecutar DEMO/QA contra datos de trabajo o cloud ni desactivar cuotas para
repeticiones. La suite completa incluye una espera real de expiración de cinco minutos.

## Presupuesto y límites

[Comparación y fuentes AWS](PRESUPUESTO_AWS_F7.md): recomendación condicionada
Lightsail4GB Ohio **US$24/mes** base, aproximadamente **4.17 meses de US$100** sin
extras. Snapshots opcionales requieren presupuesto adicional: reserva total28–32/mes,
aproximadamente3.13–3.57meses. La documentación vigente incluye EC2 y Lightsail en
Free Tier; no se verificó acceso concreto de la cuenta ni aplicación del crédito
al bundle seleccionado. No aceptar Paid Plan si Console lo pide.

Free Plan puede terminar al agotar crédito antes del28/04/2027. Respaldos cifrados
fuera de AWS son indispensables. DNS/TLS no requieren comprar otro dominio ni
servicio DNS; renovación del dominio existente es responsabilidad del titular.
Una VM no brinda alta disponibilidad ni capacidad certificada de concurrencia.

## Pendientes para publicar y checklist humano

- [ ] Revisar hallazgos residuales, especialmente los3 CRITICAL de la imagen DB;
  sin aprobación técnica de riesgo/corrección no declarar apta la publicación.
- [ ] Aprobar arquitectura, presupuesto y uso de créditos, sin cambio de plan.
- [ ] Confirmar cuenta/Ohio/bundle Ubuntu y cuotas, clave SSH/CIDR, contacto ACME.
- [ ] Revisar/publicar el commit F7 que se desplegará; `main` permanece estable.
- [ ] Crear VM+IP únicamente después de autorización; instalar host y transferir
  secretos nuevos por canal privado, conservando claves offline.
- [ ] Aprobar/agregar A `logistech` en Porkbun, verificar TLS público y renovación.
- [ ] Programar/monitorizar backups y copia externa, medir restauración AWS y repetir
  aceptación funcional desde otra red. No se midió RPO/RTO real de AWS ni SLA.

Guías: [implementación](AWS_F7_GUIA.md), [dominio/TLS](DNS_TLS_F7.md),
[seguridad](CHECKLIST_SEGURIDAD_F7.md), [backup/recuperación](BACKUP_RECUPERACION_F7.md).
F7 queda en **preparación local comprobada con revisión de seguridad pendiente**,
sin URL pública validada ni avance a nuevas fases funcionales.
