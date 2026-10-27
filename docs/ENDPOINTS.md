# Contrato REST implementado — Fase 4

Base: `/api/v1/`. Español para mensajes; campos del código en inglés. Desarrollo local: frontend 127.0.0.1:5173 con proxy y API 127.0.0.1:8000. Autenticación F2 y CRUD F3 conservados; frontend conectado en F4.

## Consulta mínima de referencias F4

`GET /api/v1/references/` exige Bearer y empresa activa para usuarios no globales. Comparte el límite de 120/min/usuario con CRUD y devuelve `Cache-Control: no-store`. HEAD/OPTIONS disponibles según DRF; POST/PUT/PATCH/DELETE no implementados (405 tras autenticación).

Único filtro opcional: `company=<UUID>`, una sola vez. Usuario no global: solo su empresa; otro ámbito 403 sin revelar su existencia. Superadmin: lista de empresas activas; sin company, productos/sucursales/categorías vacíos; con company, referencias de esa empresa activa. UUID inválido, empresa no disponible para el contexto global, filtro desconocido/repetido: 400. Anónimo 401; operador sin empresa/empresa inactiva 403; límite 429; inesperado 500 genérico.

Respuesta 200:

```json
{
  "companies": [{"id": "<uuid>", "name": "<empresa activa>"}],
  "company": "<uuid o null>",
  "products": [{"id": "<uuid>", "name": "<nombre>", "sku": "<SKU>", "category": "<uuid>", "category_name": "<nombre>"}],
  "branches": [{"id": "<uuid>", "name": "<sucursal>"}],
  "categories": [{"id": "<uuid>", "name": "<categoría>"}]
}
```

Solo productos y sucursales activos. Productos con categoría de otra empresa se excluyen. Categorías no poseen campo de actividad; se restringen por pertenencia. Listas sin paginación para el alcance inicial, orden por nombre e id. No hay CRUD nuevo de empresas, productos o sucursales. Pruebas: `test_references.py`; selección visible E2E de los tres roles autorizados. Validación definitiva de FK permanece en las escrituras F3.

## Rutas

| Método/ruta | Parámetros/cuerpo | Autorización | Respuesta correcta | Errores previstos |
|---|---|---|---|---|
| GET `/health/` | Ninguno | Público | 200 `{estado, base_de_datos}` | 503 si PostgreSQL falla |
| GET `/health/live/` | Ninguno | Público | 200 `{estado, servicio}` | No consulta DB |
| GET `/auth/csrf/` | Ninguno | Público, 60/min/IP | 200 `{csrfToken}` y cookie csrftoken | 429 |
| POST `/auth/register/` | email, password; first_name/last_name opcionales | CSRF válido, 3/h/IP | 201 identidad de operador sin empresa, sin tokens | 400 validación/duplicado/campos extra; 403 CSRF; 429 |
| POST `/auth/login/` | email, password | CSRF válido; 5/min/IP y 10/15 min por email normalizado | 200 `{access, user}` y cookie HttpOnly lt_refresh | 400 formato; 401 credenciales/cuenta inactiva; 403 CSRF; 429 |
| POST `/auth/refresh/` | `{}`; refresh únicamente en cookie | Cookie + CSRF; 30/h/IP | 200 `{access, user}`, nueva cookie y revocación de anterior | 401 ausente/inválido/expirado/reutilizado/inactivo; 403 CSRF; 429 |
| POST `/auth/logout/` | `{}` | CSRF; 60/h/IP, cierre idempotente | 204 sin cuerpo y cookie eliminada; refresh revocado si era válido | 403 CSRF; 429 |
| GET `/auth/me/` | Sin query/body de identidad | `Authorization: Bearer <access>` | 200 identidad propia, empresa vigente o null | 401 token ausente/inválido/expirado, refresh usado como access o usuario inactivo |

`/admin/` usa formularios y sesión Django, no JWT. Acceso de negocio restringido a SUPERADMIN activo con flags coherentes. El POST de login administrativo comparte el límite por IP del login API y conserva CSRF.

