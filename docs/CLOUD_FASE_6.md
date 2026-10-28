# Ruta cloud F6 — preparación sin aprovisionamiento

## Continuidad F7 (28/10/2026)

Se preparó una arquitectura de VM única AWS y ensayo HTTPS local sin modificar
infraestructura externa. Dominio acordado `logistech.stackpe.online`, DNS en Porkbun.
Ver [INFORME_FASE_7](INFORME_FASE_7.md), [presupuesto](PRESUPUESTO_AWS_F7.md),
[guía](AWS_F7_GUIA.md). Free Plan US$100 y vencimiento28/04/2027 según el usuario;
recursos/creditibilidad reales pendientes de confirmar. Cloud sigue parcial.
El contenido F6 a continuación se mantiene como antecedente, no autorización.

Estado: parcial. El repositorio público aloja código, no una aplicación cloud desplegada. No se contrató infraestructura ni se publicaron servicios. Las pruebas locales no demuestran capacidad cloud.

## Base reutilizada

Conservar Dockerfile de producción, configuración Django de producción, Gunicorn, plantilla deploy/production.env.example, health/readiness y pruebas de producción existentes. Revisar DESPLIEGUE.md y SEGURIDAD.md antes de seleccionar proveedor. No copiar .env local ni credenciales de pruebas a un entorno externo.

## Secuencia de staging propuesta

1. Confirmar proveedor/región, presupuesto, dominio, responsables y autorización antes de crear recursos de pago. Estimar API, PostgreSQL, backups, tráfico y almacenamiento; no hay cotización verificada en este documento.
2. PostgreSQL administrado privado con usuario de privilegios mínimos, TLS verify-full y certificados verificados. Red privada; no exponer 5432. Backup previo y ensayo de restauración antes de migrar una base existente.
3. Imagen backend fijada por commit y frontend compilado. Ejecutar Gunicorn y HTTPS en proxy/plataforma; jamás Django runserver ni Vite de desarrollo. Mismo origen para API/cookies, CORS/CSRF y hosts explícitos. Secretos mediante gestor del proveedor, nunca Git ni argumentos registrados.
4. Sustituir LocMem para throttling por contadores compartidos antes de múltiples procesos/instancias; comprobar atomicidad y cuotas. No declarar capacidad distribuida con la caché actual.
5. Job único de migración: verificar estados ACTIVE/INACTIVE y coherencia User.branch/company antes de 0002. Si existe dato inválido, detener y corregir con trazabilidad; no borrar ni relajar CHECK. Validar actualización en copia restaurada y luego migrar staging autorizado.
6. Crear SUPERADMIN por procedimiento administrativo seguro; sin password predeterminado. Mantener pruebas/demos fuera de producción. Smoke de login/CSRF, roles, dos empresas, desactivación, API y health, con cuentas controladas y sin secretos en logs.
7. Revisar retención/redacción de logs, límites de solicitudes y consultas, paginación y alertas. Ejecutar carga específica de nuevos endpoints en staging autorizado; resultados Locust F5 no la sustituyen.
8. Promoción y rollback de imagen a commit previo con esquema compatible; no revertir migraciones destructivamente como rutina. Ante fallo de datos usar procedimiento de recuperación aprobado y backup verificado.

## Criterios pendientes

HTTPS/DNS reales, conectividad TLS PostgreSQL externa, backup/restauración cloud, límites compartidos, supervisión y costes requieren comprobación. También faltan stock/movimientos/auditoría e integración Android de siguientes bloques. Preparar staging puede avanzar paralelamente; no se afirma que esté desplegado.

## Preparación adicional del Bloque 2 (F7 sin despliegue)

Los QR/etiquetas se generan como SVG en memoria, sin bucket, archivos públicos ni
persistencia de imagen. No se requiere S3 para este bloque. Si posteriormente se
archivan etiquetas, usar acceso privado/caducidad y permisos de empresa; nunca
publicarlas automáticamente. La aplicación web requiere HTTPS/contexto seguro
para cámara; CSP debe permitir imágenes Blob de mismo contexto y Permissions-Policy
limitar cámara al origen autorizado, sin permisos automáticos.

Respaldar PostgreSQL con Receipt, BoxEvent, constraints, índices y funciones/triggers.
Ensayar restore que conserve idempotencia e inmutabilidad; monitorizar crecimiento
del historial/índices y retención legal. No implementar purga que borre auditoría
ordinariamente. 0003/0004 son aditivas sin backfill ficticio; migrar como job único
tras backup y prueba de actualización/restauración. Las cuentas de aplicación no
deben tener privilegios de superusuario, TRUNCATE o alteración de triggers.

Probar concurrencia en el servicio administrado objetivo, manejo40P01/40001, cuotas
compartidas, TLS, restauración y rollback de aplicación compatible con esquema. Los
QR son públicos como identificadores, pero su descarga/resolución siguen privadas.
Ningún recurso AWS de pago ni servicio externo fue aprovisionado o desplegado.
