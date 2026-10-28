# Referencia de API interna para mantenimiento

## Ampliación F6

- accounts.operations: UserAdministration, UserAdministrationSerializer, UserViewSet; asignación y desactivación con filas bloqueadas. Sin DELETE ni reset de contraseña.
- organizations.serializers/views: CompanySerializer/CompanyViewSet (global), BranchSerializer/BranchViewSet (tenant).
- catalog.serializers/views: ProductSerializer/ProductViewSet, queryset y categoría limitados por empresa.
- core.operational_serializers: validación estricta de payload; core.operations_messages: mensajes ingleses centralizados.
- core.overview: recuentos reales según rol y company; sin métricas históricas inventadas.
- frontend/services/operations.js: política de presentación canAdminister/canEditUser/dashboardKey; la autorización efectiva permanece en API.
- frontend/pages/Administration.jsx: formularios y tablas Companies/Branches/Products/Users conectados a servicios reales. AppShell limita navegación y remonta Outlet al cambiar empresa.

Contratos públicos, filtros y códigos: ENDPOINTS.md. User.branch nullable es aditivo; campos y rutas anteriores se conservan.

Esta referencia complementa [ENDPOINTS](ENDPOINTS.md), que define el contrato REST. Expone las interfaces relevantes existentes; no declara módulos futuros implementados. Los tipos son descriptivos de Python/JavaScript, sin introducir TypeScript ni cambiar firmas públicas.

## Backend: identidad y sesión

| Interfaz / archivo | Entradas obligatorias y opcionales | Retorno / propósito | Restricciones y errores |
|---|---|---|---|
| `UserManager.create_user(email, password=None, **extra_fields)` — accounts/managers.py | email:string; password:string o None; atributos de modelo opcionales | User persistido, email normalizado y contraseña con hash | full_clean valida privilegios/empresa; ValueError si falta email; no usar secretos en logs |
| `create_superuser(email, password=None, **extra_fields)` — mismo gestor | email; contraseña por prompt; flags opcionales coherentes | User SUPERADMIN activo sin empresa | Rechaza flags/alcance incoherentes; no credenciales fijas |
| `RegistrationSerializer.validate(attrs)` — accounts/serializers.py | dict email/password y nombre/apellido opcionales | dict validado y normalizado | Validadores de contraseña, campos privilegiados rechazados; ValidationError |
| `LoginSerializer.validate(attrs)` — mismo archivo | email/password, contexto request | dict con User autenticado | AuthenticationFailed seguro, sin enumeración de cuentas |
| `identity(user)` — mismo archivo | User vigente | dict id/email/nombres/role/company/assignment_pending | No retorna password, refresh ni flags privilegiados |
| `token_response(user, refresh)` — accounts/views.py | User, RefreshToken | Response con access/user y cookie de refresh | HttpOnly; Secure en producción; no almacenamiento web persistente |
| `read_refresh(request)` — mismo archivo | request con cookie | tuple(raw:string, token:RefreshToken) | AuthenticationFailed si falta/expira; no aceptar refresh desde JSON |
| `RefreshView.post(request)` — mismo archivo | CSRF, cookie; JSON vacío | Response 200, refresh rotado | Transacción/bloqueo OutstandingToken, blacklist, cuenta activa; 401/403/429 |
| `LogoutView.post(request)` — mismo archivo | CSRF; cookie opcional | Response 204, elimina cookie | Idempotente; access ya emitido puede durar hasta cinco minutos |

## Backend: permisos y CRUD

| Interfaz / archivo | Argumentos y valores predeterminados | Resultado | Reglas de mantenimiento |
|---|---|---|---|
| `is_global(user)` — core/api.py | User autenticado | bool | Solo SUPERADMIN con flags staff/superuser coherentes |
| `HasCompanyAccess.has_permission(request, view)` — accounts/permissions.py | request/view | bool | Usuario activo; empresa activa o superadmin; sin empresa no inventario |
| `ResourcePermission.has_permission(request, view)` — core/api.py | request/view, operator_write=False por defecto | bool | Operador puede leer y escribir cajas autorizadas; no DELETE ni escritura de categorías |
| `StrictModelSerializer.get_fields()` — core/api.py | contexto request, instancia opcional | dict de campos | Company seleccionable solo al crear por superadmin; etiquetas/choices inglesas sin cambiar identificadores |
| `to_internal_value(data)` — mismo serializer | Mapping JSON | valores internos validados | Rechaza campos desconocidos/read-only, no los ignora silenciosamente |
| `TenantViewSet.get_queryset()` — core/api.py | request y action | QuerySet acotado y ordenado | Filtra empresa antes de consultar; filtros explícitos/únicos; UUID y choices validados; bloqueo de escritura |
| `lock_actor()` / `lock_company(company)` — mismo viewset | usuario de request / Company | actor o Company releídos con bloqueo | Ejecutar dentro de atomic; autoridad vigente del servidor, no claims/payload |
| `create/update/destroy(request, *args, **kwargs)` — mismo viewset | petición DRF y UUID de URL cuando corresponde | Response 201/200/204 | atomic; restricciones negocio/integridad → 400/403/404/409; no saltar permisos con escrituras masivas |
| `BoxSerializer.validate(attrs)` — boxes/serializers.py | atributos y contexto/instancia | dict validado | Producto/sucursal de la empresa, nueva caja REGISTERED; final inmutable |
| `BoxSerializer.create(validated_data)` — mismo archivo | atributos de caja | Box | Hasta tres intentos para colisiones de IDs; no ocultar otros errores de integridad |
| `BoxViewSet.lock_references(serializer, company)` — boxes/views.py | serializer y Company bloqueada | None; actualiza referencias validadas | Activas, misma empresa; creador impuesto al crear |
| `CategorySerializer.validate(attrs)` — catalog/serializers.py | nombre, empresa y demás campos | dict | Unicidad por empresa sin distinguir mayúsculas; conflicto 409 |
| `ReferenceView.get(request)` — core/references.py | company UUID opcional; sin otros filtros | Response de companies/products/branches/categories | Solo referencias activas/coherentes; no CRUD público de organizaciones |
| `internal_id()` — boxes/models.py | sin argumentos | string CJ- + UUID hexadecimal | Identificador automático independiente del QR; no autorización por conocerlo |

