# Seguridad — estado de Fase 2

## Controles implementados y verificados

- PBKDF2-SHA256 de Django, contraseñas no almacenadas en claro, validadores y longitud mínima 12 en registro. Hash real usado también en pruebas, sin sustituirlo por un algoritmo débil.
- Registro de operador sin empresa, rechazo explícito de campos extra y flags privilegiados. Email único sin distinguir mayúsculas con restricción PostgreSQL.
- Rol y flags coherentes mediante gestor, clean y CHECK DB; createsuperuser seguro y Admin limitado a superadmin activo. is_staff por sí solo no otorga privilegios globales.
- JWT de acceso de 5 min y refresh de 1 día en cookie HttpOnly; Secure en production, SameSite=Lax, no-store en respuestas de autenticación. Rotación, blacklist y serialización transaccional del consumo de refresh. Usuario activo leído en DB.
- CSRF obligatorio para registro/login/refresh/logout y sesión Admin; rechazo de Origin ajeno, incluso con token CSRF correcto. No se activó CORS abierto.
- Política inicial HasCompanyAccess: sin empresa/inactiva deniega; objeto de otra empresa deniega; superadmin global requiere flags. **No equivale aún a CRUD seguro:** F3 debe aplicar filtros y permisos en endpoints reales.
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