## Cuerpos y ejemplos

Registro y login reciben JSON; password tiene máximo 128 caracteres y el registro exige validadores Django, mínimo 12. El servidor rechaza todos los campos desconocidos, incluidos role/company/company_id/is_staff/is_superuser/is_active/groups/user_permissions. No basta ignorarlos.

```json
{
  "email": "operador@example.test",
  "password": "<valor introducido localmente, no registrado en logs>",
  "first_name": "Nombre",
  "last_name": "Apellido"
}
```

El ejemplo usa un marcador, no una contraseña de demostración. Login solo acepta email/password. El email se normaliza a minúsculas y espacios exteriores. Identidad correcta:

```json
{
  "id": "<uuid>",
  "email": "operador@example.test",
  "first_name": "Nombre",
  "last_name": "Apellido",
  "role": "OPERATOR",
  "company": null,
  "assignment_pending": true
}
```

Cuando existe asignación, company contiene `{id, name}`. El endpoint no acepta seleccionar otro usuario o empresa. El registro no inicia sesión automáticamente.

Secuencia de uso web: GET csrf → conservar cookie csrftoken y usar csrfToken en `X-CSRFToken` → POST register o login con JSON → guardar access solo en memoria → GET me con Bearer → POST refresh con cookie+CSRF → POST logout. En F4 Fetch debe usar credenciales de mismo origen; el navegador administra la cookie HttpOnly. Ni tokens ni csrf se escriben en logs ni en localStorage.

Demostración ejecutable sin introducir o imprimir secretos:

```powershell
docker compose exec -T backend python -m tools.verificar_http_auth
```

Crea una cuenta técnica de prueba, verifica ocho respuestas reales y al finalizar la desactiva e inutiliza su contraseña. Cada ejecución deja una cuenta técnica inactiva para distinguirla de usuarios reales. Para la suite completa usar `python scripts/verificar_fase2.py`.

La prueba HTTP consume las cuotas reales, incluido registro 3/h/IP: varias ejecuciones seguidas pueden obtener 429. No se reinician contadores ni se desactivan límites para presentar un resultado exitoso. Las pruebas pytest usan su propio proceso/caché y base de prueba.

Errores: autenticación `{detalle: "Credenciales o sesión no válidas."}`; CSRF `{detalle: "La verificación CSRF no fue válida."}`; throttling `{detalle: "Demasiadas solicitudes..."}` con Retry-After; validación `{errores: {...}}`; ruta inexistente 404 JSON y error inesperado 500 genérico. No se usa 200 para fallos de la API. El formulario HTML del Admin sigue el comportamiento Django y puede devolver 200 mostrando errores del formulario.

## Cookies y revocación

lt_refresh: HttpOnly, SameSite=Lax, path=/api/v1/auth/, max-age=86400; Secure obligatorio con production y desactivado solo en HTTP local. Access dura 5 minutos. Refresh rota y reinicia su vigencia al renovar. El anterior se revoca mediante blacklist y bloqueo transaccional del registro OutstandingToken para evitar doble consumo concurrente.

Logout revoca el refresh presentado, no todos los dispositivos. Un access ya emitido continúa válido hasta vencer (máximo 5 minutos), salvo que la cuenta sea desactivada/eliminada. No se afirma revocación instantánea de access. La baja de la cuenta se consulta en cada petición JWT y en refresh. La futura integración Android deberá definir su contrato propio; no se expuso un refresh alternativo en el body para eludir CSRF.

CHECKLIST HUMANO: usar herramientas locales para credenciales reales y no pegarlas en el chat. Revisar el contrato antes de conectar la interfaz en F4.

## CRUD de F3

Todas las rutas siguientes exigen **JWT access en Authorization: Bearer**, nunca solo la cookie de refresh o una sesión del Admin. Sin token válido: 401. Cuenta activa sin empresa o con empresa inactiva: 403. Superadmin puede consultar globalmente, incluidas empresas inactivas; las escrituras requieren empresa activa.