## Backend: errores, salud e idioma

`api_exception_handler(exc, context)` devuelve Response DRF con códigos originales y claves `detalle`/`errores`; inesperados → 500 genérico. `csrf_failure(request, reason="")` devuelve JSON 403 sin reflejar reason. `health(request)` consulta SELECT 1 y devuelve 200/503; `live(request)` no consulta DB. Implementación: core/errors.py y core/views.py.

`message(key)` devuelve el mensaje inglés conocido; clave inexistente → KeyError de programación, capturado como 500 seguro en la API. `domain_message(value)` traduce solo un mensaje de dominio exacto conocido; demás valores se conservan. `presentation_options(options)` copia metadatos de presentación, sin mutar el modelo. `EnglishAdminMixin` localiza formularios/choices/contextos, manteniendo permisos de ModelAdmin/UserAdmin y validación del modelo. `EnglishRelatedWidgetWrapper` conserva los flags de acceso del widget original. No invocar estos adaptadores para traducir datos persistidos.

## Frontend: cliente de sesión y API

Implementación principal: `frontend/src/services/api.js`.

| Firma | Entradas / defaults | Retorno y comportamiento |
|---|---|---|
| `subscribe(fn)` / `snapshot()` | callback / ninguno | función para desuscribir / estado actual; useSyncExternalStore |
| `restore(force=false)` | bool opcional | Promise de restauración deduplicada; si logout pendiente, primero confirma cierre |
| `login(data)` | objeto email/password | Promise; espera bootstrap/refresh y publica identidad vigente |
| `register(data)` | email/password; first_name/last_name opcionales | Promise con identidad de operador pendiente, sin iniciar sesión |
| `renew()` | ninguno | Promise compartida para refresh concurrentes; 401 termina sesión |
| `logout()` | ninguno | Promise; borra access/identidad inmediatamente y confirma revocación por CSRF |
| `api(path, options={})` | ruta relativa; method=GET, data/signal opcionales | Promise JSON/null para 204; ante 401 renueva y reintenta una vez; conserva AbortSignal |
| `updateProfile()` | ninguno | Promise User; recarga identidad desde servidor |
| `new ApiError(status, data, retryAfter)` | status:number, JSON opcional, segundos opcionales | Error con status, fields desde errores y retryAfter; 500 no refleja contenido interno |

Estructura de sesión: `{status, user, error, reason}`; access queda en cierre del módulo. `revision` evita resucitar identidad tras logout concurrente. Solo la marca no sensible de logout pendiente puede almacenarse en sessionStorage; nunca tokens o identidad. Raw Fetch usa same-origin, no-store y timeout de 15 segundos; estos helpers internos no se exportan como API pública.

## Frontend: consultas, salud y presentación

- `useRemote(path, query={}, enabled=true)` — hooks/useRemote.js: consulta autenticada, aborta peticiones al cambiar contexto, expone data/loading/error/reload; no sustituye autorización backend. `useDebounced(value, delay=300)` difiere entrada para búsquedas.
- `getHealth()` — services/health.js: Promise JSON health con timeout de seis segundos; mantiene estado/disponible como protocolo, presenta errores en inglés y usa código interno de fallo para controlar recuperación.
- `t(key, values={})` — i18n/index.js: string del catálogo; placeholders requeridos, sin HTML ni traducción externa. `formatNumber(value)`, `formatDate(value)` y `resultCount(count, boxes)` centralizan formatos/plural. Español solo preparado, no selector habilitado.
- `useAuth()` / `AuthProvider` — auth.jsx: contexto de sesión; `Protected({children})` impide mostrar inventarios mientras restaura, cuando no hay sesión o falta empresa. Es protección de UX, no barrera de seguridad suficiente.
- `useTenant()` — components/AppShell.jsx: ámbito seleccionado para superadmin; ámbito impuesto para demás roles. La API revalida el alcance.
- `BoxForm({record, onClose, onSaved})` y listado `Resources({kind})` — pages/Resources.jsx: record opcional para edición; kind categories/boxes; servidor decide company/created_by/IDs. Nunca usar etiquetas traducidas como valores enviados al servidor.

Para ejecutar: seguir [NUEVA_COMPUTADORA](NUEVA_COMPUTADORA.md). Para cambios: preservar firmas, contratos y pruebas; usar entornos aislados y ejecutar [PRUEBAS](PRUEBAS.md). No exponer herramientas de carga o fallos inyectados como endpoints públicos.

## Comando académico de datos DEMO

`python manage.py create_demo --namespace <namespace> --output <ruta>`: ambos argumentos son obligatorios. Namespace exige 3–32 letras minúsculas ASCII, números o guiones. Rechaza namespace/archivo existentes; no restablece contraseñas. Crea dos empresas y referencias/cajas/usuarios rotulados, con contraseñas aleatorias y archivo exclusivo 0600. Devuelve confirmación inglesa con la ruta; nunca imprime valores de credenciales. En Windows, restringir la ACL de la copia privada. No ejecutar contra producción. Sus datos de negocio españoles son fixtures identificados y no se traducen como UI.
