# Seguridad — estado de Fase 4

Las secciones de autenticación F2 y autorización CRUD F3 se conservan. La integración web F4 añade los controles siguientes.

## Sesión y referencias web F4

- Access solo en memoria de módulo, sin localStorage/sessionStorage/IndexedDB. Refresh HttpOnly sigue en cookie del backend; CSRF se obtiene mediante la ruta autorizada. Credenciales Fetch `same-origin`; proxy existente, sin abrir CORS.
- Restauración y renovación comparten promesa. Cada petición protegida reintenta una sola vez después de 401; no reintenta automáticamente mutaciones tras fallo de red. Un número de revisión impide que un refresh concurrente restaure la identidad después de logout. Prueba real con access de cinco minutos, más unitarias de concurrencia.
- Logout borra inmediatamente access/identidad y revoca refresh en servidor. Si la red falla, conserva únicamente `logistech.logout-pending=true` en sessionStorage para reintentar la revocación antes de restaurar o iniciar otra sesión. Este marcador no contiene identidad ni secretos. La UI informa que el cierre no pudo confirmarse. Almacenamiento web deshabilitado limita esa persistencia entre recargas.
- Rutas privadas bloqueadas durante restauración/error/expiración. Cuenta sin empresa no monta AppShell ni consulta referencias/inventario. Caches de consultas quedan en componentes, se descartan al desmontar y no muestran resultados de otro contexto al cambiar filtros de empresa.
- Selección de empresa solo para superadmin; formularios no ofrecen role/created_by/identificadores ni transferencias de empresa. Cada operación sigue validada por el backend. Referencias de lectura no amplían los permisos de escritura.
- Errores 500 del cliente muestran texto genérico, nunca el cuerpo interno. Fallos de red y health tienen mensajes españoles. Timeout 15 s en API y 6 s en health. No se registra cuerpo de autenticación ni access en consola.
- Datos DEMO se crean por comando explícito y namespace nuevo; archivo de claves aleatorias 0600, copia local ignorada con ACL restringida al usuario. No usar contra producción, no publicar/copiar el archivo ni capturar formularios con claves visibles. Usuarios demo incluyen superadmin: usar solo para la demostración local autorizada. No hay claves fijas ni variables VITE_ secretas.
- Playwright no conserva trace, vídeo ni storageState. Salidas crudas y contextos de fallo se ignoran; solo resumen de nombres/resultados y capturas sin secretos se versionan. Los tests no desactivan CSRF, permisos, expiración o throttles. El test de pérdida de refresh elimina su propia cookie e inyecta un Bearer inválido; ambos rechazos los resuelve el servidor.

Persisten los límites de F3: LocMem por proceso, listas sin paginar, servidor de desarrollo local, acceso HTTP solo loopback. Sin RLS, CSP de producción, pruebas cloud o certificación de seguridad. Un XSS sigue pudiendo actuar durante una sesión activa: mantener revisión de dependencias y evitar HTML arbitrario; React escapa textos y no se usa dangerouslySetInnerHTML.

## Controles implementados y verificados

- PBKDF2-SHA256 de Django, contraseñas no almacenadas en claro, validadores y longitud mínima 12 en registro. Hash real usado también en pruebas, sin sustituirlo por un algoritmo débil.
- Registro de operador sin empresa, rechazo explícito de campos extra y flags privilegiados. Email único sin distinguir mayúsculas con restricción PostgreSQL.
- Rol y flags coherentes mediante gestor, clean y CHECK DB; createsuperuser seguro y Admin limitado a superadmin activo. is_staff por sí solo no otorga privilegios globales.
- JWT de acceso de 5 min y refresh de 1 día en cookie HttpOnly; Secure en production, SameSite=Lax, no-store en respuestas de autenticación. Rotación, blacklist y serialización transaccional del consumo de refresh. Usuario activo leído en DB.
- CSRF obligatorio para registro/login/refresh/logout y sesión Admin; rechazo de Origin ajeno, incluso con token CSRF correcto. No se activó CORS abierto.
- HasCompanyAccess deniega sin empresa/inactiva y objeto ajeno; superadmin global requiere flags. F3 ya complementa esta base con ResourcePermission, querysets acotados y serializers estrictos en endpoints reales, descritos al final.
- PostgreSQL privado en Compose; web/API en loopback, procesos web sin root; .env excluido, plantilla ficticia, secretos ausentes de evidencias.
- Errores genéricos para login/token/CSRF y base de datos; sin contraseñas, cookies ni Authorization en logs del código.

## Límites de solicitudes implementados

| Ámbito | Clave | Límite |
|---|---|---|
| Login API y Admin | IP real de conexión | 5/min compartido |
| Login API | HMAC del email normalizado, sin correo en texto claro en clave caché | 10/15 min |
| Registro | IP | 3/h |
| Refresh | IP | 30/h |
| Logout | IP | 60/h |
| CSRF | IP | 60/min |
| CRUD categorías/cajas | Usuario | 120/min compartido |

Se cuentan intentos que pasan CSRF y llegan al handler/throttle; un POST rechazado previamente por CSRF devuelve 403 y no garantiza 429. Las pruebas de rate limiting usan CSRF válido. NUM_PROXIES=0 evita aceptar X-Forwarded-For arbitrario. La ventana de 15 minutos tiene parser explícito; DRF estándar no interpreta ese número de minutos.