| Método/ruta | Operación | Respuesta correcta |
|---|---|---|
| GET `/categories/` | Listado de categorías del ámbito autorizado | 200 array JSON |
| POST `/categories/` | Crear categoría | 201 objeto |
| GET `/categories/{uuid}/` | Detalle autorizado | 200 objeto |
| PUT `/categories/{uuid}/` | Actualizar; name obligatorio | 200 objeto |
| PATCH `/categories/{uuid}/` | Actualización parcial | 200 objeto |
| DELETE `/categories/{uuid}/` | Borrar categoría sin referencias | 204 sin cuerpo |
| GET `/boxes/` | Listado de cajas del ámbito autorizado | 200 array JSON |
| POST `/boxes/` | Crear caja REGISTERED | 201 objeto |
| GET `/boxes/{uuid}/` | Detalle autorizado | 200 objeto |
| PUT `/boxes/{uuid}/` | Actualizar; product, branch y quantity obligatorios | 200 objeto |
| PATCH `/boxes/{uuid}/` | Actualización parcial y cambio inicial de estado | 200 objeto |
| DELETE `/boxes/{uuid}/` | Borrar caja REGISTERED | 204 sin cuerpo |

HEAD/OPTIONS están disponibles según DRF y los mismos permisos. Métodos no admitidos: 405. Listas sin paginación en este alcance; paginación/volúmenes avanzados siguen pendientes de etapas posteriores. Orden estable por created_at e id. Respuestas privadas con Cache-Control: no-store.

### Permisos y pertenencia

| Acción | SUPERADMIN | COMPANY_ADMIN | OPERATOR asignado |
|---|---|---|---|
| Leer categorías/cajas | Global | Solo su empresa | Solo su empresa |
| Crear/editar/borrar categorías | Sí | Solo su empresa | No, 403 |
| Crear/editar cajas | Sí | Solo su empresa | Solo su empresa |
| Borrar cajas | Sí, con reglas de estado | Solo su empresa y reglas de estado | No, 403 |

El detalle ajeno se filtra antes de recuperar el objeto: 404 para un rol que puede realizar esa acción. Un método prohibido por rol devuelve 403 independientemente de que el UUID exista. No se ofrecen rutas para transferir recursos entre empresas.

POST del superadmin requiere company explícita de empresa activa. Para los demás, company la impone el servidor: enviarla incluso con su propia empresa devuelve 400. Company no es editable por nadie en PUT/PATCH. Created_by siempre es el actor de creación y no se admite en JSON de ningún rol.

### Categoría: cuerpo y validaciones

```json
{"name":"Refrigerados","description":"Cadena de frío","is_fragile":true,"is_perishable":true}
```

Solo superadmin añade `company: "<uuid-empresa-activa>"` en POST. Name: obligatorio al crear/PUT, máximo 120 caracteres, sin vacío ni solo espacios; se recortan espacios exteriores. Nombre único por empresa sin distinguir mayúsculas. Fragilidad y perecibilidad pueden coexistir. Description opcional, flags false por defecto. Respuesta: id, company, company_name, name, description, flags y created_at. Campos id/company_name/created_at son solo lectura y enviarlos devuelve 400.

Nombre duplicado: 409. DELETE referenciado por Product: 409 sin revelar datos de referencias; PROTECT conservado. Los productos/sucursales mínimos siguen administrándose por procedimiento restringido de F2; no se añadieron sus CRUD públicos en F3.

### Caja: cuerpo y validaciones

```json
{
  "product":"<uuid-producto-de-la-empresa>",
  "branch":"<uuid-sucursal-de-la-empresa>",
  "quantity":4,
  "weight_kg":"1.250",
  "priority":"HIGH"
}
```

Solo superadmin añade company en POST. El producto y la sucursal deben existir, estar activos y pertenecer a la empresa. También se valida la categoría del producto. Una referencia ajena y una inexistente devuelven 400 con mensaje genérico. No hay consultas de relaciones arbitrarias del ORM desde el JSON.

