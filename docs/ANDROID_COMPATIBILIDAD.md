# Compatibilidad Android — contrato preparado, integración pendiente

No se abrió ni modificó el repositorio Android separado. No se afirman lenguaje,
SDK, librerías, endpoints o compatibilidad de su código sin auditarlo. Este contrato
identifica lo que debe revisarse antes de integrar.

## Interfaces necesarias

- HTTPS y API versionada /api/v1/. DTO UUID/ISO8601 UTC; estados REGISTERED,
  RECEIVED y REJECTED sin traducción de valores. Nombres de productos son datos.
- Identificar por payload exacto logistech:box:<qr_code>, UUID QR o CJ-internal_id
  usando GET /identification/resolve/?code= (codificar parámetros). No abrir URLs
  arbitrarias escaneadas; rechazar otros esquemas. El QR nunca contiene Bearer.
- GET /boxes/{model_uuid}/ para detalle, /qr/ para SVG/payload y /label/ para SVG
  imprimible. No confundir model UUID con qr_code; ver ENDPOINTS.md.
- POST /receipts/ con caja/sucursal/resultado/motivo e Idempotency-Key UUID. Guardar
  la misma clave y cuerpo en cola privada hasta conocer resultado; tras timeout
  reintentar sin generar una nueva. Nueva recepción201, replay200, conflicto409.
  La clave se limita por actor y empresa: cambio de cuenta no permite reutilizarla
  como autorización. No asumir éxito ante error de red ni inventar recepción offline.
- GET /receipts/ y /box-events/ con filtros estrictos y ámbito del servidor. Historia
  solo lectura, sin PATCH/DELETE. Box UUID snapshot puede sobrevivir borrado.
- Interpretar401 como sesión inválida/renovación controlada,403 permiso/asignación,
  404 recurso no disponible,400 validación,409 negocio/concurrencia,429 respetar
  Retry-After y500 genérico recuperable. Mantener error y comando para revisión.

## Autenticación y almacenamiento

La API actual devuelve access JWT y usa refresh en cookie HttpOnly, rotación,
consumo único y CSRF en endpoints de autenticación. No existe un endpoint móvil
alternativo que devuelva refresh en JSON. El cliente Android necesitará cookie jar
seguro y GET /auth/csrf/ antes de POST de auth, cabecera X-CSRFToken y cookie CSRF
coherentes. En HTTPS debe enviar Origin/Referer aprobados conforme a la configuración
Django; comprobarlo en la prueba de integración, no desactivar CSRF ni ampliar
orígenes indiscriminadamente. Authorization: Bearer en endpoints privados.

Conservar access solo en memoria cuando sea posible y secretos persistentes mediante
almacenamiento cifrado respaldado por Android Keystore; nunca logs, QR, URLs ni
preferencias sin cifrar. Renovación única concurrente y cierre seguro, respetando
cuotas actuales (login5/min/IP, refresh30/h/IP). En redes compartidas evaluar cuotas
sin debilitarlas como atajo de integración. No se han ejecutado pruebas Android.

## Auditoría previa del repositorio móvil

Revisar SDK/target y mantenimiento de dependencias, lector de QR y permisos de cámara,
cliente HTTP/TLS/CSRF/cookies, DTO, almacenamiento, sesiones, accesibilidad/offline y
pruebas. Comparar contra los contratos reales, determinar cambios compatibles y
probar con dos empresas y usuarios reasignados/desactivados. Las rutas españolas
web no son endpoints nuevos para Android; no acoplar cliente nativo a React.

## Alcance posterior

Recepción no mueve existencias ni sucursal. Transferencias, movimientos, conciliación,
reportes y eventos compensatorios se diseñarán como próximos bloques con versiones
aditivas y pruebas, manteniendo la historia existente.

## Hitos de evolución pendientes

1. Movimiento inmutable con origen/destino, producto, unidades, motivo y vínculo
   único a evento/recepción; definir unidades y recepciones parciales antes de contar stock.
2. Saldo por empresa/producto/sucursal, conciliación y correcciones compensatorias;
   impedir doble conteo de cajas históricas sin recibo trazable.
3. Transferencias con estados y confirmación en ambos extremos; transacciones y
   permisos expresos. User.branch organizativa no implica permiso de traslado.
4. Reportes paginados/exportación segura basados en eventos reales; establecer
   fechas/cobertura y no inventar tendencias anteriores al historial instrumentado.
5. Ensayo Android con cámara real, TLS, cookies/CSRF, cola de comandos/idempotencia,
   expiración, múltiples empresas y cuenta desactivada antes de declarar integración.