**Ajuste respecto a propuesta F0:** refresh se limita por IP en esta base inicial, no por cuenta; una petición sin autenticar no aporta una identidad confiable. Debe revisarse el uso compartido de IP (también el proxy Vite) y el despliegue autorizado antes de producción.

Cache actual: LocMemCache por proceso. Pruebas verifican límites, 429, Retry-After y recuperación de ventana locales. Operaciones de historial de DRF no son atómicas y no se comparten entre workers: no se declara rate limiting distribuido ni protección DDoS. F7 debe definir proxy/red confiables y almacenamiento/operaciones compartidas según infraestructura real. No se añadió Redis sin necesidad actual.

## Límites y pendientes

Un access emitido puede seguir válido hasta 5 minutos después de logout; logout solo revoca el refresh presentado. No existe revocación de todas las sesiones por familia ni política absoluta de duración de sesión. Cambio de empresa/rol se consulta en DB; no se usa un rol fijo del claim JWT para conceder permisos.

Registro duplicado produce 400 genérico; no se garantiza resistencia completa a enumeración basada en todos los códigos/tiempos. Login inválido, cuenta ausente e inactiva devuelven el mismo 401 genérico. Restablecimiento de contraseña, verificación de email, OAuth, auditoría persistente completa y reglas avanzadas permanecen pendientes.

Validaciones de pertenencia entre entidades se aplican en modelo/save/Admin, pero no son constraints cruzadas en PostgreSQL. Evitar bulk/update/SQL sin servicio validado. Los campos role y flags sí tienen CHECK y el email tiene UNIQUE, probados incluso al omitir clean.

OutstandingToken de Simple JWT almacena refresh tokens; proteger acceso y backups de DB. Limpiar expirados con `python manage.py flushexpiredtokens` en un procedimiento autorizado futuro; no se creó automatización. La cuenta PostgreSQL inicial sigue siendo administradora local para pruebas: separar rol de aplicación antes de cloud.

Production activa HTTPS redirect, cookies Secure y rechaza DEBUG=true/claves cortas. **No hay producción desplegada ni TLS verificado.** Persisten W005/W021 de HSTS (subdominios y preload), pendientes del dominio real y no silenciadas. Servidores de desarrollo no se publican.

## Evidencias

[fase2-verificacion.json](evidencias/fase2-verificacion.json), pruebas test_auth.py, test_throttling.py y test_models_permissions.py. Las fixtures viven en DB test_ y la prueba HTTP deja únicamente una cuenta de prueba inactiva por ejecución; no inventario.

CHECKLIST HUMANO: crear superadmin con prompt local si se necesita; configurar secretos solo en herramientas locales/gestor del proveedor; autorizar antes de recursos cloud. No enviar contraseñas o tokens al chat.

## Autorización e integridad de CRUD F3

- JWT obligatorio en categorías/cajas; sin empresa activa se deniega acceso. Superadmin global identificado por rol y flags vigentes. Admin y operador permanecen en su empresa; operador no administra categorías ni elimina cajas.
- Querysets filtran empresa antes de lookup, búsqueda o filtros. Detalle ajeno 404 cuando el rol tiene permiso de método; rol sin permiso 403 sin distinguir existencia. No se acepta cambiar ámbito desde filtros/cuerpos de usuario no global.
- Lista blanca de query params, UUID tipados, valores validados y rechazo de duplicados/lookups ORM. Search solo usa campos concretos y ORM parametrizado.
- Serializers rechazan campos extra y de lectura. Empresa se impone desde usuario salvo POST superadmin con empresa explícita. Ni siquiera superadmin modifica company/created_by/identificadores por actualización REST.
- Producto/sucursal activos y de la misma empresa, con categoría coherente. Referencias ajenas/no disponibles producen validación genérica. El listado de cajas no sirve filas con relaciones de pertenencia incoherentes por escrituras externas.
- Transacciones en escrituras y bloqueos del actor/recurso/empresa/referencias para releer el estado vigente; conflictos concurrentes probados con dos actores/conexiones. No se permite sobrescribir un estado final desde una lectura anterior.
- UNIQUE y CHECK existentes conservados; nueva migración CHECK de status/priority. Creación de identificadores reintenta solo colisiones reconocidas, hasta tres veces; no omite errores de integridad.
- Creador histórico inmutable por save/API y conservado ante reasignaciones. Los permisos consultan la pertenencia actual del usuario. Direct SQL/bulk sigue siendo una vía administrativa privilegiada y no se promete RLS/triggers de coherencia cruzada.
- DELETE categoría referenciada devuelve 409 mediante PROTECT; caja recibida/rechazada no admite edición efectiva ni borrado. No se ha construido historial/recepción completo.
- Errores inesperados de vistas DRF son JSON 500 genérico incluso con DEBUG activado en la prueba de fallo. El log de ese handler registra solo la clase de excepción, sin su texto, SQL ni datos enviados. La configuración por defecto continúa DEBUG=false.

Rate privado compartido: 120/min por usuario sobre categorías/cajas; 429 y Retry-After, aislamiento de contadores entre usuarios y recuperación de ventana probados. LocMemCache sigue por proceso y las operaciones de DRF no son atómicas. Es una limitación explícita, no evidencia distribuida ni prueba de carga F5.

Evidencia actual: test_crud.py y fase3-verificacion.json; incluye pruebas HTTP sobre servidor efímero con DB test_, sin nuevos datos de negocio permanentes. No se abrió CORS, red, puerto ni servicio adicional.