Quantity: entero positivo, sin fracciones ni booleanos; validadores de modelo mantienen límites de PostgreSQL. Weight_kg: decimal opcional/null, positivo, máximo 12 dígitos y 3 decimales; se devuelve como string decimal o null. Priority: LOW/NORMAL/HIGH. Status: REGISTERED/RECEIVED/REJECTED, con CHECK PostgreSQL además de validación servidor.

Identificadores generados: id UUID, internal_id `CJ-` + 32 hexadecimales y qr_code UUID independiente, con UNIQUE. Colisión de identificadores: hasta tres intentos transaccionales; agotamiento devuelve 409 genérico. No se regeneran para cambios ordinarios. Se rechaza escribir id/internal_id/qr_code/created_by/created_at, nombres de lectura o campos desconocidos, en cualquier rol.

Respuesta incluye esos identificadores, company/company_name, product/product_name/product_sku/category_name, branch/branch_name, quantity, weight_kg, priority, status, created_by y created_at. Los nombres solo se consultan desde relaciones coherentes con la empresa; filas con relaciones externas incoherentes no se exponen en este CRUD.

Regla inicial de estados: POST únicamente REGISTERED (explícito u omitido); REGISTERED puede editar sus datos y pasar a RECEIVED o REJECTED. En estados finales no se admiten cambios de datos ni reversión; 409. Repetir los mismos valores no modifica datos y puede devolver 200. DELETE solo REGISTERED y rol administrativo; otras situaciones 409/403. Estos estados son marcas iniciales: no crean una Reception ni sustituyen el flujo de recepción/QR de F6.

El creador histórico se conserva aunque después cambie de empresa; no habilita al creador a seguir accediendo al inventario anterior. Se consulta la asignación vigente para cada petición.

### Filtros permitidos (solo GET de colección)

| Colección | Filtros |
|---|---|
| categories | company (UUID), search (name/description), is_fragile e is_perishable (`true`/`false`) |
| boxes | company/product/branch/category/qr_code (UUID), internal_id exacto, status, priority, search (internal_id/nombre de producto/SKU) |

Search: 1–100 caracteres tras recorte. Internal_id acepta minúsculas y se normaliza para búsqueda; formato CJ- seguido de 32 hexadecimales. Todos los filtros se combinan con AND, después de imponer la empresa. Dentro de search se busca por cualquiera de sus campos autorizados.

Usuario no global: company solo puede ser su empresa; otro UUID produce 403 sin consultar si existe. Un filtro válido de producto/sucursal/categoría/QR/internal_id ajeno devuelve lista vacía, nunca recursos globales. Superadmin puede filtrar por cualquier company. UUID/formato/estado inválido, filtro desconocido, repetido o filtros en detalle: 400. No se admiten lookups como company__id, product__company, ordering o filtros arbitrarios.

Ejemplos de lectura: `GET /api/v1/boxes/?internal_id=CJ-<32-hex>`; `GET /api/v1/boxes/?qr_code=<uuid>`; `GET /api/v1/categories/?is_fragile=true&search=frio`. Requieren Bearer válido. No introducir tokens reales en documentación o historial de comandos compartidos.

### Errores y límite privado

Validación 400; token 401; permiso/ámbito 403; inexistencia/objeto ajeno 404; método 405; conflicto/PROTECT/estado/colisión 409; límite 429 con Retry-After; error inesperado 500 JSON genérico sin excepción/SQL/payload. No existe ruta pública para provocar fallos. Las escrituras son atómicas y releen/bloquean actor, recurso, empresa y referencias pertinentes.

Categorías y cajas comparten **120 solicitudes/minuto por usuario** (incluidos intentos admitidos hasta el throttle), con caché local de DRF. No consume el límite de login. No se garantiza exactitud concurrente o distribución entre workers; ver SEGURIDAD.md.
