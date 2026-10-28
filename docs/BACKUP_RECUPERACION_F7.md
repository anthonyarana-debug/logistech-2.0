# Backup y recuperación — F7

Estado: procedimiento y ensayo **locales**, sin AWS ni tareas remotas programadas.
Datos privados fuera de Git. Base de trabajo anterior y volúmenes F6 conservados.

## Copia lógica

`bash deploy/production/backup.sh` ejecuta un job temporal con propietario de DB,
TLS `verify-full`, `pg_dump --format=custom`, validación `pg_restore --list`, sync
y SHA-256. El nombre incluye fecha UTC y sufijo aleatorio. Directorio 700/archivo
600; no elimina copias previas. La copia pg_dump es consistente para sus tablas;
no garantiza sincronización con otros sistemas externos. Incluye datos personales
y hashes de contraseñas: nunca adjuntarla a un informe ni subirla al repositorio.

Para ensayo, usar `F7_REHEARSAL=true` y `F7_ENV_FILE=.env.f7`; el proyecto queda
`logistech-f7-rehearsal`. En producción, proyecto `logistech-production`.

## Cifrado y copia externa

Generar **offline**, una sola vez por política de claves, clave RSA3072 y certificado
público del destinatario usando OpenSSL. Mantener la clave privada en un almacén
del operador con backup independiente; solo el certificado público va al servidor.
Los scripts no sobrescriben destinos existentes:

```bash
bash deploy/production/encrypt-offsite.sh COPIA.dump DESTINATARIO.pem NUEVA_COPIA.cms
# Copiar únicamente .cms por SSH/SFTP a un almacén externo al Free Plan.
# En equipo de recuperación autorizado, nunca con la clave privada en la VM:
bash deploy/production/decrypt-offsite.sh NUEVA_COPIA.cms DESTINATARIO.pem CLAVE_OFFLINE.key RECUPERADA.dump
```

CMS AES-256-GCM proporciona cifrado autenticado. Verificar SHA-256 del dump
descifrado contra el original. Proteger también el checksum y comprobar la copia
externa descargada. Los dumps locales sin cifrar siguen siendo sensibles: esta
preparación no afirma haber cifrado el disco Windows ni eliminado todas las copias
en claro. Definir retención, borrado aprobado y capacidad antes de automatizar.

Sugerencia inicial operativa: diario y antes de cada actualización, con revisión
del resultado y descarga externa. RPO objetivo 24h solo será verificable cuando la
tarea esté programada y monitorizada; RTO pendiente de medición en la VM. Snapshots
opcionales consumen crédito y no reemplazan una restauración lógica ensayada.
El cierre Free Plan puede bloquear todos los servicios de la cuenta; una copia
en S3 dentro de la misma cuenta no basta para ese riesgo.

## Restauración sin sobrescribir

1. Recuperar una copia autorizada y su `.sha256` al directorio privado de backups.
   Verificar autenticidad, checksum y permisos.
2. Elegir un nombre **nuevo**, por ejemplo `restore_revision_20261028`. El script
   rechaza cualquier nombre fuera de `restore_*` o base ya existente.
3. Ejecutar con variables públicas, nunca password en argumentos:

```bash
export STAGING_DB=restore_revision_20261028
export RESTORE_FILE=logistech-FECHA-SUFIJO.dump
bash deploy/production/restore.sh
```

4. El job crea una DB nueva, restaura en una transacción y aplica permisos al rol
   de aplicación sin CREATE ni TRUNCATE. Verificar conteos/manifest, integridad
   multiempresa, triggers y lectura con `scripts/production_database_check.py`.
   El ensayo real está documentado en `evidencias/fase7/database-restore.json`.
5. **La promoción es una operación distinta que requiere revisión.** Respaldar
   la DB vigente y planificar una ventana sin escrituras. Cambiar `POSTGRES_DB`
   en configuración y recrear solo servicios de aplicación contra la DB recuperada.
   No borrar la DB original; comprobar health/login/permisos y aceptar la promoción.
6. Valorar rotar la clave Django tras recuperación: invalida sesiones/JWT emitidos
   después del punto restaurado cuya revocación podría haberse perdido. Rotaciones
   de contraseñas DB en un volumen existente requieren ALTER ROLE controlado: cambiar
   el archivo por sí solo no cambia la contraseña persistida.

Para rollback, conservar el entorno anterior sin mezclar escrituras. No aplicar
automáticamente migraciones inversas ni eliminar bases. Una recuperación completa
también necesita el SHA de aplicación, configuraciones públicas, secretos protegidos,
certificado/clave PostgreSQL y capacidad de reenlazar DNS/IP según autorización.

## Certificados y persistencia

Conservar `postgres_data`, `static_data`, `caddy_data`, `caddy_config`. El CA privado
PostgreSQL es offline; certificado de servidor SAN `db` dura 365 días. Revisar con
30 días de antelación y renovar hoja/clave firmando con la CA offline; transferir
solo hoja, clave y CA pública, y recrear DB de forma controlada para recargar
montajes. No borrar volúmenes. Caddy renueva TLS público automáticamente cuando
DNS/puertos/CA son accesibles; esa renovación pública todavía no fue ejecutada.
