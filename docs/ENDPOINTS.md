# Contrato REST implementado — Fase 2

Base: `/api/v1/`. Español para mensajes; identificadores/campos del código en inglés. Desarrollo local: frontend 127.0.0.1:5173 con proxy y API 127.0.0.1:8000. No existen endpoints REST de categorías/cajas todavía.

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
